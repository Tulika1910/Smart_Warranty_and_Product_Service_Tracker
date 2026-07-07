import streamlit as st
import pandas as pd
import pymupdf
import plotly.express as px
from datetime import date
from sqlalchemy import text
from auth import login_user, create_user
from database_initialise import get_db_engine
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
import os
from sync_utils import sync_warranty_data_to_csv

# --- API Configuration ---
genai.configure(api_key="YOURKEY") 
model = genai.GenerativeModel('gemini-3.5-flash')

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #4CAF50;
        color: white;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database Helper Functions ---
def get_data(query):
    try:
        engine = get_db_engine()
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Database Query Error: {e}")
        return pd.DataFrame()

def sync_csv_to_db():
    try:
        # Update this path to where your CSV actually lives
        file_path = r'C:\Users\agraw\Smart_Warranty_and_Product_Service_Tracker\Capstone_Project\data\warranties.csv'
        
        if not os.path.exists(file_path):
            st.error(f"File not found at: {file_path}")
            return False
            
        # Read the CSV
        df = pd.read_csv(file_path)
        
        # Connect and push to SQL
        engine = get_db_engine()
        # 'replace' will drop the table and recreate it, 
        # 'append' will just add the rows
        df.to_sql('warranties', con=engine, if_exists='append', index=False)
        
        st.success(f"Successfully pushed {len(df)} records to the database!")
        return True
    except Exception as e:
        st.error(f"Sync Process Error: {e}")
        return False

# --- UI Layout Initialization ---
st.set_page_config(page_title="Smart Warranty Tracker", layout="wide", page_icon="🛡️")

if 'user' not in st.session_state: st.session_state.user = None
if 'messages' not in st.session_state: st.session_state.messages = []

# --- Authentication Logic ---
if not st.session_state.user:
    st.title("Smart Warranty & Service Tracker")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email_l = st.text_input("Email", key="l_email")
        password_l = st.text_input("Password", type="password", key="l_pass")
        if st.button("Login"):
            user = login_user(email_l, password_l)
            if user:
                st.session_state.user = user
                st.rerun()
            else: st.error("Invalid credentials.")
    with tab2:
        email_s = st.text_input("Email", key="s_email")
        password_s = st.text_input("Password", type="password", key="s_pass")
        if st.button("Sign Up"):
            if create_user(email_s, password_s): st.success("Created! Please proceed to login.")
else:
    # --- Sidebar & Navigation ---
    with st.sidebar:
        st.title("Navigation")
        choice = st.selectbox("Menu", [
    "Dashboard", 
    "Warranty Selector",  # New 5th Window
    "Add Service Request", 
    "Warranty AI Agent", 
    "Live Service Tracker"
])
        st.markdown("---")
        st.subheader("⚡ Quick View")
        df_prod = get_data("SELECT * FROM products")
        if not df_prod.empty:
            st.metric("Total Products", len(df_prod))
            if 'warranty_expiry' in df_prod.columns:
                st.metric("Expiring Soon", len(df_prod[pd.to_datetime(df_prod['warranty_expiry']) < pd.Timestamp.now()]))
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    # --- Dashboard Page Logic ---
    if choice == "Dashboard":
        st.title("📊 Warranty Overview")
        df_prod = get_data("SELECT * FROM products")
        df_reqs = get_data("SELECT * FROM service_requests")
        
        # Tier 1: Graphs
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Warranty Expiry Heatmap")
            if not df_prod.empty and 'warranty_expiry' in df_prod.columns:
                df_prod['warranty_expiry'] = pd.to_datetime(df_prod['warranty_expiry'])
                fig1 = px.histogram(df_prod, x="warranty_expiry", title="Expiry Distribution")
                st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.subheader("Requests Overview")
            if not df_reqs.empty:
                fig2 = px.pie(df_reqs, names='status', title="Request Status Breakdown")
                st.plotly_chart(fig2, use_container_width=True)
        
        # Tier 2: Data Tables
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📦 Product Inventory")
            sync_col1, sync_col2 = st.columns([1, 2])

            if st.button("Push CSV Data to SQL"):
                if sync_csv_to_db():
                    st.rerun()
            
            # Existing button to pull from DB to CSV (Backup)
            if st.button("Update Local Backup (CSV)"):
                sync_warranty_data_to_csv("warranties.csv")

            with sync_col1:
                if st.button("Sync to CSV"):
                    with st.spinner("Syncing..."):
                        if sync_warranty_data_to_csv("warranties.csv"):
                            st.success("CSV Updated!")
            with sync_col2:
                if st.checkbox("Preview CSV"):
                    try:
                        st.dataframe(pd.read_csv("warranties.csv"), use_container_width=True)
                    except:
                        st.warning("No CSV data found.")
            
            if st.button("Sync CSV to DB"): sync_csv_to_db(); st.rerun()
            st.dataframe(df_prod, use_container_width=True, hide_index=True)
            if st.button("Sync CSV Data"): sync_csv_to_db(); st.rerun()
            st.dataframe(df_prod, use_container_width=True, hide_index=True)
        with col4:
            st.subheader("🛠️ Active Service Requests")
            st.dataframe(df_reqs, use_container_width=True, hide_index=True)


    elif choice == "Warranty Selector":
        st.title("🔎 Product Warranty Lookup")
        
        # Load data from warranties table
        df_warranties = get_data("SELECT * FROM warranties")
        
        if not df_warranties.empty:
            selected_pid = st.selectbox("Select Product ID", df_warranties['product_id'].unique())
            
            # Filter data
            product_info = df_warranties[df_warranties['product_id'] == selected_pid].iloc[0]
            
            # Convert date objects to strings to fix the TypeError
            start_date_str = str(product_info['warranty_start_date'])
            end_date_str = str(product_info['warranty_end_date'])
            
            # Display details
            col1, col2 = st.columns(2)
            with col1:
                # Use st.write or st.text instead of st.metric if you don't need numeric change indicators,
                # or just pass the stringified date:
                st.metric("Warranty Start", start_date_str)
                st.metric("Warranty End", end_date_str)
            with col2:
                st.info(f"**Terms Summary:**\n\n{product_info['terms_summary']}")
        else:
            st.warning("No warranty data found in the database.")

    # --- Service Request Page ---
    elif choice == "Add Service Request":
        st.subheader("Submit a New Service Request")
        with st.form("service_form"):
            prod_id = st.text_input("Product ID")
            issue = st.text_area("Issue Description")
            deadline = st.date_input("Service Deadline")
            if st.form_submit_button("Submit"):
                query = text("INSERT INTO service_requests (product_id, issue_description, status, deadline, request_date) VALUES (:pid, :desc, 'Pending', :deadline, :req_date)")
                with get_db_engine().begin() as conn:
                    conn.execute(query, {"pid": prod_id, "desc": issue, "deadline": deadline, "req_date": date.today()})
                st.success("Request saved!"); st.rerun()
        st.dataframe(get_data("SELECT * FROM service_requests"))

    # --- Warranty AI Agent Page ---
    elif choice == "Warranty AI Agent":
        st.title("🤖 Warranty AI Agent")
        audio_text = speech_to_text(language='en', start_prompt="🎙️ Record Voice", stop_prompt="⏹️")
        uploaded_file = st.file_uploader("Upload Bill/Warranty (Optional)", type=["jpg", "png", "pdf"])
        
        for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
        
        query = audio_text or st.chat_input("Ask your question about product warranty...")
        if query:
            st.chat_message("user").write(query)
            st.session_state.messages.append({"role": "user", "content": query})
            context = get_data("SELECT * FROM products").to_string()
            
            # Hybrid processing
            payload = [f"Context: {context}. User Question: {query}"]
            if uploaded_file:
                if uploaded_file.name.endswith(".pdf"):
                    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
                    payload.append("Text: " + " ".join([page.get_text() for page in doc]))
                else: payload.append(Image.open(uploaded_file))
            
            response = model.generate_content(payload)
            st.chat_message("assistant").write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            if "add this" in query.lower() and uploaded_file and st.button("Confirm: Log to Database"):
                insert_cmd = model.generate_content(f"Convert info to SQL INSERT: {response.text}").text
                with get_db_engine().begin() as conn:
                    conn.execute(text(insert_cmd))
                st.success("Product logged!")

    elif choice == "Live Service Tracker":
        st.title("🔄 Live Service Status")
        
        # --- Update Status Form ---
        with st.expander("Update Service Request Status"):
            with st.form("status_update_form"):
                req_id = st.number_input("Request ID", min_value=1, step=1)
                new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed", "Cancelled"])
                
                if st.form_submit_button("Update Status"):
                    # 1. Update the main status using request_id
                    query = text("UPDATE service_requests SET status = :status WHERE request_id = :id")
                    with get_db_engine().begin() as conn:
                        conn.execute(query, {"status": new_status, "id": req_id})
                    
                    if new_status == "Completed":
                        history_query = text("""
                            INSERT INTO completed_requests (request_id, completion_date) 
                            VALUES (:id, :date)
                        """)
                        with get_db_engine().begin() as conn:
                            conn.execute(history_query, {"id": req_id, "date": date.today()})
                        st.toast("Request moved to Completed History! 🎉", icon="✅")
                    else:
                        st.toast(f"Status Updated: Request {req_id} is now {new_status}", icon="ℹ️")
                    
                    st.rerun()

        df_reqs = get_data("SELECT * FROM service_requests")
        st.dataframe(df_reqs, use_container_width=True)

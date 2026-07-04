import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text
from auth import login_user, create_user
from database_initialise import get_db_connection

def get_data(query):
    engine = get_db_connection()
    return pd.read_sql(query, engine)

def sync_csv_to_db():
    try:
        file_path = r'C:\Users\agraw\Desktop\Capstone_Project\data\products.csv'
        df = pd.read_csv(file_path)
        engine = get_db_connection()
        with engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            conn.execute(text("TRUNCATE TABLE products;"))
            df.to_sql('products', con=conn, if_exists='append', index=False)
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        return True
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return False

if 'user' not in st.session_state:
    st.session_state.user = None

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
            if create_user(email_s, password_s): st.success("Created! Please login.")
else:
    st.sidebar.title("Navigation")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    choice = st.sidebar.selectbox("Menu", ["Dashboard", "Add Service Request", "Warranty AI Agent"])

    if choice == "Dashboard":
        st.subheader("Your Products")
        if st.button("Sync CSV Data"):
            if sync_csv_to_db(): 
                st.success("Data Loaded!")
                st.rerun()
        try:
            st.dataframe(get_data("SELECT * FROM products"))
        except Exception:
            st.warning("No data found. Please sync CSV.")

    elif choice == "Add Service Request":
        st.subheader("Submit a New Service Request")
        with st.form("service_form"):
            prod_id = st.text_input("Product ID")
            issue = st.text_area("Issue Description")
            deadline = st.date_input("Service Deadline")
            
            if st.form_submit_button("Submit Request"):
                if prod_id and issue:
                    engine = get_db_connection()
                    # Using current date for request_date
                    query = text("""
                        INSERT INTO service_requests (product_id, issue_description, status, deadline, request_date) 
                        VALUES (:pid, :desc, 'Pending', :deadline, :req_date)
                    """)
                    with engine.begin() as conn:
                        conn.execute(query, {
                            "pid": prod_id, 
                            "desc": issue, 
                            "deadline": deadline, 
                            "req_date": date.today()
                        })
                    st.success("Request saved successfully!")
                    st.rerun()
                else: st.error("Please fill in all fields.")

        st.subheader("Your Past Service Requests")
        try:
            df_requests = get_data("SELECT * FROM service_requests")
            st.dataframe(df_requests)
        except Exception:
            st.info("No service requests found.")

    elif choice == "Warranty AI Agent":
        st.subheader("Warranty AI Agent")
        st.write("Ask questions about your product warranties or service status.")
        if prompt := st.chat_input("How can I help you?"):
            st.chat_message("user").write(prompt)
            st.chat_message("assistant").write("AI integration coming soon!")
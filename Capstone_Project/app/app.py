import os
import uuid
from datetime import date

import google.generativeai as genai
import pandas as pd
import plotly.express as px
import pymupdf
import streamlit as st
from PIL import Image
from sqlalchemy import text
from streamlit_mic_recorder import speech_to_text

from auth import create_user, login_user
from database_initialise import get_db_engine
from sync_utils import sync_warranty_data_to_csv

# --- API Configuration ---
genai.configure(api_key="YOURKEY") # Replace with your actual API key
model = genai.GenerativeModel("gemini-3.5-flash")

st.markdown(
    """
    <style>
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 8px 30px rgba(17, 24, 39, 0.04); }
        50% { box-shadow: 0 18px 40px rgba(17, 24, 39, 0.1); }
    }
    @keyframes floatUp {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }
    @keyframes dynamicTint {
        0% { background-position: 10% 10%; }
        50% { background-position: 90% 90%; }
        100% { background-position: 10% 10%; }
    }

    html, body, .stApp, .block-container {
        background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 35%, #e0f2fe 70%, #f0fdf4 100%);
        background-size: 200% 200%;
        animation: dynamicTint 20s ease infinite;
        color: #111827;
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stSidebar {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-right: 1px solid rgba(229, 231, 235, 0.7);
        box-shadow: none;
        padding: 22px 18px 18px 18px;
    }

    .css-1d391kg, .stMarkdown, .stDataFrame table, .stTextInput>div>div>input,
    .stDateInput>div>div>input, .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea, .stSelectbox>div>div>div>div,
    .stFileUploader {
        transition: all 0.25s ease;
    }

    .stButton>button {
        width: 100%;
        border-radius: 999px;
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        color: #ffffff;
        border: none;
        padding: 14px 18px;
        box-shadow: 0 12px 30px rgba(17, 24, 39, 0.08);
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        box-shadow: 0 18px 35px rgba(17, 24, 39, 0.14);
    }

    .stMetric {
        background-color: rgba(255, 255, 255, 0.82);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(229, 231, 235, 0.9);
        color: #111827;
        animation: floatUp 8s ease-in-out infinite;
        backdrop-filter: blur(14px);
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.05);
    }

    .stMetric>div {
        color: #111827;
    }

    .stDataFrame table {
        background-color: rgba(248, 250, 252, 0.92);
        color: #111827;
        border: 1px solid rgba(229, 231, 235, 0.95);
        box-shadow: 0 12px 24px rgba(15, 23, 42, 0.05);
    }

    .stPlotlyChart, .stPlotlyChart>div, .stPlotlyChart>div>div,
    .js-plotly-plot .plotly,
    .js-plotly-plot .main-svg {
        background-color: transparent !important;
    }

    .css-1d391kg, .stMarkdown {
        background-color: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(10px);
    }

    .stTextInput>div>div>input,
    .stDateInput>div>div>input,
    .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div>div {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 0px !important;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    .stTextInput>div>div>input:focus,
    .stDateInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>div>div:focus {
        outline: 2px solid rgba(59, 130, 246, 0.25) !important;
        border-color: #93c5fd !important;
    }

    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.92) !important;
        border: 1px solid rgba(229, 231, 235, 0.95);
        border-radius: 18px;
        padding: 16px;
    }

    .stAlert {
        border-radius: 16px !important;
        border: 1px solid #d1d5db !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Database Helper Functions ---
def get_data(query, params=None):
    try:
        engine = get_db_engine()
        if engine is None:
            return pd.DataFrame()
        if params is None:
            return pd.read_sql_query(query, engine)
        return pd.read_sql_query(text(query), engine, params=params)
    except Exception as e:
        st.error(f"Database Query Error: {e}")
        return pd.DataFrame()


def sync_csv_to_db():
    st.info("Warranty entries are created from the form and stay tied to your profile. CSV imports are disabled.")
    return False


def get_ai_response(prompt: str) -> str:
    try:
        if hasattr(model, "generate_text"):
            response = model.generate_text(prompt)
            return getattr(response, "text", str(response))
        if hasattr(model, "generate_content"):
            response = model.generate_content(prompt)
            if hasattr(response, "text"):
                return response.text
            if isinstance(response, dict):
                return response.get("content") or response.get("text") or str(response)
            return str(response)
        return str(model)
    except Exception as e:
        raise RuntimeError(f"AI service error: {e}") from e


def ensure_user_scoped_schema():
    engine = get_db_engine()
    if engine is None:
        return False

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS completed_requests (
                    request_id INT,
                    user_id VARCHAR(255) NULL,
                    completion_date DATE NULL,
                    FOREIGN KEY (request_id) REFERENCES service_requests(request_id)
                )
                """
            )
        )

        for table, column, definition in [
            ("service_requests", "user_id", "VARCHAR(255) NULL"),
            ("service_requests", "deadline", "DATE NULL"),
            ("service_requests", "request_date", "DATE NULL"),
            ("warranties", "user_id", "VARCHAR(255) NULL"),
            ("warranties", "purchase_date", "DATE NULL"),
            ("warranties", "price", "DECIMAL(10, 2) NULL"),
            ("warranties", "product_name", "VARCHAR(100) NULL"),
            ("warranties", "category", "VARCHAR(50) NULL"),
            ("warranties", "terms_summary", "TEXT NULL"),
            ("completed_requests", "user_id", "VARCHAR(255) NULL"),
        ]:
            check_query = text(
                """
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = :table_name
                  AND column_name = :column_name
                """
            )
            exists = conn.execute(check_query, {"table_name": table, "column_name": column}).scalar()
            if exists == 0:
                conn.execute(text(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"))

    return True


def get_current_user_id():
    if st.session_state.get("current_user_id"):
        return st.session_state.current_user_id

    user = st.session_state.get("user")
    if not user:
        return None

    if isinstance(user, dict):
        email = user.get("email")
        if email:
            user_id = str(email).strip().lower()
            st.session_state.current_user_id = user_id
            return user_id

        for key in ("localId", "uid", "user_id"):
            value = user.get(key)
            if value:
                user_id = str(value)
                st.session_state.current_user_id = user_id
                return user_id

    user_id = str(user)
    st.session_state.current_user_id = user_id
    return user_id


def backfill_user_scoped_data(user_id):
    if not user_id:
        return

    engine = get_db_engine()
    if engine is None:
        return

    with engine.begin() as conn:
        conn.execute(
            text("UPDATE service_requests SET user_id = :user_id WHERE user_id IS NULL OR TRIM(COALESCE(user_id, '')) = ''"),
            {"user_id": user_id},
        )
        conn.execute(
            text("UPDATE warranties SET user_id = :user_id WHERE user_id IS NULL OR TRIM(COALESCE(user_id, '')) = ''"),
            {"user_id": user_id},
        )
        conn.execute(
            text("UPDATE completed_requests SET user_id = :user_id WHERE user_id IS NULL OR TRIM(COALESCE(user_id, '')) = ''"),
            {"user_id": user_id},
        )


# --- UI Layout Initialization ---
st.set_page_config(page_title="Smart Warranty Tracker", layout="wide", page_icon="🛡️")

if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Dashboard"
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
if "pending_verification_email" not in st.session_state:
    st.session_state.pending_verification_email = None
if "nav_reset" not in st.session_state:
    st.session_state.nav_reset = False
if st.session_state.nav_reset:
    st.session_state.nav_choice = "Dashboard"
    st.session_state.nav_reset = False

ensure_user_scoped_schema()

# --- Authentication Logic ---
if not st.session_state.user:
    st.title("Smart Warranty & Service Tracker")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        email_l = st.text_input("Email", key="l_email")
        password_l = st.text_input("Password", type="password", key="l_pass")
        if st.session_state.pending_verification_email:
            st.info(f"A verification email was sent to {st.session_state.pending_verification_email}. Please verify before logging in.")
        if st.button("Login"):
            user = login_user(email_l, password_l)
            if user:
                st.session_state.user = user
                st.session_state.messages = []
                st.session_state.nav_choice = "Dashboard"
                st.session_state.current_user_id = None
                st.rerun()
            else:
                st.error("Invalid credentials.")
    with tab2:
        email_s = st.text_input("Email", key="s_email")
        password_s = st.text_input("Password", type="password", key="s_pass")
        if st.button("Sign Up"):
            if create_user(email_s, password_s):
                # store pending verification email so user sees the confirmation message
                st.session_state.pending_verification_email = email_s
                st.success(f"Verification email sent to {email_s}. Please verify before logging in.")
            else:
                st.error("Error creating account. Please try again.")
else:
    current_user_id = get_current_user_id()
    backfill_user_scoped_data(current_user_id)

    # --- Sidebar & Navigation ---
    with st.sidebar:
        st.title("Navigation")
        choice = st.selectbox(
            "Menu",
            ["Dashboard", "Warranty", "Add Service Request", "Warranty AI Agent", "Live Service Tracker"],
            key="nav_choice",
        )
        st.markdown("---")
        st.subheader("⚡ Quick View")
        df_prod = get_data("SELECT * FROM products")
        if not df_prod.empty:
            st.metric("Total Products", len(df_prod))
            if "warranty_expiry" in df_prod.columns:
                st.metric("Expiring Soon", len(df_prod[pd.to_datetime(df_prod["warranty_expiry"]) < pd.Timestamp.now()]))
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.messages = []
            # set a reset flag so we don't modify nav_choice after the widget exists
            st.session_state.nav_reset = True
            st.session_state.current_user_id = None
            st.rerun()

    # --- Dashboard Page Logic ---
    if choice == "Dashboard":
        st.title("📊 Warranty Overview")
        df_prod = get_data("SELECT * FROM products")
        df_reqs = get_data(
            "SELECT * FROM service_requests WHERE user_id = :user_id",
            {"user_id": current_user_id},
        )

        df_warranty_dates = get_data(
            "SELECT warranty_end_date FROM warranties WHERE user_id = :user_id AND warranty_end_date IS NOT NULL",
            {"user_id": current_user_id},
        )

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Warranty Expiry Heatmap")
            if not df_warranty_dates.empty:
                df_warranty_dates["warranty_end_date"] = pd.to_datetime(df_warranty_dates["warranty_end_date"])
                fig1 = px.histogram(df_warranty_dates, x="warranty_end_date", title="Warranty End Date Distribution")
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("No warranty end dates have been added yet for this profile.")
        with col2:
            st.subheader("Requests Overview")
            if not df_reqs.empty:
                fig2 = px.pie(df_reqs, names="status", title="Request Status Breakdown")
                st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📦 Product Inventory")
            st.dataframe(df_prod, use_container_width=True, hide_index=True)
        with col4:
            st.subheader("🛠️ Active Service Requests")
            st.dataframe(df_reqs, use_container_width=True, hide_index=True)

    elif choice == "Warranty":
        st.title("🛡️ Warranty Management")
        st.caption("Add a warranty entry for your account and review the saved records below.")

        with st.form("warranty_form"):
            product_id = st.text_input("Product ID")
            product_name = st.text_input("Product Name")
            category = st.text_input("Category")
            purchase_date = st.date_input("Purchase Date", value=date.today())
            price = st.number_input("Price", min_value=0.0, step=0.01, format="%.2f")
            warranty_start_date = st.date_input("Warranty Start Date", value=date.today())
            warranty_end_date = st.date_input("Warranty End Date", value=date.today())
            generated_terms = st.text_area(
                "AI Terms Summary",
                value=st.session_state.get("generated_terms", ""),
                key="generated_terms_input",
            )

            col_save, col_gen = st.columns(2)
            with col_save:
                submit_warranty = st.form_submit_button("Save Warranty")
            with col_gen:
                generate_terms = st.form_submit_button("Generate Terms Summary")

            if generate_terms:
                prompt = (
                    f"Create a concise warranty terms summary for a {category or 'product'} named "
                    f"{product_name or product_id or 'product'}. Include coverage from {warranty_start_date} "
                    f"to {warranty_end_date}, purchase date {purchase_date}, and price {price}. Keep it professional."
                )
                try:
                    response = model.generate_content(prompt)
                    summary_text = getattr(response, "text", str(response)).strip()
                    st.session_state.generated_terms = summary_text
                    st.session_state.generated_terms_input = summary_text
                    st.success("Terms summary generated.")
                except Exception as exc:
                    st.warning(f"Could not generate summary: {exc}")

            if submit_warranty:
                if not product_id.strip():
                    product_id = f"P-{uuid.uuid4().hex[:8].upper()}"

                product_query = text(
                    """
                    INSERT INTO products (product_id, product_name, category)
                    VALUES (:product_id, :product_name, :category)
                    ON DUPLICATE KEY UPDATE
                        product_name = VALUES(product_name),
                        category = VALUES(category)
                    """
                )
                warranty_query = text(
                    """
                    INSERT INTO warranties (
                        warranty_id,
                        product_id,
                        warranty_start_date,
                        warranty_end_date,
                        purchase_date,
                        price,
                        product_name,
                        category,
                        terms_summary,
                        user_id
                    ) VALUES (
                        :warranty_id,
                        :product_id,
                        :warranty_start_date,
                        :warranty_end_date,
                        :purchase_date,
                        :price,
                        :product_name,
                        :category,
                        :terms_summary,
                        :user_id
                    )
                    """
                )

                with get_db_engine().begin() as conn:
                    conn.execute(
                        product_query,
                        {
                            "product_id": product_id,
                            "product_name": product_name,
                            "category": category,
                        },
                    )
                    conn.execute(
                        warranty_query,
                        {
                            "warranty_id": f"W-{uuid.uuid4().hex[:8].upper()}",
                            "product_id": product_id,
                            "warranty_start_date": warranty_start_date,
                            "warranty_end_date": warranty_end_date,
                            "purchase_date": purchase_date,
                            "price": price,
                            "product_name": product_name,
                            "category": category,
                            "terms_summary": generated_terms.strip() or "AI-generated warranty summary pending.",
                            "user_id": current_user_id,
                        },
                    )

                st.success("Warranty saved for your profile.")
                st.rerun()

        df_warranties = get_data(
            """
            SELECT
                w.warranty_id,
                w.product_id,
                w.warranty_start_date,
                w.warranty_end_date,
                w.purchase_date,
                w.price,
                w.product_name,
                w.category,
                w.terms_summary,
                w.user_id,
                p.product_name AS product_name_ref,
                p.category AS category_ref
            FROM warranties w
            LEFT JOIN products p ON p.product_id = w.product_id
            WHERE w.user_id = :user_id
            """,
            {"user_id": current_user_id},
        )

        if df_warranties.empty:
            st.info("No warranty records yet for this profile.")
        else:
            option_labels = [
                f"{row['product_id']} - {row.get('product_name') or row.get('product_name_ref') or 'Unnamed'}"
                for _, row in df_warranties.iterrows()
            ]
            selected_label = st.selectbox("Your saved warranties", option_labels)
            selected_idx = option_labels.index(selected_label)
            product_info = df_warranties.iloc[selected_idx]

            start_date_str = str(product_info["warranty_start_date"])
            end_date_str = str(product_info["warranty_end_date"])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Warranty Start", start_date_str)
                st.metric("Warranty End", end_date_str)
                st.metric("Purchase Date", str(product_info.get("purchase_date") or "Not provided"))
                st.metric("Price", f"{product_info.get('price') or 0:.2f}")
            with col2:
                st.info(f"**Terms Summary:**\n\n{product_info.get('terms_summary') or 'No summary generated yet.'}")

    elif choice == "Add Service Request":
        st.subheader("Submit a New Service Request")
        with st.form("service_form"):
            prod_id = st.text_input("Product ID")
            issue = st.text_area("Issue Description")
            deadline = st.date_input("Service Deadline")
            if st.form_submit_button("Submit"):
                query = text(
                    """
                    INSERT INTO service_requests (
                        product_id,
                        issue_description,
                        status,
                        deadline,
                        request_date,
                        user_id
                    ) VALUES (
                        :pid,
                        :desc,
                        'Pending',
                        :deadline,
                        :req_date,
                        :user_id
                    )
                    """
                )
                with get_db_engine().begin() as conn:
                    conn.execute(
                        query,
                        {
                            "pid": prod_id,
                            "desc": issue,
                            "deadline": deadline,
                            "req_date": date.today(),
                            "user_id": current_user_id,
                        },
                    )
                st.success("Request saved!")
                st.rerun()
        st.dataframe(
            get_data(
                "SELECT * FROM service_requests WHERE user_id = :user_id",
                {"user_id": current_user_id},
            )
        )

    elif choice == "Warranty AI Agent":
        st.title("🤖 Warranty AI Agent")
        audio_text = speech_to_text(language="en", start_prompt="🎙️ Record Voice", stop_prompt="⏹️")
        uploaded_file = st.file_uploader("Upload Bill/Warranty (Optional)", type=["jpg", "png", "pdf"])

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        query = audio_text or st.chat_input("Ask your question about product warranty...")
        if query:
            st.chat_message("user").write(query)
            st.session_state.messages.append({"role": "user", "content": query})
            context = get_data("SELECT * FROM products").to_string()

            # Build a plain-text prompt from context and user query
            prompt_parts = [f"Context: {context}", f"User Question: {query}"]
            if uploaded_file:
                if uploaded_file.name.endswith(".pdf"):
                    try:
                        doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
                        prompt_parts.append("Text: " + " ".join([page.get_text() for page in doc]))
                    except Exception as _:
                        prompt_parts.append("(Could not extract text from uploaded PDF)")
                else:
                    prompt_parts.append(f"Attached image: {uploaded_file.name}")

            prompt = "\n\n".join(prompt_parts)

            try:
                text = get_ai_response(prompt)
                st.chat_message("assistant").write(text)
                st.session_state.messages.append({"role": "assistant", "content": text})

            except Exception as e:
                st.error(f"AI service error: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"(AI error) {e}"})

            # Offer to convert assistant output to SQL only if assistant returned text
            if any(k in (st.session_state.messages[-1].get("content") or "") for k in ["add this", "insert", "log"]):
                if uploaded_file and st.button("Confirm: Log to Database"):
                    try:
                        conv = get_ai_response(f"Convert info to SQL INSERT: {st.session_state.messages[-1]['content']}")
                        insert_cmd = conv
                        with get_db_engine().begin() as conn:
                            conn.execute(text(insert_cmd))
                        st.success("Product logged!")
                    except Exception as e:
                        st.error(f"Failed to log to database: {e}")

    elif choice == "Live Service Tracker":
        st.title("🔄 Live Service Status")

        with st.expander("Update Service Request Status"):
            with st.form("status_update_form"):
                req_id = st.number_input("Request ID", min_value=1, step=1)
                new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed", "Cancelled"])

                if st.form_submit_button("Update Status"):
                    query = text(
                        """
                        UPDATE service_requests
                        SET status = :status
                        WHERE request_id = :id AND user_id = :user_id
                        """
                    )
                    with get_db_engine().begin() as conn:
                        result = conn.execute(query, {"status": new_status, "id": req_id, "user_id": current_user_id})

                    if result.rowcount == 0:
                        st.warning("That request is not available for your profile.")
                    elif new_status == "Completed":
                        history_query = text(
                            """
                            INSERT INTO completed_requests (request_id, user_id, completion_date)
                            VALUES (:id, :user_id, :date)
                            """
                        )
                        with get_db_engine().begin() as conn:
                            conn.execute(history_query, {"id": req_id, "user_id": current_user_id, "date": date.today()})
                        st.toast("Request moved to Completed History! 🎉", icon="✅")
                    else:
                        st.toast(f"Status Updated: Request {req_id} is now {new_status}", icon="ℹ️")

                    st.rerun()

        df_reqs = get_data(
            "SELECT * FROM service_requests WHERE user_id = :user_id",
            {"user_id": current_user_id},
        )
        st.dataframe(df_reqs, use_container_width=True)

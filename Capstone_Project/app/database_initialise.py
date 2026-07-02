from sqlalchemy import create_engine
import streamlit as st

def get_db_connection():
    db_url = 'mysql+mysqlconnector://root:tulika@localhost/smart_warranty_db'
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            print("Connection successful!")
        return engine
    except Exception as e:
        st.error(f"Connection Failed: {e}")
        return None
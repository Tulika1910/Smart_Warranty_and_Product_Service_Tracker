from sqlalchemy import create_engine
import streamlit as st

def get_db_engine():
    # Use credentials from st.secrets
    user = st.secrets["database"]["user"]
    password = st.secrets["database"]["password"]
    host = st.secrets["database"]["host"]
    db = st.secrets["database"]["database"]
    
    db_url = f'mysql+mysqlconnector://{user}:{password}@{host}/{db}'
    
    try:
        engine = create_engine(db_url)
        # Test connection
        with engine.connect() as connection:
            pass
        return engine
    except Exception as e:
        st.error(f"Database Connection Failed: {e}")
        return None
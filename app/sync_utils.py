import pandas as pd
import streamlit as st
from database_initialise import get_db_engine

def sync_warranty_data_to_csv(csv_path):
    try:
        engine = get_db_engine()
        if engine is None:
            return False
            
        # Query using the engine
        query = "SELECT warranty_id, product_id, warranty_start_date, warranty_end_date, terms_summary FROM warranties"
        
        # Read directly from the engine
        df = pd.read_sql(query, engine)
        
        # Overwrite the CSV
        df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        st.error(f"Error during synchronization: {e}")
        return False
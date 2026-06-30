import streamlit as st
import pandas as pd
from database_initialise import get_db_connection 

st.title("Smart Warranty & Service Tracker")

def get_data(query):
    conn = get_db_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

menu = ["Dashboard", "Add Service Request", "Warranty AI Helper"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    st.subheader("Your Products")
    products = get_data("SELECT * FROM products")
    st.dataframe(products)

elif choice == "Warranty AI Helper":
    st.subheader("AI Warranty Assistant")

elif choice == "Add Service Request":
    st.subheader("Raise a Request")
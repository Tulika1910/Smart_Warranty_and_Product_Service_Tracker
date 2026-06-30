import mysql.connector
import streamlit as st

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="tulika",
        database="smart_warranty_db"
    )

def import_csv_to_db(file_path, table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    with open(file_path, 'r') as file:
        import csv
        reader = csv.reader(file)
        next(reader) 
        
        query = f"INSERT INTO {table_name} VALUES (%s, %s, %s, %s, %s)"
        for row in reader:
            cursor.execute(query, row)
            
    conn.commit()
    cursor.close()
    conn.close()
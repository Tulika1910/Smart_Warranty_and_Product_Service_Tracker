import pandas as pd
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="tulika",      # change this
    database="smart_warranty_db"
) 

cursor = conn.cursor()

csv_files = {
    "products": "data/products.csv",
    "warranties": "data/warranties.csv",
    "service_requests": "data/service_requests.csv",
    "documents": "data/documents.csv"
}

for table, path in csv_files.items():

    df = pd.read_csv(path)

    cols = ",".join(df.columns)
    vals = ",".join(["%s"] * len(df.columns))

    sql = f"INSERT INTO {table} ({cols}) VALUES ({vals})"

    for row in df.itertuples(index=False):
        cursor.execute(sql, tuple(row))

    conn.commit()

    print(f"{table} imported successfully.")

cursor.close()
conn.close()

print("Done!")
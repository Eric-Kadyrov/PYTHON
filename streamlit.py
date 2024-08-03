import streamlit as st
import sqlite3
import pandas as pd
import os


st.title("SQLite Table Viewer")

# Upload the .db file
uploaded_file = st.file_uploader("Choose a .db file", type="db")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    db_file_path =uploaded_file.name
    
    with open(db_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Get the list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    
    if table_names:
        # Select a table to display
        selected_table = st.selectbox("Select a table", table_names)
        
        if selected_table:
            # Query the selected table
            query = f"SELECT * FROM {selected_table}"
            df = pd.read_sql_query(query, conn)
            
            # Display the table
            st.write(f"Contents of {selected_table} table:")
            st.dataframe(df)
    
    # Close the connection
    conn.close()

import streamlit as st
import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("alerts.db")

# SQL query
query = "SELECT * FROM events"

# Read data into a dataframe
df = pd.read_sql_query(query, conn)

# Streamlit UI
st.title("Events Database")

# Display dataframe
st.dataframe(df)
conn.close()

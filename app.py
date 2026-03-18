import streamlit as st
import pandas as pd
import sqlite3

#To run the streamlit, use cmd and go to the file location via cd "C:User\etc" then enter py -m streamlit run app.py in order to run it. It will open in the browser.


# Page title
st.set_page_config(page_title="Project Argus Dashboard")

# Team title
st.title("Project Argus – Team Dashboard")


conn = sqlite3.connect("alerts.db")

query = "SELECT camera_id, confidence, timestamp FROM events"
df = pd.read_sql_query(query, conn)

df = pd.DataFrame(data)

# Section header
st.subheader("Live Camera Data (Placeholder)")

# Display table
st.dataframe(df)

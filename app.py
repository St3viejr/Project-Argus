import streamlit as st
import pandas as pd

#To run the streamlit, use cmd and go to the file location via cd "C:User\etc" then enter py -m streamlit run app.py in order to run it. It will open in the browser.


# Page title
st.set_page_config(page_title="Project Argus Dashboard")

# Team title
st.title("Project Argus – Team Dashboard")

# Placeholder data
data = {
    "Camera ID": ["Cam-01", "Cam-02", "Cam-03"],
    "Status": ["Offline", "Offline", "Offline"],
    "Detected Objects": [...,...,...],
    "Last Updated": ["--", "--", "--"]
}

df = pd.DataFrame(data)

# Section header
st.subheader("Live Camera Data (Placeholder)")

# Display table
st.dataframe(df)

import streamlit as st
import pandas as pd
import sqlite3
import base64
import time
import sys
import os



#This is the main Streamlit app for the Project Argus PSOC dashboard.

# Functionality:
#    -Connects to the SQLite database 
#    -Retrieves the latest alerts 
#    -Displays them in a user-friendly format. 
#    -Has a sidebar with a shutdown button that signals the entire system to safely terminate.
#    -Has history logs in an expander at the bottom for post-incident review.

# The app is designed to refresh every 2 seconds, 
# but you can also manually refresh by pressing "r" on the page to see updates immediately.
# to provide real-time updates on camera statuses and detected threats. 
# Custom CSS is used to style the alert boxes and make the interface visually appealing.'''

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "../../Backend/alerts.db"))


st.set_page_config(page_title="Project Argus PSOC", layout="wide")

with st.sidebar:
    st.header("Mission Control")
    st.markdown("Use this panel to manage the Project Argus system.")
    
    st.markdown("---")
    
    if st.button("SHUTDOWN SYSTEM", use_container_width=True, type="primary"):
        with open("../../shutdown.signal", "w") as f:
            f.write("terminate")
        
        st.success("Shutdown signal sent! You can safely close this browser tab.")
        st.stop()


st.markdown("""
    <style>
    .threat-box {
    padding: 20px;
    border-radius: 12px;
    background-color: #2b0000;
    border: 2px solid #ff4b4b;
    color: white;
    margin-bottom: 20px;
    font-family: 'Courier New', Courier, monospace;
    width: 100%;
    box-sizing: border-box;
    }
    .threat-header {
        color: #ff4b4b !important;
        margin: 0 !important;
        font-family: "Source Sans Pro", sans-serif;
        font-weight: 790 !important;
        text-transform: uppercase;
        white-space: nowrap;
        font-size: 1.6rem !important;
        letter-spacing: -0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Project Argus – Physical Security Operations Center (PSOC)")


@st.fragment(run_every=2)
def display_camera_status():
    try:
        conn = sqlite3.connect(DB_PATH)
        df_raw = pd.read_sql_query("SELECT camera_id, confidence, timestamp, image_data, description FROM events ORDER BY timestamp ASC", conn)
        conn.close()

        if not df_raw.empty:
            df_raw = df_raw.reset_index().rename(columns={'index': 'Threat_#'})
            df_display = df_raw.iloc[::-1]
            latest_alerts = df_display.groupby('camera_id').first().reset_index()

            # CACHE & COOLDOWN INIT
            if "analysis_cache" not in st.session_state:
                st.session_state.analysis_cache = {}
            if "last_api_call" not in st.session_state:
                st.session_state.last_api_call = 0  # Tracks the last OpenRouter ping

            for _, row in latest_alerts.iterrows():
                confidence_pct = row['confidence'] * 100


                if row['image_data']:
                    img_tag = f'<img src="data:image/jpeg;base64,{row["image_data"]}" style="width:100%; border-radius:8px; border: 1px solid #ff4b4b44; margin-bottom: 5px;">'
                    cap_tag = '<p style="text-align:center; color:#aaaaaa; font-size:0.8rem; margin: 0;">Captured Threat Evidence</p>'
                else:
                    img_tag = "<p style='color:#aaaaaa; font-style:italic;'>[NO IMAGE DATA]</p>"
                    cap_tag = ""

                alert_col, log_col = st.columns([2.5, 1], gap="large")

                with alert_col:
                    st.markdown(f"""
<div class="threat-box" style="padding: 30px; height: 100%;">
<div class="threat-header" style="font-size: 2rem !important; text-align: center;">⚠️ ALERT: THREAT EMINENT</div>
<hr style="border: 1px solid #ff4b4b44; margin: 20px 0;">

<div style="display: flex; flex-direction: row; gap: 30px; align-items: center; flex-wrap: wrap;">

<div style="flex: 1.5; min-width: 300px;">
{img_tag}
{cap_tag}
</div>

<div style="flex: 1; min-width: 250px; display: flex; flex-direction: column;">
<p style="margin: 8px 0; font-size: 1.25rem;"><b>Camera ID:</b> {row['camera_id']}</p>
<p style="margin: 8px 0; font-size: 1.25rem;"><b>ISO 8601:</b> {row['timestamp']}</p>
<p style="margin: 8px 0; font-size: 1.25rem;"><b>Confidence:</b> {confidence_pct:.1f}%</p>

<div style="margin-top: 20px; padding: 15px; background-color: #ff4b4b11; border-left: 5px solid #ff4b4b; border-radius: 6px;">
<p style="margin: 0; color: #dddddd; font-size: 1.15rem;">
<b>Description:</b><br>
<span style="font-style: italic;">{row['description']}</span>
</p>
</div>
</div>

</div>
</div>
""", unsafe_allow_html=True)

                with log_col:
                    st.markdown(f"<h4 style='color: #dddddd; margin-top: 0; margin-bottom: 15px;'>Log History</h4>", unsafe_allow_html=True)
                    camera_history = df_display[df_display['camera_id'] == row['camera_id']]
                    st.dataframe(camera_history, hide_index=True, width="stretch", height=420)

        else:
            st.success("System Status: No active threats detected.")

    except Exception as e:
        st.error(f"Database Connection Error: {e}")


spacer_left, main_col, spacer_right = st.columns([0.5, 6, 0.5])

with main_col:
    st.subheader("Active Camera Status", anchor=False)
    display_camera_status()


st.markdown("---")
st.subheader("Historical Threat Logs")

with st.expander("View Previous Detections", expanded=False):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, confidence, image_data, description FROM events ORDER BY id DESC LIMIT 20 OFFSET 1")
        historical_alerts = cursor.fetchall()
        conn.close()

        if not historical_alerts:
            st.info("No historical logs found.")
        else:
            for timestamp, conf, img_data, description in historical_alerts:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"**Time:** {timestamp}")
                    st.markdown(f"**Confidence:** {conf*100:.1f}%")
                    st.markdown(f"**AI Log:** {description}")
                with col2:
                    img_bytes = base64.b64decode(img_data)
                    st.image(img_bytes, use_column_width=True)
                st.divider()
    except Exception as e:
        st.error(f"Could not load history: {e}")

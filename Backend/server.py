from pydantic import BaseModel, Field
from database import DatabaseHandler
from datetime import datetime
from fastapi import FastAPI
import time  
import json
import sys
import os


# This module contains the main FastAPI application and handles alert triggering with throttling.

# Functionality:
#     - Initializes the database on startup.
#     - Defines a Pydantic model for incoming alert data.
#     - Implements a POST endpoint to receive alerts, with throttling to prevent spamming from the same camera.
#     - Throttling Logic:
#         - Maintains a dictionary to track the last alert time for each camera.

#--------------------------------------------------------------------------------

''' THE BLOCK BELOW allows the file to locate its postition and 
    find the root directory from its file path
    This is necessary to import the LLM_API module from the Frontend.Dashboard package,
    which is outside of the current directory structure.
'''
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)


if root_dir not in sys.path:
    sys.path.append(root_dir)

from Frontend.Dashboard.LLM_API import analyze_with_argus

#--------------------------------------------------------------------------------


app = FastAPI()

# This Initialize database when API starts
db = DatabaseHandler()
db.init_db()


#--------------------------------------------------------------------------------

'''This block is simalar, but uses the config.json file to set the throttle time, 
    which is also located in the Frontend.Dashboard directory.

    Maps the route from:
        -Frontend -> Dashboard -> config.json
'''

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
CONFIG_PATH = os.path.join(ROOT_DIR, "Frontend", "Dashboard", "config.json")

try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    THROTTLE_SECONDS = config.get("COOLDOWN_SECONDS", 5)

except FileNotFoundError:
    print(f"[Warning] config.json not found at {CONFIG_PATH}. Defaulting to 5s.")
    THROTTLE_SECONDS = 5

last_alert_time = {}

#--------------------------------------------------------------------------------


# Pydantic Model for incoming alert data (validates payload structure and types before processing)
class AlertPayload(BaseModel):
    timestamp: datetime
    confidence: float = Field(..., ge=0, le=1)
    camera_ID: str
    image_data: str

    class Config:
        extra = "forbid"

# Root endpoint checks the status of the API
@app.get("/")
def home():
    return {"message": "Object Detection Alert API is running"}

# Alert endpoint with throttling logic
@app.post("/trigger-alert")
def trigger_alert(payload: AlertPayload):
    current_time = time.time()
    camera = payload.camera_ID

    # Check if camera has sent an alert recently
    if camera in last_alert_time:
        elapsed = current_time - last_alert_time[camera]
        if elapsed < THROTTLE_SECONDS:

            # if its too soon, reject the alert
            return {
                "status": "throttled",
                "camera": camera,
                "message": f"Please wait {THROTTLE_SECONDS - int(elapsed)} more seconds before sending another alert."
            }

    # Update last alert time
    last_alert_time[camera] = current_time

    # Process the alert (for demonstration, we just print it)
    print("=== ALERT RECEIVED ===")
    print("Camera:", payload.camera_ID)
    print("Confidence:", payload.confidence)
    print("Time:", payload.timestamp)


    try:
        ai_description = analyze_with_argus(
            image_base64=payload.image_data,
            camera_id=payload.camera_ID,
            timestamp=str(payload.timestamp)
        )
    except Exception as e:
        ai_description = "AI analysis unavailable at the time of this alert."


    # Insert into database
    db.insert_event(
        camera_id=payload.camera_ID, 
        confidence=payload.confidence, 
        timestamp=str(payload.timestamp), 
        image_data=payload.image_data,
        description= ai_description
    )

    return {
        "status": "alert accepted",
        "camera": camera
    }
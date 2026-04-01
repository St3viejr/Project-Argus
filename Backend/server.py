from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from database import DatabaseHandler
import time  
import json
import os
import sys
import os

# 1. Calculate the path to the root Project-Argus folder
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

# 2. Add the root folder to Python's "search path"
if root_dir not in sys.path:
    sys.path.append(root_dir)

# 3. NOW you can safely import from Frontend
from Frontend.Dashboard.LLM_API import analyze_with_argus

''' This module contains the main FastAPI application and handles alert triggering with throttling.

Functionality:
    - Initializes the database on startup.
    - Defines a Pydantic model for incoming alert data.
    - Implements a POST endpoint to receive alerts, with throttling to prevent spamming from the same camera.
    -Throttling Logic:
        - Maintains a dictionary to track the last alert time for each camera.

'''


app = FastAPI()

# Initialize database when API starts
db = DatabaseHandler()
db.init_db()



#throttle setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = os.path.dirname(CURRENT_DIR)

# 2. Map the route from Frontend -> Dashboard -> config.json
CONFIG_PATH = os.path.join(ROOT_DIR, "Frontend", "Dashboard", "config.json")
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    # Default to 5 seconds if the file or key is missing
    THROTTLE_SECONDS = config.get("COOLDOWN_SECONDS", 5)
except FileNotFoundError:
    print(f"[Warning] config.json not found at {CONFIG_PATH}. Defaulting to 5s.")
    THROTTLE_SECONDS = 5

last_alert_time = {}




# Pydantic Model for incoming alert data
class AlertPayload(BaseModel):
    timestamp: datetime
    confidence: float = Field(..., ge=0, le=1)
    camera_ID: str
    image_data: str

    class Config:
        extra = "forbid"

# Root endpoint for health check
@app.get("/")
def home():
    return {"message": "Object Detection Alert API is running"}

# Alert endpoint with throttling logic
@app.post("/trigger-alert")
def trigger_alert(payload: AlertPayload):
    current_time = time.time()
    camera = payload.camera_ID

    # Traffic throttling logic: check if camera has sent an alert recently
    if camera in last_alert_time:
        elapsed = current_time - last_alert_time[camera]
        if elapsed < THROTTLE_SECONDS:
            # if too soon, reject alert
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
        # Note: Make sure the function name matches exactly what you imported from Gabe's script
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
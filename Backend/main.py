from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from database import init_db, insert_event
import time  

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
init_db()

# throttle setup
last_alert_time = {}  # track last alert time per camera
THROTTLE_SECONDS = 5  # minimum seconds between alerts per camera

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

    # Insert into database
    insert_event(payload)

    return {
        "status": "alert accepted",
        "camera": camera
    }
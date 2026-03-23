from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from database import init_db, insert_event
import time  # needed for throttling

app = FastAPI()

# ⭐ Initialize database when API starts
init_db()

# -------- THROTTLING SETUP --------
last_alert_time = {}           # track last alert time per camera
THROTTLE_SECONDS = 5           # minimum seconds between alerts per camera

# -------- Pydantic Model --------
class AlertPayload(BaseModel):
    timestamp: datetime
    confidence: float = Field(..., ge=0, le=1)
    camera_ID: str

    class Config:
        extra = "forbid"

# -------- ROOT ENDPOINT --------
@app.get("/")
def home():
    return {"message": "Object Detection Alert API is running"}

# -------- ALERT ENDPOINT WITH THROTTLING --------
@app.post("/trigger-alert")
def trigger_alert(payload: AlertPayload):
    current_time = time.time()
    camera = payload.camera_ID

    # --- TRAFFIC THROTTLING LOGIC ---
    if camera in last_alert_time:
        elapsed = current_time - last_alert_time[camera]
        if elapsed < THROTTLE_SECONDS:
            # Too soon, reject alert
            return {
                "status": "throttled",
                "camera": camera,
                "message": f"Please wait {THROTTLE_SECONDS - int(elapsed)} more seconds before sending another alert."
            }

    # Update last alert time
    last_alert_time[camera] = current_time

    # --- PROCESS ALERT ---
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
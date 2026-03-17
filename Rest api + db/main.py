from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from database import init_db, insert_event

app = FastAPI()

# ⭐ initialize database when API starts
init_db()


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


# -------- ALERT ENDPOINT --------
@app.post("/trigger-alert")
def trigger_alert(payload: AlertPayload):

    print("=== ALERT RECEIVED ===")
    print("Camera:", payload.camera_ID)
    print("Confidence:", payload.confidence)
    print("Time:", payload.timestamp)

    # ⭐ REQUIRED ASSIGNMENT STEP — store valid alert
    insert_event(payload)

    return {
        "status": "alert accepted",
        "camera": payload.camera_ID
    }
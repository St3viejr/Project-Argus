from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI()

# -------- Pydantic Model (from JSON Schema) --------
class AlertPayload(BaseModel):
    timestamp: datetime
    confidence: float = Field(..., ge=0, le=1)
    camera_ID: str

    class Config:
        extra = "forbid"


# -------- QUICK FIX ROOT ENDPOINT --------
@app.get("/")
def home():
    return {"message": "Object Detection Alert API is running"}


# -------- REQUIRED ASSIGNMENT ENDPOINT --------
@app.post("/trigger-alert")
def trigger_alert(payload: AlertPayload):

    print("=== ALERT RECEIVED ===")
    print("Camera:", payload.camera_ID)
    print("Confidence:", payload.confidence)
    print("Time:", payload.timestamp)

    return {
        "status": "alert accepted",
        "camera": payload.camera_ID
    }
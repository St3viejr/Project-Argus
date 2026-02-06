import json
from datetime import datetime, timezone

"""
This file follows OOP principles to create a modular and 
reusable EdgeLogicController class that can be easily 
extended for different security zones or detection types. 
"""

#The controller processes raw YOLO data, checks if it meets 
#the confidence threshold,
 
#Formats it according to the 'Alert Event JSON Schema' before 
#returning it for further use.   


class edge_controller:

    #Initializes the controller with a specific sensitivity level.
    def __init__(self, confidence_threshold=0.85):
        self.threshold = confidence_threshold

    #Internal check to see if detection meets requirements.
    def is_valid(self, confidence):
        return confidence >= self.threshold

    #Formats the data to match the Alert Event JSON Schema.
    def create_alert_payload(self, confidence, camera_id):
        return {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "confidence": round(confidence, 4),
            "camera_ID": str(camera_id)
        }

    #Main entry point: Filters and transforms raw YOLO data.
    def process_detection(self, raw_data):
        conf = raw_data.get("confidence", 0)
        cam_id = raw_data.get("camera_id", "UNKNOWN")

        if self.is_valid(conf):
            return self.create_alert_payload(conf, cam_id)
        
        return None
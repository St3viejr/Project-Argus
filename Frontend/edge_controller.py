from jsonschema import validate, ValidationError
from datetime import datetime, timezone
import base64
import time
import json

''' This the payload controller that lives on the edge (i.e. in the computer vision node). 

Functinoality:
    -Formats the payload 
    -Checks the confidence threshold before sending to the backend. 
    -Implements a cooldown mechanism to prevent spamming alerts. 
    -Alert schema is loaded from a JSON file and used to validate the 
    payload structure before sending.
'''


class EdgeLogicController:
    def __init__(self, confidence_threshold=0.25, cooldown_seconds=2.0, schema_path="Frontend/alert_schema.json", enable_schema_validation=True):
        self.threshold = confidence_threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time = 0
        self.alert_schema = {}
        
        # Load the schema rulebook into memory once upon initialization
        if enable_schema_validation:
            try:
                with open(schema_path, "r") as file:
                    self.alert_schema = json.load(file)
            except FileNotFoundError:
                print(f"[Edge Controller Error] Schema file {schema_path} not found!")

    def is_valid_confidence(self, confidence):
        return confidence >= self.threshold

    def is_cooldown_ready(self):
        return (time.time() - self.last_alert_time) > self.cooldown_seconds

    def create_alert_payload(self, confidence, camera_id, image_data):
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "confidence": round(confidence, 3),
            "camera_ID": str(camera_id),
            "image_data": image_data
        }

    def process_detection(self, confidence, camera_id, image_data):
        # Main entry point: Filters, formats, and validates raw YOLO data.
        # Returns the payload if it passes all checks, otherwise returns None.

        if not self.is_valid_confidence(confidence):
            return None
            
        if not self.is_cooldown_ready():
            return None

        payload = self.create_alert_payload(confidence, camera_id, image_data)

        # Validate Schema from alert_schema.json
        try:
            if self.alert_schema:
                validate(instance=payload, schema=self.alert_schema)
            
            # If everything passes, it updates the cooldown timer and returns the payload
            self.last_alert_time = time.time()
            return payload
            
        except ValidationError as e:
            print(f"[Schema Error] Payload blocked before sending: {e.message}")
            return None

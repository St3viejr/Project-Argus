import os
import cv2
import ctypes
import requests
import threading
import queue
import time
import base64
from ultralytics import YOLO
from edge_controller import EdgeLogicController

'''Added Sections (1-5) for clarity, because the file is a little long with ~180 lines of code.

Outline:
1. Setup Alert Queue, API Worker Thread, and Edge Controller
2. Computer Vision Loop with Custom HUD
3. Alert Creation and Queueing Logic
4. Display and Window Management
5. GRACEFUL SHUTDOWN
'''


#-----------------------------------------------------------------------
# Section 1: Setup Alert Queue, API Worker Thread, and Edge Controller
#-----------------------------------------------------------------------


# Create the "bucket" to hold alerts (max 10 to prevent memory overflow)
alert_queue = queue.Queue(maxsize=10)

def api_worker():
    # Background consumer thread that talks to FastAPI server.
    api_url = "http://127.0.0.1:8000/trigger-alert" 
    
    while True:
        payload = alert_queue.get()
        # Stops signal
        if payload is None: 
            break
            
        try:
            # Sends the data; 2-second timeout so it doesn't hang
            res = requests.post(api_url, json=payload, timeout=2.0)
            print(f"[API Thread] Alert Sent Successfully! Backend returned: {res.status_code}")
        except Exception as e:
            print(f"[API Thread Warning] Failed to reach backend: {e}")
            
        alert_queue.task_done()

# Start the worker thread in the background before the camera opens
worker_thread = threading.Thread(target=api_worker, daemon=True)
worker_thread.start()

# Initialize the Edge Controller
edge_logic = EdgeLogicController(confidence_threshold=0.25, cooldown_seconds=2.0)


# Loads models (If you want to switch out models, you would do it here)
human_tracker = YOLO('Frontend/obj_models/0_Standard_YOLO26n.onnx', task='detect')  # Your standard/segmented model
weapon_sniper = YOLO('Frontend/obj_models/1_Banana_Sniper.onnx', task='detect')  # Your custom A100 weapon weights

# Opens webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


#----------------------------------------------------------
# Section 2: Computer Vision Loop with Custom HUD
#----------------------------------------------------------


try:
    # Custom colors for object bounding boxes and labels
    argus_cyan = (255, 255, 0) # For humans
    argus_red = (0, 0, 255)    # For weapons

    # Frame skipping for performance optimization
    frames_to_skip = 3 
    frame_count = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Camera disconnected.")
            break

        if os.path.exists("shutdown.signal"):
            break
        frame_count += 1

        # Skip frames so the CPU doesn't overclock
        if frame_count % frames_to_skip != 0:
            continue

        # Looks for "Person" first: classes=[0] strictly limits standard model to finding people
        human_results = human_tracker.predict(source=frame, classes=[0], conf=0.5, imgsz=320, verbose=False)
        
        # Draw the human boxes/masks first; keeps label, doesnt show confidence
        annotated_frame = human_results[0].plot(conf=False)

        # "CASCADED SNIPER": Only look for bananas IF a human is on screen
        if len(human_results[0].boxes) > 0:
            
            # Runs the weapon sniper model
            weapon_results = weapon_sniper.predict(source=frame, conf=0.5, imgsz=320, verbose=False)

            # Custom hud (Red Boxes + Threat Text)
            results = weapon_results[0]
            boxes = results.boxes

            # If we find weapons, we draw them manually
            if len(boxes) > 0:
                for box in boxes:
                    c1, c2, c3, c4 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(c1), int(c2), int(c3), int(c4)

                    # Draws the Red Bounding Box
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), argus_red, 2)

                    # Define the custom label (No confidence number)
                    label_text = "THREAT DETECTED"
                    font_scale = 0.5
                    font_thickness = 1
                    
                    # Get text size to draw the background box
                    (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
                    
                    # Draw the solid red background rectangle for the text
                    cv2.rectangle(annotated_frame, (x1, y1 - h - 5), (x1 + w, y1), argus_red, -1)
                    
                    # Draw the text in white on top of the red background
                    cv2.putText(annotated_frame, label_text, (x1, y1 - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)
            

                # Grab the confidence of the first detected weapon
                try:
                    conf = float(boxes.conf[0].cpu().numpy())
                except AttributeError:
                    conf = float(boxes.conf[0]) # Fallback if CPU mapping isn't needed in ONNX
                

#-----------------------------------------------------------------------
# Section 3: Alert Creation and Queueing Logic
#-----------------------------------------------------------------------


                # Capture the exact frame where the weapon was seen
                _, buffer = cv2.imencode('.jpg', annotated_frame)
                img_str = base64.b64encode(buffer).decode('utf-8')

                # Lets the edge controller do the filtering, validation, and payload creation
                payload = edge_logic.process_detection(
                    confidence=conf, 
                    camera_id="Optic-1-i3", 
                    image_data=img_str
                )
                
                # If the controller returns a valid payload, we queue it
                if payload is not None:
                    if not alert_queue.full():
                        alert_queue.put(payload)
#-----------------------------------------------------------------------


#-----------------------------------------------------------------------
# Section 4: Display and Window Management
#-----------------------------------------------------------------------


        # Shows the live feed
        cv2.imshow('Project Argus: Dual Tracking', annotated_frame)
        
        # Dynamically calculate the top-right corner
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)   # Gets your primary monitor's width
        window_width = annotated_frame.shape[1]     # Gets the exact width of your camera feed
        
        # Move the window so its right edge hits the right wall of your monitor
        cv2.moveWindow('Project Argus: Dual Tracking', screen_width - window_width, 0)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


#-----------------------------------------------------------------------
# 5. GRACEFUL SHUTDOWN
#-----------------------------------------------------------------------

except KeyboardInterrupt:
    pass # Let the master script handle the terminal announcement

#if all else fails, this catches it
finally:
    cap.release()
    cv2.destroyAllWindows()
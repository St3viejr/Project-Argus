from dotenv import load_dotenv
import numpy as np
import requests
import base64
import time
import json
import cv2
import os

# ''' This module is responsible for interfacing with the OpenRouter API,
#     to analyze security camera images in real-time.

#     Funtionality:
#     - Captures video feed from the local webcam (or can be adapted to read from IP cameras)
#     - Encodes each frame as a base64 string and sends it to the OpenRouter API
#     - Receives a structured response classifying the threat level, summary, and recommended action
#     - Prints the analysis results to the console in real-time
#     - Uses a config.json file to set parameters like confidence threshold and cooldown time between API calls

#----------------------------------------------------------------------------------------------

'''
    Outline:
        1: Load API key and configuration
        2: Define the function to send images to OpenRouter and receive analysis
        3: Main loop to capture video frames and analyze them in real-time
'''


#----------------------------------------------------------
# 1: Load API key and configuration
#----------------------------------------------------------


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
dotenv_path = os.path.join(root_dir, ".env")

load_dotenv(dotenv_path)
API_KEY = os.getenv("OPENROUTER_API_KEY")

# check to ensure the API key is loaded
if not API_KEY:
    print(f"ERROR: Could not find API Key at {dotenv_path}")
else:
    print(f"Key Loaded - Path: {dotenv_path}")


#----------------------------------------------------------
# 2: Define the function to send images to OpenRouter and receive analysis
#----------------------------------------------------------


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")
config = {}

try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    COOLDOWN = config.get("COOLDOWN_SECONDS", 5)
    CONF_THRESHOLD = config.get("CONFIDENCE_THRESHOLD", 0.25)
except FileNotFoundError:
    print(f"[Warning] config.json not found at {CONFIG_PATH}. Using defaults.")
    COOLDOWN = 5
    CONF_THRESHOLD = 0.25

MODEL_NAME = config.get("LLM_MODEL")


# Shrinks the image to 512x512 and lowers JPEG quality to reduce base64 size.
def compress_payload(base64_str):
    try:
        img_bytes = base64.b64decode(base64_str)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        img_resized = cv2.resize(img, (512, 512))
        _, buffer = cv2.imencode('.jpg', img_resized, [cv2.IMWRITE_JPEG_QUALITY, 40])
        return base64.b64encode(buffer).decode('utf-8')
    
    except Exception as e:
        print(f"Compression failed: {e}")
        return base64_str
    

#----------------------------------------------------------
# 3: Analyze the image with OpenRouter and print results
#----------------------------------------------------------


# Sends a security camera image to the OpenRouter API for threat analysis.
def analyze_with_argus(image_base64, camera_id=None, timestamp=None):
    if not API_KEY:
        return "SYSTEM ERROR: OPENROUTER_API_KEY missing from .env file."

    optimized_base64 = compress_payload(image_base64)

    prompt = f"Camera ID: {camera_id}\nTimestamp: {timestamp}\nAnalyze this security camera image and determine if there is suspicious activity."
    
    #system prompt for the LLM to set the context and expected response format
    system_instruction = """
    You are Project Argus, an automated security threat analysis AI.

    Rules:
    - Be professional, analytical, and cold
    - Use short, direct sentences
    - No emojis
    - Do not overreact to normal situations

    You must:
    - Classify threat level (LOW, MEDIUM, HIGH)
    - Provide a short summary
    - Recommend an action

    Format:
    Threat Level: <LOW/MEDIUM/HIGH>
    <Space>
    Summary: <short sentence>
    <Space>
    Action: <recommended action>
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # OpenRouter/OpenAI Standard Multimodal Payload
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{optimized_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status() # Catches 402 Payment Required or 429 Rate Limit errors
        
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        return f"API Connection Error: {e}"
    except KeyError:
        return f"Unexpected API Response Format: {response.text}"


#----------------------------------------------------------
# 4: Main loop to capture video frames 
#----------------------------------------------------------


if __name__ == "__main__":
    import cv2

    cap = cv2.VideoCapture(0)
    print("Project Argus Vision System Online (OpenRouter Mode).")
    print("Press 'Q' to quit.")
    print("-" * 50)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode frame directly to base64
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode()

        try:
            result = analyze_with_argus(
                image_base64=image_base64,
                camera_id="LOCAL_CAM",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            print("\n[ALERT]")
            print(result)
        except Exception as e:
            print(f"System Error: {e}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
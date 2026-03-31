# gemini.py
import json
import base64
import time
from google import genai
from google.genai import types
from PIL import Image
import io

# =========================
# LOAD CONFIG
# =========================
with open('config.json', 'r') as f:
    config = json.load(f)

# =========================
# GEMINI SETUP (ARGUS)
# =========================
client = genai.Client(api_key=config["GEMINI_API_KEY"])

argus_config = types.GenerateContentConfig(
    system_instruction="""
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
    Summary: <short sentence>
    Action: <recommended action>
    """,
    temperature=0.2
)

chat = client.chats.create(
    model=config.get("LLM_MODEL", "gemini-1.5"),
    config=argus_config
)

# =========================
# ANALYSIS FUNCTION
# =========================
def analyze_with_argus(image_base64, camera_id=None, timestamp=None):
    """
    Sends a security camera image to the Gemini API for threat analysis.
    """

    # Convert base64 → bytes → PIL Image
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_bytes))

    prompt = f"""
Camera ID: {camera_id}
Timestamp: {timestamp}

Analyze this security camera image and determine if there is suspicious activity.
"""

    #Send PIL image directly (this is the correct format)
    response = chat.send_message([
        prompt,
        image
    ])

    return response.text

# =========================
# LOCAL CAMERA LOOP (optional)
# =========================
if __name__ == "__main__":
    import cv2

    cap = cv2.VideoCapture(0)
    print("Project Argus Vision System Online.")
    print("Press 'Q' to quit.")
    print("-" * 50)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

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
            print(f"Error communicating with Gemini API: {e}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

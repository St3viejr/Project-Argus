# Project Argus – Physical Security Operations Center (PSOC)

**Team:** Estevan, Paul, Simon, Gabe

**Context:** CSI 3370 - Software Engineer & Practice

Project Argus is an automated physical security threat detection system. It utilizes a "Cascaded Sniper" computer vision architecture to monitor camera feeds, validate threat data on the edge, generate AI-driven threat descriptions, and push real-time alerts to a centralized Physical Security Operations Center (PSOC) dashboard and mobile devices via Discord.

## Key Features
* **Cascaded Sniper Vision Architecture:** Uses a lightweight YOLO model to detect human presence, which dynamically triggers a secondary custom-trained model (e.g., Banana Sniper/Firearm) to isolate specific threats.
* **Edge Validation & Throttling:** Filters raw tracking data, enforces strict confidence thresholds, and uses a JSON schema to validate payload structure before transmission.
* **LLM Threat Analysis:** Integrates with OpenRouter (GPT-4o-mini) to instantly analyze captured threat frames and generate professional security summaries and action recommendations.
* **Real-Time Discord Push Notifications:** Instantly routes high-priority alerts (with embedded base64 images and AI descriptions) to security personnel via Discord webhooks.
* **Live PSOC Dashboard:** A Streamlit-powered command center that auto-refreshes to display active threats and maintains an SQLite-backed historical log.
* **Unified Master Launcher:** A single orchestrator script that concurrently spins up the Backend, Frontend, and Vision nodes with graceful shutdown capabilities.

---

## System Architecture

The system is modularly split into three concurrent nodes:

1. **Vision Node (`ProjectArgus_ComputerVision.py`)**: The OpenCV camera loop. Detects threats, draws custom HUD bounding boxes, encodes frames to base64, and pushes them to a background worker thread.
2. **Edge Controller (`edge_controller.py`)**: The gatekeeper. Validates bounding box data against `alert_schema.json`, enforces cooldown timers to prevent API spam, and formats the transmission payload.
3. **Backend / Frontend**:
   * **FastAPI Server (`Backend/server.py`)**: Receives validated payloads, requests LLM descriptions via `LLM_API.py`, fires off the Discord webhook, and securely logs the event to `alerts.db`.
   * **Streamlit Dashboard (`Frontend/Dashboard/app.py`)**: A live SOC interface displaying real-time threat snapshots and a scrollable Historical Threat Log.

---

## Directory Structure

```text
├── Backend
│   ├── database.py             # SQLite connection and schema logic
│   └── server.py               # FastAPI backend & Discord webhook dispatcher
│
├── Frontend
│   ├── Dashboard
│   │   ├── LLM_API.py          # OpenRouter integration for threat analysis
│   │   ├── app.py              # Streamlit PSOC Dashboard
│   │   └── config.json         # Centralized configuration (API keys, models, thresholds)
│   │
│   ├── ProjectArgus_ComputerVision.py # Main OpenCV & Ultralytics tracking loop
│   ├── alert_schema.json       # JSON validation rules for payload security
│   ├── edge_controller.py      # Edge payload formatting & cooldown logic
│   └── obj_models
│       ├── 0_Standard_YOLO26n.onnx
│       ├── 1_Banana_Sniper.onnx
│       ├── 2_firearm.onnx
│       └── 3_(untested) - firearmV2.onnx
│
├── README.md
├── requirements.txt            # Python dependencies (e.g., opencv-python, ultralytics)
├── run_system.py               # Unified multi-node Python launcher
└── start_argus.bat             # Windows one-click auto-installer & launcher
```
*(Note: `.env`, `venv/`, and `__pycache__/` directories are required locally but intentionally excluded from version control via `.gitignore` for security).*

---

## Prerequisites & Setup

**1. Clone the repository:**
```bash
git clone https://github.com/St3viejr/Project-Argus.git
cd Project-Argus
```

**2. Setup your Environment Variables (`.env`):**
Because Project Argus uses the OpenRouter API, you must create a `.env` file in the root directory of the project to securely store your keys.
* Create a file named exactly `.env` in the root folder.
* Add the following line with your active key:
  ```text
  OPENROUTER_API_KEY= "your_api_key_here"
  ```

**3. Configure System Variables:**
All system thresholds, file paths, and external webhooks are centralized. Open `Frontend/Dashboard/config.json` to modify:
* Confidence thresholds and API cooldowns.
* YOLO model paths.
* Discord Webhook URL for push notifications.

**4. Install Dependencies:**
* **Windows (Automated):** Simply double-click `start_argus.bat`! It will automatically build your virtual environment, install all packages from `requirements.txt`, and boot the system.
* **Mac/Linux (Manual):**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

---

## Usage & Operation

Project Argus utilizes a unified launcher to orchestrate all three nodes simultaneously.

* **Windows:** Double-click `start_argus.bat` (or create a desktop shortcut).
* **Mac/Linux:** Run `python run_system.py` in your terminal.

**The Boot Sequence:**
1. **[1/3]** Boots the FastAPI Backend on `http://127.0.0.1:8000`.
2. **[2/3]** Launches the Streamlit PSOC Dashboard on `http://localhost:8501`.
3. **[3/3]** Warms up the ONNX Neural Networks and snaps the live camera feed to the top right of your screen.

**How to trigger an alert:**
Place a trained threat object (e.g., a banana) in front of the camera while a human is in the frame. The system will draw a red bounding box, lock the payload, hit the LLM for a description, update the dashboard, and ping Discord.

### Graceful Shutdown
To safely terminate the system and release camera hardware, do **NOT** force-close the terminal. Instead:
* Click the red **"SHUTDOWN SYSTEM"** button in the Streamlit Dashboard sidebar.
* **OR** press `CTRL + C` in the master terminal running `run_system.py`. 
* The orchestrator will safely terminate the API thread, drop the database connection, and release the webcam.

# Project Argus - Physical Security Operations Center (PSOC)

**Team:** Estevan, Paul, Simon, Gabe

**Context:** CSI 3370 - Software Engineer & Practice

Project Argus is an automated physical security threat detection system. It utilizes a "Cascaded Sniper" computer vision architecture to monitor camera feeds, validate threat data on the edge, generate AI-driven threat descriptions, and push real-time alerts to a centralized Physical Security Operations Center (PSOC) dashboard and mobile devices via Discord. 

## Key Features & Optimizations
* **Cascaded Sniper Vision Architecture:** Uses an ultra-fast INT8 YOLO model to detect human presence, which dynamically triggers a secondary high-precision FP16 custom-trained model (e.g., Banana Sniper/Firearm) to isolate specific threats.
* **Hardware Acceleration (REQ-NF-03):** Bypasses standard generic runtimes by natively compiling models to OpenVINO. This taps into Intel DL Boost (VNNI instructions) to completely eliminate CPU bottlenecks, achieving a stable 28-34 FPS on edge hardware.
* **Edge Validation & Throttling:** Filters raw tracking data, enforces strict confidence thresholds, and uses a JSON schema to validate payload structure before transmission.
* **LLM Threat Analysis:** Integrates with OpenRouter (GPT-4o-mini) to instantly analyze captured threat frames and generate professional security summaries and action recommendations.
* **Real-Time Discord Push Notifications:** Instantly routes high-priority alerts (with embedded base64 images and AI descriptions) to security personnel via Discord webhooks.
* **Live PSOC Dashboard:** A Streamlit-powered command center that auto-refreshes to display active threats and maintains an SQLite-backed historical log.
* **Unified Master Launcher:** A single orchestrator script that concurrently spins up the Backend, Frontend, and Vision nodes with graceful shutdown capabilities.

---

## System Architecture

The system is modularly split into three concurrent nodes:

1. **Vision Node (`ProjectArgus_ComputerVision.py`)**: The OpenCV camera loop. Detects threats via hardware-accelerated OpenVINO/ONNX inference, calculates real-time FPS, draws custom HUD bounding boxes, encodes frames to base64, and pushes them to a background worker thread.
2. **Edge Controller (`edge_controller.py`)**: The gatekeeper. Validates bounding box data against `alert_schema.json`, enforces cooldown timers to prevent API spam, and formats the transmission payload.
3. **Backend / Frontend**:
   * **FastAPI Server (`Backend/server.py`)**: Receives validated payloads, requests LLM descriptions via `LLM_API.py`, fires off the Discord webhook, and securely logs the event to `alerts.db`.
   * **Streamlit Dashboard (`Frontend/Dashboard/app.py`)**: A live SOC interface displaying real-time threat snapshots and a scrollable Historical Threat Log.

---

## Directory Structure

```text
Project-Argus/ (459,877)        # Total lines (1,249 code/config + 458,628 models)
│
├── Backend/
│   ├── database.py (61)        # SQLite connection and schema logic
│   └── server.py (198)         # FastAPI backend & Discord webhook dispatcher
│
├── Frontend/
│   ├── Dashboard/
│   │   ├── LLM_API.py (214)    # OpenRouter integration for threat analysis
│   │   ├── app.py (195)        # Streamlit PSOC Dashboard
│   │   └── config.json (10)    # Centralized configuration (API keys, models, thresholds)
│   │
│   ├── ProjectArgus_ComputerVision.py (230) # Main OpenCV & Ultralytics tracking loop
│   ├── alert_schema.json (25)  # JSON validation rules for payload security
│   ├── edge_controller.py (71) # Edge payload formatting & cooldown logic
│   └── obj_models/
│       ├── FP16_BS_openvino_model/
│       │   ├── best_a100.bin (22829)
│       │   ├── best_a100.xml (17784)
│       │   └── metadata.yaml (24)
│       │
│       ├── INT8_SY26_openvino_model/
│       │   ├── yolo26n.bin (63070)
│       │   ├── yolo26n.xml (25505)
│       │   └── metadata.yaml (103)
│       │
│       ├── 0_Standard_YOLO26n.onnx (68935)
│       ├── 1_Banana_Sniper.onnx (68969)
│       ├── 2_firearm.onnx (68520)
│       ├── 3_(640) - firearmV2.onnx (68366)
│       ├── best_a100.pt (25499)
│       └── yolo26n.pt (29024)
│
├── README.md (117)
├── requirements.txt (11)       # Python dependencies (e.g., opencv-python, openvino, ultralytics)
├── run_system.py (94)          # Unified multi-node Python launcher
└── start_argus.bat (23)        # Windows one-click auto-installer & launcher
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
  OPENROUTER_API_KEY="your_api_key_here"
  ```

**3. Configure System Variables (`config.json`):**
All system thresholds, file paths, and external webhooks are centralized. Open Frontend/Dashboard/config.json to configure the system.

* Setup Discord Alerts: Paste your Discord channel's webhook URL into the configuration file to enable push notifications:
  ```json
  "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
  ```
  
* Select Hardware Engine: Project Argus supports both native Intel hardware acceleration (OpenVINO) and universal cross-platform inference (ONNX). You must set your model paths based on your machine's CPU:
  * For Intel CPUs (Maximum Performance): Point the config to the OpenVINO folders.
    ```json
    "YOLO_HUMAN_MODEL": "Frontend/obj_models/INT8_SY26_openvino_model/",
    "WEAPON_SNIPER_MODEL": "Frontend/obj_models/FP16_BS_openvino_model/"
    ```

  * For Mac / Apple Silicon / AMD (Universal Compatibility): Point the config to the standard ONNX files.
    ```json
    "YOLO_HUMAN_MODEL": "Frontend/obj_models/0_Standard_YOLO26n.onnx",
    "WEAPON_SNIPER_MODEL": "Frontend/obj_models/1_Banana_Sniper.onnx"
    ```

**4. Install Dependencies:**
* **Windows (Automated):** Simply double-click `start_argus.bat`. It will automatically build your virtual environment, install all packages from `requirements.txt`, and boot the system.
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
3. **[3/3]** Warms up the Neural Networks (OpenVINO or ONNX) into the CPU cache and snaps the live camera feed to the top right of your screen.

**How to trigger an alert:**
Place a trained threat object (e.g., a banana) in front of the camera while a human is in the frame. The system will draw a red bounding box, lock the payload, hit the LLM for a description, update the dashboard, and ping Discord.

### Graceful Shutdown
To safely terminate the system and release camera hardware, do **NOT** force-close the terminal. Instead:
* Click the red **"SHUTDOWN SYSTEM"** button in the Streamlit Dashboard sidebar.
* **OR** press `CTRL + C` in the master terminal running `run_system.py`. 
* The orchestrator will safely terminate the API thread, drop the database connection, and release the webcam.

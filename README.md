Temp - Readme (still need final modules)

# Project Argus – Physical Security Operations Center (PSOC)

**Team:** Estevan, Paul, Simon, Gabe

**Context:** CSI 3370 - Software Engineering & Practice

Project Argus is an automated physical security threat detection system. It utilizes a "Cascaded Sniper" computer vision architecture to monitor camera feeds, validate threat data on the edge, and push real-time alerts to a centralized Physical Security Operations Center (PSOC) dashboard.

## System Architecture

The system is modularly split into three concurrent nodes:

1. **Vision Node (`ProjectArgus_ComputerVision.py`)**: Uses a dual-YOLO setup. A lightweight primary model (`0_Standard_YOLO26n.onnx`) scans for human presence. If a human is detected, a secondary custom-trained model (`1_Banana_Sniper.onnx`) is triggered to isolate specific threats. Includes dynamic window positioning for clean desktop layouts.
2. **Edge Controller (`edge_controller.py`)**: Acts as a gatekeeper. It processes raw bounding box data, enforces confidence thresholds, applies cooldown timers to prevent database spam, and validates payloads against a strict JSON schema before transmitting.
3. **Backend / Frontend**: 
   * **FastAPI Backend (`Backend/main.py`)**: Receives validated threat payloads and logs them securely into an SQLite database (`alerts.db`).
   * **Streamlit Dashboard (`Frontend/app.py`)**: A live, auto-refreshing SOC interface that displays real-time threat snapshots alongside a scrollable Historical Threat Log.

---

## Installation & Setup

**1. Clone the repository and navigate to the project root:**
```bash
git clone [https://github.com/St3viejr/Project-Argus.git](https://github.com/St3viejr/Project-Argus.git)
cd Project-Argus
```

**2. Setup Environment & Install Dependencies:**

* **Windows (Automated):**
  Simply double-click the `start_argus.bat` file! It will automatically detect if it is your first time running the project, build your virtual environment, and install all required packages from `requirements.txt` before launching.

* **Mac/Linux (Manual):**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

**3. Add your Model Weights:**
Ensure your YOLO ONNX weights (`0_Standard_YOLO26n.onnx` and `1_Banana_Sniper.onnx`) are placed inside the `Frontend/obj_models` directory.

---

## Usage

Project Argus includes a unified launcher that spins up the backend, frontend, and vision nodes concurrently. 

* **Windows:** Double-click `start_argus.bat` (or create a desktop shortcut to it).
* **Mac/Linux:** Run `python run_system.py` in your terminal.

The launcher will initialize the startup sequence:
1. Boots the **FastAPI Backend** on `http://127.0.0.1:8000`.
2. Launches the **Streamlit PSOC Dashboard** on `http://localhost:8501`.
3. Warms up the **ONNX Neural Networks**, activates the webcam feed, and snaps it to the top right of your screen.

**To shut down the system:** Click the red **"SHUTDOWN SYSTEM"** button in the Streamlit Dashboard sidebar. This triggers a `shutdown.signal` that gracefully breaks the camera loop, releases the hardware, and terminates all background processes simultaneously. (You can also press `CTRL+C` in the master terminal).

---

## Directory Structure
```text
Project-Argus/
│
├── Backend/
│   ├── main.py                 # FastAPI server & endpoints
│   ├── database.py             # SQLite connection logic
│   └── alerts.db               # Threat event database (auto-generated)
│
├── Frontend/
│   ├── obj_models/
│   │   ├── 0_Standard_YOLO26n.onnx # Primary human tracker weights
│   │   └── 1_Banana_Sniper.onnx    # Custom threat detection weights
│   ├── app.py                  # Streamlit SOC Dashboard
│   ├── ProjectArgus_ComputerVision.py  # OpenCV & Ultralytics tracking
│   ├── edge_controller.py      # Payload formatting & schema validation
│   └── alert_schema.json       # JSON validation rules
│
├── run_system.py               # Unified multi-node launcher
├── start_argus.bat             # Windows one-click auto-installer & launcher
├── requirements.txt            # Python dependencies
└── .gitignore
```

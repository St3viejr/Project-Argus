Temp - Readme (still need final modules)

# Project Argus – Physical Security Operations Center (PSOC)

**Team:** Estevan, Paul, Simon, Gabe

**Context:** CSI 3370 - Software Engineer & Practice

Project Argus is an automated physical security threat detection system. It utilizes a "Cascaded Sniper" computer vision architecture to monitor camera feeds, validate threat data on the edge, and push real-time alerts to a centralized Physical Security Operations Center (PSOC) dashboard.

## System Architecture

The system is modularly split into three concurrent nodes:

1. **Vision Node (`ProjectArgus_ComputerVision.py`)**: Uses a dual-YOLO setup. A lightweight primary model (`0_Standard_YOLO26n.onnx`) scans for human presence. If a human is detected, a secondary custom-trained model (`1_Banana_Sniper.onnx`) is triggered to isolate specific threats.

2. **Edge Controller (`edge_controller.py`)**: Acts as a gatekeeper. It processes raw bounding box data, enforces confidence thresholds, applies cooldown timers to prevent database spam, and validates payloads against a strict JSON schema before transmitting.

3. **Backend / Frontend**: 
   * **FastAPI Backend (`Backend/main.py`)**: Receives validated threat payloads and logs them securely into an SQLite database (`alerts.db`).
   * **Streamlit Dashboard (`Frontend/app.py`)**: A live, auto-refreshing SOC interface that displays the most recent threat snapshots alongside full historical logs.

---

## Installation & Setup

**1. Clone the repository and navigate to the project root:**
```bash
git clone https://github.com/St3viejr/Project-Argus.git
cd Project-Argus
```

**2. Create and activate a virtual environment:**
* **Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **Mac/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

**3. Install the required dependencies:**
```bash
pip install -r requirements.txt
```

**4. Add your Model Weights:**
Ensure your YOLO ONNX weights (`0_Standard_YOLO26n.onnx` and `1_Banana_Sniper.onnx`) are placed inside the `Frontend/obj_models` directory .

---

## Usage

Project Argus includes a unified launcher that spins up the backend, frontend, and vision nodes concurrently. 

To bring the system online, simply run:
```bash
python run_system.py
```

The launcher will initialize the startup sequence:
1. Boots the **FastAPI Backend** on `http://127.0.0.1:8000`.
2. Launches the **Streamlit SOC Dashboard** on `http://localhost:8501`.
3. Warms up the **ONNX Neural Networks** and activates the webcam feed.

**To shut down the system:** Press `CTRL+C` in the terminal. The launcher will catch the interrupt and gracefully terminate all three background processes.

## Directory Structure
```text
Project-Argus/
│
├── Backend/
│   ├── main.py                 # FastAPI server & endpoints
│   ├── database.py             # SQLite connection logic
│   └── alerts.db               # Threat event database
│
├── Frontend/
│   ├── app.py                  # Streamlit SOC Dashboard
│   ├── ProjectArgus_ComputerVision.py  # OpenCV & Ultralytics tracking
│   ├── edge_controller.py      # Payload formatting & schema validation
│   ├── alert_schema.json       # JSON validation rules
│   ├── 2_yolo26n.onnx          # Primary human tracker weights
│   └── best_a100.onnx          # Custom threat detection weights
│
├── run_system.py               # Unified multi-node launcher
├── requirements.txt            # Python dependencies
└── .gitignore
```

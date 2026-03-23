import subprocess
import sys
import time

''' This is the master script that orchestrates the entire Project Argus system.

It will activate the 3 main components in 1 go:
    1. FastAPI Backend (main.py)
    2. Streamlit Dashboard (app.py)
    3. Computer Vision Node (ProjectArgus_ComputerVision.py)
'''


#-----------------------------------------------------------------------
# YOU ONLY NEED TO RUN THIS FILE TO START THE ENTIRE SYSTEM.
#-----------------------------------------------------------------------


def start_project_argus():
    processes = []
    try:
        print("========================================")
        print("  INITIALIZING PROJECT ARGUS SYSTEM...  ")
        print("========================================")
        
        # 1. Start the FastAPI Backend (main.py)
        print("\n[1/3] Activating FastAPI Backend (main.py)...")
        # sys.executable ensures it uses your current active Python/Conda environment
        # Uses the Uvicorn module to explicitly host the 'app' object inside main.py
        p_backend = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"], cwd="Backend")
        processes.append(p_backend)
        
        time.sleep(3) 

        # 2. Start the Streamlit Dashboard (app.py)
        print("[2/3] Activating Streamlit SOC Dashboard (app.py)...")
        p_frontend = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "Frontend/app.py"])
        processes.append(p_frontend)
        
        time.sleep(3) 

        # 3. Start the Computer Vision Node
        print("[3/3] Activating OpenCV Vision Node...")
        p_vision = subprocess.Popen([sys.executable, "Frontend/ProjectArgus_ComputerVision.py"])
        processes.append(p_vision)

        time.sleep(9)

        print("\n========================================")
        print("  SYSTEM ONLINE. PRESS CTRL+C TO QUIT.  ")
        print("========================================")
        
        # Keep the master script alive while the 3 subsystems run in the background
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        # Graceful Shutdown: Ctrl+C kills all 3 processes cleanly
        print("\n\n[System] Shutdown signal received. Terminating all nodes...")
        for p in processes:
            p.terminate()
        print("[System] Project Argus is offline.")

if __name__ == "__main__":
    start_project_argus()
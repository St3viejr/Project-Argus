@echo off
title Project Argus - Mission Control
cd /d "%~dp0"

:: Check if the virtual environment exists
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo ========================================
    echo   FIRST-TIME SETUP DETECTED
    echo   Building virtual environment...
    echo ========================================
    python -m venv venv
    call venv\Scripts\activate
    
    echo Installing dependencies. This may take a minute...
    pip install -r requirements.txt
    
    echo Setup complete! Booting Project Argus...
    timeout /t 3 /nobreak > NUL
) ELSE (
    call venv\Scripts\activate
)

python run_system.py
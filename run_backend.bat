@echo off
REM Vehicle Pass Registration System - Backend Startup Script for Windows

echo Starting Vehicle Pass Registration Backend...

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Copying from .env.example...
    copy .env.example .env
    echo Please edit .env file with your AWS credentials before running again.
    pause
    exit /b 1
)

REM Run backend
echo Starting Flask backend on http://0.0.0.0:5000
python backend/app.py

pause

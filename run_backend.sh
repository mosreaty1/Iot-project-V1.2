#!/bin/bash

# Vehicle Pass Registration System - Backend Startup Script

echo "Starting Vehicle Pass Registration Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your AWS credentials before running again."
    exit 1
fi

# Run backend
echo "Starting Flask backend on http://0.0.0.0:5000"
python backend/app.py

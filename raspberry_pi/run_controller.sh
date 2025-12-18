#!/bin/bash

# Vehicle Pass Registration System - Raspberry Pi Controller Startup Script

echo "Starting Vehicle Access Controller..."

# Check Python version
python3 --version

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Check if running on Raspberry Pi
if [ ! -f "/proc/device-tree/model" ]; then
    echo "Warning: Not running on Raspberry Pi - using mock hardware mode"
else
    MODEL=$(cat /proc/device-tree/model)
    echo "Detected: $MODEL"
fi

# Run controller
echo "Starting main controller..."
python3 main.py

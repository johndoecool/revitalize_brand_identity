#!/bin/bash

# Brand Service Startup Script

echo "Starting Brand Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the service
echo "Starting FastAPI server on http://localhost:8001"
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

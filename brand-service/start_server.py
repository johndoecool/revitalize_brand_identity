#!/usr/bin/env python3
"""
Start script for the Brand Service API
"""
import sys
import os
import uvicorn

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the script directory to Python path (where app module is located)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Change working directory to script location
os.chdir(script_dir)

print(f"Starting server from: {script_dir}")
print(f"Python path: {sys.path[0]}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

#!/usr/bin/env python3
"""
Install Dependencies Script
Automatically installs missing dependencies for the data collection service
"""

import subprocess
import sys
from pathlib import Path

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {command}")
            return True
        else:
            print(f"❌ Failed: {command}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception running {command}: {str(e)}")
        return False

def main():
    """Install all required dependencies"""
    print("🚀 Installing Data Collection Dependencies...")
    print("=" * 50)
    
    # Get current directory
    current_dir = Path(__file__).parent.absolute()
    requirements_file = current_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return 1
    
    # Install from requirements.txt
    print("📦 Installing from requirements.txt...")
    success = run_command(f"pip install -r {requirements_file}")
    
    if success:
        print("\n🎉 All dependencies installed successfully!")
        print("\n✅ You can now run:")
        print("   python run.py")
        print("   python quick_verify.py")
        return 0
    else:
        print("\n❌ Installation failed. Try manually:")
        print("   pip install -r requirements.txt")
        print("   pip install beautifulsoup4==4.12.2 aiohttp==3.9.1")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
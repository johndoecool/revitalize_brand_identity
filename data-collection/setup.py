#!/usr/bin/env python3
"""
Setup script for Data Collection Service
Team 3 - Satyajit & Nilanjan | Vibecoding Hackathon 2024
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'logs']
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing Python dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        print("✅ pip upgraded successfully")
        
        # Install requirements
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All dependencies installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("\n🔧 Trying alternative installation method...")
        
        # Try installing key packages individually
        key_packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0", 
            "pydantic==2.5.0",
            "pydantic-settings==2.1.0",
            "python-dotenv==1.0.0",
            "loguru==0.7.2",
            "aiohttp==3.9.1",
            "aiofiles==23.2.0",
            "requests==2.31.0",
            "beautifulsoup4==4.12.2",
            "textblob==0.17.1",
            "vaderSentiment==3.3.2"
        ]
        
        for package in key_packages:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ])
                print(f"✅ Installed: {package}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Warning: Failed to install {package}")
        
        print("\n💡 You may need to install remaining packages manually")

def setup_environment():
    """Setup environment file"""
    env_example = Path(".env.example") 
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        try:
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from .env.example")
            print("📝 Please edit .env file with your API keys")
        except Exception as e:
            print(f"⚠️  Warning: Could not create .env file: {e}")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  Warning: No .env.example file found")

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test core imports
        import fastapi
        import pydantic
        import uvicorn
        import loguru
        import aiohttp
        import aiofiles
        from bs4 import BeautifulSoup
        print("✅ Core dependencies imported successfully")
        
        # Test if the main module can be imported
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from src.config.settings import settings
            print("✅ Settings module loaded successfully")
        except Exception as e:
            print(f"⚠️  Warning: Settings module issue: {e}")
            
        try:
            from src.models.schemas import DataSource
            print("✅ Schemas module loaded successfully")
        except Exception as e:
            print(f"⚠️  Warning: Schemas module issue: {e}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Some dependencies may not be installed correctly")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Data Collection Service...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install requirements
    install_requirements()
    
    # Setup environment
    print("\n⚙️  Setting up environment...")
    setup_environment()
    
    # Test installation
    if test_installation():
        print("\n" + "=" * 50)
        print("🎉 Setup completed successfully!")
        print("\n📖 Next steps:")
        print("   1. Edit .env file with your API keys (optional)")
        print("   2. Run: python run.py")
        print("   3. Visit: http://localhost:8002/docs")
        print("\n💡 The service works with mock data even without API keys")
    else:
        print("\n" + "=" * 50)
        print("⚠️  Setup completed with warnings")
        print("💡 Try running: python run.py")
        print("   If you encounter issues, install missing packages manually")

if __name__ == "__main__":
    main() 
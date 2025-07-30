#!/usr/bin/env python3
"""
Setup script for Data Collection Service Dependencies
This script checks and installs all required dependencies for web scraping and data collection.
"""

import subprocess
import sys
import importlib
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a command and return success status"""
    try:
        print(f"🔄 {description}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e.stderr}")
        return False

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - Available")
        return True
    except ImportError:
        package = package_name or module_name
        print(f"❌ {module_name} - Missing (install with: pip install {package})")
        return False

def main():
    """Main setup function"""
    print("🚀 Data Collection Service - Dependency Setup")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python 3.8+ required. Current version: {python_version.major}.{python_version.minor}")
        sys.exit(1)
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Install requirements
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        success = run_command(
            f"pip install -r {requirements_file}",
            "Installing requirements from requirements.txt"
        )
        if not success:
            print("❌ Failed to install requirements. Please install manually.")
            sys.exit(1)
    else:
        print("⚠️  requirements.txt not found. Installing individual packages...")
        
        # Core packages
        packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "beautifulsoup4==4.12.2",
            "selenium==4.15.2",
            "webdriver-manager==4.0.1",
            "lxml==4.9.3",
            "requests==2.31.0",
            "aiohttp==3.9.1",
            "textblob==0.17.1",
            "vaderSentiment==3.3.2",
            "loguru==0.7.2",
            "chromadb==0.4.22",
            "sentence-transformers==2.2.2"
        ]
        
        for package in packages:
            run_command(f"pip install {package}", f"Installing {package}")
    
    print("\n📋 Checking Web Scraping Dependencies...")
    print("-" * 40)
    
    # Check critical imports
    dependencies = {
        "requests": "requests",
        "beautifulsoup4": "bs4",
        "selenium": "selenium",
        "webdriver_manager": "webdriver-manager",
        "pandas": "pandas",
        "numpy": "numpy",
        "chromadb": "chromadb",
        "aiohttp": "aiohttp",
        "brotli": "brotli",
        "textblob": "textblob",
        "vaderSentiment": "vaderSentiment",
        "loguru": "loguru",
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic"
    }
    
    missing_deps = []
    for module, package in dependencies.items():
        if not check_import(module, package):
            missing_deps.append(package)
    
    # Check Chrome/Chromium for Selenium
    print("\n🌐 Checking Browser Dependencies...")
    print("-" * 40)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Try to initialize Chrome driver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.quit()
        print("✅ Chrome WebDriver - Available")
        
    except Exception as e:
        print(f"❌ Chrome WebDriver - Failed: {str(e)}")
        print("📝 Install Chrome/Chromium browser for Selenium functionality")
    
    # Download NLTK data if needed
    print("\n📚 Setting up NLP Dependencies...")
    print("-" * 40)
    
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('brown', quiet=True)
        print("✅ NLTK data downloaded")
    except ImportError:
        print("⚠️  NLTK not available - some NLP features may be limited")
    
    # Summary
    print("\n📊 Setup Summary")
    print("=" * 50)
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n📝 Install missing dependencies with:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    else:
        print("✅ All dependencies are available!")
        print("🎉 Data Collection Service is ready to use!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
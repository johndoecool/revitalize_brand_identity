@echo off
echo 🚀 Analysis Engine Service Launcher
echo ====================================

REM Check if we're in the right directory
if not exist "app\main.py" (
    echo ❌ Error: Please run this from the analysis_service directory
    echo 💡 Navigate to: c:\git\revitalize_brand_identity\services\analysis_service
    pause
    exit /b 1
)

REM Check for virtual environment
if exist "analysis_env\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call analysis_env\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo 📦 Activating .venv environment...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found. Using system Python.
    echo 💡 Consider creating one: python -m venv analysis_env
)

REM Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        echo 📋 Creating .env from template...
        copy .env.example .env
        echo ⚠️  Please edit .env and add your OpenAI API key
        echo 💡 OPENAI_API_KEY=your_api_key_here
    ) else (
        echo ❌ No .env file found. Please create one with your OpenAI API key.
    )
)

echo 🔧 Starting Analysis Engine Service...
echo 🔗 API Docs: http://localhost:8003/docs
echo 🏥 Health: http://localhost:8003/health
echo.

REM Try to start the service
python start.py

if errorlevel 1 (
    echo.
    echo ❌ Failed to start service. Troubleshooting:
    echo 1. Check if dependencies are installed: pip install -r requirements.txt
    echo 2. Verify Python version: python --version
    echo 3. Check OpenAI API key in .env file
    echo 4. Run from correct directory: analysis_service
    pause
)

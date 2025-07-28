@echo off
REM Data Collection Service Setup Script
REM Team 3 - Satyajit & Nilanjan | Vibecoding Hackathon 2024

echo 🚀 Setting up Data Collection Service...
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo    Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Show Python version
for /f "tokens=2" %%i in ('python --version') do echo ✅ Python version: %%i

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️  Some dependencies failed to install
    echo 💡 Installing core dependencies individually...
    
    REM Install core dependencies one by one
    pip install fastapi==0.104.1
    pip install "uvicorn[standard]==0.24.0"
    pip install pydantic==2.5.0
    pip install pydantic-settings==2.1.0
    pip install python-dotenv==1.0.0
    pip install loguru==0.7.2
    pip install aiohttp==3.9.1
    pip install requests==2.31.0
) else (
    echo ✅ All dependencies installed successfully
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "vector_db" mkdir "vector_db"
echo ✅ Directories created

REM Setup environment file
if exist ".env.example" (
    if not exist ".env" (
        copy ".env.example" ".env" >nul
        echo ✅ Created .env file from .env.example
        echo 📝 Please edit .env file with your API keys
    ) else (
        echo ✅ .env file already exists
    )
)

REM Test installation
echo 🧪 Testing installation...
python -c "import fastapi, pydantic, uvicorn; print('Core imports successful')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Installation test failed
    echo 💡 Try running the service anyway: python run.py
) else (
    echo ✅ Installation test passed
    
    echo.
    echo ==================================================
    echo 🎉 Setup completed successfully!
    echo.
    echo 📖 Next steps:
    echo    1. Activate virtual environment: venv\Scripts\activate.bat
    echo    2. Edit .env file with your API keys (optional)
    echo    3. Run: python run.py
    echo    4. Visit: http://localhost:8002/docs
    echo.
    echo 💡 The service works with mock data even without API keys
    echo 🛑 To stop: Press Ctrl+C
)

pause 
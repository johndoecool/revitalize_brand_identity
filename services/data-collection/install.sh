#!/bin/bash

# Data Collection Service Setup Script
# Team 3 - Satyajit & Nilanjan | Vibecoding Hackathon 2024

echo "🚀 Setting up Data Collection Service..."
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
if pip install -r requirements.txt; then
    echo "✅ All dependencies installed successfully"
else
    echo "⚠️  Some dependencies failed to install"
    echo "💡 Installing core dependencies individually..."
    
    # Install core dependencies one by one
    core_deps=(
        "fastapi==0.104.1"
        "uvicorn[standard]==0.24.0"
        "pydantic==2.5.0"
        "pydantic-settings==2.1.0"
        "python-dotenv==1.0.0"
        "loguru==0.7.2"
        "aiohttp==3.9.1"
        "requests==2.31.0"
    )
    
    for dep in "${core_deps[@]}"; do
        if pip install "$dep"; then
            echo "✅ Installed: $dep"
        else
            echo "❌ Failed: $dep"
        fi
    done
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs vector_db
echo "✅ Directories created"

# Setup environment file
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
    echo "📝 Please edit .env file with your API keys"
elif [ -f ".env" ]; then
    echo "✅ .env file already exists"
fi

# Test installation
echo "🧪 Testing installation..."
if python3 -c "import fastapi, pydantic, uvicorn; print('Core imports successful')"; then
    echo "✅ Installation test passed"
    
    echo ""
    echo "=================================================="
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📖 Next steps:"
    echo "   1. Activate virtual environment: source venv/bin/activate"
    echo "   2. Edit .env file with your API keys (optional)"
    echo "   3. Run: python run.py"
    echo "   4. Visit: http://localhost:8002/docs"
    echo ""
    echo "💡 The service works with mock data even without API keys"
    echo "🛑 To stop: Press Ctrl+C"
else
    echo "❌ Installation test failed"
    echo "💡 Try running the service anyway: python run.py"
fi 
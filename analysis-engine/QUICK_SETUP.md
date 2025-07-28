# Quick Setup Guide - Analysis Engine Service

## 🚨 Python 3.13 Compatibility Fix

If you're encountering the `distutils` error, follow these steps:

### Method 1: Use Python 3.11 or 3.12 (Recommended)

```powershell
# Check your Python version
python --version

# If you have Python 3.13, consider using Python 3.11 or 3.12
# Download from https://www.python.org/downloads/
```

### Method 2: Quick Fix for Python 3.13

```powershell
# Navigate to analysis service
cd services\analysis_service

# Create virtual environment
python -m venv analysis_env

# Activate environment
analysis_env\Scripts\activate

# Upgrade pip and install setuptools first
python -m pip install --upgrade pip setuptools wheel

# Install packages one by one
pip install fastapi>=0.110.0
pip install uvicorn[standard]>=0.27.0
pip install pydantic>=2.5.0
pip install pydantic-settings>=2.1.0
pip install openai>=1.12.0
pip install python-dotenv>=1.0.0
pip install httpx>=0.26.0
pip install python-multipart>=0.0.7
pip install aiofiles>=23.2.1
pip install jinja2>=3.1.2
pip install numpy>=1.24.0
pip install pandas>=2.0.0
pip install scikit-learn>=1.4.0
pip install textblob>=0.17.1
```

### Method 3: Alternative Installation

```powershell
# Use conda instead of pip (if you have Anaconda/Miniconda)
conda create -n analysis_env python=3.11
conda activate analysis_env
conda install -c conda-forge fastapi uvicorn pydantic openai python-dotenv httpx
```

## 🔧 Environment Setup

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file and add your OpenAI API key:
# OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Start the Service

```powershell
# Make sure virtual environment is activated
analysis_env\Scripts\activate

# Start the service
python app\main.py
```

## 🧪 Test the Service

```powershell
# Check health
curl http://localhost:8003/health

# View API documentation
# Open browser: http://localhost:8003/docs
```

## 📋 Minimal Requirements (Core Only)

If you're having package issues, install only the core requirements:

```powershell
pip install fastapi uvicorn pydantic openai python-dotenv httpx
```

## 🆘 Troubleshooting

### Problem: distutils module not found
**Solution**: Use Python 3.11 or 3.12, or upgrade pip and setuptools

### Problem: Package installation fails
**Solution**: Install packages individually or use conda

### Problem: Import errors
**Solution**: Ensure virtual environment is activated

### Problem: OpenAI API errors
**Solution**: Check your API key in .env file

## 🎯 Quick Test

Once the service is running, test with this simple curl:

```powershell
curl -X POST "http://localhost:8003/api/v1/analyze" -H "Content-Type: application/json" -d "{\"brand_data\":{\"brand\":{\"name\":\"Test Brand\"}},\"competitor_data\":{\"competitor\":{\"name\":\"Test Competitor\"}},\"area_id\":\"test\",\"analysis_type\":\"comprehensive\"}"
```

## 📞 Support

If you continue to have issues:
1. Check Python version: `python --version`
2. Verify virtual environment: `which python` (should show analysis_env path)
3. Check installed packages: `pip list`
4. Look at error logs when starting the service

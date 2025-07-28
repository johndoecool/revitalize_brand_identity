# Quick Start Guide

## 🚀 Easy Setup (No Manual Package Installation)

Choose your platform and run the appropriate setup script:

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

**Cross-Platform:**
```bash
python setup.py
```

### Option 2: Manual Setup (If scripts don't work)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Activate it:
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Create directories and environment:**
   ```bash
   mkdir data logs vector_db
   cp .env.example .env
   ```

## 🏃‍♂️ Running the Service

After setup, simply run:
```bash
python run.py
```

The service will automatically:
- ✅ Check for missing dependencies
- ✅ Load environment variables
- ✅ Create necessary directories
- ✅ Start the FastAPI server

## 🌐 Access Points

Once running, visit:
- **API Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health
- **Alternative Docs**: http://localhost:8002/redoc

## 🔧 Troubleshooting

### Issue: "Module not found" errors

**Solution:** Run the setup script for your platform:
```bash
# Windows
install.bat

# Linux/Mac  
./install.sh

# Cross-platform
python setup.py
```

### Issue: "Permission denied" on Linux/Mac

**Solution:** Make scripts executable:
```bash
chmod +x install.sh
chmod +x run.py
```

### Issue: Python version errors

**Solution:** Ensure Python 3.8+ is installed:
```bash
python --version  # Should show 3.8 or higher
```

### Issue: Port 8002 already in use

**Solution:** Change the port in your `.env` file:
```bash
PORT=8003  # Or any other available port
```

### Issue: Virtual environment activation fails

**Solution:** Use Python directly:
```bash
python -m pip install -r requirements.txt
python run.py
```

## 📋 Testing the Installation

1. **Health Check:**
   ```bash
   curl http://localhost:8002/health
   ```

2. **Start a collection job:**
   ```bash
   curl -X POST "http://localhost:8002/api/v1/collect" \
     -H "Content-Type: application/json" \
     -d '{
       "brand_id": "test_brand",
       "competitor_id": "test_competitor", 
       "area_id": "test_area",
       "sources": ["news", "social_media"]
     }'
   ```

3. **Check sources configuration:**
   ```bash
   curl http://localhost:8002/api/v1/sources/config
   ```

## 💡 Notes

- **No API Keys Required**: The service works with mock data by default
- **API Keys Optional**: Add them to `.env` for real data collection
- **Docker Alternative**: Run `docker-compose up` if you prefer containers
- **Development Mode**: The service auto-reloads when you make code changes

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. Check the logs in the `logs/` directory
2. Ensure you're in the correct directory (`data-collection-service/`)
3. Try running with verbose output: `python run.py --log-level debug`
4. Verify Python version: `python --version`

## 🎯 Quick Test

Once running, visit http://localhost:8002/docs and try the "Health Check" endpoint - you should get a green response! 
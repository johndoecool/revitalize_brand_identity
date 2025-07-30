#!/usr/bin/env python3
"""
Simple run script for the Data Collection Service
For development and testing purposes
"""

import os
import sys
import asyncio
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('loguru', 'Loguru'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing_packages = []
    
    for package, display_name in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(display_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 To fix this, run one of:")
        print("   - python setup.py (recommended)")
        print("   - pip install -r requirements.txt")
        print("   - ./install.sh (Linux/Mac)")
        print("   - install.bat (Windows)")
        return False
    
    return True

def load_environment():
    """Load environment variables"""
    try:
        from dotenv import load_dotenv
        
        # Load .env file if it exists
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv()
            print("✅ Environment loaded from .env")
        else:
            print("⚠️  No .env file found, using default settings")
            print("💡 Copy .env.example to .env and configure your API keys")
        
        return True
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping .env loading")
        return True
    except Exception as e:
        print(f"⚠️  Error loading environment: {e}")
        return True

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'logs', 'vector_db']
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

def import_app():
    """Import the FastAPI app with error handling"""
    try:
        from main import app
        return app
    except ImportError as e:
        print(f"❌ Error importing main app: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure you're in the correct directory")
        print("2. Run: python setup.py")
        print("3. Check that all files are present")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading application: {e}")
        print("\n💡 This might be a configuration issue")
        print("Check your .env file and dependencies")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Data Collection Service...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Load environment
    load_environment()
    
    # Create directories
    create_directories()
    
    # Import the app
    app = import_app()
    
    # Display service info
    print("📋 Service Info:")
    print(f"   - Port: {os.getenv('PORT', 8002)}")
    print(f"   - Host: {os.getenv('HOST', '0.0.0.0')}")
    print(f"   - Debug: {os.getenv('DEBUG', 'true')}")
    print(f"   - Vector DB: {os.getenv('USE_VECTOR_DB', 'true')}")
    print()
    
    print("📖 Available endpoints:")
    print("   - Health: http://localhost:8002/health")
    print("   - API Docs: http://localhost:8002/docs")
    print("   - ReDoc: http://localhost:8002/redoc")
    print("   - API Base: http://localhost:8002/api/v1/")
    print()
    
    print("🛑 Press Ctrl+C to stop the service")
    print("=" * 50)
    
    try:
        import uvicorn
        
        uvicorn.run(
            "main:app",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8002)),
            reload=os.getenv("DEBUG", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("💡 Run: pip install uvicorn")
    except Exception as e:
        print(f"\n❌ Error starting service: {e}")
        print("💡 Check the logs and configuration")
        sys.exit(1) 
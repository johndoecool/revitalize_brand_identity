#!/usr/bin/env python3
"""
Analysis Service Production Launcher
Starts the service without auto-reload for production use
"""

import sys
import os
from pathlib import Path

# Change to the analysis_service directory
service_dir = Path(__file__).parent
if service_dir.name == "analysis_service":
    # We're in the right directory
    sys.path.insert(0, str(service_dir))
    os.chdir(service_dir)
else:
    # Find the analysis_service directory
    current = Path.cwd()
    while current.parent != current:
        if (current / "analysis_service").exists():
            service_dir = current / "analysis_service"
            break
        elif current.name == "analysis_service":
            service_dir = current
            break
        current = current.parent
    
    sys.path.insert(0, str(service_dir))
    os.chdir(service_dir)

# Check for .env file
env_file = service_dir / ".env"
if not env_file.exists():
    print("❌ No .env file found!")
    print("💡 Copy .env.example to .env and add your OpenAI API key")
    example_file = service_dir / ".env.example"
    if example_file.exists():
        print(f"   cp {example_file} {env_file}")
    sys.exit(1)

# Now import and run
try:
    import uvicorn
    
    if __name__ == "__main__":
        print("🚀 Starting Analysis Engine Service (Production Mode)")
        print(f"📁 Service directory: {service_dir}")
        print("🔗 API Documentation: http://localhost:8003/docs")
        print("🏥 Health Check: http://localhost:8003/health")
        print("📊 OpenAPI Schema: http://localhost:8003/openapi.json")
        print()
        
        # Production configuration without reload
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8003,
            reload=False,
            workers=1,
            log_level="info",
            access_log=True
        )
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Make sure dependencies are installed:")
    print("   pip install -r requirements.txt")
    print("💡 Also ensure you have an OpenAI API key in .env file")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n⏹️  Service stopped by user")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

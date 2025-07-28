#!/usr/bin/env python3
"""
Analysis Service Launcher
Run this script from the analysis_service directory
"""

import sys
from pathlib import Path

# Change to the analysis_service directory
service_dir = Path(__file__).parent
if service_dir.name == "analysis_service":
    # We're in the right directory
    sys.path.insert(0, str(service_dir))
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

# Now import and run
try:
    import uvicorn
    
    if __name__ == "__main__":
        print("🚀 Starting Analysis Engine Service...")
        print(f"📁 Service directory: {service_dir}")
        print("🔗 API Documentation: http://localhost:8003/docs")
        print("🏥 Health Check: http://localhost:8003/health")
        print("🔄 Auto-reload enabled for development")
        print()
        
        # Use import string for proper reload functionality
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8003,
            reload=True,
            reload_dirs=[str(service_dir)],
            log_level="info"
        )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Make sure you're in the analysis_service directory and dependencies are installed")
    print("💡 Try: cd c:\\git\\revitalize_brand_identity\\services\\analysis_service")
    print("💡 Then: python start.py")
    sys.exit(1)

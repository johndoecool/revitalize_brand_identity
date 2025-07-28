from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Ensure we can import from the app module
# This handles running from different directories
current_file = Path(__file__).resolve()
app_dir = current_file.parent
service_dir = app_dir.parent

# Add service directory to path if not already there
if str(service_dir) not in sys.path:
    sys.path.insert(0, str(service_dir))

try:
    from app.routers import analysis
    from app.core.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"🔧 Current working directory: {Path.cwd()}")
    print(f"🔧 Service directory should be: {service_dir}")
    print("💡 Please run from the analysis_service directory:")
    print("   cd c:\\git\\revitalize_brand_identity\\services\\analysis_service")
    print("   python app\\main.py")
    print("   OR use: python start.py")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Analysis Engine API",
    description="AI-powered brand analysis and comparison service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Analysis Engine API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analysis-engine"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True
    )

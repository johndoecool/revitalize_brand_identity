import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.endpoints import router
from src.config.settings import settings
from src.services.job_manager import job_manager


# Configure logging
logger.add(
    settings.log_file,
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# Add console logging
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}:{function}:{line}</cyan> | {message}"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Data Collection Service")
    logger.info(f"Configuration: Host={settings.host}, Port={settings.port}")
    logger.info(f"Storage: Use Vector DB={settings.use_vector_db}")
    logger.info(f"Available sources: {settings.available_sources}")
    
    # Initialize any startup tasks here
    try:
        # Test storage connection
        active_jobs = await job_manager.get_active_jobs_count()
        logger.info(f"Storage connection successful. Active jobs: {active_jobs}")
    except Exception as e:
        logger.error(f"Error initializing storage: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Data Collection Service")
    
    # Cancel any active jobs
    try:
        if job_manager.active_jobs:
            logger.info(f"Cancelling {len(job_manager.active_jobs)} active jobs")
            for job_id in list(job_manager.active_jobs.keys()):
                await job_manager.cancel_job(job_id)
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="Data Collection Service",
    description="""
    Brand Data Collection Service for Vibecoding Hackathon
    
    This service collects and analyzes brand data from multiple sources:
    - News sentiment analysis
    - Social media sentiment analysis
    - Glassdoor employee reviews
    - Website performance and UX analysis
    
    The service supports asynchronous data collection jobs with real-time progress tracking.
    """,
    version="1.0.0",
    contact={
        "name": "Team 3 - Data Collection Service",
        "description": "Satyajit & Nilanjan"
    },
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": {
                    "path": str(request.url),
                    "method": request.method
                }
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
    )


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint"""
    return {
        "service": "Data Collection Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api/v1/"
        }
    }


# Additional middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    logger.info(f"Response: {request.method} {request.url} - Status: {response.status_code}")
    
    return response


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    ) 
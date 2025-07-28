from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.brands import router as brands_router
from app.api.cache import router as cache_router
from app.models import ErrorResponse
from app.logging_config import setup_logging
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger('brand_service')

# Create FastAPI app
app = FastAPI(
    title="Brand Service API",
    description="A microservice for brand management, providing APIs for brand search, area suggestions, and competitor discovery.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger.info("Brand Service API starting up")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

# Include routers
app.include_router(brands_router)
app.include_router(cache_router)

logger.info("API routers configured")


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Brand Service API is running", "version": "1.0.0"}


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "service": "brand-service",
        "version": "1.0.0",
        "timestamp": "2025-07-25T00:00:00Z"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception in {request.method} {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error="Internal server error",
            details=str(exc)
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Brand Service with uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=8001)

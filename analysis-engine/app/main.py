from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import logging
import json
import time
import uuid

from app.routers import analysis
from app.models.analysis import HealthCheckResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Analysis Engine Service",
    description="Brand analysis and competitive intelligence service",
    version="1.0.0"
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming HTTP requests with detailed information
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]
    
    # Skip logging for health checks to reduce noise
    if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
        response = await call_next(request)
        return response
    
    # Log incoming request (one time only)
    logger.info("=" * 80)
    logger.info(f"REQUEST_ID: {request_id}")
    
    # Extract and log analysis_id if present in path
    analysis_id = None
    if "/analyze/" in request.url.path:
        # Extract analysis_id from paths like /analyze/{analysis_id}/status or /analyze/{analysis_id}/results
        path_parts = request.url.path.split('/')
        try:
            analyze_index = path_parts.index('analyze')
            if len(path_parts) > analyze_index + 1:
                potential_analysis_id = path_parts[analyze_index + 1]
                # Check if it looks like an analysis_id (starts with 'analysis_' or has expected format)
                if potential_analysis_id and (potential_analysis_id.startswith('analysis_') or len(potential_analysis_id) >= 8):
                    analysis_id = potential_analysis_id
                    logger.info(f"ANALYSIS_ID: {analysis_id}")
        except (ValueError, IndexError):
            pass
    
    logger.info("INCOMING_HTTP_REQUEST")
    logger.info("=" * 80)
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {str(request.url)}")
    logger.info(f"Path: {request.url.path}")
    logger.info(f"Client_IP: {request.client.host if request.client else 'Unknown'}")
    logger.info(f"User_Agent: {request.headers.get('user-agent', 'Unknown')}")
    logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    
    # Log request body only for analysis endpoints and only key info
    if request.method in ["POST", "PUT", "PATCH"] and "/analyze" in request.url.path:
        try:
            body = await request.body()
            if body:
                try:
                    json_body = json.loads(body.decode('utf-8'))
                    # Log only summary, not full data (to avoid duplication with LLM service logs)
                    brand_data = json_body.get('brand_data', {})
                    competitor_data = json_body.get('competitor_data', {})
                    logger.info("REQUEST_SUMMARY:")
                    logger.info(f"  Brand_data_keys: {list(brand_data.keys()) if brand_data else 'None'}")
                    logger.info(f"  Competitor_data_keys: {list(competitor_data.keys()) if competitor_data else 'None'}")
                    logger.info(f"  Area_id: {json_body.get('area_id', 'Not specified')}")
                    logger.info(f"  Analysis_type: {json_body.get('analysis_type', 'comprehensive')}")
                except json.JSONDecodeError:
                    logger.info("REQUEST_BODY: Non-JSON content")
        except Exception as e:
            logger.warning(f"Could not read request body: {e}")
    
    logger.info("-" * 80)
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response (one time only)
    logger.info(f"REQUEST_ID: {request_id}")
    if analysis_id:
        logger.info(f"ANALYSIS_ID: {analysis_id}")
    logger.info("HTTP_RESPONSE")
    logger.info(f"Status_code: {response.status_code}")
    logger.info(f"Process_time: {process_time:.3f}s")
    
    # Add process time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    if analysis_id:
        response.headers["X-Analysis-ID"] = analysis_id
    
    logger.info("=" * 80)
    
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router)

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint
    """
    # Import here to avoid circular imports
    from app.routers.analysis import active_analyses
    
    return HealthCheckResponse(
        status="healthy",
        service="Analysis Engine",
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
        llm_status="ready",
        active_analyses=len(active_analyses)
    )

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Analysis Engine Service",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone
import logging
import json

from app.models.analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisStatusResponse,
    AnalysisResultsResponse, AnalysisHistoryResponse, ErrorResponse,
    AnalysisStatus
)
from app.services.analysis_engine import AnalysisEngine

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])

# Initialize analysis engine
analysis_engine = AnalysisEngine()

@router.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest):
    """
    Start a new brand analysis comparing brand data with competitor data
    """
    # Log only the analysis-specific details (request already logged by middleware)
    logger.info("ANALYSIS_ENDPOINT_START")
    logger.info(f"Analysis_area: {getattr(request, 'area_id', 'Not specified')}")
    logger.info(f"Analysis_type: {getattr(request, 'analysis_type', 'comprehensive')}")
    
    try:
        # Validate request data
        if not request.brand_data:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid analysis data provided",
                        "details": {
                            "field": "brand_data",
                            "value": "{}"
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        if not request.competitor_data:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid analysis data provided",
                        "details": {
                            "field": "competitor_data",
                            "value": "{}"
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        if not request.area_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid analysis data provided",
                        "details": {
                            "field": "area_id",
                            "value": ""
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Start analysis
        analysis_id, status = await analysis_engine.start_analysis(request)
        
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            status=status,
            estimated_duration=60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Analysis failed: {str(e)}",
                    "details": {}
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

@router.get("/analyze/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(analysis_id: str):
    """
    Get the current status of an analysis
    """
    try:
        status_data = await analysis_engine.get_analysis_status(analysis_id)
        
        if not status_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Analysis not found",
                        "details": {
                            "field": "analysis_id",
                            "value": analysis_id
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Format response based on status
        if status_data["status"] == AnalysisStatus.PROCESSING:
            response_data = {
                "analysis_id": analysis_id,
                "status": status_data["status"],
                "progress": status_data.get("progress", 0),
                "current_step": status_data.get("current_step", "Processing"),
                "estimated_completion": "2024-01-15T10:35:00Z"  # Mock completion time
            }
        elif status_data["status"] == AnalysisStatus.COMPLETED:
            response_data = {
                "analysis_id": analysis_id,
                "status": status_data["status"],
                "progress": 100,
                "completed_at": status_data.get("completed_at", datetime.now(timezone.utc).isoformat())
            }
        else:
            response_data = {
                "analysis_id": analysis_id,
                "status": status_data["status"],
                "progress": status_data.get("progress", 0),
                "error": status_data.get("error")
            }
        
        return AnalysisStatusResponse(
            success=True,
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get analysis status: {str(e)}",
                    "details": {}
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

@router.get("/analyze/{analysis_id}/results", response_model=AnalysisResultsResponse)
async def get_analysis_results(analysis_id: str):
    """
    Get the results of a completed analysis
    """
    try:
        results = await analysis_engine.get_analysis_results(analysis_id)
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Analysis not found",
                        "details": {
                            "field": "analysis_id",
                            "value": analysis_id
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        return AnalysisResultsResponse(
            success=True,
            data=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get analysis results: {str(e)}",
                    "details": {}
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

@router.get("/analyze/history", response_model=AnalysisHistoryResponse)
async def get_analysis_history(
    brand_id: Optional[str] = Query(None, description="Filter by brand ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results")
):
    """
    Get history of completed analyses
    """
    try:
        history = await analysis_engine.get_analysis_history(brand_id, limit)
        
        return AnalysisHistoryResponse(
            success=True,
            data=history
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"Failed to get analysis history: {str(e)}",
                    "details": {}
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

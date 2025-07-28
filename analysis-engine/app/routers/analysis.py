from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from app.models.analysis import (
    AnalysisRequest, AnalysisInitResponse, AnalysisStatusResponse, 
    AnalysisResultsResponse, AnalysisStatus
)
from app.services.analysis_engine import AnalysisEngine

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize analysis engine
analysis_engine = AnalysisEngine()

@router.post("/analyze", response_model=AnalysisInitResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Start a new brand analysis job
    
    This endpoint initiates a comprehensive analysis comparing brand performance
    against competitors in a specific area (e.g., self-service portal, mobile app).
    """
    try:
        logger.info(f"Starting analysis for area: {request.area_id}")
        
        # Validate request
        if not request.brand_data or not request.competitor_data:
            raise HTTPException(
                status_code=400, 
                detail="Both brand_data and competitor_data are required"
            )
        
        # Start analysis
        analysis_id = await analysis_engine.start_analysis(request)
        
        # Estimate duration based on analysis type
        duration_map = {
            "quick": 30,
            "comprehensive": 90,
            "detailed": 120
        }
        estimated_duration = duration_map.get(request.analysis_type.value, 90)
        
        return AnalysisInitResponse(
            success=True,
            analysis_id=analysis_id,
            status=AnalysisStatus.PROCESSING,
            estimated_duration=estimated_duration
        )
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis initialization failed: {str(e)}")

@router.get("/analyze/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(analysis_id: str):
    """
    Get the current status of an analysis job
    
    Returns the progress, status, and completion information for the specified analysis.
    """
    try:
        status_data = await analysis_engine.get_analysis_status(analysis_id)
        
        if not status_data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return AnalysisStatusResponse(
            success=True,
            data=status_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.get("/analyze/{analysis_id}/results", response_model=AnalysisResultsResponse)
async def get_analysis_results(analysis_id: str):
    """
    Get the complete results of a finished analysis
    
    Returns detailed comparison results, actionable insights, and recommendations.
    Only available for completed analyses.
    """
    try:
        results = await analysis_engine.get_analysis_results(analysis_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")
        
        return AnalysisResultsResponse(
            success=True,
            data=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Results retrieval failed: {str(e)}")

@router.get("/analyze/{analysis_id}/report")
async def get_analysis_report(analysis_id: str):
    """
    Generate and return a formatted analysis report
    
    Returns a comprehensive report with executive summary, detailed comparisons,
    and actionable insights in a structured format.
    """
    try:
        report = await analysis_engine.generate_comparison_report(analysis_id)
        
        if not report:
            raise HTTPException(status_code=404, detail="Analysis not found or report generation failed")
        
        return JSONResponse(content={
            "success": True,
            "report": report
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/analyze/{analysis_id}/insights")
async def get_actionable_insights_summary(analysis_id: str):
    """
    Get a summary of actionable insights from the analysis
    
    Returns prioritized insights with effort estimates and impact projections.
    """
    try:
        insights_summary = await analysis_engine.get_actionable_insights_summary(analysis_id)
        
        if not insights_summary:
            raise HTTPException(status_code=404, detail="Analysis not found or insights not available")
        
        return JSONResponse(content={
            "success": True,
            "insights_summary": insights_summary
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get insights summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Insights retrieval failed: {str(e)}")

@router.post("/analyze/batch")
async def start_batch_analysis(requests: list[AnalysisRequest]):
    """
    Start multiple analysis jobs in batch
    
    Useful for comparing multiple competitors or analyzing multiple areas simultaneously.
    """
    try:
        if len(requests) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Batch size cannot exceed 10 analyses")
        
        analysis_ids = []
        
        for request in requests:
            analysis_id = await analysis_engine.start_analysis(request)
            analysis_ids.append(analysis_id)
        
        return JSONResponse(content={
            "success": True,
            "batch_id": f"batch_{len(analysis_ids)}_{analysis_ids[0][:8]}",
            "analysis_ids": analysis_ids,
            "total_analyses": len(analysis_ids)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start batch analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the analysis service
    """
    return {
        "status": "healthy",
        "service": "analysis-engine",
        "active_analyses": len(analysis_engine.active_jobs),
        "capabilities": [
            "brand_comparison",
            "competitor_analysis", 
            "actionable_insights",
            "trend_analysis",
            "report_generation",
            "confidence_scoring"
        ]
    }

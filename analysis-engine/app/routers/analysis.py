from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from functools import partial
import logging
import json
import os
import uuid
import asyncio

from app.models.analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisStatusResponse,
    AnalysisResultsResponse, AnalysisHistoryResponse, ErrorResponse,
    AnalysisStatus, ReportResponse
)
from app.services.llm_service import LLMService
from app.services.chart_service import ChartService
from app.services.database_service import database_service
from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])

# Initialize services
llm_service = LLMService()
chart_service = ChartService()

# Store active analyses and results
active_analyses = {}
completed_analyses = {}

@router.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, http_request: Request):
    """
    Start a new brand analysis using collected data from a collect_id
    """
    # Get or generate request ID
    request_id = http_request.headers.get("request_id") or f"req_{uuid.uuid4().hex[:8]}"
    
    logger.info("ANALYSIS_ENDPOINT_START")
    logger.info(f"Request_id: {request_id}")
    logger.info(f"Collect_id: {request.collect_id}")
    logger.info(f"Analysis_focus: {request.analysis_focus}")
    
    try:
        # Validate collect_id
        if not request.collect_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "collect_id is required",
                        "details": {
                            "field": "collect_id",
                            "value": ""
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Load collected data file using configurable path
        data_path = os.path.join(settings.DATA_COLLECTION_PATH, f"{request.collect_id}.json")
        absolute_data_path = os.path.abspath(data_path)
        
        if not os.path.exists(absolute_data_path):
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "DATA_NOT_FOUND",
                        "message": f"Collected data file not found for collect_id: {request.collect_id}",
                        "details": {
                            "field": "collect_id",
                            "value": request.collect_id
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Read and parse collected data
        try:
            with open(absolute_data_path, 'r', encoding='utf-8') as f:
                collected_data = json.load(f)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": {
                        "code": "DATA_PARSE_ERROR",
                        "message": f"Failed to parse collected data: {str(e)}",
                        "details": {
                            "file": absolute_data_path
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Database integration: Find and validate record
        logger.info(f"Looking for database record: request_id={request_id}, collect_id={request.collect_id}")
        
        # Find matching record in database.json
        db_record = await database_service.find_record(request_id, request.collect_id)
        if not db_record:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "RECORD_NOT_FOUND",
                        "message": f"No matching record found for request_id: {request_id} and collect_id: {request.collect_id}",
                        "details": {
                            "request_id": request_id,
                            "collect_id": request.collect_id
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Validate data collection is complete
        if not await database_service.validate_data_collection_complete(request_id, request.collect_id):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "DATA_COLLECTION_INCOMPLETE",
                        "message": f"Data collection is not complete for request_id: {request_id}",
                        "details": {
                            "request_id": request_id,
                            "collect_id": request.collect_id,
                            "current_status": db_record.get("dataCollectionStatus", "UNKNOWN")
                        }
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        logger.info(f"Database record validated successfully for request_id: {request_id}")
        
        # Generate analysis ID - simpler format with just request_id and timestamp
        analysis_id = f"analysis_{request_id}_{datetime.now().strftime('%H%M%S')}"
        
        # Update database record with analysis information
        await database_service.update_analysis_status(
            request_id=request_id,
            collect_id=request.collect_id,
            analysis_id=analysis_id,
            status="IN_PROGRESS"
        )
        
        logger.info(f"Updated database record to IN_PROGRESS for analysis_id: {analysis_id}")
        
        # Store analysis metadata
        active_analyses[analysis_id] = {
            "status": AnalysisStatus.PROCESSING,
            "progress": 0,
            "current_step": "Starting LLM analysis",
            "created_at": datetime.now(timezone.utc),
            "request_id": request_id,
            "collect_id": request.collect_id,
            "collected_data": collected_data,
            "analysis_focus": request.analysis_focus,
            "comparison_brand": request.comparison_brand
        }
        
        # Start analysis in background (fire and forget)
        # Create the background task without awaiting it
        task = asyncio.create_task(_perform_analysis(analysis_id, collected_data, request))
        # Add error handling for the background task
        task.add_done_callback(partial(_handle_background_task_completion, analysis_id))
        
        logger.info(f"Started background analysis {analysis_id} for collect_id: {request.collect_id} with request_id: {request_id}")
        
        # Return immediately without waiting for analysis to complete
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            status=AnalysisStatus.PROCESSING,
            estimated_duration=60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
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
    Get the current status of an analysis with chart data and results when completed
    """
    try:
        # Check if analysis exists in active analyses
        if analysis_id in active_analyses:
            status_data = active_analyses[analysis_id]
            
            # If completed, include chart data and analysis results
            if status_data["status"] == AnalysisStatus.COMPLETED and analysis_id in completed_analyses:
                completed_data = completed_analyses[analysis_id]
                
                return AnalysisStatusResponse(
                    success=True,
                    data={
                        "analysis_id": analysis_id,
                        "status": status_data["status"],
                        "progress": status_data.get("progress", 100),
                        "completed_at": status_data.get("completed_at", datetime.now(timezone.utc)).isoformat(),
                        "analysis_result": completed_data["analysis_result"].dict()
                    },
                    charts=completed_data["charts"],
                    competitor_analysis=completed_data["competitor_insights"],
                    improvement_areas=completed_data["improvement_areas"]
                )
            else:
                # Return processing status
                return AnalysisStatusResponse(
                    success=True,
                    data={
                        "analysis_id": analysis_id,
                        "status": status_data["status"],
                        "progress": status_data.get("progress", 0),
                        "current_step": status_data.get("current_step", "Processing"),
                        "estimated_completion": "2024-01-15T10:35:00Z"  # Mock completion time
                    }
                )
        
        # Check if it's in completed analyses only
        elif analysis_id in completed_analyses:
            completed_data = completed_analyses[analysis_id]
            
            return AnalysisStatusResponse(
                success=True,
                data={
                    "analysis_id": analysis_id,
                    "status": AnalysisStatus.COMPLETED,
                    "progress": 100,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "analysis_result": completed_data["analysis_result"].dict()
                },
                charts=completed_data["charts"],
                competitor_analysis=completed_data["competitor_insights"],
                improvement_areas=completed_data["improvement_areas"]
            )
        
        else:
            # Analysis not found
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
        # Check if analysis is completed
        if analysis_id in completed_analyses:
            completed_data = completed_analyses[analysis_id]
            return AnalysisResultsResponse(
                success=True,
                data=completed_data["analysis_result"]
            )
        
        # Check if analysis is still active
        elif analysis_id in active_analyses:
            status = active_analyses[analysis_id]["status"]
            if status == AnalysisStatus.PROCESSING:
                raise HTTPException(
                    status_code=202,
                    detail={
                        "success": False,
                        "error": {
                            "code": "ANALYSIS_IN_PROGRESS",
                            "message": "Analysis is still in progress",
                            "details": {
                                "field": "analysis_id",
                                "value": analysis_id
                            }
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            elif status == AnalysisStatus.FAILED:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "success": False,
                        "error": {
                            "code": "ANALYSIS_FAILED",
                            "message": "Analysis failed to complete",
                            "details": {
                                "field": "analysis_id",
                                "value": analysis_id,
                                "error": active_analyses[analysis_id].get("error", "Unknown error")
                            }
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
        
        else:
            # Analysis not found
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

@router.get("/analyze/{analysis_id}/report", response_model=ReportResponse)
async def get_analysis_report(analysis_id: str):
    """
    Generate a PDF report of the analysis and return as base64-encoded string
    """
    try:
        # Check if analysis is completed
        if analysis_id not in completed_analyses:
            if analysis_id in active_analyses:
                status = active_analyses[analysis_id]["status"]
                if status == AnalysisStatus.PROCESSING:
                    raise HTTPException(
                        status_code=202,
                        detail={
                            "success": False,
                            "error": {
                                "code": "ANALYSIS_IN_PROGRESS",
                                "message": "Analysis is still in progress",
                                "details": {"analysis_id": analysis_id}
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    )
            
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Analysis not found or not completed",
                        "details": {"analysis_id": analysis_id}
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        
        # Get completed analysis data
        completed_data = completed_analyses[analysis_id]
        
        # Generate PDF report
        report_base64 = chart_service.generate_pdf_report(
            completed_data["analysis_result"],
            completed_data["charts"],
            completed_data["competitor_insights"],
            completed_data["improvement_areas"],
            completed_data["collected_data"]
        )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"brand_analysis_report_{analysis_id}_{timestamp}.pdf"
        
        return ReportResponse(
            success=True,
            report_base64=report_base64,
            filename=filename,
            generated_at=datetime.now(timezone.utc)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report for analysis {analysis_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "REPORT_GENERATION_ERROR",
                    "message": f"Failed to generate report: {str(e)}",
                    "details": {"analysis_id": analysis_id}
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
        # Get all completed analyses
        history_items = []
        
        for analysis_id, data in completed_analyses.items():
            analysis_result = data["analysis_result"]
            
            # Apply brand_id filter if provided
            if brand_id and analysis_result.brand_name != brand_id:
                continue
            
            history_items.append({
                "analysis_id": analysis_id,
                "brand_id": analysis_result.brand_name,
                "competitor_id": analysis_result.competitor_name,
                "area_id": analysis_result.area_id,
                "created_at": analysis_result.created_at or datetime.now(timezone.utc),
                "status": AnalysisStatus.COMPLETED,
                "overall_score": analysis_result.overall_comparison.brand_score
            })
        
        # Sort by created_at descending and limit
        history_items.sort(key=lambda x: x["created_at"], reverse=True)
        history_items = history_items[:limit]
        
        return AnalysisHistoryResponse(
            success=True,
            data=history_items
        )
        
    except Exception as e:
        logger.error(f"Failed to get analysis history: {e}")
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

def _handle_background_task_completion(analysis_id: str, task: asyncio.Task):
    """Handle completion of background analysis task"""
    try:
        if task.exception():
            logger.error(f"Background analysis {analysis_id} failed with exception: {task.exception()}")
            if analysis_id in active_analyses:
                active_analyses[analysis_id]["status"] = AnalysisStatus.FAILED
                active_analyses[analysis_id]["error"] = str(task.exception())
        else:
            logger.info(f"Background analysis {analysis_id} completed successfully")
    except Exception as e:
        logger.error(f"Error handling background task completion for {analysis_id}: {e}")

# Helper function for background analysis
async def _perform_analysis(analysis_id: str, collected_data: Dict[str, Any], request: AnalysisRequest):
    """Perform the actual analysis in the background"""
    try:
        # Update status to processing
        active_analyses[analysis_id]["status"] = AnalysisStatus.PROCESSING
        active_analyses[analysis_id]["progress"] = 10
        active_analyses[analysis_id]["current_step"] = "Analyzing collected data with LLM"
        
        # Call LLM service for analysis
        analysis_result = await llm_service.analyze_collected_data(collected_data, request.analysis_focus)
        
        # Update progress
        active_analyses[analysis_id]["progress"] = 60
        active_analyses[analysis_id]["current_step"] = "Generating chart data"
        
        # Generate chart data
        charts = chart_service.generate_charts_from_analysis(analysis_result, collected_data)
        
        # Generate competitor insights
        competitor_insights = chart_service.generate_competitor_insights(analysis_result, collected_data)
        
        # Generate improvement areas
        improvement_areas = chart_service.generate_improvement_areas(analysis_result, collected_data)
        
        # Update progress
        active_analyses[analysis_id]["progress"] = 100
        active_analyses[analysis_id]["current_step"] = "Completed"
        active_analyses[analysis_id]["status"] = AnalysisStatus.COMPLETED
        active_analyses[analysis_id]["completed_at"] = datetime.now(timezone.utc)
        
        # Store completed analysis
        completed_analyses[analysis_id] = {
            "analysis_result": analysis_result,
            "charts": charts,
            "competitor_insights": competitor_insights,
            "improvement_areas": improvement_areas,
            "collected_data": collected_data
        }
        
        # Update database status to COMPLETED
        request_id = active_analyses[analysis_id]["request_id"]
        collect_id = active_analyses[analysis_id]["collect_id"]
        
        success = await database_service.update_analysis_status(
            request_id=request_id,
            collect_id=collect_id,
            analysis_id=analysis_id,
            status="COMPLETED"
        )
        
        if success:
            logger.info(f"Analysis {analysis_id} completed successfully and database updated")
        else:
            logger.warning(f"Analysis {analysis_id} completed but failed to update database status")
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {e}")
        active_analyses[analysis_id]["status"] = AnalysisStatus.FAILED
        active_analyses[analysis_id]["error"] = str(e)
        
        # Update database status to FAILED
        try:
            request_id = active_analyses[analysis_id]["request_id"]
            collect_id = active_analyses[analysis_id]["collect_id"]
            
            await database_service.update_analysis_status(
                request_id=request_id,
                collect_id=collect_id,
                analysis_id=analysis_id,
                status="FAILED"
            )
            logger.info(f"Database status updated to FAILED for analysis {analysis_id}")
        except Exception as db_error:
            logger.error(f"Failed to update database status to FAILED for analysis {analysis_id}: {db_error}")

from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from loguru import logger

from src.models.schemas import (
    CollectionRequest, CollectionStartResponse, CollectionErrorResponse,
    CollectionStatusResponse, CollectionDataResponse, DataSourcesConfigResponse,
    HealthCheckResponse, DataSourceConfig, DataSource, ErrorResponse, ErrorDetail
)
from src.services.job_manager import job_manager
from src.config.settings import settings

# Create API router
router = APIRouter()


@router.post(
    "/api/v1/collect",
    response_model=CollectionStartResponse,
    responses={
        400: {"model": CollectionErrorResponse},
        500: {"model": CollectionErrorResponse}
    },
    summary="Start Data Collection",
    description="Start a new data collection job for brand comparison analysis. If no sources are specified, all available sources will be used."
)
async def start_data_collection(request: CollectionRequest):
    """Start a new data collection job"""
    try:
        logger.info(f"Starting data collection for {request.brand_id} vs {request.competitor_id}")
        
        # Handle optional sources - default to all available sources if none specified
        sources_to_use = request.sources
        if sources_to_use is None:
            sources_to_use = [DataSource.NEWS, DataSource.SOCIAL_MEDIA, DataSource.GLASSDOOR, DataSource.WEBSITE]
            logger.info(f"No sources specified, using all available sources: {[s.value for s in sources_to_use]}")
        else:
            logger.info(f"Using specified sources: {[s.value for s in sources_to_use]}")
        
        # Validate data sources
        invalid_sources = [source for source in sources_to_use if source not in settings.available_sources]
        if invalid_sources:
            return CollectionErrorResponse(
                success=False,
                error=ErrorResponse(
                    code="VALIDATION_ERROR",
                    message="Invalid data source specified",
                    details=ErrorDetail(
                        field="sources",
                        value=invalid_sources
                    )
                )
            )
        
        # Create updated request with resolved sources
        updated_request = CollectionRequest(
            brand_id=request.brand_id,
            competitor_id=request.competitor_id,
            area_id=request.area_id,
            sources=sources_to_use
        )
        
        # Start the collection job
        job_id = await job_manager.start_collection_job(updated_request)
        
        return CollectionStartResponse(
            success=True,
            job_id=job_id,
            status="started",
            estimated_duration=180  # 3 minutes
        )
        
    except Exception as e:
        logger.error(f"Error starting data collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while starting data collection"
        )


@router.get(
    "/api/v1/collect/{job_id}/status",
    response_model=CollectionStatusResponse,
    responses={
        404: {"model": CollectionErrorResponse}
    },
    summary="Get Collection Status",
    description="Get the current status and progress of a data collection job"
)
async def get_collection_status(job_id: str):
    """Get the status of a data collection job"""
    try:
        logger.info(f"Getting status for job {job_id}")
        
        job = await job_manager.get_job_status(job_id)
        
        if not job:
            return CollectionErrorResponse(
                success=False,
                error=ErrorResponse(
                    code="NOT_FOUND",
                    message="Collection job not found",
                    details=ErrorDetail(
                        field="job_id",
                        value=job_id
                    )
                )
            )
        
        return CollectionStatusResponse(
            success=True,
            data={
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "completed_sources": job.completed_sources,
                "remaining_sources": job.remaining_sources,
                "estimated_completion": job.estimated_completion,
                "completed_at": job.completed_at,
                "current_step": job.current_step
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while getting job status"
        )


@router.get(
    "/api/v1/collect/{job_id}/data", 
    response_model=CollectionDataResponse,
    responses={
        404: {"model": CollectionErrorResponse}
    },
    summary="Get Collection Data",
    description="Get the collected data from a completed data collection job"
)
async def get_collection_data(job_id: str):
    """Get the collected data for a job"""
    try:
        logger.info(f"Getting data for job {job_id}")
        
        collected_data = await job_manager.get_job_data(job_id)
        
        if not collected_data:
            # Check if job exists but is not completed
            job = await job_manager.get_job_status(job_id)
            if not job:
                return CollectionErrorResponse(
                    success=False,
                    error=ErrorResponse(
                        code="NOT_FOUND",
                        message="Collection job not found",
                        details=ErrorDetail(
                            field="job_id",
                            value=job_id
                        )
                    )
                )
            else:
                return CollectionErrorResponse(
                    success=False,
                    error=ErrorResponse(
                        code="JOB_NOT_COMPLETED",
                        message=f"Collection job is not completed yet. Current status: {job.status}",
                        details=ErrorDetail(
                            field="status",
                            value=job.status
                        )
                    )
                )
        
        return CollectionDataResponse(
            success=True,
            data=collected_data
        )
        
    except Exception as e:
        logger.error(f"Error getting job data for {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while getting job data"
        )


@router.get(
    "/api/v1/sources/config",
    response_model=DataSourcesConfigResponse,
    summary="Get Data Sources Configuration",
    description="Get configuration information for available data sources"
)
async def get_data_sources_config():
    """Get configuration for available data sources"""
    try:
        logger.info("Getting data sources configuration")
        
        # Define available data sources with their configurations
        sources_config = [
            DataSourceConfig(
                id=DataSource.NEWS,
                name="News APIs",
                description="News sentiment analysis from various news sources",
                enabled=True,
                rate_limit=settings.news_rate_limit
            ),
            DataSourceConfig(
                id=DataSource.SOCIAL_MEDIA,
                name="Social Media",
                description="Social media sentiment analysis from Twitter, Facebook, LinkedIn",
                enabled=True,
                rate_limit=settings.social_media_rate_limit
            ),
            DataSourceConfig(
                id=DataSource.GLASSDOOR,
                name="Glassdoor Reviews",
                description="Employee reviews and company ratings from Glassdoor",
                enabled=True,
                rate_limit=settings.glassdoor_rate_limit
            ),
            DataSourceConfig(
                id=DataSource.WEBSITE,
                name="Website Analysis",
                description="Website performance, UX, and feature analysis",
                enabled=True,
                rate_limit=settings.website_rate_limit
            )
        ]
        
        return DataSourcesConfigResponse(
            success=True,
            data={
                "available_sources": sources_config
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting data sources config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while getting data sources configuration"
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check the health status of the data collection service"
)
async def health_check():
    """Health check endpoint"""
    try:
        # Get active jobs count
        active_jobs = await job_manager.get_active_jobs_count()
        
        return HealthCheckResponse(
            status="healthy",
            service="data-collection-service",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            active_jobs=active_jobs
        )
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is unhealthy"
        )


# Additional endpoints for management (optional)

@router.delete(
    "/api/v1/collect/{job_id}",
    summary="Cancel Collection Job",
    description="Cancel a running data collection job"
)
async def cancel_collection_job(job_id: str):
    """Cancel a data collection job"""
    try:
        logger.info(f"Cancelling job {job_id}")
        
        success = await job_manager.cancel_job(job_id)
        
        if not success:
            return CollectionErrorResponse(
                success=False,
                error=ErrorResponse(
                    code="NOT_FOUND",
                    message="Collection job not found or cannot be cancelled",
                    details=ErrorDetail(
                        field="job_id",
                        value=job_id
                    )
                )
            )
        
        return {"success": True, "message": f"Job {job_id} cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while cancelling job"
        )


@router.get(
    "/api/v1/stats",
    summary="Get Service Statistics",
    description="Get statistics about the data collection service"
)
async def get_service_statistics():
    """Get service statistics"""
    try:
        logger.info("Getting service statistics")
        
        stats = await job_manager.get_job_statistics()
        
        return {
            "success": True,
            "data": {
                "service_stats": stats,
                "timestamp": datetime.utcnow(),
                "uptime": "Service running",  # Could be enhanced with actual uptime
                "version": "1.0.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting service statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while getting statistics"
        ) 
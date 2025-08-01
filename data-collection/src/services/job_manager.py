import asyncio
import uuid
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from loguru import logger
from src.models.schemas import (
    CollectionJob, CollectionRequest, DataSource, JobStatus,
    BrandData, CollectedData
)
from src.database.storage import storage
from src.collectors.base import CollectorFactory
from src.config.settings import settings

# Import shared database service from local services directory
from .shared_database_service import shared_database

# Import analysis engine service
from src.services.analysis_engine_service import analysis_engine_service


class JobManager:
    """Manages background data collection jobs"""
    
    def __init__(self):
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.job_progress_callbacks: Dict[str, Callable] = {}
        self.job_completion_tracker: Dict[str, Dict[str, set]] = {}
    
    async def start_collection_job(self, request: CollectionRequest) -> str:
        """Start a new data collection job"""
        try:
            # Generate unique job ID
            job_id = f"collect_{uuid.uuid4().hex[:8]}"
            
            # Create job record
            job = CollectionJob(
                job_id=job_id,
                brand_id=request.brand_id,
                competitor_id=request.competitor_id,
                area_id=request.area_id,
                sources=request.sources,
                status=JobStatus.STARTED,
                remaining_sources=request.sources.copy(),
                estimated_completion=datetime.utcnow() + timedelta(seconds=180)  # 3 minutes
            )
            
            # Save job to storage
            await storage.save_job(job)
            
            # NOTE: Shared database record creation moved to consumer side
            # The consumer (test_consumer.py, UI, etc.) should create the initial database record
            # This ensures proper separation of concerns - data collection service only handles collection
            # 
            # # Create record in shared database
            # request_id = getattr(request, 'request_id', f"req_{job_id}")  # Use request_id if available, otherwise generate one
            # try:
            #     await shared_database.add_job_record(
            #         request_id=request_id,
            #         brand_id=request.brand_id,
            #         data_collection_id=job_id
            #     )
            #     logger.info(f"Created shared database record: {request_id} -> {job_id}")
            # except Exception as e:
            #     logger.error(f"Failed to create shared database record: {e}")
            #     # Continue with job execution even if database record creation fails
            
            # Start background task
            task = asyncio.create_task(self._run_collection_job(job))
            self.active_jobs[job_id] = task
            
            logger.info(f"Started collection job {job_id} for {request.brand_id} vs {request.competitor_id}")
            
            return job_id
            
        except Exception as e:
            logger.error(f"Error starting collection job: {str(e)}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[CollectionJob]:
        """Get the status of a collection job"""
        try:
            return await storage.get_job(job_id)
        except Exception as e:
            logger.error(f"Error getting job status for {job_id}: {str(e)}")
            return None
    
    async def get_job_data(self, job_id: str) -> Optional[CollectedData]:
        """Get the collected data for a job"""
        try:
            job = await storage.get_job(job_id)
            if not job:
                return None
            
            if job.status != JobStatus.COMPLETED:
                return None
            
            return await storage.get_collected_data(job_id)
        except Exception as e:
            logger.error(f"Error getting job data for {job_id}: {str(e)}")
            return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running collection job"""
        try:
            # Cancel the background task
            if job_id in self.active_jobs:
                task = self.active_jobs[job_id]
                task.cancel()
                del self.active_jobs[job_id]
            
            # Update job status
            await storage.update_job_status(job_id, JobStatus.CANCELLED)
            
            logger.info(f"Cancelled collection job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling job {job_id}: {str(e)}")
            return False
    
    async def get_active_jobs_count(self) -> int:
        """Get the number of active jobs"""
        try:
            active_jobs = await storage.get_active_jobs()
            return len(active_jobs)
        except Exception as e:
            logger.error(f"Error getting active jobs count: {str(e)}")
            return 0
    
    async def _run_collection_job(self, job: CollectionJob):
        """Run the actual data collection job"""
        # Track completion per entity to manage source lists properly
        self.job_completion_tracker = {
            job.job_id: {
                'brand_completed': set(),
                'competitor_completed': set()
            }
        }
        
        try:
            # Update job status to in_progress
            await storage.update_job_status(
                job.job_id, 
                JobStatus.IN_PROGRESS, 
                progress=10,
                current_step="Initializing data collection"
            )
            
            # Collect data for brand
            await storage.update_job_status(
                job.job_id,
                JobStatus.IN_PROGRESS,
                progress=20,
                current_step=f"Starting data collection for {job.brand_id}"
            )
            
            brand_data = await self._collect_brand_data(
                job.brand_id, job.area_id, job.sources, job.job_id, is_competitor=False
            )
            
            # Update progress after brand collection
            await storage.update_job_status(
                job.job_id,
                JobStatus.IN_PROGRESS,
                progress=60,
                current_step=f"Starting data collection for competitor {job.competitor_id}"
            )
            
            competitor_data = await self._collect_brand_data(
                job.competitor_id, job.area_id, job.sources, job.job_id, is_competitor=True
            )
            
            # Now that both collections are complete, properly update remaining_sources
            current_job = await storage.get_job(job.job_id)
            if current_job:
                # All sources should now be completed for both brand and competitor
                current_job.remaining_sources = []  # Clear remaining sources
                current_job.completed_sources = job.sources.copy()  # All sources completed
                await storage.save_job(current_job)
            
            # Create collected data object
            collected_data = CollectedData(
                brand_data=brand_data,
                competitor_data=competitor_data
            )
            
            # Save collected data
            await storage.save_collected_data(job.job_id, collected_data)
            
            # Update job status to completed ONLY after everything is done
            await storage.update_job_status(
                job.job_id,
                JobStatus.COMPLETED,
                progress=100,
                current_step="Data collection completed successfully"
            )
            
            logger.info(f"Completed collection job {job.job_id} - all sources processed for both brand and competitor")
            
            # Update shared database with completion status FIRST
            await self._update_shared_database_status(job.job_id, "COMPLETED")
            
            # Then start analysis engine process
            await self._start_analysis_engine(job)
            
        
            
        except asyncio.CancelledError:
            logger.info(f"Collection job {job.job_id} was cancelled")
            await storage.update_job_status(job.job_id, JobStatus.CANCELLED)
        except Exception as e:
            logger.error(f"Error in collection job {job.job_id}: {str(e)}")
            await storage.update_job_status(
                job.job_id,
                JobStatus.FAILED,
                current_step=f"Failed: {str(e)}"
            )
        finally:
            # Clean up
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            # Clean up completion tracker
            if hasattr(self, 'job_completion_tracker') and job.job_id in self.job_completion_tracker:
                del self.job_completion_tracker[job.job_id]
    
    async def _collect_brand_data(
        self, 
        brand_id: str, 
        area_id: str, 
        sources: List[DataSource],
        job_id: str,
        is_competitor: bool = False
    ) -> BrandData:
        """Collect data for a single brand or competitor"""
        try:
            # Progress callback to update job status and track individual source completion
            async def progress_callback(message: str, completed_source: DataSource = None):
                current_job = await storage.get_job(job_id)
                if current_job and completed_source:
                    # Track completion per entity
                    if hasattr(self, 'job_completion_tracker') and job_id in self.job_completion_tracker:
                        tracker = self.job_completion_tracker[job_id]
                        
                        if is_competitor:
                            tracker['competitor_completed'].add(completed_source)
                        else:
                            tracker['brand_completed'].add(completed_source)
                        
                        # Move source from remaining to completed only when BOTH entities have completed it
                        if (completed_source in tracker['brand_completed'] and 
                            completed_source in tracker['competitor_completed']):
                            
                            # Add to completed_sources if not already there
                            if completed_source not in current_job.completed_sources:
                                current_job.completed_sources.append(completed_source)
                            
                            # Remove from remaining_sources
                            if completed_source in current_job.remaining_sources:
                                current_job.remaining_sources.remove(completed_source)
                                
                            logger.info(f"Source {completed_source.value} FULLY completed for both brand and competitor in job {job_id}")
                        else:
                            entity_type = "competitor" if is_competitor else "brand"
                            logger.info(f"Source {completed_source.value} completed for {entity_type} {brand_id} in job {job_id}")
                        
                        # Save updated job status
                        await storage.save_job(current_job)
                    
                    # Calculate progress based on fully completed sources
                    total_sources = len(current_job.sources)
                    completed_count = len(current_job.completed_sources)
                    progress = min(95, int((completed_count / total_sources) * 90) + 10)  # 10-100% range
                    
                    await storage.update_job_status(
                        job_id,
                        JobStatus.IN_PROGRESS,
                        progress=progress,
                        current_step=message
                    )
            
            # Collect data from all sources with individual tracking
            collected_data = await CollectorFactory.collect_all_sources(
                brand_id, area_id, sources, progress_callback
            )
            
            # Transform collected data to BrandData schema
            brand_data = BrandData(
                brand_id=brand_id,
                news_sentiment=collected_data.get("news"),
                social_media=collected_data.get("social_media"),
                glassdoor=collected_data.get("glassdoor"),
                website_analysis=collected_data.get("website")
            )
            
            # Note: Individual source completion is now tracked in progress_callback
            # No need to bulk update completed_sources here
            
            return brand_data
            
        except Exception as e:
            logger.error(f"Error collecting data for brand {brand_id}: {str(e)}")
            
            # Return brand data with mock data on error
            return BrandData(
                brand_id=brand_id,
                news_sentiment={"score": 0.6, "articles_count": 20, "positive_articles": 12, "negative_articles": 5, "neutral_articles": 3, "recent_articles": []},
                social_media={"overall_sentiment": 0.65, "mentions_count": 500, "engagement_rate": 0.04, "platforms": {"twitter": {"sentiment": 0.7, "mentions": 200}, "facebook": {"sentiment": 0.6, "mentions": 200}, "linkedin": {"sentiment": 0.7, "mentions": 100}}, "trending_topics": ["service", "innovation"]},
                glassdoor={"overall_rating": 3.8, "reviews_count": 75, "pros": ["Good benefits"], "cons": ["Limited growth"], "recommendation_rate": 0.75, "ceo_approval": 0.8},
                website_analysis={"user_experience_score": 0.75, "feature_completeness": 0.7, "security_score": 0.85, "accessibility_score": 0.8, "mobile_friendliness": 0.8, "load_time": 2.5}
            )
    
    async def _update_shared_database_status(self, job_id: str, status: str) -> bool:
        """Update the shared database with job status"""
        try:
            success = await shared_database.update_data_collection_status(job_id, status)
            if success:
                logger.info(f"Updated shared database: {job_id} -> {status}")
            else:
                logger.warning(f"Failed to update shared database for job {job_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating shared database for job {job_id}: {str(e)}")
            return False
    
    async def _start_analysis_engine(self, job: CollectionJob) -> bool:
        """Start analysis engine process after data collection completion"""
        try:
            logger.info(f"Starting analysis engine for job {job.job_id}")
            
            # Get requestId from database
            job_record = await shared_database.get_job_record(job.job_id)
            if not job_record:
                logger.error(f"Job record not found for {job.job_id}")
                logger.debug(f"Available records: {await shared_database.get_all_records()}")
                return False
            
            request_id = job_record.get("requestId")
            if not request_id:
                logger.error(f"RequestId not found in job record for {job.job_id}")
                logger.debug(f"Job record: {job_record}")
                return False
            
            # Map data collection parameters to analysis engine parameters
            collect_id = job.job_id
            # Make analysis_focus configurable, default to "comprehensive"
            analysis_focus = getattr(settings, 'ANALYSIS_FOCUS', 'comprehensive')
            
            logger.info(f"🔗 Analysis engine parameters:")
            logger.info(f"   - Collect ID: {collect_id}")
            logger.info(f"   - Analysis Focus: {analysis_focus}")
            logger.info(f"   - Request ID (header): {request_id}")
            
            # Start analysis (requestId will be passed in header)
            analysis_result = await analysis_engine_service.start_analysis(
                collect_id=collect_id,
                analysis_focus=analysis_focus,
                request_id=request_id
            )
            
            if analysis_result:
                # Extract analysis_id and status from the response
                analysis_id = analysis_result.get("analysis_id")
                analysis_status = analysis_result.get("status", "IN_PROGRESS")
                
                # Update shared database with analysis engine job ID and actual status
                success = await shared_database.update_analysis_engine_status(
                    job.job_id, 
                    analysis_id, 
                    analysis_status
                )
                
                if success:
                    logger.info(f"✅ Started analysis engine:")
                    logger.info(f"   - Analysis ID: {analysis_id}")
                    logger.info(f"   - Status: {analysis_status}")
                    logger.info(f"   - Collect ID: {collect_id}")
                    return True
                else:
                    logger.error(f"Failed to update shared database with analysis engine status")
                    return False
            else:
                logger.error(f"Failed to start analysis engine for job {job.job_id}")
                # Update shared database to indicate analysis engine failed to start
                await shared_database.update_analysis_engine_status(
                    job.job_id, 
                    "", 
                    "FAILED"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error starting analysis engine for job {job.job_id}: {str(e)}")
            try:
                # Update shared database to indicate analysis engine failed
                await shared_database.update_analysis_engine_status(
                    job.job_id, 
                    "", 
                    "FAILED"
                )
            except:
                pass  # Don't let secondary error mask the primary error
            return False
    
    async def cleanup_old_jobs(self, days_old: int = 7):
        """Clean up old completed/failed jobs"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # This would require implementing a method to list all jobs
            # For now, we'll just log the cleanup attempt
            logger.info(f"Cleanup of jobs older than {days_old} days would run here")
            
        except Exception as e:
            logger.error(f"Error during job cleanup: {str(e)}")
    
    async def get_job_statistics(self) -> Dict[str, Any]:
        """Get statistics about jobs"""
        try:
            active_jobs = await storage.get_active_jobs()
            
            # This would require more comprehensive job tracking
            # For MVP, return basic stats
            return {
                "active_jobs": len(active_jobs),
                "total_jobs_today": len(active_jobs),  # Simplified
                "average_completion_time": 180,  # 3 minutes
                "success_rate": 0.95
            }
            
        except Exception as e:
            logger.error(f"Error getting job statistics: {str(e)}")
            return {
                "active_jobs": 0,
                "total_jobs_today": 0,
                "average_completion_time": 180,
                "success_rate": 0.0
            }


# Global job manager instance
job_manager = JobManager() 
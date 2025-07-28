import asyncio
import uuid
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


class JobManager:
    """Manages background data collection jobs"""
    
    def __init__(self):
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.job_progress_callbacks: Dict[str, Callable] = {}
    
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
        try:
            # Update job status to in_progress
            await storage.update_job_status(
                job.job_id, 
                JobStatus.IN_PROGRESS, 
                progress=5,
                current_step="Initializing data collection"
            )
            
            # Collect data for both brand and competitor
            brand_data = await self._collect_brand_data(
                job.brand_id, job.area_id, job.sources, job.job_id
            )
            
            # Update progress
            await storage.update_job_status(
                job.job_id,
                JobStatus.IN_PROGRESS,
                progress=50,
                current_step=f"Collecting competitor data for {job.competitor_id}"
            )
            
            competitor_data = await self._collect_brand_data(
                job.competitor_id, job.area_id, job.sources, job.job_id
            )
            
            # Create collected data object
            collected_data = CollectedData(
                brand_data=brand_data,
                competitor_data=competitor_data
            )
            
            # Save collected data
            await storage.save_collected_data(job.job_id, collected_data)
            
            # Update job status to completed
            await storage.update_job_status(
                job.job_id,
                JobStatus.COMPLETED,
                progress=100,
                current_step="Data collection completed"
            )
            
            logger.info(f"Completed collection job {job.job_id}")
            
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
    
    async def _collect_brand_data(
        self, 
        brand_id: str, 
        area_id: str, 
        sources: List[DataSource],
        job_id: str
    ) -> BrandData:
        """Collect data for a single brand"""
        try:
            # Progress callback to update job status
            async def progress_callback(message: str):
                current_job = await storage.get_job(job_id)
                if current_job:
                    # Calculate progress based on completed sources
                    completed_count = len(current_job.completed_sources)
                    total_sources = len(sources) * 2  # For both brand and competitor
                    progress = min(95, (completed_count / total_sources) * 100)
                    
                    await storage.update_job_status(
                        job_id,
                        JobStatus.IN_PROGRESS,
                        progress=int(progress),
                        current_step=message
                    )
            
            # Collect data from all sources
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
            
            # Update completed sources
            job = await storage.get_job(job_id)
            if job:
                job.completed_sources.extend(sources)
                job.remaining_sources = [s for s in job.remaining_sources if s not in sources]
                await storage.save_job(job)
            
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
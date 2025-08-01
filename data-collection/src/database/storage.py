import json
import os
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod
from src.models.schemas import CollectionJob, CollectedData, DataSource
from src.config.settings import settings
from loguru import logger


class StorageInterface(ABC):
    """Abstract interface for data storage operations"""
    
    @abstractmethod
    async def save_job(self, job: CollectionJob) -> bool:
        pass
    
    @abstractmethod
    async def get_job(self, job_id: str) -> Optional[CollectionJob]:
        pass
    
    @abstractmethod
    async def update_job_status(self, job_id: str, status: str, progress: int = None, current_step: str = None) -> bool:
        pass
    
    @abstractmethod
    async def save_collected_data(self, job_id: str, data: CollectedData) -> bool:
        pass
    
    @abstractmethod
    async def get_collected_data(self, job_id: str) -> Optional[CollectedData]:
        pass
    
    @abstractmethod
    async def get_active_jobs(self) -> List[CollectionJob]:
        pass


class FlatFileStorage(StorageInterface):
    """Flat file storage implementation using JSON files"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or settings.data_storage_path
        self.jobs_path = os.path.join(self.storage_path, "jobs")
        self.data_path = os.path.join(self.storage_path, "collected_data")
        
        # Ensure directories exist
        os.makedirs(self.jobs_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)
    
    def _get_job_file_path(self, job_id: str) -> str:
        return os.path.join(self.jobs_path, f"{job_id}.json")
    
    def _get_data_file_path(self, job_id: str) -> str:
        return os.path.join(self.data_path, f"{job_id}.json")
    
    async def save_job(self, job: CollectionJob) -> bool:
        try:
            file_path = self._get_job_file_path(job.job_id)
            job_data = job.model_dump()
            
            # Convert datetime objects to ISO format strings
            for key, value in job_data.items():
                if isinstance(value, datetime):
                    job_data[key] = value.isoformat()
            
            # Convert DataSource enums to strings using .value
            for field in ['sources', 'completed_sources', 'remaining_sources']:
                if field in job_data and job_data[field]:
                    job_data[field] = [source.value if hasattr(source, 'value') else str(source) for source in job_data[field]]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Job {job.job_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving job {job.job_id}: {str(e)}")
            return False
    
    async def get_job(self, job_id: str) -> Optional[CollectionJob]:
        try:
            file_path = self._get_job_file_path(job_id)
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            datetime_fields = ['created_at', 'started_at', 'completed_at', 'estimated_completion']
            for field in datetime_fields:
                if job_data.get(field):
                    job_data[field] = datetime.fromisoformat(job_data[field])
            
            # Convert string arrays back to DataSource enums
            for field in ['sources', 'completed_sources', 'remaining_sources']:
                if field in job_data and job_data[field]:
                    job_data[field] = [DataSource(source) for source in job_data[field]]
            
            return CollectionJob(**job_data)
        except Exception as e:
            logger.error(f"Error loading job {job_id}: {str(e)}")
            return None
    
    async def update_job_status(self, job_id: str, status: str, progress: int = None, current_step: str = None) -> bool:
        try:
            job = await self.get_job(job_id)
            if not job:
                return False
            
            job.status = status
            if progress is not None:
                job.progress = progress
            if current_step is not None:
                job.current_step = current_step
            
            if status == "completed":
                job.completed_at = datetime.utcnow()
            
            return await self.save_job(job)
        except Exception as e:
            logger.error(f"Error updating job status for {job_id}: {str(e)}")
            return False
    
    async def save_collected_data(self, job_id: str, data: CollectedData) -> bool:
        try:
            file_path = self._get_data_file_path(job_id)
            data_dict = data.model_dump()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False, default=str)
            
            # Also update the job with the collected data
            job = await self.get_job(job_id)
            if job:
                job.collected_data = data
                await self.save_job(job)
            
            logger.info(f"Collected data for job {job_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving collected data for {job_id}: {str(e)}")
            return False
    
    async def get_collected_data(self, job_id: str) -> Optional[CollectedData]:
        try:
            file_path = self._get_data_file_path(job_id)
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)
            
            return CollectedData(**data_dict)
        except Exception as e:
            logger.error(f"Error loading collected data for {job_id}: {str(e)}")
            return None
    
    async def get_active_jobs(self) -> List[CollectionJob]:
        try:
            active_jobs = []
            if not os.path.exists(self.jobs_path):
                return active_jobs
            
            for filename in os.listdir(self.jobs_path):
                if filename.endswith('.json'):
                    job_id = filename.replace('.json', '')
                    job = await self.get_job(job_id)
                    if job and job.status in ["started", "in_progress"]:
                        active_jobs.append(job)
            
            return active_jobs
        except Exception as e:
            logger.error(f"Error getting active jobs: {str(e)}")
            return []


# Storage factory
def get_storage() -> StorageInterface:
    """Factory function to get the appropriate storage implementation"""
    return FlatFileStorage()


# Global storage instance
storage = get_storage() 
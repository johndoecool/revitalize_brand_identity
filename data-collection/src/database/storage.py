import json
import os
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod
import chromadb
from chromadb.config import Settings as ChromaSettings
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


class VectorStorage(StorageInterface):
    """Vector database storage implementation using ChromaDB"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.vector_db_path
        self.flat_storage = FlatFileStorage()  # Fallback storage
        
        try:
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
            )
            
            # Create collections
            self.jobs_collection = self.client.get_or_create_collection("jobs")
            self.data_collection = self.client.get_or_create_collection("collected_data")
            
            logger.info("Vector database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector database: {str(e)}")
            logger.info("Falling back to flat file storage")
            self.client = None
    
    async def save_job(self, job: CollectionJob) -> bool:
        try:
            if not self.client:
                return await self.flat_storage.save_job(job)
            
            job_data = job.model_dump()
            job_text = f"Job {job.job_id} for brand {job.brand_id} vs {job.competitor_id} in area {job.area_id}"
            
            # Convert datetime objects to strings
            for key, value in job_data.items():
                if isinstance(value, datetime):
                    job_data[key] = value.isoformat()
            
            # Convert DataSource lists to comma-separated strings for ChromaDB
            if 'sources' in job_data and job_data['sources']:
                job_data['sources'] = ','.join([source.value if hasattr(source, 'value') else str(source) for source in job_data['sources']])
            elif 'sources' in job_data:
                job_data['sources'] = ''
            
            if 'completed_sources' in job_data and job_data['completed_sources']:
                job_data['completed_sources'] = ','.join([source.value if hasattr(source, 'value') else str(source) for source in job_data['completed_sources']])
            elif 'completed_sources' in job_data:
                job_data['completed_sources'] = ''
                
            if 'remaining_sources' in job_data and job_data['remaining_sources']:
                job_data['remaining_sources'] = ','.join([source.value if hasattr(source, 'value') else str(source) for source in job_data['remaining_sources']])
            elif 'remaining_sources' in job_data:
                job_data['remaining_sources'] = ''
            
            # Remove collected_data for ChromaDB metadata (too complex)
            if 'collected_data' in job_data:
                del job_data['collected_data']
            
            self.jobs_collection.upsert(
                documents=[job_text],
                metadatas=[job_data],
                ids=[job.job_id]
            )
            
            # Also save to flat file as backup
            await self.flat_storage.save_job(job)
            return True
        except Exception as e:
            logger.error(f"Error saving job to vector DB: {str(e)}")
            return await self.flat_storage.save_job(job)
    
    async def get_job(self, job_id: str) -> Optional[CollectionJob]:
        try:
            if not self.client:
                return await self.flat_storage.get_job(job_id)
            
            results = self.jobs_collection.get(ids=[job_id])
            if not results['metadatas']:
                return await self.flat_storage.get_job(job_id)
            
            job_data = results['metadatas'][0]
            
            # Convert datetime strings back to datetime objects
            datetime_fields = ['created_at', 'started_at', 'completed_at', 'estimated_completion']
            for field in datetime_fields:
                if job_data.get(field):
                    job_data[field] = datetime.fromisoformat(job_data[field])
            
            # Convert comma-separated strings back to DataSource enums
            if 'sources' in job_data and job_data['sources']:
                job_data['sources'] = [DataSource(source.strip()) for source in job_data['sources'].split(',') if source.strip()]
            elif 'sources' in job_data:
                job_data['sources'] = []
                
            if 'completed_sources' in job_data and job_data['completed_sources']:
                job_data['completed_sources'] = [DataSource(source.strip()) for source in job_data['completed_sources'].split(',') if source.strip()]
            elif 'completed_sources' in job_data:
                job_data['completed_sources'] = []
                
            if 'remaining_sources' in job_data and job_data['remaining_sources']:
                job_data['remaining_sources'] = [DataSource(source.strip()) for source in job_data['remaining_sources'].split(',') if source.strip()]
            elif 'remaining_sources' in job_data:
                job_data['remaining_sources'] = []
            
            # Set collected_data to None for ChromaDB (it's stored separately)
            job_data['collected_data'] = None
            
            return CollectionJob(**job_data)
        except Exception as e:
            logger.error(f"Error getting job from vector DB: {str(e)}")
            return await self.flat_storage.get_job(job_id)
    
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
            logger.error(f"Error updating job status in vector DB: {str(e)}")
            return await self.flat_storage.update_job_status(job_id, status, progress, current_step)
    
    async def save_collected_data(self, job_id: str, data: CollectedData) -> bool:
        try:
            if not self.client:
                return await self.flat_storage.save_collected_data(job_id, data)
            
            # Create document text for vector search
            data_text = f"Collected data for job {job_id}: {data.brand_data.brand_id} vs {data.competitor_data.brand_id}"
            
            # Only store simple metadata for ChromaDB (complex data goes to flat file)
            simple_metadata = {
                "job_id": job_id,
                "brand_id": data.brand_data.brand_id,
                "competitor_id": data.competitor_data.brand_id,
                "has_news_data": bool(data.brand_data.news_sentiment),
                "has_social_data": bool(data.brand_data.social_media),
                "has_glassdoor_data": bool(data.brand_data.glassdoor),
                "has_website_data": bool(data.brand_data.website_analysis)
            }
            
            self.data_collection.upsert(
                documents=[data_text],
                metadatas=[simple_metadata],
                ids=[job_id]
            )
            
            # Always save full data to flat file (this is the primary storage)
            await self.flat_storage.save_collected_data(job_id, data)
            return True
        except Exception as e:
            logger.error(f"Error saving collected data to vector DB: {str(e)}")
            return await self.flat_storage.save_collected_data(job_id, data)
    
    async def get_collected_data(self, job_id: str) -> Optional[CollectedData]:
        try:
            if not self.client:
                return await self.flat_storage.get_collected_data(job_id)
            
            # For vector storage, always get the full data from flat file storage
            # ChromaDB only stores simple metadata for search purposes
            return await self.flat_storage.get_collected_data(job_id)
        except Exception as e:
            logger.error(f"Error getting collected data from vector DB: {str(e)}")
            return await self.flat_storage.get_collected_data(job_id)
    
    async def get_active_jobs(self) -> List[CollectionJob]:
        try:
            if not self.client:
                return await self.flat_storage.get_active_jobs()
            
            # For ChromaDB, we'll use the flat storage as it's more efficient for this operation
            return await self.flat_storage.get_active_jobs()
        except Exception as e:
            logger.error(f"Error getting active jobs from vector DB: {str(e)}")
            return await self.flat_storage.get_active_jobs()


# Storage factory
def get_storage() -> StorageInterface:
    """Factory function to get the appropriate storage implementation"""
    if settings.use_vector_db:
        return VectorStorage()
    else:
        return FlatFileStorage()


# Global storage instance
storage = get_storage() 
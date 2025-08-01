#!/usr/bin/env python3
"""
Shared Database Service for managing shared/database.json
Following the same pattern as analysis-engine/app/services/database_service.py
"""

import json
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import sys

# Import shared config from local config directory
import sys
from pathlib import Path

# Add the config directory to path for shared_config import
config_path = Path(__file__).parent.parent / "config"
sys.path.insert(0, str(config_path))

from shared_config import shared_config

logger = logging.getLogger(__name__)

class SharedDatabaseService:
    """Service for managing the shared database.json file - following analysis-engine pattern"""
    
    def __init__(self, db_path: str = None):
        # Use configured path from shared_config if no path provided
        if db_path is None:
            db_path = shared_config.get_database_path()
            
        self.db_path = db_path
        self._lock = asyncio.Lock()
        
        # Ensure directory exists using shared config
        shared_config.ensure_database_directory()
        
        logger.info(f"Shared database initialized at: {self.db_path}")
    
    async def _read_database(self) -> List[Dict[str, Any]]:
        """Read the database.json file"""
        try:
            if not os.path.exists(self.db_path):
                # Create empty database if it doesn't exist
                await self._write_database([])
                return []
                
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
                
        except Exception as e:
            logger.error(f"Failed to read database: {e}")
            return []
    
    async def _write_database(self, data: List[Dict[str, Any]]):
        """Write data to the database.json file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"Failed to write database: {e}")
            raise
    
    async def add_job_record(
        self, 
        request_id: str, 
        brand_id: str, 
        data_collection_id: str
    ) -> bool:
        """Add a new job record to the database"""
        async with self._lock:
            try:
                data = await self._read_database()
                
                # Check if record already exists
                for record in data:
                    if record.get("dataCollectionId") == data_collection_id:
                        logger.warning(f"Job record with dataCollectionId {data_collection_id} already exists")
                        return False
                
                new_record = {
                    "requestId": request_id,
                    "brandId": brand_id,
                    "dataCollectionId": data_collection_id,
                    "dataCollectionStatus": "IN_PROGRESS",
                    "analysisEngineId": "",
                    "analysisEngineStatus": "",
                    "lastUpdated": datetime.now(timezone.utc).isoformat()
                }
                data.append(new_record)
                await self._write_database(data)
                logger.info(f"Added job record: {data_collection_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add job record: {e}")
                return False
    
    async def get_job_record(self, data_collection_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a job record by dataCollectionId"""
        async with self._lock:
            try:
                data = await self._read_database()
                
                for record in data:
                    if record.get("dataCollectionId") == data_collection_id:
                        return record
                        
                return None
                
            except Exception as e:
                logger.error(f"Failed to get job record: {e}")
                return None
    
    async def find_record(self, request_id: str, collect_id: str) -> Optional[Dict[str, Any]]:
        """Find a record by request_id and dataCollectionId - following analysis-engine pattern"""
        async with self._lock:
            try:
                data = await self._read_database()
                
                for record in data:
                    if (record.get("requestId") == request_id and 
                        record.get("dataCollectionId") == collect_id):
                        return record
                        
                return None
                
            except Exception as e:
                logger.error(f"Failed to find record: {e}")
                return None
    
    async def update_data_collection_status(self, data_collection_id: str, status: str) -> bool:
        """Update the data collection status of a job record"""
        async with self._lock:
            try:
                data = await self._read_database()
                
                for i, record in enumerate(data):
                    if record.get("dataCollectionId") == data_collection_id:
                        data[i]["dataCollectionStatus"] = status
                        data[i]["lastUpdated"] = datetime.now(timezone.utc).isoformat()
                        
                        await self._write_database(data)
                        logger.info(f"Updated data collection status for {data_collection_id} to {status}")
                        return True
                
                logger.warning(f"Job record with dataCollectionId {data_collection_id} not found")
                return False
                
            except Exception as e:
                logger.error(f"Failed to update data collection status: {e}")
                return False
    
    async def update_analysis_engine_status(
        self, 
        data_collection_id: str, 
        analysis_engine_id: str, 
        status: str
    ) -> bool:
        """Update the analysis engine status and ID of a job record - following analysis-engine pattern"""
        async with self._lock:
            try:
                data = await self._read_database()
                
                for i, record in enumerate(data):
                    if record.get("dataCollectionId") == data_collection_id:
                        # Update analysis engine fields
                        data[i]["analysisEngineId"] = analysis_engine_id
                        data[i]["analysisEngineStatus"] = status
                        data[i]["lastUpdated"] = datetime.now(timezone.utc).isoformat()
                        
                        await self._write_database(data)
                        logger.info(f"Updated analysis engine status for {data_collection_id} to {status} (ID: {analysis_engine_id})")
                        return True
                
                logger.warning(f"Job record with dataCollectionId {data_collection_id} not found")
                return False
                
            except Exception as e:
                logger.error(f"Failed to update analysis engine status: {e}")
                return False
    
    async def get_record_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a record by request_id - following analysis-engine pattern"""
        async with self._lock:
            try:
                data = await self._read_database()
                
                for record in data:
                    if record.get("requestId") == request_id:
                        return {
                            "requestId": record.get("requestId"),
                            "brandId": record.get("brandId"),
                            "dataCollectionId": record.get("dataCollectionId"),
                            "dataCollectionStatus": record.get("dataCollectionStatus"),
                            "analysisEngineId": record.get("analysisEngineId"),
                            "analysisEngineStatus": record.get("analysisEngineStatus"),
                            "lastUpdated": record.get("lastUpdated")
                        }
                        
                return None
                
            except Exception as e:
                logger.error(f"Failed to get record status: {e}")
                return None
    
    async def get_all_records(self) -> List[Dict[str, Any]]:
        """Get all job records"""
        async with self._lock:
            try:
                return await self._read_database()
            except Exception as e:
                logger.error(f"Failed to get all records: {e}")
                return []
    
    async def get_records_by_status(
        self, 
        data_collection_status: Optional[str] = None, 
        analysis_engine_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get job records filtered by status"""
        async with self._lock:
            try:
                data = await self._read_database()
                filtered_records = []
                
                for record in data:
                    dc_match = (data_collection_status is None or 
                               record.get("dataCollectionStatus") == data_collection_status)
                    ae_match = (analysis_engine_status is None or 
                               record.get("analysisEngineStatus") == analysis_engine_status)
                    if dc_match and ae_match:
                        filtered_records.append(record)
                
                return filtered_records
                
            except Exception as e:
                logger.error(f"Failed to get records by status: {e}")
                return []
    
    async def validate_data_collection_complete(self, request_id: str, collect_id: str) -> bool:
        """Validate that data collection is complete for the given request - following analysis-engine pattern"""
        try:
            record = await self.find_record(request_id, collect_id)
            
            if not record:
                logger.warning(f"No record found for request {request_id} and collect {collect_id}")
                return False
            
            data_status = record.get("dataCollectionStatus", "").upper()
            if data_status != "COMPLETED":
                logger.warning(f"Data collection not complete for request {request_id}: {data_status}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate data collection status: {e}")
            return False
    
    async def list_pending_analyses(self) -> List[Dict[str, Any]]:
        """List all records with pending analysis - following analysis-engine pattern"""
        async with self._lock:
            try:
                data = await self._read_database()
                pending = []
                
                for record in data:
                    data_status = record.get("dataCollectionStatus", "").upper()
                    analysis_status = record.get("analysisEngineStatus", "").upper()
                    
                    if data_status == "COMPLETED" and analysis_status in ["", "IN_PROGRESS"]:
                        pending.append(record)
                
                return pending
                
            except Exception as e:
                logger.error(f"Failed to list pending analyses: {e}")
                return []


# Create a singleton instance - following analysis-engine pattern
shared_database = SharedDatabaseService() 
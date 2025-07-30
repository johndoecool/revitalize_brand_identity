import json
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.core.config import Settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for managing the shared database.json file"""
    
    def __init__(self):
        self.settings = Settings()
        self.db_path = self.settings.DATABASE_JSON_PATH
        self._lock = asyncio.Lock()
        
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
    
    async def find_record(self, request_id: str, collect_id: str) -> Optional[Dict[str, Any]]:
        """Find a record by request_id and dataCollectionId"""
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
    
    async def update_analysis_status(
        self, 
        request_id: str, 
        collect_id: str, 
        analysis_id: str, 
        status: str
    ) -> bool:
        """Update the analysis engine status for a record"""
        async with self._lock:
            try:
                data = await self._read_database()
                
                for i, record in enumerate(data):
                    if (record.get("requestId") == request_id and 
                        record.get("dataCollectionId") == collect_id):
                        
                        # Update analysis engine fields
                        data[i]["analysisEngineId"] = analysis_id
                        data[i]["analysisEngineStatus"] = status
                        data[i]["lastUpdated"] = datetime.now(timezone.utc).isoformat()
                        
                        await self._write_database(data)
                        logger.info(f"Updated analysis status for request {request_id}: {status}")
                        return True
                
                logger.warning(f"Record not found for request {request_id} and collect {collect_id}")
                return False
                
            except Exception as e:
                logger.error(f"Failed to update analysis status: {e}")
                return False
    
    async def get_record_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a record by request_id"""
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
    
    async def validate_data_collection_complete(self, request_id: str, collect_id: str) -> bool:
        """Validate that data collection is complete for the given request"""
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
        """List all records with pending analysis"""
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

# Create a singleton instance
database_service = DatabaseService()

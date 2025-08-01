#!/usr/bin/env python3
"""
Test Consumer Script
Simulates how a consumer would use the data collection service and manage job status
"""

import asyncio
import aiohttp
import json
import uuid
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

# Add data collection services to path for shared database
data_collection_services_path = Path(__file__).parent / "data-collection" / "src" / "services"
sys.path.insert(0, str(data_collection_services_path))

from shared_database_service import shared_database


class TestConsumer:
    """Test consumer that demonstrates the complete workflow"""
    
    def __init__(self, data_collection_url: str = "http://localhost:8002"):
        self.data_collection_url = data_collection_url
        self.collect_endpoint = f"{data_collection_url}/api/v1/collect"
        self.status_endpoint = f"{data_collection_url}/api/v1/collect"
    
    async def start_data_collection_job(
        self, 
        brand_id: str, 
        competitor_id: str, 
        area_id: str, 
        sources: list
    ) -> Optional[Dict[str, Any]]:
        """
        Start a data collection job and create initial database entry
        
        Returns:
            Dict with requestId and dataCollectionId if successful, None if failed
        """
        try:
            # Generate unique request ID (as would be done by the UI)
            request_id = str(uuid.uuid4())
            
            # Prepare data collection request with request_id
            collect_request = {
                "brand_id": brand_id,
                "competitor_id": competitor_id,
                "area_id": area_id,
                "sources": sources,
                "request_id": request_id  # Include request_id for tracking
            }
            
            logger.info(f"Starting data collection job for brand: {brand_id}")
            logger.debug(f"Request ID: {request_id}")
            logger.debug(f"Collection request: {collect_request}")
            
            # Call data collection API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.collect_endpoint,
                    json=collect_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        data_collection_id = result.get("job_id")
                        
                        if data_collection_id:
                            logger.info(f"Data collection job started: {data_collection_id}")
                            
                            # Create initial entry in shared database (consumer responsibility)
                            success = await shared_database.add_job_record(
                                request_id=request_id,
                                brand_id=brand_id,
                                data_collection_id=data_collection_id
                            )
                            
                            if success:
                                logger.info(f"Created database entry for job {data_collection_id} with request_id: {request_id}")
                                return {
                                    "requestId": request_id,
                                    "brandId": brand_id,
                                    "dataCollectionId": data_collection_id,
                                    "dataCollectionStatus": "IN_PROGRESS",
                                    "analysisEngineId": "",
                                    "analysisEngineStatus": ""
                                }
                            else:
                                logger.error(f"Failed to create database entry for job {data_collection_id}")
                                return None
                        else:
                            logger.error("Data collection API returned success but no job_id found")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Data collection API failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error starting data collection job: {str(e)}")
            return None
    
    async def monitor_job_progress(self, data_collection_id: str, max_wait: int = 300):
        """
        Monitor a data collection job until completion
        
        Args:
            data_collection_id: The data collection job ID
            max_wait: Maximum time to wait in seconds
        """
        try:
            logger.info(f"Monitoring job progress: {data_collection_id}")
            
            for i in range(max_wait):
                await asyncio.sleep(2)  # Check every 2 seconds
                
                # Check data collection service status
                async with aiohttp.ClientSession() as session:
                    status_url = f"{self.status_endpoint}/{data_collection_id}/status"
                    async with session.get(status_url) as response:
                        if response.status == 200:
                            result = await response.json()
                            data = result.get('data', {})
                            
                            status = data.get('status', 'unknown')
                            progress = data.get('progress', 0)
                            current_step = data.get('current_step', 'N/A')
                            
                            if i % 10 == 0:  # Print every 20 seconds
                                logger.info(f"Progress: {progress}% - Status: {status} - Step: {current_step}")
                            
                            if status == "completed":
                                logger.info(f"Data collection completed for job {data_collection_id}")
                                await self._wait_for_analysis_engine_start(data_collection_id)
                                return True
                            elif status == "failed":
                                logger.error(f"Data collection failed for job {data_collection_id}")
                                return False
                
                # Check shared database status
                job_record = await shared_database.get_job_record(data_collection_id)
                if job_record:
                    dc_status = job_record.get('dataCollectionStatus', 'UNKNOWN')
                    ae_status = job_record.get('analysisEngineStatus', 'UNKNOWN')
                    ae_id = job_record.get('analysisEngineId', '')
                    
                    if i % 10 == 0:
                        logger.info(f"Shared DB - DC Status: {dc_status}, AE Status: {ae_status}, AE ID: {ae_id}")
            
            logger.warning(f"Job monitoring timed out after {max_wait} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Error monitoring job progress: {str(e)}")
            return False
    
    async def _wait_for_analysis_engine_start(self, data_collection_id: str, max_wait: int = 30):
        """Wait for analysis engine to start after data collection completion"""
        try:
            logger.info(f"Waiting for analysis engine to start for job {data_collection_id}")
            
            for i in range(max_wait):
                await asyncio.sleep(1)
                
                job_record = await shared_database.get_job_record(data_collection_id)
                if job_record:
                    ae_status = job_record.get('analysisEngineStatus', '')
                    ae_id = job_record.get('analysisEngineId', '')
                    
                    if ae_status == "IN_PROGRESS" and ae_id:
                        logger.info(f"Analysis engine started: {ae_id}")
                        return True
                    elif ae_status == "FAILED":
                        logger.error(f"Analysis engine failed to start for job {data_collection_id}")
                        return False
            
            logger.warning(f"Analysis engine didn't start within {max_wait} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for analysis engine: {str(e)}")
            return False
    
    async def get_job_status(self, data_collection_id: str) -> Optional[Dict[str, Any]]:
        """Get the current job status from shared database"""
        try:
            return await shared_database.get_job_record(data_collection_id)
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            return None
    
    async def list_all_jobs(self) -> list:
        """List all jobs in the shared database"""
        try:
            return await shared_database.get_all_records()
        except Exception as e:
            logger.error(f"Error listing all jobs: {str(e)}")
            return []


async def run_consumer_test():
    """Run a complete consumer test workflow"""
    logger.info("🧪 Starting Consumer Test Workflow")
    logger.info("=" * 60)
    
    consumer = TestConsumer()
    
    try:
        # Test data collection job
        job_info = await consumer.start_data_collection_job(
            brand_id="Apple",
            competitor_id="Google",
            area_id="employer_of_choice",
            sources=["glassdoor", "website", "social_media","news"]
        )
        
        if not job_info:
            logger.error("❌ Failed to start data collection job")
            return 1
        
        logger.info("✅ Data collection job started successfully")
        logger.info(f"📋 Job Info: {json.dumps(job_info, indent=2)}")
        
        # Monitor job progress
        success = await consumer.monitor_job_progress(job_info["dataCollectionId"])
        
        if success:
            logger.info("✅ Job completed successfully")
            
            # Get final status
            final_status = await consumer.get_job_status(job_info["dataCollectionId"])
            if final_status:
                logger.info("📊 Final Job Status:")
                logger.info(json.dumps(final_status, indent=2, default=str))
        else:
            logger.error("❌ Job failed or timed out")
        
        # List all jobs
        all_jobs = await consumer.list_all_jobs()
        logger.info(f"📋 Total jobs in database: {len(all_jobs)}")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Consumer test failed: {str(e)}")
        return 1


async def run_multiple_consumer_test():
    """Run multiple consumer jobs to test concurrent handling"""
    logger.info("🧪 Starting Multiple Consumer Test")
    logger.info("=" * 60)
    
    consumer = TestConsumer()
    
    try:
        # Start multiple jobs
        jobs = []
        for i in range(3):
            job_info = await consumer.start_data_collection_job(
                brand_id=f"TestBrand_{i}",
                competitor_id=f"TestCompetitor_{i}",
                area_id="employer_of_choice",
                sources=["glassdoor", "website"]
            )
            
            if job_info:
                jobs.append(job_info)
                logger.info(f"✅ Started job {i+1}: {job_info['dataCollectionId']}")
            else:
                logger.error(f"❌ Failed to start job {i+1}")
        
        logger.info(f"📊 Started {len(jobs)} jobs total")
        
        # Monitor all jobs
        monitor_tasks = []
        for job in jobs:
            task = asyncio.create_task(
                consumer.monitor_job_progress(job["dataCollectionId"], max_wait=180)
            )
            monitor_tasks.append(task)
        
        # Wait for all jobs to complete
        results = await asyncio.gather(*monitor_tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is True)
        logger.info(f"📊 Results: {success_count}/{len(jobs)} jobs completed successfully")
        
        # Show final database state
        all_jobs = await consumer.list_all_jobs()
        logger.info(f"📋 Final database state: {len(all_jobs)} total jobs")
        
        return 0 if success_count > 0 else 1
        
    except Exception as e:
        logger.error(f"❌ Multiple consumer test failed: {str(e)}")
        return 1


async def main():
    """Main function with test options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Consumer Script")
    parser.add_argument(
        "--test-type", 
        choices=["single", "multiple"], 
        default="single",
        help="Type of test to run"
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Data Collection Consumer Test Script")
    logger.info("Make sure data collection service is running on localhost:8002")
    logger.info("Make sure analysis engine service is running on localhost:8003")
    logger.info("")
    
    if args.test_type == "single":
        return await run_consumer_test()
    else:
        return await run_multiple_consumer_test()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 
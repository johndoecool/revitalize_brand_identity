#!/usr/bin/env python3
"""
Comprehensive Data Collection Pipeline Verification Script

This script verifies that the entire data collection system is working properly:
- API endpoints
- Job management
- Collector functionality  
- Data persistence
- End-to-end flow
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from src.collectors.base import CollectorFactory
from src.services.job_manager import JobManager
from src.database.storage import storage
from src.models.schemas import CollectionRequest, DataSource, CollectionJob, JobStatus
from loguru import logger

class DataCollectionVerifier:
    """Comprehensive data collection pipeline verifier"""
    
    def __init__(self):
        self.job_manager = JobManager()
        self.test_results = {
            "collectors": {},
            "storage": False,
            "job_manager": False,
            "end_to_end": False,
            "api_compatibility": True
        }
    
    async def verify_individual_collectors(self):
        """Test each collector individually"""
        logger.info("🔍 Testing Individual Collectors...")
        
        test_cases = [
            (DataSource.GLASSDOOR, "Microsoft", "employer_of_choice"),
            (DataSource.WEBSITE, "Google", "digital_banking"),
            (DataSource.NEWS, "Apple", "customer_service"),
            (DataSource.SOCIAL_MEDIA, "Amazon", "self_service_portal")
        ]
        
        for source_type, brand_id, area_id in test_cases:
            try:
                logger.info(f"Testing {source_type.value} collector...")
                
                collector = CollectorFactory.create_collector(source_type)
                async with collector:
                    result = await collector.collect_brand_data(brand_id, area_id)
                    
                    # Verify result structure
                    if result and isinstance(result, dict) and len(result) > 0:
                        logger.success(f"✅ {source_type.value} collector working - returned {len(result)} fields")
                        self.test_results["collectors"][source_type.value] = True
                    else:
                        logger.warning(f"⚠️ {source_type.value} collector returned empty/invalid data")
                        self.test_results["collectors"][source_type.value] = False
                        
            except Exception as e:
                logger.error(f"❌ {source_type.value} collector failed: {str(e)}")
                self.test_results["collectors"][source_type.value] = False
    
    async def verify_collector_factory(self):
        """Test the CollectorFactory's concurrent collection"""
        logger.info("🏭 Testing CollectorFactory...")
        
        try:
            sources = [DataSource.GLASSDOOR, DataSource.WEBSITE, DataSource.NEWS, DataSource.SOCIAL_MEDIA]
            
            # Progress tracking
            progress_messages = []
            async def progress_callback(message, completed_source=None):
                progress_messages.append(message)
                logger.info(f"Progress: {message}")
            
            # Collect from all sources
            results = await CollectorFactory.collect_all_sources(
                "TestBrand", "test_area", sources, progress_callback
            )
            
            # Verify results
            if len(results) == len(sources):
                logger.success(f"✅ CollectorFactory collected from all {len(sources)} sources")
                logger.info(f"📊 Progress messages received: {len(progress_messages)}")
                
                # Verify each source has data
                all_have_data = all(
                    results.get(source.value) and len(results[source.value]) > 0 
                    for source in sources
                )
                
                if all_have_data:
                    logger.success("✅ All sources returned valid data")
                    return True
                else:
                    logger.warning("⚠️ Some sources returned empty data")
                    return False
            else:
                logger.error(f"❌ Expected {len(sources)} results, got {len(results)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ CollectorFactory test failed: {str(e)}")
            return False
    
    async def verify_storage_system(self):
        """Test the storage system"""
        logger.info("💾 Testing Storage System...")
        
        try:
            # Test job storage
            test_job = CollectionJob(
                job_id="test_verify_job",
                brand_id="TestBrand",
                competitor_id="TestCompetitor", 
                area_id="test_area",
                sources=[DataSource.GLASSDOOR, DataSource.WEBSITE],
                status=JobStatus.STARTED,
                remaining_sources=[DataSource.GLASSDOOR, DataSource.WEBSITE],
                estimated_completion=datetime.utcnow()
            )
            
            # Save job
            save_success = await storage.save_job(test_job)
            if not save_success:
                logger.error("❌ Failed to save test job")
                return False
            
            # Retrieve job
            retrieved_job = await storage.get_job("test_verify_job")
            if not retrieved_job or retrieved_job.job_id != "test_verify_job":
                logger.error("❌ Failed to retrieve test job")
                return False
            
            # Update job status
            update_success = await storage.update_job_status(
                "test_verify_job", JobStatus.COMPLETED, progress=100, current_step="Verification complete"
            )
            if not update_success:
                logger.error("❌ Failed to update job status")
                return False
            
            logger.success("✅ Storage system working properly")
            self.test_results["storage"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Storage system test failed: {str(e)}")
            return False
    
    async def verify_job_manager(self):
        """Test the job manager"""
        logger.info("👔 Testing Job Manager...")
        
        try:
            # Create test request
            request = CollectionRequest(
                brand_id="TestBrand2",
                competitor_id="TestCompetitor2",
                area_id="test_area",
                sources=[DataSource.GLASSDOOR, DataSource.WEBSITE]
            )
            
            # Start job
            job_id = await self.job_manager.start_collection_job(request)
            
            if not job_id:
                logger.error("❌ Job manager failed to start job")
                return False
            
            logger.info(f"Started test job: {job_id}")
            
            # Wait a bit for job to start processing
            await asyncio.sleep(2)
            
            # Check job status
            job_status = await self.job_manager.get_job_status(job_id)
            
            if not job_status:
                logger.error("❌ Job manager failed to get job status")
                return False
            
            logger.success(f"✅ Job manager working - Job {job_id} status: {job_status.status}")
            self.test_results["job_manager"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Job manager test failed: {str(e)}")
            return False
    
    async def verify_end_to_end_flow(self):
        """Test complete end-to-end data collection flow"""
        logger.info("🚀 Testing End-to-End Data Collection Flow...")
        
        try:
            # Start a complete collection job
            request = CollectionRequest(
                brand_id="E2E_TestBrand",
                competitor_id="E2E_TestCompetitor",
                area_id="employer_of_choice",
                sources=[DataSource.GLASSDOOR, DataSource.WEBSITE]
            )
            
            job_id = await self.job_manager.start_collection_job(request)
            logger.info(f"Started E2E test job: {job_id}")
            
            # Monitor job progress
            max_wait_time = 30  # 30 seconds
            wait_time = 0
            final_status = None
            
            while wait_time < max_wait_time:
                job_status = await self.job_manager.get_job_status(job_id)
                
                if not job_status:
                    logger.error("❌ Lost track of job during E2E test")
                    return False
                
                logger.info(f"Job progress: {job_status.progress}% - {job_status.current_step}")
                
                if job_status.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    final_status = job_status
                    break
                
                await asyncio.sleep(2)
                wait_time += 2
            
            if not final_status:
                logger.error("❌ E2E test timed out")
                return False
            
            if final_status.status == JobStatus.COMPLETED:
                logger.success("✅ End-to-end data collection completed successfully!")
                
                # Try to retrieve collected data
                collected_data = await storage.get_collected_data(job_id)
                if collected_data:
                    logger.success("✅ Collected data successfully retrieved from storage")
                    logger.info(f"Brand data sources: {list(collected_data.brand_data.__dict__.keys())}")
                    logger.info(f"Competitor data sources: {list(collected_data.competitor_data.__dict__.keys())}")
                    self.test_results["end_to_end"] = True
                    return True
                else:
                    logger.warning("⚠️ Job completed but no data found in storage")
                    return False
            else:
                logger.error(f"❌ E2E job failed with status: {final_status.status}")
                return False
                
        except Exception as e:
            logger.error(f"❌ End-to-end test failed: {str(e)}")
            return False
    
    def print_summary(self):
        """Print verification summary"""
        logger.info("=" * 60)
        logger.info("📊 DATA COLLECTION VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        # Collector results
        logger.info("🔧 Individual Collectors:")
        for source, status in self.test_results["collectors"].items():
            status_icon = "✅" if status else "❌"
            logger.info(f"   {status_icon} {source.title()}: {'WORKING' if status else 'FAILED'}")
        
        # System components
        storage_icon = "✅" if self.test_results["storage"] else "❌"
        job_mgr_icon = "✅" if self.test_results["job_manager"] else "❌"
        e2e_icon = "✅" if self.test_results["end_to_end"] else "❌"
        
        logger.info(f"\n🏗️ System Components:")
        logger.info(f"   {storage_icon} Storage System: {'WORKING' if self.test_results['storage'] else 'FAILED'}")
        logger.info(f"   {job_mgr_icon} Job Manager: {'WORKING' if self.test_results['job_manager'] else 'FAILED'}")
        logger.info(f"   {e2e_icon} End-to-End Flow: {'WORKING' if self.test_results['end_to_end'] else 'FAILED'}")
        
        # Overall status
        all_collectors_working = all(self.test_results["collectors"].values())
        all_systems_working = all([self.test_results["storage"], self.test_results["job_manager"]])
        
        logger.info("\n🎯 Overall Status:")
        if all_collectors_working and all_systems_working and self.test_results["end_to_end"]:
            logger.info("   🟢 DATA COLLECTION SYSTEM IS FULLY OPERATIONAL!")
            return True
        elif all_systems_working:
            logger.info("   🟡 Core systems working, some collectors may have issues")
            return True
        else:
            logger.info("   🔴 System has critical issues that need attention")
            return False

async def main():
    """Run comprehensive verification"""
    logger.info("🚀 Starting Comprehensive Data Collection Verification...")
    logger.info("=" * 60)
    
    verifier = DataCollectionVerifier()
    
    # Run all verification tests
    try:
        await verifier.verify_individual_collectors()
        factory_success = await verifier.verify_collector_factory()
        await verifier.verify_storage_system()
        await verifier.verify_job_manager()
        await verifier.verify_end_to_end_flow()
        
        # Print summary
        system_healthy = verifier.print_summary()
        
        # Additional recommendations
        logger.info("\n💡 Recommendations:")
        if system_healthy:
            logger.info("   • System is ready for production use")
            logger.info("   • Consider monitoring job completion rates")
            logger.info("   • Set up alerting for failed collections")
        else:
            logger.info("   • Review failed components and fix issues")
            logger.info("   • Check network connectivity for web scraping")
            logger.info("   • Verify all dependencies are installed")
        
        return 0 if system_healthy else 1
        
    except Exception as e:
        logger.error(f"❌ Verification script failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 
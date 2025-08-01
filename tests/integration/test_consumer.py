#!/usr/bin/env python3
"""
Integration Test Consumer Script for Brand Intelligence Hub
Tests the complete end-to-end workflow across all three microservices:
- Brand Service (Port 8001)
- Data Collection Service (Port 8002) 
- Analysis Engine Service (Port 8003)
"""

import asyncio
import aiohttp
import json
import uuid
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Simple logging to avoid external dependencies
class Logger:
    @staticmethod
    def info(msg: str):
        print(f"[INFO {datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    @staticmethod
    def error(msg: str):
        print(f"[ERROR {datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    @staticmethod
    def warning(msg: str):
        print(f"[WARN {datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    @staticmethod
    def debug(msg: str):
        print(f"[DEBUG {datetime.now().strftime('%H:%M:%S')}] {msg}")

logger = Logger()


class BrandIntelligenceTestConsumer:
    """Test consumer for Brand Intelligence Hub microservices"""
    
    def __init__(
        self, 
        brand_service_url: str = "http://localhost:8001",
        data_collection_url: str = "http://localhost:8002", 
        analysis_engine_url: str = "http://localhost:8003"
    ):
        self.brand_service_url = brand_service_url
        self.data_collection_url = data_collection_url
        self.analysis_engine_url = analysis_engine_url
        
        # Service endpoints
        self.brand_search_endpoint = f"{brand_service_url}/api/v1/brands/search"
        self.brand_areas_endpoint = f"{brand_service_url}/api/v1/brands"
        self.brand_competitors_endpoint = f"{brand_service_url}/api/v1/brands"
        
        self.collect_endpoint = f"{data_collection_url}/api/v1/collect"
        self.collect_status_endpoint = f"{data_collection_url}/api/v1/collect"
        
        self.analyze_endpoint = f"{analysis_engine_url}/api/v1/analyze"
        self.analyze_status_endpoint = f"{analysis_engine_url}/api/v1/analyze"
    
    async def check_services_health(self) -> Dict[str, bool]:
        """Check if all services are running and healthy"""
        services = {
            "brand-service": f"{self.brand_service_url}/health",
            "data-collection": f"{self.data_collection_url}/health", 
            "analysis-engine": f"{self.analysis_engine_url}/health"
        }
        
        health_status = {}
        
        async with aiohttp.ClientSession() as session:
            for service_name, health_url in services.items():
                try:
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            health_status[service_name] = health_data.get("status") == "healthy"
                            logger.info(f"✅ {service_name}: {health_data.get('status', 'unknown')}")
                        else:
                            health_status[service_name] = False
                            logger.error(f"❌ {service_name}: HTTP {response.status}")
                except Exception as e:
                    health_status[service_name] = False
                    logger.error(f"❌ {service_name}: {str(e)}")
        
        return health_status
    
    async def search_brands(self, query: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Search for brands using the brand service"""
        try:
            search_request = {
                "query": query,
                "limit": limit
            }
            
            logger.info(f"🔍 Searching for brands: '{query}'")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.brand_search_endpoint,
                    json=search_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            brands = result.get("data", [])
                            logger.info(f"✅ Found {len(brands)} brands")
                            return brands
                        else:
                            logger.error(f"Brand search failed: {result}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Brand search API failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error searching brands: {str(e)}")
            return None
    
    async def get_brand_areas(self, brand_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get suggested areas for a brand"""
        try:
            areas_url = f"{self.brand_areas_endpoint}/{brand_id}/areas"
            logger.info(f"📋 Getting areas for brand: {brand_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(areas_url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            areas = result.get("data", [])
                            logger.info(f"✅ Found {len(areas)} areas")
                            return areas
                        else:
                            logger.error(f"Get areas failed: {result}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Get areas API failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting brand areas: {str(e)}")
            return None
    
    async def get_competitors(self, brand_id: str, area_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get competitors for a brand in a specific area"""
        try:
            competitors_url = f"{self.brand_competitors_endpoint}/{brand_id}/competitors"
            params = {"area": area_id}
            
            logger.info(f"🏢 Getting competitors for brand: {brand_id}, area: {area_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(competitors_url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            competitors = result.get("data", [])
                            logger.info(f"✅ Found {len(competitors)} competitors")
                            return competitors
                        else:
                            logger.error(f"Get competitors failed: {result}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Get competitors API failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting competitors: {str(e)}")
            return None
    
    async def start_data_collection(
        self, 
        request_id: str,
        brand_id: str, 
        competitor_id: str, 
        area_id: str, 
        sources: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Start a data collection job"""
        try:
            collect_request = {
                "request_id": request_id,
                "brand_id": brand_id,
                "competitor_id": competitor_id,
                "area_id": area_id,
                "sources": sources
            }
            
            logger.info(f"📊 Starting data collection job")
            logger.debug(f"Request: {collect_request}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.collect_endpoint,
                    json=collect_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            job_id = result.get("job_id")
                            if job_id:
                                logger.info(f"✅ Data collection job started: {job_id}")
                                return {
                                    "job_id": job_id,
                                    "status": result.get("status", "started"),
                                    "estimated_duration": result.get("estimated_duration", 180)
                                }
                            else:
                                logger.error("Data collection API returned success but no job_id")
                                return None
                        else:
                            logger.error(f"Data collection failed: {result}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Data collection API failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error starting data collection: {str(e)}")
            return None
    
    async def monitor_data_collection(self, job_id: str, max_wait: int = 300) -> Optional[Dict[str, Any]]:
        """Monitor data collection job until completion"""
        try:
            logger.info(f"⏳ Monitoring data collection job: {job_id}")
            
            for i in range(max_wait // 2):  # Check every 2 seconds
                await asyncio.sleep(2)
                
                status_url = f"{self.collect_status_endpoint}/{job_id}/status"
                async with aiohttp.ClientSession() as session:
                    async with session.get(status_url) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get("success"):
                                data = result.get('data', {})
                                status = data.get('status', 'unknown')
                                progress = data.get('progress', 0)
                                
                                if i % 15 == 0:  # Print every 30 seconds
                                    logger.info(f"Progress: {progress}% - Status: {status}")
                                
                                if status == "completed":
                                    logger.info(f"✅ Data collection completed")
                                    # Get the collected data
                                    return await self.get_collected_data(job_id)
                                elif status == "failed":
                                    logger.error(f"❌ Data collection failed")
                                    return None
            
            logger.warning(f"⏰ Data collection monitoring timed out after {max_wait} seconds")
            return None
            
        except Exception as e:
            logger.error(f"Error monitoring data collection: {str(e)}")
            return None
    
    async def get_collected_data(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the collected data from a completed job"""
        try:
            data_url = f"{self.collect_status_endpoint}/{job_id}/data"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(data_url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            logger.info("✅ Retrieved collected data")
                            return result.get("data")
                        else:
                            logger.error(f"Get collected data failed: {result}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Get collected data API failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting collected data: {str(e)}")
            return None
    
    async def start_analysis(self, brand_data: Dict, competitor_data: Dict, area_id: str) -> Optional[Dict[str, Any]]:
        """Start analysis job with collected data"""
        try:
            analysis_request = {
                "brand_data": brand_data,
                "competitor_data": competitor_data,
                "area_id": area_id,
                "analysis_type": "comprehensive"
            }
            
            logger.info(f"🧠 Starting analysis job")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.analyze_endpoint,
                    json=analysis_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            analysis_id = result.get("analysis_id")
                            if analysis_id:
                                logger.info(f"✅ Analysis job started: {analysis_id}")
                                return {
                                    "analysis_id": analysis_id,
                                    "status": result.get("status", "processing"),
                                    "estimated_duration": result.get("estimated_duration", 60)
                                }
                            else:
                                logger.error("Analysis API returned success but no analysis_id")
                                return None
                        else:
                            logger.error(f"Analysis failed: {result}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Analysis API failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error starting analysis: {str(e)}")
            return None
    
    async def monitor_analysis(self, analysis_id: str, max_wait: int = 180) -> Optional[Dict[str, Any]]:
        """Monitor analysis job until completion"""
        try:
            logger.info(f"⏳ Monitoring analysis job: {analysis_id}")
            
            for i in range(max_wait // 2):  # Check every 2 seconds
                await asyncio.sleep(2)
                
                status_url = f"{self.analyze_status_endpoint}/{analysis_id}/status"
                async with aiohttp.ClientSession() as session:
                    async with session.get(status_url) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get("success"):
                                data = result.get('data', {})
                                status = data.get('status', 'unknown')
                                progress = data.get('progress', 0)
                                
                                if i % 15 == 0:  # Print every 30 seconds
                                    logger.info(f"Analysis Progress: {progress}% - Status: {status}")
                                
                                if status == "completed":
                                    logger.info(f"✅ Analysis completed")
                                    return await self.get_analysis_results(analysis_id)
                                elif status == "failed":
                                    logger.error(f"❌ Analysis failed")
                                    return None
            
            logger.warning(f"⏰ Analysis monitoring timed out after {max_wait} seconds")
            return None
            
        except Exception as e:
            logger.error(f"Error monitoring analysis: {str(e)}")
            return None
    
    async def get_analysis_results(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get the analysis results"""
        try:
            results_url = f"{self.analyze_status_endpoint}/{analysis_id}/results"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(results_url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            logger.info("✅ Retrieved analysis results")
                            return result.get("data")
                        else:
                            logger.error(f"Get analysis results failed: {result}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Get analysis results API failed: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"Error getting analysis results: {str(e)}")
            return None


async def run_full_integration_test():
    """Run complete end-to-end integration test"""
    logger.info("🚀 Brand Intelligence Hub - Full Integration Test")
    logger.info("=" * 80)
    
    consumer = BrandIntelligenceTestConsumer()
    
    try:
        # Step 1: Health check
        logger.info("Step 1: Checking service health...")
        health_status = await consumer.check_services_health()
        
        unhealthy_services = [name for name, healthy in health_status.items() if not healthy]
        if unhealthy_services:
            logger.error(f"❌ Unhealthy services: {unhealthy_services}")
            logger.error("Please ensure all services are running with: ./start_all_services.sh")
            return 1
        
        logger.info("✅ All services are healthy")
        
        # Step 2: Brand search
        logger.info("\nStep 2: Searching for brands...")
        brands = await consumer.search_brands("Apple", limit=5)
        if not brands:
            logger.error("❌ Brand search failed")
            return 1
        
        selected_brand = brands[0]  # Use first brand
        brand_id = selected_brand.get("id", "apple")
        logger.info(f"✅ Selected brand: {selected_brand.get('name', 'Apple')} (ID: {brand_id})")
        
        # Step 3: Get areas
        logger.info("\nStep 3: Getting brand areas...")
        areas = await consumer.get_brand_areas(brand_id)
        if not areas:
            logger.error("❌ Get areas failed")
            return 1
        
        selected_area = areas[0]  # Use first area
        area_id = selected_area.get("id", "employer_branding")
        logger.info(f"✅ Selected area: {selected_area.get('name', 'Employer Branding')} (ID: {area_id})")
        
        # Step 4: Get competitors
        logger.info("\nStep 4: Getting competitors...")
        competitors = await consumer.get_competitors(brand_id, area_id)
        if not competitors:
            logger.error("❌ Get competitors failed")
            return 1
        
        selected_competitor = competitors[0]  # Use first competitor
        competitor_id = selected_competitor.get("id", "google")
        logger.info(f"✅ Selected competitor: {selected_competitor.get('name', 'Google')} (ID: {competitor_id})")
        
        # Step 5: Start data collection
        logger.info("\nStep 5: Starting data collection...")
        request_id = str(uuid.uuid4())
        collection_job = await consumer.start_data_collection(
            request_id=request_id,
            brand_id=brand_id,
            competitor_id=competitor_id,
            area_id=area_id,
            sources=["news", "social_media", "glassdoor", "website"]
        )
        
        if not collection_job:
            logger.error("❌ Data collection start failed")
            return 1
        
        # Step 6: Monitor data collection
        logger.info("\nStep 6: Monitoring data collection...")
        collected_data = await consumer.monitor_data_collection(collection_job["job_id"])
        
        if not collected_data:
            logger.error("❌ Data collection failed or timed out")
            return 1
        
        # Step 7: Start analysis
        logger.info("\nStep 7: Starting analysis...")
        analysis_job = await consumer.start_analysis(
            brand_data=collected_data.get("brand_data", {}),
            competitor_data=collected_data.get("competitor_data", {}),
            area_id=area_id
        )
        
        if not analysis_job:
            logger.error("❌ Analysis start failed")
            return 1
        
        # Step 8: Monitor analysis
        logger.info("\nStep 8: Monitoring analysis...")
        analysis_results = await consumer.monitor_analysis(analysis_job["analysis_id"])
        
        if not analysis_results:
            logger.error("❌ Analysis failed or timed out")
            return 1
        
        # Step 9: Display results summary
        logger.info("\n" + "="*80)
        logger.info("🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        
        logger.info(f"📊 Test Summary:")
        logger.info(f"  • Request ID: {request_id}")
        logger.info(f"  • Brand: {selected_brand.get('name', 'N/A')} (ID: {brand_id})")
        logger.info(f"  • Competitor: {selected_competitor.get('name', 'N/A')} (ID: {competitor_id})")
        logger.info(f"  • Area: {selected_area.get('name', 'N/A')} (ID: {area_id})")
        logger.info(f"  • Data Collection Job: {collection_job['job_id']}")
        logger.info(f"  • Analysis Job: {analysis_job['analysis_id']}")
        
        # Display key analysis insights
        if analysis_results and "actionable_insights" in analysis_results:
            insights = analysis_results["actionable_insights"][:3]  # Show top 3
            logger.info(f"\n📋 Top Insights:")
            for i, insight in enumerate(insights, 1):
                logger.info(f"  {i}. {insight.get('title', 'N/A')} (Priority: {insight.get('priority', 'N/A')})")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        return 1


async def run_quick_health_test():
    """Run quick health check test"""
    logger.info("🏥 Brand Intelligence Hub - Quick Health Test")
    logger.info("=" * 60)
    
    consumer = BrandIntelligenceTestConsumer()
    
    try:
        health_status = await consumer.check_services_health()
        
        all_healthy = all(health_status.values())
        
        if all_healthy:
            logger.info("✅ All services are healthy and ready!")
            return 0
        else:
            unhealthy = [name for name, healthy in health_status.items() if not healthy]
            logger.error(f"❌ Unhealthy services: {unhealthy}")
            logger.error("Run: ./start_all_services.sh to start all services")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Health test failed: {str(e)}")
        return 1


async def main():
    """Main function with test options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Brand Intelligence Hub Integration Test")
    parser.add_argument(
        "--test-type", 
        choices=["full", "health"], 
        default="health",
        help="Type of test to run (default: health)"
    )
    
    args = parser.parse_args()
    
    logger.info("🧪 Brand Intelligence Hub Integration Tests")
    logger.info("Make sure all services are running: ./start_all_services.sh")
    logger.info("")
    
    if args.test_type == "full":
        return await run_full_integration_test()
    else:
        return await run_quick_health_test()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
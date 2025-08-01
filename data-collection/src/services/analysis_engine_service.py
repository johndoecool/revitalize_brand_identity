#!/usr/bin/env python3
"""
Analysis Engine Integration Service  
Integrates with the existing Analysis Engine Service (analysis-engine/)
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
from loguru import logger


class AnalysisEngineService:
    """Service for integrating with the existing Analysis Engine API"""
    
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url
        self.analyze_endpoint = f"{self.base_url}/api/v1/analyze"
        self.health_endpoint = f"{self.base_url}/health"
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def start_analysis(
        self, 
        collect_id: str, 
        analysis_focus: str, 
        request_id: str
    ) -> Optional[Dict[str, str]]:
        """
        Start analysis using the existing Analysis Engine Service
        
        Uses the existing API from analysis-engine/app/routers/analysis.py:
        POST /api/v1/analyze
        
        Args:
            collect_id: The data collection job ID (maps to collect_id)
            analysis_focus: The analysis focus area (maps to analysis_focus, default "comprehensive")
            request_id: The request ID (passed in headers)
        
        Returns:
            Dict with analysis_id and status if successful, None if failed
        """
        try:
            # Map data collection parameters to analysis engine format
            # Based on analysis-engine/app/models/analysis.py AnalysisRequest
            request_payload = {
                "collect_id": collect_id,                    # Required: Collection ID matching filename
                "analysis_focus": analysis_focus             # Optional: Focus area (defaults to "comprehensive")
            }
            
            # Prepare headers with requestId
            headers = {
                "Content-Type": "application/json",
                "request_id": request_id                     # Pass requestId in header
            }
            
            logger.info(f"🔗 Starting analysis engine for collect_id: {collect_id}")
            logger.info(f"   - Analysis focus: {analysis_focus}")
            logger.info(f"   - Request ID (header): {request_id}")
            logger.debug(f"   - Request payload: {request_payload}")
            logger.debug(f"   - Request headers: {headers}")
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    self.analyze_endpoint,
                    json=request_payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Based on AnalysisResponse model: success, analysis_id, status
                        if result.get("success"):
                            analysis_id = result.get("analysis_id")
                            status = result.get("status", "unknown")
                            
                            if analysis_id:
                                logger.info(f"✅ Analysis started successfully:")
                                logger.info(f"   - Analysis ID: {analysis_id}")  
                                logger.info(f"   - Status: {status}")
                                return {
                                    "analysis_id": analysis_id,
                                    "status": status
                                }
                            else:
                                logger.error(f"❌ Analysis API returned success=true but no analysis_id: {result}")
                                return None
                        else:
                            logger.error(f"❌ Analysis API returned success=false: {result}")
                            return None
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Analysis API request failed: HTTP {response.status}")
                        logger.error(f"   Response: {error_text}")
                        
                        # Try to parse error details if available
                        try:
                            error_data = await response.json() if response.content_type == 'application/json' else {}
                            if isinstance(error_data, dict) and "error" in error_data:
                                error_details = error_data["error"]
                                logger.error(f"   Error code: {error_details.get('code', 'UNKNOWN')}")
                                logger.error(f"   Error message: {error_details.get('message', 'No message')}")
                        except:
                            pass  # Could not parse error details
                        
                        return None
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Network error calling analysis engine: {str(e)}")
            return None
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout calling analysis engine for collect_id: {collect_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error calling analysis engine: {str(e)}")
            return None
    
    async def check_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Check the status of an analysis job using existing API
        
        Uses: GET /api/v1/analyze/{analysis_id}/status
        
        Args:
            analysis_id: The analysis job ID
        
        Returns:
            Status information if successful, None if failed
        """
        try:
            status_endpoint = f"{self.base_url}/api/v1/analyze/{analysis_id}/status"
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(status_endpoint) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Based on AnalysisStatusResponse: success, data, charts, etc.
                        if result.get("success"):
                            logger.info(f"📊 Analysis status for {analysis_id}: {result.get('data', {}).get('status', 'unknown')}")
                            return result
                        else:
                            logger.warning(f"⚠️ Analysis status returned success=false for {analysis_id}")
                            return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to get analysis status: HTTP {response.status}")
                        logger.error(f"   Response: {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Error checking analysis status: {str(e)}")
            return None
    
    async def get_analysis_results(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the results of a completed analysis using existing API
        
        Uses: GET /api/v1/analyze/{analysis_id}/results
        
        Args:
            analysis_id: The analysis job ID
        
        Returns:
            Analysis results if successful, None if failed
        """
        try:
            results_endpoint = f"{self.base_url}/api/v1/analyze/{analysis_id}/results"
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(results_endpoint) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Based on AnalysisResultsResponse: success, data
                        if result.get("success"):
                            logger.info(f"📈 Retrieved analysis results for {analysis_id}")
                            return result
                        else:
                            logger.warning(f"⚠️ Analysis results returned success=false for {analysis_id}")
                            return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to get analysis results: HTTP {response.status}")
                        logger.error(f"   Response: {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Error getting analysis results: {str(e)}")
            return None
    
    async def get_analysis_report(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the PDF report of a completed analysis using existing API
        
        Uses: GET /api/v1/analyze/{analysis_id}/report
        
        Args:
            analysis_id: The analysis job ID
        
        Returns:
            Report data (base64 PDF) if successful, None if failed
        """
        try:
            report_endpoint = f"{self.base_url}/api/v1/analyze/{analysis_id}/report"
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(report_endpoint) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Based on ReportResponse: success, report_base64, filename
                        if result.get("success"):
                            logger.info(f"📄 Retrieved analysis report for {analysis_id}")
                            return result
                        else:
                            logger.warning(f"⚠️ Analysis report returned success=false for {analysis_id}")
                            return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to get analysis report: HTTP {response.status}")
                        logger.error(f"   Response: {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Error getting analysis report: {str(e)}")
            return None
    
    async def health_check(self) -> bool:
        """
        Check if the existing Analysis Engine is healthy and accessible
        
        Uses: GET /health (from analysis-engine/app/main.py)
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(self.health_endpoint) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        # Based on HealthCheckResponse: status, service, llm_status, active_analyses
                        status = result.get("status", "unknown")
                        service = result.get("service", "unknown")
                        llm_status = result.get("llm_status", "unknown")
                        active_analyses = result.get("active_analyses", 0)
                        
                        logger.info(f"💚 Analysis Engine health check passed:")
                        logger.info(f"   - Service: {service}")
                        logger.info(f"   - Status: {status}")
                        logger.info(f"   - LLM Status: {llm_status}")
                        logger.info(f"   - Active analyses: {active_analyses}")
                        
                        return status == "healthy"
                    else:
                        logger.warning(f"🔴 Analysis Engine health check failed: HTTP {response.status}")
                        return False
        
        except Exception as e:
            logger.warning(f"🔴 Analysis Engine health check failed: {str(e)}")
            return False

# Global analysis engine service instance
analysis_engine_service = AnalysisEngineService() 
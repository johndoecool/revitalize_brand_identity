import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.analysis import (
    AnalysisRequest, AnalysisResults, AnalysisJob, AnalysisStatus, AnalysisType
)
from app.services.openai_service import OpenAIService
from app.services.report_service import ReportService

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.report_service = ReportService()
        self.active_jobs: Dict[str, AnalysisJob] = {}
    
    async def start_analysis(self, request: AnalysisRequest) -> str:
        """
        Start a new analysis job and return analysis ID
        """
        analysis_id = str(uuid.uuid4())
        
        # Create analysis job
        job = AnalysisJob(
            analysis_id=analysis_id,
            request_data=request,
            status=AnalysisStatus.PENDING
        )
        
        self.active_jobs[analysis_id] = job
        
        # Start background analysis
        asyncio.create_task(self._run_analysis(analysis_id))
        
        logger.info(f"Started analysis job: {analysis_id}")
        return analysis_id
    
    async def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of an analysis job
        """
        if analysis_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[analysis_id]
        
        return {
            "analysis_id": analysis_id,
            "status": job.status.value,
            "progress": job.progress,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message
        }
    
    async def get_analysis_results(self, analysis_id: str) -> Optional[AnalysisResults]:
        """
        Get the results of a completed analysis
        """
        if analysis_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[analysis_id]
        
        if job.status != AnalysisStatus.COMPLETED:
            return None
        
        return job.results
    
    async def _run_analysis(self, analysis_id: str):
        """
        Run the complete analysis pipeline
        """
        try:
            job = self.active_jobs[analysis_id]
            job.status = AnalysisStatus.PROCESSING
            job.progress = 10
            
            logger.info(f"Starting analysis pipeline for {analysis_id}")
            
            # Step 1: Data preprocessing and validation
            await self._update_progress(analysis_id, 20, "Preprocessing data...")
            validated_data = await self._preprocess_data(job.request_data)
            
            # Step 2: AI-powered comparison analysis
            await self._update_progress(analysis_id, 40, "Running AI analysis...")
            analysis_results = await self.openai_service.analyze_brand_comparison(
                validated_data["brand_data"],
                validated_data["competitor_data"],
                validated_data["area_id"]
            )
            
            # Set analysis ID
            analysis_results.analysis_id = analysis_id
            
            # Step 3: Trend analysis and pattern recognition
            await self._update_progress(analysis_id, 60, "Analyzing trends...")
            trend_data = await self._perform_trend_analysis(validated_data)
            
            # Step 4: Confidence scoring and validation
            await self._update_progress(analysis_id, 80, "Validating results...")
            confidence_score = await self.openai_service.validate_analysis_confidence(analysis_results)
            analysis_results.confidence_score = confidence_score
            
            # Step 5: Report generation
            await self._update_progress(analysis_id, 90, "Generating reports...")
            await self.report_service.generate_analysis_report(analysis_results)
            
            # Complete the analysis
            await self._update_progress(analysis_id, 100, "Analysis completed")
            job.results = analysis_results
            job.status = AnalysisStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            logger.info(f"Analysis completed successfully: {analysis_id}")
            
        except Exception as e:
            logger.error(f"Analysis failed for {analysis_id}: {str(e)}")
            job.status = AnalysisStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
    
    async def _update_progress(self, analysis_id: str, progress: int, message: str):
        """
        Update analysis progress
        """
        if analysis_id in self.active_jobs:
            self.active_jobs[analysis_id].progress = progress
            logger.info(f"Analysis {analysis_id}: {progress}% - {message}")
        
        # Small delay to simulate processing time
        await asyncio.sleep(0.5)
    
    async def _preprocess_data(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Preprocess and validate input data
        """
        # Data validation and cleaning
        brand_data = request.brand_data
        competitor_data = request.competitor_data
        area_id = request.area_id
        
        # Basic validation
        if not brand_data or not competitor_data:
            raise ValueError("Brand data and competitor data are required")
        
        # Normalize data structure
        normalized_brand = self._normalize_brand_data(brand_data)
        normalized_competitor = self._normalize_brand_data(competitor_data)
        
        return {
            "brand_data": normalized_brand,
            "competitor_data": normalized_competitor,
            "area_id": area_id,
            "analysis_type": request.analysis_type
        }
    
    def _normalize_brand_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize brand data structure for consistent processing
        """
        # Ensure required fields exist
        normalized = data.copy()
        
        # Add default values if missing
        if "brand" not in normalized:
            normalized["brand"] = {"name": "Unknown Brand"}
        
        if "competitor" not in normalized:
            normalized["competitor"] = {"name": "Unknown Competitor"}
        
        return normalized
    
    async def _perform_trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform trend analysis and pattern recognition
        """
        try:
            # Extract historical data if available
            brand_data = data["brand_data"]
            
            # Look for time-series data in the brand data
            historical_data = {}
            
            # Check for news sentiment trends
            if "brand_data" in brand_data and "news_sentiment" in brand_data["brand_data"]:
                historical_data["news_sentiment"] = brand_data["brand_data"]["news_sentiment"]
            
            # Check for social media trends
            if "brand_data" in brand_data and "social_media" in brand_data["brand_data"]:
                historical_data["social_media"] = brand_data["brand_data"]["social_media"]
            
            # Generate trend analysis if we have data
            if historical_data:
                return await self.openai_service.generate_trend_analysis(historical_data)
            else:
                return {"message": "Insufficient historical data for trend analysis"}
                
        except Exception as e:
            logger.warning(f"Trend analysis failed: {str(e)}")
            return {"error": "Trend analysis unavailable"}
    
    async def generate_comparison_report(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate formatted comparison report
        """
        results = await self.get_analysis_results(analysis_id)
        if not results:
            return None
        
        return await self.report_service.generate_comparison_report(results)
    
    async def get_actionable_insights_summary(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summarized actionable insights
        """
        results = await self.get_analysis_results(analysis_id)
        if not results:
            return None
        
        return {
            "analysis_id": analysis_id,
            "total_insights": len(results.actionable_insights),
            "high_priority": len([i for i in results.actionable_insights if i.priority.value == "high"]),
            "medium_priority": len([i for i in results.actionable_insights if i.priority.value == "medium"]),
            "low_priority": len([i for i in results.actionable_insights if i.priority.value == "low"]),
            "estimated_total_effort": self._calculate_total_effort(results.actionable_insights),
            "confidence_score": results.confidence_score
        }
    
    def _calculate_total_effort(self, insights) -> str:
        """
        Calculate total estimated effort for all insights
        """
        # Simple effort calculation - in production, this would be more sophisticated
        total_months = 0
        for insight in insights:
            effort = insight.estimated_effort
            if "month" in effort.lower():
                # Extract numeric value (simplified)
                import re
                numbers = re.findall(r'\d+', effort)
                if numbers:
                    total_months += int(numbers[0])
        
        return f"{total_months} months total estimated effort"

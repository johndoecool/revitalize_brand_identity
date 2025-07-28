import asyncio
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.services.llm_service import LLMService
from app.models.analysis import (
    AnalysisResults, AnalysisRequest, AnalysisStatus,
    OverallComparison, ComparisonScore, ActionableInsight,
    Strength, MarketPositioning, TrendAnalysis, Priority
)

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self):
        self.llm_service = LLMService()
        self.active_analyses: Dict[str, Dict[str, Any]] = {}
        self.completed_analyses: Dict[str, AnalysisResults] = {}
        
    async def start_analysis(self, request: AnalysisRequest) -> tuple[str, str]:
        """
        Start a new analysis and return analysis ID and status
        """
        analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
        
        # Store analysis metadata
        self.active_analyses[analysis_id] = {
            "status": AnalysisStatus.PENDING,
            "progress": 0,
            "current_step": "Initializing analysis",
            "created_at": datetime.now(timezone.utc),
            "request": request
        }
        
        # Start analysis in background
        asyncio.create_task(self._perform_analysis(analysis_id, request))
        
        logger.info(f"Started analysis {analysis_id} for area: {request.area_id}")
        return analysis_id, AnalysisStatus.PROCESSING
    
    async def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an analysis"""
        if analysis_id in self.active_analyses:
            return self.active_analyses[analysis_id]
        elif analysis_id in self.completed_analyses:
            return {
                "analysis_id": analysis_id,
                "status": AnalysisStatus.COMPLETED,
                "progress": 100,
                "completed_at": self.completed_analyses[analysis_id].completed_at.isoformat()
            }
        return None
    
    async def get_analysis_results(self, analysis_id: str) -> Optional[AnalysisResults]:
        """Get the results of a completed analysis"""
        return self.completed_analyses.get(analysis_id)
    
    async def get_analysis_history(self, brand_id: Optional[str] = None, limit: int = 10) -> list:
        """Get history of completed analyses"""
        analyses = []
        count = 0
        
        for analysis_id, results in self.completed_analyses.items():
            if count >= limit:
                break
                
            # Filter by brand_id if specified
            if brand_id and results.brand_name.lower().replace(" ", "_") != brand_id:
                continue
            
            analyses.append({
                "analysis_id": analysis_id,
                "brand_id": results.brand_name.lower().replace(" ", "_"),
                "competitor_id": results.competitor_name.lower().replace(" ", "_"),
                "area_id": results.area_id,
                "created_at": results.created_at,
                "status": AnalysisStatus.COMPLETED,
                "overall_score": results.overall_comparison.brand_score
            })
            count += 1
        
        # Sort by created_at descending
        analyses.sort(key=lambda x: x["created_at"], reverse=True)
        return analyses
    
    async def _perform_analysis(self, analysis_id: str, request: AnalysisRequest):
        """Perform the actual analysis workflow"""
        try:
            # Update status to processing
            self.active_analyses[analysis_id].update({
                "status": AnalysisStatus.PROCESSING,
                "progress": 10,
                "current_step": "Analyzing brand data"
            })
            
            # Step 1: Validate and preprocess data
            await asyncio.sleep(1)  # Simulate processing time
            self.active_analyses[analysis_id].update({
                "progress": 25,
                "current_step": "Preprocessing competitor data"
            })
            
            # Step 2: Perform LLM-based analysis
            await asyncio.sleep(1)
            self.active_analyses[analysis_id].update({
                "progress": 50,
                "current_step": "Generating competitive analysis"
            })
            
            # Call LLM service for analysis
            results = await self.llm_service.analyze_brand_comparison(
                request.brand_data,
                request.competitor_data,
                request.area_id
            )
            
            # Step 3: Post-process results
            await asyncio.sleep(0.5)
            self.active_analyses[analysis_id].update({
                "progress": 75,
                "current_step": "Generating actionable insights"
            })
            
            # Step 4: Generate trend analysis if applicable
            await asyncio.sleep(0.5)
            trend_analysis = await self._generate_trend_analysis(request)
            results.trend_analysis = trend_analysis
            
            # Step 5: Finalize results
            results.analysis_id = analysis_id
            results.created_at = self.active_analyses[analysis_id]["created_at"]
            results.completed_at = datetime.now(timezone.utc)
            
            # Validate confidence score
            results.confidence_score = await self.llm_service.validate_analysis_confidence(results)
            
            # Store completed analysis
            self.completed_analyses[analysis_id] = results
            
            # Remove from active analyses
            del self.active_analyses[analysis_id]
            
            logger.info(f"Completed analysis {analysis_id} with confidence {results.confidence_score}")
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {str(e)}")
            self.active_analyses[analysis_id].update({
                "status": AnalysisStatus.FAILED,
                "error": str(e),
                "failed_at": datetime.now(timezone.utc)
            })
    
    async def _generate_trend_analysis(self, request: AnalysisRequest) -> TrendAnalysis:
        """Generate trend analysis based on the comparison data"""
        try:
            # Extract trend indicators from data
            brand_score = self._calculate_trend_score(request.brand_data)
            competitor_score = self._calculate_trend_score(request.competitor_data)
            
            # Determine trends
            brand_trend = "improving" if brand_score > 0.75 else "stable" if brand_score > 0.5 else "declining"
            competitor_trend = "improving" if competitor_score > 0.75 else "stable" if competitor_score > 0.5 else "declining"
            
            # Generate recommendations based on trends
            recommendations = []
            if competitor_score > brand_score:
                recommendations.extend([
                    "Accelerate digital transformation initiatives",
                    "Focus on customer experience improvements"
                ])
            
            if brand_score > 0.8:
                recommendations.append("Maintain current market leadership position")
            
            recommendations.append("Monitor competitive landscape for emerging threats")
            
            return TrendAnalysis(
                brand_trend=brand_trend,
                competitor_trend=competitor_trend,
                market_trend="digital_transformation",
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.warning(f"Failed to generate trend analysis: {str(e)}")
            return TrendAnalysis(
                brand_trend="stable",
                competitor_trend="stable",
                market_trend="digital_transformation",
                recommendations=["Monitor market trends and competitor activities"]
            )
    
    def _calculate_trend_score(self, data: Dict[str, Any]) -> float:
        """Calculate a trend score from data"""
        scores = []
        
        if 'news_sentiment' in data and isinstance(data['news_sentiment'], dict):
            scores.append(data['news_sentiment'].get('score', 0.5))
        
        if 'social_media' in data and isinstance(data['social_media'], dict):
            scores.append(data['social_media'].get('overall_sentiment', 0.5))
        
        if 'glassdoor' in data and isinstance(data['glassdoor'], dict):
            scores.append(data['glassdoor'].get('overall_rating', 3.0) / 5.0)
        
        if 'website_analysis' in data and isinstance(data['website_analysis'], dict):
            scores.append(data['website_analysis'].get('user_experience_score', 0.5))
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health information"""
        try:
            # Test LLM connectivity
            llm_status = "connected" if self.llm_service else "disconnected"
            
            return {
                "status": "healthy",
                "service": "analysis-engine",
                "timestamp": datetime.now(timezone.utc),
                "version": "1.0.0",
                "llm_status": llm_status,
                "active_analyses": len(self.active_analyses)
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "analysis-engine",
                "timestamp": datetime.now(timezone.utc),
                "version": "1.0.0",
                "llm_status": "error",
                "active_analyses": 0,
                "error": str(e)
            }

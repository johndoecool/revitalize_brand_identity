from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class AnalysisType(str, Enum):
    COMPREHENSIVE = "comprehensive"
    QUICK = "quick"
    DETAILED = "detailed"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Request Models
class AnalysisRequest(BaseModel):
    brand_data: Dict[str, Any] = Field(..., description="Brand data from Data Collection Service")
    competitor_data: Dict[str, Any] = Field(..., description="Competitor data from Data Collection Service")
    area_id: str = Field(..., description="Area of analysis (e.g., 'self_service_portal')")
    analysis_type: AnalysisType = Field(default=AnalysisType.COMPREHENSIVE, description="Type of analysis to perform")

# Response Models
class AnalysisInitResponse(BaseModel):
    success: bool
    analysis_id: str
    status: AnalysisStatus
    estimated_duration: int = Field(..., description="Estimated duration in seconds")

class AnalysisStatusResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

class ComparisonScore(BaseModel):
    brand_score: float = Field(..., ge=0.0, le=1.0, description="Brand score (0-1)")
    competitor_score: float = Field(..., ge=0.0, le=1.0, description="Competitor score (0-1)")
    difference: float = Field(..., description="Difference (brand - competitor)")
    insight: str = Field(..., description="AI-generated insight")

class OverallComparison(BaseModel):
    brand_score: float = Field(..., ge=0.0, le=1.0)
    competitor_score: float = Field(..., ge=0.0, le=1.0)
    gap: float = Field(..., description="Gap between scores")
    brand_ranking: str = Field(..., description="Brand ranking (first, second, etc.)")

class ActionableInsight(BaseModel):
    priority: Priority
    category: str
    title: str
    description: str
    estimated_effort: str
    expected_impact: str
    implementation_steps: List[str]

class Strength(BaseModel):
    area: str
    description: str
    recommendation: str

class MarketPositioning(BaseModel):
    brand_position: str
    competitor_position: str
    differentiation_opportunity: str

class AnalysisResults(BaseModel):
    analysis_id: str
    area_id: str
    brand_name: str
    competitor_name: str
    overall_comparison: OverallComparison
    detailed_comparison: Dict[str, ComparisonScore]
    actionable_insights: List[ActionableInsight]
    strengths_to_maintain: List[Strength]
    market_positioning: MarketPositioning
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence in analysis")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnalysisResultsResponse(BaseModel):
    success: bool
    data: AnalysisResults

# Internal Models
class AnalysisJob(BaseModel):
    analysis_id: str
    request_data: AnalysisRequest
    status: AnalysisStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    progress: int = Field(default=0, ge=0, le=100)
    results: Optional[AnalysisResults] = None
    error_message: Optional[str] = None

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ComparisonScore(BaseModel):
    brand_score: float = Field(..., ge=0.0, le=1.0, description="Brand score (0.0-1.0)")
    competitor_score: float = Field(..., ge=0.0, le=1.0, description="Competitor score (0.0-1.0)")
    difference: float = Field(..., description="Score difference (brand - competitor)")
    insight: str = Field(..., description="Insight about this comparison")
    trend: Optional[str] = Field(default="stable", description="Trend direction")

class OverallComparison(BaseModel):
    brand_score: float = Field(..., ge=0.0, le=1.0)
    competitor_score: float = Field(..., ge=0.0, le=1.0)
    gap: float = Field(..., description="Performance gap")
    brand_ranking: str = Field(..., description="Brand ranking position")
    confidence_level: Optional[float] = Field(default=0.85, ge=0.0, le=1.0)

class ActionableInsight(BaseModel):
    priority: Priority
    category: str
    title: str
    description: str
    estimated_effort: str
    expected_impact: str
    roi_estimate: Optional[str] = None
    implementation_steps: List[str]
    success_metrics: Optional[List[str]] = None

class Strength(BaseModel):
    area: str
    description: str
    recommendation: str
    current_score: Optional[float] = None

class MarketPositioning(BaseModel):
    brand_position: str
    competitor_position: str
    differentiation_opportunity: str
    target_audience: Optional[str] = None

class TrendAnalysis(BaseModel):
    brand_trend: str
    competitor_trend: str
    market_trend: str
    recommendations: List[str]

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
    trend_analysis: Optional[TrendAnalysis] = None
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# Request Models
class AnalysisRequest(BaseModel):
    collect_id: str = Field(..., description="Collection ID matching the filename in collected_data")
    analysis_focus: Optional[str] = Field("comprehensive", description="Focus area for analysis")

class ChartData(BaseModel):
    chart_type: str = Field(..., description="Type of chart (bar, line, pie, radar, etc.)")
    title: str = Field(..., description="Chart title")
    description: str = Field(..., description="Chart description")
    data: Dict[str, Any] = Field(..., description="Chart data structure")
    config: Dict[str, Any] = Field(default_factory=dict, description="Chart configuration options")

class CompetitorInsight(BaseModel):
    competitor_name: str
    comparison_score: float = Field(..., ge=0.0, le=1.0)
    strengths: List[str]
    weaknesses: List[str] 
    opportunities: List[str]
    key_differences: List[str]

class ImprovementArea(BaseModel):
    area: str
    current_score: float = Field(..., ge=0.0, le=1.0)
    target_score: float = Field(..., ge=0.0, le=1.0)
    priority: Priority
    description: str
    action_items: List[str]
    expected_outcomes: List[str]
    timeline: str
    resources_needed: List[str]

class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    status: AnalysisStatus
    estimated_duration: Optional[int] = None

class AnalysisStatusResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    charts: Optional[List[ChartData]] = None
    competitor_analysis: Optional[List[CompetitorInsight]] = None
    improvement_areas: Optional[List[ImprovementArea]] = None

class ReportResponse(BaseModel):
    success: bool
    report_base64: str = Field(..., description="Base64 encoded PDF report")
    filename: str = Field(..., description="Suggested filename for the report")
    generated_at: datetime = Field(default_factory=datetime.now)

class AnalysisResultsResponse(BaseModel):
    success: bool
    data: AnalysisResults

class AnalysisHistoryItem(BaseModel):
    analysis_id: str
    brand_id: str
    competitor_id: str
    area_id: str
    created_at: datetime
    status: AnalysisStatus
    overall_score: float

class AnalysisHistoryResponse(BaseModel):
    success: bool
    data: List[AnalysisHistoryItem]

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
    version: str
    llm_status: str
    active_analyses: int

class ErrorDetails(BaseModel):
    field: str
    value: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, Any]
    timestamp: datetime

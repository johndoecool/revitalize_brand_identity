from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class DataSource(str, Enum):
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    GLASSDOOR = "glassdoor"
    WEBSITE = "website"


class JobStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Request Models
class CollectionRequest(BaseModel):
    brand_id: str = Field(..., description="Unique identifier for the brand")
    competitor_id: str = Field(..., description="Unique identifier for the competitor")
    area_id: str = Field(..., description="Area of interest/segment")
    sources: Optional[List[DataSource]] = Field(None, description="List of data sources to collect from (optional - defaults to all sources)")
    request_id: Optional[str] = Field(None, description="Optional request ID for tracking across services")
    
    @validator('sources')
    def validate_sources(cls, v):
        # If sources is None or empty, it will be handled by the API to use all available sources
        if v is not None and not v:
            raise ValueError('If sources are specified, at least one data source must be provided')
        return v


# Response Models
class ErrorDetail(BaseModel):
    field: str
    value: Any


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[ErrorDetail] = None


class BaseApiResponse(BaseModel):
    success: bool
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class CollectionStartResponse(BaseApiResponse):
    job_id: str
    status: JobStatus
    estimated_duration: int  # in seconds


class CollectionErrorResponse(BaseApiResponse):
    error: ErrorResponse


# Status Response Models
class CollectionStatusData(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(..., ge=0, le=100)
    completed_sources: List[DataSource] = []
    remaining_sources: List[DataSource] = []
    estimated_completion: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None


class CollectionStatusResponse(BaseApiResponse):
    data: CollectionStatusData


# Data Models
class NewsArticle(BaseModel):
    title: str
    sentiment: str
    published_date: str
    url: Optional[str] = None
    source: Optional[str] = None


class NewsSentiment(BaseModel):
    score: float = Field(..., ge=-1, le=1)
    articles_count: int
    positive_articles: int
    negative_articles: int
    neutral_articles: int
    recent_articles: List[NewsArticle] = []


class SocialMediaPlatform(BaseModel):
    sentiment: float = Field(..., ge=-1, le=1)
    mentions: int


class SocialMediaData(BaseModel):
    overall_sentiment: float = Field(..., ge=-1, le=1)
    mentions_count: int
    engagement_rate: float = Field(..., ge=0, le=1)
    platforms: Dict[str, SocialMediaPlatform]
    trending_topics: List[str] = []


class GlassdoorData(BaseModel):
    overall_rating: float = Field(..., ge=0, le=5)
    reviews_count: int
    pros: List[str] = []
    cons: List[str] = []
    recommendation_rate: float = Field(..., ge=0, le=1)
    ceo_approval: float = Field(..., ge=0, le=1)


class WebsiteAnalysis(BaseModel):
    user_experience_score: float = Field(..., ge=0, le=1)
    feature_completeness: float = Field(..., ge=0, le=1)
    security_score: float = Field(..., ge=0, le=1)
    accessibility_score: float = Field(..., ge=0, le=1)
    mobile_friendliness: float = Field(..., ge=0, le=1)
    load_time: float = Field(..., gt=0)


class BrandData(BaseModel):
    brand_id: str
    news_sentiment: Optional[NewsSentiment] = None
    social_media: Optional[SocialMediaData] = None
    glassdoor: Optional[GlassdoorData] = None
    website_analysis: Optional[WebsiteAnalysis] = None


class CollectedData(BaseModel):
    brand_data: BrandData
    competitor_data: BrandData


class CollectionDataResponse(BaseApiResponse):
    data: CollectedData


# Data Sources Configuration Models
class DataSourceConfig(BaseModel):
    id: DataSource
    name: str
    description: str
    enabled: bool = True
    rate_limit: int


class DataSourcesConfigResponse(BaseApiResponse):
    data: Dict[str, List[DataSourceConfig]]


# Health Check Model
class HealthCheckResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    active_jobs: int = 0


# Internal Models for Data Storage
class CollectionJob(BaseModel):
    job_id: str
    brand_id: str
    competitor_id: str
    area_id: str
    sources: List[DataSource]
    status: JobStatus
    progress: int = 0
    completed_sources: List[DataSource] = []
    remaining_sources: List[DataSource] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    current_step: Optional[str] = None
    collected_data: Optional[CollectedData] = None
    error_message: Optional[str] = None 
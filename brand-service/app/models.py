from typing import List, Optional
from pydantic import BaseModel, Field


class BrandSearchRequest(BaseModel):
    """Request model for brand search"""
    query: str = Field(..., description="Search query for brands", min_length=1)
    limit: int = Field(default=10, description="Maximum number of results to return", ge=1, le=100)


class Brand(BaseModel):
    """Brand model"""
    id: str = Field(..., description="Unique brand identifier")
    name: str = Field(..., description="Brand name")
    full_name: str = Field(..., description="Full brand name")
    industry: str = Field(..., description="Industry category")
    logo_url: str = Field(..., description="URL to brand logo")
    description: str = Field(..., description="Brand description")
    confidence_score: float = Field(..., description="Search confidence score", ge=0.0, le=1.0)


class BrandSearchResponse(BaseModel):
    """Response model for brand search"""
    success: bool = Field(..., description="Request success status")
    data: List[Brand] = Field(..., description="List of matching brands")
    total_results: int = Field(..., description="Total number of results found")


class Area(BaseModel):
    """Area model for brand analysis"""
    id: str = Field(..., description="Unique area identifier")
    name: str = Field(..., description="Area name")
    description: str = Field(..., description="Area description")
    relevance_score: float = Field(..., description="Relevance score for the brand", ge=0.0, le=1.0)
    metrics: List[str] = Field(..., description="List of relevant metrics")


class AreaSuggestionsResponse(BaseModel):
    """Response model for area suggestions"""
    success: bool = Field(..., description="Request success status")
    data: List[Area] = Field(..., description="List of suggested areas")


class Competitor(BaseModel):
    """Competitor model"""
    id: str = Field(..., description="Unique competitor identifier")
    name: str = Field(..., description="Competitor name")
    logo_url: str = Field(..., description="URL to competitor logo")
    industry: str = Field(..., description="Industry category")
    relevance_score: float = Field(..., description="Relevance score", ge=0.0, le=1.0)
    competition_level: str = Field(..., description="Level of competition (direct, indirect, etc.)")


class CompetitorDiscoveryResponse(BaseModel):
    """Response model for competitor discovery"""
    success: bool = Field(..., description="Request success status")
    data: List[Competitor] = Field(..., description="List of competitors")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Request success status")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

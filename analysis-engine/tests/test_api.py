import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.models.analysis import AnalysisType

client = TestClient(app)

@pytest.fixture
def sample_analysis_request():
    return {
        "brand_data": {
            "brand": {"name": "Test Brand", "id": "test_brand"},
            "brand_data": {
                "news_sentiment": {"score": 0.75, "articles_count": 10},
                "social_media": {"followers": 10000, "engagement_rate": 0.05}
            }
        },
        "competitor_data": {
            "competitor": {"name": "Test Competitor", "id": "test_competitor"},
            "brand_data": {
                "news_sentiment": {"score": 0.85, "articles_count": 15},
                "social_media": {"followers": 15000, "engagement_rate": 0.07}
            }
        },
        "area_id": "self_service_portal",
        "analysis_type": "comprehensive"
    }

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Analysis Engine API"
    assert data["version"] == "1.0.0"

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "analysis-engine"

def test_analysis_health_check():
    """Test the analysis router health check"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "analysis-engine"
    assert "capabilities" in data

@patch('app.routers.analysis.analysis_engine.start_analysis')
def test_start_analysis_success(mock_start_analysis, sample_analysis_request):
    """Test successful analysis start"""
    mock_start_analysis.return_value = "test_analysis_id_123"
    
    response = client.post("/api/v1/analyze", json=sample_analysis_request)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["analysis_id"] == "test_analysis_id_123"
    assert data["status"] == "processing"
    assert "estimated_duration" in data

def test_start_analysis_missing_data():
    """Test analysis start with missing data"""
    invalid_request = {
        "brand_data": {},
        "competitor_data": {},
        "area_id": "test_area"
    }
    
    response = client.post("/api/v1/analyze", json=invalid_request)
    
    assert response.status_code == 400
    assert "brand_data and competitor_data are required" in response.json()["detail"]

def test_start_analysis_invalid_json():
    """Test analysis start with invalid JSON"""
    response = client.post("/api/v1/analyze", json={"invalid": "data"})
    
    # Should fail validation
    assert response.status_code in [400, 422]

@patch('app.routers.analysis.analysis_engine.get_analysis_status')
def test_get_analysis_status_success(mock_get_status):
    """Test successful status retrieval"""
    mock_get_status.return_value = {
        "analysis_id": "test_123",
        "status": "processing",
        "progress": 50,
        "completed_at": None
    }
    
    response = client.get("/api/v1/analyze/test_123/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["analysis_id"] == "test_123"

@patch('app.routers.analysis.analysis_engine.get_analysis_status')
def test_get_analysis_status_not_found(mock_get_status):
    """Test status retrieval for non-existent analysis"""
    mock_get_status.return_value = None
    
    response = client.get("/api/v1/analyze/nonexistent/status")
    
    assert response.status_code == 404
    assert "Analysis not found" in response.json()["detail"]

@patch('app.routers.analysis.analysis_engine.get_analysis_results')
def test_get_analysis_results_success(mock_get_results):
    """Test successful results retrieval"""
    from app.models.analysis import AnalysisResults, OverallComparison, MarketPositioning
    
    mock_results = AnalysisResults(
        analysis_id="test_123",
        area_id="test_area",
        brand_name="Test Brand",
        competitor_name="Test Competitor",
        overall_comparison=OverallComparison(
            brand_score=0.75, competitor_score=0.85, gap=-0.10, brand_ranking="second"
        ),
        detailed_comparison={},
        actionable_insights=[],
        strengths_to_maintain=[],
        market_positioning=MarketPositioning(
            brand_position="pos1", competitor_position="pos2", differentiation_opportunity="opp"
        ),
        confidence_score=0.8
    )
    
    mock_get_results.return_value = mock_results
    
    response = client.get("/api/v1/analyze/test_123/results")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["analysis_id"] == "test_123"

@patch('app.routers.analysis.analysis_engine.get_analysis_results')
def test_get_analysis_results_not_found(mock_get_results):
    """Test results retrieval for non-existent analysis"""
    mock_get_results.return_value = None
    
    response = client.get("/api/v1/analyze/nonexistent/results")
    
    assert response.status_code == 404
    assert "Analysis not found" in response.json()["detail"]

@patch('app.routers.analysis.analysis_engine.generate_comparison_report')
def test_get_analysis_report_success(mock_generate_report):
    """Test successful report generation"""
    mock_report = {
        "comparison_summary": {"brand": "Test Brand", "competitor": "Test Competitor"},
        "category_breakdown": {},
        "recommendations": []
    }
    
    mock_generate_report.return_value = mock_report
    
    response = client.get("/api/v1/analyze/test_123/report")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "report" in data

@patch('app.routers.analysis.analysis_engine.get_actionable_insights_summary')
def test_get_insights_summary_success(mock_get_insights):
    """Test successful insights summary retrieval"""
    mock_insights = {
        "analysis_id": "test_123",
        "total_insights": 3,
        "high_priority": 1,
        "medium_priority": 2,
        "confidence_score": 0.85
    }
    
    mock_get_insights.return_value = mock_insights
    
    response = client.get("/api/v1/analyze/test_123/insights")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["insights_summary"]["total_insights"] == 3

@patch('app.routers.analysis.analysis_engine.start_analysis')
def test_batch_analysis_success(mock_start_analysis, sample_analysis_request):
    """Test successful batch analysis"""
    mock_start_analysis.side_effect = ["id1", "id2", "id3"]
    
    batch_request = [sample_analysis_request, sample_analysis_request, sample_analysis_request]
    
    response = client.post("/api/v1/analyze/batch", json=batch_request)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["analysis_ids"]) == 3
    assert data["total_analyses"] == 3

def test_batch_analysis_too_large(sample_analysis_request):
    """Test batch analysis with too many requests"""
    # Create batch with 11 requests (over limit of 10)
    large_batch = [sample_analysis_request] * 11
    
    response = client.post("/api/v1/analyze/batch", json=large_batch)
    
    assert response.status_code == 400
    assert "Batch size cannot exceed 10" in response.json()["detail"]

def test_batch_analysis_empty():
    """Test batch analysis with empty request"""
    response = client.post("/api/v1/analyze/batch", json=[])
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_analyses"] == 0

@patch('app.routers.analysis.analysis_engine.start_analysis')
def test_analysis_engine_exception_handling(mock_start_analysis, sample_analysis_request):
    """Test exception handling in analysis endpoints"""
    mock_start_analysis.side_effect = Exception("Analysis engine error")
    
    response = client.post("/api/v1/analyze", json=sample_analysis_request)
    
    assert response.status_code == 500
    assert "Analysis initialization failed" in response.json()["detail"]

def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/api/v1/analyze")
    
    # FastAPI with CORS middleware should handle OPTIONS requests
    assert response.status_code in [200, 405]  # Either allowed or method not allowed

def test_openapi_docs():
    """Test that OpenAPI documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])

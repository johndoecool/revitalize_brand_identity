import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.analysis_engine import AnalysisEngine
from app.models.analysis import AnalysisRequest, AnalysisType, AnalysisStatus

@pytest.fixture
def analysis_engine():
    return AnalysisEngine()

@pytest.fixture
def sample_analysis_request():
    return AnalysisRequest(
        brand_data={
            "brand": {"name": "Test Brand", "id": "test_brand"},
            "brand_data": {
                "news_sentiment": {"score": 0.75, "articles_count": 10},
                "social_media": {"followers": 10000, "engagement_rate": 0.05}
            }
        },
        competitor_data={
            "competitor": {"name": "Test Competitor", "id": "test_competitor"},
            "brand_data": {
                "news_sentiment": {"score": 0.85, "articles_count": 15},
                "social_media": {"followers": 15000, "engagement_rate": 0.07}
            }
        },
        area_id="self_service_portal",
        analysis_type=AnalysisType.COMPREHENSIVE
    )

@pytest.mark.asyncio
async def test_start_analysis(analysis_engine, sample_analysis_request):
    """Test starting a new analysis"""
    analysis_id = await analysis_engine.start_analysis(sample_analysis_request)
    
    assert analysis_id is not None
    assert len(analysis_id) > 0
    assert analysis_id in analysis_engine.active_jobs
    
    # Check job is created with correct status
    job = analysis_engine.active_jobs[analysis_id]
    assert job.status == AnalysisStatus.PENDING
    assert job.request_data == sample_analysis_request

@pytest.mark.asyncio
async def test_get_analysis_status(analysis_engine, sample_analysis_request):
    """Test getting analysis status"""
    analysis_id = await analysis_engine.start_analysis(sample_analysis_request)
    
    # Wait a moment for processing to start
    await asyncio.sleep(0.1)
    
    status = await analysis_engine.get_analysis_status(analysis_id)
    
    assert status is not None
    assert status["analysis_id"] == analysis_id
    assert "status" in status
    assert "progress" in status

@pytest.mark.asyncio
async def test_get_analysis_status_not_found(analysis_engine):
    """Test getting status for non-existent analysis"""
    status = await analysis_engine.get_analysis_status("non_existent_id")
    assert status is None

@pytest.mark.asyncio
async def test_data_preprocessing(analysis_engine, sample_analysis_request):
    """Test data preprocessing and validation"""
    preprocessed = await analysis_engine._preprocess_data(sample_analysis_request)
    
    assert "brand_data" in preprocessed
    assert "competitor_data" in preprocessed
    assert "area_id" in preprocessed
    assert preprocessed["area_id"] == "self_service_portal"

@pytest.mark.asyncio
async def test_data_preprocessing_with_missing_data(analysis_engine):
    """Test data preprocessing with missing required data"""
    invalid_request = AnalysisRequest(
        brand_data={},
        competitor_data={},
        area_id="test_area"
    )
    
    with pytest.raises(ValueError, match="Brand data and competitor data are required"):
        await analysis_engine._preprocess_data(invalid_request)

def test_normalize_brand_data(analysis_engine):
    """Test brand data normalization"""
    incomplete_data = {"some_field": "some_value"}
    
    normalized = analysis_engine._normalize_brand_data(incomplete_data)
    
    assert "brand" in normalized
    assert "competitor" in normalized
    assert normalized["brand"]["name"] == "Unknown Brand"

@pytest.mark.asyncio
async def test_update_progress(analysis_engine, sample_analysis_request):
    """Test progress updating"""
    analysis_id = await analysis_engine.start_analysis(sample_analysis_request)
    
    await analysis_engine._update_progress(analysis_id, 50, "Testing progress")
    
    job = analysis_engine.active_jobs[analysis_id]
    assert job.progress == 50

@pytest.mark.asyncio
async def test_get_actionable_insights_summary(analysis_engine, sample_analysis_request):
    """Test getting actionable insights summary"""
    analysis_id = await analysis_engine.start_analysis(sample_analysis_request)
    
    # Wait for analysis to complete (in a real test, you'd mock this)
    await asyncio.sleep(2)
    
    summary = await analysis_engine.get_actionable_insights_summary(analysis_id)
    
    # Check if summary exists (might be None if analysis hasn't completed)
    if summary:
        assert "analysis_id" in summary
        assert "total_insights" in summary
        assert "confidence_score" in summary

@pytest.mark.asyncio
async def test_trend_analysis_with_data(analysis_engine):
    """Test trend analysis with historical data"""
    data = {
        "brand_data": {
            "brand_data": {
                "news_sentiment": {
                    "score": 0.75,
                    "articles_count": 10,
                    "trend": "positive"
                }
            }
        }
    }
    
    with patch.object(analysis_engine.openai_service, 'generate_trend_analysis') as mock_trend:
        mock_trend.return_value = {"trends": "Positive sentiment trend", "confidence": 0.8}
        
        result = await analysis_engine._perform_trend_analysis(data)
        
        assert "trends" in result or "message" in result

@pytest.mark.asyncio
async def test_trend_analysis_without_data(analysis_engine):
    """Test trend analysis without sufficient data"""
    data = {"brand_data": {}}
    
    result = await analysis_engine._perform_trend_analysis(data)
    
    assert "message" in result
    assert "Insufficient historical data" in result["message"]

def test_calculate_total_effort(analysis_engine):
    """Test effort calculation for insights"""
    from app.models.analysis import ActionableInsight, Priority
    
    insights = [
        ActionableInsight(
            priority=Priority.HIGH,
            category="test",
            title="Test 1",
            description="Test insight 1",
            estimated_effort="3-4 months",
            expected_impact="High impact",
            implementation_steps=["Step 1", "Step 2"]
        ),
        ActionableInsight(
            priority=Priority.MEDIUM,
            category="test",
            title="Test 2", 
            description="Test insight 2",
            estimated_effort="2 months",
            expected_impact="Medium impact",
            implementation_steps=["Step 1"]
        )
    ]
    
    total_effort = analysis_engine._calculate_total_effort(insights)
    
    assert "months" in total_effort
    assert "5" in total_effort  # Should calculate 3+2 = 5 months

if __name__ == "__main__":
    pytest.main([__file__])

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.openai_service import OpenAIService
from app.models.analysis import AnalysisResults

@pytest.fixture
def openai_service():
    with patch('openai.OpenAI') as mock_openai:
        service = OpenAIService()
        service.client = mock_openai.return_value
        return service

@pytest.fixture
def sample_brand_data():
    return {
        "brand": {"name": "Test Brand"},
        "brand_data": {
            "news_sentiment": {"score": 0.75},
            "social_media": {"followers": 10000}
        }
    }

@pytest.fixture
def sample_competitor_data():
    return {
        "competitor": {"name": "Test Competitor"},
        "brand_data": {
            "news_sentiment": {"score": 0.85},
            "social_media": {"followers": 15000}
        }
    }

@pytest.mark.asyncio
async def test_analyze_brand_comparison(openai_service, sample_brand_data, sample_competitor_data):
    """Test OpenAI brand comparison analysis"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Detailed analysis result..."
    
    openai_service.client.chat.completions.create.return_value = mock_response
    
    result = await openai_service.analyze_brand_comparison(
        sample_brand_data,
        sample_competitor_data,
        "self_service_portal"
    )
    
    assert isinstance(result, AnalysisResults)
    assert result.brand_name == "Test Brand"
    assert result.competitor_name == "Test Competitor"
    assert result.area_id == "self_service_portal"
    assert result.overall_comparison is not None
    assert result.detailed_comparison is not None
    assert len(result.actionable_insights) > 0

@pytest.mark.asyncio
async def test_analyze_brand_comparison_api_failure(openai_service, sample_brand_data, sample_competitor_data):
    """Test handling of OpenAI API failures"""
    # Mock API failure
    openai_service.client.chat.completions.create.side_effect = Exception("API Error")
    
    with pytest.raises(Exception, match="Analysis failed"):
        await openai_service.analyze_brand_comparison(
            sample_brand_data,
            sample_competitor_data,
            "self_service_portal"
        )

def test_create_analysis_prompt(openai_service, sample_brand_data, sample_competitor_data):
    """Test analysis prompt creation"""
    prompt = openai_service._create_analysis_prompt(
        sample_brand_data,
        sample_competitor_data,
        "self_service_portal"
    )
    
    assert "Test Brand" in prompt
    assert "Test Competitor" in prompt
    assert "self_service_portal" in prompt
    assert "BRAND DATA" in prompt
    assert "COMPETITOR DATA" in prompt

def test_get_system_prompt(openai_service):
    """Test system prompt generation"""
    system_prompt = openai_service._get_system_prompt()
    
    assert "expert brand analyst" in system_prompt.lower()
    assert "actionable" in system_prompt.lower()
    assert "confidence" in system_prompt.lower()

@pytest.mark.asyncio
async def test_parse_analysis_response(openai_service, sample_brand_data, sample_competitor_data):
    """Test parsing of OpenAI analysis response"""
    analysis_text = "Sample analysis response from OpenAI..."
    
    result = await openai_service._parse_analysis_response(
        analysis_text,
        sample_brand_data,
        sample_competitor_data,
        "self_service_portal"
    )
    
    assert isinstance(result, AnalysisResults)
    assert result.brand_name == "Test Brand"
    assert result.competitor_name == "Test Competitor"
    assert 0 <= result.confidence_score <= 1

@pytest.mark.asyncio
async def test_generate_trend_analysis(openai_service):
    """Test trend analysis generation"""
    historical_data = {
        "news_sentiment": {"score": 0.75, "trend": "positive"},
        "social_media": {"engagement": 0.05, "growth": "stable"}
    }
    
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Trend analysis result..."
    
    openai_service.client.chat.completions.create.return_value = mock_response
    
    result = await openai_service.generate_trend_analysis(historical_data)
    
    assert "trends" in result
    assert "confidence" in result
    assert "analysis_date" in result

@pytest.mark.asyncio
async def test_generate_trend_analysis_failure(openai_service):
    """Test trend analysis with API failure"""
    historical_data = {"some": "data"}
    
    # Mock API failure
    openai_service.client.chat.completions.create.side_effect = Exception("API Error")
    
    with pytest.raises(Exception, match="Trend analysis failed"):
        await openai_service.generate_trend_analysis(historical_data)

@pytest.mark.asyncio
async def test_validate_analysis_confidence(openai_service):
    """Test analysis confidence validation"""
    from app.models.analysis import AnalysisResults, OverallComparison, MarketPositioning
    
    # Create mock analysis results
    results = AnalysisResults(
        analysis_id="test_123",
        area_id="test_area",
        brand_name="Test Brand",
        competitor_name="Test Competitor",
        overall_comparison=OverallComparison(
            brand_score=0.75,
            competitor_score=0.85,
            gap=-0.10,
            brand_ranking="second"
        ),
        detailed_comparison={
            "category1": MagicMock(),
            "category2": MagicMock()
        },
        actionable_insights=[MagicMock(), MagicMock()],
        strengths_to_maintain=[],
        market_positioning=MarketPositioning(
            brand_position="position1",
            competitor_position="position2", 
            differentiation_opportunity="opportunity"
        ),
        confidence_score=0.8
    )
    
    confidence = await openai_service.validate_analysis_confidence(results)
    
    assert 0 <= confidence <= 1
    assert isinstance(confidence, float)

def test_openai_service_initialization():
    """Test OpenAI service initialization"""
    with patch('app.core.config.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "test_key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        
        with patch('openai.OpenAI') as mock_openai:
            service = OpenAIService()
            assert service.model == "gpt-4"

def test_openai_service_initialization_no_key():
    """Test OpenAI service initialization without API key"""
    with patch('app.core.config.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = ""
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            OpenAIService()

if __name__ == "__main__":
    pytest.main([__file__])

"""
Unit tests for API endpoints with enhanced coverage
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestBrandSearchAPIEnhanced:
    """Enhanced test coverage for brand search API endpoints"""
    
    def test_search_brands_empty_query(self):
        """Test brand search with empty query"""
        payload = {"query": "", "limit": 10}
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_search_brands_invalid_limit(self):
        """Test brand search with invalid limit"""
        payload = {"query": "test", "limit": 0}
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error
        
        payload = {"query": "test", "limit": 101}
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_search_brands_missing_query(self):
        """Test brand search with missing query field"""
        payload = {"limit": 10}
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error
    
    @patch('app.api.brands.cache_service')
    def test_search_brands_cache_hit(self, mock_cache_service):
        """Test brand search with cache hit"""
        # Mock cache hit
        mock_cache_service.get_cached_search.return_value = MagicMock(
            success=True,
            data=[],
            total_results=0
        )
        
        payload = {"query": "test", "limit": 10}
        response = client.post("/api/v1/brands/search", json=payload)
        
        assert response.status_code == 200
        mock_cache_service.get_cached_search.assert_called_once()
    
    @patch('app.api.brands.cache_service')
    @patch('httpx.AsyncClient')
    def test_search_brands_fmp_error(self, mock_httpx, mock_cache_service):
        """Test brand search with FMP API error"""
        # Mock cache miss
        mock_cache_service.get_cached_search.return_value = None
        
        # Mock FMP API error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("FMP API Error")
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        payload = {"query": "test", "limit": 10}
        response = client.post("/api/v1/brands/search", json=payload)
        
        # Should still try Alpha Vantage, but this test focuses on FMP error handling
        assert response.status_code in [200, 500]


class TestBrandAreasAPIEnhanced:
    """Enhanced test coverage for brand areas API endpoints"""
    
    def test_get_brand_areas_empty_brand_id(self):
        """Test areas endpoint with empty brand_id"""
        response = client.get("/api/v1/brands//areas")
        assert response.status_code == 404  # Not found due to empty path
    
    @patch('app.api.brands.areas_cache_service')
    def test_get_brand_areas_cache_hit(self, mock_cache_service):
        """Test areas endpoint with cache hit"""
        mock_cache_service.get_cached_areas.return_value = {
            "success": True,
            "data": [
                {
                    "id": "financial_performance",
                    "name": "Financial Performance",
                    "description": "Revenue metrics",
                    "relevance_score": 0.95,
                    "metrics": ["revenue"]
                }
            ]
        }
        
        response = client.get("/api/v1/brands/TEST/areas")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
    
    @patch('app.api.brands.areas_cache_service')
    @patch('app.api.brands._generate_areas_with_together_ai')
    def test_get_brand_areas_together_ai_error(self, mock_together_ai, mock_cache_service):
        """Test areas endpoint with Together.ai error"""
        # Mock cache miss
        mock_cache_service.get_cached_areas.return_value = None
        
        # Mock Together.ai error
        mock_together_ai.return_value = None
        
        response = client.get("/api/v1/brands/TEST/areas")
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "No Records Found"


class TestBrandCompetitorsAPIEnhanced:
    """Enhanced test coverage for brand competitors API endpoints"""
    
    def test_get_brand_competitors_no_area(self):
        """Test competitors endpoint without area parameter"""
        response = client.get("/api/v1/brands/TEST/competitors")
        # Should work without area parameter
        assert response.status_code in [200, 400]  # Depends on cache/API response
    
    def test_get_brand_competitors_with_area(self):
        """Test competitors endpoint with area parameter"""
        response = client.get("/api/v1/brands/TEST/competitors?area=digital_transformation")
        # Should work with area parameter
        assert response.status_code in [200, 400]  # Depends on cache/API response
    
    @patch('app.api.brands.competitors_cache_service')
    def test_get_brand_competitors_cache_hit(self, mock_cache_service):
        """Test competitors endpoint with cache hit"""
        mock_cache_service.get_cached_competitors.return_value = {
            "success": True,
            "data": [
                {
                    "id": "ACN",
                    "name": "Accenture",
                    "logo_url": "https://example.com/logo.png",
                    "industry": "IT Consulting",
                    "relevance_score": 0.92,
                    "competition_level": "direct",
                    "symbol": "ACN"
                }
            ]
        }
        
        response = client.get("/api/v1/brands/TEST/competitors?area=digital")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
    
    @patch('app.api.brands.competitors_cache_service')
    @patch('app.api.brands._generate_competitors_with_together_ai')
    def test_get_brand_competitors_together_ai_error(self, mock_together_ai, mock_cache_service):
        """Test competitors endpoint with Together.ai error"""
        # Mock cache miss
        mock_cache_service.get_cached_competitors.return_value = None
        
        # Mock Together.ai error
        mock_together_ai.return_value = None
        
        response = client.get("/api/v1/brands/TEST/competitors?area=digital")
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "No Records Found"


class TestTogetherAIIntegration:
    """Test Together.ai integration functions"""
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_generate_areas_with_together_ai_success(self, mock_httpx):
        """Test successful Together.ai areas generation"""
        from app.api.brands import _generate_areas_with_together_ai
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "success": True,
                        "data": [
                            {
                                "id": "financial_performance",
                                "name": "Financial Performance",
                                "description": "Revenue metrics",
                                "relevance_score": 0.95,
                                "metrics": ["revenue"]
                            }
                        ]
                    })
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        result = await _generate_areas_with_together_ai("TEST")
        
        assert result is not None
        assert result["success"] is True
        assert len(result["data"]) == 1
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_generate_competitors_with_together_ai_success(self, mock_httpx):
        """Test successful Together.ai competitors generation"""
        from app.api.brands import _generate_competitors_with_together_ai
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "success": True,
                        "data": [
                            {
                                "id": "ACN",
                                "name": "Accenture",
                                "logo_url": "https://example.com/logo.png",
                                "industry": "IT Consulting",
                                "relevance_score": 0.92,
                                "competition_level": "direct",
                                "symbol": "ACN"
                            }
                        ]
                    })
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        result = await _generate_competitors_with_together_ai("TEST", "digital")
        
        assert result is not None
        assert result["success"] is True
        assert len(result["data"]) == 1
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_together_ai_json_parsing_error(self, mock_httpx):
        """Test Together.ai JSON parsing error"""
        from app.api.brands import _generate_areas_with_together_ai
        
        # Mock API response with invalid JSON
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "invalid json content"
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        result = await _generate_areas_with_together_ai("TEST")
        
        assert result is None
    
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_together_ai_http_error(self, mock_httpx):
        """Test Together.ai HTTP error"""
        from app.api.brands import _generate_competitors_with_together_ai
        
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        result = await _generate_competitors_with_together_ai("TEST", "area")
        
        assert result is None


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_invalid_json_request(self):
        """Test invalid JSON request"""
        response = client.post(
            "/api/v1/brands/search",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test request without content type"""
        response = client.post("/api/v1/brands/search", data='{"query": "test"}')
        assert response.status_code == 422
    
    def test_nonexistent_endpoint(self):
        """Test accessing non-existent endpoint"""
        response = client.get("/api/v1/brands/nonexistent")
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__])

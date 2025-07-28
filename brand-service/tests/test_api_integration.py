import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestUpdatedBrandSearchAPI:
    """Test the updated brand search API with Alpha Vantage integration"""
    
    @patch('app.alphavantage_service.AlphaVantageService.search_brands')
    def test_search_brands_cache_miss_with_results(self, mock_search_brands):
        """Test brand search with cache miss but Alpha Vantage returns results"""
        # Mock Alpha Vantage service to return brands
        from app.models import Brand
        mock_brands = [
            Brand(
                id="AAPL",
                name="Apple Inc.",
                full_name="Apple Inc.",
                industry="Technology",
                logo_url="https://img.logo.dev/ticker/AAPL?token=pk_TVi0kXveSqGUNVDsvdijOA",
                description="Apple Inc. designs and manufactures consumer electronics.",
                confidence_score=0.95
            )
        ]
        
        # Convert to async mock
        async def async_return():
            return mock_brands
        
        mock_search_brands.return_value = asyncio.create_task(async_return())
        
        payload = {
            "query": "Apple Inc",
            "limit": 10
        }
        response = client.post("/api/v1/brands/search", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "Apple Inc"
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == "AAPL"
        assert data["data"][0]["name"] == "Apple Inc."
        assert data["total_results"] == 1
    
    @patch('app.alphavantage_service.AlphaVantageService.search_brands')
    def test_search_brands_no_results_found(self, mock_search_brands):
        """Test brand search when no results are found"""
        # Mock Alpha Vantage service to return empty list
        async def async_return():
            return []
        
        mock_search_brands.return_value = asyncio.create_task(async_return())
        
        payload = {
            "query": "NonexistentCompany",
            "limit": 10
        }
        response = client.post("/api/v1/brands/search", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "No Records Found"
    
    def test_search_brands_cache_hit(self):
        """Test brand search with cache hit"""
        # First, let's add something to cache by searching
        # This test assumes the cache file already has some data
        
        payload = {
            "query": "Oriental Bank",  # This should be in cache from previous tests
            "limit": 10
        }
        response = client.post("/api/v1/brands/search", json=payload)
        
        # Should get a response (either from cache or fresh)
        assert response.status_code in [200, 400]  # 400 if no results from Alpha Vantage
        
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "query" in data
            assert "data" in data
            assert "total_results" in data
    
    def test_search_brands_invalid_request(self):
        """Test brand search with invalid request data"""
        payload = {
            "query": "",  # Empty query should fail validation
            "limit": 10
        }
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_search_brands_limit_validation(self):
        """Test brand search with invalid limit"""
        payload = {
            "query": "Apple",
            "limit": 0  # Invalid limit
        }
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error
    
    @patch('app.alphavantage_service.AlphaVantageService.search_brands')
    def test_search_brands_api_error(self, mock_search_brands):
        """Test brand search when Alpha Vantage API fails"""
        # Mock Alpha Vantage service to raise an exception
        async def async_error():
            raise Exception("API Error")
        
        mock_search_brands.return_value = asyncio.create_task(async_error())
        
        payload = {
            "query": "Test Company",
            "limit": 10
        }
        response = client.post("/api/v1/brands/search", json=payload)
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Internal server error"


class TestCacheIntegration:
    """Test cache integration with the new API"""
    
    def test_cache_stats_endpoint(self):
        """Test cache statistics endpoint"""
        response = client.get("/api/v1/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_entries" in data["data"]
        assert "total_brands" in data["data"]
    
    def test_cache_search_endpoint(self):
        """Test cache search endpoint"""
        response = client.get("/api/v1/cache/search?q=Bank")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_results" in data


if __name__ == '__main__':
    pytest.main([__file__, "-v"])

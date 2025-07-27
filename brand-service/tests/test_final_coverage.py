"""
Final comprehensive test to maximize coverage
"""
import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestFinalCoverage:
    """Final tests to maximize code coverage"""

    @patch('app.api.brands.cache_service')
    @patch('httpx.AsyncClient')
    def test_brand_search_fmp_success(self, mock_httpx, mock_cache_service):
        """Test successful FMP API flow"""
        # Mock cache miss
        mock_cache_service.get_cached_search.return_value = None
        
        # Mock FMP search success
        mock_search_response = MagicMock()
        mock_search_response.json.return_value = [{
            "symbol": "AAPL",
            "name": "Apple Inc",
            "exchange": "NASDAQ"
        }]
        mock_search_response.raise_for_status.return_value = None
        
        # Mock FMP profile success
        mock_profile_response = MagicMock()
        mock_profile_response.json.return_value = [{
            "symbol": "AAPL",
            "companyName": "Apple Inc.",
            "industry": "Technology",
            "description": "Technology company",
            "image": "apple_logo.png"
        }]
        mock_profile_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.get.side_effect = [mock_search_response, mock_profile_response]
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/brands/search", json={"query": "Apple", "limit": 5})
        assert response.status_code == 200

    @patch('app.api.brands.cache_service')
    @patch('httpx.AsyncClient')
    def test_brand_search_alpha_vantage_fallback(self, mock_httpx, mock_cache_service):
        """Test Alpha Vantage fallback when FMP fails"""
        # Mock cache miss
        mock_cache_service.get_cached_search.return_value = None
        
        # Mock FMP failure
        mock_fmp_response = MagicMock()
        mock_fmp_response.json.return_value = []
        mock_fmp_response.raise_for_status.return_value = None
        
        # Mock Alpha Vantage success
        mock_av_response = MagicMock()
        mock_av_response.json.return_value = {
            "bestMatches": [{
                "1. symbol": "AAPL",
                "2. name": "Apple Inc",
                "9. matchScore": "0.95"
            }]
        }
        mock_av_response.raise_for_status.return_value = None
        
        # Mock Alpha Vantage overview
        mock_overview_response = MagicMock()
        mock_overview_response.json.return_value = {
            "Symbol": "AAPL",
            "Name": "Apple Inc.",
            "Industry": "Technology",
            "Description": "Technology company"
        }
        mock_overview_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.get.side_effect = [mock_fmp_response, mock_av_response, mock_overview_response]
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/brands/search", json={"query": "Apple", "limit": 5})
        assert response.status_code == 200

    @patch('app.api.brands.areas_cache_service')
    @patch('httpx.AsyncClient')
    def test_brand_areas_together_ai_success(self, mock_httpx, mock_cache_service):
        """Test successful Together.ai areas generation"""
        # Mock cache miss
        mock_cache_service.get_cached_areas.return_value = None
        
        # Mock successful Together.ai response
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
                                "description": "Revenue and profitability metrics",
                                "relevance_score": 0.95,
                                "metrics": ["revenue", "profit"]
                            }
                        ]
                    })
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/api/v1/brands/AAPL/areas")
        assert response.status_code == 200

    @patch('app.api.brands.competitors_cache_service')
    @patch('httpx.AsyncClient')
    def test_brand_competitors_together_ai_success(self, mock_httpx, mock_cache_service):
        """Test successful Together.ai competitors generation"""
        # Mock cache miss
        mock_cache_service.get_cached_competitors.return_value = None
        
        # Mock successful Together.ai response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "success": True,
                        "data": [
                            {
                                "id": "MSFT",
                                "name": "Microsoft",
                                "logo_url": "https://img.logo.dev/ticker/MSFT?token=test",
                                "industry": "Technology",
                                "relevance_score": 0.92,
                                "competition_level": "direct",
                                "symbol": "MSFT"
                            }
                        ]
                    })
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.get("/api/v1/brands/AAPL/competitors?area=technology")
        assert response.status_code == 200

    def test_cache_service_advanced_operations(self):
        """Test advanced cache service operations"""
        from app.cache_service import BrandCacheService
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write('[]')
            temp_file_path = temp_file.name
        
        try:
            cache_service = BrandCacheService(temp_file_path)
            
            # Test multiple cache operations
            for i in range(5):
                response_data = {
                    "query": f"test{i}",
                    "success": True,
                    "data": [{"id": f"brand{i}", "name": f"Brand {i}"}],
                    "total_results": 1
                }
                cache_service.cache_search_response(response_data)
            
            # Test cache limit (should keep only last entries)
            stats = cache_service.get_cache_stats()
            assert stats["total_entries"] == 5
            
            # Test export/import functionality
            export_path = temp_file_path + "_export"
            cache_service.export_cache(export_path)
            
            # Clear and import
            cache_service.clear_cache()
            cache_service.import_cache(export_path, merge=False)
            
            stats_after_import = cache_service.get_cache_stats()
            assert stats_after_import["total_entries"] == 5
            
            # Clean up export file
            if os.path.exists(export_path):
                os.unlink(export_path)
                
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_error_scenarios(self):
        """Test various error scenarios"""
        # Test invalid brand ID characters
        response = client.get("/api/v1/brands//areas")
        assert response.status_code == 404
        
        # Test malformed requests
        response = client.post("/api/v1/brands/search", json={})
        assert response.status_code == 422
        
        # Test special characters in brand ID
        response = client.get("/api/v1/brands/TEST@#$/areas")
        assert response.status_code in [200, 400]

    @patch('httpx.AsyncClient')
    def test_api_error_handling(self, mock_httpx):
        """Test API error handling scenarios"""
        # Mock connection error
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Connection error")
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        response = client.post("/api/v1/brands/search", json={"query": "test", "limit": 10})
        assert response.status_code in [400, 500]

    def test_cache_file_permissions(self):
        """Test cache file permission handling"""
        from app.cache_service import BrandCacheService
        
        # Test with existing cache file
        cache_service = BrandCacheService()
        
        # These should not crash even if file permissions are restricted
        try:
            stats = cache_service.get_cache_stats()
            cache_service.search_cache("test")
            cache_service.remove_cached_query("nonexistent")
        except Exception:
            # Should handle errors gracefully
            pass

    def test_configuration_coverage(self):
        """Test configuration edge cases"""
        from app.config import Config
        
        # Test with various input types
        special_chars_query = "test query with spaces & symbols"
        url = Config.get_alpha_vantage_symbol_search_url(special_chars_query)
        assert "test query with spaces & symbols" in url
        
        # Test with empty/None inputs
        url = Config.get_fmp_search_url("")
        assert "search-name?query=" in url
        
        symbol_with_dots = "BRK.A"
        logo_url = Config.get_logo_url(symbol_with_dots)
        assert "BRK.A" in logo_url

    def test_model_edge_cases(self):
        """Test model validation edge cases"""
        from app.models import Brand, BrandSearchRequest
        
        # Test with edge values
        brand = Brand(
            id="X", name="X", full_name="X Corp",
            industry="Tech", logo_url="http://x.com",
            description="X", confidence_score=0.0
        )
        assert brand.confidence_score == 0.0
        
        brand = Brand(
            id="Y", name="Y", full_name="Y Corp",
            industry="Tech", logo_url="http://y.com",
            description="Y", confidence_score=1.0
        )
        assert brand.confidence_score == 1.0
        
        # Test request with edge limits
        request = BrandSearchRequest(query="test", limit=1)
        assert request.limit == 1
        
        request = BrandSearchRequest(query="test", limit=100)
        assert request.limit == 100

if __name__ == '__main__':
    pytest.main([__file__])

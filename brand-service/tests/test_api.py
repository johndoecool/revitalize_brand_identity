import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Brand Service API is running"
        assert data["version"] == "1.0.0"
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "brand-service"
        assert data["version"] == "1.0.0"


class TestBrandSearchAPI:
    """Test brand search API endpoints"""
    
    def test_search_brands_success(self):
        """Test successful brand search"""
        payload = {
            "query": "Oriental Bank",
            "limit": 10
        }
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_results" in data
        assert isinstance(data["data"], list)
        assert data["total_results"] >= 0
        
        # Check if Oriental Bank is in the results
        if data["data"]:
            found_oriental = any(
                brand["name"] == "Oriental Bank" 
                for brand in data["data"]
            )
            assert found_oriental
    
    def test_search_brands_with_limit(self):
        """Test brand search with custom limit"""
        payload = {
            "query": "Bank",
            "limit": 2
        }
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) <= 2
    
    def test_search_brands_empty_query(self):
        """Test brand search with empty query"""
        payload = {
            "query": "",
            "limit": 10
        }
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_search_brands_invalid_limit(self):
        """Test brand search with invalid limit"""
        payload = {
            "query": "Bank",
            "limit": 0
        }
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_search_brands_missing_query(self):
        """Test brand search with missing query field"""
        payload = {
            "limit": 10
        }
        response = client.post("/api/v1/brands/search", json=payload)
        assert response.status_code == 422  # Validation error


class TestAreaSuggestionsAPI:
    """Test area suggestions API endpoints"""
    
    def test_get_brand_areas_success(self):
        """Test successful area suggestions retrieval"""
        brand_id = "oriental_bank_pr"
        response = client.get(f"/api/v1/brands/{brand_id}/areas")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
        
        # Check area structure
        if data["data"]:
            area = data["data"][0]
            required_fields = ["id", "name", "description", "relevance_score", "metrics"]
            for field in required_fields:
                assert field in area
            
            assert isinstance(area["metrics"], list)
            assert 0.0 <= area["relevance_score"] <= 1.0
    
    def test_get_brand_areas_different_brand(self):
        """Test area suggestions for different brand"""
        brand_id = "banco_popular_pr"
        response = client.get(f"/api/v1/brands/{brand_id}/areas")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)


class TestCompetitorDiscoveryAPI:
    """Test competitor discovery API endpoints"""
    
    def test_get_brand_competitors_success(self):
        """Test successful competitor discovery"""
        brand_id = "oriental_bank_pr"
        response = client.get(f"/api/v1/brands/{brand_id}/competitors")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
        
        # Check competitor structure
        if data["data"]:
            competitor = data["data"][0]
            required_fields = ["id", "name", "logo_url", "industry", "relevance_score", "competition_level"]
            for field in required_fields:
                assert field in competitor
            
            assert 0.0 <= competitor["relevance_score"] <= 1.0
            assert competitor["id"] != brand_id  # Should not include the brand itself
    
    def test_get_brand_competitors_with_area(self):
        """Test competitor discovery with area filter"""
        brand_id = "oriental_bank_pr"
        area_id = "self_service_portal"
        response = client.get(f"/api/v1/brands/{brand_id}/competitors?area={area_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
    
    def test_get_brand_competitors_nonexistent_brand(self):
        """Test competitor discovery for non-existent brand"""
        brand_id = "nonexistent_brand"
        response = client.get(f"/api/v1/brands/{brand_id}/competitors")
        assert response.status_code == 200  # Mock service returns data regardless
        
        data = response.json()
        assert data["success"] is True


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self):
        """Test OpenAPI schema availability"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Brand Service API"
    
    def test_swagger_ui(self):
        """Test Swagger UI availability"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_ui(self):
        """Test ReDoc UI availability"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

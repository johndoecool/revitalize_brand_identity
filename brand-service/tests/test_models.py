"""
Unit tests for models
"""
import unittest
from pydantic import ValidationError
from app.models import (
    Brand, BrandSearchRequest, BrandSearchResponse,
    AreaSuggestionsResponse, CompetitorDiscoveryResponse,
    ErrorResponse, Area, Competitor
)


class TestBrandModel(unittest.TestCase):
    """Test Brand model"""
    
    def test_brand_creation_valid(self):
        """Test creating a valid Brand instance"""
        brand = Brand(
            id="TEST",
            name="Test Company",
            full_name="Test Company Inc.",
            industry="Technology",
            logo_url="https://example.com/logo.png",
            description="A test company",
            confidence_score=0.95
        )
        
        self.assertEqual(brand.id, "TEST")
        self.assertEqual(brand.name, "Test Company")
        self.assertEqual(brand.confidence_score, 0.95)
    
    def test_brand_confidence_score_validation(self):
        """Test Brand confidence score validation"""
        # Valid confidence scores
        valid_scores = [0.0, 0.5, 1.0]
        for score in valid_scores:
            brand = Brand(
                id="TEST", name="Test", full_name="Test",
                industry="Tech", logo_url="url", description="desc",
                confidence_score=score
            )
            self.assertEqual(brand.confidence_score, score)
        
        # Invalid confidence scores should raise ValidationError
        invalid_scores = [-0.1, 1.1, 2.0]
        for score in invalid_scores:
            with self.assertRaises(ValidationError):
                Brand(
                    id="TEST", name="Test", full_name="Test",
                    industry="Tech", logo_url="url", description="desc",
                    confidence_score=score
                )
    
    def test_brand_required_fields(self):
        """Test Brand required fields"""
        # Missing required field should raise ValidationError
        with self.assertRaises(ValidationError):
            Brand(name="Test", full_name="Test")


class TestBrandSearchRequest(unittest.TestCase):
    """Test BrandSearchRequest model"""
    
    def test_valid_search_request(self):
        """Test creating a valid search request"""
        request = BrandSearchRequest(query="test", limit=5)
        self.assertEqual(request.query, "test")
        self.assertEqual(request.limit, 5)
    
    def test_default_limit(self):
        """Test default limit value"""
        request = BrandSearchRequest(query="test")
        self.assertEqual(request.limit, 10)
    
    def test_limit_validation(self):
        """Test limit validation"""
        # Valid limits
        for limit in [1, 50, 100]:
            request = BrandSearchRequest(query="test", limit=limit)
            self.assertEqual(request.limit, limit)
        
        # Invalid limits
        for limit in [0, 101, -1]:
            with self.assertRaises(ValidationError):
                BrandSearchRequest(query="test", limit=limit)
    
    def test_empty_query_validation(self):
        """Test empty query validation"""
        with self.assertRaises(ValidationError):
            BrandSearchRequest(query="", limit=10)


class TestBrandSearchResponse(unittest.TestCase):
    """Test BrandSearchResponse model"""
    
    def test_valid_search_response(self):
        """Test creating a valid search response"""
        brand = Brand(
            id="TEST", name="Test", full_name="Test Company",
            industry="Tech", logo_url="url", description="desc",
            confidence_score=0.8
        )
        
        response = BrandSearchResponse(
            success=True,
            data=[brand],
            total_results=1
        )
        
        self.assertTrue(response.success)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.total_results, 1)


class TestAreaModel(unittest.TestCase):
    """Test Area model"""
    
    def test_area_creation_valid(self):
        """Test creating a valid Area instance"""
        area = Area(
            id="financial_performance",
            name="Financial Performance",
            description="Revenue and profit metrics",
            relevance_score=0.95,
            metrics=["revenue", "profit"]
        )
        
        self.assertEqual(area.id, "financial_performance")
        self.assertEqual(area.name, "Financial Performance")
        self.assertEqual(area.relevance_score, 0.95)
        self.assertEqual(len(area.metrics), 2)
    
    def test_area_relevance_score_validation(self):
        """Test Area relevance score validation"""
        # Valid scores
        for score in [0.0, 0.5, 1.0]:
            area = Area(
                id="test", name="Test", description="Test",
                relevance_score=score, metrics=[]
            )
            self.assertEqual(area.relevance_score, score)
        
        # Invalid scores
        for score in [-0.1, 1.1]:
            with self.assertRaises(ValidationError):
                Area(
                    id="test", name="Test", description="Test",
                    relevance_score=score, metrics=[]
                )


class TestCompetitorModel(unittest.TestCase):
    """Test Competitor model"""
    
    def test_competitor_creation_valid(self):
        """Test creating a valid Competitor instance"""
        competitor = Competitor(
            id="ACN",
            name="Accenture",
            logo_url="https://example.com/logo.png",
            industry="IT Consulting",
            relevance_score=0.92,
            competition_level="direct"
        )
        
        self.assertEqual(competitor.id, "ACN")
        self.assertEqual(competitor.name, "Accenture")
        self.assertEqual(competitor.relevance_score, 0.92)
        self.assertEqual(competitor.competition_level, "direct")
    
    def test_competitor_relevance_score_validation(self):
        """Test Competitor relevance score validation"""
        # Valid scores
        for score in [0.0, 0.5, 1.0]:
            competitor = Competitor(
                id="TEST", name="Test", logo_url="url",
                industry="Tech", relevance_score=score,
                competition_level="direct"
            )
            self.assertEqual(competitor.relevance_score, score)
        
        # Invalid scores
        for score in [-0.1, 1.1]:
            with self.assertRaises(ValidationError):
                Competitor(
                    id="TEST", name="Test", logo_url="url",
                    industry="Tech", relevance_score=score,
                    competition_level="direct"
                )


class TestAreaSuggestionsResponse(unittest.TestCase):
    """Test AreaSuggestionsResponse model"""
    
    def test_valid_area_response(self):
        """Test creating a valid area suggestions response"""
        area = Area(
            id="test", name="Test", description="Test area",
            relevance_score=0.8, metrics=["metric1"]
        )
        
        response = AreaSuggestionsResponse(
            success=True,
            data=[area]
        )
        
        self.assertTrue(response.success)
        self.assertEqual(len(response.data), 1)


class TestCompetitorDiscoveryResponse(unittest.TestCase):
    """Test CompetitorDiscoveryResponse model"""
    
    def test_valid_competitor_response(self):
        """Test creating a valid competitor discovery response"""
        competitor = Competitor(
            id="TEST", name="Test", logo_url="url",
            industry="Tech", relevance_score=0.8,
            competition_level="direct"
        )
        
        response = CompetitorDiscoveryResponse(
            success=True,
            data=[competitor]
        )
        
        self.assertTrue(response.success)
        self.assertEqual(len(response.data), 1)


class TestErrorResponse(unittest.TestCase):
    """Test ErrorResponse model"""
    
    def test_valid_error_response(self):
        """Test creating a valid error response"""
        error = ErrorResponse(
            success=False,
            error="Not Found",
            details="Resource not found"
        )
        
        self.assertFalse(error.success)
        self.assertEqual(error.error, "Not Found")
        self.assertEqual(error.details, "Resource not found")


if __name__ == '__main__':
    unittest.main()

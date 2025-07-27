import unittest
from app.services import BrandService, MockDataService
from app.models import Brand, Area, Competitor


class TestMockDataService(unittest.TestCase):
    """Test mock data service"""
    
    def setUp(self):
        self.mock_service = MockDataService()
    
    def test_get_mock_brands(self):
        """Test getting mock brands"""
        brands = self.mock_service.get_mock_brands()
        
        self.assertIsInstance(brands, list)
        self.assertGreater(len(brands), 0)
        
        # Check brand structure
        for brand in brands:
            self.assertIsInstance(brand, Brand)
            self.assertTrue(hasattr(brand, 'id'))
            self.assertTrue(hasattr(brand, 'name'))
            self.assertTrue(hasattr(brand, 'confidence_score'))
            self.assertGreaterEqual(brand.confidence_score, 0.0)
            self.assertLessEqual(brand.confidence_score, 1.0)
    
    def test_get_mock_areas(self):
        """Test getting mock areas"""
        areas = self.mock_service.get_mock_areas()
        
        self.assertIsInstance(areas, list)
        self.assertGreater(len(areas), 0)
        
        # Check area structure
        for area in areas:
            self.assertIsInstance(area, Area)
            self.assertTrue(hasattr(area, 'id'))
            self.assertTrue(hasattr(area, 'name'))
            self.assertTrue(hasattr(area, 'relevance_score'))
            self.assertGreaterEqual(area.relevance_score, 0.0)
            self.assertLessEqual(area.relevance_score, 1.0)
    
    def test_get_mock_competitors(self):
        """Test getting mock competitors"""
        competitors = self.mock_service.get_mock_competitors()
        
        self.assertIsInstance(competitors, list)
        self.assertGreater(len(competitors), 0)
        
        # Check competitor structure
        for competitor in competitors:
            self.assertIsInstance(competitor, Competitor)
            self.assertTrue(hasattr(competitor, 'id'))
            self.assertTrue(hasattr(competitor, 'name'))
            self.assertTrue(hasattr(competitor, 'relevance_score'))
            self.assertGreaterEqual(competitor.relevance_score, 0.0)
            self.assertLessEqual(competitor.relevance_score, 1.0)


class TestBrandService(unittest.TestCase):
    """Test brand service functionality"""
    
    def setUp(self):
        self.brand_service = BrandService()
    
    def test_search_brands_exact_match(self):
        """Test brand search with exact match"""
        results = self.brand_service.search_brands("Oriental Bank")
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Should find Oriental Bank
        oriental_found = any(brand.name == "Oriental Bank" for brand in results)
        self.assertTrue(oriental_found)
    
    def test_search_brands_partial_match(self):
        """Test brand search with partial match"""
        results = self.brand_service.search_brands("Bank")
        
        self.assertIsInstance(results, list)
        # Should find multiple banks
        self.assertGreater(len(results), 0)
    
    def test_search_brands_case_insensitive(self):
        """Test brand search is case insensitive"""
        results_lower = self.brand_service.search_brands("oriental bank")
        results_upper = self.brand_service.search_brands("ORIENTAL BANK")
        
        self.assertEqual(len(results_lower), len(results_upper))
        if results_lower:
            self.assertEqual(results_lower[0].id, results_upper[0].id)
    
    def test_search_brands_with_limit(self):
        """Test brand search respects limit"""
        results = self.brand_service.search_brands("Bank", limit=2)
        
        self.assertLessEqual(len(results), 2)
    
    def test_search_brands_no_match(self):
        """Test brand search with no matches"""
        results = self.brand_service.search_brands("NonexistentBrand")
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)
    
    def test_search_brands_sorted_by_confidence(self):
        """Test brand search results are sorted by confidence score"""
        results = self.brand_service.search_brands("Bank")
        
        if len(results) > 1:
            for i in range(len(results) - 1):
                self.assertGreaterEqual(
                    results[i].confidence_score, 
                    results[i + 1].confidence_score
                )
    
    def test_get_brand_areas(self):
        """Test getting brand areas"""
        areas = self.brand_service.get_brand_areas("oriental_bank_pr")
        
        self.assertIsInstance(areas, list)
        self.assertGreater(len(areas), 0)
        
        # Check areas are sorted by relevance score
        if len(areas) > 1:
            for i in range(len(areas) - 1):
                self.assertGreaterEqual(
                    areas[i].relevance_score, 
                    areas[i + 1].relevance_score
                )
    
    def test_get_brand_competitors(self):
        """Test getting brand competitors"""
        competitors = self.brand_service.get_brand_competitors("oriental_bank_pr")
        
        self.assertIsInstance(competitors, list)
        self.assertGreater(len(competitors), 0)
        
        # Check that the brand itself is not in the competitors list
        brand_ids = [comp.id for comp in competitors]
        self.assertNotIn("oriental_bank_pr", brand_ids)
        
        # Check competitors are sorted by relevance score
        if len(competitors) > 1:
            for i in range(len(competitors) - 1):
                self.assertGreaterEqual(
                    competitors[i].relevance_score, 
                    competitors[i + 1].relevance_score
                )
    
    def test_get_brand_competitors_with_area(self):
        """Test getting brand competitors with area filter"""
        competitors = self.brand_service.get_brand_competitors(
            "oriental_bank_pr", 
            "self_service_portal"
        )
        
        self.assertIsInstance(competitors, list)
        # For mock implementation, should return the same results regardless of area
        self.assertGreater(len(competitors), 0)


if __name__ == '__main__':
    unittest.main()

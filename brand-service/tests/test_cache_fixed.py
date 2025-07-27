import unittest
import os
import tempfile
import json
from app.cache_service import BrandCacheService
from app.models import Brand, BrandSearchResponse


class TestBrandCacheService(unittest.TestCase):
    """Test brand cache service functionality"""
    
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.write('[]')
        self.temp_file.close()
        
        self.cache_service = BrandCacheService(self.temp_file.name)
        
        # Create sample brand data
        self.sample_brands = [
            Brand(
                id="test_bank_1",
                name="Test Bank",
                full_name="Test Bank Corporation",
                industry="Banking",
                logo_url="https://example.com/test_bank_logo.png",
                description="A test bank for testing purposes",
                confidence_score=0.95
            ),
            Brand(
                id="test_bank_2",
                name="Another Test Bank",
                full_name="Another Test Bank Ltd",
                industry="Banking",
                logo_url="https://example.com/another_test_bank_logo.png",
                description="Another test bank",
                confidence_score=0.88
            )
        ]
        
        # Create sample response data
        self.sample_response_data = {
            "query": "Test Bank",
            "success": True,
            "data": [brand.__dict__ for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
    
    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_cache_search_response(self):
        """Test caching search response"""
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Verify the cache file was updated
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 1)
        self.assertEqual(cache_data[0]["query"], "Test Bank")
        self.assertEqual(len(cache_data[0]["data"]), 2)
        self.assertEqual(cache_data[0]["total_results"], 2)
    
    def test_get_cached_search(self):
        """Test retrieving cached search results"""
        # Cache some data first
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Retrieve cached data
        result = self.cache_service.get_cached_search("Test Bank")
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["total_results"], 2)
    
    def test_get_cached_search_with_limit(self):
        """Test retrieving cached search results with limit"""
        # Cache some data first
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Retrieve cached data with limit
        result = self.cache_service.get_cached_search("Test Bank", limit=1)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["total_results"], 1)
    
    def test_get_cached_search_not_found(self):
        """Test retrieving non-existent cached search"""
        result = self.cache_service.get_cached_search("Non-existent query")
        self.assertIsNone(result)
    
    def test_case_insensitive_query(self):
        """Test case insensitive query matching"""
        # Cache with original case
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Search with different case
        result = self.cache_service.get_cached_search("test bank")
        self.assertIsNotNone(result)
        
        result = self.cache_service.get_cached_search("TEST BANK")
        self.assertIsNotNone(result)
    
    def test_clear_cache(self):
        """Test clearing cache"""
        # Add some data
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Clear cache
        self.cache_service.clear_cache()
        
        # Verify cache is empty
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 0)
    
    def test_remove_cached_query(self):
        """Test removing specific cached query"""
        # Cache some data
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Remove the cached query
        result = self.cache_service.remove_cached_query("Test Bank")
        self.assertTrue(result)
        
        # Verify it's removed
        cached_result = self.cache_service.get_cached_search("Test Bank")
        self.assertIsNone(cached_result)
        
        # Try to remove non-existent query
        result = self.cache_service.remove_cached_query("Non-existent")
        self.assertFalse(result)
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        # Initially empty
        stats = self.cache_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 0)
        self.assertEqual(stats["total_brands"], 0)
        
        # Add some data
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Check stats
        stats = self.cache_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 1)
        self.assertEqual(stats["total_brands"], 2)
        self.assertIn("Test Bank", stats["queries"])
    
    def test_search_cache(self):
        """Test searching through cache"""
        # Cache some data
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Search for bank
        results = self.cache_service.search_cache("bank")
        self.assertGreater(len(results), 0)
        
        # Check that we get both query and brand matches
        query_matches = [r for r in results if r["type"] == "query"]
        brand_matches = [r for r in results if r["type"] == "brand"]
        
        self.assertGreater(len(query_matches), 0)
        self.assertGreater(len(brand_matches), 0)
    
    def test_update_existing_query(self):
        """Test updating existing cached query"""
        # Cache initial data
        self.cache_service.cache_search_response(self.sample_response_data)
        
        # Update with new data
        updated_response = {
            "query": "Test Bank",
            "success": True,
            "data": [self.sample_brands[0].__dict__],  # Only one brand this time
            "total_results": 1
        }
        self.cache_service.cache_search_response(updated_response)
        
        # Verify updated data
        result = self.cache_service.get_cached_search("Test Bank")
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["total_results"], 1)
        
        # Verify only one cache entry exists
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        self.assertEqual(len(cache_data), 1)


if __name__ == '__main__':
    unittest.main()

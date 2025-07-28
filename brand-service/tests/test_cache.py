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
    
    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_cache_search_response(self):
        """Test caching search response"""
        query = "Test Bank"
        
        # Create response data in the expected format
        response_data = {
            "query": query,
            "success": True,
            "data": [brand.__dict__ for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        
        self.cache_service.cache_search_response(response_data)
        
        # Verify the cache file was updated
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 1)
        self.assertEqual(cache_data[0]["query"], query)
        self.assertEqual(len(cache_data[0]["data"]), 2)
        self.assertEqual(cache_data[0]["total_results"], 2)
    
    def test_get_cached_search(self):
        """Test retrieving cached search results"""
        query = "Test Bank"
        
        # Cache some data first
        response_data = {
            "query": query,
            "success": True,
            "data": [brand.__dict__ for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        self.cache_service.cache_search_response(response_data)
        
        # Retrieve cached data
        result = self.cache_service.get_cached_search(query)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BrandSearchResponse)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.total_results, 2)
        self.assertEqual(result.data[0].name, "Test Bank")
    
    def test_get_cached_search_with_limit(self):
        """Test retrieving cached search results with limit"""
        query = "Test Bank"
        
        # Cache some data first
        response_data = {
            "query": query,
            "success": True,
            "data": [brand.__dict__ for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        self.cache_service.cache_search_response(response_data)
        
        # Retrieve cached data with limit
        result = self.cache_service.get_cached_search(query, limit=1)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.total_results, 1)
    
    def test_get_cached_search_not_found(self):
        """Test retrieving non-existent cached search"""
        result = self.cache_service.get_cached_search("Non-existent query")
        self.assertIsNone(result)
    
    def test_case_insensitive_query(self):
        """Test case insensitive query matching"""
        query = "Test Bank"
        
        # Cache with original case
        self.cache_service.cache_search_results(query, self.sample_brands, len(self.sample_brands))
        
        # Retrieve with different case
        result = self.cache_service.get_cached_search("test bank")
        self.assertIsNotNone(result)
        
        result = self.cache_service.get_cached_search("TEST BANK")
        self.assertIsNotNone(result)
    
    def test_remove_cached_query(self):
        """Test removing cached query"""
        query = "Test Bank"
        
        # Cache some data
        self.cache_service.cache_search_results(query, self.sample_brands, len(self.sample_brands))
        
        # Verify it exists
        result = self.cache_service.get_cached_search(query)
        self.assertIsNotNone(result)
        
        # Remove it
        removed = self.cache_service.remove_cached_query(query)
        self.assertTrue(removed)
        
        # Verify it's gone
        result = self.cache_service.get_cached_search(query)
        self.assertIsNone(result)
        
        # Try to remove again
        removed = self.cache_service.remove_cached_query(query)
        self.assertFalse(removed)
    
    def test_clear_cache(self):
        """Test clearing all cache"""
        # Cache some data
        self.cache_service.cache_search_results("Query 1", self.sample_brands, len(self.sample_brands))
        self.cache_service.cache_search_results("Query 2", self.sample_brands, len(self.sample_brands))
        
        # Verify cache has data
        stats = self.cache_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 2)
        
        # Clear cache
        self.cache_service.clear_cache()
        
        # Verify cache is empty
        stats = self.cache_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 0)
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        # Initially empty
        stats = self.cache_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 0)
        self.assertEqual(stats["total_brands"], 0)
        self.assertIsInstance(stats["queries"], list)
        self.assertGreaterEqual(stats["cache_file_size_bytes"], 0)
        
        # Add some data
        self.cache_service.cache_search_results("Test Query", self.sample_brands, len(self.sample_brands))
        
        stats = self.cache_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 1)
        self.assertEqual(stats["total_brands"], 2)
        self.assertIn("Test Query", stats["queries"])
    
    def test_search_cache(self):
        """Test searching through cache"""
        # Cache some data
        self.cache_service.cache_search_results("Banking Query", self.sample_brands, len(self.sample_brands))
        
        # Search for query
        results = self.cache_service.search_cache("Banking")
        self.assertGreater(len(results), 0)
        
        # Should find query match
        query_matches = [r for r in results if r["type"] == "query"]
        self.assertGreater(len(query_matches), 0)
        
        # Search for brand
        results = self.cache_service.search_cache("Test Bank")
        brand_matches = [r for r in results if r["type"] == "brand"]
        self.assertGreater(len(brand_matches), 0)
    
    def test_update_existing_query(self):
        """Test updating cache for existing query"""
        query = "Test Query"
        
        # Cache initial data
        self.cache_service.cache_search_results(query, [self.sample_brands[0]], 1)
        
        # Verify initial cache
        result = self.cache_service.get_cached_search(query)
        self.assertEqual(len(result.data), 1)
        
        # Update with new data
        self.cache_service.cache_search_results(query, self.sample_brands, len(self.sample_brands))
        
        # Verify updated cache
        result = self.cache_service.get_cached_search(query)
        self.assertEqual(len(result.data), 2)
        
        # Verify only one entry exists for this query
        stats = self.cache_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 1)


if __name__ == '__main__':
    unittest.main()

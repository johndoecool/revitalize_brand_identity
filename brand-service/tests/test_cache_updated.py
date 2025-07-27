"""
Fixed tests for BrandCacheService with correct method names and return types
"""
import unittest
import tempfile
import os
from app.cache_service import BrandCacheService
from app.models import Brand, BrandSearchResponse


class TestBrandCacheServiceFixed(unittest.TestCase):
    """Updated tests for BrandCacheService with correct method names"""
    
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        self.cache_service = BrandCacheService(self.temp_file.name)
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
    
    def test_cache_search_response_and_retrieval(self):
        """Test caching and retrieving search response"""
        query = "Test Bank"
        
        # Create response data in correct format
        response_data = {
            "query": query,
            "success": True,
            "data": [brand.model_dump() for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        
        # Cache the response
        self.cache_service.cache_search_response(response_data)
        
        # Retrieve from cache
        result = self.cache_service.get_cached_search(query, limit=10)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["query"], query)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 2)
    
    def test_get_cached_search_not_found(self):
        """Test retrieving non-existent search from cache"""
        result = self.cache_service.get_cached_search("Non-existent Query", limit=10)
        self.assertIsNone(result)
    
    def test_get_cached_search_with_limit(self):
        """Test retrieving cached search with limit"""
        query = "Test Bank"
        
        response_data = {
            "query": query,
            "success": True,
            "data": [brand.model_dump() for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        self.cache_service.cache_search_response(response_data)
        
        # Test with limit
        result = self.cache_service.get_cached_search(query, limit=1)
        self.assertIsNotNone(result)
        self.assertEqual(len(result["data"]), 1)
    
    def test_case_insensitive_query(self):
        """Test case insensitive query matching"""
        query = "Test Bank"
        
        response_data = {
            "query": query,
            "success": True,
            "data": [brand.model_dump() for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        self.cache_service.cache_search_response(response_data)
        
        # Retrieve with different case
        result = self.cache_service.get_cached_search("test bank", limit=10)
        self.assertIsNotNone(result)
        
        result = self.cache_service.get_cached_search("TEST BANK", limit=10)
        self.assertIsNotNone(result)
    
    def test_remove_cached_query(self):
        """Test removing cached query"""
        query = "Test Query"
        
        response_data = {
            "query": query,
            "success": True,
            "data": [brand.model_dump() for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        self.cache_service.cache_search_response(response_data)
        
        # Verify it exists
        result = self.cache_service.get_cached_search(query, limit=10)
        self.assertIsNotNone(result)
        
        # Remove it
        self.cache_service.remove_cached_query(query)
        
        # Verify it's gone
        result = self.cache_service.get_cached_search(query, limit=10)
        self.assertIsNone(result)
    
    def test_clear_cache(self):
        """Test clearing entire cache"""
        # Add multiple queries
        queries = ["Query 1", "Query 2"]
        for query in queries:
            response_data = {
                "query": query,
                "success": True,
                "data": [brand.model_dump() for brand in self.sample_brands],
                "total_results": len(self.sample_brands)
            }
            self.cache_service.cache_search_response(response_data)
        
        # Verify they exist
        for query in queries:
            result = self.cache_service.get_cached_search(query, limit=10)
            self.assertIsNotNone(result)
        
        # Clear cache
        self.cache_service.clear_cache()
        
        # Verify they're gone
        for query in queries:
            result = self.cache_service.get_cached_search(query, limit=10)
            self.assertIsNone(result)
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        # Initially empty
        stats = self.cache_service.get_cache_stats()
        self.assertIn("total_entries", stats)
        self.assertEqual(stats["total_entries"], 0)
        
        # Add a query
        response_data = {
            "query": "Test Query",
            "success": True,
            "data": [brand.model_dump() for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        self.cache_service.cache_search_response(response_data)
        
        # Check stats again
        stats = self.cache_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 1)
    
    def test_search_cache(self):
        """Test searching through cache entries"""
        # Add multiple queries with different brands
        query1 = "Banking Query"
        response_data1 = {
            "query": query1,
            "success": True,
            "data": [brand.model_dump() for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        self.cache_service.cache_search_response(response_data1)
        
        query2 = "Tech Query"
        tech_brand = Brand(
            id="tech_1",
            name="Tech Corp",
            full_name="Technology Corporation",
            industry="Technology",
            logo_url="https://example.com/tech_logo.png",
            description="A tech company",
            confidence_score=0.92
        )
        response_data2 = {
            "query": query2,
            "success": True,
            "data": [tech_brand.model_dump()],
            "total_results": 1
        }
        self.cache_service.cache_search_response(response_data2)
        
        # Search cache
        search_results = self.cache_service.search_cache("Banking")
        self.assertIsInstance(search_results, list)
        # Should find entries containing "Banking"
        found_banking = any("banking" in str(result).lower() for result in search_results)
        self.assertTrue(found_banking)
    
    def test_update_existing_query(self):
        """Test updating an existing cached query"""
        query = "Update Test"
        
        # Initial cache
        initial_data = {
            "query": query,
            "success": True,
            "data": [self.sample_brands[0].model_dump()],
            "total_results": 1
        }
        self.cache_service.cache_search_response(initial_data)
        
        result = self.cache_service.get_cached_search(query, limit=10)
        self.assertEqual(len(result["data"]), 1)
        
        # Update with more data
        updated_data = {
            "query": query,
            "success": True,
            "data": [brand.model_dump() for brand in self.sample_brands],
            "total_results": len(self.sample_brands)
        }
        self.cache_service.cache_search_response(updated_data)
        
        # Verify update
        result = self.cache_service.get_cached_search(query, limit=10)
        self.assertEqual(len(result["data"]), 2)


if __name__ == '__main__':
    unittest.main()

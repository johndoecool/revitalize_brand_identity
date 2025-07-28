"""
Unit tests for areas cache service
"""
import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from app.areas_cache_service import BrandAreasCacheService


class TestBrandAreasCacheService(unittest.TestCase):
    """Test brand areas cache service functionality"""
    
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.write('[]')
        self.temp_file.close()
        
        # Mock the cache file path
        with patch.object(BrandAreasCacheService, '_BrandAreasCacheService__init__') as mock_init:
            mock_init.return_value = None
            self.cache_service = BrandAreasCacheService()
            self.cache_service.cache_file_path = self.temp_file.name
    
    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_ensure_cache_file_exists(self):
        """Test cache file creation"""
        # Delete the file first
        os.unlink(self.temp_file.name)
        
        # Call the method
        self.cache_service._ensure_cache_file_exists()
        
        # Check file exists and is valid JSON
        self.assertTrue(os.path.exists(self.temp_file.name))
        with open(self.temp_file.name, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, [])
    
    def test_get_cached_areas_found(self):
        """Test retrieving cached areas when found"""
        # Setup test data
        test_data = [{
            "brand_id": "TEST",
            "cached_at": "2025-07-27T12:00:00",
            "success": True,
            "data": [
                {
                    "id": "financial_performance",
                    "name": "Financial Performance",
                    "description": "Revenue and profitability metrics",
                    "relevance_score": 0.95
                }
            ]
        }]
        
        with open(self.temp_file.name, 'w') as f:
            json.dump(test_data, f)
        
        # Test retrieval
        result = self.cache_service.get_cached_areas("TEST")
        
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["id"], "financial_performance")
    
    def test_get_cached_areas_not_found(self):
        """Test retrieving cached areas when not found"""
        result = self.cache_service.get_cached_areas("NONEXISTENT")
        self.assertIsNone(result)
    
    def test_get_cached_areas_file_not_found(self):
        """Test retrieving cached areas when cache file doesn't exist"""
        os.unlink(self.temp_file.name)
        result = self.cache_service.get_cached_areas("TEST")
        self.assertIsNone(result)
    
    def test_get_cached_areas_invalid_json(self):
        """Test retrieving cached areas with invalid JSON"""
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json")
        
        result = self.cache_service.get_cached_areas("TEST")
        self.assertIsNone(result)
    
    def test_cache_areas_response(self):
        """Test caching areas response"""
        areas_data = {
            "success": True,
            "data": [
                {
                    "id": "market_position",
                    "name": "Market Position",
                    "description": "Competitive landscape analysis",
                    "relevance_score": 0.88
                }
            ]
        }
        
        self.cache_service.cache_areas_response("TEST_BRAND", areas_data)
        
        # Verify the cache
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 1)
        self.assertEqual(cache_data[0]["brand_id"], "TEST_BRAND")
        self.assertTrue(cache_data[0]["success"])
        self.assertEqual(len(cache_data[0]["data"]), 1)
    
    def test_cache_areas_response_replaces_existing(self):
        """Test that caching replaces existing entry for same brand"""
        # Cache initial data
        initial_data = {
            "success": True,
            "data": [{"id": "old_area", "name": "Old Area"}]
        }
        self.cache_service.cache_areas_response("TEST", initial_data)
        
        # Cache new data for same brand
        new_data = {
            "success": True,
            "data": [{"id": "new_area", "name": "New Area"}]
        }
        self.cache_service.cache_areas_response("TEST", new_data)
        
        # Verify only new data exists
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 1)
        self.assertEqual(cache_data[0]["data"][0]["id"], "new_area")
    
    def test_cache_areas_response_limits_entries(self):
        """Test that cache limits the number of entries"""
        # Create more than 100 entries
        for i in range(105):
            data = {"success": True, "data": [{"id": f"area_{i}"}]}
            self.cache_service.cache_areas_response(f"BRAND_{i}", data)
        
        # Verify only last 100 entries are kept
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 100)
        # Check that the latest entries are kept
        self.assertEqual(cache_data[-1]["brand_id"], "BRAND_104")
    
    def test_cache_areas_response_error_handling(self):
        """Test error handling during caching"""
        # Make file read-only to cause an error
        os.chmod(self.temp_file.name, 0o444)
        
        try:
            areas_data = {"success": True, "data": []}
            # This should not raise an exception, just log the error
            self.cache_service.cache_areas_response("TEST", areas_data)
        finally:
            # Restore write permissions for cleanup
            os.chmod(self.temp_file.name, 0o644)


if __name__ == '__main__':
    unittest.main()

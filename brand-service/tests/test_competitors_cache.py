"""
Unit tests for competitors cache service
"""
import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from app.competitors_cache_service import BrandCompetitorsCacheService


class TestBrandCompetitorsCacheService(unittest.TestCase):
    """Test brand competitors cache service functionality"""
    
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.write('[]')
        self.temp_file.close()
        
        # Mock the cache file path
        with patch.object(BrandCompetitorsCacheService, '_BrandCompetitorsCacheService__init__') as mock_init:
            mock_init.return_value = None
            self.cache_service = BrandCompetitorsCacheService()
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
    
    def test_get_cached_competitors_found(self):
        """Test retrieving cached competitors when found"""
        # Setup test data
        test_data = [{
            "brand_id": "TEST",
            "area_id": "digital_transformation",
            "cached_at": "2025-07-27T12:00:00",
            "success": True,
            "data": [
                {
                    "id": "ACN",
                    "name": "Accenture",
                    "logo_url": "https://img.logo.dev/ticker/ACN?token=test",
                    "industry": "IT Consulting",
                    "relevance_score": 0.92,
                    "competition_level": "direct",
                    "symbol": "ACN"
                }
            ]
        }]
        
        with open(self.temp_file.name, 'w') as f:
            json.dump(test_data, f)
        
        # Test retrieval
        result = self.cache_service.get_cached_competitors("TEST", "digital_transformation")
        
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["symbol"], "ACN")
    
    def test_get_cached_competitors_with_none_area(self):
        """Test retrieving cached competitors with None area_id"""
        # Setup test data
        test_data = [{
            "brand_id": "TEST",
            "area_id": None,
            "cached_at": "2025-07-27T12:00:00",
            "success": True,
            "data": []
        }]
        
        with open(self.temp_file.name, 'w') as f:
            json.dump(test_data, f)
        
        # Test retrieval
        result = self.cache_service.get_cached_competitors("TEST", None)
        
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
    
    def test_get_cached_competitors_not_found(self):
        """Test retrieving cached competitors when not found"""
        result = self.cache_service.get_cached_competitors("NONEXISTENT", "area")
        self.assertIsNone(result)
    
    def test_get_cached_competitors_file_not_found(self):
        """Test retrieving cached competitors when cache file doesn't exist"""
        os.unlink(self.temp_file.name)
        result = self.cache_service.get_cached_competitors("TEST", "area")
        self.assertIsNone(result)
    
    def test_get_cached_competitors_invalid_json(self):
        """Test retrieving cached competitors with invalid JSON"""
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json")
        
        result = self.cache_service.get_cached_competitors("TEST", "area")
        self.assertIsNone(result)
    
    def test_cache_competitors_response(self):
        """Test caching competitors response"""
        competitors_data = {
            "success": True,
            "data": [
                {
                    "id": "IBM",
                    "name": "IBM",
                    "logo_url": "https://img.logo.dev/ticker/IBM?token=test",
                    "industry": "Technology",
                    "relevance_score": 0.85,
                    "competition_level": "direct",
                    "symbol": "IBM"
                }
            ]
        }
        
        self.cache_service.cache_competitors_response("TEST_BRAND", "test_area", competitors_data)
        
        # Verify the cache
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 1)
        self.assertEqual(cache_data[0]["brand_id"], "TEST_BRAND")
        self.assertEqual(cache_data[0]["area_id"], "test_area")
        self.assertTrue(cache_data[0]["success"])
        self.assertEqual(len(cache_data[0]["data"]), 1)
    
    def test_cache_competitors_response_with_none_area(self):
        """Test caching competitors response with None area_id"""
        competitors_data = {"success": True, "data": []}
        
        self.cache_service.cache_competitors_response("TEST", None, competitors_data)
        
        # Verify the cache
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 1)
        self.assertEqual(cache_data[0]["brand_id"], "TEST")
        self.assertIsNone(cache_data[0]["area_id"])
    
    def test_cache_competitors_response_replaces_existing(self):
        """Test that caching replaces existing entry for same brand/area"""
        # Cache initial data
        initial_data = {
            "success": True,
            "data": [{"symbol": "OLD", "name": "Old Company"}]
        }
        self.cache_service.cache_competitors_response("TEST", "area", initial_data)
        
        # Cache new data for same brand/area
        new_data = {
            "success": True,
            "data": [{"symbol": "NEW", "name": "New Company"}]
        }
        self.cache_service.cache_competitors_response("TEST", "area", new_data)
        
        # Verify only new data exists
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 1)
        self.assertEqual(cache_data[0]["data"][0]["symbol"], "NEW")
    
    def test_cache_competitors_response_limits_entries(self):
        """Test that cache limits the number of entries"""
        # Create more than 100 entries
        for i in range(105):
            data = {"success": True, "data": [{"symbol": f"SYM_{i}"}]}
            self.cache_service.cache_competitors_response(f"BRAND_{i}", f"area_{i}", data)
        
        # Verify only last 100 entries are kept
        with open(self.temp_file.name, 'r') as f:
            cache_data = json.load(f)
        
        self.assertEqual(len(cache_data), 100)
        # Check that the latest entries are kept
        self.assertEqual(cache_data[-1]["brand_id"], "BRAND_104")
    
    def test_cache_competitors_response_error_handling(self):
        """Test error handling during caching"""
        # Make file read-only to cause an error
        os.chmod(self.temp_file.name, 0o444)
        
        try:
            competitors_data = {"success": True, "data": []}
            # This should not raise an exception, just log the error
            self.cache_service.cache_competitors_response("TEST", "area", competitors_data)
        finally:
            # Restore write permissions for cleanup
            os.chmod(self.temp_file.name, 0o644)


if __name__ == '__main__':
    unittest.main()

import unittest
import tempfile
import os
import logging
from unittest.mock import patch
from app.services import BrandService
from app.cache_service import BrandCacheService
from app.logging_config import setup_logging


class TestLogging(unittest.TestCase):
    """Test logging functionality"""
    
    def setUp(self):
        # Setup logging for tests
        setup_logging()
        
        # Create temporary cache file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.write('[]')
        self.temp_file.close()
    
    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_brand_service_logging(self):
        """Test that BrandService logs operations correctly"""
        with self.assertLogs('brand_service', level='INFO') as log:
            service = BrandService()
            
            # Test search with cache miss
            results = service.search_brands("Oriental Bank", limit=5)
            
            # Check that logging occurred
            self.assertTrue(any("BrandService initialized" in message for message in log.output))
            self.assertTrue(any("Brand search requested" in message for message in log.output))
            self.assertTrue(any("Cache miss" in message for message in log.output))
    
    def test_cache_service_logging(self):
        """Test that CacheService logs operations correctly"""
        with self.assertLogs('brand_service.cache', level='INFO') as log:
            cache_service = BrandCacheService(self.temp_file.name)
            
            # Test cache miss
            result = cache_service.get_cached_search("Test Query")
            self.assertIsNone(result)
            
            # Check that logging occurred
            self.assertTrue(any("BrandCacheService initialized" in message for message in log.output))
            self.assertTrue(any("Cache MISS" in message for message in log.output))
    
    def test_cache_hit_logging(self):
        """Test logging for cache hits"""
        from app.models import Brand
        
        cache_service = BrandCacheService(self.temp_file.name)
        
        # Add data to cache
        sample_brand = Brand(
            id="test_brand",
            name="Test Brand",
            full_name="Test Brand Corp",
            industry="Testing",
            logo_url="https://example.com/logo.png",
            description="A test brand",
            confidence_score=0.95
        )
        
        cache_service.cache_search_results("Test Query", [sample_brand], 1)
        
        # Test cache hit
        with self.assertLogs('brand_service.cache', level='INFO') as log:
            result = cache_service.get_cached_search("Test Query")
            self.assertIsNotNone(result)
            
            # Check that cache hit was logged
            self.assertTrue(any("Cache HIT" in message for message in log.output))
    
    def test_service_integration_logging(self):
        """Test end-to-end logging for search operations"""
        with self.assertLogs('brand_service', level='INFO') as log:
            service = BrandService()
            
            # First search (cache miss)
            results1 = service.search_brands("Bank", limit=3)
            
            # Second search (cache hit)
            results2 = service.search_brands("Bank", limit=3)
            
            # Verify both cache miss and hit are logged
            log_messages = ' '.join(log.output)
            self.assertIn("Cache miss", log_messages)
            self.assertIn("Cache hit", log_messages)


if __name__ == '__main__':
    unittest.main()

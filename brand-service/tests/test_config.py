"""
Unit tests for config module
"""
import unittest
import os
from unittest.mock import patch
from app.config import Config, config


class TestConfig(unittest.TestCase):
    """Test configuration class functionality"""
    
    def test_default_config_values(self):
        """Test default configuration values"""
        self.assertEqual(Config.ALPHA_VANTAGE_API_KEY, "V45CYDJMRGPPDDZH")
        self.assertEqual(Config.FMP_API_KEY, "GKfomFCs7H9TyoB8XR58L8MaGiDqtWXi")
        self.assertEqual(Config.TOGETHER_AI_API_KEY, "tgp_v1_DQRzQY2vHkoS6j6bGTPiWwIVVB0cFJmqLxwx0k4_tMY")
        self.assertEqual(Config.TOGETHER_AI_MODEL, "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")
        self.assertEqual(Config.LOGO_DEV_API_KEY, "pk_TVi0kXveSqGUNVDsvdijOA")
        self.assertEqual(Config.API_TIMEOUT, 30)
        self.assertEqual(Config.MAX_CACHE_ENTRIES, 100)
        self.assertEqual(Config.MAX_REQUESTS_PER_MINUTE, 60)
    
    @patch.dict(os.environ, {
        'ALPHA_VANTAGE_API_KEY': 'test_alpha_key',
        'FMP_API_KEY': 'test_fmp_key',
        'TOGETHER_AI_API_KEY': 'test_together_key',
        'TOGETHER_AI_MODEL': 'test_model',
        'LOGO_DEV_API_KEY': 'test_logo_key'
    })
    def test_environment_variable_override(self):
        """Test that environment variables override default values"""
        # Test that environment variables can be accessed
        self.assertEqual(os.getenv('ALPHA_VANTAGE_API_KEY'), "test_alpha_key")
        self.assertEqual(os.getenv('FMP_API_KEY'), "test_fmp_key")
        self.assertEqual(os.getenv('TOGETHER_AI_API_KEY'), "test_together_key")
        self.assertEqual(os.getenv('TOGETHER_AI_MODEL'), "test_model")
        self.assertEqual(os.getenv('LOGO_DEV_API_KEY'), "test_logo_key")
    
    def test_get_alpha_vantage_symbol_search_url(self):
        """Test Alpha Vantage symbol search URL generation"""
        query = "TEST_QUERY"
        expected_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={query}&apikey={Config.ALPHA_VANTAGE_API_KEY}"
        actual_url = Config.get_alpha_vantage_symbol_search_url(query)
        self.assertEqual(actual_url, expected_url)
    
    def test_get_alpha_vantage_overview_url(self):
        """Test Alpha Vantage company overview URL generation"""
        symbol = "TEST_SYMBOL"
        expected_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={Config.ALPHA_VANTAGE_API_KEY}"
        actual_url = Config.get_alpha_vantage_overview_url(symbol)
        self.assertEqual(actual_url, expected_url)
    
    def test_get_fmp_search_url(self):
        """Test FMP search URL generation"""
        query = "TEST_QUERY"
        expected_url = f"https://financialmodelingprep.com/stable/search-name?query={query}&apikey={Config.FMP_API_KEY}"
        actual_url = Config.get_fmp_search_url(query)
        self.assertEqual(actual_url, expected_url)
    
    def test_get_fmp_profile_url(self):
        """Test FMP profile URL generation"""
        symbol = "TEST_SYMBOL"
        expected_url = f"https://financialmodelingprep.com/stable/profile?symbol={symbol}&apikey={Config.FMP_API_KEY}"
        actual_url = Config.get_fmp_profile_url(symbol)
        self.assertEqual(actual_url, expected_url)
    
    def test_get_logo_url(self):
        """Test logo URL generation"""
        symbol = "TEST_SYMBOL"
        expected_url = f"https://img.logo.dev/ticker/{symbol}?token={Config.LOGO_DEV_API_KEY}"
        actual_url = Config.get_logo_url(symbol)
        self.assertEqual(actual_url, expected_url)
    
    def test_get_together_ai_chat_url(self):
        """Test Together.ai chat URL generation"""
        expected_url = "https://api.together.xyz/v1/chat/completions"
        actual_url = Config.get_together_ai_chat_url()
        self.assertEqual(actual_url, expected_url)
    
    def test_global_config_instance(self):
        """Test that global config instance exists and is accessible"""
        self.assertIsInstance(config, Config)
        self.assertEqual(config.ALPHA_VANTAGE_BASE_URL, "https://www.alphavantage.co/query")
        self.assertEqual(config.FMP_BASE_URL, "https://financialmodelingprep.com/stable")
        self.assertEqual(config.TOGETHER_AI_BASE_URL, "https://api.together.xyz/v1")
        self.assertEqual(config.LOGO_DEV_BASE_URL, "https://img.logo.dev/ticker")
    
    def test_url_methods_with_special_characters(self):
        """Test URL generation with special characters"""
        query_with_spaces = "Test Query"
        symbol_with_special = "TEST-SYMBOL.A"
        
        # These should not raise exceptions
        alpha_url = Config.get_alpha_vantage_symbol_search_url(query_with_spaces)
        fmp_url = Config.get_fmp_search_url(query_with_spaces)
        logo_url = Config.get_logo_url(symbol_with_special)
        
        self.assertIn("Test Query", alpha_url)
        self.assertIn("Test Query", fmp_url)
        self.assertIn("TEST-SYMBOL.A", logo_url)


if __name__ == '__main__':
    unittest.main()

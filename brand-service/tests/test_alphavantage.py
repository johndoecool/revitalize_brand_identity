import unittest
import asyncio
from unittest.mock import patch, AsyncMock
from app.alphavantage_service import AlphaVantageService
from app.models import Brand


class TestAlphaVantageService(unittest.TestCase):
    """Test Alpha Vantage service functionality"""
    
    def setUp(self):
        self.service = AlphaVantageService()
    
    def test_extract_match_score(self):
        """Test match score extraction"""
        # Test valid match score
        match_data = {"9. matchScore": "0.8500"}
        score = self.service.extract_match_score(match_data)
        self.assertEqual(score, 0.85)
        
        # Test invalid match score
        match_data = {"9. matchScore": "invalid"}
        score = self.service.extract_match_score(match_data)
        self.assertEqual(score, 0.0)
        
        # Test missing match score
        match_data = {}
        score = self.service.extract_match_score(match_data)
        self.assertEqual(score, 0.0)
    
    def test_create_brand_from_data(self):
        """Test brand creation from Alpha Vantage data"""
        symbol_data = {
            "1. symbol": "AAPL",
            "2. name": "Apple Inc.",
            "9. matchScore": "0.9000"
        }
        
        overview_data = {
            "Symbol": "AAPL",
            "Name": "Apple Inc.",
            "Industry": "Technology",
            "Description": "Apple Inc. designs and manufactures consumer electronics."
        }
        
        brand = self.service.create_brand_from_data(symbol_data, overview_data)
        
        self.assertIsInstance(brand, Brand)
        self.assertEqual(brand.id, "AAPL")
        self.assertEqual(brand.name, "Apple Inc.")
        self.assertEqual(brand.industry, "Technology")
        self.assertEqual(brand.confidence_score, 0.9)
        self.assertIn("AAPL", brand.logo_url)
    
    @patch('httpx.AsyncClient.get')
    async def test_search_symbols_success(self, mock_get):
        """Test successful symbol search"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "bestMatches": [
                {
                    "1. symbol": "AAPL",
                    "2. name": "Apple Inc.",
                    "9. matchScore": "0.9000"
                }
            ]
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        results = await self.service.search_symbols("Apple")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["1. symbol"], "AAPL")
    
    @patch('httpx.AsyncClient.get')
    async def test_get_company_overview_success(self, mock_get):
        """Test successful company overview retrieval"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "Symbol": "AAPL",
            "Name": "Apple Inc.",
            "Industry": "Technology",
            "Description": "Apple Inc. designs and manufactures consumer electronics."
        }
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await self.service.get_company_overview("AAPL")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["Symbol"], "AAPL")
        self.assertEqual(result["Name"], "Apple Inc.")
    
    @patch('httpx.AsyncClient.get')
    async def test_get_company_overview_not_found(self, mock_get):
        """Test company overview for invalid symbol"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {}  # Empty response for invalid symbol
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        result = await self.service.get_company_overview("INVALID")
        
        self.assertIsNone(result)
    
    @patch.object(AlphaVantageService, 'get_company_overview')
    @patch.object(AlphaVantageService, 'search_symbols')
    async def test_search_brands_integration(self, mock_search_symbols, mock_get_overview):
        """Test full brand search integration"""
        # Mock symbol search response
        mock_search_symbols.return_value = [
            {
                "1. symbol": "AAPL",
                "2. name": "Apple Inc.",
                "9. matchScore": "0.9000"
            },
            {
                "1. symbol": "MSFT",
                "2. name": "Microsoft Corporation",
                "9. matchScore": "0.8000"
            }
        ]
        
        # Mock company overview responses
        async def mock_overview_side_effect(symbol):
            if symbol == "AAPL":
                return {
                    "Symbol": "AAPL",
                    "Name": "Apple Inc.",
                    "Industry": "Technology",
                    "Description": "Apple Inc. designs and manufactures consumer electronics."
                }
            elif symbol == "MSFT":
                return {
                    "Symbol": "MSFT",
                    "Name": "Microsoft Corporation",
                    "Industry": "Technology",
                    "Description": "Microsoft Corporation develops software and services."
                }
            return None
        
        mock_get_overview.side_effect = mock_overview_side_effect
        
        brands = await self.service.search_brands("Tech", limit=2)
        
        self.assertEqual(len(brands), 2)
        self.assertEqual(brands[0].id, "AAPL")  # Should be first due to higher match score
        self.assertEqual(brands[1].id, "MSFT")


if __name__ == '__main__':
    # Run async tests
    unittest.main()

"""
Alpha Vantage API Service for fetching real brand/company data
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx
from app.config import config
from app.models import Brand


class AlphaVantageService:
    """Service for interacting with Alpha Vantage API"""
    
    def __init__(self):
        self.logger = logging.getLogger('brand_service.alphavantage')
        self.timeout = httpx.Timeout(config.API_TIMEOUT)
        self.logger.info("AlphaVantageService initialized")
    
    async def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for symbols using Alpha Vantage API"""
        self.logger.info(f"Searching symbols for query: '{query}'")
        
        url = config.get_alpha_vantage_symbol_search_url(query)
        self.logger.debug(f"Alpha Vantage search URL: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                self.logger.debug(f"Alpha Vantage search response: {data}")
                
                # Check for API rate limit response
                if "Information" in data and "rate limit" in data["Information"].lower():
                    self.logger.warning(f"Alpha Vantage rate limit reached: {data['Information']}")
                    return []
                
                # Extract best matches
                best_matches = data.get("bestMatches", [])
                self.logger.info(f"Found {len(best_matches)} symbol matches for query: '{query}'")
                
                return best_matches
                
        except httpx.ConnectError as e:
            self.logger.error(f"Network connection error during symbol search for '{query}': {str(e)}")
            return []  # Return empty list instead of raising
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout error during symbol search for '{query}': {str(e)}")
            return []  # Return empty list instead of raising
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error during symbol search for '{query}': {str(e)}")
            return []  # Return empty list instead of raising
        except Exception as e:
            self.logger.error(f"Unexpected error during symbol search for '{query}': {str(e)}")
            return []  # Return empty list instead of raising
    
    async def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company overview for a symbol"""
        self.logger.info(f"Getting company overview for symbol: '{symbol}'")
        
        url = config.get_alpha_vantage_overview_url(symbol)
        self.logger.debug(f"Alpha Vantage overview URL: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                self.logger.debug(f"Alpha Vantage overview response for {symbol}: {data}")
                
                # Check for API rate limit response
                if "Information" in data and "rate limit" in data.get("Information", "").lower():
                    self.logger.warning(f"Alpha Vantage rate limit reached for symbol '{symbol}': {data['Information']}")
                    return None
                
                # Check if we got valid data (Alpha Vantage returns empty dict for invalid symbols)
                if not data or "Symbol" not in data:
                    self.logger.warning(f"No company data found for symbol: '{symbol}'")
                    return None
                
                self.logger.info(f"Successfully retrieved company overview for symbol: '{symbol}'")
                return data
                
        except httpx.ConnectError as e:
            self.logger.error(f"Network connection error during company overview for '{symbol}': {str(e)}")
            return None
        except httpx.TimeoutException as e:
            self.logger.error(f"Timeout error during company overview for '{symbol}': {str(e)}")
            return None
        except httpx.HTTPError as e:
            self.logger.error(f"HTTP error during company overview for '{symbol}': {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during company overview for '{symbol}': {str(e)}")
            return None
    
    def extract_match_score(self, match_data: Dict[str, Any]) -> float:
        """Extract match score from Alpha Vantage search result"""
        try:
            # Alpha Vantage provides matchScore as a string like "0.8000"
            match_score = float(match_data.get("9. matchScore", "0.0"))
            self.logger.debug(f"Extracted match score: {match_score} for symbol: {match_data.get('1. symbol', 'Unknown')}")
            return match_score
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid match score in data: {match_data}")
            return 0.0
    
    def create_brand_from_data(self, symbol_data: Dict[str, Any], overview_data: Dict[str, Any]) -> Brand:
        """Create a Brand object from Alpha Vantage data"""
        symbol = overview_data.get("Symbol", symbol_data.get("1. symbol", ""))
        name = overview_data.get("Name", symbol_data.get("2. name", ""))
        industry = overview_data.get("Industry", "Unknown")
        description = overview_data.get("Description", "")
        match_score = self.extract_match_score(symbol_data)
        
        # Generate logo URL
        logo_url = config.get_logo_url(symbol)
        
        brand = Brand(
            id=symbol,
            name=name,
            full_name=name,  # Using the same name as full_name
            industry=industry,
            logo_url=logo_url,
            description=description,
            confidence_score=match_score
        )
        
        self.logger.debug(f"Created brand object for symbol: {symbol}")
        return brand
    
    async def search_brands(self, query: str, limit: int = 10) -> List[Brand]:
        """
        Search for brands using Alpha Vantage API
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of Brand objects
        """
        self.logger.info(f"Starting Alpha Vantage brand search for query: '{query}' with limit: {limit}")
        
        # Step 1: Search for symbols
        symbol_matches = await self.search_symbols(query)
        
        if not symbol_matches:
            self.logger.info(f"No symbol matches found for query: '{query}'")
            return []
        
        # Step 2: Sort by match score and take top results
        symbol_matches.sort(key=self.extract_match_score, reverse=True)
        top_matches = symbol_matches[:limit]
        
        self.logger.info(f"Processing top {len(top_matches)} symbol matches")
        
        # Step 3: Get company overview for each symbol (with concurrent requests)
        brands = []
        
        async def process_symbol(symbol_data: Dict[str, Any]) -> Optional[Brand]:
            symbol = symbol_data.get("1. symbol", "")
            if not symbol:
                self.logger.warning(f"No symbol found in data: {symbol_data}")
                return None
            
            overview_data = await self.get_company_overview(symbol)
            if overview_data:
                return self.create_brand_from_data(symbol_data, overview_data)
            return None
        
        # Process symbols concurrently but with some rate limiting
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
        
        async def process_with_semaphore(symbol_data):
            async with semaphore:
                return await process_symbol(symbol_data)
        
        tasks = [process_with_semaphore(symbol_data) for symbol_data in top_matches]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        for result in results:
            if isinstance(result, Brand):
                brands.append(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Error processing symbol: {str(result)}")
        
        self.logger.info(f"Successfully created {len(brands)} brand objects from Alpha Vantage data")
        return brands

"""
Configuration settings for the Brand Service
"""
import os
from typing import Optional


class Config:
    """Configuration class for Brand Service"""
    
    # Alpha Vantage API Configuration
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "V45CYDJMRGPPDDZH")
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
    
    # Financial Modeling Prep API Configuration
    FMP_API_KEY: str = os.getenv("FMP_API_KEY", "GKfomFCs7H9TyoB8XR58L8MaGiDqtWXi")
    FMP_BASE_URL: str = "https://financialmodelingprep.com/stable"
    
    # Together.ai API Configuration
    TOGETHER_AI_API_KEY: str = os.getenv("TOGETHER_AI_API_KEY", "tgp_v1_DQRzQY2vHkoS6j6bGTPiWwIVVB0cFJmqLxwx0k4_tMY")
    TOGETHER_AI_BASE_URL: str = "https://api.together.xyz/v1"
    TOGETHER_AI_MODEL: str = os.getenv("TOGETHER_AI_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")
    
    # Logo.dev API Configuration
    LOGO_DEV_API_KEY: str = os.getenv("LOGO_DEV_API_KEY", "pk_TVi0kXveSqGUNVDsvdijOA")
    LOGO_DEV_BASE_URL: str = "https://img.logo.dev/ticker"
    
    # Request timeouts
    API_TIMEOUT: int = 30
    
    # Cache configuration
    CACHE_FILE_PATH: str = "brand-cache.json"
    MAX_CACHE_ENTRIES: int = 100
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    
    @classmethod
    def get_alpha_vantage_symbol_search_url(cls, query: str) -> str:
        """Get Alpha Vantage symbol search URL"""
        return f"{cls.ALPHA_VANTAGE_BASE_URL}?function=SYMBOL_SEARCH&keywords={query}&apikey={cls.ALPHA_VANTAGE_API_KEY}"
    
    @classmethod
    def get_alpha_vantage_overview_url(cls, symbol: str) -> str:
        """Get Alpha Vantage company overview URL"""
        return f"{cls.ALPHA_VANTAGE_BASE_URL}?function=OVERVIEW&symbol={symbol}&apikey={cls.ALPHA_VANTAGE_API_KEY}"
    
    @classmethod
    def get_fmp_search_url(cls, query: str) -> str:
        """Get Financial Modeling Prep search URL"""
        return f"{cls.FMP_BASE_URL}/search-name?query={query}&apikey={cls.FMP_API_KEY}"
    
    @classmethod
    def get_fmp_profile_url(cls, symbol: str) -> str:
        """Get Financial Modeling Prep profile URL"""
        return f"{cls.FMP_BASE_URL}/profile?symbol={symbol}&apikey={cls.FMP_API_KEY}"
    
    @classmethod
    def get_logo_url(cls, symbol: str) -> str:
        """Get logo URL for a given symbol"""
        return f"{cls.LOGO_DEV_BASE_URL}/{symbol}?token={cls.LOGO_DEV_API_KEY}"
    
    @classmethod
    def get_together_ai_chat_url(cls) -> str:
        """Get Together.ai chat completions URL"""
        return f"{cls.TOGETHER_AI_BASE_URL}/chat/completions"


# Create a global config instance
config = Config()

from pydantic_settings import BaseSettings
import os
from enum import Enum

class LLMProvider(str, Enum):
    OPENAI = "openai"
    TOGETHER = "together"

class Settings(BaseSettings):
    # LLM Provider Configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.OPENAI
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Together.ai Configuration
    TOGETHER_API_KEY: str = os.getenv("TOGETHER_API_KEY", "")
    TOGETHER_MODEL: str = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")
    
    # SSL Configuration
    SSL_VERIFY: bool = os.getenv("SSL_VERIFY", "true").lower() == "true"
    
    # Service Configuration
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "analysis-engine")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8003"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # External Services
    DATA_SERVICE_URL: str = os.getenv("DATA_SERVICE_URL", "http://localhost:8002")
    BRAND_SERVICE_URL: str = os.getenv("BRAND_SERVICE_URL", "http://localhost:8001")
    
    # Database Configuration
    DATABASE_JSON_PATH: str = os.getenv("DATABASE_JSON_PATH", "../shared/database.json")
    
    # PDF Report Configuration
    SAVE_REPORTS_LOCALLY: bool = os.getenv("SAVE_REPORTS_LOCALLY", "true").lower() == "true"
    REPORTS_DIRECTORY: str = os.getenv("REPORTS_DIRECTORY", "./reports")
    
    # Data Collection Configuration
    DATA_COLLECTION_PATH: str = os.getenv("DATA_COLLECTION_PATH", "../data-collection/data/collected_data")
    
    class Config:
        env_file = ".env"
        
    def get_active_llm_config(self):
        """Get the configuration for the active LLM provider"""
        if self.LLM_PROVIDER == LLMProvider.OPENAI:
            return {
                "provider": "openai",
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL
            }
        elif self.LLM_PROVIDER == LLMProvider.TOGETHER:
            return {
                "provider": "together",
                "api_key": self.TOGETHER_API_KEY,
                "model": self.TOGETHER_MODEL,
                "ssl_verify": self.SSL_VERIFY
            }
        else:
            raise ValueError(f"Unknown LLM provider: {self.LLM_PROVIDER}")

settings = Settings()

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pydantic import Field


class Settings(BaseSettings):
    # Server Configuration
    port: int = 8002
    host: str = "0.0.0.0"
    debug: bool = True
    
    # Database Configuration
    data_storage_path: str = "./data"
    use_vector_db: bool = False
    
    # API Keys
    news_api_key: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY") 
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    twitter_bearer_token: Optional[str] = Field(default=None, env="TWITTER_BEARER_TOKEN")
    
    # LLM API Keys for Sentiment Analysis
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    cohere_api_key: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    
    # LLM Configuration
    preferred_llm_provider: str = Field(default="openai", env="PREFERRED_LLM_PROVIDER")  # openai, anthropic, huggingface, cohere
    llm_model_name: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL_NAME")
    llm_max_tokens: int = Field(default=150, env="LLM_MAX_TOKENS")
    llm_temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")  # Low temperature for consistent sentiment analysis
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Rate Limiting Configuration
    default_rate_limit: int = 1000
    news_rate_limit: int = 1000
    social_media_rate_limit: int = 500
    glassdoor_rate_limit: int = 100
    website_rate_limit: int = 50
    
    # Scraping Configuration
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    request_timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = False  # Set to True for production
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # Data Sources Configuration
    available_sources: List[str] = ["news", "social_media", "glassdoor", "website"]
    
    # Analysis Engine Configuration
    ANALYSIS_FOCUS: str = Field(default="comprehensive", env="ANALYSIS_FOCUS")  # Configurable analysis focus
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()

# Ensure data directories exist
os.makedirs(settings.data_storage_path, exist_ok=True)
os.makedirs("logs", exist_ok=True) 
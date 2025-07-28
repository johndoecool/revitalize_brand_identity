from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Server Configuration
    port: int = 8002
    host: str = "0.0.0.0"
    debug: bool = True
    
    # Database Configuration
    data_storage_path: str = "./data"
    vector_db_path: str = "./vector_db"
    use_vector_db: bool = True
    
    # API Keys
    news_api_key: Optional[str] = ""
    twitter_api_key: Optional[str] = ""
    twitter_api_secret: Optional[str] = ""
    twitter_bearer_token: Optional[str] = ""
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure data directories exist
os.makedirs(settings.data_storage_path, exist_ok=True)
os.makedirs(settings.vector_db_path, exist_ok=True)
os.makedirs("logs", exist_ok=True) 

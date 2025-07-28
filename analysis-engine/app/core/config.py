from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Service Configuration
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "analysis-engine")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8003"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # External Services
    DATA_SERVICE_URL: str = os.getenv("DATA_SERVICE_URL", "http://localhost:8002")
    BRAND_SERVICE_URL: str = os.getenv("BRAND_SERVICE_URL", "http://localhost:8001")
    
    class Config:
        env_file = ".env"

settings = Settings()

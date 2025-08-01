#!/usr/bin/env python3
"""
Configuration for shared services
Following the same pattern as analysis-engine/app/core/config.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in data-collection directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

class SharedConfig:
    """Configuration for shared services"""
    
        # Shared Database Configuration - configurable via environment variable  
    # Default path is now relative to the project root from data-collection/src/config/
    SHARED_DATABASE_PATH: str = os.getenv("SHARED_DATABASE_PATH", "../../../shared/database.json")
    
    # Default paths for different services
    DATA_COLLECTION_SERVICE_URL: str = os.getenv("DATA_COLLECTION_SERVICE_URL", "http://localhost:8002")
    ANALYSIS_ENGINE_SERVICE_URL: str = os.getenv("ANALYSIS_ENGINE_SERVICE_URL", "http://localhost:8003")
    
    @classmethod
    def get_database_path(cls) -> str:
        """Get the configured database path, respecting environment variable"""
        db_path = cls.SHARED_DATABASE_PATH
        
        # Always use the configured path as-is (whether absolute or relative)
        # If it's a relative path, resolve it relative to this config file's location
        if not os.path.isabs(db_path):
            config_dir = Path(__file__).parent
            resolved_path = (config_dir / db_path).resolve()
            return str(resolved_path)
        
        # For absolute paths, use exactly as specified
        return db_path
    
    @classmethod
    def ensure_database_directory(cls) -> bool:
        """Ensure the database directory exists"""
        try:
            db_path = Path(cls.get_database_path())
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating database directory: {e}")
            return False


# Global configuration instance
shared_config = SharedConfig() 
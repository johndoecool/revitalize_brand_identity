"""
Brand Areas Cache Service
Handles caching for brand area suggestions
"""
import json
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger('brand_service.areas_cache')

class BrandAreasCacheService:
    """Service for managing brand areas cache"""
    
    def __init__(self):
        """Initialize the cache service"""
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cache_file_path = os.path.join(script_dir, "brand-areas.json")
        logger.debug(f"Areas cache file path: {self.cache_file_path}")
        
        # Ensure cache file exists
        self._ensure_cache_file_exists()
    
    def _ensure_cache_file_exists(self) -> None:
        """Ensure the cache file exists"""
        try:
            if not os.path.exists(self.cache_file_path):
                logger.info(f"Creating new areas cache file: {self.cache_file_path}")
                with open(self.cache_file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)
            else:
                logger.debug(f"Areas cache file exists: {self.cache_file_path}")
        except Exception as e:
            logger.error(f"Error ensuring areas cache file exists: {str(e)}")
    
    def get_cached_areas(self, brand_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached areas for a brand
        
        Args:
            brand_id: The brand identifier
            
        Returns:
            Cached areas data if found, None otherwise
        """
        try:
            logger.info(f"Searching areas cache for brand_id: '{brand_id}'")
            
            if not os.path.exists(self.cache_file_path):
                logger.info(f"Areas cache file not found: {self.cache_file_path}")
                return None
            
            with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Search for the brand_id in cache
            for entry in cache_data:
                if entry.get("brand_id") == brand_id:
                    logger.info(f"Areas cache HIT for brand_id: '{brand_id}'")
                    return entry
            
            logger.info(f"Areas cache MISS for brand_id: '{brand_id}'")
            return None
            
        except FileNotFoundError:
            logger.info(f"Areas cache file not found: {self.cache_file_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing areas cache JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error reading areas cache: {str(e)}")
            return None
    
    def cache_areas_response(self, brand_id: str, areas_data: Dict[str, Any]) -> None:
        """
        Cache areas response for a brand
        
        Args:
            brand_id: The brand identifier
            areas_data: The areas data to cache
        """
        try:
            logger.info(f"Caching areas for brand_id: '{brand_id}'")
            
            # Load existing cache
            cache_data = []
            if os.path.exists(self.cache_file_path):
                try:
                    with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    logger.warning("Could not load existing areas cache, starting fresh")
                    cache_data = []
            
            # Remove existing entry for this brand_id if present
            cache_data = [entry for entry in cache_data if entry.get("brand_id") != brand_id]
            
            # Add new entry
            cache_entry = {
                "brand_id": brand_id,
                "cached_at": datetime.now().isoformat(),
                **areas_data
            }
            
            cache_data.append(cache_entry)
            
            # Keep only the last 100 entries to prevent unlimited growth
            if len(cache_data) > 100:
                cache_data = cache_data[-100:]
            
            # Write back to file
            with open(self.cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully cached areas for brand_id: '{brand_id}'")
            
        except Exception as e:
            logger.error(f"Error caching areas response for brand_id '{brand_id}': {str(e)}")

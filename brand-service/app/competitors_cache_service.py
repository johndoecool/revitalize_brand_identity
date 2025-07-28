"""
Brand Competitors Cache Service
Handles caching for brand competitor suggestions
"""
import json
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger('brand_service.competitors_cache')

class BrandCompetitorsCacheService:
    """Service for managing brand competitors cache"""
    
    def __init__(self):
        """Initialize the cache service"""
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cache_file_path = os.path.join(script_dir, "brand-competitors.json")
        logger.debug(f"Competitors cache file path: {self.cache_file_path}")
        
        # Ensure cache file exists
        self._ensure_cache_file_exists()
    
    def _ensure_cache_file_exists(self) -> None:
        """Ensure the cache file exists"""
        try:
            if not os.path.exists(self.cache_file_path):
                logger.info(f"Creating new competitors cache file: {self.cache_file_path}")
                with open(self.cache_file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)
            else:
                logger.debug(f"Competitors cache file exists: {self.cache_file_path}")
        except Exception as e:
            logger.error(f"Error ensuring competitors cache file exists: {str(e)}")
    
    def get_cached_competitors(self, brand_id: str, area_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached competitors for a brand and area combination
        
        Args:
            brand_id: The brand identifier
            area_id: The area identifier (optional)
            
        Returns:
            Cached competitors data if found, None otherwise
        """
        try:
            cache_key = f"{brand_id}_{area_id}" if area_id else brand_id
            logger.info(f"Searching competitors cache for key: '{cache_key}'")
            
            if not os.path.exists(self.cache_file_path):
                logger.info(f"Competitors cache file not found: {self.cache_file_path}")
                return None
            
            with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Search for the brand_id and area_id combination in cache
            for entry in cache_data:
                entry_brand_id = entry.get("brand_id")
                entry_area_id = entry.get("area_id")
                
                # Check if this entry matches our search criteria
                if entry_brand_id == brand_id and entry_area_id == area_id:
                    logger.info(f"Competitors cache HIT for key: '{cache_key}'")
                    return entry
            
            logger.info(f"Competitors cache MISS for key: '{cache_key}'")
            return None
            
        except FileNotFoundError:
            logger.info(f"Competitors cache file not found: {self.cache_file_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing competitors cache JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error reading competitors cache: {str(e)}")
            return None
    
    def cache_competitors_response(self, brand_id: str, area_id: Optional[str], competitors_data: Dict[str, Any]) -> None:
        """
        Cache competitors response for a brand and area combination
        
        Args:
            brand_id: The brand identifier
            area_id: The area identifier (optional)
            competitors_data: The competitors data to cache
        """
        try:
            cache_key = f"{brand_id}_{area_id}" if area_id else brand_id
            logger.info(f"Caching competitors for key: '{cache_key}'")
            
            # Load existing cache
            cache_data = []
            if os.path.exists(self.cache_file_path):
                try:
                    with open(self.cache_file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    logger.warning("Could not load existing competitors cache, starting fresh")
                    cache_data = []
            
            # Remove existing entry for this brand_id and area_id combination if present
            cache_data = [
                entry for entry in cache_data 
                if not (entry.get("brand_id") == brand_id and entry.get("area_id") == area_id)
            ]
            
            # Add new entry
            cache_entry = {
                "brand_id": brand_id,
                "area_id": area_id,
                "cached_at": datetime.now().isoformat(),
                **competitors_data
            }
            
            cache_data.append(cache_entry)
            
            # Keep only the last 100 entries to prevent unlimited growth
            if len(cache_data) > 100:
                cache_data = cache_data[-100:]
            
            # Write back to file
            with open(self.cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully cached competitors for key: '{cache_key}'")
            
        except Exception as e:
            logger.error(f"Error caching competitors response for key '{cache_key}': {str(e)}")

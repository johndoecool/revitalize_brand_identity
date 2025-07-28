import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models import Brand, BrandSearchResponse


class BrandCacheService:
    """Service for managing brand search cache"""
    
    def __init__(self, cache_file_path: str = "brand-cache.json"):
        # Ensure we use the correct path relative to the project root
        if not os.path.isabs(cache_file_path):
            # Get the project root directory (one level up from app directory)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_file_path = os.path.join(project_root, cache_file_path)
        
        self.cache_file_path = cache_file_path
        self.logger = logging.getLogger('brand_service.cache')
        self._ensure_cache_file_exists()
        self.logger.info(f"BrandCacheService initialized with cache file: {cache_file_path}")
        
        # Debug: Print cache file location
        print(f"Cache file path: {self.cache_file_path}")
        print(f"Cache file exists: {os.path.exists(self.cache_file_path)}")
    
    def _ensure_cache_file_exists(self):
        """Ensure the cache file exists, create if it doesn't"""
        if not os.path.exists(self.cache_file_path):
            self.logger.info(f"Cache file {self.cache_file_path} not found, creating new one")
            self._write_cache([])
        else:
            self.logger.debug(f"Cache file {self.cache_file_path} found")
    
    def _read_cache(self) -> List[Dict[str, Any]]:
        """Read cache data from file"""
        try:
            with open(self.cache_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.logger.debug(f"Successfully read cache file with {len(data)} entries")
                return data
        except FileNotFoundError:
            self.logger.warning(f"Cache file {self.cache_file_path} not found")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in cache file {self.cache_file_path}: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error reading cache file {self.cache_file_path}: {str(e)}")
            return []
    
    def _write_cache(self, cache_data: List[Dict[str, Any]]):
        """Write cache data to file"""
        try:
            with open(self.cache_file_path, 'w', encoding='utf-8') as file:
                json.dump(cache_data, file, indent=2, ensure_ascii=False)
                self.logger.debug(f"Successfully wrote {len(cache_data)} entries to cache file")
        except Exception as e:
            self.logger.error(f"Error writing to cache file {self.cache_file_path}: {str(e)}")
            raise
    
    def get_cached_search(self, query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Get cached search results for a query"""
        self.logger.info(f"Searching cache for query: '{query}' with limit: {limit}")
        
        cache_data = self._read_cache()
        
        # Normalize query for comparison
        normalized_query = query.lower().strip()
        
        for cache_entry in cache_data:
            if cache_entry.get("query", "").lower().strip() == normalized_query:
                self.logger.info(f"Cache HIT for query: '{query}'")
                
                # Filter results based on limit
                cached_brands = cache_entry.get("data", [])[:limit]
                
                # Return the cache entry format (not BrandSearchResponse)
                result = {
                    "query": cache_entry.get("query"),
                    "success": True,
                    "data": cached_brands,
                    "total_results": len(cached_brands)
                }
                
                self.logger.info(f"Returning {len(cached_brands)} cached brands for query: '{query}'")
                return result
        
        self.logger.info(f"Cache MISS for query: '{query}'")
        return None
    
    def cache_search_response(self, response_data: Dict[str, Any]):
        """Cache a complete search response"""
        query = response_data.get("query", "")
        self.logger.info(f"Caching complete search response for query: '{query}'")
        
        cache_data = self._read_cache()
        
        # Normalize query
        normalized_query = query.lower().strip()
        
        # Remove existing cache entry for this query
        original_count = len(cache_data)
        cache_data = [
            entry for entry in cache_data 
            if entry.get("query", "").lower().strip() != normalized_query
        ]
        
        if len(cache_data) < original_count:
            self.logger.debug(f"Removed existing cache entry for query: '{query}'")
        
        # Add new cache entry with timestamp
        cache_entry = {
            **response_data,
            "cached_at": datetime.now().isoformat(),
            "expires_at": None  # Can be implemented for TTL
        }
        
        cache_data.append(cache_entry)
        
        # Keep only the last 100 entries to prevent cache from growing too large
        if len(cache_data) > 100:
            removed_count = len(cache_data) - 100
            cache_data = cache_data[-100:]
            self.logger.warning(f"Cache size limit reached, removed {removed_count} oldest entries")
        
        self._write_cache(cache_data)
        self.logger.info(f"Successfully cached response for query: '{query}'")
    
    def clear_cache(self):
        """Clear all cached data"""
        self.logger.info("Clearing all cache data")
        try:
            self._write_cache([])
            self.logger.info("Cache cleared successfully")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {str(e)}")
            raise
    
    def remove_cached_query(self, query: str) -> bool:
        """Remove cached data for a specific query"""
        self.logger.info(f"Attempting to remove cached query: '{query}'")
        
        cache_data = self._read_cache()
        normalized_query = query.lower().strip()
        
        original_length = len(cache_data)
        cache_data = [
            entry for entry in cache_data 
            if entry.get("query", "").lower().strip() != normalized_query
        ]
        
        if len(cache_data) < original_length:
            self._write_cache(cache_data)
            self.logger.info(f"Successfully removed cached query: '{query}'")
            return True
        
        self.logger.info(f"No cached data found for query: '{query}'")
        return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_data = self._read_cache()
        
        return {
            "total_entries": len(cache_data),
            "total_brands": sum(len(entry.get("data", [])) for entry in cache_data),
            "queries": [entry.get("query") for entry in cache_data],
            "cache_file_size_bytes": os.path.getsize(self.cache_file_path) if os.path.exists(self.cache_file_path) else 0
        }
    
    def search_cache(self, search_term: str) -> List[Dict[str, Any]]:
        """Search through cached queries and brands"""
        cache_data = self._read_cache()
        results = []
        
        search_term_lower = search_term.lower()
        
        for entry in cache_data:
            # Search in query
            if search_term_lower in entry.get("query", "").lower():
                results.append({
                    "type": "query",
                    "match": entry.get("query"),
                    "entry": entry
                })
            
            # Search in brand data
            for brand in entry.get("data", []):
                if (search_term_lower in brand.get("name", "").lower() or
                    search_term_lower in brand.get("full_name", "").lower() or
                    search_term_lower in brand.get("description", "").lower()):
                    results.append({
                        "type": "brand",
                        "match": brand.get("name"),
                        "brand": brand,
                        "query": entry.get("query")
                    })
        
        return results
    
    def export_cache(self, export_path: str):
        """Export cache to a different file"""
        cache_data = self._read_cache()
        with open(export_path, 'w', encoding='utf-8') as file:
            json.dump(cache_data, file, indent=2, ensure_ascii=False)
    
    def import_cache(self, import_path: str, merge: bool = True):
        """Import cache from a file"""
        with open(import_path, 'r', encoding='utf-8') as file:
            imported_data = json.load(file)
        
        if merge:
            existing_data = self._read_cache()
            # Merge, avoiding duplicates based on query
            existing_queries = {entry.get("query", "").lower() for entry in existing_data}
            
            for entry in imported_data:
                if entry.get("query", "").lower() not in existing_queries:
                    existing_data.append(entry)
            
            self._write_cache(existing_data)
        else:
            self._write_cache(imported_data)

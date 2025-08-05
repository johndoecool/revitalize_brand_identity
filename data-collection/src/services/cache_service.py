"""
Smart Cache Service for Data Collection

Implements intelligent caching to avoid re-collecting the same brand data
multiple times within a reasonable time window, improving performance significantly.
"""

import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from loguru import logger
from src.models.schemas import DataSource


class SmartCacheService:
    """Intelligent caching service for data collection results"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()
        # Cache TTL: 30 minutes for brand data, 15 minutes for news/social media
        self.default_ttl = timedelta(minutes=30)
        self.fast_changing_ttl = timedelta(minutes=15)
        self.fast_changing_sources = {DataSource.NEWS, DataSource.SOCIAL_MEDIA}
    
    def _generate_cache_key(self, brand_id: str, area_id: str, source: DataSource) -> str:
        """Generate a unique cache key for brand + area + source combination"""
        key_data = f"{brand_id.lower()}:{area_id.lower()}:{source.value}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_cached_data(
        self, 
        brand_id: str, 
        area_id: str, 
        source: DataSource
    ) -> Optional[Dict[str, Any]]:
        """Get cached data if available and not expired"""
        cache_key = self._generate_cache_key(brand_id, area_id, source)
        
        async with self._cache_lock:
            if cache_key not in self._cache:
                return None
            
            cached_entry = self._cache[cache_key]
            cached_time = cached_entry.get('timestamp')
            
            if not cached_time:
                # Invalid cache entry
                del self._cache[cache_key]
                return None
            
            # Check if cache is expired
            ttl = self.fast_changing_ttl if source in self.fast_changing_sources else self.default_ttl
            if datetime.utcnow() - cached_time > ttl:
                logger.info(f"Cache expired for {brand_id}:{source.value}, removing entry")
                del self._cache[cache_key]
                return None
            
            logger.info(f"Cache HIT for {brand_id}:{source.value} (age: {datetime.utcnow() - cached_time})")
            return cached_entry.get('data')
    
    async def store_cached_data(
        self, 
        brand_id: str, 
        area_id: str, 
        source: DataSource, 
        data: Dict[str, Any]
    ) -> None:
        """Store data in cache with timestamp"""
        cache_key = self._generate_cache_key(brand_id, area_id, source)
        
        async with self._cache_lock:
            self._cache[cache_key] = {
                'data': data,
                'timestamp': datetime.utcnow(),
                'brand_id': brand_id,
                'area_id': area_id,
                'source': source.value
            }
            
            logger.info(f"Cache STORE for {brand_id}:{source.value}")
    
    async def invalidate_brand_cache(self, brand_id: str) -> None:
        """Invalidate all cache entries for a specific brand"""
        brand_id_lower = brand_id.lower()
        
        async with self._cache_lock:
            keys_to_remove = [
                key for key, entry in self._cache.items()
                if entry.get('brand_id', '').lower() == brand_id_lower
            ]
            
            for key in keys_to_remove:
                del self._cache[key]
            
            if keys_to_remove:
                logger.info(f"Invalidated {len(keys_to_remove)} cache entries for brand {brand_id}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        async with self._cache_lock:
            total_entries = len(self._cache)
            expired_count = 0
            source_breakdown = {}
            
            now = datetime.utcnow()
            
            for entry in self._cache.values():
                source = entry.get('source', 'unknown')
                source_breakdown[source] = source_breakdown.get(source, 0) + 1
                
                cached_time = entry.get('timestamp')
                if cached_time:
                    source_enum = None
                    try:
                        source_enum = DataSource(source)
                    except ValueError:
                        continue
                    
                    ttl = self.fast_changing_ttl if source_enum in self.fast_changing_sources else self.default_ttl
                    if now - cached_time > ttl:
                        expired_count += 1
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_count,
                'active_entries': total_entries - expired_count,
                'source_breakdown': source_breakdown,
                'cache_efficiency': round((total_entries - expired_count) / max(total_entries, 1) * 100, 2)
            }
    
    async def cleanup_expired_entries(self) -> int:
        """Clean up expired cache entries and return count of removed entries"""
        removed_count = 0
        now = datetime.utcnow()
        
        async with self._cache_lock:
            keys_to_remove = []
            
            for key, entry in self._cache.items():
                cached_time = entry.get('timestamp')
                if not cached_time:
                    keys_to_remove.append(key)
                    continue
                
                source = entry.get('source')
                if not source:
                    keys_to_remove.append(key)
                    continue
                
                try:
                    source_enum = DataSource(source)
                    ttl = self.fast_changing_ttl if source_enum in self.fast_changing_sources else self.default_ttl
                    
                    if now - cached_time > ttl:
                        keys_to_remove.append(key)
                except ValueError:
                    # Invalid source, remove entry
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._cache[key]
                removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} expired cache entries")
        
        return removed_count


# Global cache service instance
cache_service = SmartCacheService() 
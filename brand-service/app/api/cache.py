from fastapi import APIRouter, HTTPException, Query
import logging
from typing import Optional, Dict, Any, List
from app.cache_service import BrandCacheService
from app.models import ErrorResponse

router = APIRouter(prefix="/api/v1/cache", tags=["cache"])
cache_service = BrandCacheService()
logger = logging.getLogger('brand_service.api')


@router.get(
    "/stats",
    summary="Get cache statistics",
    description="Retrieve statistics about the brand cache"
)
async def get_cache_stats():
    """Get cache statistics including total entries, brands, and file size"""
    try:
        stats = cache_service.get_cache_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to get cache stats", "details": str(e)}
        )


@router.delete(
    "/clear",
    summary="Clear all cache",
    description="Remove all cached brand search results"
)
async def clear_cache():
    """Clear all cached data"""
    try:
        cache_service.clear_cache()
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to clear cache", "details": str(e)}
        )


@router.delete(
    "/query/{query}",
    summary="Remove cached query",
    description="Remove cached results for a specific query"
)
async def remove_cached_query(query: str):
    """Remove cached data for a specific query"""
    try:
        removed = cache_service.remove_cached_query(query)
        if removed:
            return {
                "success": True,
                "message": f"Cached data for query '{query}' removed successfully"
            }
        else:
            return {
                "success": False,
                "message": f"No cached data found for query '{query}'"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to remove cached query", "details": str(e)}
        )


@router.get(
    "/search",
    summary="Search cache",
    description="Search through cached queries and brand data"
)
async def search_cache(
    q: str = Query(..., description="Search term to look for in cache")
):
    """Search through cached data"""
    try:
        results = cache_service.search_cache(q)
        return {
            "success": True,
            "data": results,
            "total_results": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to search cache", "details": str(e)}
        )


@router.post(
    "/export",
    summary="Export cache",
    description="Export cache data to a file"
)
async def export_cache(export_path: str = Query(..., description="Path to export the cache file")):
    """Export cache to a file"""
    try:
        cache_service.export_cache(export_path)
        return {
            "success": True,
            "message": f"Cache exported to {export_path}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to export cache", "details": str(e)}
        )


@router.post(
    "/import",
    summary="Import cache",
    description="Import cache data from a file"
)
async def import_cache(
    import_path: str = Query(..., description="Path to import the cache file from"),
    merge: bool = Query(True, description="Whether to merge with existing cache or replace it")
):
    """Import cache from a file"""
    try:
        cache_service.import_cache(import_path, merge)
        action = "merged with" if merge else "replaced"
        return {
            "success": True,
            "message": f"Cache {action} data from {import_path}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Failed to import cache", "details": str(e)}
        )

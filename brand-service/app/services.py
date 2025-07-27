from typing import List, Dict, Any
import logging
from app.models import Brand, Area, Competitor
from app.cache_service import BrandCacheService


class MockDataService:
    """Service for managing mock data"""
    
    @staticmethod
    def get_mock_brands() -> List[Brand]:
        """Return mock brand data"""
        return [
            Brand(
                id="oriental_bank_pr",
                name="Oriental Bank",
                full_name="Oriental Bank of Puerto Rico",
                industry="Banking",
                logo_url="https://example.com/oriental_bank_logo.png",
                description="Leading bank in Puerto Rico",
                confidence_score=0.95
            ),
            Brand(
                id="banco_popular_pr",
                name="Banco Popular",
                full_name="Banco Popular de Puerto Rico",
                industry="Banking",
                logo_url="https://example.com/banco_popular_logo.png",
                description="Major commercial bank in Puerto Rico",
                confidence_score=0.88
            ),
            Brand(
                id="first_bank_pr",
                name="First Bank",
                full_name="FirstBank Puerto Rico",
                industry="Banking",
                logo_url="https://example.com/first_bank_logo.png",
                description="Full-service commercial bank",
                confidence_score=0.82
            )
        ]
    
    @staticmethod
    def get_mock_areas() -> List[Area]:
        """Return mock area data"""
        return [
            Area(
                id="self_service_portal",
                name="Self Service Portal",
                description="Online banking and customer self-service capabilities",
                relevance_score=0.92,
                metrics=["user_experience", "feature_completeness", "security"]
            ),
            Area(
                id="employer_branding",
                name="Employer Branding",
                description="Company reputation as an employer",
                relevance_score=0.78,
                metrics=["employee_satisfaction", "compensation", "work_life_balance"]
            ),
            Area(
                id="mobile_banking",
                name="Mobile Banking",
                description="Mobile app experience and functionality",
                relevance_score=0.85,
                metrics=["app_rating", "download_count", "feature_set"]
            ),
            Area(
                id="customer_service",
                name="Customer Service",
                description="Quality of customer support and service",
                relevance_score=0.88,
                metrics=["response_time", "satisfaction_rating", "channel_availability"]
            )
        ]
    
    @staticmethod
    def get_mock_competitors() -> List[Competitor]:
        """Return mock competitor data"""
        return [
            Competitor(
                id="banco_popular",
                name="Banco Popular",
                logo_url="https://example.com/banco_popular_logo.png",
                industry="Banking",
                relevance_score=0.89,
                competition_level="direct"
            ),
            Competitor(
                id="first_bank",
                name="First Bank",
                logo_url="https://example.com/first_bank_logo.png",
                industry="Banking",
                relevance_score=0.76,
                competition_level="direct"
            ),
            Competitor(
                id="santander_pr",
                name="Santander Puerto Rico",
                logo_url="https://example.com/santander_logo.png",
                industry="Banking",
                relevance_score=0.71,
                competition_level="direct"
            )
        ]


class BrandService:
    """Service for brand-related operations"""
    
    def __init__(self):
        self.mock_data = MockDataService()
        self.cache_service = BrandCacheService()
        self.logger = logging.getLogger('brand_service')
        self.logger.info("BrandService initialized")
    
    def search_brands(self, query: str, limit: int = 10, use_cache: bool = True) -> List[Brand]:
        """Search for brands based on query"""
        self.logger.info(f"Brand search requested - Query: '{query}', Limit: {limit}, Use Cache: {use_cache}")
        
        # Try to get from cache first
        if use_cache:
            self.logger.debug("Attempting to retrieve results from cache")
            cached_result = self.cache_service.get_cached_search(query, limit)
            if cached_result:
                self.logger.info(f"Cache hit! Returning {len(cached_result['data'])} cached brands for query: '{query}'")
                # Convert dict data back to Brand objects
                cached_brands = [Brand(**brand_data) for brand_data in cached_result['data']]
                return cached_brands
        
        # If not in cache, perform search
        self.logger.info(f"Cache miss or cache disabled. Performing fresh search for query: '{query}'")
        brands = self.mock_data.get_mock_brands()
        
        # Simple text matching for mock implementation
        query_lower = query.lower()
        matching_brands = [
            brand for brand in brands 
            if query_lower in brand.name.lower() or 
               query_lower in brand.full_name.lower() or 
               query_lower in brand.description.lower()
        ]
        
        self.logger.debug(f"Found {len(matching_brands)} matching brands before applying limit")
        
        # Sort by confidence score descending
        matching_brands.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Apply limit
        result_brands = matching_brands[:limit]
        
        self.logger.info(f"Returning {len(result_brands)} brands after applying limit of {limit}")
        
        # Cache the results if we have any
        if use_cache and result_brands:
            self.logger.debug(f"Caching {len(result_brands)} results for query: '{query}'")
            response_data = {
                "query": query,
                "success": True,
                "data": [brand.model_dump() for brand in result_brands],
                "total_results": len(result_brands)
            }
            self.cache_service.cache_search_response(response_data)
        
        return result_brands
    
    def get_brand_areas(self, brand_id: str) -> List[Area]:
        """Get area suggestions for a brand"""
        self.logger.info(f"Getting brand areas for brand_id: '{brand_id}'")
        
        # For mock implementation, return all areas regardless of brand_id
        areas = self.mock_data.get_mock_areas()
        
        # Sort by relevance score descending
        areas.sort(key=lambda x: x.relevance_score, reverse=True)
        
        self.logger.info(f"Returning {len(areas)} areas for brand_id: '{brand_id}'")
        return areas
    
    def get_brand_competitors(self, brand_id: str, area_id: str = None) -> List[Competitor]:
        """Get competitors for a brand in a specific area"""
        self.logger.info(f"Getting competitors for brand_id: '{brand_id}', area_id: '{area_id}'")
        
        # For mock implementation, return competitors regardless of area_id
        competitors = self.mock_data.get_mock_competitors()
        
        # Filter out the brand itself if it appears in competitors
        competitors = [comp for comp in competitors if comp.id != brand_id]
        
        self.logger.debug(f"Filtered out brand itself, {len(competitors)} competitors remaining")
        
        # Sort by relevance score descending
        competitors.sort(key=lambda x: x.relevance_score, reverse=True)
        
        self.logger.info(f"Returning {len(competitors)} competitors for brand_id: '{brand_id}'")
        return competitors

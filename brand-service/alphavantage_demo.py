#!/usr/bin/env python3
"""
Alpha Vantage API Integration Demo

This script demonstrates the Alpha Vantage API integration by making real API calls.
"""
import asyncio
import sys
from app.logging_config import setup_logging
from app.alphavantage_service import AlphaVantageService
from app.cache_service import BrandCacheService


async def main():
    print("🚀 Alpha Vantage API Integration Demo")
    print("=" * 50)
    
    # Initialize logging
    setup_logging()
    print("✅ Logging initialized")
    
    # Initialize services
    print("🔧 Initializing Alpha Vantage service...")
    alphavantage_service = AlphaVantageService()
    cache_service = BrandCacheService()
    print()
    
    # Test queries
    test_queries = ["Apple", "Microsoft", "Banking", "Tesla"]
    
    for query in test_queries:
        print(f"📝 Testing query: '{query}'")
        print("-" * 30)
        
        try:
            # Check cache first
            print(f"🔍 Checking cache for '{query}'...")
            cached_result = cache_service.get_cached_search(query, limit=3)
            
            if cached_result:
                print(f"✅ Cache HIT! Found {len(cached_result['data'])} cached results")
                for brand in cached_result['data'][:2]:  # Show first 2
                    print(f"   - {brand['name']} ({brand['id']}) - Score: {brand['confidence_score']}")
            else:
                print(f"❌ Cache MISS - Making API call...")
                
                # Make real API call
                brands = await alphavantage_service.search_brands(query, limit=3)
                
                if brands:
                    print(f"✅ Found {len(brands)} brands from Alpha Vantage:")
                    for brand in brands[:2]:  # Show first 2
                        print(f"   - {brand.name} ({brand.id}) - Industry: {brand.industry}")
                        print(f"     Score: {brand.confidence_score}")
                        print(f"     Logo: {brand.logo_url}")
                    
                    # Create response for caching
                    brand_dicts = [
                        {
                            "id": brand.id,
                            "name": brand.name,
                            "full_name": brand.full_name,
                            "industry": brand.industry,
                            "logo_url": brand.logo_url,
                            "description": brand.description,
                            "confidence_score": brand.confidence_score
                        }
                        for brand in brands
                    ]
                    
                    response = {
                        "query": query,
                        "success": True,
                        "data": brand_dicts,
                        "total_results": len(brand_dicts)
                    }
                    
                    # Cache the response
                    cache_service.cache_search_response(response)
                    print(f"💾 Results cached for future queries")
                else:
                    print(f"❌ No brands found for query: '{query}'")
        
        except Exception as e:
            print(f"❌ Error processing query '{query}': {str(e)}")
        
        print()
        # Small delay between queries to be respectful to the API
        await asyncio.sleep(1)
    
    # Show final cache stats
    print("📊 Final Cache Statistics:")
    print("-" * 25)
    stats = cache_service.get_cache_stats()
    print(f"Total entries: {stats['total_entries']}")
    print(f"Total brands: {stats['total_brands']}")
    print(f"Cached queries: {', '.join(stats['queries'])}")
    
    print()
    print("🎉 Demo completed!")
    print("💡 Tip: Run the demo again to see cache hits in action!")


if __name__ == "__main__":
    print("⚠️  This demo makes real API calls to Alpha Vantage.")
    print("🔑 Make sure you have a valid API key configured.")
    print("⏳ The demo may take a few moments due to API rate limits.")
    print()
    
    response = input("Do you want to continue? (y/N): ")
    if response.lower() in ['y', 'yes']:
        asyncio.run(main())
    else:
        print("Demo cancelled.")
        sys.exit(0)

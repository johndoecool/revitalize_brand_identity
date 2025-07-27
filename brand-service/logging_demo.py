#!/usr/bin/env python3
"""
Logging Demo Script

This script demonstrates the logging functionality of the brand service
by performing various operations and showing how they are logged.
"""
import sys
import os
import time
from app.logging_config import setup_logging
from app.services import BrandService
from app.cache_service import BrandCacheService


def main():
    print("🚀 Brand Service Logging Demo")
    print("=" * 50)
    
    # Initialize logging
    setup_logging()
    print("✅ Logging initialized")
    print("📂 Log files will be created in the 'logs' directory")
    print()
    
    # Initialize services
    print("🔧 Initializing services...")
    brand_service = BrandService()
    cache_service = BrandCacheService()
    print()
    
    # Demo 1: Brand search with cache miss
    print("📝 Demo 1: Brand search (Cache MISS)")
    print("-" * 30)
    query1 = "Oriental Bank"
    print(f"Searching for: '{query1}'")
    results1 = brand_service.search_brands(query1, limit=5)
    print(f"✅ Found {len(results1)} results")
    print("📋 Check logs for cache MISS entries")
    print()
    
    time.sleep(1)
    
    # Demo 2: Same search with cache hit
    print("📝 Demo 2: Same brand search (Cache HIT)")
    print("-" * 30)
    print(f"Searching for: '{query1}' again")
    results2 = brand_service.search_brands(query1, limit=5)
    print(f"✅ Found {len(results2)} results (from cache)")
    print("📋 Check logs for cache HIT entries")
    print()
    
    time.sleep(1)
    
    # Demo 3: Different search
    print("📝 Demo 3: Different brand search")
    print("-" * 30)
    query2 = "Bank"
    print(f"Searching for: '{query2}'")
    results3 = brand_service.search_brands(query2, limit=3)
    print(f"✅ Found {len(results3)} results")
    print()
    
    time.sleep(1)
    
    # Demo 4: Get brand areas
    print("📝 Demo 4: Get brand areas")
    print("-" * 30)
    brand_id = "oriental_bank_pr"
    print(f"Getting areas for brand: '{brand_id}'")
    areas = brand_service.get_brand_areas(brand_id)
    print(f"✅ Found {len(areas)} areas")
    print()
    
    time.sleep(1)
    
    # Demo 5: Get competitors
    print("📝 Demo 5: Get brand competitors")
    print("-" * 30)
    print(f"Getting competitors for brand: '{brand_id}'")
    competitors = brand_service.get_brand_competitors(brand_id)
    print(f"✅ Found {len(competitors)} competitors")
    print()
    
    time.sleep(1)
    
    # Demo 6: Cache operations
    print("📝 Demo 6: Cache management")
    print("-" * 30)
    stats = cache_service.get_cache_stats()
    print(f"Cache stats: {stats['total_entries']} entries, {stats['total_brands']} brands")
    
    # Search cache
    search_results = cache_service.search_cache("Bank")
    print(f"Cache search for 'Bank': {len(search_results)} results")
    print()
    
    # Show log files
    print("📁 Log Files Created:")
    print("-" * 20)
    logs_dir = "logs"
    if os.path.exists(logs_dir):
        for file in os.listdir(logs_dir):
            if file.endswith('.log'):
                file_path = os.path.join(logs_dir, file)
                size = os.path.getsize(file_path)
                print(f"📄 {file} ({size} bytes)")
    else:
        print("❌ Logs directory not found")
    
    print()
    print("🎉 Demo completed!")
    print("📋 Check the log files in the 'logs' directory to see detailed logging:")
    print("   - brand-service-*.log: General application logs")
    print("   - brand-service-cache.log: Cache-specific logs (JSON format)")
    print("   - brand-service-api.log: API request logs (JSON format)")
    print("   - brand-service-errors.log: Error logs only")


if __name__ == "__main__":
    main()

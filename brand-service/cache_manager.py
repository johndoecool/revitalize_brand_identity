#!/usr/bin/env python3
"""
Brand Cache Management Utility

This script provides command-line tools to manage the brand cache.
"""
import argparse
import json
import sys
import os
from app.cache_service import BrandCacheService
from app.models import Brand


def main():
    parser = argparse.ArgumentParser(description="Brand Cache Management Utility")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show cache statistics")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear all cache")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search cache")
    search_parser.add_argument("term", help="Search term")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove cached query")
    remove_parser.add_argument("query", help="Query to remove")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export cache to file")
    export_parser.add_argument("file", help="Export file path")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import cache from file")
    import_parser.add_argument("file", help="Import file path")
    import_parser.add_argument("--merge", action="store_true", help="Merge with existing cache")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add brand data to cache")
    add_parser.add_argument("query", help="Search query")
    add_parser.add_argument("--brands-json", help="JSON file containing brand data")
    add_parser.add_argument("--brand-id", help="Brand ID")
    add_parser.add_argument("--brand-name", help="Brand name")
    add_parser.add_argument("--brand-full-name", help="Brand full name")
    add_parser.add_argument("--brand-industry", help="Brand industry")
    add_parser.add_argument("--brand-logo-url", help="Brand logo URL")
    add_parser.add_argument("--brand-description", help="Brand description")
    add_parser.add_argument("--brand-confidence", type=float, default=1.0, help="Brand confidence score")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all cached queries")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize cache service
    cache_service = BrandCacheService()
    
    try:
        if args.command == "stats":
            stats = cache_service.get_cache_stats()
            print("Cache Statistics:")
            print(f"  Total entries: {stats['total_entries']}")
            print(f"  Total brands: {stats['total_brands']}")
            print(f"  Cache file size: {stats['cache_file_size_bytes']} bytes")
            print(f"  Queries: {', '.join(stats['queries'])}")
        
        elif args.command == "clear":
            cache_service.clear_cache()
            print("Cache cleared successfully")
        
        elif args.command == "search":
            results = cache_service.search_cache(args.term)
            print(f"Found {len(results)} results for '{args.term}':")
            for result in results:
                if result["type"] == "query":
                    print(f"  Query: {result['match']}")
                else:
                    print(f"  Brand: {result['match']} (from query: {result['query']})")
        
        elif args.command == "remove":
            removed = cache_service.remove_cached_query(args.query)
            if removed:
                print(f"Removed cached data for query '{args.query}'")
            else:
                print(f"No cached data found for query '{args.query}'")
        
        elif args.command == "export":
            cache_service.export_cache(args.file)
            print(f"Cache exported to {args.file}")
        
        elif args.command == "import":
            cache_service.import_cache(args.file, args.merge)
            action = "merged with" if args.merge else "replaced"
            print(f"Cache {action} data from {args.file}")
        
        elif args.command == "add":
            brands = []
            
            if args.brands_json:
                # Load brands from JSON file
                with open(args.brands_json, 'r') as f:
                    brands_data = json.load(f)
                    for brand_data in brands_data:
                        brands.append(Brand(**brand_data))
            elif args.brand_id:
                # Create single brand from command line args
                brand = Brand(
                    id=args.brand_id,
                    name=args.brand_name or args.brand_id,
                    full_name=args.brand_full_name or args.brand_name or args.brand_id,
                    industry=args.brand_industry or "Unknown",
                    logo_url=args.brand_logo_url or "",
                    description=args.brand_description or "",
                    confidence_score=args.brand_confidence
                )
                brands.append(brand)
            else:
                print("Error: Must provide either --brands-json or --brand-id")
                return
            
            cache_service.cache_search_results(args.query, brands, len(brands))
            print(f"Added {len(brands)} brand(s) to cache for query '{args.query}'")
        
        elif args.command == "list":
            stats = cache_service.get_cache_stats()
            if stats['queries']:
                print("Cached queries:")
                for i, query in enumerate(stats['queries'], 1):
                    print(f"  {i}. {query}")
            else:
                print("No cached queries found")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

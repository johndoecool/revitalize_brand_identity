#!/usr/bin/env python3
"""
Quick SSL Test - Minimal test to identify SSL issues
"""

import asyncio
import sys
import os
import ssl
import aiohttp
from loguru import logger

async def test_direct_ssl_disabled():
    """Test direct aiohttp request with SSL disabled"""
    logger.info("🔍 Testing direct SSL-disabled request")
    
    try:
        # Create SSL context with all verification disabled
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with SSL completely disabled
        connector = aiohttp.TCPConnector(
            verify_ssl=False,
            ssl_context=ssl_context,
            limit=10
        )
        
        timeout = aiohttp.ClientTimeout(total=15)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            
            url = "https://m.facebook.com/cognizant"
            logger.info(f"Testing: {url}")
            
            async with session.get(url) as response:
                logger.success(f"✅ SUCCESS: Status {response.status}")
                content = await response.text()
                logger.info(f"Content length: {len(content)}")
                
                if 'login' in content.lower():
                    logger.info("📋 Got Facebook login page")
                    
                return True
                
    except Exception as e:
        logger.error(f"❌ FAILED: {str(e)}")
        return False

async def test_with_scraper_imports():
    """Test using our scraper modules"""
    logger.info("\n🕷️  Testing with scraper modules")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from scrapers.scraper_config import ScraperConfig
        from scrapers.web_scraper import WebScraper
        
        # Create config
        config = ScraperConfig(
            verify_ssl=True,  # This should be overridden for Facebook
            disable_ssl_for_domains=['facebook.com', 'm.facebook.com']
        )
        
        logger.info("✅ Imported scraper modules")
        logger.info(f"Config disable domains: {config.disable_ssl_for_domains}")
        
        # Test the scraper
        async with WebScraper(config) as scraper:
            url = "https://m.facebook.com/cognizant"
            
            # Check domain detection
            should_disable = scraper._should_disable_ssl(url)
            logger.info(f"SSL should be disabled: {should_disable}")
            
            if not should_disable:
                logger.error("❌ Domain detection failed - SSL won't be disabled")
                return False
            
            # Try scraping
            result = await scraper.scrape_url(url)
            
            if result.success:
                logger.success(f"✅ Scraper SUCCESS: Status {result.status_code}")
                logger.info(f"Content length: {len(result.content) if result.content else 0}")
                return True
            else:
                logger.error(f"❌ Scraper FAILED: {result.error}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Scraper test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    logger.info("🚀 Quick SSL Test")
    logger.info("=" * 20)
    
    # Test 1: Direct aiohttp with SSL disabled
    direct_ok = await test_direct_ssl_disabled()
    
    # Test 2: Using our scraper modules  
    scraper_ok = await test_with_scraper_imports()
    
    logger.info("\n📊 Results:")
    logger.info(f"Direct SSL-disabled request: {'✅ PASS' if direct_ok else '❌ FAIL'}")
    logger.info(f"Scraper module test: {'✅ PASS' if scraper_ok else '❌ FAIL'}")
    
    if direct_ok and not scraper_ok:
        logger.warning("⚠️  Direct request works but scraper fails - issue is in scraper code")
    elif not direct_ok:
        logger.error("❌ Even direct SSL-disabled requests fail - system SSL issue")
    else:
        logger.success("✅ Both tests pass - SSL fix should be working")

if __name__ == "__main__":
    asyncio.run(main()) 
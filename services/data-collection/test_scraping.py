#!/usr/bin/env python3
"""
Test script for web scraping functionality
Run this to verify that Facebook and LinkedIn scraping works correctly
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_social_media_scraping():
    """Test the social media scraping functionality"""
    
    try:
        from src.collectors.social_media_collector import SocialMediaCollector
        from src.config.scraping_config import print_scraping_status
        
        print("🕷️  Testing Social Media Web Scraping")
        print("=" * 50)
        
        # Show scraping configuration status
        print_scraping_status()
        print("\n" + "=" * 50)
        
        # Test brands
        test_brands = [
            ("Microsoft", "Test brand with strong social presence"),
            ("Starbucks", "Test brand with active social media"),
            ("Tesla", "Test brand with high social engagement")
        ]
        
        collector = SocialMediaCollector()
        
        async with collector:
            for brand_name, description in test_brands:
                print(f"\n🔍 Testing scraping for: {brand_name}")
                print(f"   Description: {description}")
                print("-" * 40)
                
                try:
                    # Test Facebook scraping
                    print("📘 Testing Facebook scraping...")
                    facebook_data = await collector._scrape_facebook_page(brand_name)
                    
                    if facebook_data:
                        print(f"   ✅ Facebook: Found {facebook_data['mentions']} mentions")
                        print(f"   📊 Sentiment: {facebook_data['sentiment']:.2f}")
                        print(f"   📝 Posts: {len(facebook_data['posts'])} found")
                    else:
                        print("   ❌ Facebook scraping failed - using fallback")
                    
                    # Test LinkedIn scraping
                    print("🔗 Testing LinkedIn scraping...")
                    linkedin_data = await collector._scrape_linkedin_company(brand_name)
                    
                    if linkedin_data:
                        print(f"   ✅ LinkedIn: Found {linkedin_data['mentions']} followers")
                        print(f"   📊 Sentiment: {linkedin_data['sentiment']:.2f}")
                        print(f"   📝 Posts: {len(linkedin_data['posts'])} found")
                    else:
                        print("   ❌ LinkedIn scraping failed - using fallback")
                    
                    # Test complete social media collection
                    print("🌐 Testing complete social media collection...")
                    complete_data = await collector.collect_brand_data(brand_name, "test_area")
                    
                    print(f"   ✅ Complete data collected successfully")
                    print(f"   📊 Overall sentiment: {complete_data['overall_sentiment']:.2f}")
                    print(f"   📈 Total mentions: {complete_data['mentions_count']}")
                    print(f"   🚀 Engagement rate: {complete_data['engagement_rate']:.3f}")
                    
                except Exception as e:
                    print(f"   ❌ Error testing {brand_name}: {str(e)}")
                
                # Add delay between brands to be respectful
                await asyncio.sleep(2)
        
        print("\n" + "=" * 50)
        print("🎉 Web scraping test completed!")
        print("\n💡 Notes:")
        print("- If scraping fails, the service will use mock data")
        print("- Social media platforms may block requests - this is normal")
        print("- For production, consider using official APIs when available")
        print("- Always respect platform Terms of Service")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_dependencies():
    """Test if all scraping dependencies are available"""
    print("🔍 Checking Web Scraping Dependencies")
    print("=" * 40)
    
    dependencies = {
        "BeautifulSoup": ("bs4", "pip install beautifulsoup4"),
        "lxml": ("lxml", "pip install lxml"),
        "Selenium": ("selenium", "pip install selenium"),
        "Requests": ("requests", "pip install requests"),
        "aiohttp": ("aiohttp", "pip install aiohttp")
    }
    
    missing_deps = []
    
    for name, (module, install_cmd) in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name}: Available")
        except ImportError:
            print(f"❌ {name}: Missing - {install_cmd}")
            missing_deps.append(name)
    
    # Test ChromeDriver for Selenium
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("✅ ChromeDriver: Available")
    except Exception as e:
        print(f"❌ ChromeDriver: Missing - {str(e)}")
        missing_deps.append("ChromeDriver")
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Install missing dependencies before running scraping tests")
        return False
    else:
        print("\n🎉 All dependencies are available!")
        return True

async def main():
    """Main test function"""
    print("🕷️  Social Media Web Scraping Test Suite")
    print("=" * 60)
    
    print("\n1️⃣  Testing Dependencies...")
    if not test_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    print("\n2️⃣  Testing Web Scraping Functionality...")
    await test_social_media_scraping()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}") 
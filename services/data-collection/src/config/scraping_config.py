"""
Web Scraping Configuration for Social Media Platforms
"""

from typing import Dict, Any, List
from pydantic import BaseSettings


class ScrapingConfig(BaseSettings):
    """Configuration for web scraping social media platforms"""
    
    # Enable/disable scraping for each platform
    enable_facebook_scraping: bool = True
    enable_linkedin_scraping: bool = True
    
    # Scraping method preferences (basic, selenium, or both)
    facebook_scraping_method: str = "basic"  # "basic", "selenium", "both"
    linkedin_scraping_method: str = "basic"  # "basic", "selenium", "both"
    
    # Rate limiting for scraping
    scraping_delay_seconds: float = 1.0
    max_scraping_retries: int = 3
    
    # User agents for different platforms
    facebook_user_agent: str = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
    linkedin_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Selenium configuration
    selenium_headless: bool = True
    selenium_timeout: int = 10
    
    class Config:
        env_prefix = "SCRAPING_"


# Platform-specific scraping capabilities
PLATFORM_CAPABILITIES = {
    "facebook": {
        "basic_scraping": {
            "can_get_page_info": True,
            "can_get_follower_count": False,  # Limited without JavaScript
            "can_get_posts": False,  # Requires JavaScript/login
            "can_get_sentiment": True,
            "requires_mobile_version": True
        },
        "selenium_scraping": {
            "can_get_page_info": True,
            "can_get_follower_count": True,
            "can_get_posts": True,
            "can_get_sentiment": True,
            "requires_mobile_version": False
        }
    },
    "linkedin": {
        "basic_scraping": {
            "can_get_company_info": True,
            "can_get_follower_count": True,
            "can_get_posts": False,  # Limited without JavaScript
            "can_get_sentiment": True,
            "requires_login": False
        },
        "selenium_scraping": {
            "can_get_company_info": True,
            "can_get_follower_count": True,
            "can_get_posts": True,
            "can_get_sentiment": True,
            "requires_login": True  # For full access
        }
    }
}

# Required dependencies for scraping
SCRAPING_DEPENDENCIES = {
    "basic": ["beautifulsoup4", "lxml", "requests", "aiohttp"],
    "selenium": ["selenium", "webdriver-manager"]
}

# Installation instructions
INSTALLATION_INSTRUCTIONS = """
Web Scraping Setup Instructions:

1. Basic Scraping (BeautifulSoup):
   pip install beautifulsoup4 lxml

2. Advanced Scraping (Selenium):
   pip install selenium webdriver-manager
   
   # Install Chrome browser or ChromeDriver
   # For Ubuntu/Debian:
   sudo apt-get install google-chrome-stable
   
   # For Windows/Mac:
   Download Chrome from https://www.google.com/chrome/

3. Environment Variables:
   Add to your .env file:
   
   SCRAPING_ENABLE_FACEBOOK_SCRAPING=true
   SCRAPING_ENABLE_LINKEDIN_SCRAPING=true
   SCRAPING_FACEBOOK_SCRAPING_METHOD=basic
   SCRAPING_LINKEDIN_SCRAPING_METHOD=basic
   SCRAPING_DELAY_SECONDS=1.0

Important Notes:
- Web scraping social media platforms may violate their Terms of Service
- Some platforms (like Facebook) heavily restrict scraping and require JavaScript
- LinkedIn requires proper rate limiting to avoid being blocked
- For production use, prefer official APIs when available
- Always respect robots.txt and platform policies
"""

def get_scraping_config() -> ScrapingConfig:
    """Get the current scraping configuration"""
    return ScrapingConfig()

def check_scraping_dependencies() -> Dict[str, bool]:
    """Check if scraping dependencies are installed"""
    dependencies_status = {}
    
    # Check basic dependencies
    try:
        import bs4
        dependencies_status["beautifulsoup4"] = True
    except ImportError:
        dependencies_status["beautifulsoup4"] = False
    
    try:
        import lxml
        dependencies_status["lxml"] = True
    except ImportError:
        dependencies_status["lxml"] = False
    
    # Check Selenium dependencies
    try:
        import selenium
        dependencies_status["selenium"] = True
    except ImportError:
        dependencies_status["selenium"] = False
    
    try:
        from selenium import webdriver
        # Try to create a Chrome driver to check if ChromeDriver is available
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        driver.quit()
        dependencies_status["chromedriver"] = True
    except Exception:
        dependencies_status["chromedriver"] = False
    
    return dependencies_status

def print_scraping_status():
    """Print the current status of scraping capabilities"""
    config = get_scraping_config()
    dependencies = check_scraping_dependencies()
    
    print("🕷️  Web Scraping Configuration Status")
    print("=" * 40)
    
    print(f"Facebook Scraping: {'✅' if config.enable_facebook_scraping else '❌'}")
    print(f"LinkedIn Scraping: {'✅' if config.enable_linkedin_scraping else '❌'}")
    print(f"Scraping Delay: {config.scraping_delay_seconds}s")
    
    print("\n📦 Dependencies Status:")
    for dep, status in dependencies.items():
        print(f"  {dep}: {'✅' if status else '❌'}")
    
    missing_deps = [dep for dep, status in dependencies.items() if not status]
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Run installation commands from scraping_config.py")
    else:
        print("\n🎉 All scraping dependencies are installed!")

if __name__ == "__main__":
    print(INSTALLATION_INSTRUCTIONS)
    print_scraping_status() 
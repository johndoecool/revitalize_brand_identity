"""
Web Scraper Configuration

Defines configuration classes and strategies for different types of web scraping.
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

class ScrapingStrategy(Enum):
    """Different scraping strategies available"""
    BASIC_HTTP = "basic_http"
    SELENIUM_HEADLESS = "selenium_headless" 
    SELENIUM_FULL = "selenium_full"
    REQUESTS_SESSION = "requests_session"
    MOBILE_USER_AGENT = "mobile_user_agent"

class ContentType(Enum):
    """Types of content to extract"""
    HTML = "html"
    JSON = "json"
    TEXT = "text"
    MIXED = "mixed"

@dataclass
class ScraperConfig:
    """Configuration for web scraping operations"""
    
    # Basic settings
    max_retries: int = 3
    timeout: int = 15
    delay_between_requests: float = 1.0
    
    # HTTP settings
    user_agents: List[str] = None
    headers: Dict[str, str] = None
    cookies: Dict[str, str] = None
    
    # Selenium settings
    headless: bool = True
    window_size: tuple = (1920, 1080)
    chrome_options: List[str] = None
    
    # Content settings
    expected_content_type: ContentType = ContentType.HTML
    follow_redirects: bool = True
    verify_ssl: bool = True
    # SSL handling for problematic sites
    disable_ssl_for_domains: List[str] = None
    
    # Rate limiting
    rate_limit_delay: float = 0.5
    concurrent_requests: int = 1
    
    def __post_init__(self):
        """Set default values after initialization"""
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0'
            ]
        
        if self.headers is None:
            self.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        
        # Domains with known SSL issues - disable SSL verification for these
        if self.disable_ssl_for_domains is None:
            self.disable_ssl_for_domains = [
                'facebook.com',
                'm.facebook.com',
                'web.facebook.com',
                'touch.facebook.com',
                'linkedin.com',
                'www.linkedin.com',
                'm.linkedin.com',
                'mobile.linkedin.com'
            ]
        
        if self.chrome_options is None:
            self.chrome_options = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-logging',
                '--disable-web-security',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--ignore-certificate-errors-spki-list',  
                '--ignore-certificate-errors-sp-list',
                '--allow-running-insecure-content',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-component-extensions-with-background-pages',
                '--disable-background-networking',
                '--disable-sync',
                '--metrics-recording-only',
                '--disable-default-apps',
                '--no-first-run',
                '--disable-cloud-policy-on-signin',
                '--log-level=3'
            ]

@dataclass
class SiteConfig:
    """Configuration for specific websites"""
    
    name: str
    base_urls: List[str]
    url_patterns: List[str]
    scraping_strategy: ScrapingStrategy
    
    # CSS/XPath selectors for common elements
    selectors: Dict[str, str] = None
    
    # Site-specific settings
    requires_login: bool = False
    has_anti_bot: bool = False
    javascript_required: bool = False
    
    # Rate limiting for this specific site
    custom_delay: Optional[float] = None
    
    def __post_init__(self):
        """Set default selectors"""
        if self.selectors is None:
            self.selectors = {
                'title': 'title, h1, .title, [data-testid="title"]',
                'content': 'article, .content, .post, .entry, main',
                'meta_description': 'meta[name="description"]',
                'links': 'a[href]',
                'images': 'img[src]'
            }

# Predefined configurations for popular websites
SITE_CONFIGS = {
    'facebook': SiteConfig(
        name='Facebook',
        base_urls=['https://www.facebook.com', 'https://m.facebook.com'],
        url_patterns=[
            'facebook.com/{handle}',
            'facebook.com/pages/{handle}',
            'm.facebook.com/{handle}'
        ],
        scraping_strategy=ScrapingStrategy.BASIC_HTTP,
        has_anti_bot=True,
        javascript_required=True,
        selectors={
            'title': 'title, h1, [role="main"] h1',
            'follower_count': '[aria-label*="follower"], [aria-label*="like"]',
            'posts': '[data-testid="post"], .userContentWrapper',
            'post_text': '[data-testid="post_message"], .userContent'
        }
    ),
    
    'linkedin': SiteConfig(
        name='LinkedIn',
        base_urls=['https://www.linkedin.com'],
        url_patterns=[
            'linkedin.com/company/{handle}',
            'linkedin.com/in/{handle}'
        ],
        scraping_strategy=ScrapingStrategy.BASIC_HTTP,
        has_anti_bot=True,
        javascript_required=True,
        selectors={
            'title': 'title, h1, .org-top-card-summary__title',
            'follower_count': '.org-top-card-summary__follower-count, [aria-label*="follower"]',
            'posts': '.feed-shared-update-v2, .occludable-update',
            'company_info': '.org-top-card-summary-info-list'
        }
    ),
    
    'twitter': SiteConfig(
        name='Twitter/X',
        base_urls=['https://twitter.com', 'https://x.com'],
        url_patterns=[
            'twitter.com/{handle}',
            'x.com/{handle}'
        ],
        scraping_strategy=ScrapingStrategy.SELENIUM_HEADLESS,
        has_anti_bot=True,
        javascript_required=True,
        selectors={
            'title': 'title, [data-testid="UserName"]',
            'follower_count': '[data-testid="UserFollowers"] span',
            'posts': '[data-testid="tweet"]',
            'post_text': '[data-testid="tweetText"]'
        }
    ),
    
    'generic_news': SiteConfig(
        name='Generic News Site',
        base_urls=[],
        url_patterns=['*'],
        scraping_strategy=ScrapingStrategy.BASIC_HTTP,
        selectors={
            'title': 'title, h1, .headline, .article-title',
            'content': 'article, .article-content, .post-content, .entry-content',
            'author': '.author, .byline, [rel="author"]',
            'date': '.date, .publish-date, time[datetime]',
            'meta_description': 'meta[name="description"]'
        }
    )
} 
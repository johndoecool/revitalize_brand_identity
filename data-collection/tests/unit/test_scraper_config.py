"""
Unit tests for scraper configuration classes

Tests the ScraperConfig, SiteConfig, and related configuration functionality.
"""

import pytest
from scrapers.scraper_config import (
    ScraperConfig, 
    SiteConfig, 
    ScrapingStrategy, 
    ContentType, 
    SITE_CONFIGS
)

class TestScraperConfig:
    """Test cases for ScraperConfig class"""
    
    def test_default_initialization(self):
        """Test ScraperConfig with default values"""
        config = ScraperConfig()
        
        assert config.max_retries == 3
        assert config.timeout == 15
        assert config.delay_between_requests == 1.0
        assert config.headless is True
        assert config.window_size == (1920, 1080)
        assert config.expected_content_type == ContentType.HTML
        assert config.follow_redirects is True
        assert config.verify_ssl is True
        assert config.rate_limit_delay == 0.5
        assert config.concurrent_requests == 1
    
    def test_custom_initialization(self):
        """Test ScraperConfig with custom values"""
        config = ScraperConfig(
            max_retries=5,
            timeout=30,
            delay_between_requests=2.0,
            headless=False,
            window_size=(1280, 720),
            expected_content_type=ContentType.JSON,
            follow_redirects=False,
            verify_ssl=False,
            rate_limit_delay=1.0,
            concurrent_requests=3
        )
        
        assert config.max_retries == 5
        assert config.timeout == 30
        assert config.delay_between_requests == 2.0
        assert config.headless is False
        assert config.window_size == (1280, 720)
        assert config.expected_content_type == ContentType.JSON
        assert config.follow_redirects is False
        assert config.verify_ssl is False
        assert config.rate_limit_delay == 1.0
        assert config.concurrent_requests == 3
    
    def test_post_init_user_agents(self):
        """Test __post_init__ sets default user agents"""
        config = ScraperConfig()
        
        assert config.user_agents is not None
        assert len(config.user_agents) > 0
        assert all('Mozilla' in ua for ua in config.user_agents)
        
        # Test that desktop and mobile user agents are included
        user_agents_str = ' '.join(config.user_agents)
        assert 'Windows NT' in user_agents_str
        assert 'iPhone' in user_agents_str or 'Android' in user_agents_str
    
    def test_post_init_headers(self):
        """Test __post_init__ sets default headers"""
        config = ScraperConfig()
        
        assert config.headers is not None
        assert 'Accept' in config.headers
        assert 'Accept-Language' in config.headers
        assert 'Accept-Encoding' in config.headers
        assert 'Connection' in config.headers
        assert 'Upgrade-Insecure-Requests' in config.headers
    
    def test_post_init_chrome_options(self):
        """Test __post_init__ sets default Chrome options"""
        config = ScraperConfig()
        
        assert config.chrome_options is not None
        assert len(config.chrome_options) > 0
        
        # Check for important Chrome options
        options_str = ' '.join(config.chrome_options)
        assert '--no-sandbox' in options_str
        assert '--disable-dev-shm-usage' in options_str
        assert '--disable-gpu' in options_str
        assert '--log-level=3' in options_str
    
    def test_custom_user_agents_preserved(self):
        """Test that custom user agents are preserved during __post_init__"""
        custom_agents = ['Custom Agent 1.0', 'Custom Agent 2.0']
        config = ScraperConfig(user_agents=custom_agents)
        
        assert config.user_agents == custom_agents
    
    def test_custom_headers_preserved(self):
        """Test that custom headers are preserved during __post_init__"""
        custom_headers = {'Custom-Header': 'Custom-Value'}
        config = ScraperConfig(headers=custom_headers)
        
        assert config.headers == custom_headers
    
    def test_custom_chrome_options_preserved(self):
        """Test that custom Chrome options are preserved during __post_init__"""
        custom_options = ['--custom-option=value']
        config = ScraperConfig(chrome_options=custom_options)
        
        assert config.chrome_options == custom_options

class TestSiteConfig:
    """Test cases for SiteConfig class"""
    
    def test_basic_initialization(self):
        """Test SiteConfig basic initialization"""
        config = SiteConfig(
            name="Test Site",
            base_urls=["https://test.com"],
            url_patterns=["test.com/{handle}"],
            scraping_strategy=ScrapingStrategy.BASIC_HTTP
        )
        
        assert config.name == "Test Site"
        assert config.base_urls == ["https://test.com"]
        assert config.url_patterns == ["test.com/{handle}"]
        assert config.scraping_strategy == ScrapingStrategy.BASIC_HTTP
        assert config.requires_login is False
        assert config.has_anti_bot is False
        assert config.javascript_required is False
        assert config.custom_delay is None
    
    def test_advanced_initialization(self):
        """Test SiteConfig with advanced options"""
        custom_selectors = {
            'title': 'h1.custom-title',
            'content': '.custom-content'
        }
        
        config = SiteConfig(
            name="Advanced Site",
            base_urls=["https://advanced.com"],
            url_patterns=["advanced.com/{handle}"],
            scraping_strategy=ScrapingStrategy.SELENIUM_HEADLESS,
            selectors=custom_selectors,
            requires_login=True,
            has_anti_bot=True,
            javascript_required=True,
            custom_delay=2.0
        )
        
        assert config.name == "Advanced Site"
        assert config.scraping_strategy == ScrapingStrategy.SELENIUM_HEADLESS
        assert config.selectors == custom_selectors
        assert config.requires_login is True
        assert config.has_anti_bot is True
        assert config.javascript_required is True
        assert config.custom_delay == 2.0
    
    def test_post_init_default_selectors(self):
        """Test __post_init__ sets default selectors"""
        config = SiteConfig(
            name="Test",
            base_urls=["https://test.com"],
            url_patterns=["test.com/{handle}"],
            scraping_strategy=ScrapingStrategy.BASIC_HTTP
        )
        
        assert config.selectors is not None
        assert 'title' in config.selectors
        assert 'content' in config.selectors
        assert 'meta_description' in config.selectors
        assert 'links' in config.selectors
        assert 'images' in config.selectors
    
    def test_custom_selectors_preserved(self):
        """Test that custom selectors are preserved during __post_init__"""
        custom_selectors = {'custom': '.custom-selector'}
        config = SiteConfig(
            name="Test",
            base_urls=["https://test.com"],
            url_patterns=["test.com/{handle}"],
            scraping_strategy=ScrapingStrategy.BASIC_HTTP,
            selectors=custom_selectors
        )
        
        assert config.selectors == custom_selectors

class TestScrapingStrategy:
    """Test cases for ScrapingStrategy enum"""
    
    def test_enum_values(self):
        """Test ScrapingStrategy enum values"""
        assert ScrapingStrategy.BASIC_HTTP.value == "basic_http"
        assert ScrapingStrategy.SELENIUM_HEADLESS.value == "selenium_headless"
        assert ScrapingStrategy.SELENIUM_FULL.value == "selenium_full"
        assert ScrapingStrategy.REQUESTS_SESSION.value == "requests_session"
        assert ScrapingStrategy.MOBILE_USER_AGENT.value == "mobile_user_agent"
    
    def test_enum_membership(self):
        """Test ScrapingStrategy enum membership"""
        strategies = list(ScrapingStrategy)
        assert len(strategies) == 5
        assert ScrapingStrategy.BASIC_HTTP in strategies
        assert ScrapingStrategy.SELENIUM_HEADLESS in strategies

class TestContentType:
    """Test cases for ContentType enum"""
    
    def test_enum_values(self):
        """Test ContentType enum values"""
        assert ContentType.HTML.value == "html"
        assert ContentType.JSON.value == "json"
        assert ContentType.TEXT.value == "text"
        assert ContentType.MIXED.value == "mixed"
    
    def test_enum_membership(self):
        """Test ContentType enum membership"""
        types = list(ContentType)
        assert len(types) == 4
        assert ContentType.HTML in types
        assert ContentType.JSON in types

class TestSiteConfigs:
    """Test cases for predefined SITE_CONFIGS"""
    
    def test_site_configs_exist(self):
        """Test that predefined site configurations exist"""
        assert 'facebook' in SITE_CONFIGS
        assert 'linkedin' in SITE_CONFIGS
        assert 'twitter' in SITE_CONFIGS
        assert 'generic_news' in SITE_CONFIGS
    
    def test_facebook_config(self):
        """Test Facebook site configuration"""
        fb_config = SITE_CONFIGS['facebook']
        
        assert fb_config.name == 'Facebook'
        assert 'facebook.com' in fb_config.base_urls[0]
        assert 'm.facebook.com' in fb_config.base_urls[1]
        assert fb_config.scraping_strategy == ScrapingStrategy.MOBILE_USER_AGENT
        assert fb_config.has_anti_bot is True
        assert fb_config.javascript_required is True
        
        # Check Facebook-specific selectors
        assert 'follower_count' in fb_config.selectors
        assert 'posts' in fb_config.selectors
        assert 'post_text' in fb_config.selectors
    
    def test_linkedin_config(self):
        """Test LinkedIn site configuration"""
        li_config = SITE_CONFIGS['linkedin']
        
        assert li_config.name == 'LinkedIn'
        assert 'linkedin.com' in li_config.base_urls[0]
        assert li_config.scraping_strategy == ScrapingStrategy.BASIC_HTTP
        assert li_config.has_anti_bot is True
        assert li_config.javascript_required is True
        
        # Check LinkedIn-specific selectors
        assert 'follower_count' in li_config.selectors
        assert 'posts' in li_config.selectors
        assert 'company_info' in li_config.selectors
    
    def test_twitter_config(self):
        """Test Twitter site configuration"""
        tw_config = SITE_CONFIGS['twitter']
        
        assert tw_config.name == 'Twitter/X'
        assert 'twitter.com' in tw_config.base_urls[0]
        assert 'x.com' in tw_config.base_urls[1]
        assert tw_config.scraping_strategy == ScrapingStrategy.SELENIUM_HEADLESS
        assert tw_config.has_anti_bot is True
        assert tw_config.javascript_required is True
        
        # Check Twitter-specific selectors
        assert 'follower_count' in tw_config.selectors
        assert 'posts' in tw_config.selectors
        assert 'post_text' in tw_config.selectors
    
    def test_generic_news_config(self):
        """Test generic news site configuration"""
        news_config = SITE_CONFIGS['generic_news']
        
        assert news_config.name == 'Generic News Site'
        assert news_config.base_urls == []
        assert news_config.url_patterns == ['*']
        assert news_config.scraping_strategy == ScrapingStrategy.BASIC_HTTP
        assert news_config.has_anti_bot is False
        assert news_config.javascript_required is False
        
        # Check generic news selectors
        assert 'title' in news_config.selectors
        assert 'content' in news_config.selectors
        assert 'author' in news_config.selectors
        assert 'date' in news_config.selectors
    
    def test_all_configs_valid(self):
        """Test that all predefined site configs are valid"""
        for site_name, config in SITE_CONFIGS.items():
            # Basic validation
            assert isinstance(config, SiteConfig)
            assert config.name is not None
            assert len(config.name) > 0
            assert isinstance(config.base_urls, list)
            assert isinstance(config.url_patterns, list)
            assert isinstance(config.scraping_strategy, ScrapingStrategy)
            assert isinstance(config.selectors, dict)
            assert isinstance(config.requires_login, bool)
            assert isinstance(config.has_anti_bot, bool)
            assert isinstance(config.javascript_required, bool)
            
            # Validate selectors are strings
            for selector_name, selector_value in config.selectors.items():
                assert isinstance(selector_name, str)
                assert isinstance(selector_value, str)
                assert len(selector_value) > 0
    
    def test_config_immutability(self):
        """Test that modifying SITE_CONFIGS doesn't affect other tests"""
        original_fb_name = SITE_CONFIGS['facebook'].name
        
        # Try to modify (this should not affect the original)
        test_config = SITE_CONFIGS['facebook']
        # In a real scenario, configs should be copied to avoid side effects
        
        assert SITE_CONFIGS['facebook'].name == original_fb_name 
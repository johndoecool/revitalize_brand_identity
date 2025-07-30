"""
Unit tests for WebScraper class

Tests the core web scraping functionality including different strategies,
error handling, and data extraction capabilities.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from scrapers.web_scraper import WebScraper, ScrapingResult
from scrapers.scraper_config import ScraperConfig, ScrapingStrategy, ContentType
from tests.utils.mock_helpers import MockAiohttpSession, MockSeleniumDriver, setup_mock_http_responses
from tests.fixtures.mock_html_responses import MOCK_RESPONSES

class TestWebScraper:
    """Test cases for WebScraper class"""
    
    @pytest.fixture
    def scraper_config(self):
        """Create a test scraper configuration"""
        return ScraperConfig(
            max_retries=2,
            timeout=5,
            delay_between_requests=0.1,
            concurrent_requests=2
        )
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock aiohttp session"""
        return MockAiohttpSession()
    
    @pytest.mark.asyncio
    async def test_scraper_initialization(self, scraper_config):
        """Test WebScraper initialization with custom config"""
        scraper = WebScraper(scraper_config)
        assert scraper.config == scraper_config
        assert scraper.session is None
        assert scraper.driver is None
    
    @pytest.mark.asyncio
    async def test_scraper_context_manager(self, scraper_config):
        """Test WebScraper as async context manager"""
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            async with WebScraper(scraper_config) as scraper:
                assert scraper.session is not None
                mock_session_class.assert_called_once()
            
            # Ensure session is closed
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_scrape_url_success(self, scraper_config):
        """Test successful URL scraping with HTTP strategy"""
        test_url = "https://example.com"
        expected_html = MOCK_RESPONSES['generic_success']
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = MockAiohttpSession()
            mock_session.set_response(test_url, content=expected_html)
            mock_session_class.return_value = mock_session
            
            async with WebScraper(scraper_config) as scraper:
                result = await scraper.scrape_url(test_url)
                
                assert result.success is True
                assert result.url == test_url
                assert result.content == expected_html
                assert result.status_code == 200
                assert result.error is None
                assert 'title' in result.extracted_data
    
    @pytest.mark.asyncio
    async def test_scrape_url_404_error(self, scraper_config):
        """Test scraping URL that returns 404"""
        test_url = "https://example.com/nonexistent"
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = MockAiohttpSession()
            mock_session.set_response(test_url, status=404, content=MOCK_RESPONSES['generic_404'])
            mock_session_class.return_value = mock_session
            
            async with WebScraper(scraper_config) as scraper:
                result = await scraper.scrape_url(test_url)
                
                assert result.success is False
                assert result.url == test_url
                assert result.status_code == 404
    
    @pytest.mark.asyncio
    async def test_scrape_url_403_forbidden(self, scraper_config):
        """Test scraping URL that returns 403 Forbidden"""
        test_url = "https://protected.com"
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = MockAiohttpSession()
            mock_session.set_response(test_url, status=403, content=MOCK_RESPONSES['forbidden_403'])
            mock_session_class.return_value = mock_session
            
            async with WebScraper(scraper_config) as scraper:
                result = await scraper.scrape_url(test_url)
                
                assert result.success is False
                assert result.status_code == 403
    
    @pytest.mark.asyncio
    async def test_scrape_url_rate_limited(self, scraper_config):
        """Test scraping URL that returns 429 Rate Limited"""
        test_url = "https://ratelimited.com"
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = MockAiohttpSession()
            mock_session.set_response(test_url, status=429, content=MOCK_RESPONSES['rate_limited_429'])
            mock_session_class.return_value = mock_session
            
            with patch('asyncio.sleep') as mock_sleep:  # Speed up test
                async with WebScraper(scraper_config) as scraper:
                    result = await scraper.scrape_url(test_url)
                    
                    # Should retry but eventually fail
                    assert result.success is False
                    assert result.status_code == 429
                    assert mock_sleep.call_count > 0  # Verify retry delay was called
    
    @pytest.mark.asyncio
    async def test_scrape_multiple_urls(self, scraper_config):
        """Test scraping multiple URLs concurrently"""
        test_urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = MockAiohttpSession()
            for url in test_urls:
                mock_session.set_response(url, content=MOCK_RESPONSES['generic_success'])
            mock_session_class.return_value = mock_session
            
            async with WebScraper(scraper_config) as scraper:
                results = await scraper.scrape_multiple_urls(test_urls, max_concurrent=2)
                
                assert len(results) == 3
                for result in results:
                    assert result.success is True
                    assert result.url in test_urls
    
    @pytest.mark.asyncio
    async def test_mobile_user_agent_strategy(self, scraper_config):
        """Test mobile user agent scraping strategy"""
        from scrapers.scraper_config import SiteConfig, ScrapingStrategy
        
        test_url = "https://www.facebook.com/microsoft"
        mobile_url = "https://m.facebook.com/microsoft"
        
        site_config = SiteConfig(
            name="Facebook",
            base_urls=["https://www.facebook.com"],
            url_patterns=["facebook.com/{handle}"],
            scraping_strategy=ScrapingStrategy.MOBILE_USER_AGENT
        )
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = MockAiohttpSession()
            mock_session.set_response(mobile_url, content=MOCK_RESPONSES['facebook_mobile'])
            mock_session_class.return_value = mock_session
            
            async with WebScraper(scraper_config) as scraper:
                result = await scraper.scrape_url(test_url, site_config)
                
                assert result.success is True
                # Verify that mobile URL was used
                assert any('m.facebook.com' in req[1] for req in mock_session.request_history)
    
    @pytest.mark.asyncio
    async def test_selenium_strategy(self, scraper_config):
        """Test Selenium scraping strategy"""
        from scrapers.scraper_config import SiteConfig, ScrapingStrategy
        
        test_url = "https://spa-app.com"
        
        site_config = SiteConfig(
            name="SPA Application",
            base_urls=["https://spa-app.com"],
            url_patterns=["spa-app.com/*"],
            scraping_strategy=ScrapingStrategy.SELENIUM_HEADLESS,
            javascript_required=True
        )
        
        mock_driver = MockSeleniumDriver(MOCK_RESPONSES['generic_success'])
        
        with patch('scrapers.web_scraper.webdriver.Chrome', return_value=mock_driver):
            with patch('scrapers.web_scraper.ChromeDriverManager') as mock_manager:
                mock_manager.return_value.install.return_value = "/path/to/chromedriver"
                
                async with WebScraper(scraper_config) as scraper:
                    result = await scraper.scrape_url(test_url, site_config)
                    
                    assert result.success is True
                    assert result.content == mock_driver.page_source
                    mock_driver.get.assert_called_once_with(test_url)
                    mock_driver.quit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_site_config_detection(self, scraper_config):
        """Test automatic site configuration detection"""
        facebook_url = "https://www.facebook.com/microsoft"
        linkedin_url = "https://www.linkedin.com/company/microsoft"
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = MockAiohttpSession()
            mock_session.set_response(facebook_url, content=MOCK_RESPONSES['facebook_success'])
            mock_session.set_response(linkedin_url, content=MOCK_RESPONSES['linkedin_success'])
            mock_session_class.return_value = mock_session
            
            async with WebScraper(scraper_config) as scraper:
                # Test Facebook detection
                fb_result = await scraper.scrape_url(facebook_url)
                assert fb_result.success is True
                
                # Test LinkedIn detection
                li_result = await scraper.scrape_url(linkedin_url)
                assert li_result.success is True
    
    @pytest.mark.asyncio
    async def test_structured_data_extraction(self, scraper_config):
        """Test structured data extraction using CSS selectors"""
        test_url = "https://news.example.com/article"
        custom_selectors = {
            'headline': '.headline, h1',
            'author': '.byline [rel="author"], .author',
            'publish_date': '.publish-date, time[datetime]',
            'article_content': '.article-content, article'
        }
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            mock_session = MockAiohttpSession()
            mock_session.set_response(test_url, content=MOCK_RESPONSES['generic_success'])
            mock_session_class.return_value = mock_session
            
            async with WebScraper(scraper_config) as scraper:
                result = await scraper.scrape_url(test_url, custom_selectors=custom_selectors)
                
                assert result.success is True
                assert 'headline' in result.extracted_data
                assert 'author' in result.extracted_data
                assert 'publish_date' in result.extracted_data
                assert result.extracted_data['headline'] is not None
    
    @pytest.mark.asyncio
    async def test_error_handling_and_retries(self, scraper_config):
        """Test error handling and retry mechanism"""
        test_url = "https://unreliable.com"
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            # Mock session that throws exception
            mock_session = AsyncMock()
            mock_session.get.side_effect = Exception("Connection failed")
            mock_session_class.return_value = mock_session
            
            with patch('asyncio.sleep'):  # Speed up test
                async with WebScraper(scraper_config) as scraper:
                    result = await scraper.scrape_url(test_url)
                    
                    assert result.success is False
                    assert result.error is not None
                    # Verify retries were attempted
                    assert mock_session.get.call_count == scraper_config.max_retries
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, scraper_config):
        """Test timeout handling during scraping"""
        test_url = "https://slow.com"
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            # Mock session that times out
            mock_session = AsyncMock()
            mock_session.get.side_effect = asyncio.TimeoutError("Request timeout")
            mock_session_class.return_value = mock_session
            
            with patch('asyncio.sleep'):  # Speed up test
                async with WebScraper(scraper_config) as scraper:
                    result = await scraper.scrape_url(test_url)
                    
                    assert result.success is False
                    assert mock_session.get.call_count == scraper_config.max_retries

class TestScrapingResult:
    """Test cases for ScrapingResult class"""
    
    def test_scraping_result_creation(self):
        """Test ScrapingResult object creation"""
        url = "https://example.com"
        result = ScrapingResult(url, success=True)
        
        assert result.url == url
        assert result.success is True
        assert result.content is None
        assert result.html is None
        assert result.status_code is None
        assert result.headers == {}
        assert result.error is None
        assert result.extracted_data == {}
        assert result.metadata == {}
    
    def test_scraping_result_repr(self):
        """Test ScrapingResult string representation"""
        url = "https://example.com"
        
        # Test successful result
        success_result = ScrapingResult(url, success=True)
        assert "SUCCESS" in str(success_result)
        assert url in str(success_result)
        
        # Test failed result
        failed_result = ScrapingResult(url, success=False)
        assert "FAILED" in str(failed_result)
        assert url in str(failed_result) 
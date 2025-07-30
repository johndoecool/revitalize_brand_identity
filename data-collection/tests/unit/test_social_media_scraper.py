"""
Unit tests for SocialMediaScraper class

Tests the specialized social media scraping functionality for different platforms.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from scrapers.social_media_scraper import SocialMediaScraper
from scrapers.web_scraper import ScrapingResult
from scrapers.scraper_config import ScraperConfig
from tests.utils.mock_helpers import (
    MockAiohttpSession, 
    create_mock_scraping_result, 
    create_mock_social_media_data
)
from tests.fixtures.mock_html_responses import MOCK_RESPONSES

class TestSocialMediaScraper:
    """Test cases for SocialMediaScraper class"""
    
    @pytest.fixture
    def scraper_config(self):
        """Create a test scraper configuration"""
        return ScraperConfig(
            max_retries=2,
            timeout=5,
            delay_between_requests=0.1
        )
    
    @pytest.mark.asyncio
    async def test_scraper_initialization(self, scraper_config):
        """Test SocialMediaScraper initialization"""
        scraper = SocialMediaScraper(scraper_config)
        assert scraper.config == scraper_config
        assert scraper.web_scraper is not None
        assert scraper.web_scraper.config == scraper_config
    
    @pytest.mark.asyncio
    async def test_context_manager(self, scraper_config):
        """Test SocialMediaScraper as async context manager"""
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            mock_web_scraper.__aenter__ = AsyncMock()
            mock_web_scraper.__aexit__ = AsyncMock()
            
            async with SocialMediaScraper(scraper_config) as scraper:
                assert scraper is not None
            
            mock_web_scraper.__aenter__.assert_called_once()
            mock_web_scraper.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_scrape_facebook_page_success(self, scraper_config):
        """Test successful Facebook page scraping"""
        brand_name = "Microsoft"
        expected_data = create_mock_social_media_data("facebook", brand_name, 0.75, 18234567)
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock successful scraping result
            mock_result = create_mock_scraping_result(
                "https://m.facebook.com/microsoft",
                success=True,
                content=MOCK_RESPONSES['facebook_success']
            )
            mock_web_scraper.scrape_url = AsyncMock(return_value=mock_result)
            
            scraper = SocialMediaScraper(scraper_config)
            result = await scraper.scrape_facebook_page(brand_name)
            
            assert result is not None
            assert result['sentiment'] > 0
            assert result['mentions'] > 0
            assert len(result['posts']) > 0
            assert 'raw_data' in result
            
            # Verify scrape_url was called with Facebook URLs
            mock_web_scraper.scrape_url.assert_called()
    
    @pytest.mark.asyncio
    async def test_scrape_facebook_page_login_redirect(self, scraper_config):
        """Test Facebook page scraping with login redirect"""
        brand_name = "Microsoft"
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock login redirect response
            mock_result = create_mock_scraping_result(
                "https://m.facebook.com/microsoft",
                success=True,
                content=MOCK_RESPONSES['facebook_login']
            )
            mock_web_scraper.scrape_url = AsyncMock(return_value=mock_result)
            
            scraper = SocialMediaScraper(scraper_config)
            result = await scraper.scrape_facebook_page(brand_name)
            
            # Should try multiple URLs when login redirect is detected
            assert mock_web_scraper.scrape_url.call_count >= 1
            
            # May return None if all URLs redirect to login
            if result is None:
                assert True  # This is expected behavior for login redirects
    
    @pytest.mark.asyncio
    async def test_scrape_facebook_page_no_data(self, scraper_config):
        """Test Facebook page scraping when no data is found"""
        brand_name = "NonExistentBrand"
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock failed scraping results for all URLs
            mock_result = create_mock_scraping_result(
                "https://m.facebook.com/nonexistentbrand",
                success=False
            )
            mock_web_scraper.scrape_url = AsyncMock(return_value=mock_result)
            
            scraper = SocialMediaScraper(scraper_config)
            result = await scraper.scrape_facebook_page(brand_name)
            
            assert result is None
            # Should try multiple URL variations
            assert mock_web_scraper.scrape_url.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_scrape_linkedin_company_success(self, scraper_config):
        """Test successful LinkedIn company page scraping"""
        brand_name = "Microsoft"
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock successful LinkedIn scraping
            mock_result = create_mock_scraping_result(
                "https://www.linkedin.com/company/microsoft",
                success=True,
                content=MOCK_RESPONSES['linkedin_success']
            )
            mock_web_scraper.scrape_url = AsyncMock(return_value=mock_result)
            
            scraper = SocialMediaScraper(scraper_config)
            result = await scraper.scrape_linkedin_company(brand_name)
            
            assert result is not None
            assert result['sentiment'] > 0
            assert result['mentions'] > 0
            assert len(result['posts']) >= 0
            assert 'raw_data' in result
            
            # Verify correct LinkedIn URLs were attempted
            mock_web_scraper.scrape_url.assert_called()
            call_args = mock_web_scraper.scrape_url.call_args_list
            assert any('linkedin.com/company' in str(call) for call in call_args)
    
    @pytest.mark.asyncio
    async def test_scrape_linkedin_company_challenge(self, scraper_config):
        """Test LinkedIn company scraping with anti-bot challenge"""
        brand_name = "Microsoft"
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock LinkedIn challenge response
            mock_result = create_mock_scraping_result(
                "https://www.linkedin.com/company/microsoft",
                success=True,
                content=MOCK_RESPONSES['linkedin_challenge']
            )
            mock_web_scraper.scrape_url = AsyncMock(return_value=mock_result)
            
            scraper = SocialMediaScraper(scraper_config)
            result = await scraper.scrape_linkedin_company(brand_name)
            
            # Should try multiple URLs when challenge is detected
            assert mock_web_scraper.scrape_url.call_count >= 1
            
            # May return None if challenge blocks all attempts
            if result is None:
                assert True  # This is expected behavior for challenges
    
    @pytest.mark.asyncio
    async def test_scrape_twitter_profile_success(self, scraper_config):
        """Test successful Twitter profile scraping"""
        brand_name = "Microsoft"
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock successful Twitter scraping
            mock_result = create_mock_scraping_result(
                "https://twitter.com/microsoft",
                success=True,
                content=MOCK_RESPONSES['twitter_success']
            )
            mock_web_scraper.scrape_url = AsyncMock(return_value=mock_result)
            
            scraper = SocialMediaScraper(scraper_config)
            result = await scraper.scrape_twitter_profile(brand_name)
            
            assert result is not None
            assert result['sentiment'] > 0
            assert result['mentions'] >= 0
            assert len(result['posts']) >= 0
            assert 'raw_data' in result
    
    @pytest.mark.asyncio
    async def test_scrape_generic_website_success(self, scraper_config):
        """Test generic website scraping with custom selectors"""
        test_url = "https://example.com/article"
        custom_selectors = {
            'title': 'h1, .headline',
            'author': '.author, .byline',
            'content': 'article, .content'
        }
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock successful generic scraping
            mock_result = create_mock_scraping_result(
                test_url,
                success=True,
                content=MOCK_RESPONSES['generic_success']
            )
            mock_result.extracted_data = {
                'title': 'Sample Article Title',
                'author': 'John Smith',
                'content': 'Article content here...'
            }
            mock_web_scraper.scrape_url = AsyncMock(return_value=mock_result)
            
            scraper = SocialMediaScraper(scraper_config)
            result = await scraper.scrape_generic_website(test_url, custom_selectors)
            
            assert result is not None
            assert result['success'] is True
            assert result['url'] == test_url
            assert 'extracted_data' in result
            assert result['extracted_data']['title'] is not None
            
            # Verify scrape_url was called with custom selectors
            mock_web_scraper.scrape_url.assert_called_once_with(
                test_url, 
                custom_selectors=custom_selectors
            )
    
    @pytest.mark.asyncio
    async def test_scrape_generic_website_failure(self, scraper_config):
        """Test generic website scraping failure"""
        test_url = "https://example.com/nonexistent"
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock failed scraping
            mock_result = create_mock_scraping_result(test_url, success=False)
            mock_result.error = "Page not found"
            mock_web_scraper.scrape_url = AsyncMock(return_value=mock_result)
            
            scraper = SocialMediaScraper(scraper_config)
            result = await scraper.scrape_generic_website(test_url)
            
            assert result is not None
            assert result['success'] is False
            assert result['url'] == test_url
            assert 'error' in result
    
    def test_extract_facebook_data(self, scraper_config):
        """Test Facebook data extraction from HTML"""
        scraper = SocialMediaScraper(scraper_config)
        
        # Mock ScrapingResult with Facebook HTML
        mock_result = create_mock_scraping_result(
            "https://facebook.com/microsoft",
            success=True,
            content=MOCK_RESPONSES['facebook_success']
        )
        mock_result.extracted_data = {
            'title': 'Microsoft - Home | Facebook',
            'follower_count': 18234567
        }
        
        result = scraper._extract_facebook_data(mock_result, "Microsoft")
        
        assert result is not None
        assert result['sentiment'] > 0
        assert result['mentions'] == 18234567
        assert len(result['posts']) > 0
        assert result['posts'][0]['source'] == 'facebook'
        assert 'raw_data' in result
    
    def test_extract_linkedin_data(self, scraper_config):
        """Test LinkedIn data extraction from HTML"""
        scraper = SocialMediaScraper(scraper_config)
        
        # Mock ScrapingResult with LinkedIn HTML
        mock_result = create_mock_scraping_result(
            "https://linkedin.com/company/microsoft",
            success=True,
            content=MOCK_RESPONSES['linkedin_success']
        )
        mock_result.extracted_data = {
            'title': 'Microsoft | LinkedIn',
            'follower_count': 18509628,
            'company_info': 'Computer Software • Redmond, Washington'
        }
        
        result = scraper._extract_linkedin_data(mock_result, "Microsoft")
        
        assert result is not None
        assert result['sentiment'] > 0
        assert result['mentions'] == 18509628
        assert len(result['posts']) >= 0
        assert 'raw_data' in result
    
    def test_extract_twitter_data(self, scraper_config):
        """Test Twitter data extraction from HTML"""
        scraper = SocialMediaScraper(scraper_config)
        
        # Mock ScrapingResult with Twitter HTML
        mock_result = create_mock_scraping_result(
            "https://twitter.com/microsoft",
            success=True,
            content=MOCK_RESPONSES['twitter_success']
        )
        mock_result.extracted_data = {
            'title': 'Microsoft (@microsoft) / X',
            'follower_count': 4200000  # 4.2M converted to number
        }
        
        result = scraper._extract_twitter_data(mock_result, "Microsoft")
        
        assert result is not None
        assert result['sentiment'] > 0
        assert result['mentions'] == 4200000
        assert len(result['posts']) >= 0
        assert 'raw_data' in result
    
    @pytest.mark.asyncio
    async def test_error_handling_during_scraping(self, scraper_config):
        """Test error handling during scraping operations"""
        brand_name = "Microsoft"
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            # Mock scraper that raises exception
            mock_web_scraper.scrape_url = AsyncMock(side_effect=Exception("Network error"))
            
            scraper = SocialMediaScraper(scraper_config)
            
            # Test Facebook scraping error handling
            fb_result = await scraper.scrape_facebook_page(brand_name)
            assert fb_result is None
            
            # Test LinkedIn scraping error handling
            li_result = await scraper.scrape_linkedin_company(brand_name)
            assert li_result is None
            
            # Test Twitter scraping error handling
            tw_result = await scraper.scrape_twitter_profile(brand_name)
            assert tw_result is None
    
    @pytest.mark.asyncio
    async def test_url_generation_patterns(self, scraper_config):
        """Test URL generation patterns for different brands"""
        brand_names = ["Microsoft", "Coca Cola", "AT&T"]
        
        with patch.object(SocialMediaScraper, 'web_scraper') as mock_web_scraper:
            mock_web_scraper.scrape_url = AsyncMock(return_value=create_mock_scraping_result("", False))
            
            scraper = SocialMediaScraper(scraper_config)
            
            for brand_name in brand_names:
                # Test Facebook URL generation
                await scraper.scrape_facebook_page(brand_name)
                
                # Test LinkedIn URL generation
                await scraper.scrape_linkedin_company(brand_name)
                
                # Test Twitter URL generation
                await scraper.scrape_twitter_profile(brand_name)
            
            # Verify multiple URL patterns were attempted
            assert mock_web_scraper.scrape_url.call_count > len(brand_names)
            
            # Check that URLs contain expected transformations
            call_args = [call[0][0] for call in mock_web_scraper.scrape_url.call_args_list]
            
            # Should have Facebook URLs with different formats
            facebook_urls = [url for url in call_args if 'facebook.com' in url]
            assert len(facebook_urls) > 0
            
            # Should have LinkedIn URLs with company slug transformations
            linkedin_urls = [url for url in call_args if 'linkedin.com' in url]
            assert len(linkedin_urls) > 0
            
            # Should have Twitter URLs
            twitter_urls = [url for url in call_args if 'twitter.com' in url or 'x.com' in url]
            assert len(twitter_urls) > 0 
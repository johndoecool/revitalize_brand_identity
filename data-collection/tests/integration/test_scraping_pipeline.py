"""
Integration tests for the complete scraping pipeline

Tests the integration between WebScraper, SocialMediaScraper, and SocialMediaCollector.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from scrapers import WebScraper, SocialMediaScraper, ScraperConfig
from collectors.social_media_collector import SocialMediaCollector
from tests.fixtures.mock_html_responses import MOCK_RESPONSES

class TestScrapingPipelineIntegration:
    """Integration tests for the complete scraping pipeline"""
    
    @pytest.fixture
    def scraper_config(self):
        """Test scraper configuration"""
        return ScraperConfig(
            max_retries=2,
            timeout=5,
            delay_between_requests=0.1,
            concurrent_requests=2
        )
    
    @pytest.mark.asyncio
    async def test_web_scraper_to_social_media_scraper_integration(self, scraper_config):
        """Test integration between WebScraper and SocialMediaScraper"""
        test_url = "https://www.facebook.com/microsoft"
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            # Mock successful HTTP response
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=MOCK_RESPONSES['facebook_success'])
            mock_response.headers = {'content-type': 'text/html'}
            
            mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Test the integration
            async with SocialMediaScraper(scraper_config) as sm_scraper:
                result = await sm_scraper.scrape_facebook_page("Microsoft")
                
                # Verify the pipeline worked
                assert result is not None
                assert result['sentiment'] > 0
                assert result['mentions'] >= 0
                assert 'posts' in result
                assert 'raw_data' in result
    
    @pytest.mark.asyncio
    async def test_social_media_scraper_to_collector_integration(self, scraper_config):
        """Test integration between SocialMediaScraper and SocialMediaCollector"""
        brand_name = "Microsoft"
        
        # Mock the SocialMediaScraper responses
        with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
            mock_scraper = AsyncMock()
            
            # Mock Facebook scraping
            mock_scraper.scrape_facebook_page = AsyncMock(return_value={
                "sentiment": 0.75,
                "mentions": 5000,
                "posts": [{"text": "Great product!", "sentiment": 0.8, "source": "facebook"}],
                "raw_data": {"title": "Microsoft - Facebook", "extracted_fields": {}}
            })
            
            # Mock LinkedIn scraping
            mock_scraper.scrape_linkedin_company = AsyncMock(return_value={
                "sentiment": 0.8,
                "mentions": 7500,
                "posts": [{"text": "Innovation leader", "sentiment": 0.85, "source": "linkedin"}],
                "raw_data": {"title": "Microsoft | LinkedIn", "company_info": "Tech company"}
            })
            
            mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
            mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Test collector integration
            collector = SocialMediaCollector()
            
            with patch.object(collector, '_analyze_web_content_sentiment', return_value=0.85):
                # Test Facebook integration
                fb_result = await collector._scrape_facebook_data(brand_name)
                assert fb_result is not None
                assert fb_result['sentiment'] == 0.85  # Enhanced by LLM
                
                # Test LinkedIn integration
                li_result = await collector._scrape_linkedin_data(brand_name)
                assert li_result is not None
                assert li_result['sentiment'] == 0.85  # Enhanced by LLM
    
    @pytest.mark.asyncio
    async def test_complete_brand_analysis_pipeline(self, scraper_config):
        """Test the complete brand analysis pipeline from scraping to final result"""
        brand_id = "Microsoft"
        area_id = "innovation"
        
        # Mock all external dependencies
        mock_settings = Mock()
        mock_settings.twitter_api_key = "test_key"
        mock_settings.twitter_bearer_token = "AAAAAAAAAAAAAAAAAAAAAA%test_token"
        mock_settings.preferred_llm_provider = "openai"
        mock_settings.openai_api_key = "test_openai_key"
        
        with patch('collectors.social_media_collector.settings', mock_settings):
            with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
                # Setup comprehensive mock scraper
                mock_scraper = AsyncMock()
                mock_scraper.scrape_facebook_page = AsyncMock(return_value={
                    "sentiment": 0.7,
                    "mentions": 18234567,
                    "posts": [
                        {"text": "AI innovation is amazing!", "sentiment": 0.8, "source": "facebook"},
                        {"text": "Great productivity tools", "sentiment": 0.7, "source": "facebook"}
                    ],
                    "raw_data": {"title": "Microsoft - Facebook", "extracted_fields": {"follower_count": 18234567}}
                })
                
                mock_scraper.scrape_linkedin_company = AsyncMock(return_value={
                    "sentiment": 0.8,
                    "mentions": 18509628,
                    "posts": [
                        {"text": "Hiring great engineers", "sentiment": 0.85, "source": "linkedin"},
                        {"text": "Carbon neutral commitment", "sentiment": 0.75, "source": "linkedin"}
                    ],
                    "raw_data": {"title": "Microsoft | LinkedIn", "company_info": "Technology company"}
                })
                
                mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
                mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
                
                # Mock Twitter API
                twitter_response = {
                    'data': [
                        {'text': 'Excited about AI features! #Innovation', 'public_metrics': {'like_count': 500}},
                        {'text': 'Developer community rocks! #Tech', 'public_metrics': {'like_count': 300}}
                    ]
                }
                
                collector = SocialMediaCollector()
                
                with patch.object(collector, 'make_request', return_value=twitter_response):
                    with patch.object(collector, 'calculate_sentiment_score', return_value=0.75):
                        with patch.object(collector, '_analyze_web_content_sentiment', return_value=0.85):
                            async with collector:
                                result = await collector.collect_brand_data(brand_id, area_id)
                                
                                # Verify complete pipeline result
                                assert result is not None
                                
                                # Check top-level metrics
                                assert 'overall_sentiment' in result
                                assert 'mentions_count' in result
                                assert 'engagement_rate' in result
                                assert 'platforms' in result
                                assert 'trending_topics' in result
                                
                                # Verify platform data
                                platforms = result['platforms']
                                assert 'facebook' in platforms
                                assert 'linkedin' in platforms
                                assert 'twitter' in platforms
                                
                                # Check Facebook data
                                fb_data = platforms['facebook']
                                assert fb_data['mentions'] == 18234567
                                assert fb_data['sentiment'] > 0
                                
                                # Check LinkedIn data
                                li_data = platforms['linkedin']
                                assert li_data['mentions'] == 18509628
                                assert li_data['sentiment'] > 0
                                
                                # Check Twitter data
                                tw_data = platforms['twitter']
                                assert tw_data['mentions'] == 2  # 2 tweets
                                assert tw_data['sentiment'] > 0
                                
                                # Verify aggregated metrics
                                total_mentions = 18234567 + 18509628 + 2
                                assert result['mentions_count'] == total_mentions
                                assert result['overall_sentiment'] > 0
                                assert result['engagement_rate'] > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_throughout_pipeline(self, scraper_config):
        """Test error handling throughout the entire pipeline"""
        brand_id = "TestBrand"
        area_id = "test_area"
        
        # Mock settings
        mock_settings = Mock()
        mock_settings.twitter_bearer_token = None  # No Twitter token
        
        with patch('collectors.social_media_collector.settings', mock_settings):
            with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
                # Setup scraper to fail
                mock_scraper = AsyncMock()
                mock_scraper.scrape_facebook_page = AsyncMock(return_value=None)  # Facebook fails
                mock_scraper.scrape_linkedin_company = AsyncMock(return_value=None)  # LinkedIn fails
                
                mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
                mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
                
                collector = SocialMediaCollector()
                
                # Mock get_mock_data to return fallback data
                mock_fallback_data = {
                    "overall_sentiment": 0.5,
                    "mentions_count": 100,
                    "engagement_rate": 0.03,
                    "platforms": {"twitter": {"sentiment": 0.5, "mentions": 50}},
                    "trending_topics": ["technology"]
                }
                
                with patch.object(collector, 'get_mock_data', return_value=mock_fallback_data):
                    async with collector:
                        result = await collector.collect_brand_data(brand_id, area_id)
                        
                        # Should still return data (fallback/mock data)
                        assert result is not None
                        assert isinstance(result, dict)
                        assert 'overall_sentiment' in result
    
    @pytest.mark.asyncio
    async def test_concurrent_scraping_integration(self, scraper_config):
        """Test concurrent scraping across multiple brands"""
        brands = ["Microsoft", "Apple", "Google"]
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            # Mock session for concurrent requests
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=MOCK_RESPONSES['generic_success'])
            mock_response.headers = {'content-type': 'text/html'}
            
            mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_session.close = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Test concurrent scraping
            async with WebScraper(scraper_config) as scraper:
                test_urls = [f"https://example.com/{brand.lower()}" for brand in brands]
                
                results = await scraper.scrape_multiple_urls(test_urls, max_concurrent=2)
                
                assert len(results) == len(brands)
                for result in results:
                    assert result.success is True
                    assert result.content is not None
    
    @pytest.mark.asyncio
    async def test_llm_integration_pipeline(self, scraper_config):
        """Test LLM integration throughout the pipeline"""
        brand_name = "Microsoft"
        
        # Mock LLM settings
        mock_settings = Mock()
        mock_settings.preferred_llm_provider = "openai"
        mock_settings.openai_api_key = "test_key"
        mock_settings.llm_model_name = "gpt-3.5-turbo"
        
        with patch('collectors.social_media_collector.settings', mock_settings):
            with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
                # Mock scraper with raw data for LLM enhancement
                mock_scraper = AsyncMock()
                mock_scraper.scrape_facebook_page = AsyncMock(return_value={
                    "sentiment": 0.6,  # Base sentiment
                    "mentions": 1000,
                    "posts": [{"text": "Great product", "sentiment": 0.6, "source": "facebook"}],
                    "raw_data": {"title": "Microsoft - Facebook", "extracted_fields": {}}
                })
                
                mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
                mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
                
                collector = SocialMediaCollector()
                
                # Mock LLM enhancement
                with patch.object(collector, '_get_openai_sentiment', return_value=0.85):
                    result = await collector._scrape_facebook_data(brand_name)
                    
                    # Verify LLM enhancement worked
                    assert result is not None
                    assert result['sentiment'] == 0.85  # Enhanced from 0.6 to 0.85
                    assert result['posts'][0]['sentiment'] == 0.85  # Post sentiment also enhanced
    
    @pytest.mark.asyncio
    async def test_configuration_propagation(self, scraper_config):
        """Test that configuration is properly propagated through the pipeline"""
        # Verify ScraperConfig propagates to WebScraper
        async with WebScraper(scraper_config) as web_scraper:
            assert web_scraper.config.max_retries == scraper_config.max_retries
            assert web_scraper.config.timeout == scraper_config.timeout
        
        # Verify ScraperConfig propagates to SocialMediaScraper
        async with SocialMediaScraper(scraper_config) as sm_scraper:
            assert sm_scraper.config.max_retries == scraper_config.max_retries
            assert sm_scraper.web_scraper.config.timeout == scraper_config.timeout
    
    @pytest.mark.asyncio
    async def test_data_flow_integrity(self, scraper_config):
        """Test data integrity throughout the pipeline"""
        brand_name = "Microsoft"
        
        # Test data preservation through pipeline
        original_data = {
            "sentiment": 0.75,
            "mentions": 12345,
            "posts": [
                {"text": "Original post text", "sentiment": 0.8, "source": "facebook"}
            ],
            "raw_data": {
                "title": "Microsoft - Facebook",
                "extracted_fields": {"follower_count": 12345}
            }
        }
        
        with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
            mock_scraper = AsyncMock()
            mock_scraper.scrape_facebook_page = AsyncMock(return_value=original_data)
            mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
            mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            collector = SocialMediaCollector()
            
            # Mock LLM to return neutral (no enhancement)
            with patch.object(collector, '_analyze_web_content_sentiment', return_value=0.05):
                result = await collector._scrape_facebook_data(brand_name)
                
                # Verify data integrity
                assert result is not None
                assert result['mentions'] == original_data['mentions']  # Mentions preserved
                assert result['posts'][0]['text'] == original_data['posts'][0]['text']  # Post text preserved
                assert result['raw_data']['title'] == original_data['raw_data']['title']  # Raw data preserved 
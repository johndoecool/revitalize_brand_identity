"""
Unit tests for SocialMediaCollector class

Tests the updated SocialMediaCollector that uses the modular scraping architecture
and integrates with LLM-based sentiment analysis.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from collectors.social_media_collector import SocialMediaCollector
from scrapers.social_media_scraper import SocialMediaScraper
from tests.utils.mock_helpers import create_mock_social_media_data, create_mock_brand_analysis_data

class TestSocialMediaCollector:
    """Test cases for SocialMediaCollector class"""
    
    @pytest.fixture
    def collector(self):
        """Create a SocialMediaCollector instance for testing"""
        return SocialMediaCollector()
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        mock_settings = Mock()
        mock_settings.twitter_api_key = "test_api_key"
        mock_settings.twitter_bearer_token = "test_bearer_token"
        mock_settings.preferred_llm_provider = "openai"
        mock_settings.llm_model_name = "gpt-3.5-turbo"
        mock_settings.openai_api_key = "test_openai_key"
        return mock_settings
    
    def test_collector_initialization(self, collector, mock_settings):
        """Test SocialMediaCollector initialization"""
        with patch('collectors.social_media_collector.settings', mock_settings):
            new_collector = SocialMediaCollector()
            assert new_collector.twitter_api_key == "test_api_key"
            assert new_collector.twitter_bearer_token == "test_bearer_token"
    
    @pytest.mark.asyncio
    async def test_collect_brand_data_success(self, collector, mock_settings):
        """Test successful brand data collection"""
        brand_id = "Microsoft"
        area_id = "innovation"
        
        # Mock the individual scraping methods
        fb_data = create_mock_social_media_data("facebook", brand_id, 0.75, 5000)
        li_data = create_mock_social_media_data("linkedin", brand_id, 0.8, 7500)
        tw_data = create_mock_social_media_data("twitter", brand_id, 0.7, 3250)
        
        with patch.object(collector, '_collect_twitter_data', return_value=tw_data):
            with patch.object(collector, '_scrape_facebook_data', return_value=fb_data):
                with patch.object(collector, '_scrape_linkedin_data', return_value=li_data):
                    with patch('collectors.social_media_collector.settings', mock_settings):
                        async with collector:
                            result = await collector.collect_brand_data(brand_id, area_id)
                            
                            assert result is not None
                            assert 'overall_sentiment' in result
                            assert 'mentions_count' in result
                            assert 'engagement_rate' in result
                            assert 'platforms' in result
                            assert 'trending_topics' in result
                            
                            # Check platform data
                            assert 'twitter' in result['platforms']
                            assert 'facebook' in result['platforms']
                            assert 'linkedin' in result['platforms']
    
    @pytest.mark.asyncio
    async def test_collect_brand_data_error_handling(self, collector):
        """Test brand data collection with error handling"""
        brand_id = "TestBrand"
        area_id = "test_area"
        
        # Mock methods to raise exceptions
        with patch.object(collector, '_collect_twitter_data', side_effect=Exception("Twitter API error")):
            with patch.object(collector, '_scrape_facebook_data', side_effect=Exception("Facebook scraping error")):
                with patch.object(collector, '_scrape_linkedin_data', side_effect=Exception("LinkedIn scraping error")):
                    async with collector:
                        result = await collector.collect_brand_data(brand_id, area_id)
                        
                        # Should return mock data when errors occur
                        assert result is not None
                        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_scrape_facebook_data_success(self, collector):
        """Test successful Facebook data scraping using modular scraper"""
        brand_name = "Microsoft"
        expected_data = create_mock_social_media_data("facebook", brand_name, 0.75, 18234567)
        
        with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
            # Mock the SocialMediaScraper
            mock_scraper = AsyncMock()
            mock_scraper.scrape_facebook_page = AsyncMock(return_value=expected_data)
            mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
            mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Mock LLM sentiment analysis
            with patch.object(collector, '_analyze_web_content_sentiment', return_value=0.8):
                result = await collector._scrape_facebook_data(brand_name)
                
                assert result is not None
                assert result['sentiment'] == 0.8  # Enhanced by LLM
                assert result['mentions'] == expected_data['mentions']
                assert len(result['posts']) > 0
                
                # Verify SocialMediaScraper was used
                mock_scraper.scrape_facebook_page.assert_called_once_with(brand_name)
    
    @pytest.mark.asyncio
    async def test_scrape_facebook_data_no_enhancement(self, collector):
        """Test Facebook data scraping without LLM enhancement"""
        brand_name = "Microsoft"
        expected_data = create_mock_social_media_data("facebook", brand_name, 0.6, 1000)
        
        with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
            mock_scraper = AsyncMock()
            mock_scraper.scrape_facebook_page = AsyncMock(return_value=expected_data)
            mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
            mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Mock LLM sentiment analysis returning neutral
            with patch.object(collector, '_analyze_web_content_sentiment', return_value=0.05):
                result = await collector._scrape_facebook_data(brand_name)
                
                assert result is not None
                # Should keep original sentiment when LLM returns neutral
                assert result['sentiment'] == 0.6
    
    @pytest.mark.asyncio
    async def test_scrape_facebook_data_error(self, collector):
        """Test Facebook data scraping error handling"""
        brand_name = "Microsoft"
        
        with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
            mock_scraper = AsyncMock()
            mock_scraper.scrape_facebook_page = AsyncMock(side_effect=Exception("Scraping failed"))
            mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
            mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await collector._scrape_facebook_data(brand_name)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_scrape_linkedin_data_success(self, collector):
        """Test successful LinkedIn data scraping using modular scraper"""
        brand_name = "Microsoft"
        expected_data = create_mock_social_media_data("linkedin", brand_name, 0.8, 18509628)
        
        with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
            mock_scraper = AsyncMock()
            mock_scraper.scrape_linkedin_company = AsyncMock(return_value=expected_data)
            mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
            mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Mock LLM sentiment analysis
            with patch.object(collector, '_analyze_web_content_sentiment', return_value=0.85):
                result = await collector._scrape_linkedin_data(brand_name)
                
                assert result is not None
                assert result['sentiment'] == 0.85  # Enhanced by LLM
                assert result['mentions'] == expected_data['mentions']
                
                # Verify SocialMediaScraper was used
                mock_scraper.scrape_linkedin_company.assert_called_once_with(brand_name)
    
    @pytest.mark.asyncio
    async def test_scrape_linkedin_data_error(self, collector):
        """Test LinkedIn data scraping error handling"""
        brand_name = "Microsoft"
        
        with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
            mock_scraper = AsyncMock()
            mock_scraper.scrape_linkedin_company = AsyncMock(side_effect=Exception("LinkedIn error"))
            mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
            mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await collector._scrape_linkedin_data(brand_name)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_collect_twitter_data_success(self, collector, mock_settings):
        """Test successful Twitter data collection"""
        brand_name = "Microsoft"
        area_id = "innovation"
        
        mock_twitter_response = {
            'data': [
                {
                    'text': 'Excited to announce our new AI features!',
                    'public_metrics': {'like_count': 150, 'retweet_count': 45}
                },
                {
                    'text': 'Innovation is at the heart of everything we do.',
                    'public_metrics': {'like_count': 200, 'retweet_count': 60}
                }
            ]
        }
        
        with patch('collectors.social_media_collector.settings', mock_settings):
            with patch.object(collector, 'make_request', return_value=mock_twitter_response):
                with patch.object(collector, 'calculate_sentiment_score', return_value=0.75):
                    async with collector:
                        result = await collector._collect_twitter_data(brand_name, area_id)
                        
                        assert result is not None
                        assert result['sentiment'] > 0
                        assert result['mentions'] == 2
                        assert len(result['posts']) == 2
    
    @pytest.mark.asyncio
    async def test_collect_twitter_data_invalid_token(self, collector):
        """Test Twitter data collection with invalid token"""
        brand_name = "Microsoft"
        area_id = "innovation"
        
        # Mock settings with invalid token
        mock_settings = Mock()
        mock_settings.twitter_bearer_token = "invalid_token_format"
        
        with patch('collectors.social_media_collector.settings', mock_settings):
            async with collector:
                result = await collector._collect_twitter_data(brand_name, area_id)
                
                assert result is not None
                assert result['sentiment'] == 0.0
                assert result['mentions'] == 0
                assert result['posts'] == []
    
    @pytest.mark.asyncio
    async def test_collect_twitter_data_no_token(self, collector):
        """Test Twitter data collection with no token"""
        brand_name = "Microsoft"
        area_id = "innovation"
        
        # Mock settings with no token
        mock_settings = Mock()
        mock_settings.twitter_bearer_token = None
        
        with patch('collectors.social_media_collector.settings', mock_settings):
            async with collector:
                result = await collector._collect_twitter_data(brand_name, area_id)
                
                assert result is not None
                assert result['sentiment'] == 0.0
                assert result['mentions'] == 0
                assert result['posts'] == []
    
    def test_analyze_twitter_sentiment(self, collector):
        """Test Twitter sentiment analysis"""
        tweets = [
            {'text': 'Great product! Love the new features.'},
            {'text': 'Amazing innovation from this company.'},
            {'text': 'Not impressed with the latest update.'}
        ]
        
        with patch.object(collector, 'calculate_sentiment_score', side_effect=[0.8, 0.9, 0.2]):
            result = collector._analyze_twitter_sentiment(tweets)
            
            assert result is not None
            assert result['sentiment'] == pytest.approx(0.633, rel=1e-2)  # Average of 0.8, 0.9, 0.2
            assert result['mentions'] == 3
            assert len(result['posts']) == 3  # Should return first 5, but we have 3
    
    def test_analyze_twitter_sentiment_empty(self, collector):
        """Test Twitter sentiment analysis with empty tweets"""
        result = collector._analyze_twitter_sentiment([])
        
        assert result is not None
        assert result['sentiment'] == 0.0
        assert result['mentions'] == 0
        assert result['posts'] == []
    
    def test_analyze_web_content_sentiment(self, collector, mock_settings):
        """Test web content sentiment analysis with LLM"""
        content = "Microsoft announces new AI features that will revolutionize productivity"
        brand_name = "Microsoft"
        platform = "Facebook"
        
        # Mock LLM provider methods
        with patch('collectors.social_media_collector.settings', mock_settings):
            with patch.object(collector, '_get_openai_sentiment', return_value=0.85):
                result = collector._analyze_web_content_sentiment(content, brand_name, platform)
                
                assert result == 0.85
    
    def test_analyze_web_content_sentiment_fallback(self, collector):
        """Test web content sentiment analysis fallback to traditional methods"""
        content = "Microsoft announces new AI features"
        brand_name = "Microsoft"
        platform = "Facebook"
        
        # Mock LLM providers to fail
        with patch.object(collector, '_get_openai_sentiment', side_effect=Exception("API error")):
            with patch.object(collector, '_get_anthropic_sentiment', side_effect=Exception("API error")):
                with patch.object(collector, 'calculate_sentiment_score', return_value=0.7):
                    result = collector._analyze_web_content_sentiment(content, brand_name, platform)
                    
                    assert result == 0.7  # Should fallback to traditional sentiment
    
    def test_aggregate_social_media_data(self, collector):
        """Test social media data aggregation"""
        platform_data = {
            'twitter': {'sentiment': 0.7, 'mentions': 1000},
            'facebook': {'sentiment': 0.8, 'mentions': 2000},
            'linkedin': {'sentiment': 0.75, 'mentions': 1500}
        }
        brand_id = "Microsoft"
        
        with patch.object(collector, '_generate_trending_topics', return_value=['innovation', 'AI', 'technology']):
            result = collector._aggregate_social_media_data(platform_data, brand_id)
            
            assert result is not None
            assert 'overall_sentiment' in result
            assert 'mentions_count' in result
            assert 'engagement_rate' in result
            assert 'platforms' in result
            assert 'trending_topics' in result
            
            # Check calculations
            expected_mentions = 1000 + 2000 + 1500
            assert result['mentions_count'] == expected_mentions
            
            # Check weighted sentiment calculation
            expected_sentiment = (0.7*1000 + 0.8*2000 + 0.75*1500) / expected_mentions
            assert result['overall_sentiment'] == pytest.approx(expected_sentiment, rel=1e-2)
    
    def test_aggregate_social_media_data_no_mentions(self, collector):
        """Test social media data aggregation with no mentions"""
        platform_data = {
            'twitter': {'sentiment': 0.7, 'mentions': 0},
            'facebook': {'sentiment': 0.8, 'mentions': 0},
            'linkedin': {'sentiment': 0.75, 'mentions': 0}
        }
        brand_id = "Microsoft"
        
        result = collector._aggregate_social_media_data(platform_data, brand_id)
        
        assert result is not None
        assert result['overall_sentiment'] == 0.0
        assert result['mentions_count'] == 0
    
    def test_get_area_keywords(self, collector):
        """Test area keywords generation"""
        # Test known area
        keywords = collector._get_area_keywords("innovation")
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert all(isinstance(keyword, str) for keyword in keywords)
        
        # Test unknown area
        keywords = collector._get_area_keywords("unknown_area")
        assert keywords == []
    
    def test_generate_trending_topics(self, collector):
        """Test trending topics generation"""
        brand_id = "Microsoft"
        
        topics = collector._generate_trending_topics(brand_id)
        
        assert isinstance(topics, list)
        assert len(topics) == 3  # Should return first 3 topics
        assert all(isinstance(topic, str) for topic in topics)

class TestSocialMediaCollectorIntegration:
    """Integration tests for SocialMediaCollector with modular scraping"""
    
    @pytest.fixture
    def collector_with_session(self):
        """Create collector with mocked session"""
        collector = SocialMediaCollector()
        collector.session = AsyncMock()
        return collector
    
    @pytest.mark.asyncio
    async def test_end_to_end_brand_collection(self, collector_with_session, mock_settings):
        """Test end-to-end brand data collection"""
        brand_id = "Microsoft"
        area_id = "innovation"
        
        # Mock all external dependencies
        with patch('collectors.social_media_collector.settings', mock_settings):
            with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper_class:
                # Setup mock scraper
                mock_scraper = AsyncMock()
                mock_scraper.scrape_facebook_page = AsyncMock(return_value=create_mock_social_media_data("facebook", brand_id))
                mock_scraper.scrape_linkedin_company = AsyncMock(return_value=create_mock_social_media_data("linkedin", brand_id))
                mock_scraper_class.return_value.__aenter__ = AsyncMock(return_value=mock_scraper)
                mock_scraper_class.return_value.__aexit__ = AsyncMock(return_value=None)
                
                # Mock Twitter API response
                twitter_response = {
                    'data': [
                        {'text': 'Great innovation!', 'public_metrics': {'like_count': 100}}
                    ]
                }
                collector_with_session.make_request = AsyncMock(return_value=twitter_response)
                collector_with_session.calculate_sentiment_score = Mock(return_value=0.8)
                collector_with_session._analyze_web_content_sentiment = Mock(return_value=0.75)
                
                # Execute full collection
                result = await collector_with_session.collect_brand_data(brand_id, area_id)
                
                # Verify complete result structure
                assert result is not None
                assert all(key in result for key in [
                    'overall_sentiment', 'mentions_count', 'engagement_rate', 
                    'platforms', 'trending_topics'
                ])
                
                # Verify platform data exists
                assert 'facebook' in result['platforms']
                assert 'linkedin' in result['platforms']  
                assert 'twitter' in result['platforms']
                
                # Verify scraping methods were called
                mock_scraper.scrape_facebook_page.assert_called_once_with(brand_id)
                mock_scraper.scrape_linkedin_company.assert_called_once_with(brand_id) 
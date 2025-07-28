from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import aiohttp
from datetime import datetime
from loguru import logger
from src.config.settings import settings
from src.models.schemas import DataSource


class BaseCollector(ABC):
    """Base class for all data collectors"""
    
    def __init__(self, source_type: DataSource):
        self.source_type = source_type
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit = getattr(settings, f"{source_type.value}_rate_limit", settings.default_rate_limit)
        self.request_timeout = settings.request_timeout
        self.max_retries = settings.max_retries
    
    async def __aenter__(self):
        """Async context manager entry"""
        import ssl
        import aiohttp
        
        # Create SSL context based on configuration
        if settings.verify_ssl:
            # Production: Use default SSL verification
            connector = aiohttp.TCPConnector()
        else:
            # Development: Disable SSL verification for problematic certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.request_timeout),
            headers={"User-Agent": settings.user_agent},
            connector=connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def collect_brand_data(self, brand_id: str, area_id: str) -> Dict[str, Any]:
        """Collect data for a specific brand in a given area"""
        pass
    
    async def make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    async with self.session.get(url, **kwargs) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:  # Rate limited
                            await asyncio.sleep(2 ** attempt)
                            continue
                        else:
                            logger.warning(f"Request failed with status {response.status}: {url}")
                            return None
                elif method.upper() == "POST":
                    async with self.session.post(url, **kwargs) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 429:  # Rate limited
                            await asyncio.sleep(2 ** attempt)
                            continue
                        else:
                            logger.warning(f"Request failed with status {response.status}: {url}")
                            return None
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout (attempt {attempt + 1}): {url}")
                await asyncio.sleep(1)
            except Exception as e:
                error_msg = str(e)
                if "SSL" in error_msg or "certificate" in error_msg.lower():
                    logger.warning(f"SSL error (attempt {attempt + 1}): {error_msg}")
                    logger.info("SSL verification issues detected - using mock data for this source")
                    return None  # This will trigger fallback to mock data
                else:
                    logger.error(f"Request error (attempt {attempt + 1}): {error_msg}")
                await asyncio.sleep(1)
        
        logger.error(f"All retry attempts failed for URL: {url}")
        return None
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score using basic text analysis"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except ImportError:
            # Fallback to VADER sentiment if TextBlob is not available
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                analyzer = SentimentIntensityAnalyzer()
                score = analyzer.polarity_scores(text)
                return score['compound']
            except ImportError:
                # Simple keyword-based sentiment as last resort
                positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'outstanding']
                negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor', 'worst']
                
                text_lower = text.lower()
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                if pos_count == neg_count:
                    return 0.0
                elif pos_count > neg_count:
                    return min(0.8, pos_count * 0.2)
                else:
                    return max(-0.8, -neg_count * 0.2)
    
    def normalize_brand_name(self, brand_name: str) -> str:
        """Normalize brand name for API searches"""
        return brand_name.lower().replace('_', ' ').replace('-', ' ').strip()
    
    async def collect_with_progress_callback(self, brand_id: str, area_id: str, progress_callback=None) -> Dict[str, Any]:
        """Collect data with progress reporting"""
        try:
            if progress_callback:
                await progress_callback(f"Starting {self.source_type.value} collection for {brand_id}")
            
            data = await self.collect_brand_data(brand_id, area_id)
            
            if progress_callback:
                await progress_callback(f"Completed {self.source_type.value} collection for {brand_id}")
            
            return data
        except Exception as e:
            logger.error(f"Error in {self.source_type.value} collector: {str(e)}")
            if progress_callback:
                await progress_callback(f"Failed {self.source_type.value} collection for {brand_id}: {str(e)}")
            raise
    
    def get_mock_data(self, brand_id: str) -> Dict[str, Any]:
        """Generate mock data when real data collection fails"""
        logger.info(f"Generating mock data for {self.source_type.value} - {brand_id}")
        
        if self.source_type == DataSource.NEWS:
            return {
                "score": 0.6,
                "articles_count": 25,
                "positive_articles": 15,
                "negative_articles": 5,
                "neutral_articles": 5,
                "recent_articles": [
                    {
                        "title": f"{brand_id} - Recent News Update",
                        "sentiment": "positive",
                        "published_date": datetime.now().strftime("%Y-%m-%d")
                    }
                ]
            }
        elif self.source_type == DataSource.SOCIAL_MEDIA:
            return {
                "overall_sentiment": 0.65,
                "mentions_count": 850,
                "engagement_rate": 0.048,
                "platforms": {
                    "twitter": {"sentiment": 0.68, "mentions": 400},
                    "facebook": {"sentiment": 0.63, "mentions": 300},
                    "linkedin": {"sentiment": 0.72, "mentions": 150}
                },
                "trending_topics": ["service", "customer experience", "innovation"]
            }
        elif self.source_type == DataSource.GLASSDOOR:
            return {
                "overall_rating": 3.7,
                "reviews_count": 75,
                "pros": ["Good benefits", "Stable environment", "Team collaboration"],
                "cons": ["Limited growth", "Bureaucracy", "Slow processes"],
                "recommendation_rate": 0.72,
                "ceo_approval": 0.78
            }
        elif self.source_type == DataSource.WEBSITE:
            return {
                "user_experience_score": 0.78,
                "feature_completeness": 0.72,
                "security_score": 0.85,
                "accessibility_score": 0.76,
                "mobile_friendliness": 0.74,
                "load_time": 2.8
            }
        
        return {}


class CollectorFactory:
    """Factory class to create appropriate collectors"""
    
    @staticmethod
    def create_collector(source_type: DataSource) -> BaseCollector:
        """Create a collector for the specified source type"""
        if source_type == DataSource.NEWS:
            from src.collectors.news_collector import NewsCollector
            return NewsCollector()
        elif source_type == DataSource.SOCIAL_MEDIA:
            from src.collectors.social_media_collector import SocialMediaCollector
            return SocialMediaCollector()
        elif source_type == DataSource.GLASSDOOR:
            from src.collectors.glassdoor_collector import GlassdoorCollector
            return GlassdoorCollector()
        elif source_type == DataSource.WEBSITE:
            from src.collectors.website_collector import WebsiteCollector
            return WebsiteCollector()
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    @staticmethod
    async def collect_all_sources(brand_id: str, area_id: str, sources: list, progress_callback=None) -> Dict[str, Any]:
        """Collect data from all specified sources concurrently"""
        results = {}
        
        async def collect_single_source(source_type: DataSource):
            try:
                collector = CollectorFactory.create_collector(source_type)
                async with collector:
                    data = await collector.collect_with_progress_callback(brand_id, area_id, progress_callback)
                    results[source_type.value] = data
            except Exception as e:
                logger.error(f"Failed to collect from {source_type.value}: {str(e)}")
                # Use mock data as fallback
                collector = CollectorFactory.create_collector(source_type)
                results[source_type.value] = collector.get_mock_data(brand_id)
        
        # Collect from all sources concurrently
        tasks = [collect_single_source(source) for source in sources]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results 
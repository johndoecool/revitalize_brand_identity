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
        """Make HTTP request with retry logic for API calls (expects JSON response)"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    async with self.session.get(url, **kwargs) as response:
                        if response.status == 200:
                            try:
                                return await response.json()
                            except Exception as e:
                                logger.warning(f"Failed to parse JSON response from {url}: {str(e)}")
                                return None
                        elif response.status == 401:
                            logger.error(f"Authentication failed (401) for URL: {url}. Check API credentials.")
                            return None  # Don't retry auth failures
                        elif response.status == 403:
                            logger.error(f"Forbidden (403) for URL: {url}. Check API permissions.")
                            return None  # Don't retry permission failures
                        elif response.status == 429:  # Rate limited
                            retry_after = response.headers.get('retry-after', 2 ** attempt)
                            logger.warning(f"Rate limited (429). Retrying after {retry_after}s...")
                            await asyncio.sleep(int(retry_after))
                            continue
                        else:
                            response_text = await response.text()
                            logger.warning(f"Request failed with status {response.status}: {url}. Response: {response_text[:200]}...")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            return None
                elif method.upper() == "POST":
                    async with self.session.post(url, **kwargs) as response:
                        if response.status == 200:
                            try:
                                return await response.json()
                            except Exception as e:
                                logger.warning(f"Failed to parse JSON response from {url}: {str(e)}")
                                return None
                        elif response.status == 401:
                            logger.error(f"Authentication failed (401) for URL: {url}. Check API credentials.")
                            return None  # Don't retry auth failures
                        elif response.status == 403:
                            logger.error(f"Forbidden (403) for URL: {url}. Check API permissions.")
                            return None  # Don't retry permission failures
                        elif response.status == 429:  # Rate limited
                            retry_after = response.headers.get('retry-after', 2 ** attempt)
                            logger.warning(f"Rate limited (429). Retrying after {retry_after}s...")
                            await asyncio.sleep(int(retry_after))
                            continue
                        else:
                            response_text = await response.text()
                            logger.warning(f"Request failed with status {response.status}: {url}. Response: {response_text[:200]}...")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2 ** attempt)
                                continue
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
    
    async def make_web_request(self, url: str, method: str = "GET", **kwargs) -> Optional[str]:
        """Make HTTP request for web scraping (returns HTML content)"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        # Default headers for web scraping
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Merge default headers with provided headers
        headers = kwargs.get('headers', {})
        headers = {**default_headers, **headers}
        kwargs['headers'] = headers
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    async with self.session.get(url, **kwargs) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 403:
                            logger.warning(f"Forbidden (403) for URL: {url}. Website may be blocking scrapers.")
                            return None
                        elif response.status == 404:
                            logger.warning(f"Page not found (404) for URL: {url}")
                            return None
                        elif response.status == 429:  # Rate limited
                            retry_after = response.headers.get('retry-after', 2 ** attempt)
                            logger.warning(f"Rate limited (429). Retrying after {retry_after}s...")
                            await asyncio.sleep(int(retry_after))
                            continue
                        else:
                            response_text = await response.text()
                            logger.warning(f"Web request failed with status {response.status}: {url}. Response: {response_text[:200]}...")
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(2 ** attempt)
                                continue
                            return None
            except asyncio.TimeoutError:
                logger.warning(f"Web request timeout (attempt {attempt + 1}): {url}")
                await asyncio.sleep(1)
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Web request error (attempt {attempt + 1}): {error_msg}")
                await asyncio.sleep(1)
        
        logger.warning(f"All web scraping attempts failed for URL: {url}")
        return None
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score using LLM with fallback to traditional methods"""
        if not text or not text.strip():
            return 0.0
        
        # Try LLM-based sentiment first
        llm_sentiment = self._get_llm_sentiment(text)
        if llm_sentiment is not None:
            return llm_sentiment
        
        # Fallback to traditional methods
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
    
    def _get_llm_sentiment(self, text: str) -> Optional[float]:
        """Get sentiment score using LLM models"""
        try:
            from src.config.settings import settings
            
            # Create sentiment analysis prompt
            prompt = self._create_sentiment_prompt(text)
            
            # Try different LLM providers in order of preference
            providers = [
                ('openai', self._get_openai_sentiment),
                ('anthropic', self._get_anthropic_sentiment),
                ('huggingface', self._get_huggingface_sentiment),
                ('cohere', self._get_cohere_sentiment)
            ]
            
            # Start with preferred provider, then try others
            preferred = settings.preferred_llm_provider
            if preferred:
                providers = [(p, f) for p, f in providers if p == preferred] + [(p, f) for p, f in providers if p != preferred]
            
            for provider_name, provider_func in providers:
                try:
                    sentiment = provider_func(prompt, text)
                    if sentiment is not None:
                        logger.debug(f"Successfully got sentiment from {provider_name}: {sentiment}")
                        return sentiment
                except Exception as e:
                    logger.debug(f"LLM provider {provider_name} failed: {str(e)}")
                    continue
            
            logger.debug("All LLM providers failed, falling back to traditional methods")
            return None
            
        except Exception as e:
            logger.debug(f"LLM sentiment analysis failed: {str(e)}")
            return None
    
    def _create_sentiment_prompt(self, text: str) -> str:
        """Create a prompt for sentiment analysis"""
        return f"""
Analyze the sentiment of the following text and return ONLY a decimal number between -1.0 and 1.0:
- -1.0 = Very negative
- -0.5 = Negative  
- 0.0 = Neutral
- 0.5 = Positive
- 1.0 = Very positive

Text to analyze: "{text[:500]}"

Return only the numerical score (e.g., 0.7 or -0.3):
"""
    
    def _get_openai_sentiment(self, prompt: str, text: str) -> Optional[float]:
        """Get sentiment using OpenAI API"""
        try:
            from src.config.settings import settings
            if not settings.openai_api_key:
                return None
            
            import openai
            openai.api_key = settings.openai_api_key
            
            response = openai.ChatCompletion.create(
                model=settings.llm_model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature
            )
            
            result = response.choices[0].message.content.strip()
            return self._parse_sentiment_score(result)
            
        except Exception as e:
            logger.debug(f"OpenAI sentiment analysis failed: {str(e)}")
            return None
    
    def _get_anthropic_sentiment(self, prompt: str, text: str) -> Optional[float]:
        """Get sentiment using Anthropic Claude API"""
        try:
            from src.config.settings import settings
            if not settings.anthropic_api_key:
                return None
            
            import anthropic
            client = anthropic.Client(api_key=settings.anthropic_api_key)
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip()
            return self._parse_sentiment_score(result)
            
        except Exception as e:
            logger.debug(f"Anthropic sentiment analysis failed: {str(e)}")
            return None
    
    def _get_huggingface_sentiment(self, prompt: str, text: str) -> Optional[float]:
        """Get sentiment using Hugging Face API"""
        try:
            from src.config.settings import settings
            if not settings.huggingface_api_key:
                return None
            
            import requests
            
            # Use a sentiment-specific model
            model_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
            headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
            
            response = requests.post(model_url, headers=headers, json={"inputs": text[:500]})
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    # Convert Hugging Face sentiment to our scale
                    scores = {item['label']: item['score'] for item in result[0]}
                    
                    # Calculate weighted sentiment score
                    positive = scores.get('LABEL_2', 0)  # Positive
                    negative = scores.get('LABEL_0', 0)  # Negative  
                    neutral = scores.get('LABEL_1', 0)   # Neutral
                    
                    # Convert to -1 to 1 scale
                    sentiment = (positive - negative)
                    return max(-1.0, min(1.0, sentiment))
            
            return None
            
        except Exception as e:
            logger.debug(f"Hugging Face sentiment analysis failed: {str(e)}")
            return None
    
    def _get_cohere_sentiment(self, prompt: str, text: str) -> Optional[float]:
        """Get sentiment using Cohere API"""
        try:
            from src.config.settings import settings
            if not settings.cohere_api_key:
                return None
            
            import cohere
            co = cohere.Client(settings.cohere_api_key)
            
            response = co.generate(
                model='command',
                prompt=prompt,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature
            )
            
            result = response.generations[0].text.strip()
            return self._parse_sentiment_score(result)
            
        except Exception as e:
            logger.debug(f"Cohere sentiment analysis failed: {str(e)}")
            return None
    
    def _parse_sentiment_score(self, result: str) -> Optional[float]:
        """Parse sentiment score from LLM response"""
        try:
            # Extract number from response
            import re
            numbers = re.findall(r'-?\d*\.?\d+', result)
            if numbers:
                score = float(numbers[0])
                # Ensure score is within valid range
                return max(-1.0, min(1.0, score))
            return None
        except:
            return None
    
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
            # Generate randomized social media data instead of fixed values
            import random
            import hashlib
            
            # Create consistent seed based on brand name
            brand_hash = int(hashlib.md5(brand_id.lower().encode()).hexdigest()[:8], 16)
            random.seed(brand_hash)
            
            # Industry-based sentiment patterns
            brand_lower = brand_id.lower()
            if any(tech in brand_lower for tech in ['tech', 'microsoft', 'google', 'apple']):
                sentiment_base = random.uniform(0.65, 0.85)
                mentions_mult = random.uniform(1.2, 1.8)
            elif any(consulting in brand_lower for consulting in ['cognizant', 'tcs', 'accenture']):
                sentiment_base = random.uniform(0.60, 0.80)
                mentions_mult = random.uniform(0.8, 1.4)
            else:
                sentiment_base = random.uniform(0.55, 0.75)
                mentions_mult = random.uniform(0.9, 1.3)
            
            # Generate platform-specific data with realistic variations
            twitter_sentiment = round(sentiment_base + random.uniform(-0.1, 0.1), 3)
            facebook_sentiment = round(sentiment_base + random.uniform(-0.05, 0.05), 3)
            linkedin_sentiment = round(min(0.95, sentiment_base + 0.1 + random.uniform(-0.05, 0.05)), 3)
            
            twitter_mentions = int(400 * mentions_mult * random.uniform(0.8, 1.2))
            facebook_mentions = int(300 * mentions_mult * random.uniform(0.7, 1.3))
            linkedin_mentions = int(150 * mentions_mult * random.uniform(0.6, 1.1))
            
            total_mentions = twitter_mentions + facebook_mentions + linkedin_mentions
            overall_sentiment = round((twitter_sentiment * twitter_mentions + 
                                     facebook_sentiment * facebook_mentions + 
                                     linkedin_sentiment * linkedin_mentions) / total_mentions, 3)
            
            engagement_rate = round(random.uniform(0.025, 0.065), 4)
            
            # Randomize trending topics
            all_topics = ["service", "customer experience", "innovation", "quality", "support", 
                         "technology", "leadership", "growth", "partnership", "solutions", "digital"]
            trending_topics = random.sample(all_topics, 3)
            
            logger.info(f"Generated randomized social media mock data for {brand_id}: sentiment={overall_sentiment}, mentions={total_mentions}")
            
            return {
                "overall_sentiment": overall_sentiment,
                "mentions_count": total_mentions,
                "engagement_rate": engagement_rate,
                "platforms": {
                    "twitter": {"sentiment": twitter_sentiment, "mentions": twitter_mentions},
                    "facebook": {"sentiment": facebook_sentiment, "mentions": facebook_mentions},
                    "linkedin": {"sentiment": linkedin_sentiment, "mentions": linkedin_mentions}
                },
                "trending_topics": trending_topics
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
                logger.info(f"Starting collection from {source_type.value} for {brand_id}")
                
                # Notify progress callback that this source is starting
                if progress_callback:
                    await progress_callback(f"Collecting data from {source_type.value}...")
                
                collector = CollectorFactory.create_collector(source_type)
                async with collector:
                    data = await collector.collect_with_progress_callback(brand_id, area_id, progress_callback)
                    results[source_type.value] = data
                
                # Notify progress callback that this source completed
                if progress_callback:
                    await progress_callback(f"Completed data collection from {source_type.value}", completed_source=source_type)
                    
                logger.info(f"Successfully collected data from {source_type.value} for {brand_id}")
                
            except Exception as e:
                logger.error(f"Failed to collect from {source_type.value}: {str(e)}")
                
                # Notify progress callback about the failure
                if progress_callback:
                    await progress_callback(f"Failed to collect from {source_type.value}, using fallback data")
                
                # Use mock data as fallback
                collector = CollectorFactory.create_collector(source_type)
                results[source_type.value] = collector.get_mock_data(brand_id)
                
                # Still mark as completed (with fallback data)
                if progress_callback:
                    await progress_callback(f"Using fallback data for {source_type.value}", completed_source=source_type)
        
        # Collect from all sources concurrently
        tasks = [collect_single_source(source) for source in sources]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results 
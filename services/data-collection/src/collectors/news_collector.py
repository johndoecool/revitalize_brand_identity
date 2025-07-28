from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from src.collectors.base import BaseCollector
from src.models.schemas import DataSource
from src.config.settings import settings


class NewsCollector(BaseCollector):
    """Collector for news sentiment analysis"""
    
    def __init__(self):
        super().__init__(DataSource.NEWS)
        self.api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2"
    
    async def collect_brand_data(self, brand_id: str, area_id: str) -> Dict[str, Any]:
        """Collect news data for a brand"""
        try:
            brand_name = self.normalize_brand_name(brand_id)
            search_query = f"{brand_name}"
            
            # Add area-specific keywords if relevant
            if area_id:
                area_keywords = self._get_area_keywords(area_id)
                if area_keywords:
                    search_query += f" AND ({' OR '.join(area_keywords)})"
            
            # Get news articles from the last 30 days
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            articles = await self._fetch_news_articles(search_query, from_date)
            
            if not articles:
                logger.warning(f"No news articles found for {brand_id}, using mock data")
                return self.get_mock_data(brand_id)
            
            return self._analyze_news_sentiment(articles)
            
        except Exception as e:
            logger.error(f"Error collecting news data for {brand_id}: {str(e)}")
            return self.get_mock_data(brand_id)
    
    def _get_area_keywords(self, area_id: str) -> List[str]:
        """Get relevant keywords for a specific area"""
        area_keywords = {
            "self_service_portal": ["portal", "online", "digital", "self-service", "website", "app"],
            "employer_of_choice": ["employee", "workplace", "career", "job", "culture", "benefits"],
            "customer_service": ["customer", "service", "support", "satisfaction", "experience"],
            "digital_banking": ["digital", "mobile", "online", "banking", "fintech", "technology"],
            "innovation": ["innovation", "technology", "digital", "AI", "automation", "transformation"]
        }
        
        return area_keywords.get(area_id.lower(), [])
    
    async def _fetch_news_articles(self, query: str, from_date: str) -> List[Dict[str, Any]]:
        """Fetch news articles from News API"""
        try:
            if not self.api_key:
                logger.warning("No News API key configured, using mock data")
                return []
            
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.api_key,
                'pageSize': 100
            }
            
            url = f"{self.base_url}/everything"
            response = await self.make_request(url, params=params)
            
            if response and response.get('status') == 'ok':
                return response.get('articles', [])
            else:
                logger.warning(f"News API request failed: {response}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching news articles: {str(e)}")
            return []
    
    def _analyze_news_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of news articles"""
        if not articles:
            return self.get_mock_data("unknown")
        
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        recent_articles = []
        
        for article in articles[:50]:  # Analyze first 50 articles
            title = article.get('title', '')
            description = article.get('description', '')
            content = f"{title} {description}"
            
            sentiment_score = self.calculate_sentiment_score(content)
            sentiments.append(sentiment_score)
            
            # Categorize sentiment
            if sentiment_score > 0.1:
                positive_count += 1
                sentiment_label = "positive"
            elif sentiment_score < -0.1:
                negative_count += 1
                sentiment_label = "negative"
            else:
                neutral_count += 1
                sentiment_label = "neutral"
            
            # Add to recent articles (first 5)
            if len(recent_articles) < 5:
                recent_articles.append({
                    "title": title,
                    "sentiment": sentiment_label,
                    "published_date": article.get('publishedAt', '')[:10],  # YYYY-MM-DD format
                    "url": article.get('url', ''),
                    "source": article.get('source', {}).get('name', '')
                })
        
        # Calculate overall sentiment score
        overall_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        return {
            "score": round(overall_sentiment, 3),
            "articles_count": len(articles),
            "positive_articles": positive_count,
            "negative_articles": negative_count,
            "neutral_articles": neutral_count,
            "recent_articles": recent_articles
        }
    
    async def _fetch_alternative_news(self, brand_name: str) -> List[Dict[str, Any]]:
        """Fetch news from alternative free sources if News API is not available"""
        try:
            # This is a placeholder for alternative news sources
            # You could implement RSS feeds, web scraping from news sites, etc.
            logger.info(f"Attempting to fetch alternative news sources for {brand_name}")
            
            # For now, return empty list which will trigger mock data
            return []
            
        except Exception as e:
            logger.error(f"Error fetching alternative news: {str(e)}")
            return [] 
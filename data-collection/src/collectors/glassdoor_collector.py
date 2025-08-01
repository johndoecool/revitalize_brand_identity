from typing import Dict, Any, List, Optional
import asyncio
import re
from datetime import datetime
from loguru import logger

try:
    from bs4 import BeautifulSoup
except ImportError:
    logger.error("❌ BeautifulSoup4 is not installed. Please run: pip install beautifulsoup4==4.12.2")
    raise ImportError("Missing required dependency: beautifulsoup4. Run 'pip install beautifulsoup4==4.12.2' to fix this.")

from src.collectors.base import BaseCollector
from src.models.schemas import DataSource
from src.config.settings import settings


class GlassdoorCollector(BaseCollector):
    """Collector for Glassdoor employee reviews and ratings"""
    
    def __init__(self):
        super().__init__(DataSource.GLASSDOOR)
        self.base_url = "https://www.glassdoor.com"
    
    async def collect_brand_data(self, brand_id: str, area_id: str) -> Dict[str, Any]:
        """Collect Glassdoor data for a brand"""
        try:
            brand_name = self.normalize_brand_name(brand_id)
            
            # Search for company on Glassdoor
            company_url = await self._search_company(brand_name)
            
            if not company_url:
                logger.warning(f"Could not find Glassdoor page for {brand_id}")
                return self.get_mock_data(brand_id)
            
            # Collect company data
            company_data = await self._collect_company_data(company_url)
            reviews_data = await self._collect_reviews_data(company_url)
            
            return self._aggregate_glassdoor_data(company_data, reviews_data)
            
        except Exception as e:
            logger.error(f"Error collecting Glassdoor data for {brand_id}: {str(e)}")
            return self.get_mock_data(brand_id)
    
    async def _search_company(self, brand_name: str) -> Optional[str]:
        """Search for company on Glassdoor"""
        try:
            # For demo purposes, we'll simulate finding a company by trying to access the URL
            # In production, this would involve searching Glassdoor's search API or web scraping
            
            search_url = f"{self.base_url}/Reviews/company-reviews.htm"
            
            # Note: Glassdoor has anti-scraping measures, so this is a simplified implementation
            # In production, you'd need to handle CAPTCHAs, rate limiting, and use proper scraping tools
            
            logger.info(f"Searching for {brand_name} on Glassdoor")
            
            # Try to verify the company exists (with proper session handling)
            if self.session:
                try:
                    # Attempt a basic search to verify the domain is accessible
                    response = await self.make_web_request(search_url)
                    if response:
                        logger.debug("Glassdoor is accessible, using mock company URL")
                except Exception as e:
                    logger.debug(f"Glassdoor access test failed: {str(e)}")
            
            # Return mock URL for demonstration (this works even without real web scraping)
            return f"{self.base_url}/Reviews/{brand_name.replace(' ', '-')}-Reviews-E123456.htm"
            
        except Exception as e:
            logger.error(f"Error searching company on Glassdoor: {str(e)}")
            return None
    
    async def _collect_company_data(self, company_url: str) -> Dict[str, Any]:
        """Collect basic company information"""
        try:
            # In a real implementation, this would scrape the company overview page
            # For MVP, we'll return structured mock data that varies by company
            
            logger.info(f"Collecting company data from {company_url}")
            
            # Simulate web scraping delay
            await asyncio.sleep(1)
            
            # Extract company name from URL for variation in mock data
            company_name = self._extract_company_name_from_url(company_url)
            
            # Generate realistic data based on company name hash
            rating_base = (hash(company_name) % 30) / 10 + 3.0  # Range 3.0-6.0, then normalize
            rating = min(5.0, max(1.0, rating_base))
            
            return {
                "overall_rating": round(rating, 1),
                "reviews_count": (hash(company_name) % 300) + 50,  # 50-350 reviews
                "company_name": company_name
            }
            
        except Exception as e:
            logger.error(f"Error collecting company data: {str(e)}")
            return {
                "overall_rating": 3.5,
                "reviews_count": 100,
                "company_name": "Unknown Company"
            }
    
    async def _collect_reviews_data(self, company_url: str) -> Dict[str, Any]:
        """Collect and analyze employee reviews"""
        try:
            logger.info(f"Collecting reviews data from {company_url}")
            
            # Simulate web scraping delay
            await asyncio.sleep(2)
            
            # In production, this would scrape actual reviews
            # For MVP, we'll generate realistic review data
            
            company_name = self._extract_company_name_from_url(company_url)
            
            # Generate pros and cons based on common themes
            pros_options = [
                "Good work-life balance",
                "Competitive salary",
                "Great benefits package",
                "Supportive management",
                "Learning opportunities",
                "Flexible working hours",
                "Collaborative team environment",
                "Job security",
                "Career growth opportunities",
                "Good company culture"
            ]
            
            cons_options = [
                "Limited career advancement",
                "Outdated technology",
                "Poor communication",
                "High workload",
                "Bureaucratic processes",
                "Limited training opportunities",
                "Inconsistent management",
                "Low pay increases",
                "Long working hours",
                "Lack of recognition"
            ]
            
            # Select pros and cons based on company name hash for consistency
            hash_val = hash(company_name)
            selected_pros = [pros_options[i] for i in [(hash_val + i) % len(pros_options) for i in range(3)]]
            selected_cons = [cons_options[i] for i in [(hash_val * 2 + i) % len(cons_options) for i in range(3)]]
            
            # Generate recommendation and CEO approval rates
            recommendation_rate = (hash_val % 50) / 100 + 0.5  # 0.5-1.0
            ceo_approval = (hash_val % 40) / 100 + 0.6  # 0.6-1.0
            
            return {
                "pros": selected_pros,
                "cons": selected_cons,
                "recommendation_rate": round(recommendation_rate, 2),
                "ceo_approval": round(ceo_approval, 2)
            }
            
        except Exception as e:
            logger.error(f"Error collecting reviews data: {str(e)}")
            return {
                "pros": ["Good benefits", "Team collaboration"],
                "cons": ["Limited growth", "Bureaucracy"],
                "recommendation_rate": 0.75,
                "ceo_approval": 0.80
            }
    
    def _aggregate_glassdoor_data(self, company_data: Dict[str, Any], reviews_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate all Glassdoor data"""
        try:
            return {
                "overall_rating": company_data.get("overall_rating", 3.5),
                "reviews_count": company_data.get("reviews_count", 100),
                "pros": reviews_data.get("pros", []),
                "cons": reviews_data.get("cons", []),
                "recommendation_rate": reviews_data.get("recommendation_rate", 0.75),
                "ceo_approval": reviews_data.get("ceo_approval", 0.80)
            }
        except Exception as e:
            logger.error(f"Error aggregating Glassdoor data: {str(e)}")
            return self.get_mock_data("unknown")
    
    def _extract_company_name_from_url(self, url: str) -> str:
        """Extract company name from Glassdoor URL"""
        try:
            # Extract company name from URL pattern like:
            # https://www.glassdoor.com/Reviews/Company-Name-Reviews-E123456.htm
            match = re.search(r'/Reviews/(.+?)-Reviews-E\d+\.htm', url)
            if match:
                return match.group(1).replace('-', ' ')
            else:
                return "Unknown Company"
        except Exception:
            return "Unknown Company"
    
    async def _parse_reviews_page(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse individual reviews from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            reviews = []
            
            # This would contain actual parsing logic for Glassdoor's HTML structure
            # For MVP, we'll return mock review data
            
            mock_reviews = [
                {
                    "rating": 4,
                    "title": "Great place to work",
                    "pros": "Good benefits and work-life balance",
                    "cons": "Limited career growth",
                    "date": "2024-01-15"
                },
                {
                    "rating": 3,
                    "title": "Average experience",
                    "pros": "Stable job",
                    "cons": "Outdated processes",
                    "date": "2024-01-10"
                }
            ]
            
            return mock_reviews
            
        except Exception as e:
            logger.error(f"Error parsing reviews: {str(e)}")
            return []
    
    def _analyze_review_sentiment(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment from reviews"""
        if not reviews:
            return {"positive_ratio": 0.5, "themes": []}
        
        positive_count = 0
        themes = []
        
        for review in reviews:
            rating = review.get('rating', 3)
            if rating >= 4:
                positive_count += 1
            
            # Extract themes from pros/cons
            pros = review.get('pros', '')
            cons = review.get('cons', '')
            themes.extend(self._extract_themes(f"{pros} {cons}"))
        
        positive_ratio = positive_count / len(reviews)
        unique_themes = list(set(themes))[:5]  # Top 5 unique themes
        
        return {
            "positive_ratio": round(positive_ratio, 2),
            "themes": unique_themes
        }
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract common themes from review text"""
        # Simple keyword extraction - could be enhanced with NLP
        theme_keywords = {
            "work-life balance": ["balance", "flexible", "hours"],
            "management": ["management", "manager", "leadership"],
            "culture": ["culture", "environment", "team"],
            "benefits": ["benefits", "insurance", "vacation"],
            "growth": ["growth", "career", "advancement", "promotion"]
        }
        
        text_lower = text.lower()
        themes = []
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes 
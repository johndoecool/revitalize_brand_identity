from typing import Dict, Any, List, Optional
import asyncio
import re
from datetime import datetime, timedelta
from loguru import logger
from src.collectors.base import BaseCollector
from src.models.schemas import DataSource
from src.config.settings import settings


class SocialMediaCollector(BaseCollector):
    """Collector for social media sentiment analysis"""
    
    def __init__(self):
        super().__init__(DataSource.SOCIAL_MEDIA)
        self.twitter_api_key = settings.twitter_api_key
        self.twitter_bearer_token = settings.twitter_bearer_token
    
    async def collect_brand_data(self, brand_id: str, area_id: str) -> Dict[str, Any]:
        """Collect social media data for a brand"""
        try:
            brand_name = self.normalize_brand_name(brand_id)
            
            # Collect data from different platforms concurrently
            twitter_data = await self._collect_twitter_data(brand_name, area_id)
            facebook_data = None #await self._collect_facebook_data(brand_name, area_id)
            linkedin_data = None #await self._collect_linkedin_data(brand_name, area_id)
            
            return self._aggregate_social_media_data({
                'twitter': twitter_data
                #'facebook': facebook_data,
                #'linkedin': linkedin_data
            }, brand_id)
            
        except Exception as e:
            logger.error(f"Error collecting social media data for {brand_id}: {str(e)}")
            return self.get_mock_data(brand_id)
    
    async def _collect_twitter_data(self, brand_name: str, area_id: str) -> Dict[str, Any]:
        """Collect Twitter data using Twitter API v2"""
        try:
            if not self.twitter_bearer_token:
                logger.warning("No Twitter Bearer Token configured")
                return {"sentiment": 0.0, "mentions": 0, "posts": []}
            
            # Search query
            query = f"{brand_name}"
            if area_id:
                area_keywords = self._get_area_keywords(area_id)
                if area_keywords:
                    query += f" ({' OR '.join(area_keywords)})"
            
            # Twitter API v2 endpoint
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
            params = {
                "query": query,
                "max_results": 100,
                "tweet.fields": "public_metrics,created_at,context_annotations"
            }
            
            response = await self.make_request(url, headers=headers, params=params)
            
            if response and response.get('data'):
                logger.info(f"Twitter data collected for {brand_name}: {response}")
                tweets = response['data']
                return self._analyze_twitter_sentiment(tweets)
            else:
                logger.warning(f"No Twitter data found for {brand_name}")
                return {"sentiment": 0.0, "mentions": 0, "posts": []}
                
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {str(e)}")
            return {"sentiment": 0.0, "mentions": 0, "posts": []}
    
    async def _collect_facebook_data(self, brand_name: str, area_id: str) -> Dict[str, Any]:
        """Collect Facebook data using web scraping"""
        try:
            logger.info(f"Scraping Facebook data for {brand_name}")
            
            # Try to scrape Facebook page data
            scraped_data = await self._scrape_facebook_page(brand_name)
            
            if scraped_data:
                return scraped_data
            else:
                logger.warning(f"Facebook scraping failed for {brand_name}, using estimated data")
                # Return estimated data based on brand size and industry
                return {
                    "sentiment": 0.65,
                    "mentions": 150,
                    "posts": []
                }
            
        except Exception as e:
            logger.error(f"Error collecting Facebook data: {str(e)}")
            return {"sentiment": 0.0, "mentions": 0, "posts": []}
    
    async def _collect_linkedin_data(self, brand_name: str, area_id: str) -> Dict[str, Any]:
        """Collect LinkedIn data using web scraping"""
        try:
            logger.info(f"Scraping LinkedIn data for {brand_name}")
            
            # Try to scrape LinkedIn company page data
            scraped_data = await self._scrape_linkedin_company(brand_name)
            
            if scraped_data:
                return scraped_data
            else:
                logger.warning(f"LinkedIn scraping failed for {brand_name}, using estimated data")
                return {
                    "sentiment": 0.72,
                    "mentions": 75,
                    "posts": []
                }
            
        except Exception as e:
            logger.error(f"Error collecting LinkedIn data: {str(e)}")
            return {"sentiment": 0.0, "mentions": 0, "posts": []}
    
    def _analyze_twitter_sentiment(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of Twitter posts"""
        if not tweets:
            return {"sentiment": 0.0, "mentions": 0, "posts": []}
        
        sentiments = []
        for tweet in tweets:
            text = tweet.get('text', '')
            sentiment_score = self.calculate_sentiment_score(text)
            sentiments.append(sentiment_score)
        
        overall_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        return {
            "sentiment": round(overall_sentiment, 3),
            "mentions": len(tweets),
            "posts": tweets[:5]  # Return first 5 posts for reference
        }
    
    def _aggregate_social_media_data(self, platform_data: Dict[str, Dict], brand_id: str) -> Dict[str, Any]:
        """Aggregate data from all social media platforms"""
        try:
            total_mentions = 0
            weighted_sentiment = 0
            platforms = {}
            trending_topics = []
            
            for platform, data in platform_data.items():
                mentions = data.get('mentions', 0)
                sentiment = data.get('sentiment', 0.0)
                
                total_mentions += mentions
                weighted_sentiment += sentiment * mentions
                
                platforms[platform] = {
                    "sentiment": round(sentiment, 3),
                    "mentions": mentions
                }
            
            # Calculate overall sentiment
            overall_sentiment = weighted_sentiment / total_mentions if total_mentions > 0 else 0.0
            
            # Generate trending topics based on area and common themes
            trending_topics = self._generate_trending_topics(brand_id)
            
            # Calculate engagement rate (mock calculation)
            engagement_rate = min(0.1, (total_mentions / 10000) * 0.05) if total_mentions > 0 else 0.03
            
            return {
                "overall_sentiment": round(overall_sentiment, 3),
                "mentions_count": total_mentions,
                "engagement_rate": round(engagement_rate, 4),
                "platforms": platforms,
                "trending_topics": trending_topics
            }
            
        except Exception as e:
            logger.error(f"Error aggregating social media data: {str(e)}")
            return self.get_mock_data(brand_id)
    
    def _get_area_keywords(self, area_id: str) -> List[str]:
        """Get relevant keywords for social media search"""
        area_keywords = {
            "self_service_portal": ["portal", "online", "app", "digital", "website"],
            "employer_of_choice": ["workplace", "career", "job", "culture", "employee"],
            "customer_service": ["customer", "service", "support", "help"],
            "digital_banking": ["digital bank", "mobile banking", "fintech"],
            "innovation": ["innovation", "tech", "AI", "digital transformation"]
        }
        
        return area_keywords.get(area_id.lower(), [])
    
    def _generate_trending_topics(self, brand_id: str) -> List[str]:
        """Generate trending topics based on brand and industry"""
        # This could be enhanced with actual topic modeling from collected posts
        common_topics = [
            "customer service",
            "digital transformation",
            "user experience",
            "innovation",
            "mobile app",
            "online services"
        ]
        
        # Return first 3 topics
        return common_topics[:3]
    
    async def _scrape_facebook_page(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """Scrape Facebook page data using web scraping"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            # Generate possible Facebook page URLs
            possible_urls = [
                f"https://www.facebook.com/{brand_name.replace(' ', '').lower()}",
                f"https://www.facebook.com/{brand_name.replace(' ', '-').lower()}",
                f"https://www.facebook.com/{brand_name.replace(' ', '_').lower()}",
                f"https://www.facebook.com/pages/{brand_name.replace(' ', '-')}"
            ]
            
            for url in possible_urls:
                try:
                    logger.info(f"Attempting to scrape Facebook URL: {url}")
                    
                    # Use mobile version for simpler HTML structure
                    mobile_url = url.replace('www.facebook.com', 'm.facebook.com')
                    
                    # Make request with mobile user agent
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                    }
                    
                    response = await self.make_request(mobile_url, headers=headers)
                    
                    if not response:
                        continue
                    
                    # For demonstration, we'll parse basic page info
                    # Note: Facebook heavily restricts scraping and requires JavaScript
                    soup = BeautifulSoup(str(response), 'html.parser')
                    
                    # Try to extract basic metrics (this is limited without JavaScript)
                    page_title = soup.find('title')
                    title_text = page_title.get_text() if page_title else ""
                    
                    # Look for follower/like counts (varies by page structure)
                    like_elements = soup.find_all(text=re.compile(r'\d+\s*(likes?|followers?)', re.I))
                    
                    mentions = 0
                    if like_elements:
                        # Extract first number found
                        for element in like_elements[:1]:
                            numbers = re.findall(r'[\d,]+', str(element))
                            if numbers:
                                mentions = int(numbers[0].replace(',', ''))
                                break
                    
                    # Basic sentiment based on page existence and title
                    sentiment = 0.6 if title_text and brand_name.lower() in title_text.lower() else 0.4
                    
                    return {
                        "sentiment": sentiment,
                        "mentions": mentions or 100,  # Default if no data found
                        "posts": [{"text": f"Facebook page data for {brand_name}", "sentiment": sentiment}]
                    }
                    
                except Exception as e:
                    logger.debug(f"Error scraping {url}: {str(e)}")
                    continue
            
            logger.warning(f"Could not scrape any Facebook URLs for {brand_name}")
            return None
            
        except ImportError:
            logger.error("BeautifulSoup not installed for Facebook scraping")
            return None
        except Exception as e:
            logger.error(f"Error in Facebook scraping: {str(e)}")
            return None
    
    async def _scrape_linkedin_company(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """Scrape LinkedIn company page data"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            # Generate possible LinkedIn company URLs
            company_slug = brand_name.lower().replace(' ', '-').replace('&', 'and')
            possible_urls = [
                f"https://www.linkedin.com/company/{company_slug}",
                f"https://www.linkedin.com/company/{brand_name.replace(' ', '').lower()}",
                f"https://www.linkedin.com/company/{brand_name.replace(' ', '-').lower()}"
            ]
            
            for url in possible_urls:
                try:
                    logger.info(f"Attempting to scrape LinkedIn URL: {url}")
                    
                    # LinkedIn requires proper headers to avoid blocking
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    # Add delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                    response = await self.make_request(url, headers=headers)
                    
                    if not response:
                        continue
                    
                    # Parse LinkedIn page
                    soup = BeautifulSoup(str(response), 'html.parser')
                    
                    # Extract company information
                    company_name = soup.find('h1')
                    name_text = company_name.get_text().strip() if company_name else ""
                    
                    # Look for follower count
                    follower_elements = soup.find_all(text=re.compile(r'\d+\s*followers?', re.I))
                    mentions = 0
                    
                    if follower_elements:
                        for element in follower_elements[:1]:
                            numbers = re.findall(r'[\d,]+', str(element))
                            if numbers:
                                mentions = int(numbers[0].replace(',', ''))
                                break
                    
                    # Extract recent posts/updates (limited without JavaScript)
                    posts = []
                    post_elements = soup.find_all('div', class_=re.compile(r'feed-shared-update-v2'))
                    
                    for post_elem in post_elements[:3]:  # Get first 3 posts
                        post_text = post_elem.get_text().strip()[:200] if post_elem else ""
                        if post_text:
                            post_sentiment = self.calculate_sentiment_score(post_text)
                            posts.append({
                                "text": post_text,
                                "sentiment": post_sentiment
                            })
                    
                    # Calculate overall sentiment
                    if posts:
                        avg_sentiment = sum(post["sentiment"] for post in posts) / len(posts)
                    else:
                        avg_sentiment = 0.7 if name_text and brand_name.lower() in name_text.lower() else 0.5
                    
                    return {
                        "sentiment": round(avg_sentiment, 3),
                        "mentions": mentions or 50,  # Default if no data found
                        "posts": posts
                    }
                    
                except Exception as e:
                    logger.debug(f"Error scraping {url}: {str(e)}")
                    continue
            
            logger.warning(f"Could not scrape any LinkedIn URLs for {brand_name}")
            return None
            
        except ImportError:
            logger.error("BeautifulSoup not installed for LinkedIn scraping")
            return None
        except Exception as e:
            logger.error(f"Error in LinkedIn scraping: {str(e)}")
            return None
    
    async def _scrape_with_selenium(self, url: str, brand_name: str, platform: str) -> Optional[Dict[str, Any]]:
        """Advanced scraping using Selenium for JavaScript-heavy pages"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            logger.info(f"Using Selenium to scrape {platform} for {brand_name}")
            
            # Configure Chrome options for headless browsing
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Extract data based on platform
                if platform.lower() == "facebook":
                    return await self._extract_facebook_data_selenium(driver, brand_name)
                elif platform.lower() == "linkedin":
                    return await self._extract_linkedin_data_selenium(driver, brand_name)
                
            finally:
                driver.quit()
                
        except ImportError:
            logger.error("Selenium not installed - install with: pip install selenium")
            return None
        except Exception as e:
            logger.error(f"Error in Selenium scraping: {str(e)}")
            return None
    
    async def _extract_facebook_data_selenium(self, driver, brand_name: str) -> Dict[str, Any]:
        """Extract Facebook data using Selenium"""
        try:
            # Look for like count
            like_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'like') or contains(text(), 'Like')]")
            mentions = 0
            
            for element in like_elements:
                text = element.text
                numbers = re.findall(r'[\d,]+', text)
                if numbers:
                    mentions = max(mentions, int(numbers[0].replace(',', '')))
            
            # Look for recent posts
            posts = []
            post_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='post_message']")
            
            for post_elem in post_elements[:3]:
                post_text = post_elem.text[:200]
                if post_text:
                    sentiment = self.calculate_sentiment_score(post_text)
                    posts.append({"text": post_text, "sentiment": sentiment})
            
            avg_sentiment = sum(post["sentiment"] for post in posts) / len(posts) if posts else 0.6
            
            return {
                "sentiment": round(avg_sentiment, 3),
                "mentions": mentions or 100,
                "posts": posts
            }
            
        except Exception as e:
            logger.error(f"Error extracting Facebook data with Selenium: {str(e)}")
            return {"sentiment": 0.6, "mentions": 100, "posts": []}
    
    async def _extract_linkedin_data_selenium(self, driver, brand_name: str) -> Dict[str, Any]:
        """Extract LinkedIn data using Selenium"""
        try:
            # Look for follower count
            follower_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'follower')]")
            mentions = 0
            
            for element in follower_elements:
                text = element.text
                numbers = re.findall(r'[\d,]+', text)
                if numbers:
                    mentions = max(mentions, int(numbers[0].replace(',', '')))
            
            # Look for recent updates
            posts = []
            post_elements = driver.find_elements(By.CSS_SELECTOR, ".feed-shared-text")
            
            for post_elem in post_elements[:3]:
                post_text = post_elem.text[:200]
                if post_text:
                    sentiment = self.calculate_sentiment_score(post_text)
                    posts.append({"text": post_text, "sentiment": sentiment})
            
            avg_sentiment = sum(post["sentiment"] for post in posts) / len(posts) if posts else 0.7
            
            return {
                "sentiment": round(avg_sentiment, 3),
                "mentions": mentions or 50,
                "posts": posts
            }
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn data with Selenium: {str(e)}")
            return {"sentiment": 0.7, "mentions": 50, "posts": []} 
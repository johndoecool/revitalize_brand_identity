"""
Social Media Scraper

Specialized scraper for social media platforms using the common WebScraper.
Provides platform-specific methods and data extraction logic.
"""

import re
from typing import Dict, List, Optional, Any
from loguru import logger

from .web_scraper import WebScraper, ScrapingResult
from .scraper_config import ScraperConfig, SiteConfig, SITE_CONFIGS

class SocialMediaScraper:
    """Specialized scraper for social media platforms"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.web_scraper = WebScraper(self.config)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.web_scraper.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.web_scraper.__aexit__(exc_type, exc_val, exc_tb)
    
    async def scrape_facebook_page(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Facebook page data for a brand
        
        Args:
            brand_name: Name of the brand to search for
            
        Returns:
            Dictionary with sentiment, mentions, and posts data or None if failed
        """
        # Generate possible Facebook page URLs (desktop-focused)
        possible_urls = [
            # Primary desktop URLs (most likely to work)
            f"https://www.facebook.com/{brand_name.replace(' ', '').lower()}",
            f"https://www.facebook.com/{brand_name.replace(' ', '-').lower()}", 
            f"https://www.facebook.com/{brand_name.replace(' ', '_').lower()}",
            # Business/official page patterns  
            f"https://www.facebook.com/{brand_name.replace(' ', '').lower()}official",
            f"https://www.facebook.com/{brand_name.replace(' ', '').lower()}inc",
            # Common brand name variations
            f"https://www.facebook.com/{brand_name.replace(' ', '').replace('&', 'and').lower()}",
            f"https://www.facebook.com/{brand_name.split()[0].lower()}",  # First word only
            # Legacy pages format (as last resort)
            f"https://www.facebook.com/pages/{brand_name.replace(' ', '-')}"
        ]
        
        facebook_config = SITE_CONFIGS['facebook']
        
        for url in possible_urls:
            try:
                logger.info(f"Attempting to scrape Facebook URL: {url}")
                
                result = await self.web_scraper.scrape_url(url, facebook_config)
                
                if result.success and result.html:
                    # Check for login redirects
                    if 'login' in result.html.lower() or 'sign in' in result.html.lower():
                        logger.debug(f"Got login redirect for {url}")
                        continue
                    
                    # Extract Facebook-specific data
                    data = self._extract_facebook_data(result, brand_name)
                    if data:
                        return data
                        
            except Exception as e:
                logger.debug(f"Error scraping Facebook URL {url}: {str(e)}")
                continue
        
        logger.warning(f"Could not scrape any Facebook URLs for {brand_name}")
        return None
    
    async def scrape_linkedin_company(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrape LinkedIn company page data for a brand
        
        Args:
            brand_name: Name of the brand to search for
            
        Returns:
            Dictionary with sentiment, mentions, and posts data or None if failed
        """
        # Generate possible LinkedIn company URLs
        company_slug = brand_name.lower().replace(' ', '-').replace('&', 'and')
        possible_urls = [
            f"https://www.linkedin.com/company/{company_slug}",
            f"https://www.linkedin.com/company/{brand_name.replace(' ', '').lower()}",
            f"https://www.linkedin.com/company/{brand_name.replace(' ', '-').lower()}"
        ]
        
        linkedin_config = SITE_CONFIGS['linkedin']
        
        for url in possible_urls:
            try:
                logger.info(f"Attempting to scrape LinkedIn URL: {url}")
                
                result = await self.web_scraper.scrape_url(url, linkedin_config)
                
                if result.success and result.html:
                    # Check for LinkedIn's anti-bot measures
                    if 'challenge' in result.html.lower() or 'authwall' in result.html.lower():
                        logger.debug(f"LinkedIn challenge detected for {url}")
                        continue
                    
                    # Extract LinkedIn-specific data
                    data = self._extract_linkedin_data(result, brand_name)
                    if data:
                        return data
                        
            except Exception as e:
                logger.debug(f"Error scraping LinkedIn URL {url}: {str(e)}")
                continue
        
        logger.warning(f"Could not scrape any LinkedIn URLs for {brand_name}")
        return None
    
    async def scrape_twitter_profile(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Twitter/X profile data for a brand
        
        Args:
            brand_name: Name of the brand to search for
            
        Returns:
            Dictionary with sentiment, mentions, and posts data or None if failed
        """
        # Generate possible Twitter URLs
        handle = brand_name.lower().replace(' ', '').replace('.', '')
        possible_urls = [
            f"https://twitter.com/{handle}",
            f"https://twitter.com/{brand_name.replace(' ', '_').lower()}",
            f"https://x.com/{handle}"
        ]
        
        twitter_config = SITE_CONFIGS['twitter']
        
        for url in possible_urls:
            try:
                logger.info(f"Attempting to scrape Twitter URL: {url}")
                
                result = await self.web_scraper.scrape_url(url, twitter_config)
                
                if result.success and result.html:
                    # Extract Twitter-specific data
                    data = self._extract_twitter_data(result, brand_name)
                    if data:
                        return data
                        
            except Exception as e:
                logger.debug(f"Error scraping Twitter URL {url}: {str(e)}")
                continue
        
        logger.warning(f"Could not scrape any Twitter URLs for {brand_name}")
        return None
    
    def _extract_facebook_data(self, result: ScrapingResult, brand_name: str) -> Optional[Dict[str, Any]]:
        """Extract Facebook-specific data from scraping result"""
        try:
            # Use extracted structured data if available
            extracted = result.extracted_data
            
            # Get follower/like count
            mentions = 0
            if 'follower_count' in extracted:
                mentions = extracted['follower_count']
            else:
                # Fallback to regex extraction
                like_patterns = [
                    r'(\d+(?:,\d+)*)\s*(?:people\s+)?like',
                    r'(\d+(?:,\d+)*)\s*followers?',
                    r'(\d+(?:,\d+)*)\s*likes?'
                ]
                
                for pattern in like_patterns:
                    matches = re.findall(pattern, result.html, re.IGNORECASE)
                    if matches:
                        try:
                            mentions = int(matches[0].replace(',', ''))
                            break
                        except ValueError:
                            continue
            
            # Extract title for basic sentiment
            title_text = extracted.get('title', '')
            
            # Basic sentiment calculation (will be enhanced by LLM in the collector)
            has_brand_mention = brand_name.lower() in title_text.lower()
            base_sentiment = 0.6 if has_brand_mention else 0.4
            
            logger.info(f"Extracted Facebook data for {brand_name}: {mentions} mentions")
            
            return {
                "sentiment": base_sentiment,
                "mentions": mentions or 100,  # Default if no data found
                "posts": [{
                    "text": f"Facebook page data for {brand_name} - {title_text[:100]}",
                    "sentiment": base_sentiment,
                    "source": "facebook"
                }],
                "raw_data": {
                    "title": title_text,
                    "extracted_fields": extracted
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting Facebook data: {str(e)}")
            return None
    
    def _extract_linkedin_data(self, result: ScrapingResult, brand_name: str) -> Optional[Dict[str, Any]]:
        """Extract LinkedIn-specific data from scraping result"""
        try:
            extracted = result.extracted_data
            
            # Get follower count
            mentions = 0
            if 'follower_count' in extracted:
                mentions = extracted['follower_count']
            else:
                # Fallback to regex extraction with K/M/B support
                follower_patterns = [
                    r'(\d+(?:,\d+)*)\s*followers?',
                    r'(\d+(?:,\d+)*)\s*employees?',
                    r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*followers?'
                ]
                
                for pattern in follower_patterns:
                    matches = re.findall(pattern, result.html, re.IGNORECASE)
                    if matches:
                        try:
                            follower_text = matches[0].replace(',', '')
                            # Handle K, M, B suffixes
                            if follower_text.endswith('K'):
                                mentions = int(float(follower_text[:-1]) * 1000)
                            elif follower_text.endswith('M'):
                                mentions = int(float(follower_text[:-1]) * 1000000)
                            elif follower_text.endswith('B'):
                                mentions = int(float(follower_text[:-1]) * 1000000000)
                            else:
                                mentions = int(follower_text)
                            break
                        except (ValueError, TypeError):
                            continue
            
            # Extract company info
            title_text = extracted.get('title', '')
            company_info = extracted.get('company_info', '')
            
            # Extract posts if available
            posts = []
            if 'posts' in extracted and isinstance(extracted['posts'], list):
                for post_text in extracted['posts'][:3]:
                    if post_text and len(post_text) > 20:
                        posts.append({
                            "text": post_text[:200],
                            "sentiment": 0.5,  # Will be calculated by LLM
                            "source": "linkedin"
                        })
            
            # Basic sentiment
            has_brand_mention = brand_name.lower() in title_text.lower()
            base_sentiment = 0.7 if has_brand_mention else 0.5
            
            logger.info(f"Extracted LinkedIn data for {brand_name}: {mentions} followers")
            
            return {
                "sentiment": base_sentiment,
                "mentions": mentions or 50,
                "posts": posts or [{
                    "text": f"LinkedIn company page for {brand_name} - {title_text[:100]}",
                    "sentiment": base_sentiment,
                    "source": "linkedin"
                }],
                "raw_data": {
                    "title": title_text,
                    "company_info": company_info,
                    "extracted_fields": extracted
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn data: {str(e)}")
            return None
    
    def _extract_twitter_data(self, result: ScrapingResult, brand_name: str) -> Optional[Dict[str, Any]]:
        """Extract Twitter-specific data from scraping result"""
        try:
            extracted = result.extracted_data
            
            # Get follower count
            mentions = 0
            if 'follower_count' in extracted:
                mentions = extracted['follower_count']
            
            # Extract posts
            posts = []
            if 'posts' in extracted and isinstance(extracted['posts'], list):
                for post_text in extracted['posts'][:5]:
                    if post_text and len(post_text) > 10:
                        posts.append({
                            "text": post_text[:280],  # Twitter character limit
                            "sentiment": 0.5,  # Will be calculated by LLM
                            "source": "twitter"
                        })
            
            # Basic sentiment
            title_text = extracted.get('title', '')
            base_sentiment = 0.6
            
            logger.info(f"Extracted Twitter data for {brand_name}: {mentions} followers, {len(posts)} posts")
            
            return {
                "sentiment": base_sentiment,
                "mentions": mentions or 25,
                "posts": posts or [{
                    "text": f"Twitter profile for {brand_name}",
                    "sentiment": base_sentiment,
                    "source": "twitter"
                }],
                "raw_data": {
                    "title": title_text,
                    "extracted_fields": extracted
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting Twitter data: {str(e)}")
            return None
    
    async def scrape_generic_website(self, url: str, custom_selectors: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """
        Scrape any website with custom selectors
        
        Args:
            url: URL to scrape
            custom_selectors: Custom CSS selectors for data extraction
            
        Returns:
            Dictionary with extracted data or None if failed
        """
        try:
            result = await self.web_scraper.scrape_url(url, custom_selectors=custom_selectors)
            
            if result.success:
                return {
                    "url": url,
                    "success": True,
                    "extracted_data": result.extracted_data,
                    "content_length": len(result.content) if result.content else 0,
                    "status_code": result.status_code
                }
            else:
                return {
                    "url": url,
                    "success": False,
                    "error": result.error
                }
                
        except Exception as e:
            logger.error(f"Error scraping generic website {url}: {str(e)}")
            return None 
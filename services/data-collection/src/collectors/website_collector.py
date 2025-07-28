from typing import Dict, Any, List, Optional
import asyncio
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime
from loguru import logger
from bs4 import BeautifulSoup
from src.collectors.base import BaseCollector
from src.models.schemas import DataSource
from src.config.settings import settings


class WebsiteCollector(BaseCollector):
    """Collector for website performance and UX analysis"""
    
    def __init__(self):
        super().__init__(DataSource.WEBSITE)
    
    async def collect_brand_data(self, brand_id: str, area_id: str) -> Dict[str, Any]:
        """Collect website analysis data for a brand"""
        try:
            brand_name = self.normalize_brand_name(brand_id)
            
            # Find brand website URL
            website_url = await self._find_brand_website(brand_name)
            
            if not website_url:
                logger.warning(f"Could not find website for {brand_id}")
                return self.get_mock_data(brand_id)
            
            # Perform comprehensive website analysis
            analysis_results = await self._analyze_website(website_url, area_id)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error collecting website data for {brand_id}: {str(e)}")
            return self.get_mock_data(brand_id)
    
    async def _find_brand_website(self, brand_name: str) -> Optional[str]:
        """Find the official website URL for a brand"""
        try:
            # For MVP, we'll simulate finding websites
            # In production, this could use search APIs or a database of known brands
            
            common_domains = [
                f"https://www.{brand_name.replace(' ', '').lower()}.com",
                f"https://{brand_name.replace(' ', '').lower()}.com",
                f"https://www.{brand_name.replace(' ', '-').lower()}.com",
                f"https://{brand_name.replace(' ', '-').lower()}.com"
            ]
            
            # Test each potential URL
            for url in common_domains:
                try:
                    response = await self.make_request(url, method="GET")
                    if response is not None:  # If we get any response, assume it's valid
                        logger.info(f"Found website for {brand_name}: {url}")
                        return url
                except Exception:
                    continue
            
            # If no direct match, return a mock URL for demonstration
            mock_url = f"https://www.{brand_name.replace(' ', '').lower()}.com"
            logger.info(f"Using mock URL for {brand_name}: {mock_url}")
            return mock_url
            
        except Exception as e:
            logger.error(f"Error finding website for {brand_name}: {str(e)}")
            return None
    
    async def _analyze_website(self, website_url: str, area_id: str) -> Dict[str, Any]:
        """Perform comprehensive website analysis"""
        try:
            # Run multiple analysis tasks concurrently
            tasks = [
                self._analyze_performance(website_url),
                self._analyze_user_experience(website_url),
                self._analyze_security(website_url),
                self._analyze_accessibility(website_url),
                self._analyze_mobile_friendliness(website_url),
                self._analyze_feature_completeness(website_url, area_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine all analysis results
            combined_results = {}
            for result in results:
                if isinstance(result, dict):
                    combined_results.update(result)
                else:
                    logger.error(f"Analysis task failed: {result}")
            
            return self._normalize_analysis_results(combined_results)
            
        except Exception as e:
            logger.error(f"Error analyzing website {website_url}: {str(e)}")
            return self.get_mock_data("unknown")
    
    async def _analyze_performance(self, website_url: str) -> Dict[str, Any]:
        """Analyze website performance metrics"""
        try:
            start_time = time.time()
            
            # Make request to measure load time
            response = await self.make_request(website_url)
            
            load_time = time.time() - start_time
            
            # Simulate additional performance metrics
            # In production, you'd use tools like Lighthouse, PageSpeed Insights API, etc.
            
            return {
                "load_time": round(load_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {str(e)}")
            return {"load_time": 3.0}
    
    async def _analyze_user_experience(self, website_url: str) -> Dict[str, Any]:
        """Analyze user experience factors"""
        try:
            # Fetch website content
            html_content = await self._fetch_html_content(website_url)
            
            if not html_content:
                return {"user_experience_score": 0.5}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Calculate UX score based on various factors
            score = 0.0
            max_score = 0.0
            
            # Check for navigation menu
            nav_elements = soup.find_all(['nav', 'ul', 'div'], class_=lambda x: x and any(
                nav_word in str(x).lower() for nav_word in ['nav', 'menu', 'header']
            ))
            if nav_elements:
                score += 0.2
            max_score += 0.2
            
            # Check for search functionality
            search_elements = soup.find_all('input', type='search')
            search_elements.extend(soup.find_all('input', placeholder=lambda x: x and 'search' in x.lower()))
            if search_elements:
                score += 0.15
            max_score += 0.15
            
            # Check for contact information
            contact_keywords = ['contact', 'phone', 'email', 'address']
            page_text = soup.get_text().lower()
            if any(keyword in page_text for keyword in contact_keywords):
                score += 0.1
            max_score += 0.1
            
            # Check for responsive design indicators
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            if viewport_meta:
                score += 0.15
            max_score += 0.15
            
            # Check for clear headings structure
            headings = soup.find_all(['h1', 'h2', 'h3'])
            if len(headings) >= 3:
                score += 0.1
            max_score += 0.1
            
            # Check for images with alt text
            images = soup.find_all('img')
            images_with_alt = [img for img in images if img.get('alt')]
            if images and len(images_with_alt) / len(images) > 0.5:
                score += 0.1
            max_score += 0.1
            
            # Base score
            score += 0.2
            max_score += 0.2
            
            ux_score = score / max_score if max_score > 0 else 0.5
            
            return {
                "user_experience_score": round(min(1.0, ux_score), 3)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing user experience: {str(e)}")
            return {"user_experience_score": 0.7}
    
    async def _analyze_security(self, website_url: str) -> Dict[str, Any]:
        """Analyze website security features"""
        try:
            security_score = 0.0
            
            # Check HTTPS
            if website_url.startswith('https://'):
                security_score += 0.4
            
            # Try to fetch security headers (mock implementation)
            try:
                # In production, you'd check for security headers like:
                # - Content-Security-Policy
                # - X-Frame-Options
                # - X-XSS-Protection
                # - Strict-Transport-Security
                
                # For MVP, simulate security score based on domain
                domain = urlparse(website_url).netloc
                if any(indicator in domain for indicator in ['bank', 'secure', 'trust']):
                    security_score += 0.3
                else:
                    security_score += 0.2
                    
                # Base security score
                security_score += 0.3
                
            except Exception:
                security_score += 0.2
            
            return {
                "security_score": round(min(1.0, security_score), 3)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing security: {str(e)}")
            return {"security_score": 0.8}
    
    async def _analyze_accessibility(self, website_url: str) -> Dict[str, Any]:
        """Analyze website accessibility features"""
        try:
            html_content = await self._fetch_html_content(website_url)
            
            if not html_content:
                return {"accessibility_score": 0.5}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            accessibility_score = 0.0
            
            # Check for alt text on images
            images = soup.find_all('img')
            if images:
                images_with_alt = [img for img in images if img.get('alt')]
                alt_ratio = len(images_with_alt) / len(images)
                accessibility_score += alt_ratio * 0.25
            else:
                accessibility_score += 0.25
            
            # Check for proper heading structure
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                accessibility_score += 0.2
            
            # Check for form labels
            forms = soup.find_all('form')
            if forms:
                labels = soup.find_all('label')
                inputs = soup.find_all('input')
                if labels and inputs and len(labels) >= len(inputs) * 0.5:
                    accessibility_score += 0.15
                else:
                    accessibility_score += 0.05
            else:
                accessibility_score += 0.15
            
            # Check for skip links or similar navigation aids
            skip_links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
            if skip_links:
                accessibility_score += 0.1
            
            # Base accessibility score
            accessibility_score += 0.3
            
            return {
                "accessibility_score": round(min(1.0, accessibility_score), 3)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing accessibility: {str(e)}")
            return {"accessibility_score": 0.75}
    
    async def _analyze_mobile_friendliness(self, website_url: str) -> Dict[str, Any]:
        """Analyze mobile friendliness"""
        try:
            html_content = await self._fetch_html_content(website_url)
            
            if not html_content:
                return {"mobile_friendliness": 0.5}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            mobile_score = 0.0
            
            # Check for viewport meta tag
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            if viewport_meta:
                mobile_score += 0.4
            
            # Check for responsive CSS frameworks
            css_links = soup.find_all('link', rel='stylesheet')
            css_content = ' '.join([link.get('href', '') for link in css_links])
            responsive_frameworks = ['bootstrap', 'foundation', 'bulma', 'materialize']
            
            if any(framework in css_content.lower() for framework in responsive_frameworks):
                mobile_score += 0.2
            
            # Check for media queries in inline CSS
            style_tags = soup.find_all('style')
            style_content = ' '.join([tag.get_text() for tag in style_tags])
            if '@media' in style_content:
                mobile_score += 0.2
            else:
                mobile_score += 0.1
            
            # Base mobile score
            mobile_score += 0.2
            
            return {
                "mobile_friendliness": round(min(1.0, mobile_score), 3)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing mobile friendliness: {str(e)}")
            return {"mobile_friendliness": 0.8}
    
    async def _analyze_feature_completeness(self, website_url: str, area_id: str) -> Dict[str, Any]:
        """Analyze feature completeness based on the specific area"""
        try:
            html_content = await self._fetch_html_content(website_url)
            
            if not html_content:
                return {"feature_completeness": 0.5}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            page_text = soup.get_text().lower()
            
            # Define expected features for different areas
            area_features = {
                "self_service_portal": [
                    "login", "account", "dashboard", "profile", "settings",
                    "self-service", "portal", "online", "digital"
                ],
                "employer_of_choice": [
                    "careers", "jobs", "apply", "benefits", "culture",
                    "employee", "work", "opportunity", "team"
                ],
                "customer_service": [
                    "support", "help", "contact", "faq", "chat",
                    "customer", "service", "assistance", "phone"
                ],
                "digital_banking": [
                    "banking", "account", "transfer", "mobile", "online",
                    "digital", "financial", "payment", "transaction"
                ]
            }
            
            expected_features = area_features.get(area_id.lower(), [
                "about", "contact", "services", "products", "support"
            ])
            
            # Calculate feature completeness
            found_features = 0
            for feature in expected_features:
                if feature in page_text:
                    found_features += 1
            
            completeness_score = found_features / len(expected_features) if expected_features else 0.5
            
            return {
                "feature_completeness": round(min(1.0, completeness_score), 3)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing feature completeness: {str(e)}")
            return {"feature_completeness": 0.7}
    
    async def _fetch_html_content(self, website_url: str) -> Optional[str]:
        """Fetch HTML content from website"""
        try:
            # For MVP, we'll simulate HTML content
            # In production, you'd fetch actual HTML content
            
            logger.info(f"Simulating HTML content fetch for {website_url}")
            
            # Return mock HTML content for analysis
            mock_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Brand Website</title>
                <style>
                    @media (max-width: 768px) {{
                        .responsive {{ display: block; }}
                    }}
                </style>
            </head>
            <body>
                <nav>
                    <ul>
                        <li><a href="#home">Home</a></li>
                        <li><a href="#about">About</a></li>
                        <li><a href="#contact">Contact</a></li>
                    </ul>
                </nav>
                <main>
                    <h1>Welcome to Our Website</h1>
                    <h2>Our Services</h2>
                    <p>We provide excellent customer service and support.</p>
                    <img src="logo.jpg" alt="Company Logo">
                    <form>
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email">
                    </form>
                </main>
                <footer>
                    <p>Contact us: info@company.com | Phone: (555) 123-4567</p>
                </footer>
            </body>
            </html>
            """
            
            return mock_html
            
        except Exception as e:
            logger.error(f"Error fetching HTML content: {str(e)}")
            return None
    
    def _normalize_analysis_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and ensure all required fields are present"""
        return {
            "user_experience_score": results.get("user_experience_score", 0.7),
            "feature_completeness": results.get("feature_completeness", 0.7),
            "security_score": results.get("security_score", 0.8),
            "accessibility_score": results.get("accessibility_score", 0.75),
            "mobile_friendliness": results.get("mobile_friendliness", 0.8),
            "load_time": results.get("load_time", 2.5)
        } 
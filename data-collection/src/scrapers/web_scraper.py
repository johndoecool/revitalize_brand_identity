"""
Generic Web Scraper

A flexible web scraping module that supports multiple scraping strategies
and can be used across different collectors and data sources.
"""

import asyncio
import random
import re
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin, urlparse
from loguru import logger
import ssl

# Import scraping dependencies with fallbacks
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from .scraper_config import ScraperConfig, SiteConfig, ScrapingStrategy, ContentType, SITE_CONFIGS

class ScrapingResult:
    """Result object for web scraping operations"""
    
    def __init__(self, url: str, success: bool = False):
        self.url = url
        self.success = success
        self.content = None
        self.html = None
        self.status_code = None
        self.headers = {}
        self.error = None
        self.extracted_data = {}
        self.metadata = {}
    
    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"ScrapingResult({status}, {self.url})"

class WebScraper:
    """Generic web scraper with multiple strategy support"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.session = None
        self.driver = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        if AIOHTTP_AVAILABLE:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            # Create SSL context - this will be the default for most sites
            ssl_context = ssl.create_default_context()
            
            # For the main session, we'll create a secure default
            # Individual requests will create temporary sessions if SSL needs to be disabled
            connector = aiohttp.TCPConnector(
                limit=10,
                verify_ssl=self.config.verify_ssl,
                ssl_context=ssl_context
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.driver:
            self.driver.quit()
    
    async def scrape_url(self, url: str, site_config: SiteConfig = None, 
                        custom_selectors: Dict[str, str] = None) -> ScrapingResult:
        """
        Scrape a single URL using the appropriate strategy
        
        Args:
            url: URL to scrape
            site_config: Site-specific configuration
            custom_selectors: Custom CSS selectors for extraction
            
        Returns:
            ScrapingResult object with scraped data
        """
        result = ScrapingResult(url)
        
        try:
            # Determine site config
            if site_config is None:
                site_config = self._detect_site_config(url)
            
            # Choose scraping strategy
            strategy = site_config.scraping_strategy if site_config else ScrapingStrategy.SELENIUM_HEADLESS
            
            # Apply custom delay if specified
            if site_config and site_config.custom_delay:
                await asyncio.sleep(site_config.custom_delay)
            else:
                await asyncio.sleep(self.config.rate_limit_delay)
            
            # Execute scraping based on strategy
            if strategy == ScrapingStrategy.BASIC_HTTP:
                await self._scrape_with_http(result, site_config)
            elif strategy == ScrapingStrategy.SELENIUM_HEADLESS:
                await self._scrape_with_selenium(result, site_config, headless=True)
            elif strategy == ScrapingStrategy.SELENIUM_FULL:
                await self._scrape_with_selenium(result, site_config, headless=False)
            elif strategy == ScrapingStrategy.MOBILE_USER_AGENT:
                await self._scrape_with_mobile_agent(result, site_config)
            elif strategy == ScrapingStrategy.REQUESTS_SESSION:
                await self._scrape_with_session(result, site_config)
            
            # Extract structured data if successful
            if result.success and result.html:
                selectors = custom_selectors or (site_config.selectors if site_config else {})
                result.extracted_data = self._extract_structured_data(result.html, selectors)
            
            return result
            
        except Exception as e:
            result.error = str(e)
            logger.error(f"Error scraping {url}: {str(e)}")
            return result
    
    async def scrape_multiple_urls(self, urls: List[str], 
                                 site_config: SiteConfig = None,
                                 max_concurrent: int = None) -> List[ScrapingResult]:
        """
        Scrape multiple URLs concurrently
        
        Args:
            urls: List of URLs to scrape
            site_config: Site-specific configuration
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of ScrapingResult objects
        """
        max_concurrent = max_concurrent or self.config.concurrent_requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_url(url, site_config)
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks)
    
    def _detect_site_config(self, url: str) -> Optional[SiteConfig]:
        """Detect site configuration based on URL"""
        domain = urlparse(url).netloc.lower()
        
        for site_key, site_config in SITE_CONFIGS.items():
            for base_url in site_config.base_urls:
                if domain in base_url or base_url in domain:
                    return site_config
        
        # Return generic config for unknown sites
        return SITE_CONFIGS.get('generic_news')
    
    def _should_disable_ssl(self, url: str) -> bool:
        """Check if SSL verification should be disabled for this URL"""
        domain = urlparse(url).netloc.lower()
        
        # Check if domain is in the list of problematic SSL domains
        for ssl_domain in self.config.disable_ssl_for_domains:
            if ssl_domain.lower() in domain:
                logger.debug(f"SSL will be disabled for {url} (matches {ssl_domain})")
                return True
        
        # Also check for any facebook.com variant
        if 'facebook.com' in domain:
            logger.debug(f"SSL will be disabled for {url} (Facebook domain detected)")
            return True
        
        logger.debug(f"SSL will remain enabled for {url}")
        return False
    
    def _convert_to_facebook_mobile_url(self, url: str) -> str:
        """Convert Facebook desktop URL to proper mobile URL format"""
        try:
            # Handle different Facebook URL patterns
            if 'facebook.com' not in url:
                return url
            
            # Remove common Facebook desktop patterns that don't work on mobile
            url = url.replace('www.facebook.com', 'm.facebook.com')
            
            # Fix /pages/ URLs - mobile Facebook doesn't use /pages/ prefix
            if '/pages/' in url:
                # Extract the page name from /pages/PageName format
                if '/pages/' in url:
                    parts = url.split('/pages/')
                    if len(parts) > 1:
                        page_name = parts[1].split('/')[0]  # Get just the page name
                        # Create clean mobile URL
                        url = f"https://m.facebook.com/{page_name}"
                        logger.debug(f"Converted Facebook pages URL to mobile: {url}")
            
            # Clean any trailing slashes and parameters for mobile
            url = url.split('?')[0].rstrip('/')
            
            logger.debug(f"Facebook mobile URL: {url}")
            return url
            
        except Exception as e:
            logger.warning(f"Error converting Facebook URL to mobile: {str(e)}")
            # Fallback to simple replacement
            return url.replace('www.facebook.com', 'm.facebook.com')


    async def _scrape_with_http(self, result: ScrapingResult, site_config: SiteConfig = None):
        """Scrape using basic HTTP requests with enhanced anti-detection"""
        if not AIOHTTP_AVAILABLE or not self.session:
            raise RuntimeError("aiohttp not available or session not initialized")
        
        headers = self._get_headers(site_config)
        
        # Add random delay to appear more human-like
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        for attempt in range(self.config.max_retries):
            try:
                # For SSL problematic domains, create a new session with disabled SSL
                session_to_use = self.session
                
                logger.info(f"HTTP scraping {result.url} (attempt {attempt + 1})")
                
                # Check if we need to handle SSL differently for this URL
                if self._should_disable_ssl(result.url):
                    # Create a temporary session with SSL completely disabled
                    logger.debug(f"Disabling SSL verification for {result.url}")
                    timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                    
                    # When verify_ssl=False, don't pass ssl_context (they are mutually exclusive)
                    connector = aiohttp.TCPConnector(
                        limit=10,
                        verify_ssl=False  # This completely disables SSL verification
                    )
                    
                    async with aiohttp.ClientSession(
                        timeout=timeout,
                        connector=connector
                    ) as temp_session:
                        async with temp_session.get(result.url, headers=headers) as response:
                            await self._handle_response(response, result)
                            logger.success(f"✅ HTTP scraping successful: {result.url}")
                            return
                else:
                    async with session_to_use.get(result.url, headers=headers) as response:
                        await self._handle_response(response, result)
                        logger.success(f"✅ HTTP scraping successful: {result.url}")
                        return
                        
            except asyncio.TimeoutError:
                logger.warning(f"⏱️  Timeout scraping {result.url} (attempt {attempt + 1})")
                if attempt < self.config.max_retries - 1:
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0.5, 1.5)
                    await asyncio.sleep(delay)
            except aiohttp.ClientSSLError as e:
                logger.warning(f"🔒 SSL error scraping {result.url} (attempt {attempt + 1}): {str(e)}")
                if "certificate verify failed" in str(e).lower():
                    logger.info(f"🔄 Retrying {result.url} with SSL verification disabled")
                    # Force SSL bypass for remaining attempts
                    result.url = result.url  # Keep URL but force SSL disable logic
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(random.uniform(1, 3))
            except aiohttp.ClientError as e:
                error_str = str(e)
                logger.warning(f"⚠️  Client error scraping {result.url} (attempt {attempt + 1}): {str(e)}")
                
                # Handle specific compression errors
                if 'brotli' in error_str.lower() or 'br' in error_str.lower():
                    logger.info(f"🔧 Brotli compression error detected - installing brotli may fix this")
                    logger.info(f"   Run: pip install brotli")
                    
                    # On retry, we could fallback to no-br headers, but since we added brotli to requirements,
                    # user should install it instead
                    
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                logger.error(f"❌ Unexpected error scraping {result.url}: {str(e)}")
                result.error = str(e)
                break
        
        # If all attempts failed
        if not result.success:
            logger.error(f"❌ All HTTP scraping attempts failed for {result.url}")
            result.error = result.error or "All retry attempts failed"
    
    async def _handle_response(self, response, result: ScrapingResult):
        """Handle HTTP response and update result object"""
        result.status_code = response.status
        result.headers = dict(response.headers)
        
        if response.status == 200:
            content = await response.text()
            result.html = content
            result.content = content
            result.success = True
        elif response.status == 403:
            logger.warning(f"Access forbidden (403) for {result.url}")
        elif response.status == 404:
            logger.warning(f"Page not found (404) for {result.url}")
        elif response.status == 429:
            logger.warning(f"Rate limited (429) for {result.url}")
        else:
            logger.warning(f"HTTP {response.status} for {result.url}")
            result.error = f"HTTP {response.status}"
    
    async def _scrape_with_mobile_agent(self, result: ScrapingResult, site_config: SiteConfig = None):
        """Scrape using mobile user agent with enhanced anti-detection"""
        if not AIOHTTP_AVAILABLE or not self.session:
            raise RuntimeError("aiohttp not available or session not initialized")
        
        # Use enhanced mobile-specific headers
        mobile_headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add site-specific mobile headers 
        if 'facebook.com' in result.url:
            mobile_headers.update({
                'Referer': 'https://www.google.com/',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"'
            })
        
        # Convert to mobile URL if applicable
        mobile_url = result.url
        if 'facebook.com' in result.url:
            # Smart Facebook mobile URL conversion
            mobile_url = self._convert_to_facebook_mobile_url(result.url)
        elif 'twitter.com' in result.url:
            mobile_url = result.url.replace('twitter.com', 'mobile.twitter.com')
        
        result.url = mobile_url
        
        # Add human-like delay before mobile scraping
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        for attempt in range(self.config.max_retries):
            try:
                # Handle SSL issues for mobile URLs as well
                should_disable_ssl = self._should_disable_ssl(mobile_url)
                logger.info(f"📱 Mobile scraping {mobile_url} (attempt {attempt + 1}): SSL disable = {should_disable_ssl}")
                
                if should_disable_ssl:
                    # Create a temporary session with SSL completely disabled
                    logger.info(f"Creating SSL-disabled session for mobile URL {mobile_url}")
                    timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                    
                    # When verify_ssl=False, don't pass ssl_context (they are mutually exclusive)
                    connector = aiohttp.TCPConnector(
                        limit=10,
                        verify_ssl=False  # This completely disables SSL verification
                    )
                    
                    async with aiohttp.ClientSession(
                        timeout=timeout,
                        connector=connector
                    ) as temp_session:
                        async with temp_session.get(mobile_url, headers=mobile_headers) as response:
                            await self._handle_response(response, result)
                            logger.success(f"✅ Mobile scraping successful: {mobile_url}")
                            return
                else:
                    async with self.session.get(mobile_url, headers=mobile_headers) as response:
                        await self._handle_response(response, result)
                        logger.success(f"✅ Mobile scraping successful: {mobile_url}")
                        return
                        
            except asyncio.TimeoutError:
                logger.warning(f"⏱️  Mobile timeout for {mobile_url} (attempt {attempt + 1})")
                if attempt < self.config.max_retries - 1:
                    # Longer delays for mobile to appear more realistic
                    delay = (2 ** attempt) + random.uniform(2, 4)
                    await asyncio.sleep(delay)
            except aiohttp.ClientSSLError as e:
                logger.warning(f"🔒 Mobile SSL error for {mobile_url} (attempt {attempt + 1}): {str(e)}")
                if "certificate verify failed" in str(e).lower():
                    logger.info(f"🔄 Retrying mobile URL with SSL disabled: {mobile_url}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(random.uniform(2, 4))
            except aiohttp.ClientError as e:
                logger.warning(f"📱 Mobile client error for {mobile_url} (attempt {attempt + 1}): {str(e)}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(random.uniform(1.5, 3))
            except Exception as e:
                logger.error(f"❌ Mobile scraping error for {mobile_url}: {str(e)}")
                result.error = str(e)
                break
        
        # If all attempts failed
        if not result.success:
            logger.error(f"❌ All mobile scraping attempts failed for {mobile_url}")
            result.error = result.error or "All mobile scraping attempts failed"
    
    async def _scrape_with_selenium(self, result: ScrapingResult, site_config: SiteConfig = None, headless: bool = True):
        """Scrape using Selenium WebDriver with enhanced timeout handling"""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium not available")
        
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import TimeoutException, WebDriverException
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Configure Chrome options with enhanced stability
                chrome_options = Options()
                if headless:
                    chrome_options.add_argument("--headless")
                
                # Add default Chrome options
                for option in self.config.chrome_options:
                    chrome_options.add_argument(option)
                
                # Add enhanced stability options for heavy JavaScript sites
                stability_options = [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions-file-access-check',
                    '--disable-extensions-except',
                    '--disable-plugins-discovery',
                    '--disable-default-apps',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows',
                    '--force-device-scale-factor=1',
                    '--disable-dev-shm-usage',
                    '--disable-ipc-flooding-protection',
                    '--memory-pressure-off',
                    '--max_old_space_size=4096'
                ]
                
                for stability_option in stability_options:
                    chrome_options.add_argument(stability_option)
                
                # Add SSL-specific options for problematic domains
                if self._should_disable_ssl(result.url):
                    logger.info(f"Adding extra SSL bypass options for Selenium: {result.url}")
                    ssl_options = [
                        '--disable-web-security',
                        '--allow-running-insecure-content',
                        '--ignore-certificate-errors',
                        '--ignore-ssl-errors',
                        '--ignore-certificate-errors-spki-list',
                        '--ignore-certificate-errors-sp-list',
                        '--disable-features=VizDisplayCompositor'
                    ]
                    for ssl_option in ssl_options:
                        if ssl_option not in self.config.chrome_options:
                            chrome_options.add_argument(ssl_option)
                
                chrome_options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
                chrome_options.add_argument(f"--user-agent={random.choice(self.config.user_agents)}")
                
                # Initialize driver
                try:
                    service = webdriver.chrome.service.Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception:
                    self.driver = webdriver.Chrome(options=chrome_options)
                
                # Set enhanced timeouts - longer for Facebook and social media
                page_timeout = self.config.timeout * 3 if 'facebook.com' in result.url or 'linkedin.com' in result.url else self.config.timeout * 2
                self.driver.set_page_load_timeout(page_timeout)
                self.driver.implicitly_wait(10)
                
                logger.info(f"Loading page with Selenium (timeout: {page_timeout}s): {result.url}")
                
                # Load page with timeout handling
                try:
                    self.driver.get(result.url)
                    logger.info("✅ Page loaded successfully")
                except TimeoutException as te:
                    logger.warning(f"⚠️  Page load timeout (attempt {attempt + 1}): {str(te)}")
                    if attempt < max_retries - 1:
                        continue  # Retry
                    else:
                        # Try to get partial content if available
                        try:
                            result.html = self.driver.page_source
                            if result.html and len(result.html) > 500:
                                logger.info("📄 Got partial content despite timeout")
                                result.content = result.html
                                result.status_code = 200
                                result.success = True
                                result.partial = True
                                return
                        except:
                            pass
                        raise te
                
                # Smart waiting - wait for page to be interactive
                try:
                    wait = WebDriverWait(self.driver, 15)
                    
                    # Wait for document ready state
                    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                    logger.info("📄 Document ready state: complete")
                    
                    # For Facebook, wait for specific elements
                    if 'facebook.com' in result.url:
                        try:
                            # Wait for either main content or login redirect
                            wait.until(lambda driver: 
                                driver.find_element(By.TAG_NAME, "body") and 
                                len(driver.page_source) > 1000
                            )
                            logger.info("📱 Facebook content loaded")
                        except TimeoutException:
                            logger.info("⏱️  Facebook content timeout - proceeding with available content")
                    
                    # For LinkedIn, wait for content
                    elif 'linkedin.com' in result.url:
                        try:
                            wait.until(lambda driver: 
                                driver.find_element(By.TAG_NAME, "main") or
                                driver.find_element(By.CLASS_NAME, "org-top-card-summary") or
                                len(driver.page_source) > 1000
                            )
                            logger.info("💼 LinkedIn content loaded")
                        except TimeoutException:
                            logger.info("⏱️  LinkedIn content timeout - proceeding with available content")
                    
                    # Additional wait for JavaScript rendering
                    await asyncio.sleep(2)
                    
                except TimeoutException:
                    logger.info("⏱️  Smart wait timeout - proceeding with current page state")
                
                # Check if page loaded successfully
                current_url = self.driver.current_url
                page_title = self.driver.title or "No title"
                
                logger.info(f"Selenium loaded: {current_url} | Title: {page_title[:50]}...")
                
                # Get page source
                result.html = self.driver.page_source
                result.content = result.html
                result.status_code = 200
                result.success = True
                
                # Enhanced blocking detection
                if result.html:
                    html_lower = result.html.lower()
                    content_length = len(result.html)
                    
                    # Check for blocking patterns
                    blocking_patterns = [
                        'blocked', 'access denied', 'captcha', 'robot', 
                        'verification required', 'unusual traffic',
                        'temporarily blocked', 'rate limit'
                    ]
                    
                    if any(pattern in html_lower for pattern in blocking_patterns):
                        logger.warning(f"🚫 Selenium may have been blocked: {result.url}")
                        result.blocked = True
                    elif content_length < 500:
                        logger.warning(f"📄 Very short content ({content_length} chars) - may be blocked")
                        result.blocked = True
                    elif 'login' in html_lower and 'facebook.com' in result.url:
                        logger.info("🔐 Got Facebook login page - expected for some pages")
                        result.login_required = True
                    else:
                        logger.success(f"✅ Selenium scraping successful: {content_length} chars")
                
                # Successfully completed
                return
                
            except TimeoutException as te:
                error_msg = f"Selenium timeout (attempt {attempt + 1}): {str(te)}"
                logger.warning(error_msg)
                
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying Selenium scraping (attempt {attempt + 2}/{max_retries})")
                    # Clean up driver before retry
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
                    await asyncio.sleep(2)  # Brief pause before retry
                    continue
                else:
                    result.error = error_msg
                    logger.error(f"❌ All Selenium attempts failed due to timeout: {result.url}")
                    
            except WebDriverException as we:
                error_msg = f"WebDriver error (attempt {attempt + 1}): {str(we)}"
                logger.warning(error_msg)
                
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying after WebDriver error (attempt {attempt + 2}/{max_retries})")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
                    await asyncio.sleep(1)
                    continue
                else:
                    result.error = error_msg
                    logger.error(f"❌ All Selenium attempts failed: {result.url}")
                    
            except Exception as e:
                result.error = str(e)
                logger.error(f"❌ Selenium scraping failed for {result.url}: {str(e)}")
                break
                
        # Clean up driver after all attempts
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    async def _scrape_with_session(self, result: ScrapingResult, site_config: SiteConfig = None):
        """Scrape using persistent session (for sites requiring cookies/session state)"""
        # This would implement session-based scraping for sites that require login
        # or maintain state across requests
        await self._scrape_with_http(result, site_config)
    
    def _get_headers(self, site_config: SiteConfig = None) -> Dict[str, str]:
        """Get appropriate headers for the request with enhanced anti-detection"""
        headers = self.config.headers.copy()
        
        # Use realistic user agent
        headers['User-Agent'] = random.choice(self.config.user_agents)
        
        # Check if Brotli is available for compression
        try:
            import brotli
            accept_encoding = 'gzip, deflate, br'
            brotli_available = True
        except ImportError:
            accept_encoding = 'gzip, deflate'
            brotli_available = False
            logger.debug("Brotli not available, using gzip/deflate only")
        
        # Add more realistic browser headers to avoid detection
        headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-US,en;q=0.9,es;q=0.8',
                'en-GB,en;q=0.9,en-US;q=0.8'
            ]),
            'Accept-Encoding': accept_encoding,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
        
        # Site-specific header customization
        if site_config and 'facebook.com' in str(site_config.base_urls):
            headers.update({
                'Referer': 'https://www.google.com/',
                'Origin': 'https://www.facebook.com',
                'Sec-Fetch-Site': 'same-origin'
            })
        elif site_config and 'linkedin.com' in str(site_config.base_urls):
            headers.update({
                'Referer': 'https://www.google.com/',
                'Origin': 'https://www.linkedin.com',
                'Sec-Fetch-Site': 'same-origin'
            })
        
        if self.config.cookies:
            headers['Cookie'] = '; '.join([f'{k}={v}' for k, v in self.config.cookies.items()])
        
        return headers
    
    def _extract_structured_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract structured data from HTML using CSS selectors"""
        if not BS4_AVAILABLE:
            return {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            data = {}
            
            for key, selector in selectors.items():
                try:
                    # Handle multiple selectors separated by comma
                    selector_list = [s.strip() for s in selector.split(',')]
                    
                    for sel in selector_list:
                        elements = soup.select(sel)
                        if elements:
                            if key.endswith('_count') or 'count' in key:
                                # Extract numeric values
                                text = elements[0].get_text().strip()
                                numbers = re.findall(r'[\d,]+', text)
                                if numbers:
                                    data[key] = int(numbers[0].replace(',', ''))
                            elif key.endswith('_list') or 'list' in key:
                                # Extract list of items
                                data[key] = [elem.get_text().strip() for elem in elements[:5]]
                            else:
                                # Extract single text value
                                data[key] = elements[0].get_text().strip()
                            break
                except Exception as e:
                    logger.debug(f"Failed to extract {key} with selector {selector}: {str(e)}")
                    continue
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {str(e)}")
            return {} 
# Web Scraping Module Architecture

## Overview

The web scraping functionality has been restructured into a modular, reusable system that can be used across different collectors and data sources. This new architecture provides better maintainability, extensibility, and code reuse.

## Module Structure

```
src/scrapers/
├── __init__.py                 # Module exports
├── scraper_config.py          # Configuration classes and site configs
├── web_scraper.py             # Core web scraping engine
└── social_media_scraper.py    # Specialized social media scraper
```

## Core Components

### 1. WebScraper (Core Engine)

The main scraping engine that supports multiple strategies:

- **Basic HTTP**: Standard HTTP requests with aiohttp
- **Mobile User Agent**: Mobile-optimized scraping
- **Selenium Headless**: Browser automation for JavaScript sites
- **Selenium Full**: Full browser for complex interactions
- **Session-based**: Persistent sessions for login-required sites

#### Key Features:
- ✅ Multiple scraping strategies
- ✅ Automatic retry with backoff
- ✅ Rate limiting and concurrent request control
- ✅ Structured data extraction with CSS selectors
- ✅ Error handling and fallback mechanisms

#### Usage:
```python
from src.scrapers import WebScraper, ScraperConfig

config = ScraperConfig(max_retries=3, timeout=15)
async with WebScraper(config) as scraper:
    result = await scraper.scrape_url("https://example.com")
    if result.success:
        print(f"Content: {result.content}")
        print(f"Extracted: {result.extracted_data}")
```

### 2. SocialMediaScraper (Specialized)

Specialized scraper for social media platforms with platform-specific optimizations:

#### Supported Platforms:
- **Facebook**: Page scraping with mobile agent
- **LinkedIn**: Company page data extraction
- **Twitter/X**: Profile and post scraping
- **Generic**: Any website with custom selectors

#### Key Features:
- ✅ Platform-specific URL generation
- ✅ Anti-bot detection handling
- ✅ Data normalization across platforms
- ✅ LLM-enhanced sentiment analysis integration

#### Usage:
```python
from src.scrapers import SocialMediaScraper

async with SocialMediaScraper() as scraper:
    # Facebook
    fb_data = await scraper.scrape_facebook_page("Microsoft")
    
    # LinkedIn
    li_data = await scraper.scrape_linkedin_company("IBM")
    
    # Generic website
    custom_data = await scraper.scrape_generic_website(
        "https://example.com",
        custom_selectors={'title': 'h1', 'content': '.main'}
    )
```

### 3. ScraperConfig (Configuration)

Centralized configuration management:

```python
@dataclass
class ScraperConfig:
    max_retries: int = 3
    timeout: int = 15
    delay_between_requests: float = 1.0
    user_agents: List[str] = None
    headers: Dict[str, str] = None
    headless: bool = True
    concurrent_requests: int = 1
    # ... more options
```

### 4. SiteConfig (Site-Specific Settings)

Pre-configured settings for popular websites:

```python
SITE_CONFIGS = {
    'facebook': SiteConfig(
        name='Facebook',
        scraping_strategy=ScrapingStrategy.MOBILE_USER_AGENT,
        has_anti_bot=True,
        selectors={
            'title': 'title, h1',
            'follower_count': '[aria-label*="follower"]',
            'posts': '[data-testid="post"]'
        }
    ),
    'linkedin': SiteConfig(...),
    'twitter': SiteConfig(...),
    'generic_news': SiteConfig(...)
}
```

## Scraping Strategies

### 1. Basic HTTP (Default)
- Fast and lightweight
- Good for static content
- No JavaScript execution
- Best for: News sites, blogs, simple pages

### 2. Mobile User Agent
- Uses mobile-specific headers
- Often bypasses desktop-only blocks
- Simpler mobile HTML structure
- Best for: Facebook, mobile-optimized sites

### 3. Selenium Headless
- Full browser automation
- JavaScript execution
- Slower but more capable
- Best for: SPAs, JavaScript-heavy sites

### 4. Selenium Full Browser
- Visible browser window
- Interactive capabilities
- Debugging and development
- Best for: Testing and development

## Data Extraction

### CSS Selectors

The system uses CSS selectors for structured data extraction:

```python
selectors = {
    'title': 'title, h1, .headline',
    'author': '.author, .byline',
    'date': '.date, time[datetime]',
    'content': 'article, .content, .post',
    'follower_count': '[aria-label*="follower"]'
}
```

### Automatic Data Processing

- **Numeric extraction**: Automatically parses follower counts, likes, etc.
- **List extraction**: Extracts multiple items (posts, links, etc.)
- **Text normalization**: Cleans and normalizes extracted text
- **Handle suffixes**: Converts "1.2K" to 1200, "5M" to 5000000

## Integration with Collectors

### Before (Embedded in SocialMediaCollector):
```python
class SocialMediaCollector:
    async def _scrape_facebook_page(self, brand_name):
        # 200+ lines of scraping logic embedded here
        pass
    
    async def make_web_request(self, url):
        # HTTP request logic embedded here
        pass
```

### After (Using Common Module):
```python
class SocialMediaCollector:
    async def _scrape_facebook_data(self, brand_name):
        async with SocialMediaScraper() as scraper:
            data = await scraper.scrape_facebook_page(brand_name)
            # Enhance with LLM sentiment analysis
            enhanced_data = self._enhance_with_llm(data)
            return enhanced_data
```

## Benefits of New Architecture

### ✅ **Modularity**
- Scraping logic separated from collector logic
- Easy to maintain and update
- Single responsibility principle

### ✅ **Reusability**
- Common scraping functionality across collectors
- No code duplication
- Consistent scraping behavior

### ✅ **Extensibility**
- Easy to add new websites and platforms
- Configurable scraping strategies
- Plugin-like architecture for new scrapers

### ✅ **Testing**
- Individual components can be tested separately
- Mock different scraping scenarios
- Better test coverage

### ✅ **Configuration Management**
- Centralized scraping configurations
- Site-specific optimizations
- Easy to adjust scraping behavior

### ✅ **Error Handling**
- Consistent error handling across all scrapers
- Graceful fallbacks
- Detailed error reporting

## Advanced Features

### Concurrent Scraping
```python
urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
results = await scraper.scrape_multiple_urls(urls, max_concurrent=3)
```

### Custom Site Configurations
```python
custom_config = SiteConfig(
    name="My Custom Site",
    scraping_strategy=ScrapingStrategy.SELENIUM_HEADLESS,
    selectors={'title': '.custom-title', 'content': '.custom-content'}
)
result = await scraper.scrape_url(url, site_config=custom_config)
```

### Dynamic Strategy Selection
The scraper automatically chooses the best strategy based on:
- Website detection (Facebook → Mobile UA)
- Content requirements (JavaScript → Selenium)
- Performance needs (Static → Basic HTTP)

## Migration Guide

### For Existing Collectors:

1. **Replace direct scraping methods**:
   ```python
   # Old
   html = await self.make_web_request(url)
   
   # New
   async with WebScraper() as scraper:
       result = await scraper.scrape_url(url)
       html = result.html
   ```

2. **Use specialized scrapers**:
   ```python
   # Old
   data = await self._scrape_facebook_page(brand)
   
   # New
   async with SocialMediaScraper() as scraper:
       data = await scraper.scrape_facebook_page(brand)
   ```

3. **Configure scraping behavior**:
   ```python
   config = ScraperConfig(
       max_retries=5,
       timeout=20,
       delay_between_requests=2.0
   )
   scraper = WebScraper(config)
   ```

## Future Enhancements

### Planned Features:
- [ ] **Proxy support** for IP rotation
- [ ] **CAPTCHA solving** integration
- [ ] **Machine learning** for anti-bot detection
- [ ] **Caching layer** for scraped content
- [ ] **Database integration** for scraped data storage
- [ ] **Monitoring and alerting** for scraping failures
- [ ] **A/B testing** for different scraping strategies

### Extensibility Points:
- Custom scraping strategies
- New social media platforms
- Industry-specific scrapers (e-commerce, news, etc.)
- Advanced data extraction (computer vision, NLP)

## Performance Considerations

### Optimization Strategies:
- **Connection pooling** for HTTP requests
- **Concurrent scraping** with semaphores
- **Smart retry** with exponential backoff
- **Resource management** (memory, file handles)
- **Rate limiting** to avoid IP blocks

### Monitoring:
- Success/failure rates per site
- Average response times
- Resource usage tracking
- Error pattern analysis

This new architecture provides a solid foundation for scalable, maintainable web scraping that can grow with your needs while maintaining high performance and reliability. 
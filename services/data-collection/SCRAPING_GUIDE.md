# Web Scraping Guide for Social Media Data Collection

## 🕷️ Overview

The data collection service now includes web scraping capabilities for Facebook and LinkedIn to gather brand sentiment and engagement data when APIs are not available or have limitations.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Basic scraping (recommended)
pip install beautifulsoup4 lxml

# Advanced scraping with Selenium (optional)
pip install selenium webdriver-manager

# Install Chrome browser (for Selenium)
# Windows/Mac: Download from https://www.google.com/chrome/
# Ubuntu: sudo apt-get install google-chrome-stable
```

### 2. Test Installation
```bash
python test_scraping.py
```

### 3. Configure Scraping (Optional)
Add to your `.env` file:
```bash
SCRAPING_ENABLE_FACEBOOK_SCRAPING=true
SCRAPING_ENABLE_LINKEDIN_SCRAPING=true
SCRAPING_FACEBOOK_SCRAPING_METHOD=basic
SCRAPING_LINKEDIN_SCRAPING_METHOD=basic
SCRAPING_DELAY_SECONDS=1.0
```

## 📊 What Data is Collected

### Facebook Pages
- **Basic Method**:
  - ✅ Page existence verification
  - ✅ Basic sentiment analysis
  - ❌ Follower count (requires JavaScript)
  - ❌ Recent posts (requires JavaScript/login)

- **Selenium Method**:
  - ✅ Page information
  - ✅ Follower/like counts
  - ✅ Recent posts content
  - ✅ Advanced sentiment analysis

### LinkedIn Company Pages
- **Basic Method**:
  - ✅ Company information
  - ✅ Follower counts
  - ✅ Basic sentiment analysis
  - ❌ Recent posts (limited)

- **Selenium Method**:
  - ✅ Complete company data
  - ✅ Follower counts
  - ✅ Recent company updates
  - ✅ Advanced sentiment analysis

## 🛠️ Scraping Methods

### 1. Basic Scraping (BeautifulSoup)
- **Pros**: Fast, lightweight, no browser required
- **Cons**: Limited by JavaScript-heavy content
- **Best for**: Basic company information, follower counts

### 2. Selenium Scraping
- **Pros**: Full JavaScript support, complete data access
- **Cons**: Slower, requires Chrome browser, more resources
- **Best for**: Detailed post content, complex interactions

## ⚙️ Configuration Options

```python
# In your .env file:

# Enable/disable platforms
SCRAPING_ENABLE_FACEBOOK_SCRAPING=true
SCRAPING_ENABLE_LINKEDIN_SCRAPING=true

# Scraping methods: "basic", "selenium", "both"
SCRAPING_FACEBOOK_SCRAPING_METHOD=basic
SCRAPING_LINKEDIN_SCRAPING_METHOD=basic

# Rate limiting
SCRAPING_DELAY_SECONDS=1.0
SCRAPING_MAX_SCRAPING_RETRIES=3

# Selenium options
SCRAPING_SELENIUM_HEADLESS=true
SCRAPING_SELENIUM_TIMEOUT=10
```

## 🔒 Important Considerations

### Legal and Ethical
- ⚠️ **Terms of Service**: Web scraping may violate platform ToS
- ⚠️ **Rate Limiting**: Always respect platform rate limits
- ⚠️ **robots.txt**: Check and respect robots.txt files
- ✅ **Fallback Strategy**: Service uses mock data when scraping fails

### Technical Limitations
- **Facebook**: Heavy anti-bot measures, requires JavaScript for most data
- **LinkedIn**: Rate limiting, may require login for full access
- **Network Issues**: SSL certificates, proxy settings, firewalls
- **Data Freshness**: Scraped data may be less current than API data

### Best Practices
1. **Start with Basic Scraping**: Less likely to be blocked
2. **Use Realistic Delays**: Don't overwhelm servers
3. **Handle Failures Gracefully**: Always have fallback data
4. **Monitor for Changes**: Platform layouts change frequently
5. **Prefer Official APIs**: When available and practical

## 🧪 Testing Your Setup

### Quick Test
```bash
python test_scraping.py
```

### Manual Testing
```python
import asyncio
from src.collectors.social_media_collector import SocialMediaCollector

async def test_brand():
    collector = SocialMediaCollector()
    async with collector:
        data = await collector.collect_brand_data("Microsoft", "technology")
        print(f"Sentiment: {data['overall_sentiment']}")
        print(f"Mentions: {data['mentions_count']}")

asyncio.run(test_brand())
```

## 🛠️ Troubleshooting

### Common Issues

**1. "ChromeDriver not found"**
```bash
# Install Chrome browser first, then:
pip install webdriver-manager
```

**2. "SSL Certificate errors"**
```bash
# Set in .env file:
VERIFY_SSL=false
```

**3. "BeautifulSoup not found"**
```bash
pip install beautifulsoup4 lxml
```

**4. "Scraping blocked/empty results"**
- This is normal - platforms actively block scrapers
- Service will automatically use mock data as fallback
- Try different user agents or methods

### Debug Mode
```python
# Enable debug logging in your collector
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Tips

1. **Use Basic Method First**: Faster and less detectable
2. **Implement Caching**: Cache results to reduce requests
3. **Batch Requests**: Collect multiple brands in one session
4. **Monitor Success Rates**: Track which methods work best
5. **Rotate User Agents**: Use different browser signatures

## 🔄 Fallback Strategy

The service implements a robust fallback strategy:

1. **Try Web Scraping**: Attempt to collect real data
2. **Handle Errors Gracefully**: Log warnings, not errors
3. **Use Mock Data**: Provide realistic mock data when scraping fails
4. **Continue Processing**: Never fail the entire job due to scraping issues

## 📝 Example Output

```json
{
  "overall_sentiment": 0.72,
  "mentions_count": 1250,
  "engagement_rate": 0.048,
  "platforms": {
    "facebook": {"sentiment": 0.68, "mentions": 800},
    "linkedin": {"sentiment": 0.75, "mentions": 450}
  },
  "trending_topics": ["innovation", "technology", "leadership"]
}
```

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: Look in `logs/app.log` for detailed error messages
2. **Test dependencies**: Run `python test_scraping.py`
3. **Verify configuration**: Check your `.env` file settings
4. **Check network**: Ensure internet connectivity and proxy settings
5. **Update dependencies**: Keep scraping libraries up to date

---

**Remember**: Web scraping is a best-effort approach. The service is designed to work gracefully even when scraping fails, using mock data to ensure consistent operation. 
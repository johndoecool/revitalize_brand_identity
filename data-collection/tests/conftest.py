"""
pytest configuration and common fixtures

This file contains pytest configuration and fixtures that are shared
across all test modules.
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, Optional

# Test configuration
pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for HTTP request testing"""
    session = AsyncMock()
    
    # Mock successful response
    response = AsyncMock()
    response.status = 200
    response.text = AsyncMock(return_value="<html><title>Test</title><body>Test content</body></html>")
    response.json = AsyncMock(return_value={"test": "data"})
    response.headers = {"content-type": "text/html"}
    
    session.get.return_value.__aenter__.return_value = response
    session.post.return_value.__aenter__.return_value = response
    
    return session

@pytest.fixture
def mock_selenium_driver():
    """Mock Selenium WebDriver for browser automation testing"""
    driver = Mock()
    driver.page_source = "<html><title>Selenium Test</title><body>Selenium content</body></html>"
    driver.find_elements.return_value = []
    driver.find_element.return_value = Mock(text="Mock element text")
    driver.quit = Mock()
    driver.get = Mock()
    driver.set_page_load_timeout = Mock()
    driver.implicitly_wait = Mock()
    
    return driver

@pytest.fixture
def sample_facebook_html():
    """Sample Facebook page HTML for testing"""
    return """
    <html>
        <head><title>Microsoft - Home | Facebook</title></head>
        <body>
            <h1>Microsoft</h1>
            <div aria-label="5,234,567 people like this">5,234,567 people like this</div>
            <div data-testid="post_message">Great new product launch!</div>
            <div data-testid="post_message">Excited about our latest innovation</div>
        </body>
    </html>
    """

@pytest.fixture
def sample_linkedin_html():
    """Sample LinkedIn company page HTML for testing"""
    return """
    <html>
        <head><title>Microsoft | LinkedIn</title></head>
        <body>
            <h1 class="org-top-card-summary__title">Microsoft</h1>
            <div class="org-top-card-summary__follower-count">18,509,628 followers</div>
            <div class="feed-shared-update-v2">
                <div class="feed-shared-text">LinkedIn post about innovation</div>
            </div>
            <div class="org-top-card-summary-info-list">
                <div>Technology company</div>
            </div>
        </body>
    </html>
    """

@pytest.fixture
def sample_twitter_html():
    """Sample Twitter profile HTML for testing"""
    return """
    <html>
        <head><title>Microsoft (@microsoft) / Twitter</title></head>
        <body>
            <div data-testid="UserName">Microsoft</div>
            <div data-testid="UserFollowers"><span>4.2M</span> Followers</div>
            <div data-testid="tweet">
                <div data-testid="tweetText">Excited to announce our new AI features!</div>
            </div>
            <div data-testid="tweet">
                <div data-testid="tweetText">Join us at the tech conference next week</div>
            </div>
        </body>
    </html>
    """

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response for sentiment analysis"""
    def _mock_response(sentiment_score: float = 0.7):
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = str(sentiment_score)
        return response
    return _mock_response

@pytest.fixture
def sample_scraper_config():
    """Sample scraper configuration for testing"""
    from scrapers.scraper_config import ScraperConfig
    return ScraperConfig(
        max_retries=2,
        timeout=10,
        delay_between_requests=0.1,  # Faster for tests
        concurrent_requests=2
    )

@pytest.fixture
def sample_brand_data():
    """Sample brand data for testing"""
    return {
        "sentiment": 0.75,
        "mentions": 12500,
        "posts": [
            {
                "text": "Great product launch!",
                "sentiment": 0.8,
                "source": "facebook"
            },
            {
                "text": "Looking forward to new features",
                "sentiment": 0.7,
                "source": "linkedin"
            }
        ]
    }

@pytest.fixture(autouse=True)
def mock_external_dependencies(monkeypatch):
    """Automatically mock external dependencies for all tests"""
    # Mock OpenAI
    mock_openai = Mock()
    mock_openai.ChatCompletion = Mock()
    mock_openai.ChatCompletion.create = Mock(return_value=Mock(
        choices=[Mock(message=Mock(content="0.7"))]
    ))
    monkeypatch.setattr("openai.ChatCompletion", mock_openai.ChatCompletion)
    
    # Mock Selenium imports
    mock_webdriver = Mock()
    mock_options = Mock()
    monkeypatch.setattr("selenium.webdriver.Chrome", mock_webdriver)
    monkeypatch.setattr("selenium.webdriver.chrome.options.Options", mock_options)
    
    # Mock webdriver manager
    mock_chrome_manager = Mock()
    mock_chrome_manager.install = Mock(return_value="/path/to/chromedriver")
    monkeypatch.setattr("webdriver_manager.chrome.ChromeDriverManager", lambda: mock_chrome_manager)

@pytest.fixture
def test_urls():
    """Common test URLs"""
    return {
        'facebook': 'https://www.facebook.com/microsoft',
        'linkedin': 'https://www.linkedin.com/company/microsoft',
        'twitter': 'https://twitter.com/microsoft',
        'generic': 'https://example.com'
    } 
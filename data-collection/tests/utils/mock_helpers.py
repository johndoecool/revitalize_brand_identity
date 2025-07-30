"""
Mock helper utilities for testing

Contains utility functions for creating mock objects and responses.
"""

from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, Optional, List
from tests.fixtures.mock_html_responses import MOCK_RESPONSES

class MockAiohttpResponse:
    """Mock aiohttp response object"""
    
    def __init__(self, status: int = 200, content: str = None, json_data: Dict = None, headers: Dict = None):
        self.status = status
        self.headers = headers or {'content-type': 'text/html; charset=utf-8'}
        self._content = content or MOCK_RESPONSES.get('generic_success', '<html><body>Test</body></html>')
        self._json_data = json_data or {}
    
    async def text(self) -> str:
        """Return text content"""
        return self._content
    
    async def json(self) -> Dict:
        """Return JSON content"""
        if self.status != 200 or 'application/json' not in self.headers.get('content-type', ''):
            raise Exception("Cannot parse JSON")
        return self._json_data

class MockAiohttpSession:
    """Mock aiohttp session for HTTP request testing"""
    
    def __init__(self):
        self.responses = {}
        self.request_history = []
    
    def set_response(self, url: str, status: int = 200, content: str = None, json_data: Dict = None, headers: Dict = None):
        """Set mock response for a specific URL"""
        self.responses[url] = MockAiohttpResponse(status, content, json_data, headers)
    
    def get(self, url: str, **kwargs):
        """Mock GET request"""
        self.request_history.append(('GET', url, kwargs))
        response = self.responses.get(url, MockAiohttpResponse())
        
        # Create async context manager
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        return context_manager
    
    def post(self, url: str, **kwargs):
        """Mock POST request"""
        self.request_history.append(('POST', url, kwargs))
        response = self.responses.get(url, MockAiohttpResponse())
        
        # Create async context manager
        context_manager = AsyncMock()
        context_manager.__aenter__ = AsyncMock(return_value=response)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        return context_manager
    
    async def close(self):
        """Mock session close"""
        pass

class MockSeleniumDriver:
    """Mock Selenium WebDriver for browser automation testing"""
    
    def __init__(self, page_source: str = None):
        self.page_source = page_source or MOCK_RESPONSES.get('generic_success', '<html><body>Test</body></html>')
        self.current_url = "https://example.com"
        self.title = "Test Page"
        self._elements = {}
        self.request_history = []
    
    def get(self, url: str):
        """Mock navigate to URL"""
        self.current_url = url
        self.request_history.append(('GET', url))
    
    def find_element(self, by, value):
        """Mock find single element"""
        element = Mock()
        element.text = f"Mock text for {value}"
        element.get_attribute = Mock(return_value="mock-attribute")
        return element
    
    def find_elements(self, by, value):
        """Mock find multiple elements"""
        elements = []
        # Return mock elements based on selector
        if 'post' in value.lower():
            for i in range(3):
                element = Mock()
                element.text = f"Mock post {i+1} content"
                elements.append(element)
        elif 'follower' in value.lower():
            element = Mock()
            element.text = "1.2M followers"
            elements.append(element)
        return elements
    
    def set_page_load_timeout(self, timeout: int):
        """Mock set page load timeout"""
        pass
    
    def implicitly_wait(self, timeout: int):
        """Mock implicit wait"""
        pass
    
    def quit(self):
        """Mock driver quit"""
        pass

class MockLLMResponse:
    """Mock LLM API response for sentiment analysis"""
    
    def __init__(self, sentiment_score: float = 0.7):
        self.sentiment_score = sentiment_score
    
    def openai_response(self):
        """Mock OpenAI response format"""
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = str(self.sentiment_score)
        return response
    
    def anthropic_response(self):
        """Mock Anthropic response format"""
        response = Mock()
        response.content = [Mock()]
        response.content[0].text = str(self.sentiment_score)
        return response
    
    def huggingface_response(self):
        """Mock Hugging Face response format"""
        # Convert sentiment score to HF format
        if self.sentiment_score > 0.3:
            # Positive
            return [[
                {'label': 'LABEL_0', 'score': 0.1},  # Negative
                {'label': 'LABEL_1', 'score': 0.2},  # Neutral
                {'label': 'LABEL_2', 'score': 0.7}   # Positive
            ]]
        elif self.sentiment_score < -0.3:
            # Negative
            return [[
                {'label': 'LABEL_0', 'score': 0.7},  # Negative
                {'label': 'LABEL_1', 'score': 0.2},  # Neutral
                {'label': 'LABEL_2', 'score': 0.1}   # Positive
            ]]
        else:
            # Neutral
            return [[
                {'label': 'LABEL_0', 'score': 0.2},  # Negative
                {'label': 'LABEL_1', 'score': 0.6},  # Neutral
                {'label': 'LABEL_2', 'score': 0.2}   # Positive
            ]]
    
    def cohere_response(self):
        """Mock Cohere response format"""
        response = Mock()
        response.generations = [Mock()]
        response.generations[0].text = str(self.sentiment_score)
        return response

def create_mock_scraping_result(url: str, success: bool = True, content: str = None) -> Mock:
    """Create a mock ScrapingResult object"""
    from scrapers.web_scraper import ScrapingResult
    
    result = Mock(spec=ScrapingResult)
    result.url = url
    result.success = success
    result.content = content or MOCK_RESPONSES.get('generic_success', '<html><body>Test</body></html>')
    result.html = result.content
    result.status_code = 200 if success else 404
    result.headers = {'content-type': 'text/html'}
    result.error = None if success else "Mock error"
    result.extracted_data = {
        'title': 'Mock Title',
        'content': 'Mock content',
        'author': 'Mock Author'
    } if success else {}
    result.metadata = {}
    
    return result

def create_mock_social_media_data(platform: str, brand_name: str, sentiment: float = 0.7, mentions: int = 1000) -> Dict[str, Any]:
    """Create mock social media data"""
    return {
        "sentiment": sentiment,
        "mentions": mentions,
        "posts": [
            {
                "text": f"Mock {platform} post about {brand_name}",
                "sentiment": sentiment,
                "source": platform.lower()
            },
            {
                "text": f"Another {platform} post mentioning {brand_name}",
                "sentiment": sentiment + 0.1,
                "source": platform.lower()
            }
        ],
        "raw_data": {
            "title": f"{brand_name} - {platform}",
            "extracted_fields": {
                "follower_count": mentions,
                "title": f"{brand_name} Official Page"
            }
        }
    }

def setup_mock_http_responses(mock_session: MockAiohttpSession, scenarios: Dict[str, str]):
    """Setup multiple HTTP response scenarios"""
    for url, scenario in scenarios.items():
        if scenario in MOCK_RESPONSES:
            mock_session.set_response(url, content=MOCK_RESPONSES[scenario])
        elif scenario == 'error_404':
            mock_session.set_response(url, status=404, content=MOCK_RESPONSES['generic_404'])
        elif scenario == 'error_403':
            mock_session.set_response(url, status=403, content=MOCK_RESPONSES['forbidden_403'])
        elif scenario == 'error_429':
            mock_session.set_response(url, status=429, content=MOCK_RESPONSES['rate_limited_429'])

def create_mock_brand_analysis_data(brand_name: str) -> Dict[str, Any]:
    """Create comprehensive mock brand analysis data"""
    return {
        "overall_sentiment": 0.75,
        "mentions_count": 15750,
        "engagement_rate": 0.045,
        "platforms": {
            "facebook": {
                "sentiment": 0.7,
                "mentions": 5000
            },
            "linkedin": {
                "sentiment": 0.8,
                "mentions": 7500
            },
            "twitter": {
                "sentiment": 0.75,
                "mentions": 3250
            }
        },
        "trending_topics": [
            "innovation",
            "technology",
            "customer service"
        ]
    } 
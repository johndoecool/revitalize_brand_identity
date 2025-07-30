# Testing Guide

## Overview

The Data Collection Service now uses a comprehensive testing framework with proper separation between unit tests, integration tests, and test utilities. This guide explains how to run tests, write new tests, and understand the testing architecture.

## 🏗️ Test Architecture

### Directory Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py             # Pytest configuration and common fixtures
├── unit/                   # Unit tests for individual components
│   ├── __init__.py
│   ├── test_web_scraper.py          # WebScraper class tests
│   ├── test_social_media_scraper.py # SocialMediaScraper class tests
│   ├── test_scraper_config.py       # Configuration classes tests
│   └── test_social_media_collector.py # Collector integration tests
├── integration/            # Integration tests
│   ├── __init__.py
│   └── test_scraping_pipeline.py    # End-to-end pipeline tests
├── fixtures/               # Test data and mock responses
│   ├── __init__.py
│   └── mock_html_responses.py       # Mock HTML for different websites
└── utils/                  # Test utilities and helpers
    ├── __init__.py
    └── mock_helpers.py              # Mock creation utilities
```

### Test Categories

- **Unit Tests**: Test individual components in isolation with mocked dependencies
- **Integration Tests**: Test component interactions and data flow
- **Fixtures**: Reusable test data and mock responses
- **Utilities**: Helper functions for creating mocks and test scenarios

## 🚀 Running Tests

### Quick Start

```bash
# Install testing dependencies
pip install -r requirements.txt

# Check test environment
python run_tests.py check

# Run all tests
python run_tests.py all
```

### Test Runner Commands

The `run_tests.py` script provides easy access to different test suites:

```bash
# Run specific test types
python run_tests.py unit           # Unit tests only
python run_tests.py integration    # Integration tests only
python run_tests.py fast           # Fast tests (excludes slow markers)

# Run tests by category
python run_tests.py scraping       # Scraping-related tests
python run_tests.py llm            # LLM/sentiment analysis tests

# Run with coverage
python run_tests.py coverage       # Generate coverage report

# Run specific test
python run_tests.py specific --test tests/unit/test_web_scraper.py
python run_tests.py specific --test tests/unit/test_web_scraper.py::TestWebScraper::test_scrape_url_success
```

### Direct Pytest Usage

You can also run pytest directly:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_web_scraper.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests matching a pattern
pytest -k "scraper"

# Run tests with specific markers
pytest -m "unit"
```

## 📋 Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*  
python_functions = test_*
markers =
    unit: Unit tests for individual components
    integration: Integration tests for component interactions
    slow: Tests that take a long time to run
    external: Tests that require external services
    llm: Tests that involve LLM APIs
    scraping: Tests that involve web scraping
asyncio_mode = auto
```

### Common Fixtures (`tests/conftest.py`)

- `mock_aiohttp_session`: Mock HTTP session for web requests
- `mock_selenium_driver`: Mock Selenium WebDriver
- `sample_facebook_html`: Sample Facebook page HTML
- `sample_linkedin_html`: Sample LinkedIn page HTML
- `sample_twitter_html`: Sample Twitter page HTML
- `mock_llm_response`: Mock LLM API responses
- `sample_scraper_config`: Test scraper configuration

## ✏️ Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from scrapers.web_scraper import WebScraper

class TestWebScraper:
    @pytest.fixture
    def scraper_config(self):
        from scrapers.scraper_config import ScraperConfig
        return ScraperConfig(max_retries=2, timeout=5)
    
    @pytest.mark.asyncio
    async def test_scrape_url_success(self, scraper_config):
        """Test successful URL scraping"""
        test_url = "https://example.com"
        
        with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session_class:
            # Setup mock response
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
            
            mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session_class.return_value = mock_session
            
            # Test the scraper
            async with WebScraper(scraper_config) as scraper:
                result = await scraper.scrape_url(test_url)
                
                assert result.success is True
                assert result.url == test_url
                assert result.content is not None
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_complete_brand_analysis_pipeline():
    """Test end-to-end brand analysis"""
    brand_id = "Microsoft"
    
    # Mock external dependencies
    with patch('collectors.social_media_collector.SocialMediaScraper') as mock_scraper:
        # Setup comprehensive mocks
        mock_instance = AsyncMock()
        mock_instance.scrape_facebook_page = AsyncMock(return_value={
            "sentiment": 0.75,
            "mentions": 1000,
            "posts": [{"text": "Great product!", "sentiment": 0.8}]
        })
        mock_scraper.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
        
        # Test complete pipeline
        collector = SocialMediaCollector()
        async with collector:
            result = await collector.collect_brand_data(brand_id, "innovation")
            
            assert result is not None
            assert 'overall_sentiment' in result
            assert 'platforms' in result
```

### Using Fixtures

```python
def test_facebook_data_extraction(sample_facebook_html):
    """Test using predefined fixtures"""
    # sample_facebook_html is automatically provided by conftest.py
    assert "Microsoft" in sample_facebook_html
    assert "people like this" in sample_facebook_html

@pytest.mark.asyncio
async def test_with_mock_session(mock_aiohttp_session):
    """Test using mock HTTP session"""
    mock_aiohttp_session.set_response(
        "https://example.com", 
        content="<html>Test</html>"
    )
    # Use the mock session in your test
```

## 🎯 Test Patterns

### Mocking External Dependencies

```python
# Mock HTTP requests
with patch('scrapers.web_scraper.aiohttp.ClientSession') as mock_session:
    # Setup mock behavior
    pass

# Mock Selenium
with patch('scrapers.web_scraper.webdriver.Chrome') as mock_driver:
    # Setup mock driver
    pass

# Mock LLM APIs
with patch.object(collector, '_get_openai_sentiment', return_value=0.85):
    # Test with mocked LLM response
    pass
```

### Async Test Patterns

```python
@pytest.mark.asyncio
async def test_async_function():
    """Always use @pytest.mark.asyncio for async tests"""
    result = await some_async_function()
    assert result is not None

# Test async context managers
async with SomeContextManager() as manager:
    result = await manager.do_something()
    assert result.success
```

### Parameterized Tests

```python
@pytest.mark.parametrize("brand_name,expected_mentions", [
    ("Microsoft", 1000000),
    ("Apple", 2000000),
    ("Google", 1500000)
])
def test_brand_mentions(brand_name, expected_mentions):
    # Test runs once for each parameter set
    pass
```

## 📊 Coverage and Reporting

### Coverage Reports

```bash
# Generate HTML coverage report
python run_tests.py coverage

# View coverage report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

### Coverage Configuration

Coverage tracks:
- Line coverage: Which lines were executed
- Branch coverage: Which code paths were taken
- Function coverage: Which functions were called

Target coverage: **≥ 80%** for production code

## 🐛 Debugging Tests

### Running Single Tests

```bash
# Run specific test with verbose output
pytest tests/unit/test_web_scraper.py::TestWebScraper::test_scrape_url_success -v -s

# Run with debugger
pytest --pdb tests/unit/test_web_scraper.py

# Run with print statements (disable capture)
pytest -s tests/unit/test_web_scraper.py
```

### Common Debugging Techniques

```python
# Add debugging prints
def test_something():
    result = function_under_test()
    print(f"DEBUG: result = {result}")  # Use -s flag to see output
    assert result is not None

# Use pytest fixtures for debugging
@pytest.fixture
def debug_config():
    return ScraperConfig(max_retries=1, timeout=1)  # Faster failures

# Use pytest.fail for custom failure messages
def test_complex_logic():
    if complex_condition:
        pytest.fail("Complex condition failed with specific context")
```

## 🏷️ Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration  
def test_integration_functionality():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.llm
def test_llm_integration():
    pass

@pytest.mark.external
def test_with_real_api():  # Requires real API key
    pass
```

Run specific markers:
```bash
pytest -m unit      # Run only unit tests
pytest -m "not slow" # Skip slow tests
pytest -m "llm or scraping" # Run LLM or scraping tests
```

## 🔧 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python run_tests.py check
      - run: python run_tests.py coverage
```

## 📚 Best Practices

### Test Organization

- ✅ **One test class per source class**
- ✅ **Descriptive test names** (`test_scrape_url_with_404_error`)
- ✅ **Arrange-Act-Assert pattern**
- ✅ **Mock external dependencies**
- ✅ **Test edge cases and error conditions**

### Test Quality

- ✅ **Fast execution** (unit tests < 1s each)
- ✅ **Independent tests** (no test depends on another)
- ✅ **Reliable** (no flaky tests)
- ✅ **Readable** (clear setup and assertions)
- ✅ **Maintainable** (easy to update when code changes)

### What to Test

**DO Test:**
- ✅ Public method behavior
- ✅ Error handling and edge cases  
- ✅ Integration between components
- ✅ Configuration handling
- ✅ Data transformation logic

**DON'T Test:**
- ❌ Private methods directly
- ❌ Third-party library internals
- ❌ Simple getters/setters
- ❌ Configuration constants

## 🆘 Troubleshooting

### Common Issues

**ImportError: No module named 'src'**
```bash
# Solution: Run tests from project root
cd revitalize_brand_identity/services/data-collection
python run_tests.py all
```

**pytest-asyncio warnings**
```bash
# Solution: Already configured in pytest.ini
asyncio_mode = auto
```

**Tests failing with "Session not initialized"**
```python
# Solution: Use async context manager in tests
async with SomeClass() as instance:
    result = await instance.method()
```

**Mock not working as expected**
```python
# Solution: Check patch target is correct
# Patch where it's imported, not where it's defined
with patch('module_using_it.ClassName') as mock:
    pass
```

### Getting Help

1. **Check test environment**: `python run_tests.py check`
2. **Run specific test**: `python run_tests.py specific --test <test_file>`
3. **Enable verbose output**: Add `-v` flag
4. **Check fixtures**: Look in `tests/conftest.py` and `tests/fixtures/`
5. **Review examples**: See existing tests in `tests/unit/`

## 📈 Performance

### Test Performance Tips

- **Use fixtures** for expensive setup
- **Mock external calls** (HTTP, database, LLM APIs)
- **Parallel execution**: `pytest -n auto` (requires pytest-xdist)
- **Skip slow tests**: `pytest -m "not slow"`
- **Profile tests**: `pytest --durations=10`

### Expected Performance

- **Unit tests**: < 1 second each
- **Integration tests**: < 5 seconds each
- **Full test suite**: < 30 seconds
- **Coverage generation**: < 60 seconds

This comprehensive testing framework ensures reliable, maintainable code with high confidence in functionality and regressions detection. 
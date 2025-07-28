# Brand Service FastAPI Project - Context for GitHub Copilot

## Project Overview
This is a FastAPI-based microservice for brand management that provides APIs for brand search, area suggestions, and competitor discovery. The service implements cache-first architecture with AI-powered fallbacks using Together.ai.

## 🎯 Project Status & Achievements
- ✅ **82% Unit Test Coverage** achieved (excluding utility modules)
- ✅ **FastAPI endpoint `/api/v1/brands/{brand_id}/competitors?area={area_id}`** implemented
- ✅ **Cache-first logic** with JSON file persistence
- ✅ **Together.ai integration** for AI-powered competitor discovery
- ✅ **Robust error handling** and structured logging
- ✅ **Configurable API keys** and model parameters
- ✅ **Comprehensive test suite** (199 test cases across 16 modules)

## 🏗️ Architecture & Key Components

### Core Application Structure
```
brand-service/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration management (100% coverage)
│   ├── models.py                  # Pydantic data models (100% coverage)
│   ├── services.py                # Business logic (95% coverage)
│   ├── logging_config.py          # Logging setup (EXCLUDED from coverage)
│   ├── alphavantage_service.py    # Alpha Vantage API client (87% coverage)
│   ├── cache_service.py           # Brand search cache (86% coverage)
│   ├── areas_cache_service.py     # Areas cache service (69% coverage)
│   ├── competitors_cache_service.py # Competitors cache (68% coverage)
│   └── api/
│       ├── brands.py              # Main API endpoints (77% coverage)
│       └── cache.py               # Cache management APIs (EXCLUDED)
├── tests/                         # Comprehensive test suite
├── brand-cache.json               # Brand search cache
├── brand-areas.json               # Areas suggestions cache
├── brand-competitors.json         # Competitors cache
├── .coveragerc                    # Coverage configuration
├── requirements.txt               # Dependencies
└── logs/                          # Application logs
```

### Key Design Patterns
1. **Cache-First Architecture**: All endpoints check cache before external APIs
2. **Fallback Strategy**: Financial Modeling Prep → Alpha Vantage → Together.ai
3. **Dependency Injection**: Configurable services via app/config.py
4. **Error Resilience**: Comprehensive exception handling with structured logging
5. **Test-Driven Development**: High coverage with mocked external dependencies

## 🚀 Main API Endpoints

### Primary Endpoint (Main Feature)
```python
GET /api/v1/brands/{brand_id}/competitors?area={area_id}
```
**Implementation Details:**
- Cache-first logic checking `brand-competitors.json`
- Together.ai fallback with configurable model (`TOGETHER_AI_MODEL`)
- Returns competitors with relevance scores and reasoning
- Comprehensive error handling and logging
- Response caching with brand_id + area as cache key

### Supporting Endpoints
```python
POST /api/v1/brands/search          # Brand search with FMP/AV fallback
GET /api/v1/brands/{brand_id}/areas # Area suggestions via Together.ai
GET /api/v1/cache/*                 # Cache management utilities
GET /health                         # Health check
```

## 📋 Configuration Management

### Environment Variables (app/config.py)
```python
# API Keys
FMP_API_KEY                 # Financial Modeling Prep API key
ALPHA_VANTAGE_API_KEY      # Alpha Vantage API key  
TOGETHER_AI_API_KEY        # Together.ai API key

# Model Configuration
TOGETHER_AI_MODEL          # AI model name (default: "meta-llama/Llama-2-7b-chat-hf")
LOGO_SEARCH_TOKENS         # Logo search API tokens

# Cache Configuration  
BRAND_CACHE_FILE           # Brand search cache file path
BRAND_AREAS_CACHE_FILE     # Areas cache file path
BRAND_COMPETITORS_CACHE_FILE # Competitors cache file path
```

### Key Configuration Features
- All external API endpoints configurable via URL builders
- Environment-based configuration with sensible defaults
- Separate cache files for different data types
- Logging configuration with file rotation

## 🧪 Testing Strategy & Coverage

### Test Structure (199 tests total)
```
tests/
├── test_api.py                    # Core API endpoint tests
├── test_api_enhanced.py           # Enhanced API scenarios
├── test_api_integration.py        # Integration tests
├── test_cache*.py                 # Cache system tests (multiple files)
├── test_areas_cache.py            # Areas cache specific tests
├── test_competitors_cache.py      # Competitors cache tests
├── test_config.py                 # Configuration tests
├── test_models.py                 # Pydantic model validation
├── test_services.py               # Business logic tests
├── test_alphavantage.py           # Alpha Vantage service tests
├── test_logging.py                # Logging functionality
└── test_*coverage*.py             # Various coverage enhancement tests
```

### Coverage Exclusions (.coveragerc)
```ini
[run]
omit = 
    */logging_config.py    # Utility logging configuration
    */cache.py            # Utility cache management endpoints
    app/logging_config.py
    app/api/cache.py
```

### Test Categories
1. **Unit Tests**: Individual component testing with mocks
2. **Integration Tests**: End-to-end API flows
3. **Cache Tests**: Cache hit/miss scenarios and file operations  
4. **Error Handling**: Exception scenarios and resilience
5. **Configuration**: Environment variable handling
6. **External APIs**: Mocked external service responses

## 🔄 Cache System Design

### Cache Files Structure
```json
// brand-cache.json - Brand search results
{
  "query_text": {
    "query": "search_term",
    "success": true, 
    "data": [{"id": "brand_id", "name": "Brand Name", ...}],
    "total_results": 10,
    "cached_at": "2025-07-27T10:30:00Z"
  }
}

// brand-competitors.json - Competitor data
{
  "brand_id": {
    "None": {...},      // No area specified
    "area_id": {...}    // Specific area
  }
}

// brand-areas.json - Area suggestions  
{
  "brand_id": {
    "success": true,
    "data": [{"id": "area_id", "name": "Area Name", ...}]
  }
}
```

### Cache Service Features
- **File-based persistence** with JSON format
- **Error resilience** with corrupted file recovery
- **Size limiting** to prevent unbounded growth
- **TTL support** for cache expiration
- **Search capabilities** across cached data

## 🤖 AI Integration (Together.ai)

### Implementation Details
```python
# Together.ai API Integration
- Endpoint: https://api.together.xyz/v1/chat/completions
- Model: Configurable via TOGETHER_AI_MODEL environment variable  
- Use Cases:
  * Competitor discovery with business context
  * Area suggestions for brands
  * Structured JSON responses with relevance scoring
```

### AI Prompt Engineering
- **Competitor Discovery**: "Find competitors for {brand} in {area} with reasoning"
- **Area Suggestions**: "Suggest business areas relevant to {brand}"
- **Response Format**: Structured JSON with scores and explanations
- **Error Handling**: Graceful fallback to cached/mock data

## 🐛 Common Issues & Solutions

### Server Startup Issues
```python
# Issue: Module import errors with uvicorn
# Solution: Use direct Python execution with path manipulation
python simple_server.py  # Simplified server for development
python start_server.py   # Full server with path resolution
```

### Testing Issues
```python
# Issue: Async test failures
# Solution: Use pytest-asyncio and proper async/await patterns

# Issue: Mock configuration in older tests  
# Solution: Use working test files (test_cache_fixed.py, test_cache_updated.py)
```

### Cache File Issues
```python
# Issue: JSON corruption or missing files
# Solution: Services auto-create missing files and handle corruption
```

## 📦 Dependencies

### Core Dependencies
```
fastapi>=0.104.0           # Web framework
uvicorn[standard]>=0.24.0  # ASGI server  
pydantic>=2.0              # Data validation
httpx>=0.25.0              # HTTP client
python-multipart>=0.0.6    # Form parsing
```

### Development Dependencies
```
pytest>=7.4.0             # Testing framework
pytest-asyncio>=0.21.0    # Async testing
pytest-cov>=4.1.0         # Coverage reporting
coverage>=7.3.0           # Coverage measurement
```

## 🎯 Next Development Priorities

### Immediate Improvements
1. **Server Startup**: Resolve uvicorn module import issues for reliable deployment
2. **Cache Performance**: Implement TTL and size limits for production use
3. **API Rate Limiting**: Add rate limiting for external API calls
4. **Error Monitoring**: Enhanced error tracking and alerting

### Feature Enhancements  
1. **Authentication**: API key authentication for production
2. **Database Integration**: Move from JSON files to database backend
3. **Real-time Updates**: WebSocket support for live competitor data
4. **Analytics**: Usage metrics and performance monitoring

### Testing Improvements
1. **Integration Tests**: More end-to-end scenarios with real APIs
2. **Performance Tests**: Load testing for cache and API endpoints  
3. **Contract Tests**: API contract validation
4. **Security Tests**: Input validation and injection testing

## 💡 Development Tips for Copilot

### Code Patterns to Follow
1. **Use async/await** for all API endpoints and external calls
2. **Implement cache-first logic** for all data retrieval
3. **Add comprehensive logging** with structured format
4. **Include error handling** with specific exception types
5. **Write tests** for new functionality with good coverage

### Existing Helper Functions
```python
# In app/config.py
config.get_fmp_search_url(query)        # FMP API URL builder
config.get_alpha_vantage_symbol_search_url(query) # AV URL builder
config.get_together_ai_chat_url()        # Together.ai URL builder

# In cache services
cache_service.get_cached_search(query, limit)     # Retrieve cached data
cache_service.cache_search_response(query, data)  # Store in cache
```

### Testing Patterns
```python
# Use these working test patterns
@pytest.mark.asyncio
async def test_api_endpoint():
    with patch('app.services.external_api_call') as mock_call:
        mock_call.return_value = test_data
        response = await client.post("/endpoint", json=request_data)
        assert response.status_code == 200
```

This context should help Copilot understand the project structure, current implementation status, and development patterns to continue building upon this foundation effectively.

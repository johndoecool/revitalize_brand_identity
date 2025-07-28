# Brand Service

A FastAPI microservice for brand management, providing APIs for brand search, area suggestions, and competitor discovery.

## Features

- **Brand Search API** - Search for brands with intelligent caching
- **Area Suggestions API** - Get relevant analysis areas for brands
- **Competitor Discovery API** - Find competitors in specific areas
- **Smart Caching** - Automatic caching of search results with cache management APIs
- **Comprehensive Logging** - Detailed logging with multiple log levels and file separation
- **OpenAPI documentation** - Interactive API documentation with Swagger UI and ReDoc
- **Unit tests** - Comprehensive test coverage including API, services, and cache functionality

## Logging Features

The service includes comprehensive logging with the following features:

### Log Files
- `logs/brand-service-YYYY-MM-DD.log` - General application logs (detailed format)
- `logs/brand-service-cache.log` - Cache-specific operations (JSON format)
- `logs/brand-service-api.log` - API request logs (JSON format)  
- `logs/brand-service-errors.log` - Error logs only

### Logged Operations
- **Cache Operations**: Cache hits/misses, cache writes, cache statistics
- **Brand Search**: Query parameters, result counts, data sources (cache vs fresh)
- **API Requests**: Endpoint access, request parameters, response status
- **Service Operations**: Service initialization, data retrieval, error handling

### Log Levels
- **DEBUG**: Detailed technical information
- **INFO**: General operational information
- **WARNING**: Important notices
- **ERROR**: Error conditions

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

3. Access the API documentation:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## API Endpoints

### Brand APIs
- `POST /api/v1/brands/search` - Search for brands
- `GET /api/v1/brands/{brand_id}/areas` - Get area suggestions for a brand
- `GET /api/v1/brands/{brand_id}/competitors` - Get competitors for a brand in a specific area

### Cache Management APIs
- `GET /api/v1/cache/stats` - Get cache statistics
- `DELETE /api/v1/cache/clear` - Clear all cache
- `DELETE /api/v1/cache/query/{query}` - Remove specific cached query
- `GET /api/v1/cache/search?q={term}` - Search through cache
- `POST /api/v1/cache/export?export_path={path}` - Export cache to file
- `POST /api/v1/cache/import?import_path={path}&merge={bool}` - Import cache from file

## Cache Management

The service includes a JSON-based cache (`brand-cache.json`) that stores search results. You can manage the cache programmatically using:

### Command Line Tool
```bash
# Show cache statistics
python cache_manager.py stats

# Clear all cache
python cache_manager.py clear

# Search cache
python cache_manager.py search "Bank"

# Add brand to cache
python cache_manager.py add "OFG Bank" --brand-id "ofg_bank" --brand-name "OFG Bank" --brand-industry "Banking"

# List all cached queries
python cache_manager.py list
```

### Cache API Endpoints
Use the `/api/v1/cache/*` endpoints for programmatic cache management.

## Testing

Run all tests:
```bash
pytest
```

Run specific test suites:
```bash
# API tests
pytest tests/test_api.py -v

# Service tests
pytest tests/test_services.py -v

# Cache tests
pytest tests/test_cache.py -v

# Logging tests
pytest tests/test_logging.py -v
```

## Logging Demo

Run the logging demonstration:
```bash
python logging_demo.py
```

This will perform various operations and show how they are logged, including:
- Cache hits and misses
- Search operations
- Service initialization
- Cache management

## Docker Support

Build and run with Docker:
```bash
# Build image
docker build -t brand-service .

# Run container
docker run -p 8001:8001 brand-service

# Or use docker-compose
docker-compose up
```

## Project Structure

```
brand-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── services.py          # Business logic
│   ├── cache_service.py     # Cache management
│   ├── logging_config.py    # Logging configuration
│   └── api/
│       ├── __init__.py
│       ├── brands.py        # Brand API endpoints
│       └── cache.py         # Cache management endpoints
├── tests/
│   ├── test_api.py          # API integration tests
│   ├── test_services.py     # Service unit tests
│   ├── test_cache.py        # Cache functionality tests
│   └── test_logging.py      # Logging tests
├── logs/                    # Log files (auto-created)
├── brand-cache.json         # Cache data file
├── cache_manager.py         # Cache management CLI tool
├── logging_demo.py          # Logging demonstration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

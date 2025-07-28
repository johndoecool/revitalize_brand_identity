# Data Collection Service

**Team 3 - Data Collection Service** (Satyajit & Nilanjan)  
*Vibecoding Hackathon 2024*

## Overview

The Data Collection Service is a comprehensive brand analysis platform that collects and analyzes data from multiple sources to help businesses understand their brand perception and competitive position.

## Features

- 🔍 **Multi-Source Data Collection**: News, Social Media, Glassdoor, Website Analysis
- ⚡ **Asynchronous Processing**: Background jobs with real-time progress tracking
- 📊 **Comprehensive Analysis**: Sentiment analysis, performance metrics, competitive insights
- 🔄 **Flexible Storage**: Support for both flat file and vector database storage
- 📋 **RESTful API**: Well-documented API with OpenAPI specification
- 🚀 **Production Ready**: Proper logging, error handling, and monitoring

## Architecture

```
data-collection-service/
├── src/
│   ├── api/                # FastAPI endpoints
│   ├── collectors/         # Data collection modules
│   ├── config/            # Configuration management
│   ├── database/          # Data storage layer
│   ├── models/            # Pydantic schemas
│   └── services/          # Business logic
├── data/                  # Local data storage
├── logs/                  # Application logs
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
└── .env                  # Environment configuration
```

## Data Sources

### 1. News Sentiment Analysis
- Collects news articles from various sources
- Performs sentiment analysis on brand mentions
- Tracks positive, negative, and neutral coverage

### 2. Social Media Analysis
- Twitter, Facebook, and LinkedIn monitoring
- Sentiment analysis of brand mentions
- Engagement metrics and trending topics

### 3. Glassdoor Reviews
- Employee satisfaction ratings
- Company culture insights
- Pros and cons analysis

### 4. Website Analysis
- Performance metrics (load time, UX score)
- Security and accessibility analysis
- Feature completeness assessment

## Quick Start

### Prerequisites

- Python 3.8+
- Redis (optional, for background jobs)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   cd revitalize_brand_identity/data-collection-service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the service**
   ```bash
   python run.py
   ```

The service will be available at:
- **API Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health
- **API Base**: http://localhost:8002/api/v1/

## API Usage

### Start Data Collection

```bash
curl -X POST "http://localhost:8002/api/v1/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "oriental_bank_pr",
    "competitor_id": "banco_popular",
    "area_id": "self_service_portal",
    "sources": ["news", "social_media", "glassdoor", "website"]
  }'
```

Response:
```json
{
  "success": true,
  "job_id": "collect_12345678",
  "status": "started",
  "estimated_duration": 180
}
```

### Check Job Status

```bash
curl "http://localhost:8002/api/v1/collect/collect_12345678/status"
```

### Get Collected Data

```bash
curl "http://localhost:8002/api/v1/collect/collect_12345678/data"
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8002` |
| `HOST` | Service host | `0.0.0.0` |
| `DEBUG` | Debug mode | `true` |
| `USE_VECTOR_DB` | Use ChromaDB | `true` |
| `NEWS_API_KEY` | News API key | `None` |
| `TWITTER_BEARER_TOKEN` | Twitter API token | `None` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |

### Data Sources Configuration

The service supports configurable data sources with rate limiting:

- **News**: 1000 requests/hour
- **Social Media**: 500 requests/hour  
- **Glassdoor**: 100 requests/hour
- **Website Analysis**: 50 requests/hour

## Development

### Project Structure

```python
# Core modules
src/
├── api/endpoints.py       # FastAPI route handlers
├── models/schemas.py      # Pydantic data models
├── config/settings.py     # Configuration management
├── database/storage.py    # Data persistence layer
├── services/job_manager.py # Background job management
└── collectors/
    ├── base.py           # Base collector class
    ├── news_collector.py # News data collection
    ├── social_media_collector.py # Social media analysis
    ├── glassdoor_collector.py # Employee reviews
    └── website_collector.py # Website analysis
```

### Adding New Data Sources

1. **Create collector class**:
   ```python
   from src.collectors.base import BaseCollector
   from src.models.schemas import DataSource
   
   class NewCollector(BaseCollector):
       def __init__(self):
           super().__init__(DataSource.NEW_SOURCE)
       
       async def collect_brand_data(self, brand_id: str, area_id: str):
           # Implementation here
           pass
   ```

2. **Update schemas**:
   ```python
   # Add to DataSource enum
   class DataSource(str, Enum):
       NEW_SOURCE = "new_source"
   ```

3. **Register in factory**:
   ```python
   # Update CollectorFactory.create_collector()
   ```

### Testing

```bash
# Run with mock data (no API keys required)
python run.py

# Test endpoints
curl http://localhost:8002/health
curl http://localhost:8002/api/v1/sources/config
```

## Storage Options

### Flat File Storage (Default)
- JSON files in `./data/` directory
- Simple and reliable
- Good for development and small deployments

### Vector Database (ChromaDB)
- Advanced querying capabilities
- Automatic fallback to flat files
- Better for production deployments

## Deployment

### Production Deployment

1. **Set production environment**:
   ```bash
   export DEBUG=false
   export LOG_LEVEL=WARNING
   ```

2. **Use production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002
   ```

3. **Configure reverse proxy** (nginx, Apache, etc.)

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8002

CMD ["python", "main.py"]
```

## Monitoring

### Health Check
- **GET** `/health` - Service health status
- **GET** `/api/v1/stats` - Service statistics

### Logging
- Structured logging with Loguru
- File rotation and retention
- Configurable log levels

### Metrics
- Active job counts
- Success rates
- Average processing times

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/collect` | Start data collection job |
| GET | `/api/v1/collect/{job_id}/status` | Get job status |
| GET | `/api/v1/collect/{job_id}/data` | Get collected data |
| GET | `/api/v1/sources/config` | Get sources configuration |
| GET | `/health` | Health check |
| DELETE | `/api/v1/collect/{job_id}` | Cancel job |
| GET | `/api/v1/stats` | Service statistics |

### Data Models

The service uses comprehensive Pydantic models for data validation:

- `CollectionRequest` - Job creation request
- `CollectedData` - Complete analysis results
- `BrandData` - Individual brand metrics
- `NewsSentiment` - News analysis results
- `SocialMediaData` - Social media metrics
- `GlassdoorData` - Employee review data
- `WebsiteAnalysis` - Website performance metrics

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check Python version (3.8+ required)
   - Verify all dependencies installed
   - Check port 8002 availability

2. **No data collected**
   - Verify API keys in `.env` file
   - Check network connectivity
   - Review logs in `logs/app.log`

3. **Jobs stuck in progress**
   - Check Redis connection
   - Restart service to clear stuck jobs
   - Monitor system resources

### Support

For issues and questions:
- Check the logs: `tail -f logs/app.log`
- Verify configuration: `GET /api/v1/sources/config`
- Test connectivity: `GET /health`

## License

This project was developed for the Vibecoding Hackathon 2024.

## Team

**Team 3 - Data Collection Service**
- Satyajit
- Nilanjan

---

*Built with ❤️ for Vibecoding Hackathon 2024* 
# Analysis Engine Service

A comprehensive AI-powered brand analysis and comparison service using OpenAI GPT for generating actionable insights, recommendations, and competitive intelligence.

## Features

- **OpenAI GPT Integration**: AI-powered analysis using GPT-4 for intelligent brand comparison
- **Brand Comparison Engine**: Comprehensive brand vs competitor analysis
- **Actionable Insights**: Prioritized recommendations with implementation roadmaps
- **Trend Analysis**: Pattern recognition and trend analysis from historical data
- **Report Generation**: Formatted reports with executive summaries and detailed breakdowns
- **Confidence Scoring**: AI model validation and confidence metrics
- **Real-time Progress**: Background processing with progress tracking
- **Batch Analysis**: Support for multiple simultaneous analyses

## API Endpoints

### Core Analysis Endpoints

- `POST /api/v1/analyze` - Start new analysis
- `GET /api/v1/analyze/{id}/status` - Check analysis progress
- `GET /api/v1/analyze/{id}/results` - Get complete results
- `GET /api/v1/analyze/{id}/report` - Generate formatted report
- `GET /api/v1/analyze/{id}/insights` - Get insights summary
- `POST /api/v1/analyze/batch` - Batch analysis processing

### Health & Monitoring

- `GET /health` - Service health check
- `GET /api/v1/health` - Detailed health status

## Quick Start

### 1. Environment Setup

```powershell
# Navigate to the analysis service directory
cd services\analysis_service

# Create virtual environment
python -m venv analysis_env

# Activate virtual environment
analysis_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template and configure your settings:

```powershell
copy .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
SERVICE_PORT=8003
LOG_LEVEL=INFO
```

### 3. Run the Service

```powershell
# Development mode with auto-reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Or run directly
python app\main.py
```

### 4. Test the Service

The service will be available at:
- API: http://localhost:8003
- Documentation: http://localhost:8003/docs
- Alternative docs: http://localhost:8003/redoc

## Usage Examples

### Start Analysis

```python
import requests

# Analysis request
data = {
    "brand_data": {
        "brand": {"name": "Oriental Bank", "id": "oriental_bank"},
        "brand_data": {
            "news_sentiment": {"score": 0.75, "articles_count": 45},
            "social_media": {"followers": 50000, "engagement_rate": 0.03}
        }
    },
    "competitor_data": {
        "competitor": {"name": "Banco Popular", "id": "banco_popular"},
        "brand_data": {
            "news_sentiment": {"score": 0.85, "articles_count": 62},
            "social_media": {"followers": 75000, "engagement_rate": 0.05}
        }
    },
    "area_id": "self_service_portal",
    "analysis_type": "comprehensive"
}

# Start analysis
response = requests.post("http://localhost:8003/api/v1/analyze", json=data)
analysis_id = response.json()["analysis_id"]
```

### Check Progress

```python
# Check status
status_response = requests.get(f"http://localhost:8003/api/v1/analyze/{analysis_id}/status")
print(f"Progress: {status_response.json()['data']['progress']}%")
```

### Get Results

```python
# Get complete results (when analysis is complete)
results = requests.get(f"http://localhost:8003/api/v1/analyze/{analysis_id}/results")
analysis_data = results.json()["data"]

print(f"Brand Score: {analysis_data['overall_comparison']['brand_score']}")
print(f"Competitor Score: {analysis_data['overall_comparison']['competitor_score']}")
print(f"Total Insights: {len(analysis_data['actionable_insights'])}")
```

## Project Structure

```
analysis_service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── analysis.py         # Pydantic models and data schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── analysis.py         # API route handlers
│   └── services/
│       ├── __init__.py
│       ├── analysis_engine.py  # Core analysis orchestration
│       ├── openai_service.py   # OpenAI GPT integration
│       └── report_service.py   # Report generation and formatting
├── tests/
│   ├── __init__.py
│   ├── test_api.py            # API integration tests
│   ├── test_analysis_engine.py # Analysis engine unit tests
│   ├── test_openai_service.py  # OpenAI service tests
│   └── test_report_service.py  # Report service tests
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
└── README.md                  # This file
```

## Development

### Running Tests

```powershell
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_analysis_engine.py

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```powershell
# Format code
pip install black
black app/ tests/

# Lint code
pip install flake8
flake8 app/ tests/
```

## OpenAI Integration Details

### Key Features

1. **Intelligent Analysis**: Uses GPT-4 for sophisticated brand comparison
2. **Structured Prompts**: Carefully crafted prompts for consistent analysis
3. **Error Handling**: Robust error handling for API failures
4. **Confidence Scoring**: Built-in validation and confidence metrics

### Analysis Process

1. **Data Preprocessing**: Validates and normalizes input data
2. **AI Analysis**: Sends structured prompts to OpenAI GPT
3. **Result Parsing**: Converts AI responses to structured data
4. **Trend Analysis**: Additional AI analysis for pattern recognition
5. **Confidence Validation**: Validates analysis quality and reliability
6. **Report Generation**: Formats results into comprehensive reports

## API Contract Compliance

This service implements the exact API contracts specified in the project documentation:

- ✅ `POST /api/v1/analyze` - Analysis request endpoint
- ✅ `GET /api/v1/analyze/{analysis_id}/status` - Status monitoring
- ✅ `GET /api/v1/analyze/{analysis_id}/results` - Results retrieval
- ✅ Background processing with progress tracking
- ✅ Comprehensive analysis data structure
- ✅ Actionable insights and recommendations
- ✅ Market positioning analysis

## Monitoring & Health

### Health Checks

The service provides multiple health check endpoints:

```powershell
# Basic health check
curl http://localhost:8003/health

# Detailed health status
curl http://localhost:8003/api/v1/health
```

### Logging

Comprehensive logging is implemented throughout the service:

- Analysis start/completion events
- OpenAI API interactions
- Error tracking and debugging
- Performance metrics

## Production Considerations

### Security

- Environment-based configuration
- API key protection
- Input validation and sanitization
- Error message sanitization

### Performance

- Asynchronous processing
- Background task management
- Efficient OpenAI API usage
- Response caching considerations

### Scalability

- Stateless service design
- Horizontal scaling capability
- Database integration ready
- Load balancing support

## Troubleshooting

### Common Issues

1. **OpenAI API Key Issues**
   ```
   Error: OPENAI_API_KEY is required
   Solution: Set your OpenAI API key in the .env file
   ```

2. **Import Errors**
   ```
   Error: Module not found
   Solution: Ensure virtual environment is activated and dependencies installed
   ```

3. **Port Conflicts**
   ```
   Error: Port 8003 already in use
   Solution: Change SERVICE_PORT in .env or stop conflicting service
   ```

### Logs

Check application logs for detailed error information:

```powershell
# Run with detailed logging
LOG_LEVEL=DEBUG python app/main.py
```

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure OpenAI integration best practices
5. Test with demo data before deployment

## License

This project is part of the Revitalize Brand Identity microservice architecture.

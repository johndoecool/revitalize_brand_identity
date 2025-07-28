# Analysis Engine Service

A comprehensive brand analysis service with LLM provider toggle support for competitive intelligence and actionable insights.

## 🚀 Features

- **LLM Provider Toggle**: Switch between OpenAI and Together.ai
- **Comprehensive Analysis**: Brand vs competitor analysis with scoring
- **Actionable Insights**: Priority-based recommendations with implementation steps
- **Real-time Status**: Track analysis progress with polling endpoints
- **Trend Analysis**: Market positioning and trend identification
- **Health Monitoring**: Service health and LLM connectivity checks

## 🔧 LLM Provider Configuration

### Supported Providers

1. **OpenAI GPT-4** (Default)
   - High-quality analysis with proven reliability
   - Requires OpenAI API key

2. **Together.ai Llama-3.3-70B** 
   - Cost-effective alternative with excellent performance
   - Requires Together.ai API key

### Switching Providers

Edit the `.env` file to change the LLM provider:

```bash
# For OpenAI (default)
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# For Together.ai
LLM_PROVIDER=together
TOGETHER_API_KEY=your_together_api_key_here
TOGETHER_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo-Free
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | Choose `openai` or `together` | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4` |
| `TOGETHER_API_KEY` | Together.ai API key | - |
| `TOGETHER_MODEL` | Together.ai model name | `meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` |

## 📦 Installation

1. **Navigate to the analysis-engine directory:**
   ```bash
   cd analysis-engine
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferred LLM provider
   ```

## 🏃‍♂️ Quick Start

### Option 1: Direct Start (Recommended)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

### Option 2: Python Module Mode
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

### Option 3: Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003 --workers 4
```

## 📊 API Endpoints

### 1. Start Analysis
**POST** `/api/v1/analyze`

Start a new brand analysis comparing brand data with competitor data.

**Request Body:**
```json
{
  "brand_data": {
    "brand_id": "oriental_bank_pr",
    "news_sentiment": {"score": 0.75},
    "social_media": {"overall_sentiment": 0.68},
    "glassdoor": {"overall_rating": 3.8},
    "website_analysis": {"user_experience_score": 0.82}
  },
  "competitor_data": {
    "brand_id": "banco_popular",
    "news_sentiment": {"score": 0.82},
    "social_media": {"overall_sentiment": 0.74},
    "glassdoor": {"overall_rating": 4.1},
    "website_analysis": {"user_experience_score": 0.89}
  },
  "area_id": "self_service_portal",
  "analysis_type": "comprehensive"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "analysis_id": "analysis_12345678",
  "status": "processing",
  "estimated_duration": 60
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid analysis data provided",
    "details": {
      "field": "brand_data",
      "value": "{}"
    }
  },
  "timestamp": "2025-07-28T21:00:00Z"
}
```

---

### 2. Check Analysis Status
**GET** `/api/v1/analyze/{analysis_id}/status`

Get the current status and progress of an analysis.

**Path Parameters:**
- `analysis_id` (string): The unique identifier of the analysis

**Success Response - Processing (200):**
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_12345678",
    "status": "processing",
    "progress": 45,
    "current_step": "Generating competitive analysis",
    "estimated_completion": "2025-07-28T21:35:00Z"
  }
}
```

**Success Response - Completed (200):**
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_12345678",
    "status": "completed",
    "progress": 100,
    "completed_at": "2025-07-28T21:30:00Z"
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Analysis not found",
    "details": {
      "field": "analysis_id",
      "value": "analysis_12345678"
    }
  },
  "timestamp": "2025-07-28T21:00:00Z"
}
```

---

### 3. Get Analysis Results
**GET** `/api/v1/analyze/{analysis_id}/results`

Retrieve the complete results of a finished analysis.

**Path Parameters:**
- `analysis_id` (string): The unique identifier of the analysis

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_12345678",
    "area_id": "self_service_portal",
    "brand_name": "Oriental Bank PR",
    "competitor_name": "Banco Popular",
    "overall_comparison": {
      "brand_score": 0.76,
      "competitor_score": 0.84,
      "gap": -0.08,
      "brand_ranking": "second",
      "confidence_level": 0.92
    },
    "detailed_comparison": {
      "user_experience": {
        "brand_score": 0.82,
        "competitor_score": 0.89,
        "difference": -0.07,
        "insight": "Competitor has superior UI/UX design and mobile optimization",
        "trend": "improving"
      },
      "customer_satisfaction": {
        "brand_score": 0.75,
        "competitor_score": 0.81,
        "difference": -0.06,
        "insight": "Higher employee satisfaction correlates with better customer service",
        "trend": "stable"
      }
    },
    "actionable_insights": [
      {
        "priority": "high",
        "category": "Technology",
        "title": "Implement Advanced Mobile Banking Features",
        "description": "Enhance mobile app with biometric authentication and advanced financial tools",
        "estimated_effort": "3-6 months",
        "expected_impact": "Increase UX score by 0.15 points",
        "roi_estimate": "15-25% improvement in customer satisfaction",
        "implementation_steps": [
          "Conduct UX audit of current mobile app",
          "Research competitor mobile features",
          "Develop biometric authentication system",
          "Implement advanced financial planning tools",
          "Conduct user testing and feedback collection"
        ],
        "success_metrics": [
          "Mobile app rating >4.5 stars",
          "15% increase in mobile engagement",
          "Reduced customer support tickets"
        ]
      }
    ],
    "strengths_to_maintain": [
      {
        "area": "Brand Trust",
        "description": "Strong local market presence and customer loyalty",
        "recommendation": "Continue community engagement and local sponsorships",
        "current_score": 0.88
      }
    ],
    "market_positioning": {
      "brand_position": "Local community-focused bank with traditional values",
      "competitor_position": "Technology-forward regional bank with modern services",
      "differentiation_opportunity": "Combine traditional trust with modern technology",
      "target_audience": "Local professionals and small businesses"
    },
    "trend_analysis": {
      "brand_trend": "Gradual digital transformation needed",
      "competitor_trend": "Strong digital innovation momentum",
      "market_trend": "Increasing demand for digital banking solutions",
      "recommendations": [
        "Accelerate digital transformation initiatives",
        "Invest in mobile-first customer experience",
        "Maintain competitive advantage in personal service"
      ]
    },
    "confidence_score": 0.89,
    "created_at": "2025-07-28T21:00:00Z",
    "completed_at": "2025-07-28T21:30:00Z"
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Analysis not found",
    "details": {
      "field": "analysis_id",
      "value": "analysis_12345678"
    }
  },
  "timestamp": "2025-07-28T21:00:00Z"
}
```

---

### 4. Get Analysis History
**GET** `/api/v1/analyze/history`

Retrieve a list of completed analyses with optional filtering.

**Query Parameters:**
- `brand_id` (string, optional): Filter by specific brand ID
- `limit` (integer, optional): Maximum number of results (1-100, default: 10)

**Example Request:**
```bash
GET /api/v1/analyze/history?brand_id=oriental_bank_pr&limit=5
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "analysis_id": "analysis_12345678",
      "brand_id": "oriental_bank_pr",
      "competitor_id": "banco_popular", 
      "area_id": "self_service_portal",
      "status": "completed",
      "overall_score": 0.76,
      "completed_at": "2025-07-28T21:30:00Z"
    },
    {
      "analysis_id": "analysis_87654321",
      "brand_id": "oriental_bank_pr",
      "competitor_id": "firstbank_pr",
      "area_id": "mobile_banking",
      "status": "completed", 
      "overall_score": 0.82,
      "completed_at": "2025-07-27T15:45:00Z"
    }
  ]
}
```

---

### 5. Health Check
**GET** `/health`

Check the health status of the Analysis Engine service and its dependencies.

**Success Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-28T21:00:00Z",
  "version": "1.0.0",
  "dependencies": {
    "llm_service": "healthy",
    "openai_api": "connected",
    "together_api": "connected"
  },
  "uptime": "2h 45m 30s",
  "memory_usage": "245.6 MB",
  "active_analyses": 3
}
```

**Degraded Response (200):**
```json
{
  "status": "degraded",
  "timestamp": "2025-07-28T21:00:00Z",
  "version": "1.0.0",
  "dependencies": {
    "llm_service": "healthy",
    "openai_api": "disconnected",
    "together_api": "connected"
  },
  "uptime": "2h 45m 30s",
  "memory_usage": "245.6 MB",
  "active_analyses": 1,
  "warnings": ["OpenAI API connection issues"]
}
```

---

### 6. Root Endpoint
**GET** `/`

Get basic service information and documentation links.

**Success Response (200):**
```json
{
  "message": "Analysis Engine Service",
  "version": "1.0.0",
  "timestamp": "2025-07-28T21:00:00Z",
  "docs": "/docs"
}
```

## 🧪 Testing & Verification

### Test LLM Connectivity
```bash
# Test OpenAI provider
curl -X POST "http://localhost:8003/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_data": {"brand_id": "test_brand"},
    "competitor_data": {"brand_id": "test_competitor"},
    "area_id": "test_area",
    "analysis_type": "comprehensive"
  }'
```

### Test Health Endpoint
```bash
curl http://localhost:8003/health
```

### Switch Providers and Test
```bash
# 1. Edit .env to change LLM_PROVIDER
# 2. Restart service
# 3. Test with the same curl command above
```

This will verify:
- LLM service initialization and connectivity
- Analysis engine workflow
- Provider switching functionality
- API response format compliance

## 🔧 Configuration Details

### LLM Service Architecture

The `LLMService` class provides a unified interface for both providers:

```python
from app.services.llm_service import LLMService

# Automatically uses the configured provider
llm_service = LLMService()

# Generate completion with either provider
response = await llm_service.generate_completion(messages)
```

### Provider-Specific Features

**OpenAI GPT-4:**
- Excellent reasoning and analysis quality
- Consistent response format
- Reliable API uptime

**Together.ai Llama-3.3-70B:**
- Cost-effective for high-volume usage
- Strong performance on analytical tasks
- Open-source model flexibility

## 📈 Analysis Output Structure

The service returns comprehensive analysis results:

```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_12345",
    "overall_comparison": {
      "brand_score": 0.76,
      "competitor_score": 0.84,
      "gap": -0.08,
      "brand_ranking": "second"
    },
    "detailed_comparison": {
      "user_experience": {
        "brand_score": 0.82,
        "competitor_score": 0.89,
        "difference": -0.07,
        "insight": "Competitor has superior UI/UX design"
      }
    },
    "actionable_insights": [
      {
        "priority": "high",
        "title": "Implement Advanced Mobile Banking Features",
        "implementation_steps": ["...", "..."],
        "expected_impact": "Increase UX score by 0.15"
      }
    ]
  }
}
```

## 🚀 Production Deployment

1. **Set production environment variables**
2. **Choose appropriate LLM provider based on cost/quality requirements**
3. **Configure logging level** (`LOG_LEVEL=INFO`)
4. **Set up monitoring** for health endpoint
5. **Configure rate limiting** for API endpoints

## 🤝 Integration with Other Services

The Analysis Engine integrates with:
- **Data Collection Service** (port 8002): Raw data input
- **Brand Service** (port 8001): Brand metadata
- **Frontend Service**: Analysis visualization

## 📋 API Contract Compliance

This implementation maintains full compatibility with the expected API contract defined in the Postman collection:
- Identical request/response formats
- Same endpoint paths and methods
- Consistent error handling structure
- Matching data models and validation

## 🔍 Troubleshooting

### Common Issues

1. **LLM API Key Not Working:**
   - Verify API key in `.env` file
   - Check API key permissions and quotas
   - Test connectivity with simple requests

2. **Analysis Fails:**
   - Check input data format matches examples
   - Verify LLM provider is accessible
   - Review service logs for error details

3. **Service Won't Start:**
   - Ensure port 8003 is available
   - Install all required dependencies
   - Check Python version compatibility

### Debug Mode

Enable debug logging and start service:
```bash
# Set environment variable and start
LOG_LEVEL=DEBUG uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

### Test API Manually
```bash
# Check service is running
curl http://localhost:8003/health

# Test analysis endpoint
curl -X POST "http://localhost:8003/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_data": {"brand_id": "test_brand", "news_sentiment": {"score": 0.75}},
    "competitor_data": {"brand_id": "test_competitor", "news_sentiment": {"score": 0.82}},
    "area_id": "test_area",
    "analysis_type": "comprehensive"
  }'
```

## 🔄 Analysis Engine Processing Flow

The following diagram illustrates the internal processing logic of the Analysis Engine service:

```mermaid
flowchart TD
    A["HTTP Request /api/v1/analyze"] --> B["Request Logging Middleware"]
    B --> C["Analysis Router"]
    C --> D["Input Validation"]
    
    D --> E{"Valid Input?"}
    E -->|No| F["Return 400 Error"]
    E -->|Yes| G["Analysis Engine Service"]
    
    G --> H["Generate Analysis ID"]
    H --> I["Extract Brand & Competitor Data"]
    
    I --> J["LLM Service Provider Check"]
    J --> K{"Provider Type?"}
    
    K -->|OpenAI| L["OpenAI GPT-4 Client"]
    K -->|Together.ai| M["Together.ai HTTP Client"]
    
    L --> N["Build Analysis Prompt"]
    M --> N
    
    N --> O["Context Assembly"]
    O --> P["Brand Data Context"]
    O --> Q["Competitor Data Context"]
    O --> R["Analysis Instructions"]
    
    P --> S["LLM API Call"]
    Q --> S
    R --> S
    
    S --> T{"API Success?"}
    T -->|No| U["Fallback Response Generation"]
    T -->|Yes| V["Parse LLM Response"]
    
    U --> W["Structure Fallback Results"]
    V --> X["Extract Analysis Components"]
    
    X --> Y["Overall Comparison Scores"]
    X --> Z["Detailed Category Analysis"]
    X --> AA["Actionable Insights"]
    X --> BB["Strengths & Positioning"]
    
    Y --> CC["Build AnalysisResults Object"]
    Z --> CC
    AA --> CC
    BB --> CC
    W --> CC
    
    CC --> DD["Response Logging"]
    DD --> EE["Return JSON Response"]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style J fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style L fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style M fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style S fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    style CC fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style EE fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    
    classDef httpNode fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef llmNode fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef dataNode fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef resultNode fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef errorNode fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px
    
    class A,B,C,DD,EE httpNode
    class J,K,L,M,N,O,S,V llmNode
    class P,Q,R,I,Y,Z,AA,BB dataNode
    class CC,W,X resultNode
    class F,U,T errorNode
```

### 🔧 Key Processing Steps

1. **Request Handling**: HTTP middleware logs all requests and routes to analysis endpoint
2. **Data Validation**: Ensures proper format of brand and competitor data
3. **Provider Selection**: Dynamically chooses between OpenAI or Together.ai based on configuration
4. **Context Building**: Assembles comprehensive prompts with brand data and analysis instructions
5. **LLM Processing**: Makes API calls with robust error handling and SSL bypass for corporate environments
6. **Response Parsing**: Extracts structured analysis components from AI responses
7. **Fallback Logic**: Generates contextual responses when LLM calls fail
8. **Result Structuring**: Builds standardized AnalysisResults with scores and insights
9. **Response Delivery**: Returns JSON with comprehensive logging

### 🎯 Analysis Components Generated

- **Overall Scores**: Brand vs competitor numerical comparisons
- **Category Analysis**: Detailed breakdown by business areas
- **Actionable Insights**: Priority-ranked recommendations with implementation steps
- **Competitive Strengths**: Brand advantages and market positioning analysis

## 📝 License

This service is part of the Brand Identity Revitalization project.

# API Contracts - Day 0 Deliverables

## Overview
This document contains complete API specifications for all 4 microservices. Each team must implement these exact contracts to ensure seamless integration.

## Service Architecture

```
Frontend (Team 1) ←→ Brand Service (Team 2)
     ↓                    ↓
Data Collection ←→ Analysis Engine
   (Team 3)         (Team 4)
```

## 1. Brand Service API (Team 2: Srini & Sandipan)

### Base URL: `http://localhost:8001`

### 1.1 Brand Search API
```yaml
POST /api/v1/brands/search
Content-Type: application/json

Request:
{
  "query": "Oriental Bank",
  "limit": 10
}

Response:
{
  "success": true,
  "data": [
    {
      "id": "oriental_bank_pr",
      "name": "Oriental Bank",
      "full_name": "Oriental Bank of Puerto Rico",
      "industry": "Banking",
      "logo_url": "https://example.com/oriental_bank_logo.png",
      "description": "Leading bank in Puerto Rico",
      "confidence_score": 0.95
    }
  ],
  "total_results": 1
}
```

### 1.2 Area Suggestions API
```yaml
GET /api/v1/brands/{brand_id}/areas
Content-Type: application/json

Response:
{
  "success": true,
  "data": [
    {
      "id": "self_service_portal",
      "name": "Self Service Portal",
      "description": "Online banking and customer self-service capabilities",
      "relevance_score": 0.92,
      "metrics": ["user_experience", "feature_completeness", "security"]
    },
    {
      "id": "employer_branding",
      "name": "Employer Branding",
      "description": "Company reputation as an employer",
      "relevance_score": 0.78,
      "metrics": ["employee_satisfaction", "compensation", "work_life_balance"]
    }
  ]
}
```

### 1.3 Competitor Discovery API
```yaml
GET /api/v1/brands/{brand_id}/competitors?area={area_id}
Content-Type: application/json

Response:
{
  "success": true,
  "data": [
    {
      "id": "banco_popular",
      "name": "Banco Popular",
      "logo_url": "https://example.com/banco_popular_logo.png",
      "industry": "Banking",
      "relevance_score": 0.89,
      "competition_level": "direct"
    },
    {
      "id": "first_bank",
      "name": "First Bank",
      "logo_url": "https://example.com/first_bank_logo.png",
      "industry": "Banking",
      "relevance_score": 0.76,
      "competition_level": "direct"
    }
  ]
}
```

## 2. Data Collection Service API (Team 3: Satyajit & Nilanjan)

### Base URL: `http://localhost:8002`

### 2.1 Data Collection Request API
```yaml
POST /api/v1/collect
Content-Type: application/json

Request:
{
  "brand_id": "oriental_bank_pr",
  "competitor_id": "banco_popular",
  "area_id": "self_service_portal",
  "sources": ["news", "social_media", "glassdoor", "website"]
}

Response:
{
  "success": true,
  "job_id": "collect_12345",
  "status": "started",
  "estimated_duration": 180
}
```

### 2.2 Collection Status API
```yaml
GET /api/v1/collect/{job_id}/status
Content-Type: application/json

Response:
{
  "success": true,
  "data": {
    "job_id": "collect_12345",
    "status": "in_progress",
    "progress": 65,
    "completed_sources": ["news", "social_media"],
    "remaining_sources": ["glassdoor", "website"],
    "estimated_completion": "2024-01-15T10:30:00Z"
  }
}
```

### 2.3 Data Retrieval API
```yaml
GET /api/v1/collect/{job_id}/data
Content-Type: application/json

Response:
{
  "success": true,
  "data": {
    "brand_data": {
      "brand_id": "oriental_bank_pr",
      "news_sentiment": {
        "score": 0.75,
        "articles_count": 45,
        "positive_articles": 34,
        "negative_articles": 8,
        "neutral_articles": 3
      },
      "social_media": {
        "overall_sentiment": 0.68,
        "mentions_count": 1234,
        "engagement_rate": 0.045,
        "platforms": {
          "twitter": {"sentiment": 0.72, "mentions": 567},
          "facebook": {"sentiment": 0.65, "mentions": 432},
          "linkedin": {"sentiment": 0.71, "mentions": 235}
        }
      },
      "glassdoor": {
        "overall_rating": 3.8,
        "reviews_count": 89,
        "pros": ["Good benefits", "Work-life balance"],
        "cons": ["Limited growth opportunities"],
        "recommendation_rate": 0.78
      },
      "website_analysis": {
        "user_experience_score": 0.82,
        "feature_completeness": 0.75,
        "security_score": 0.88,
        "accessibility_score": 0.79
      }
    },
    "competitor_data": {
      "brand_id": "banco_popular",
      "news_sentiment": {
        "score": 0.82,
        "articles_count": 67,
        "positive_articles": 52,
        "negative_articles": 10,
        "neutral_articles": 5
      },
      "social_media": {
        "overall_sentiment": 0.74,
        "mentions_count": 1890,
        "engagement_rate": 0.052,
        "platforms": {
          "twitter": {"sentiment": 0.78, "mentions": 890},
          "facebook": {"sentiment": 0.71, "mentions": 678},
          "linkedin": {"sentiment": 0.76, "mentions": 322}
        }
      },
      "glassdoor": {
        "overall_rating": 4.1,
        "reviews_count": 156,
        "pros": ["Career growth", "Competitive salary"],
        "cons": ["High workload"],
        "recommendation_rate": 0.85
      },
      "website_analysis": {
        "user_experience_score": 0.89,
        "feature_completeness": 0.82,
        "security_score": 0.91,
        "accessibility_score": 0.84
      }
    }
  }
}
```

## 3. Analysis Engine API (Team 4: Prakash & Prakash)

### Base URL: `http://localhost:8003`

### 3.1 Analysis Request API
```yaml
POST /api/v1/analyze
Content-Type: application/json

Request:
{
  "brand_data": { /* Data from Data Collection Service */ },
  "competitor_data": { /* Data from Data Collection Service */ },
  "area_id": "self_service_portal",
  "analysis_type": "comprehensive"
}

Response:
{
  "success": true,
  "analysis_id": "analysis_67890",
  "status": "processing",
  "estimated_duration": 60
}
```

### 3.2 Analysis Status API
```yaml
GET /api/v1/analyze/{analysis_id}/status
Content-Type: application/json

Response:
{
  "success": true,
  "data": {
    "analysis_id": "analysis_67890",
    "status": "completed",
    "progress": 100,
    "completed_at": "2024-01-15T10:35:00Z"
  }
}
```

### 3.3 Analysis Results API
```yaml
GET /api/v1/analyze/{analysis_id}/results
Content-Type: application/json

Response:
{
  "success": true,
  "data": {
    "analysis_id": "analysis_67890",
    "area_id": "self_service_portal",
    "brand_name": "Oriental Bank",
    "competitor_name": "Banco Popular",
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
        "insight": "Banco Popular has superior user interface design"
      },
      "feature_completeness": {
        "brand_score": 0.75,
        "competitor_score": 0.82,
        "difference": -0.07,
        "insight": "Oriental Bank lacks advanced mobile banking features"
      },
      "security": {
        "brand_score": 0.88,
        "competitor_score": 0.91,
        "difference": -0.03,
        "insight": "Both banks have strong security measures"
      }
    },
    "actionable_insights": [
      {
        "priority": "high",
        "category": "feature_development",
        "title": "Implement Advanced Mobile Banking",
        "description": "Develop mobile app features like biometric authentication and real-time notifications",
        "estimated_effort": "3-4 months",
        "expected_impact": "Increase user experience score by 0.15",
        "implementation_steps": [
          "Conduct user research for mobile banking needs",
          "Design mobile-first user interface",
          "Implement biometric authentication",
          "Add real-time transaction notifications"
        ]
      },
      {
        "priority": "medium",
        "category": "user_experience",
        "title": "Improve Website Navigation",
        "description": "Redesign website navigation for better user flow",
        "estimated_effort": "2-3 months",
        "expected_impact": "Increase user experience score by 0.08",
        "implementation_steps": [
          "Analyze user journey patterns",
          "Redesign navigation structure",
          "Implement A/B testing",
          "Optimize for mobile responsiveness"
        ]
      }
    ],
    "strengths_to_maintain": [
      {
        "area": "security",
        "description": "Strong security measures are competitive advantage",
        "recommendation": "Continue investing in security infrastructure"
      }
    ],
    "market_positioning": {
      "brand_position": "Reliable traditional banking",
      "competitor_position": "Innovative digital banking",
      "differentiation_opportunity": "Focus on personalized customer service"
    }
  }
}
```

## 4. Frontend Service API (Team 1: Chandu & Avishek)

### Base URL: `http://localhost:3000`

### 4.1 WebSocket Connection (Real-time Progress)
```yaml
WebSocket: ws://localhost:3000/ws/progress

Message Format:
{
  "type": "progress_update",
  "job_id": "collect_12345",
  "progress": 65,
  "current_step": "Collecting Glassdoor data",
  "estimated_remaining": 120
}
```

### 4.2 Demo Data API
```yaml
GET /api/v1/demo/scenarios
Content-Type: application/json

Response:
{
  "success": true,
  "data": [
    {
      "id": "banking_demo",
      "name": "Banking Comparison",
      "brand": "Oriental Bank",
      "competitor": "Banco Popular",
      "area": "Self Service Portal",
      "preview_image": "/demo/banking_preview.png"
    },
    {
      "id": "tech_demo",
      "name": "Tech Employer Branding",
      "brand": "Microsoft",
      "competitor": "Google",
      "area": "Employer Branding",
      "preview_image": "/demo/tech_preview.png"
    },
    {
      "id": "healthcare_demo",
      "name": "Healthcare Product Comparison",
      "brand": "Pfizer",
      "competitor": "Moderna",
      "area": "Product Innovation",
      "preview_image": "/demo/healthcare_preview.png"
    }
  ]
}
```

## Error Response Format

All APIs follow this error format:
```yaml
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid brand ID provided",
    "details": {
      "field": "brand_id",
      "value": "invalid_id"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Common Error Codes
- `VALIDATION_ERROR`: Invalid input parameters
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable
- `INTERNAL_ERROR`: Internal server error

## Mock Data Requirements

Each team must provide realistic mock data that:
1. **Matches the exact response format** specified above
2. **Includes all required fields** with realistic values
3. **Covers error scenarios** with appropriate error codes
4. **Supports all 3 demo scenarios** (Banking, Tech, Healthcare)

## Integration Testing Checklist

- [ ] All APIs return expected response format
- [ ] Error handling works correctly
- [ ] Mock data is realistic and complete
- [ ] WebSocket connections function properly
- [ ] Demo scenarios load successfully
- [ ] Progress tracking works end-to-end 
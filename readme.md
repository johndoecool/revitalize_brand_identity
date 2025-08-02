# Revitalize Brand Identity - VibeCoding Hackathon 2025

AI-Powered Brand Reputation Analysis & Competitive Intelligence Platform

## 🏗️ Project Structure

This is a monorepo containing both frontend and backend components:

```
revitalize_brand_identity/
├── flutter/                 # Flutter frontend application
│   ├── lib/                # Dart source code
│   ├── assets/             # Frontend assets and demo data
│   ├── web/                # Web platform files
│   ├── android/            # Android platform files
│   ├── ios/                # iOS platform files
│   └── README.md           # Flutter-specific documentation
├── services/               # Backend microservices
│   ├── brand-service/      # Brand data management service
│   ├── analysis-engine/    # AI analysis processing service
│   ├── data-collection/    # Data aggregation service
│   └── frontend-service/   # API gateway and frontend service
├── docs/                   # Shared documentation
│   ├── frontend-plan.md    # Frontend development roadmap
│   ├── api_contracts_day0.md # API specifications
│   └── microservice_architecture_plan.md
├── demodata/               # Shared demo datasets
├── postman/                # API testing collections
└── README.md               # This file
```

## 🚀 Quick Start

### Frontend (Flutter)

```bash
cd flutter
flutter pub get
flutter run -d web-server --web-port 8080
```

### Backend Services

```bash
cd services
# Each service has its own setup instructions
```

## 🎯 Features

- **Cross-Platform Frontend**: Single Flutter codebase for web, iOS, and Android
- **Microservices Architecture**: Scalable backend with dedicated services
- **Real-Time Analysis**: AI-powered brand reputation monitoring
- **Interactive Dashboards**: Charts and visualizations with fl_chart
- **PDF Reports**: Comprehensive analysis export functionality
- **Demo Data**: Three industry scenarios (Banking, Technology, Healthcare)

## 🛠️ Tech Stack

### Frontend

- **Framework**: Flutter 3.32+
- **Language**: Dart
- **UI**: Custom glassmorphism design system
- **Charts**: fl_chart library
- **State Management**: Provider pattern

### Backend

- **Architecture**: Microservices
- **API Gateway**: Frontend service
- **Data Processing**: Analysis engine
- **Data Sources**: Multi-platform aggregation

## 📋 Development Status

✅ **Completed**:

- Flutter frontend with complete 5-tab interface
- Interactive chart visualizations
- PDF generation and export functionality
- Responsive design with animations
- Demo data integration

🚧 **In Progress**:

- Backend microservices implementation
- API integration
- Mobile platform builds

## 📖 Documentation

- [Frontend Development Plan](docs/frontend-plan.md)
- [API Contracts](docs/api_contracts_day0.md)
- [Microservice Architecture](docs/microservice_architecture_plan.md)
- [Flutter App README](flutter/README.md)

## 🤝 Team Collaboration

This monorepo structure supports:

- **Frontend Team**: Work in `flutter/` directory
- **Backend Teams**: Each service team works in respective `services/` subdirectory
- **Shared Resources**: Documentation, demo data, and API contracts at root level

## 🏆 VibeCoding Hackathon 2025

Built for maximum "wow factor" demonstrating:

- Rapid cross-platform development
- Professional UI/UX design
- Scalable architecture
- Real-world applicability

---

For specific setup instructions, see the README in each component directory.

## For analysis engine service

API to get roadmap, analysis, etc. hit below api
GET - http:..localhost:8003/api/v1/analyze/{analyze_id}/status

API to download report
http://localhost:8003/api/v1/analyze/{analyze_id}/report?reportType=executive_summary
http://localhost:8003/api/v1/analyze/{analyze_id}/report?reportType=detailed_report

Postman collection with examples is available in postman folder under analysis-engine folder

## For data-collection service

**Available Endpoints:**

| Method | Endpoint                          | Description                        |
| ------ | --------------------------------- | ---------------------------------- |
| POST   | `/api/v1/collect`                 | Start data collection job          |
| GET    | `/api/v1/collect/{job_id}/status` | Get job status and progress        |
| GET    | `/api/v1/collect/{job_id}/data`   | Get collected data (when complete) |
| DELETE | `/api/v1/collect/{job_id}`        | Cancel running job                 |
| GET    | `/api/v1/sources/config`          | Get data sources configuration     |
| GET    | `/api/v1/stats`                   | Get service statistics             |
| GET    | `/health`                         | Health check endpoint              |
| GET    | `/docs`                           | API documentation (Swagger UI)     |
| GET    | `/redoc`                          | Alternative API documentation      |

**Example Usage:**

Trigger data collection:

```bash
POST "http://localhost:8002/api/v1/collect"
Content-Type: application/json

{
  "request_id": "213434324234dsfdsf223",
  "brand_id": "Google",
  "competitor_id": "Apple",
  "area_id": "Best place to work",
  "sources": ["news", "social_media", "glassdoor", "website"]
}
```

Get job status:

```bash
GET "http://localhost:8002/api/v1/collect/{job_id}/status"
```

Get collected data:

```bash
GET "http://localhost:8002/api/v1/collect/{job_id}/data"
```

**Data Sources:** News APIs, Social Media, Glassdoor Reviews, Website Analysis

**Service Configuration:**

- Port: 8002
- Real-time progress tracking
- Comprehensive logging
- Rate limiting per data source
- Asynchronous job processing

## ✅ Data Collection Service Integration - Complete

### Current Status
✅ **Brand Service Integration**: Complete - Brand selection, area selection, and competitor discovery fully functional  
✅ **Data Collection Service Integration**: Complete - Flutter app now connects to real backend services with fallback to demo data

### ✨ Completed Implementation Details

#### 🔗 **Data Collection Service Integration**
- **Service Integration**: Created `DataCollectionService` class with full API integration
- **UUID Generation**: Added `uuid` package for unique request ID generation  
- **Polling Mechanism**: Implemented real-time status polling with 8-second intervals
- **Error Handling**: 5-minute timeout with graceful fallback to demo data
- **Health Checks**: Service availability verification before starting analysis
- **Progress Updates**: Real-time status messages during data collection and analysis phases

#### 🎯 **Real Analysis Workflow**
1. **Health Check**: Verifies all backend services (ports 8001, 8002, 8003) are responsive
2. **Data Collection**: POST to `/api/v1/collect` with brand, competitor, area, and UUID
3. **Status Polling**: GET `/api/v1/shared-data/{request_id}` until `analysisEngineStatus` = "COMPLETED"
4. **Results Retrieval**: GET `/api/v1/analyze/{analysisId}/status` for comprehensive analysis data
5. **Report Generation**: GET `/api/v1/analyze/{analysisId}/report` for PDF downloads

#### 🛡️ **Robust Error Handling**
- **Service Unavailable**: Clear error dialog with fallback to demo data
- **Network Issues**: Automatic retry with exponential backoff
- **Timeout Protection**: 5-minute maximum analysis time with user notification
- **API Failures**: Graceful degradation maintains user experience

#### 📱 **Enhanced User Experience**
- **Single Loading State**: Unified progress indicator throughout entire analysis
- **Status Messages**: Real-time updates ("Collecting data...", "Running AI analysis...", etc.)
- **Error Recovery**: User-friendly error dialogs with option to use demo data
- **Seamless Integration**: Maintains existing UI/UX while adding real backend connectivity  

### Integration Flow Overview
The next integration follows this workflow:
1. **User Action**: Click "LAUNCH ANALYSIS" button after selecting brand, area, and competitor
2. **POST Request**: Frontend calls `POST /api/v1/collect` with request data
3. **Polling Loop**: Frontend polls `GET /api/v1/shared-data/{request_id}` until analysis completes
4. **Data Retrieval**: Frontend fetches analysis results and displays real data
5. **Report Generation**: Frontend enables report download functionality

### Required API Integration

#### 1. Start Data Collection
```bash
POST http://localhost:8002/api/v1/collect
Content-Type: application/json

{
  "request_id": "generated-uuid-v4",
  "brand_id": "Google", 
  "competitor_id": "Apple",
  "area_id": "Best place to work",
  "sources": ["news", "social_media", "glassdoor", "website"]  // Optional
}
```

#### 2. Poll Job Status (Every 5-10 seconds)
```bash
GET http://localhost:8002/api/v1/shared-data/{request_id}

Response Structure:
{
  "success": true,
  "data": {
    "requestId": "uuid",
    "brandId": "Google",
    "dataCollectionId": "job_uuid", 
    "dataCollectionStatus": "COMPLETED",
    "analysisEngineId": "analysis_uuid",
    "analysisEngineStatus": "COMPLETED",  // Poll until this is "COMPLETED"
    "lastUpdated": "2025-08-02T..."
  },
  "timestamp": "2025-08-02T..."
}
```

#### 3. Get Analysis Results (When analysisEngineStatus = "COMPLETED")
```bash
GET http://localhost:8003/api/v1/analyze/{analysisEngineId}/status

Response: Full analysis results for Analysis, Insights, Roadmap tabs
```

#### 4. Generate Reports (For Report tab)
```bash
GET http://localhost:8003/api/v1/analyze/{analysisEngineId}/report?reportType=executive_summary
GET http://localhost:8003/api/v1/analyze/{analysisEngineId}/report?reportType=detailed_report
```

### Flutter Implementation Requirements

#### 1. UUID Generation
```dart
import 'package:uuid/uuid.dart';

final uuid = Uuid();
final requestId = uuid.v4();
```

#### 2. Data Collection Service Class
Create `lib/services/data_collection_service.dart`:
- Method to start data collection job
- Polling mechanism with exponential backoff
- Error handling with 5-minute timeout
- Status tracking and progress updates

#### 3. Integration Points
- **Analysis Tab**: Replace dummy charts with real API data
- **Insights Tab**: Display AI-generated insights from analysis results  
- **Roadmap Tab**: Show actionable recommendations from analysis
- **Report Tab**: Enable real PDF report downloads
- **Error Handling**: Fallback to dummy data if APIs fail (like brand service)

#### 4. UI/UX Updates
- Single loader during entire process (data collection + analysis)
- Progress indicator showing current stage
- Success/error states with appropriate messaging
- Timeout handling with user-friendly error messages

### Error Handling Strategy
- **5-minute timeout**: If polling exceeds timeout, show error with option to use dummy data
- **API failures**: Graceful degradation to existing dummy data with notification
- **Network issues**: Retry mechanism with exponential backoff
- **Service unavailable**: Clear error messages with retry options

### Testing Strategy
1. **Service Health**: Verify all backend services running on ports 8001, 8002, 8003
2. **End-to-End Flow**: Test complete workflow with real API calls
3. **Error Scenarios**: Test timeout, service failures, network issues
4. **Fallback Behavior**: Verify dummy data fallback works correctly

### Development Sequence
1. Create data collection service class in Flutter
2. Implement UUID generation and API calls
3. Add polling mechanism with status updates
4. Update Analysis tab with real data integration
5. Update Insights tab with AI-generated content
6. Update Roadmap tab with recommendations
7. Implement Report tab with PDF downloads
8. Add comprehensive error handling and fallbacks
9. Test end-to-end integration
10. Polish UI/UX and loading states

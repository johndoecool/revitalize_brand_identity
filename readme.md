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
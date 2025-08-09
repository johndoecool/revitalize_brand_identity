# Files to Create - Brand Intelligence Hub ADO Deployment

## 🐳 Container & Infrastructure Files

### 1. `analysis-engine/Dockerfile`
**Context**: Create Dockerfile for Python FastAPI service running on port 8003 using uvicorn, based on existing docker-compose patterns from brand-service, with health check endpoint and proper Python environment setup.

### 2. `api-gateway/Dockerfile` 
**Context**: Create nginx-based API gateway Dockerfile that routes /api/brand/* to brand-service:8001, /api/data/* to data-collection:8002, /api/analysis/* to analysis-engine:8003, with CORS headers and health check.

### 3. `api-gateway/nginx.conf`
**Context**: Nginx configuration file for API gateway with upstream definitions for three Python services, proper proxy headers, CORS configuration for Flutter web app, and load balancing.

### 4. `docker-compose.override.yml`
**Context**: Complete docker-compose file that orchestrates all 5 services (brand-service, data-collection, analysis-engine, api-gateway, redis) with shared network, Azure File Share volume mounts for JSON data, and proper service dependencies.

## 🏗️ Infrastructure as Code (Bicep)

### 5. `.azure/infrastructure/main.bicep`
**Context**: Azure Bicep template creating Container Group with 5 containers, Azure File Share for shared JSON storage, Container Registry, and all networking/security configurations for internal service communication.

### 6. `.azure/infrastructure/parameters/dev.bicepparam`
**Context**: Bicep parameters file for development environment with smaller resource allocations, debug enabled, and development-specific configurations.

### 7. `.azure/infrastructure/parameters/prod.bicepparam`
**Context**: Bicep parameters file for production environment with production-scale resources, security hardening, and monitoring enabled.

## 🚀 Azure DevOps Pipeline Files

### 8. `.azure/pipelines/azure-pipelines.yml`
**Context**: Main ADO pipeline with multi-stage deployment, triggers for main/develop branches, build jobs for 4 Docker images, infrastructure deployment using Bicep, and environment-specific deployments with approvals.

### 9. `.azure/pipelines/build-backend.yml`
**Context**: Template pipeline for building and pushing 4 Docker images (brand-service, data-collection, analysis-engine, api-gateway) to Azure Container Registry with proper tagging strategy.

### 10. `.azure/pipelines/build-frontend.yml`
**Context**: Template pipeline for building Flutter web application with environment-specific API endpoint configuration and deployment to Azure Static Web Apps.

### 11. `.azure/pipelines/deploy-infrastructure.yml`
**Context**: Template pipeline for deploying Azure infrastructure using Bicep templates with parameter files, resource group management, and output variable handling for subsequent deployment stages.

## 📱 Frontend Configuration

### 12. `flutter/web/config/config.dev.json`
**Context**: Development configuration file for Flutter web with API gateway URLs, debug settings, and development-specific feature flags for the Brand Intelligence Hub frontend.

### 13. `flutter/web/config/config.prod.json`
**Context**: Production configuration file for Flutter web with production API gateway URLs, analytics enabled, and production-specific settings.

### 14. `flutter/lib/config/environment_config.dart`
**Context**: Dart class for loading environment-specific configurations in Flutter app, handling API endpoints, debug modes, and runtime environment detection.

## 🔧 DevOps Configuration Files

### 15. `.azure/environments/dev.yml`
**Context**: Azure DevOps environment definition for development with auto-approval policies, variable group references, and development-specific deployment configurations.

### 16. `.azure/environments/prod.yml`
**Context**: Azure DevOps environment definition for production with manual approval gates, business hours restrictions, and production deployment safeguards.

### 17. `.azure/variable-groups/shared.yml`
**Context**: Shared variable group template defining common variables across environments like container registry name, resource naming conventions, and shared configuration values.

## 📋 Setup & Documentation Files

### 18. `scripts/setup-self-hosted-agent.sh`
**Context**: Shell script to install and configure Azure DevOps self-hosted agent on Ubuntu/macOS, with Docker installation, agent registration, and service configuration.

### 19. `scripts/setup-self-hosted-agent.ps1`
**Context**: PowerShell script for Windows to install and configure Azure DevOps self-hosted agent, including Docker Desktop setup and agent service registration.

### 20. `scripts/deploy-infrastructure.sh`
**Context**: Shell script for manual infrastructure deployment using Azure CLI and Bicep templates, with environment parameter handling and resource validation.

### 21. `.env.template`
**Context**: Environment variables template file showing all required variables for local development and production deployment, with example values and descriptions.

### 22. `deployment-checklist.md`
**Context**: Step-by-step checklist for deploying Brand Intelligence Hub to Azure using ADO, including prerequisites, validation steps, and troubleshooting guidance.

## 🔄 Utility & Maintenance Files

### 23. `scripts/health-check.sh`
**Context**: Health check script that verifies all services are running correctly in Azure Container Group, tests API endpoints, and validates service communication.

### 24. `scripts/logs-collector.sh`
**Context**: Script to collect and download logs from Azure Container Group for debugging purposes, with filtering options and log aggregation.

### 25. `azure-pipelines-variables.md`
**Context**: Documentation explaining all Azure DevOps variables, variable groups, and pipeline parameters needed for successful deployment and configuration management.

---

## 📊 Summary
- **Total Files**: 25
- **Docker Files**: 4
- **Infrastructure Files**: 4  
- **Pipeline Files**: 4
- **Frontend Config**: 3
- **DevOps Config**: 3
- **Scripts & Docs**: 7

Each file has specific context for generating production-ready code that integrates with your existing Brand Intelligence Hub services running on ports 8001-8003, Flutter web frontend, and Azure DevOps deployment pipeline.
# Azure DevOps Deployment Plan - Brand Intelligence Hub

## 🎯 Architecture Overview

```
Azure Container Group (Internal Network):
├── brand-service (port 8001) ← Internal only
├── data-collection (port 8002) ← Internal only
├── analysis-engine (port 8003) ← Internal only
├── redis (port 6379) ← Internal only
└── api-gateway (port 80) ← Public facing (routes to services)

Azure File Share:
└── Shared JSON data storage

Azure Static Web Apps:
└── Flutter Web App ← Points to API Gateway

Azure DevOps:
├── Build Pipeline (CI)
├── Release Pipeline (CD)
├── Environments (dev, staging, prod)
└── Variable Groups (secrets management)
```

## 🚀 Phase 1: Immediate Actions (Parallelism Issue)

### Option A: Self-Hosted Agent (Immediate)
1. **Install Azure DevOps Agent** on your local machine or a VM
2. **Register as self-hosted agent** in your ADO organization
3. **Use this for initial setup** while waiting for Microsoft-hosted parallelism

### Option B: Request Free Parallelism
1. Fill form: https://aka.ms/azpipelines-parallelism-request
2. Wait 5-10 business days for approval
3. Use Microsoft-hosted agents

**Recommendation: Go with Option A for immediate progress**

## 📁 Phase 2: Repository Structure Setup

```
brand-intelligence-hub/
├── .azure/
│   ├── pipelines/
│   │   ├── azure-pipelines.yml
│   │   ├── build-backend.yml
│   │   └── build-frontend.yml
│   ├── environments/
│   │   ├── dev.yml
│   │   ├── staging.yml
│   │   └── prod.yml
│   └── infrastructure/
│       ├── main.bicep
│       └── parameters/
├── brand-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ... (existing code)
├── data-collection/
│   ├── Dockerfile (existing)
│   └── ... (existing code)
├── analysis-engine/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ... (existing code)
├── api-gateway/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── ... (new component)
├── flutter/
│   └── ... (existing Flutter app)
├── shared-data/
│   └── ... (JSON files for all services)
├── docker-compose.yml (orchestration)
└── README.md
```

## 🔧 Phase 3: Infrastructure as Code (Bicep)

Create `.azure/infrastructure/main.bicep`:
- **Azure Container Group** with all services
- **Azure File Share** for shared JSON storage
- **Azure Static Web App** for Flutter frontend
- **Application Gateway** for routing (optional)
- **Log Analytics** for monitoring

## 🏗️ Phase 4: CI/CD Pipeline Setup

### Build Pipeline (azure-pipelines.yml)
```yaml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - brand-service/*
    - data-collection/*
    - analysis-engine/*
    - flutter/*

stages:
- stage: Build
  jobs:
  - job: BuildBackend
  - job: BuildFrontend
  - job: BuildInfrastructure

- stage: Deploy_Dev
  condition: eq(variables['Build.SourceBranch'], 'refs/heads/develop')
  
- stage: Deploy_Staging  
  condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')
  
- stage: Deploy_Production
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
```

### Key Pipeline Features:
1. **Multi-stage builds** (Backend services + Frontend)
2. **Container registry push** (Azure Container Registry)
3. **Infrastructure deployment** (Bicep templates)
4. **Environment-specific deployments**
5. **Automated testing** integration
6. **Manual approvals** for production

## 🌐 Phase 5: Service Architecture

### API Gateway (nginx-based)
```nginx
upstream brand_service {
    server brand-service:8001;
}
upstream data_collection {
    server data-collection:8002;
}
upstream analysis_engine {
    server analysis-engine:8003;
}

server {
    listen 80;
    
    location /api/brand/ {
        proxy_pass http://brand_service/;
    }
    location /api/data/ {
        proxy_pass http://data_collection/;
    }
    location /api/analysis/ {
        proxy_pass http://analysis_engine/;
    }
}
```

### Container Group Configuration
- **Shared network** for internal service communication
- **Azure File Share mount** for JSON data persistence
- **Environment variables** from Azure Key Vault
- **Health checks** and restart policies
- **Resource limits** and scaling

## 📱 Phase 6: Flutter Web Deployment

### Build Configuration
```yaml
- task: FlutterBuild@0
  inputs:
    target: 'web'
    projectDirectory: 'flutter'
    entryPoint: 'lib/main.dart'
    buildName: '$(Build.BuildNumber)'
    buildNumber: '$(Build.BuildId)'
```

### Deployment Options
1. **Azure Static Web Apps** (Recommended)
   - Built-in CDN
   - Custom domains
   - SSL certificates
   - Global distribution

2. **Azure Blob Storage + CDN**
   - Cost-effective
   - Manual SSL setup
   - Good performance

## 🔐 Phase 7: Security & Configuration

### Azure DevOps Variable Groups
```
Dev Environment:
├── API_GATEWAY_URL=https://dev-api.azurecontainer.com
├── REDIS_URL=redis://redis:6379
└── DEBUG=true

Staging Environment:
├── API_GATEWAY_URL=https://staging-api.azurecontainer.com
├── REDIS_URL=redis://redis:6379
└── DEBUG=false

Production Environment:
├── API_GATEWAY_URL=https://prod-api.azurecontainer.com
├── REDIS_URL=redis://redis:6379
└── DEBUG=false
```

### Azure Key Vault Integration
- **API Keys** storage
- **Connection strings** 
- **Service principal** credentials
- **SSL certificates**

## 🔄 Phase 8: Environment Management

### ADO Environments Setup
1. **Development**
   - Auto-deploy from `develop` branch
   - No approvals required
   - Shared resources

2. **Staging** 
   - Auto-deploy from `main` branch
   - Optional manual approval
   - Production-like setup

3. **Production**
   - Manual approval required
   - Business hours deployment only
   - Rollback capabilities

## 📊 Phase 9: Monitoring & Logging

### Azure Monitor Integration
- **Container insights**
- **Application performance monitoring**
- **Custom dashboards**
- **Alert rules**

### Log Analytics
- **Centralized logging** from all containers
- **Query capabilities**
- **Performance metrics**
- **Error tracking**

## 🎯 Phase 10: Implementation Timeline

### Week 1: Foundation
- [ ] Set up self-hosted agent
- [ ] Create repository structure
- [ ] Write Dockerfiles for missing services
- [ ] Create API Gateway

### Week 2: Infrastructure
- [ ] Create Bicep templates
- [ ] Set up Azure resources manually (first time)
- [ ] Configure networking and security
- [ ] Test container deployment

### Week 3: CI/CD
- [ ] Create build pipeline
- [ ] Set up container registry
- [ ] Configure release pipeline
- [ ] Test end-to-end deployment

### Week 4: Frontend & Integration
- [ ] Configure Flutter web build
- [ ] Deploy to Azure Static Web Apps
- [ ] Integration testing
- [ ] Performance optimization

## 🚨 Critical Success Factors

1. **Service Communication**: Ensure internal networking works
2. **Shared Storage**: Mount Azure File Share correctly
3. **Environment Variables**: Proper configuration management
4. **Health Checks**: All services must have `/health` endpoints
5. **CORS Configuration**: Frontend-backend communication
6. **SSL/TLS**: Secure communication in production

## 🛠️ Next Steps

1. **Confirm this architecture** meets your requirements
2. **Choose parallelism approach** (self-hosted vs wait for grant)
3. **Start with Phase 1** setup
4. **I'll create the actual YAML files** and Dockerfiles once confirmed

Would you like me to proceed with creating the specific implementation files (Dockerfiles, pipeline YAML, Bicep templates) for this plan?
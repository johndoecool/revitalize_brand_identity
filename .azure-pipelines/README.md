# Azure DevOps Pipelines for Revitalize Brand Identity

This directory contains the Azure DevOps pipeline configurations for building and deploying the microservices architecture.

## Pipeline Structure

### 1. Infrastructure Pipeline (`infrastructure-pipeline.yml`)
**Purpose**: Sets up the Azure infrastructure
**Triggers**: Changes to `azure-setup/` or the pipeline file itself
**What it does**:
- Creates Resource Group
- Sets up Azure Container Registry (ACR)
- Creates Storage Account and File Share
- Sets up Container Apps Environment
- Uploads shared database.json

### 2. Service Pipelines
Each microservice has its own dedicated pipeline:

#### Brand Service Pipeline (`brand-service-pipeline.yml`)
- **Triggers**: Changes to `brand-service/` directory
- **Python Version**: 3.11
- **Port**: 8001
- **Resource Requirements**: 0.5 CPU, 1Gi memory

#### Data Collection Pipeline (`data-collection-pipeline.yml`)
- **Triggers**: Changes to `data-collection/` directory  
- **Python Version**: 3.9
- **Port**: 8002
- **Resource Requirements**: 1.0 CPU, 2Gi memory
- **Note**: Selenium tests are skipped in CI/CD

#### Analysis Engine Pipeline (`analysis-engine-pipeline.yml`)
- **Triggers**: Changes to `analysis-engine/` directory
- **Python Version**: 3.11  
- **Port**: 8003
- **Resource Requirements**: 1.0 CPU, 2Gi memory

## Setup Instructions

### Prerequisites
1. Azure subscription with sufficient permissions
2. Azure DevOps organization and project
3. Azure CLI installed locally

### Step 1: Run Infrastructure Setup
```bash
cd azure-setup
chmod +x *.sh
./01-infrastructure-setup.sh
```

### Step 2: Create Service Principal
```bash
./02-service-principal-setup.sh
```

### Step 3: Set up Variable Groups
```bash
./03-variable-groups-setup.sh
```

### Step 4: Create Azure DevOps Service Connection
1. Go to Azure DevOps → Project Settings → Service Connections
2. Create new "Azure Resource Manager" connection
3. Use Service Principal (manual) method
4. Name it: `Azure-RevitalizeBrandIdentity`
5. Use the credentials from Step 2

### Step 5: Add API Keys to Variable Groups
1. Go to Azure DevOps → Pipelines → Library
2. Edit the "API-Keys" variable group
3. Add these secret variables:
   - `OPENAI_API_KEY`
   - `TOGETHER_API_KEY`

### Step 6: Create Pipelines in Azure DevOps
1. Go to Azure DevOps → Pipelines
2. Create new pipeline for each YAML file:
   - `infrastructure-pipeline.yml`
   - `brand-service-pipeline.yml`
   - `data-collection-pipeline.yml`
   - `analysis-engine-pipeline.yml`

## Pipeline Features

### Build Stage
- **Code Quality**: Black formatting and Flake8 linting
- **Testing**: Unit tests with pytest
- **Coverage**: Minimum 50% code coverage required
- **Docker**: Multi-stage builds with caching
- **Security**: Secrets managed via Azure Key Vault references

### Deploy Stage
- **Container Apps**: Serverless container deployment
- **Auto-scaling**: 1-5 replicas based on demand
- **Health Checks**: Automated service health verification
- **Rolling Updates**: Zero-downtime deployments
- **Environment Variables**: Secure secret management

## Variable Groups

### Azure-Config
- `RESOURCE_GROUP`: Azure resource group name
- `ACR_NAME`: Container registry name
- `CONTAINER_APPS_ENV`: Container Apps environment
- `SUBSCRIPTION_ID`: Azure subscription ID
- `LOCATION`: Azure region (East US)

### API-Keys (Secrets)
- `OPENAI_API_KEY`: OpenAI API key
- `TOGETHER_API_KEY`: Together AI API key

### Storage-Config
- `STORAGE_ACCOUNT_NAME`: Azure storage account
- `STORAGE_ACCOUNT_KEY`: Storage access key (secret)
- `FILE_SHARE_NAME`: File share name for shared data

### Container-Apps
- Service names and port configurations
- Resource allocation settings

## Monitoring and Troubleshooting

### Pipeline Logs
- Check build logs in Azure DevOps
- Review deployment logs for errors
- Monitor test results and coverage reports

### Application Logs
- Use Azure Container Apps log streaming
- Check application insights for runtime issues
- Monitor health endpoints

### Common Issues
1. **Service Connection**: Verify Azure permissions
2. **Variable Groups**: Ensure all secrets are populated
3. **Docker Build**: Check Dockerfile syntax and dependencies
4. **Health Checks**: Verify service startup time and endpoints

## Service URLs
After successful deployment, services will be available at:
- Brand Service: `https://ca-revitalize-brand-service.{region}.azurecontainerapps.io`
- Data Collection: `https://ca-revitalize-data-collection.{region}.azurecontainerapps.io`
- Analysis Engine: `https://ca-revitalize-analysis-engine.{region}.azurecontainerapps.io`

Each service provides:
- `/health` - Health check endpoint
- `/docs` - Interactive API documentation
- `/` - Service root endpoint

## Cost Optimization
- Container Apps use consumption-based pricing
- Services auto-scale to zero when not in use
- Resource limits prevent runaway costs
- Use Azure Cost Management for monitoring

## Security Best Practices
- All secrets stored in Azure Key Vault
- Container images scanned for vulnerabilities
- Network isolation via Container Apps environment
- HTTPS enforced for all external endpoints
- Least-privilege access for service principals
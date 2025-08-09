# How-To Deploy Brand Intelligence Hub to Azure ADO

## 🎯 Prerequisites Checklist

### Azure Requirements
- [ ] **Azure Subscription** with Contributor permissions
- [ ] **Azure DevOps Organization** with project admin rights
- [ ] **Azure CLI** installed locally (`az --version`)
- [ ] **Docker** installed for self-hosted agent

### ADO Project Setup
- [ ] **Project created** in Azure DevOps
- [ ] **Repository imported** with your existing code
- [ ] **Service connections** permissions available

---

## 🖥️ Phase 1: Self-Hosted Agent Setup (30 minutes)

### Step 1.1: Prepare Agent Machine
```bash
# For Ubuntu/Linux (run setup-self-hosted-agent.sh)
sudo apt update && sudo apt install -y docker.io curl wget
sudo usermod -aG docker $USER
# Log out and back in for docker group changes
```

### Step 1.2: Create Agent Pool in ADO
1. **Navigate**: ADO Project → Project Settings → Agent pools
2. **Click**: "Add pool" → "Self-hosted"  
3. **Name**: `Brand-Intelligence-Pool`
4. **Permissions**: Grant access to your project

### Step 1.3: Download & Configure Agent
1. **Navigate**: Agent pools → Brand-Intelligence-Pool → "New agent"
2. **Download** the agent package for your OS
3. **Run setup script**: `./scripts/setup-self-hosted-agent.sh`
4. **Verify**: Agent shows "Online" in ADO

### Step 1.4: Test Agent
```bash
# Create test pipeline in ADO with:
pool:
  name: Brand-Intelligence-Pool
steps:
- script: echo "Self-hosted agent working!"
```

---

## 🏗️ Phase 2: Azure Infrastructure Setup (45 minutes)

### Step 2.1: Create Azure Resources Manually (First Time)
```bash
# Login to Azure
az login

# Create resource group
az group create --name "rg-brand-intelligence-dev" --location "East US"

# Create container registry  
az acr create --name "acrbrandintelligence" --resource-group "rg-brand-intelligence-dev" --sku Basic --admin-enabled true
```

### Step 2.2: Create Service Principal for ADO
```bash
# Create service principal with Contributor role
az ad sp create-for-rbac --name "sp-brand-intelligence-ado" --role Contributor --scopes /subscriptions/{your-subscription-id}

# Note down: appId, password, tenant - needed for ADO service connection
```

### Step 2.3: Configure ADO Service Connections
1. **Navigate**: ADO Project → Project Settings → Service connections
2. **Create**: "Azure Resource Manager" connection
3. **Choose**: "Service principal (manual)"
4. **Fill**: Subscription ID, Service Principal details from Step 2.2
5. **Name**: `azure-connection-dev`
6. **Test**: Verify connection works

---

## 📦 Phase 3: ADO Repository & Pipeline Setup (60 minutes)

### Step 3.1: Repository Structure
```bash
# Add all new files to your existing repository
git add .azure/ scripts/ deployment-checklist.md
git add analysis-engine/Dockerfile api-gateway/
git add docker-compose.override.yml .env.template
git commit -m "Add Azure DevOps deployment configuration"
git push origin main
```

### Step 3.2: Create Variable Groups in ADO
1. **Navigate**: ADO Project → Pipelines → Library → Variable groups
2. **Create group**: `brand-intelligence-shared`
   - `AZURE_SUBSCRIPTION`: Your subscription ID
   - `CONTAINER_REGISTRY`: acrbrandintelligence.azurecr.io
   - `RESOURCE_GROUP_PREFIX`: rg-brand-intelligence

3. **Create group**: `brand-intelligence-dev`
   - `API_GATEWAY_URL`: https://dev-api.azurecontainer.com
   - `ENVIRONMENT`: dev
   - `DEBUG_ENABLED`: true

4. **Create group**: `brand-intelligence-prod`
   - `API_GATEWAY_URL`: https://prod-api.azurecontainer.com  
   - `ENVIRONMENT`: prod
   - `DEBUG_ENABLED`: false

### Step 3.3: Create ADO Environments
1. **Navigate**: ADO Project → Pipelines → Environments
2. **Create**: `Development`
   - **Approval policy**: None (auto-deploy)
   - **Security**: Allow all pipelines

3. **Create**: `Production`
   - **Approval policy**: Required (manual approval)
   - **Approvers**: Add yourself and team leads
   - **Business hours**: Optional restriction

---

## 🚀 Phase 4: Pipeline Deployment (30 minutes)

### Step 4.1: Create Main Pipeline
1. **Navigate**: ADO Project → Pipelines → Create Pipeline
2. **Choose**: "Azure Repos Git" → Select your repository
3. **Configure**: "Existing Azure Pipelines YAML file"
4. **Path**: `.azure/pipelines/azure-pipelines.yml`
5. **Review**: Pipeline YAML content
6. **Save**: Don't run yet

### Step 4.2: Configure Pipeline Variables
1. **Edit pipeline** → Variables
2. **Add variable groups**:
   - `brand-intelligence-shared`
   - `brand-intelligence-dev` 
   - `brand-intelligence-prod`
3. **Link to variable groups** in pipeline settings

### Step 4.3: Run First Deployment
1. **Run pipeline** from main branch
2. **Monitor**: Build stage completion
3. **Approve**: Development deployment (should be automatic)
4. **Verify**: All stages complete successfully

---

## 🌐 Phase 5: Frontend Deployment (20 minutes)

### Step 5.1: Create Static Web App
```bash
# Create Static Web App resource
az staticwebapp create \
  --name "swa-brand-intelligence-dev" \
  --resource-group "rg-brand-intelligence-dev" \
  --location "East US 2"

# Get deployment token
az staticwebapp secrets list --name "swa-brand-intelligence-dev" --query "properties.apiKey"
```

### Step 5.2: Configure Flutter Build Pipeline
1. **Add variable** to pipeline:
   - `STATIC_WEB_APP_TOKEN`: Token from Step 5.1
2. **Run pipeline** to deploy Flutter web app
3. **Get URL** from Static Web App overview in Azure portal

---

## 🔍 Phase 6: Verification & Testing (15 minutes)

### Step 6.1: Health Check Services
```bash
# Run health check script
./scripts/health-check.sh dev

# Expected output: All services responding ✅
```

### Step 6.2: Test Frontend Integration
1. **Open** Static Web App URL
2. **Test**: Brand analysis functionality
3. **Verify**: API calls to backend services work
4. **Check**: Browser developer console for errors

### Step 6.3: Review Logs
```bash
# Collect container logs
./scripts/logs-collector.sh dev

# Review logs for any issues
```

---

## 🎯 Phase 7: Production Deployment (10 minutes)

### Step 7.1: Merge to Main Branch
```bash
# Ensure all changes are in main branch
git checkout main
git pull origin main
```

### Step 7.2: Trigger Production Pipeline
1. **Pipeline** will automatically trigger for main branch
2. **Approve** staging deployment
3. **Approve** production deployment (manual gate)
4. **Monitor** deployment progress

---

## ✅ Success Verification Checklist

### Infrastructure
- [ ] **Container Group** running in Azure
- [ ] **All 5 containers** healthy (brand-service, data-collection, analysis-engine, api-gateway, redis)
- [ ] **Azure File Share** mounted and accessible
- [ ] **Static Web App** deployed and accessible

### Application
- [ ] **Flutter web app** loads without errors
- [ ] **API calls** work from frontend to backend
- [ ] **Service-to-service** communication working
- [ ] **Health checks** pass for all services

### DevOps  
- [ ] **Pipeline** runs successfully end-to-end
- [ ] **Environments** configured with proper approvals
- [ ] **Variable groups** linked correctly
- [ ] **Self-hosted agent** operating normally

---

## 🚨 Troubleshooting Common Issues

### Pipeline Fails
- **Check**: Self-hosted agent is online
- **Verify**: Service connection permissions
- **Review**: Variable group configurations

### Container Deployment Fails
- **Check**: Docker images built successfully
- **Verify**: Azure Container Registry access
- **Review**: Container Group logs in Azure portal

### Frontend Can't Reach Backend
- **Check**: API Gateway nginx configuration  
- **Verify**: CORS headers in nginx.conf
- **Test**: Direct container endpoint access

### Services Can't Communicate
- **Check**: Container Group networking
- **Verify**: Service discovery configuration
- **Test**: Internal DNS resolution

---

## 📞 Support & Next Steps

### Monitoring Setup
- Configure **Azure Monitor** for container insights
- Set up **Log Analytics** for centralized logging
- Create **alert rules** for service failures

### Security Hardening
- Implement **Azure Key Vault** for secrets
- Configure **managed identities** for service authentication
- Set up **network security groups** for container access

### Scaling Considerations
- Plan **Container Instances scaling** for production load
- Implement **Azure Load Balancer** for high availability
- Consider **Azure Kubernetes Service** for advanced orchestration

---

## 📋 Estimated Total Time: 3.5 hours
- **Phase 1**: 30 minutes (Self-hosted agent)
- **Phase 2**: 45 minutes (Azure infrastructure) 
- **Phase 3**: 60 minutes (ADO setup)
- **Phase 4**: 30 minutes (Pipeline deployment)
- **Phase 5**: 20 minutes (Frontend deployment)
- **Phase 6**: 15 minutes (Verification)
- **Phase 7**: 10 minutes (Production deployment)

Ready to proceed with creating all the implementation files! 🚀
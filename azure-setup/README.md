# Azure Infrastructure Setup for Revitalize Brand Identity

This directory contains scripts to set up the complete Azure infrastructure needed for the microservices deployment.

## Overview

The setup creates a modern, scalable, and cost-effective infrastructure using:
- **Azure Container Apps** - Serverless containers with auto-scaling
- **Azure Container Registry** - Private Docker image storage
- **Azure File Share** - Shared storage for database.json
- **Azure Resource Group** - Logical container for all resources

## Quick Start

Run these scripts in order:

```bash
# Make scripts executable
chmod +x *.sh

# 1. Set up Azure infrastructure
./01-infrastructure-setup.sh

# 2. Create service principal for Azure DevOps
./02-service-principal-setup.sh

# 3. Set up variable groups in Azure DevOps
./03-variable-groups-setup.sh
```

## Script Details

### 1. Infrastructure Setup (`01-infrastructure-setup.sh`)

Creates all the Azure resources needed:

**Resources Created:**
- Resource Group: `rg-revitalize-brand-identity-prod`
- Container Registry: `crrevitalizebrandidentity`
- Storage Account: `sarevitalizebrand{random}` 
- File Share: `shared-data`
- Container Apps Environment: `cae-revitalize-brand-identity-prod`

**What it does:**
- Checks for existing resources to avoid duplicates
- Creates resources with appropriate configurations
- Uploads shared/database.json to File Share
- Outputs summary with important connection details

**Prerequisites:**
- Azure CLI installed and configured
- Sufficient permissions in Azure subscription
- `shared/database.json` file exists in the repository

### 2. Service Principal Setup (`02-service-principal-setup.sh`)

Creates a service principal for Azure DevOps authentication:

**What it creates:**
- Service Principal: `sp-revitalize-brand-identity-devops`
- Contributor role on Resource Group
- ACR Push/Pull roles for Container Registry

**Outputs:**
- Service Principal credentials for Azure DevOps
- Step-by-step instructions for creating service connection
- Values to save for pipeline configuration

**Usage in Azure DevOps:**
1. Project Settings → Service Connections
2. New Service Connection → Azure Resource Manager
3. Service Principal (manual)
4. Use the provided credentials

### 3. Variable Groups Setup (`03-variable-groups-setup.sh`)

Creates variable groups in Azure DevOps:

**Variable Groups Created:**

#### Azure-Config
- Infrastructure settings (Resource Group, ACR, etc.)
- Automatically populated from Azure resources

#### API-Keys  
- External service credentials (requires manual setup)
- OPENAI_API_KEY, TOGETHER_API_KEY (mark as secret)

#### Storage-Config
- Azure Storage settings for shared data
- Includes storage account and access keys

#### Container-Apps
- Service names and port configurations
- Resource allocation settings

**Prerequisites:**
- Azure DevOps CLI extension installed
- Access to Azure DevOps organization
- Service principal from step 2 configured

## Architecture Diagram

```
Azure Subscription
├── Resource Group (rg-revitalize-brand-identity-prod)
│   ├── Container Registry (crrevitalizebrandidentity.azurecr.io)
│   ├── Storage Account (sarevitalizebrand{id})
│   │   └── File Share (shared-data)
│   │       └── database.json
│   ├── Container Apps Environment (cae-revitalize-brand-identity-prod)
│   │   ├── Brand Service (ca-revitalize-brand-service)
│   │   ├── Data Collection (ca-revitalize-data-collection)  
│   │   └── Analysis Engine (ca-revitalize-analysis-engine)
│   └── Log Analytics Workspace (auto-created)
```

## Configuration Details

### Naming Convention
All resources follow the pattern: `{type}-revitalize-brand-identity-{env}`
- `rg-` = Resource Group
- `cr` = Container Registry (no hyphens allowed)
- `ca-` = Container App
- `cae-` = Container Apps Environment
- `sa` = Storage Account (alphanumeric only)

### Resource Specifications

#### Container Registry
- **SKU**: Basic (cost-effective for development)
- **Admin enabled**: Yes (for simple authentication)
- **Public access**: Enabled (required for Container Apps)

#### Storage Account
- **SKU**: Standard_LRS (locally redundant)
- **Kind**: StorageV2 (general purpose v2)
- **File Share Quota**: 1GB (sufficient for JSON files)

#### Container Apps Environment
- **Location**: East US
- **Log Analytics**: Auto-created
- **Virtual Network**: Default (public endpoints)

## Security Considerations

### Access Control
- Service Principal has minimum required permissions
- Container Registry uses admin credentials (basic auth)
- Storage keys stored as secrets in variable groups
- All external endpoints use HTTPS

### Network Security
- Container Apps use public ingress (required for UI access)
- Internal service-to-service communication possible
- No custom virtual network (simplified setup)

### Secret Management
- API keys stored in Azure DevOps variable groups
- Marked as secret variables
- Injected as environment variables at runtime
- Storage keys secured in Key Vault references

## Cost Optimization

### Container Apps Pricing
- **Consumption-based**: Pay only for what you use
- **Auto-scaling**: Scale to zero when idle
- **Resource limits**: Prevent unexpected costs

### Estimated Monthly Costs (USD)
- Container Apps Environment: ~$0 (no base charge)
- Container Registry (Basic): ~$5
- Storage Account (1GB): ~$0.02
- Container Apps (light usage): ~$5-20
- **Total**: ~$10-25/month for development workloads

### Cost Monitoring
- Set up Azure Cost Management alerts
- Monitor resource usage in Azure Portal
- Use resource tags for cost allocation

## Troubleshooting

### Common Issues

#### Permission Errors
```bash
ERROR: Insufficient privileges to complete the operation
```
**Solution**: Ensure you have Contributor or Owner role on the subscription

#### Resource Name Conflicts
```bash
ERROR: Storage account name already exists
```
**Solution**: Storage account names are globally unique, script adds random suffix

#### Azure CLI Not Authenticated
```bash
ERROR: Please run 'az login' to setup account
```
**Solution**: Run `az login` and select the correct subscription

#### Container Apps Extension Missing
```bash
ERROR: Extension 'containerapp' is not installed
```
**Solution**: Run `az extension add --name containerapp`

### Verification Commands

Check if resources were created successfully:

```bash
# List all resources in the resource group
az resource list --resource-group rg-revitalize-brand-identity-prod --output table

# Check Container Registry
az acr list --resource-group rg-revitalize-brand-identity-prod --output table

# Check Storage Account
az storage account list --resource-group rg-revitalize-brand-identity-prod --output table

# Check Container Apps Environment
az containerapp env list --resource-group rg-revitalize-brand-identity-prod --output table
```

### Cleanup

To delete all resources (use with caution):

```bash
# Delete the entire resource group (removes all resources)
az group delete --name rg-revitalize-brand-identity-prod --yes --no-wait

# Delete service principal
az ad sp delete --id sp-revitalize-brand-identity-devops
```

## Next Steps

After running these scripts:

1. **Verify Infrastructure**: Check Azure Portal for created resources
2. **Set up Azure DevOps**: Create service connection using provided credentials  
3. **Add API Keys**: Manually add secret variables to API-Keys group
4. **Run Pipelines**: Execute the Azure DevOps pipelines
5. **Test Services**: Verify deployments and service endpoints
6. **Monitor Costs**: Set up cost alerts and monitoring

For detailed pipeline setup instructions, see [.azure-pipelines/README.md](../.azure-pipelines/README.md).
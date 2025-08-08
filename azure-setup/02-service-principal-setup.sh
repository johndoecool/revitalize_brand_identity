#!/bin/bash

# =============================================================================
# Azure Service Principal Setup for Azure DevOps
# =============================================================================
# This script creates a service principal for Azure DevOps pipelines
# =============================================================================

set -e

# Configuration
APP_NAME="sp-revitalize-brand-identity-devops"
RESOURCE_GROUP="rg-revitalize-brand-identity-prod"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_status "🔐 Creating Service Principal for Azure DevOps"
echo

# Check if service principal already exists
if az ad app list --display-name $APP_NAME --query "[0].appId" -o tsv | grep -q "."; then
    print_warning "Service Principal $APP_NAME already exists"
    APP_ID=$(az ad app list --display-name $APP_NAME --query "[0].appId" -o tsv)
    print_status "Using existing App ID: $APP_ID"
else
    print_status "Creating new Service Principal: $APP_NAME"
    
    # Create service principal
    SP_OUTPUT=$(az ad sp create-for-rbac \
        --name $APP_NAME \
        --role Contributor \
        --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
        --sdk-auth)
    
    APP_ID=$(echo $SP_OUTPUT | jq -r '.clientId')
    APP_SECRET=$(echo $SP_OUTPUT | jq -r '.clientSecret')
    TENANT_ID=$(echo $SP_OUTPUT | jq -r '.tenantId')
    
    print_success "Service Principal created successfully"
fi

# Get the service principal details
SP_DETAILS=$(az ad sp show --id $APP_ID)
SP_OBJECT_ID=$(echo $SP_DETAILS | jq -r '.id')

# Assign additional roles if needed
print_status "Assigning additional roles to Service Principal"

# Assign ACR Push/Pull role
ACR_NAME="crrevitalizebrandidentity"
ACR_ID=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query id -o tsv)

az role assignment create \
    --assignee $APP_ID \
    --role "AcrPush" \
    --scope $ACR_ID

az role assignment create \
    --assignee $APP_ID \
    --role "AcrPull" \
    --scope $ACR_ID

print_success "ACR roles assigned to Service Principal"

echo
print_success "🎉 Service Principal setup completed!"
echo
echo "=== Azure DevOps Service Connection Information ==="
echo "Use these details to create a service connection in Azure DevOps:"
echo
echo "Connection Type: Azure Resource Manager"
echo "Authentication Method: Service Principal (manual)"
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Subscription Name: $(az account show --query name -o tsv)"
echo "Service Principal ID: $APP_ID"
if [ ! -z "$APP_SECRET" ]; then
    echo "Service Principal Key: $APP_SECRET"
fi
echo "Tenant ID: $(az account show --query tenantId -o tsv)"
echo
echo "=== Steps to Create Service Connection in Azure DevOps ==="
echo "1. Go to Azure DevOps -> Project Settings -> Service Connections"
echo "2. Click 'New Service Connection'"
echo "3. Select 'Azure Resource Manager'"
echo "4. Choose 'Service Principal (manual)'"
echo "5. Fill in the details above"
echo "6. Name the connection: 'Azure-RevitalizeBrandIdentity'"
echo "7. Test and save the connection"
echo
echo "=== Save These Values for Pipeline Variables ==="
echo "SUBSCRIPTION_ID=$SUBSCRIPTION_ID"
echo "SERVICE_PRINCIPAL_ID=$APP_ID"
echo "TENANT_ID=$(az account show --query tenantId -o tsv)"
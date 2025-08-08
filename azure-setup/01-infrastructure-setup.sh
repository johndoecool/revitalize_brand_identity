#!/bin/bash

# =============================================================================
# Azure Infrastructure Setup for Revitalize Brand Identity
# =============================================================================
# This script creates all the Azure resources needed for the microservices
# =============================================================================

set -e

# Configuration
RESOURCE_GROUP="rg-revitalize-brand-identity-prod"
LOCATION="eastus"
ACR_NAME="crrevitalizebrandidentity"
CONTAINER_APPS_ENV="cae-revitalize-brand-identity-prod"
FILE_SHARE_ACCOUNT="sarevitalizebrand$(date +%s | tail -c 6)"  # Unique storage account
FILE_SHARE_NAME="shared-data"

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

# Function to check if resource exists
resource_exists() {
    local resource_type=$1
    local resource_name=$2
    local resource_group=${3:-$RESOURCE_GROUP}
    
    az $resource_type show --name $resource_name --resource-group $resource_group >/dev/null 2>&1
}

print_status "🚀 Starting Azure Infrastructure Setup for Revitalize Brand Identity"
echo

# 1. Create Resource Group
print_status "Creating Resource Group: $RESOURCE_GROUP"
if resource_exists "group" $RESOURCE_GROUP ""; then
    print_warning "Resource Group $RESOURCE_GROUP already exists"
else
    az group create --name $RESOURCE_GROUP --location $LOCATION
    print_success "Resource Group created: $RESOURCE_GROUP"
fi

# 2. Create Container Registry
print_status "Creating Azure Container Registry: $ACR_NAME"
if resource_exists "acr" $ACR_NAME; then
    print_warning "Container Registry $ACR_NAME already exists"
else
    az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
    print_success "Container Registry created: $ACR_NAME"
fi

# 3. Create Storage Account for File Share
print_status "Creating Storage Account: $FILE_SHARE_ACCOUNT"
if resource_exists "storage account" $FILE_SHARE_ACCOUNT; then
    print_warning "Storage Account $FILE_SHARE_ACCOUNT already exists"
else
    az storage account create \
        --name $FILE_SHARE_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2
    print_success "Storage Account created: $FILE_SHARE_ACCOUNT"
fi

# 4. Create File Share
print_status "Creating File Share: $FILE_SHARE_NAME"
STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $FILE_SHARE_ACCOUNT --query "[0].value" -o tsv)

# Check if file share exists
if az storage share exists --name $FILE_SHARE_NAME --account-name $FILE_SHARE_ACCOUNT --account-key $STORAGE_KEY --query "exists" -o tsv | grep -q "true"; then
    print_warning "File Share $FILE_SHARE_NAME already exists"
else
    az storage share create \
        --name $FILE_SHARE_NAME \
        --account-name $FILE_SHARE_ACCOUNT \
        --account-key $STORAGE_KEY \
        --quota 1
    print_success "File Share created: $FILE_SHARE_NAME"
fi

# 5. Upload shared database.json to File Share
print_status "Uploading shared database.json to File Share"
if [ -f "../shared/database.json" ]; then
    az storage file upload \
        --share-name $FILE_SHARE_NAME \
        --source "../shared/database.json" \
        --path "database.json" \
        --account-name $FILE_SHARE_ACCOUNT \
        --account-key $STORAGE_KEY
    print_success "Database.json uploaded to File Share"
else
    print_warning "shared/database.json not found - you'll need to upload it manually later"
fi

# 6. Create Container Apps Environment
print_status "Creating Container Apps Environment: $CONTAINER_APPS_ENV"
if resource_exists "containerapp env" $CONTAINER_APPS_ENV; then
    print_warning "Container Apps Environment $CONTAINER_APPS_ENV already exists"
else
    az containerapp env create \
        --name $CONTAINER_APPS_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
    print_success "Container Apps Environment created: $CONTAINER_APPS_ENV"
fi

# 7. Get ACR credentials for later use
print_status "Getting ACR credentials"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

echo
print_success "🎉 Infrastructure setup completed successfully!"
echo
echo "=== Resource Summary ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Container Registry: $ACR_NAME.azurecr.io"
echo "Storage Account: $FILE_SHARE_ACCOUNT"
echo "File Share: $FILE_SHARE_NAME"
echo "Container Apps Environment: $CONTAINER_APPS_ENV"
echo
echo "=== Next Steps ==="
echo "1. Set up Azure DevOps service connection with these credentials:"
echo "   ACR Username: $ACR_USERNAME"
echo "   ACR Password: $ACR_PASSWORD"
echo "2. Create variable groups in Azure DevOps"
echo "3. Run the pipeline setup scripts"
echo
echo "=== Important Information (Save These Values) ==="
echo "RESOURCE_GROUP=$RESOURCE_GROUP"
echo "ACR_NAME=$ACR_NAME"
echo "STORAGE_ACCOUNT=$FILE_SHARE_ACCOUNT"
echo "STORAGE_KEY=$STORAGE_KEY"
echo "FILE_SHARE_NAME=$FILE_SHARE_NAME"
echo "CONTAINER_APPS_ENV=$CONTAINER_APPS_ENV"
echo
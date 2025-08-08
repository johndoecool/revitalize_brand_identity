#!/bin/bash

# =============================================================================
# Azure DevOps Variable Groups Setup
# =============================================================================
# This script creates variable groups in Azure DevOps for the pipelines
# =============================================================================

set -e

# Configuration
ORGANIZATION="https://dev.azure.com/Vibects13"
PROJECT="118797"

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

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_status "📝 Setting up Azure DevOps Variable Groups"
echo

# Check if Azure DevOps CLI is configured
print_status "Configuring Azure DevOps CLI"
az devops configure --defaults organization=$ORGANIZATION project=$PROJECT

# Function to create variable group if it doesn't exist
create_variable_group() {
    local group_name=$1
    local description=$2
    
    print_status "Creating variable group: $group_name"
    
    # Check if variable group exists
    if az pipelines variable-group list --group-name "$group_name" --query "[0].name" -o tsv 2>/dev/null | grep -q "$group_name"; then
        print_warning "Variable group '$group_name' already exists"
        GROUP_ID=$(az pipelines variable-group list --group-name "$group_name" --query "[0].id" -o tsv)
        echo "Group ID: $GROUP_ID"
    else
        GROUP_ID=$(az pipelines variable-group create --name "$group_name" --variables placeholder=temp --description "$description" --query "id" -o tsv)
        print_success "Variable group '$group_name' created with ID: $GROUP_ID"
        
        # Remove placeholder variable
        az pipelines variable-group variable delete --group-id $GROUP_ID --name placeholder --yes
    fi
}

# Function to add variable to group
add_variable_to_group() {
    local group_name=$1
    local var_name=$2
    local var_value=$3
    local is_secret=${4:-false}
    
    GROUP_ID=$(az pipelines variable-group list --group-name "$group_name" --query "[0].id" -o tsv)
    
    if [ "$is_secret" = "true" ]; then
        az pipelines variable-group variable create --group-id $GROUP_ID --name "$var_name" --value "$var_value" --secret true
        print_success "Added secret variable '$var_name' to '$group_name'"
    else
        az pipelines variable-group variable create --group-id $GROUP_ID --name "$var_name" --value "$var_value"
        print_success "Added variable '$var_name' to '$group_name'"
    fi
}

# 1. Create Azure Configuration Variable Group
create_variable_group "Azure-Config" "Azure infrastructure configuration variables"

# Get current Azure settings
RESOURCE_GROUP="rg-revitalize-brand-identity-prod"
ACR_NAME="crrevitalizebrandidentity"
CONTAINER_APPS_ENV="cae-revitalize-brand-identity-prod"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
LOCATION="eastus"

# Add Azure configuration variables
add_variable_to_group "Azure-Config" "RESOURCE_GROUP" "$RESOURCE_GROUP"
add_variable_to_group "Azure-Config" "ACR_NAME" "$ACR_NAME"
add_variable_to_group "Azure-Config" "CONTAINER_APPS_ENV" "$CONTAINER_APPS_ENV"
add_variable_to_group "Azure-Config" "SUBSCRIPTION_ID" "$SUBSCRIPTION_ID"
add_variable_to_group "Azure-Config" "LOCATION" "$LOCATION"

# 2. Create API Keys Variable Group
create_variable_group "API-Keys" "API keys and secrets for external services"

print_info "You need to manually add these secret variables to the 'API-Keys' variable group:"
echo "  - OPENAI_API_KEY (mark as secret)"
echo "  - TOGETHER_API_KEY (mark as secret)"
echo "  - Any other API keys your services need"

# 3. Create Storage Configuration Variable Group
create_variable_group "Storage-Config" "Azure Storage configuration for shared data"

# Try to get storage account details (if infrastructure was already set up)
STORAGE_ACCOUNTS=$(az storage account list --resource-group $RESOURCE_GROUP --query "[?contains(name, 'sarevitalizebrand')].name" -o tsv)

if [ ! -z "$STORAGE_ACCOUNTS" ]; then
    STORAGE_ACCOUNT=$(echo $STORAGE_ACCOUNTS | head -n1)
    STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query "[0].value" -o tsv)
    
    add_variable_to_group "Storage-Config" "STORAGE_ACCOUNT_NAME" "$STORAGE_ACCOUNT"
    add_variable_to_group "Storage-Config" "STORAGE_ACCOUNT_KEY" "$STORAGE_KEY" true
    add_variable_to_group "Storage-Config" "FILE_SHARE_NAME" "shared-data"
else
    print_warning "Storage account not found. Run infrastructure setup first, then manually add:"
    echo "  - STORAGE_ACCOUNT_NAME"
    echo "  - STORAGE_ACCOUNT_KEY (mark as secret)"
    echo "  - FILE_SHARE_NAME"
fi

# 4. Create Container Apps Variable Group
create_variable_group "Container-Apps" "Container Apps specific configuration"

add_variable_to_group "Container-Apps" "BRAND_SERVICE_NAME" "ca-revitalize-brand-service"
add_variable_to_group "Container-Apps" "DATA_COLLECTION_SERVICE_NAME" "ca-revitalize-data-collection"
add_variable_to_group "Container-Apps" "ANALYSIS_ENGINE_SERVICE_NAME" "ca-revitalize-analysis-engine"
add_variable_to_group "Container-Apps" "BRAND_SERVICE_PORT" "8001"
add_variable_to_group "Container-Apps" "DATA_COLLECTION_PORT" "8002"
add_variable_to_group "Container-Apps" "ANALYSIS_ENGINE_PORT" "8003"

echo
print_success "🎉 Variable groups setup completed!"
echo
echo "=== Created Variable Groups ==="
echo "1. Azure-Config - Azure infrastructure settings"
echo "2. API-Keys - External API keys and secrets"
echo "3. Storage-Config - Azure Storage configuration"
echo "4. Container-Apps - Container Apps specific settings"
echo
echo "=== Manual Steps Required ==="
echo "1. Go to Azure DevOps -> Pipelines -> Library"
echo "2. Open 'API-Keys' variable group"
echo "3. Add these secret variables:"
echo "   - OPENAI_API_KEY (your OpenAI API key)"
echo "   - TOGETHER_API_KEY (your Together AI API key)"
echo "4. Mark both as 'Keep this value secret'"
echo
echo "=== Verify Variable Groups ==="
echo "Run: az pipelines variable-group list --organization $ORGANIZATION --project $PROJECT"
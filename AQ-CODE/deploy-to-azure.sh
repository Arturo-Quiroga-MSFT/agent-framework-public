#!/bin/bash

# Deployment script for Streamlit Azure AI Demo to Azure Container Apps
# This script reads secrets from .env file and deploys to Azure

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Azure Container Apps Deployment Script ===${NC}"
echo ""

# ============================================================================
# CONFIGURATION - Customize these values
# ============================================================================

RESOURCE_GROUP="agent-framework-rg"
LOCATION="eastus"
ACR_NAME="aqr2d2agentframeworkacr007"  # Must be globally unique, lowercase, no hyphens
CONTAINERAPPS_ENV="agent-framework-env"
APP_NAME="agent-framework-demo"
IMAGE_NAME="agent-framework-demo"
IMAGE_TAG="$(date +%Y%m%d-%H%M%S)"  # Timestamp tag for versioning

# ============================================================================
# Load secrets from .env file
# ============================================================================

ENV_FILE="../python/samples/getting_started/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: .env file not found at $ENV_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Loading secrets from .env file...${NC}"

# Function to extract value from .env file
get_env_value() {
    local key=$1
    local value=$(grep "^${key}=" "$ENV_FILE" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    echo "$value"
}

# Load required secrets
AZURE_AI_PROJECT_ENDPOINT=$(get_env_value "AZURE_AI_PROJECT_ENDPOINT")
AZURE_AI_MODEL_DEPLOYMENT_NAME=$(get_env_value "AZURE_AI_MODEL_DEPLOYMENT_NAME")
OPENWEATHER_API_KEY=$(get_env_value "OPENWEATHER_API_KEY")
BING_CONNECTION_ID=$(get_env_value "BING_CONNECTION_ID")
FIRECRAWL_API_KEY=$(get_env_value "FIRECRAWL_API_KEY")

# Validate required secrets
if [ -z "$AZURE_AI_PROJECT_ENDPOINT" ] || [ -z "$AZURE_AI_MODEL_DEPLOYMENT_NAME" ]; then
    echo -e "${RED}Error: AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME are required in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Secrets loaded successfully${NC}"
echo ""

# ============================================================================
# Step 1: Create Azure resources
# ============================================================================

echo -e "${YELLOW}Step 1: Creating Azure resources...${NC}"

# Create resource group
echo "Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none || true

# Create Azure Container Registry
echo "Creating Azure Container Registry: $ACR_NAME"
ACR_EXISTS=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP 2>/dev/null || echo "")

if [ -z "$ACR_EXISTS" ]; then
    echo "Creating new ACR..."
    az acr create \
      --resource-group $RESOURCE_GROUP \
      --name $ACR_NAME \
      --sku Basic \
      --admin-enabled true \
      --output none
else
    echo "ACR already exists in this resource group, continuing..."
fi

# Create Container Apps environment
echo "Creating Container Apps environment: $CONTAINERAPPS_ENV"
az containerapp env create \
  --name $CONTAINERAPPS_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --output none 2>/dev/null || echo "Environment already exists, continuing..."

echo -e "${GREEN}✓ Azure resources ready${NC}"
echo ""

# ============================================================================
# Step 2: Build image in Azure Container Registry
# ============================================================================

echo -e "${YELLOW}Step 2: Building Docker image in ACR...${NC}"
echo "This will take a few minutes..."

cd ..
az acr build \
  --registry $ACR_NAME \
  --image ${IMAGE_NAME}:${IMAGE_TAG} \
  --file AQ-CODE/Dockerfile \
  .

echo -e "${GREEN}✓ Image built successfully: ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo ""

# ============================================================================
# Step 3: Deploy to Azure Container Apps
# ============================================================================

echo -e "${YELLOW}Step 3: Deploying to Azure Container Apps...${NC}"

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Check if app already exists
APP_EXISTS=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP 2>/dev/null || echo "")

if [ -z "$APP_EXISTS" ]; then
    echo "Creating new Container App: $APP_NAME"
    
    # Create Container App
    az containerapp create \
      --name $APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --environment $CONTAINERAPPS_ENV \
      --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
      --registry-server ${ACR_NAME}.azurecr.io \
      --registry-username $ACR_USERNAME \
      --registry-password $ACR_PASSWORD \
      --target-port 8501 \
      --ingress external \
      --cpu 1.0 \
      --memory 2.0Gi \
      --min-replicas 1 \
      --max-replicas 3 \
      --secrets \
        azure-ai-endpoint="$AZURE_AI_PROJECT_ENDPOINT" \
        azure-ai-model="$AZURE_AI_MODEL_DEPLOYMENT_NAME" \
        openweather-key="$OPENWEATHER_API_KEY" \
        bing-connection="$BING_CONNECTION_ID" \
        firecrawl-key="$FIRECRAWL_API_KEY" \
      --env-vars \
        AZURE_AI_PROJECT_ENDPOINT=secretref:azure-ai-endpoint \
        AZURE_AI_MODEL_DEPLOYMENT_NAME=secretref:azure-ai-model \
        OPENWEATHER_API_KEY=secretref:openweather-key \
        BING_CONNECTION_ID=secretref:bing-connection \
        FIRECRAWL_API_KEY=secretref:firecrawl-key \
      --output none
else
    echo "Updating existing Container App: $APP_NAME"
    
    # Update secrets
    az containerapp secret set \
      --name $APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --secrets \
        azure-ai-endpoint="$AZURE_AI_PROJECT_ENDPOINT" \
        azure-ai-model="$AZURE_AI_MODEL_DEPLOYMENT_NAME" \
        openweather-key="$OPENWEATHER_API_KEY" \
        bing-connection="$BING_CONNECTION_ID" \
        firecrawl-key="$FIRECRAWL_API_KEY" \
      --output none
    
    # Update image
    az containerapp update \
      --name $APP_NAME \
      --resource-group $RESOURCE_GROUP \
      --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
      --output none
fi

echo -e "${GREEN}✓ Deployment complete${NC}"
echo ""

# ============================================================================
# Step 4: Get app URL
# ============================================================================

echo -e "${YELLOW}Step 4: Retrieving app URL...${NC}"

APP_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Deployment Successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Your Streamlit app is available at:"
echo -e "${GREEN}https://${APP_URL}${NC}"
echo ""
echo "It may take 1-2 minutes for the app to fully start."
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo -e "${YELLOW}To redeploy after code changes:${NC}"
echo "cd AQ-CODE && bash deploy-to-azure.sh"
echo ""

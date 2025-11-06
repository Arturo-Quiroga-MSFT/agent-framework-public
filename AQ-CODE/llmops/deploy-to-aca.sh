#!/bin/bash

# Deploy LLMOps Production Agent to Azure Container Apps
# This script builds and deploys the Streamlit UI to Azure Container Apps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}LLMOps Production Agent - Azure Container Apps Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed${NC}"
    echo "Install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
echo -e "${YELLOW}Checking Azure login status...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}Not logged in to Azure. Logging in...${NC}"
    az login
fi

# Get current subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
echo -e "${GREEN}✓ Logged in to Azure${NC}"
echo -e "  Subscription: ${SUBSCRIPTION}"
echo ""

# Prompt for configuration
read -p "Enter Resource Group name [llmops-rg]: " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-llmops-rg}

read -p "Enter Azure Container Registry name [llmopsacr]: " ACR_NAME
ACR_NAME=${ACR_NAME:-llmopsacr}

read -p "Enter Container App name [llmops-ui]: " APP_NAME
APP_NAME=${APP_NAME:-llmops-ui}

read -p "Enter Azure region [eastus]: " LOCATION
LOCATION=${LOCATION:-eastus}

read -p "Enter Container App Environment name [llmops-env]: " ENVIRONMENT
ENVIRONMENT=${ENVIRONMENT:-llmops-env}

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  ACR Name: $ACR_NAME"
echo "  App Name: $APP_NAME"
echo "  Location: $LOCATION"
echo "  Environment: $ENVIRONMENT"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

# Create resource group
echo -e "${YELLOW}Creating resource group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo -e "${YELLOW}Creating Azure Container Registry...${NC}"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Build and push Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
IMAGE_NAME="${ACR_NAME}.azurecr.io/${APP_NAME}:latest"

az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME \
    --file Dockerfile \
    .

echo -e "${GREEN}✓ Image built and pushed to ACR${NC}"

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Create Container App Environment
echo -e "${YELLOW}Creating Container App Environment...${NC}"
az containerapp env create \
    --name $ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Prompt for Azure AI configuration
echo ""
echo -e "${YELLOW}Azure AI Configuration:${NC}"
read -p "Enter AZURE_AI_PROJECT_CONNECTION_STRING: " AZURE_AI_PROJECT_CONNECTION_STRING
read -p "Enter AZURE_AI_MODEL_DEPLOYMENT_NAME [gpt-4]: " AZURE_AI_MODEL_DEPLOYMENT_NAME
AZURE_AI_MODEL_DEPLOYMENT_NAME=${AZURE_AI_MODEL_DEPLOYMENT_NAME:-gpt-4}

read -p "Enter Application Insights Connection String (optional): " APPLICATIONINSIGHTS_CONNECTION_STRING

# Create Container App
echo -e "${YELLOW}Creating Container App...${NC}"
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image $IMAGE_NAME \
    --registry-server "${ACR_NAME}.azurecr.io" \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8501 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 5 \
    --cpu 1.0 \
    --memory 2.0Gi \
    --env-vars \
        "AZURE_AI_PROJECT_CONNECTION_STRING=$AZURE_AI_PROJECT_CONNECTION_STRING" \
        "AZURE_AI_MODEL_DEPLOYMENT_NAME=$AZURE_AI_MODEL_DEPLOYMENT_NAME" \
        "APPLICATIONINSIGHTS_CONNECTION_STRING=$APPLICATIONINSIGHTS_CONNECTION_STRING" \
        "ENABLE_TRACING=true" \
        "DAILY_TOKEN_BUDGET=1000000" \
        "MAX_TOKENS_PER_REQUEST=4000"

# Get the app URL
APP_URL=$(az containerapp show \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}Your LLMOps Production Agent is now running at:${NC}"
echo -e "${GREEN}https://${APP_URL}${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View logs:    az containerapp logs show -n $APP_NAME -g $RESOURCE_GROUP --follow"
echo "  Scale up:     az containerapp update -n $APP_NAME -g $RESOURCE_GROUP --min-replicas 2 --max-replicas 10"
echo "  Update image: az containerapp update -n $APP_NAME -g $RESOURCE_GROUP --image $IMAGE_NAME"
echo "  Delete app:   az containerapp delete -n $APP_NAME -g $RESOURCE_GROUP"
echo ""

#!/bin/bash
# Pure Azure CLI deployment script for Redis Agents DevUI
# Uses ACR build, ACA environments, revisions, and rollback support

set -e

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-devui-redis}"
LOCATION="${LOCATION:-swedencentral}"
ACR_NAME="${ACR_NAME:-acrdevuidemos}"
ACA_ENV_NAME="${ACA_ENV_NAME:-aca-env-devui}"
APP_NAME="${APP_NAME:-devui-redis-agents}"
REDIS_CACHE_NAME="${REDIS_CACHE_NAME:-redis-devui-cache}"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}"
LOG_ANALYTICS_WORKSPACE="${LOG_ANALYTICS_WORKSPACE:-logs-devui}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Redis Agents DevUI Deployment${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check required environment variables
if [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo -e "${RED}Error: AZURE_OPENAI_ENDPOINT not set${NC}"
    echo "Please set it: export AZURE_OPENAI_ENDPOINT='https://your-openai.openai.azure.com/'"
    exit 1
fi

if [ -z "$AZURE_OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: AZURE_OPENAI_API_KEY not set${NC}"
    echo "Please set it: export AZURE_OPENAI_API_KEY='your-key'"
    exit 1
fi

AZURE_OPENAI_DEPLOYMENT_NAME="${AZURE_OPENAI_DEPLOYMENT_NAME:-gpt-4o-mini}"
AZURE_OPENAI_API_VERSION="${AZURE_OPENAI_API_VERSION:-2024-08-01-preview}"

echo -e "${GREEN}✓ Configuration loaded${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  ACR Name: $ACR_NAME"
echo "  ACA Environment: $ACA_ENV_NAME"
echo "  App Name: $APP_NAME"
echo "  Redis Cache: $REDIS_CACHE_NAME"
echo "  Image Tag: $IMAGE_TAG"
echo ""

# Create resource group
echo -e "${BLUE}Step 1/9: Creating/verifying resource group...${NC}"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none
echo -e "${GREEN}✓ Resource group ready${NC}"

# Create or reuse ACR
echo -e "${BLUE}Step 2/9: Setting up Azure Container Registry...${NC}"
if ! az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating new ACR..."
    az acr create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$ACR_NAME" \
        --sku Standard \
        --admin-enabled true \
        --output none
    echo -e "${GREEN}✓ ACR created${NC}"
else
    echo -e "${GREEN}✓ ACR already exists (reusing)${NC}"
fi

# Get ACR credentials
ACR_SERVER=$(az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query passwords[0].value -o tsv)

echo -e "${GREEN}✓ ACR credentials retrieved${NC}"

# Build and push Docker image using ACR
echo -e "${BLUE}Step 3/9: Building Docker image with ACR...${NC}"

# Get absolute path to repo root and Dockerfile
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DOCKERFILE_PATH="$SCRIPT_DIR/Dockerfile"

echo "Building from repository root: $REPO_ROOT"
echo "Using Dockerfile: $DOCKERFILE_PATH"

az acr build \
    --registry "$ACR_NAME" \
    --image "devui-redis:$IMAGE_TAG" \
    --image "devui-redis:latest" \
    --file "$DOCKERFILE_PATH" \
    "$REPO_ROOT"

echo -e "${GREEN}✓ Image built and pushed: $ACR_SERVER/devui-redis:$IMAGE_TAG${NC}"

# Create or reuse Redis Cache
echo -e "${BLUE}Step 4/9: Setting up Azure Redis Cache...${NC}"
if ! az redis show --name "$REDIS_CACHE_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating new Redis Cache (this takes 10-15 minutes)..."
    az redis create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$REDIS_CACHE_NAME" \
        --location "$LOCATION" \
        --sku Basic \
        --vm-size c0 \
        --enable-non-ssl-port false \
        --minimum-tls-version 1.2 \
        --output none
    echo -e "${GREEN}✓ Redis Cache created${NC}"
else
    echo -e "${GREEN}✓ Redis Cache already exists (reusing)${NC}"
fi

# Get Redis connection details
REDIS_HOST="${REDIS_CACHE_NAME}.redis.cache.windows.net"
REDIS_PASSWORD=$(az redis list-keys --name "$REDIS_CACHE_NAME" --resource-group "$RESOURCE_GROUP" --query primaryKey -o tsv)

echo -e "${GREEN}✓ Redis connection details retrieved${NC}"

# Create or reuse Log Analytics workspace
echo -e "${BLUE}Step 5/9: Setting up Log Analytics workspace...${NC}"
if ! az monitor log-analytics workspace show --workspace-name "$LOG_ANALYTICS_WORKSPACE" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating new Log Analytics workspace..."
    az monitor log-analytics workspace create \
        --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --output none
    echo -e "${GREEN}✓ Log Analytics workspace created${NC}"
else
    echo -e "${GREEN}✓ Log Analytics workspace already exists (reusing)${NC}"
fi

LOG_ANALYTICS_WORKSPACE_ID=$(az monitor log-analytics workspace show \
    --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
    --resource-group "$RESOURCE_GROUP" \
    --query customerId -o tsv)

LOG_ANALYTICS_KEY=$(az monitor log-analytics workspace get-shared-keys \
    --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
    --resource-group "$RESOURCE_GROUP" \
    --query primarySharedKey -o tsv)

# Create or reuse Container Apps environment
echo -e "${BLUE}Step 6/9: Setting up Container Apps environment...${NC}"
if ! az containerapp env show --name "$ACA_ENV_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating new Container Apps environment..."
    az containerapp env create \
        --name "$ACA_ENV_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --logs-workspace-id "$LOG_ANALYTICS_WORKSPACE_ID" \
        --logs-workspace-key "$LOG_ANALYTICS_KEY" \
        --output none
    echo -e "${GREEN}✓ Container Apps environment created${NC}"
else
    echo -e "${GREEN}✓ Container Apps environment already exists (reusing)${NC}"
fi

# Create managed identity or reuse existing
echo -e "${BLUE}Step 7/9: Setting up managed identity...${NC}"
IDENTITY_NAME="${APP_NAME}-identity"
if ! az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating new managed identity..."
    az identity create \
        --name "$IDENTITY_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --output none
    echo -e "${GREEN}✓ Managed identity created${NC}"
else
    echo -e "${GREEN}✓ Managed identity already exists (reusing)${NC}"
fi

IDENTITY_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query id -o tsv)
IDENTITY_CLIENT_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query clientId -o tsv)
IDENTITY_PRINCIPAL_ID=$(az identity show --name "$IDENTITY_NAME" --resource-group "$RESOURCE_GROUP" --query principalId -o tsv)

echo -e "${GREEN}✓ Identity IDs retrieved${NC}"

# Check if Container App exists
echo -e "${BLUE}Step 8/9: Deploying Container App...${NC}"
FULL_IMAGE_NAME="$ACR_SERVER/devui-redis:$IMAGE_TAG"

if ! az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating new Container App..."
    
    # Create new app
    az containerapp create \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --environment "$ACA_ENV_NAME" \
        --image "$FULL_IMAGE_NAME" \
        --target-port 8200 \
        --ingress external \
        --registry-server "$ACR_SERVER" \
        --registry-username "$ACR_USERNAME" \
        --registry-password "$ACR_PASSWORD" \
        --cpu 1.0 \
        --memory 2.0Gi \
        --min-replicas 1 \
        --max-replicas 3 \
        --user-assigned "$IDENTITY_ID" \
        --secrets \
            azure-openai-endpoint="$AZURE_OPENAI_ENDPOINT" \
            azure-openai-api-key="$AZURE_OPENAI_API_KEY" \
            redis-password="$REDIS_PASSWORD" \
            app-insights-connection-string="${APPLICATIONINSIGHTS_CONNECTION_STRING:-}" \
        --env-vars \
            AZURE_OPENAI_ENDPOINT=secretref:azure-openai-endpoint \
            AZURE_OPENAI_API_KEY=secretref:azure-openai-api-key \
            AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
            AZURE_OPENAI_API_VERSION="$AZURE_OPENAI_API_VERSION" \
            REDIS_HOST="$REDIS_HOST" \
            REDIS_PORT=6380 \
            REDIS_PASSWORD=secretref:redis-password \
            REDIS_SSL=true \
            APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:app-insights-connection-string \
            ENABLE_DEVUI_TRACING=true \
            ENABLE_OTEL=true \
            ENABLE_SENSITIVE_DATA=false \
            AZURE_CLIENT_ID="$IDENTITY_CLIENT_ID" \
        --output none
    
    echo -e "${GREEN}✓ Container App created${NC}"
else
    echo "Container App exists, creating new revision..."
    
    # Get current revision name for potential rollback
    CURRENT_REVISION=$(az containerapp revision list \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?properties.active].name | [0]" -o tsv)
    
    echo -e "${YELLOW}Current active revision: $CURRENT_REVISION${NC}"
    
    # Update with new image (creates new revision)
    az containerapp update \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --image "$FULL_IMAGE_NAME" \
        --set-env-vars \
            AZURE_OPENAI_ENDPOINT=secretref:azure-openai-endpoint \
            AZURE_OPENAI_API_KEY=secretref:azure-openai-api-key \
            AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
            AZURE_OPENAI_API_VERSION="$AZURE_OPENAI_API_VERSION" \
            REDIS_HOST="$REDIS_HOST" \
            REDIS_PORT=6380 \
            REDIS_PASSWORD=secretref:redis-password \
            REDIS_SSL=true \
            APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:app-insights-connection-string \
            ENABLE_DEVUI_TRACING=true \
            ENABLE_OTEL=true \
            ENABLE_SENSITIVE_DATA=false \
            AZURE_CLIENT_ID="$IDENTITY_CLIENT_ID" \
        --output none
    
    # Get new revision name
    NEW_REVISION=$(az containerapp revision list \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?properties.active].name | [0]" -o tsv)
    
    echo -e "${GREEN}✓ New revision created: $NEW_REVISION${NC}"
    echo -e "${YELLOW}Previous revision: $CURRENT_REVISION (kept for rollback)${NC}"
fi

# Get app FQDN
echo -e "${BLUE}Step 9/9: Verifying deployment...${NC}"
FQDN=$(az containerapp show \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.configuration.ingress.fqdn -o tsv)

# Wait a bit for app to be ready
echo "Waiting for app to become ready..."
sleep 10

# Test the endpoint
echo "Testing endpoint..."
if curl -s -o /dev/null -w "%{http_code}" "https://$FQDN" | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✓ Endpoint is responding${NC}"
else
    echo -e "${YELLOW}⚠ Endpoint may still be starting up${NC}"
fi

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${BLUE}DevUI URL:${NC} https://$FQDN"
echo -e "${BLUE}App Name:${NC} $APP_NAME"
echo -e "${BLUE}Resource Group:${NC} $RESOURCE_GROUP"
echo -e "${BLUE}Image:${NC} $FULL_IMAGE_NAME"
echo -e "${BLUE}Redis Cache:${NC} $REDIS_HOST"
echo -e "${BLUE}Identity Principal ID:${NC} $IDENTITY_PRINCIPAL_ID"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. View logs:"
echo "   ${BLUE}az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow${NC}"
echo ""
echo "2. List revisions:"
echo "   ${BLUE}az containerapp revision list --name $APP_NAME --resource-group $RESOURCE_GROUP -o table${NC}"
echo ""
echo "3. Rollback if needed:"
echo "   ${BLUE}az containerapp revision activate --revision <previous-revision-name> --resource-group $RESOURCE_GROUP${NC}"
echo ""
echo "4. (Optional) Use managed identity for Azure OpenAI instead of API key:"
echo "   ${BLUE}az role assignment create \\${NC}"
echo "     ${BLUE}--role 'Cognitive Services User' \\${NC}"
echo "     ${BLUE}--assignee-object-id $IDENTITY_PRINCIPAL_ID \\${NC}"
echo "     ${BLUE}--scope /subscriptions/{subscription-id}/resourceGroups/{openai-rg}/providers/Microsoft.CognitiveServices/accounts/{openai-account}${NC}"
echo ""
echo -e "${GREEN}✓ Access DevUI at: https://$FQDN${NC}"

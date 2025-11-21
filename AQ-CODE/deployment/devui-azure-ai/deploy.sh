#!/bin/bash
# Pure Azure CLI deployment script for Azure AI Agents DevUI
# Uses ACR build, ACA environments, revisions, and rollback support

set -e

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-devui-azure-ai}"
LOCATION="${LOCATION:-swedencentral}"
ACR_NAME="${ACR_NAME:-acrdevuidemos}"
ACA_ENV_NAME="${ACA_ENV_NAME:-aca-env-devui}"
APP_NAME="${APP_NAME:-devui-azure-ai-agents}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
SKIP_BUILD="${SKIP_BUILD:-false}"
LOG_ANALYTICS_WORKSPACE="${LOG_ANALYTICS_WORKSPACE:-logs-devui}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Azure AI Agents DevUI Deployment${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check required environment variables
if [ -z "$AZURE_AI_PROJECT_ENDPOINT" ]; then
    echo -e "${RED}Error: AZURE_AI_PROJECT_ENDPOINT not set${NC}"
    echo "Please set it: export AZURE_AI_PROJECT_ENDPOINT='https://your-project.services.ai.azure.com/api/projects/yourProject'"
    exit 1
fi

AZURE_AI_MODEL_DEPLOYMENT_NAME="${AZURE_AI_MODEL_DEPLOYMENT_NAME:-gpt-4o-mini}"

echo -e "${GREEN}✓ Configuration loaded${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  ACR Name: $ACR_NAME"
echo "  ACA Environment: $ACA_ENV_NAME"
echo "  App Name: $APP_NAME"
echo "  Image Tag: $IMAGE_TAG"
echo ""

# Create resource group
echo -e "${BLUE}Step 1/8: Creating/verifying resource group...${NC}"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none
echo -e "${GREEN}✓ Resource group ready${NC}"

# Create or reuse ACR
echo -e "${BLUE}Step 2/8: Setting up Azure Container Registry...${NC}"
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
echo -e "${BLUE}Step 3/8: Building Docker image with ACR...${NC}"

if [ "$SKIP_BUILD" = "true" ]; then
    echo -e "${YELLOW}⊘ Skipping build (SKIP_BUILD=true), using existing image: $IMAGE_TAG${NC}"
else
    # Get absolute path to repo root and Dockerfile
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
    DOCKERFILE_PATH="$SCRIPT_DIR/Dockerfile"

    echo "Building from repository root: $REPO_ROOT"
    echo "Using Dockerfile: $DOCKERFILE_PATH"

    az acr build \
        --registry "$ACR_NAME" \
        --image "devui-azure-ai:$IMAGE_TAG" \
        --image "devui-azure-ai:latest" \
        --file "$DOCKERFILE_PATH" \
        "$REPO_ROOT"

    echo -e "${GREEN}✓ Image built and pushed: $ACR_SERVER/devui-azure-ai:$IMAGE_TAG${NC}"
fi

# Create or reuse Log Analytics workspace
echo -e "${BLUE}Step 4/8: Setting up Log Analytics workspace...${NC}"
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
echo -e "${BLUE}Step 5/8: Setting up Container Apps environment...${NC}"
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
echo -e "${BLUE}Step 6/8: Setting up managed identity...${NC}"
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
echo -e "${BLUE}Step 7/8: Deploying Container App...${NC}"
FULL_IMAGE_NAME="$ACR_SERVER/devui-azure-ai:$IMAGE_TAG"

if ! az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating new Container App..."
    
    # Create new app
    az containerapp create \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --environment "$ACA_ENV_NAME" \
        --image "$FULL_IMAGE_NAME" \
        --target-port 8100 \
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
            azure-ai-endpoint="$AZURE_AI_PROJECT_ENDPOINT" \
            openweather-api-key="$OPENWEATHER_API_KEY" \
            bing-connection-id="$BING_CONNECTION_ID" \
            file-search-vector-store-id="$FILE_SEARCH_VECTOR_STORE_ID" \
        --env-vars \
            AZURE_AI_PROJECT_ENDPOINT=secretref:azure-ai-endpoint \
            AZURE_AI_MODEL_DEPLOYMENT_NAME="$AZURE_AI_MODEL_DEPLOYMENT_NAME" \
            OPENWEATHER_API_KEY=secretref:openweather-api-key \
            BING_CONNECTION_ID=secretref:bing-connection-id \
            FILE_SEARCH_VECTOR_STORE_ID=secretref:file-search-vector-store-id \
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
            AZURE_AI_PROJECT_ENDPOINT=secretref:azure-ai-endpoint \
            AZURE_AI_MODEL_DEPLOYMENT_NAME="$AZURE_AI_MODEL_DEPLOYMENT_NAME" \
            OPENWEATHER_API_KEY=secretref:openweather-api-key \
            BING_CONNECTION_ID=secretref:bing-connection-id \
            FILE_SEARCH_VECTOR_STORE_ID=secretref:file-search-vector-store-id \
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
echo -e "${BLUE}Step 8/8: Verifying deployment...${NC}"
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
echo -e "${BLUE}Identity Principal ID:${NC} $IDENTITY_PRINCIPAL_ID"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Grant the managed identity access to Azure AI services:"
echo "   ${BLUE}az role assignment create \\${NC}"
echo "     ${BLUE}--role 'Cognitive Services User' \\${NC}"
echo "     ${BLUE}--assignee-object-id $IDENTITY_PRINCIPAL_ID \\${NC}"
echo "     ${BLUE}--scope /subscriptions/{subscription-id}/resourceGroups/{ai-rg}/providers/Microsoft.CognitiveServices/accounts/{ai-account}${NC}"
echo ""
echo "2. View logs:"
echo "   ${BLUE}az containerapp logs show --name $APP_NAME --resource-group $RESOURCE_GROUP --follow${NC}"
echo ""
echo "3. List revisions:"
echo "   ${BLUE}az containerapp revision list --name $APP_NAME --resource-group $RESOURCE_GROUP -o table${NC}"
echo ""
echo "4. Rollback if needed:"
echo "   ${BLUE}az containerapp revision activate --revision <previous-revision-name> --resource-group $RESOURCE_GROUP${NC}"
echo ""
echo -e "${GREEN}✓ Access DevUI at: https://$FQDN${NC}"

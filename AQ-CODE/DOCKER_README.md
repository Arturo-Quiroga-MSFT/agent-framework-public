# Streamlit Azure AI Demo - Docker & Azure Container Apps Deployment

This guide shows how to build the Docker image in Azure Container Registry (ACR) and deploy to Azure Container Apps using secrets for configuration.

## Prerequisites

- Azure CLI installed and logged in: `az login`
- An Azure subscription
- (Optional) An existing Container Apps environment or we'll create one

## Step-by-Step Deployment

### 1. Set your variables

```bash
# Configuration
RESOURCE_GROUP="agent-framework-rg"
LOCATION="eastus"
ACR_NAME="agentframeworkacr"  # Must be globally unique, lowercase, no hyphens
CONTAINERAPPS_ENV="agent-framework-env"
APP_NAME="agent-framework-demo"
IMAGE_NAME="agent-framework-demo"
IMAGE_TAG="latest"
```

### 2. Create resources (if they don't exist)

```bash
# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Create Container Apps environment
az containerapp env create \
  --name $CONTAINERAPPS_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### 3. Build image in Azure Container Registry (no local Docker needed!)

```bash
# Navigate to repo root
cd /path/to/agent-framework-public

# Build image directly in ACR using ACR Tasks
az acr build \
  --registry $ACR_NAME \
  --image ${IMAGE_NAME}:${IMAGE_TAG} \
  --file AQ-CODE/Dockerfile \
  .

# This uploads the build context and builds in the cloud
# The image will be available at: ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}
```

### 4. Deploy to Azure Container Apps with secrets

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Create Container App with secrets
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
    azure-ai-endpoint="<YOUR_AZURE_AI_PROJECT_ENDPOINT>" \
    azure-ai-model="<YOUR_MODEL_DEPLOYMENT_NAME>" \
    openweather-key="<YOUR_OPENWEATHER_API_KEY>" \
    bing-connection="<YOUR_BING_CONNECTION_ID>" \
    firecrawl-key="<YOUR_FIRECRAWL_API_KEY>" \
  --env-vars \
    AZURE_AI_PROJECT_ENDPOINT=secretref:azure-ai-endpoint \
    AZURE_AI_MODEL_DEPLOYMENT_NAME=secretref:azure-ai-model \
    OPENWEATHER_API_KEY=secretref:openweather-key \
    BING_CONNECTION_ID=secretref:bing-connection \
    FIRECRAWL_API_KEY=secretref:firecrawl-key

# Get the app URL
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  -o tsv
```

### 5. Update secrets (after initial deployment)

```bash
# Update a secret value
az containerapp secret set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --secrets azure-ai-endpoint="<NEW_VALUE>"

# Restart to pick up changes
az containerapp revision restart \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### 6. Rebuild and redeploy (for code updates)

```bash
# Rebuild in ACR
az acr build \
  --registry $ACR_NAME \
  --image ${IMAGE_NAME}:${IMAGE_TAG} \
  --file AQ-CODE/Dockerfile \
  .

# Update Container App to use new image
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}
```

## Security Best Practices

- ✅ **No `.env` in image**: Secrets are provided via Container Apps secrets
- ✅ **Non-root user**: Dockerfile runs as user `appuser` (UID 1000)
- ✅ **Minimal image**: Multi-stage build keeps runtime image small
- ✅ **ACR integration**: Private registry with managed credentials
- 🔒 **Consider**: Use Azure Key Vault references for production secrets

## Monitoring & Troubleshooting

```bash
# View logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 100 \
  --follow

# Check app status
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.runningStatus

# Scale manually
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 5
```

## Cost Optimization

- Set `--min-replicas 0` to scale to zero when not in use
- Use smaller CPU/memory if sufficient: `--cpu 0.5 --memory 1.0Gi`
- Delete resources when done: `az group delete --name $RESOURCE_GROUP`

## Common Issues

**Missing packages**: Update `AQ-CODE/requirements.txt` and rebuild in ACR

**Auth errors**: Ensure Azure CLI is logged in and Container App has ACR credentials

**Secrets not loading**: Verify secret names match env var references (`secretref:secret-name`)

**App not accessible**: Check ingress is set to `external` and firewall rules allow traffic


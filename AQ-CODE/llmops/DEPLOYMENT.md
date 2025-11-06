# Deploying LLMOps Production Agent to Azure Container Apps

This guide walks you through deploying the LLMOps Production Agent Streamlit UI to Azure Container Apps (ACA).

## Prerequisites

- Azure CLI installed ([Install Guide](https://docs.microsoft.com/cli/azure/install-azure-cli))
- Docker installed (for local testing)
- Azure subscription with appropriate permissions
- Azure AI Foundry project with a deployed model

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
cd AQ-CODE/llmops
chmod +x deploy-to-aca.sh
./deploy-to-aca.sh
```

The script will:
1. ✅ Check Azure CLI login
2. ✅ Create resource group
3. ✅ Create Azure Container Registry (ACR)
4. ✅ Build and push Docker image
5. ✅ Create Container App Environment
6. ✅ Deploy Container App with environment variables
7. ✅ Return public URL

### Option 2: Manual Deployment

#### 1. Build Docker Image Locally

```bash
cd AQ-CODE/llmops
docker build -t llmops-ui:latest .
```

Test locally:
```bash
docker run -p 8501:8501 \
  -e AZURE_AI_PROJECT_CONNECTION_STRING="your-connection-string" \
  -e AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4" \
  llmops-ui:latest
```

Visit: http://localhost:8501

#### 2. Push to Azure Container Registry

```bash
# Variables
RESOURCE_GROUP="llmops-rg"
ACR_NAME="llmopsacr"
LOCATION="eastus"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Build and push
az acr build \
  --registry $ACR_NAME \
  --image llmops-ui:latest \
  --file Dockerfile \
  .
```

#### 3. Deploy to Container Apps

```bash
# Variables
APP_NAME="llmops-ui"
ENVIRONMENT="llmops-env"

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Create Container App Environment
az containerapp env create \
  --name $ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Create Container App
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image "${ACR_NAME}.azurecr.io/llmops-ui:latest" \
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
    "AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string" \
    "AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4" \
    "APPLICATIONINSIGHTS_CONNECTION_STRING=your-app-insights-connection" \
    "ENABLE_TRACING=true" \
    "DAILY_TOKEN_BUDGET=1000000" \
    "MAX_TOKENS_PER_REQUEST=4000"
```

#### 4. Get Application URL

```bash
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv
```

## Environment Variables

Required:
- `AZURE_AI_PROJECT_CONNECTION_STRING` - Your Azure AI Foundry project connection string
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` - Name of deployed model (e.g., "gpt-4")

Optional:
- `APPLICATIONINSIGHTS_CONNECTION_STRING` - For observability and monitoring
- `ENABLE_TRACING` - Enable OpenTelemetry tracing (default: true)
- `DAILY_TOKEN_BUDGET` - Daily token limit (default: 1000000)
- `MAX_TOKENS_PER_REQUEST` - Per-request token limit (default: 4000)

## Configuration

### Scaling

```bash
# Update scaling settings
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 10
```

### Update Environment Variables

```bash
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "DAILY_TOKEN_BUDGET=2000000"
```

### Update Image

```bash
# Rebuild and push new image
az acr build \
  --registry $ACR_NAME \
  --image llmops-ui:latest \
  --file Dockerfile \
  .

# Update container app
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image "${ACR_NAME}.azurecr.io/llmops-ui:latest"
```

## Monitoring

### View Logs

```bash
# Real-time logs
az containerapp logs show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Tail logs
az containerapp logs tail \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### View Metrics

```bash
# CPU and memory usage
az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration
```

### Application Insights

If you configured `APPLICATIONINSIGHTS_CONNECTION_STRING`, you can:
- View traces in Azure Portal → Application Insights
- Query custom metrics (agent calls, costs, quality scores)
- Set up alerts for errors or budget thresholds

## Security Best Practices

1. **Use Managed Identity** (recommended):
   ```bash
   # Enable managed identity
   az containerapp identity assign \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP
   
   # Remove explicit credentials from env vars
   # App will use managed identity automatically
   ```

2. **Store secrets in Key Vault**:
   ```bash
   # Reference Key Vault secrets
   az containerapp update \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --secrets "connection-string=keyvaultref:https://myvault.vault.azure.net/secrets/connection-string"
   ```

3. **Enable Authentication** (optional):
   ```bash
   az containerapp auth update \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --enable-authentication true \
     --action RedirectToLoginPage
   ```

## Troubleshooting

### Container won't start

```bash
# Check container logs
az containerapp logs show -n $APP_NAME -g $RESOURCE_GROUP --tail 100

# Check revision status
az containerapp revision list -n $APP_NAME -g $RESOURCE_GROUP -o table
```

### Port issues

Ensure Streamlit is configured correctly:
- Container exposes port 8501
- Ingress target port is 8501
- Dockerfile CMD uses `--server.port=8501 --server.address=0.0.0.0`

### Authentication errors

Verify environment variables:
```bash
az containerapp show -n $APP_NAME -g $RESOURCE_GROUP --query properties.configuration.secrets
```

## Cost Optimization

1. **Use spot instances** for dev/test:
   ```bash
   az containerapp update \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --workload-profile-name "Consumption"
   ```

2. **Set idle timeouts**:
   ```bash
   az containerapp update \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --scale-rule-name "http-rule" \
     --scale-rule-http-concurrency 10
   ```

3. **Monitor with budgets**:
   - Set up Azure Cost Management alerts
   - Use the built-in token budget manager
   - Monitor Application Insights for usage patterns

## Cleanup

```bash
# Delete entire resource group (⚠️ deletes everything)
az group delete --name $RESOURCE_GROUP --yes

# Or delete individual resources
az containerapp delete -n $APP_NAME -g $RESOURCE_GROUP --yes
az acr delete -n $ACR_NAME -g $RESOURCE_GROUP --yes
```

## Next Steps

- Configure custom domain: [ACA Custom Domains](https://learn.microsoft.com/azure/container-apps/custom-domains-certificates)
- Set up CI/CD: [GitHub Actions for ACA](https://learn.microsoft.com/azure/container-apps/github-actions)
- Enable HTTPS: Automatic with ACA ingress
- Add authentication: [Easy Auth](https://learn.microsoft.com/azure/container-apps/authentication)

## Support

- Azure Container Apps docs: https://learn.microsoft.com/azure/container-apps/
- File issues: [GitHub Repository](https://github.com/Arturo-Quiroga-MSFT/agent-framework-public)

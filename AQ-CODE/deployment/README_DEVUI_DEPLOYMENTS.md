# DevUI Demos - Azure Container Apps Deployment

This directory contains deployment configurations for both DevUI agent galleries.

## 📦 What Gets Deployed

### 1. Azure AI Agents DevUI (`devui-azure-ai/`)
**8 Azure AI Agent Demos**
- Weather Agent (Basic) - Real weather via OpenWeatherMap
- Weather Agent (Functions) - Multi-tool coordination
- Bing Grounding Agent - Web search
- Code Interpreter Agent - Python execution
- Code Interpreter with Images - Plot extraction
- File Search Agent - Document RAG
- Azure AI Search Agent - Enterprise search
- OpenAPI Tools Agent - REST API integration

**URL Pattern**: `https://devui-azure-ai-agents.{region}.azurecontainerapps.io`

### 2. Redis Agents DevUI (`devui-redis/`)
**4 Redis-Backed Agent Demos**
- Preference Assistant - Personalized recommendations
- Support Bot - Customer support with memory
- Personal Assistant - Task management
- Work Assistant - Professional productivity

**URL Pattern**: `https://devui-redis-agents.{region}.azurecontainerapps.io`

## 🚀 Quick Deployment

### Deploy Azure AI Agents DevUI

```bash
# Set required environment variables
export AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/yourProject"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"

# Optional: for enhanced features
export OPENWEATHER_API_KEY="your-key"
export BING_CONNECTION_ID="/subscriptions/.../connections/bing"
export FILE_SEARCH_VECTOR_STORE_ID="vs_xxx"
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."

# Deploy
cd devui-azure-ai
chmod +x deploy.sh
./deploy.sh
```

### Deploy Redis Agents DevUI

```bash
# Set required environment variables
export AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"

# Optional
export REDIS_CACHE_NAME="redis-devui-cache"  # Will be created if doesn't exist
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."

# Deploy
cd devui-redis
chmod +x deploy.sh
./deploy.sh
```

## 📋 Prerequisites

- Azure CLI installed and authenticated (`az login`)
- `jq` command-line JSON processor
- Docker (for local testing)
- Appropriate Azure permissions:
  - Create resource groups
  - Create/manage Container Apps
  - Create/manage Container Registry
  - Create/manage Redis Cache
  - Create managed identities

## 🏗️ Architecture

Both deployments use:
- **Azure Container Apps** - Serverless container hosting
- **Azure Container Registry** - Private image registry
- **Managed Identity** - Secure authentication
- **Log Analytics** - Monitoring and diagnostics
- **Auto-scaling** - 1-3 replicas based on HTTP load

### Azure AI Deployment
```
┌─────────────────────────────────────┐
│   Azure Container Apps (DevUI)      │
│   ├─ 8 Azure AI Agents              │
│   ├─ Managed Identity                │
│   └─ Port: 8100                      │
└──────────────┬──────────────────────┘
               │
               ├─► Azure AI Foundry Project
               ├─► Azure OpenAI Service
               ├─► Azure AI Search (optional)
               ├─► Bing Grounding (optional)
               └─► Application Insights (optional)
```

### Redis Deployment
```
┌─────────────────────────────────────┐
│   Azure Container Apps (DevUI)      │
│   ├─ 4 Redis Agents                 │
│   ├─ Managed Identity                │
│   └─ Port: 8200                      │
└──────────────┬──────────────────────┘
               │
               ├─► Azure OpenAI Service
               ├─► Azure Redis Cache
               └─► Application Insights (optional)
```

## 🔧 Configuration

### Azure AI Agents Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_AI_PROJECT_ENDPOINT` | ✅ | Azure AI Foundry project endpoint |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | ✅ | Model deployment name (e.g., gpt-4o-mini) |
| `OPENWEATHER_API_KEY` | ❌ | For real weather data in weather agents |
| `BING_CONNECTION_ID` | ❌ | For web search in bing grounding agent |
| `FILE_SEARCH_VECTOR_STORE_ID` | ❌ | For document search in file search agent |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | ❌ | For detailed telemetry |
| `ENABLE_DEVUI_TRACING` | Auto | Set to `true` (automatic) |
| `ENABLE_OTEL` | Auto | Set to `true` (automatic) |

### Redis Agents Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | ✅ | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | ✅ | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | ✅ | Model deployment name |
| `REDIS_HOST` | Auto | Set automatically to Azure Redis |
| `REDIS_PORT` | Auto | Set to 6380 (SSL) |
| `REDIS_PASSWORD` | Auto | Retrieved from Redis Cache |
| `REDIS_SSL` | Auto | Set to `true` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | ❌ | For detailed telemetry |

## 🎯 Post-Deployment Steps

### For Azure AI Agents
Grant the managed identity access to Azure AI services:

```bash
# Get the identity principal ID from deployment output
IDENTITY_PRINCIPAL_ID="<from-deployment-output>"

# Grant access to Azure AI Foundry
az role assignment create \
  --role "Cognitive Services User" \
  --assignee-object-id "$IDENTITY_PRINCIPAL_ID" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/{ai-rg}/providers/Microsoft.CognitiveServices/accounts/{ai-account}"
```

### For Redis Agents
The Redis password is automatically retrieved during deployment. No additional steps needed.

## 🧪 Local Testing

Before deploying, test the Docker images locally:

### Test Azure AI Agents DevUI
```bash
cd devui-azure-ai

# Build
docker build -t devui-azure-ai:test -f Dockerfile ../../..

# Run
docker run -p 8100:8100 \
  -e AZURE_AI_PROJECT_ENDPOINT="$AZURE_AI_PROJECT_ENDPOINT" \
  -e AZURE_AI_MODEL_DEPLOYMENT_NAME="$AZURE_AI_MODEL_DEPLOYMENT_NAME" \
  devui-azure-ai:test

# Access at http://localhost:8100
```

### Test Redis Agents DevUI
```bash
cd devui-redis

# Build
docker build -t devui-redis:test -f Dockerfile ../../..

# Run (requires Redis running)
docker run -p 8200:8200 \
  -e AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
  -e AZURE_OPENAI_API_KEY="$AZURE_OPENAI_API_KEY" \
  -e AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
  -e REDIS_HOST="your-redis-host" \
  -e REDIS_PASSWORD="your-redis-password" \
  devui-redis:test

# Access at http://localhost:8200
```

## 📊 Monitoring

Both deployments include:
- **Log Analytics** - Query logs with KQL
- **Container Apps metrics** - CPU, memory, requests
- **Application Insights** (optional) - Detailed telemetry

View logs:
```bash
# Azure AI Agents
az containerapp logs show \
  --name devui-azure-ai-agents \
  --resource-group rg-devui-azure-ai \
  --follow

# Redis Agents
az containerapp logs show \
  --name devui-redis-agents \
  --resource-group rg-devui-redis \
  --follow
```

## 🔄 Updates

Redeploy with new code:

```bash
# Set a new image tag
export IMAGE_TAG=$(date +%Y%m%d-%H%M%S)

# Run deployment script again
cd devui-azure-ai  # or devui-redis
./deploy.sh
```

## 💰 Cost Optimization

- **Scale to zero**: Set `minReplicas: 0` in Bicep for non-production
- **Redis SKU**: Use Basic C0 for development (already configured)
- **Container resources**: Adjust CPU/memory in Bicep based on usage
- **Log retention**: Default is 30 days, adjust if needed

## 🗑️ Cleanup

Remove all resources:

```bash
# Azure AI Agents
az group delete --name rg-devui-azure-ai --yes --no-wait

# Redis Agents
az group delete --name rg-devui-redis --yes --no-wait
```

## 🐛 Troubleshooting

### Container fails to start
```bash
# Check logs
az containerapp logs show --name <app-name> --resource-group <rg-name> --follow

# Check revision status
az containerapp revision list --name <app-name> --resource-group <rg-name>
```

### Authentication issues
- Verify managed identity has proper role assignments
- Check environment variables are set correctly
- Ensure Azure AI/OpenAI endpoints are accessible

### Redis connection issues
- Verify Redis Cache is running
- Check firewall rules allow Container Apps
- Verify SSL is enabled (port 6380)

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [Azure Redis Cache Documentation](https://learn.microsoft.com/azure/azure-cache-for-redis/)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [DevUI Documentation](../../README.md)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Container Apps logs
3. Check Azure service health status
4. Open an issue in the repository

# Streamlit Azure AI Demo - Docker & Azure Container Apps Deployment

This guide covers containerization and production deployment of the Agent Framework Streamlit demo to Azure Container Apps with enterprise-grade security and features.

## 🆕 Latest Enhancements (October 2025)

### **Automated Deployment Script**
- ✅ **One-command deployment**: `bash deploy-to-azure.sh`
- ✅ **Timestamp-based image tags**: Automatic versioning (e.g., `20251026-211128`)
- ✅ **Azure Container Registry builds**: No local Docker needed
- ✅ **Zero-downtime updates**: Container Apps handles rolling updates
- ✅ **2-minute deployment**: From code change to live in ~120 seconds

### **Managed Identity Authentication**
- 🔐 **No API keys in code**: Uses DefaultAzureCredential
- 🔐 **Automatic credential rotation**: Azure AD managed
- 🔐 **Role-based access**: "Cognitive Services User" assigned to MI
- 🔐 **Compliant with enterprise security**: No secrets in environment

### **Conversation Memory (Thread Persistence)**
- 💬 **4 scenarios with memory**: Thread Management, Azure AI Search, Bing Grounding, File Search
- 💬 **Session-based persistence**: Memory lasts until explicitly cleared
- 💬 **Clear memory buttons**: User control over conversation context
- 💬 **Thread reuse**: Efficient context management across messages

### **Plot Download Button**
- 📥 **Instant downloads**: No external storage needed
- 📥 **Works in ACA**: Compatible with non-root user permissions
- 📥 **PNG format**: Browser-native download buttons
- 📥 **Auto-detection**: Finds latest generated plot automatically

---

## Prerequisites

- Azure CLI installed and logged in: `az login`
- An Azure subscription
- (Optional) An existing Container Apps environment or we'll create one

## 🚀 Quick Manual Deployment (Start (Recommended)

Use the automated deployment script for the easiest deployment:

```bash
cd AQ-CODE
bash deploy-to-azure.sh
```

This script will:
1. Build the Docker image in Azure Container Registry (ACR) with timestamp tag
2. Push the image to ACR
3. Update or create the Azure Container App
4. Enable Managed Identity and assign necessary roles
5. Provide the HTTPS URL of your deployed app

**Deployment time: ~2 minutes**

**Live demo:** https://agent-framework-demo.livelyforest-d40d7875.eastus.azurecontep)

> **Note:** The automated script (`deploy-to-azure.sh`) handles all these stainerapps.io

---

## Manuals automatically.
> Use manual deployment only if you need custom cont (Step-by-Sfiguratep)ion.

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

### 4. Deploy to Azure Container Apps with Managed Identity (Recommended)

**Option A: With Managed Identity (No secrets needed!)**

```bash
# Get ACR credentials for registry auth only
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Create Container App with Managed Identity
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
  --system-assigned

# Assign "Cognitive Services User" role to the Managed Identity
MI_PRINCIPAL_ID=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query identity.principalId -o tsv)

SUBSCRIPTION_ID=$(az account show --query id -o tsv)

az role assignment create \
  --assignee $MI_PRINCIPAL_ID \
  --role "Cognitive Services User" \
  --scope /subscriptions/$SUBSCRIPTION_ID

echo "Managed Identity configured! No API keys needed in environment."
```

**Option B: With Secrets (Legacy approach)**

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

**Using the automated script (recommended):**
```bash
cd AQ-CODE
bash deploy-to-azure.sh
# Automatically creates new timestamp tag and deploys
```

**Manual approach:**
```bash
# Generate timestamp tag
IMAGE_TAG=$(date +%Y%m%d-%H%M%S)

# Rebuild in ACR with new tag
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

- ✅ **Managed Identity authentication**: No API keys in code or environment (recommended)
- ✅ **DefaultAzureCredential**: Automatic authentication with Azure services
- ✅ **Role-based access control**: Least-privilege "Cognitive Services User" role
- ✅ **No `.env` in image**: Secrets provided via Container Apps secrets or MI
- ✅ **Non-root user**: Dockerfile runs as user `appuser` (UID 1000)
- ✅ **Minimal image**: Multi-stage build keeps runtime image small (~1.5GB)
- ✅ **ACR integration**: Private registry with managed credentials
- ✅ **HTTPS only**: Automatic SSL/TLS termination via Container Apps
- ✅ **Timestamp tags**: Immutable image versions for rollback capability
- 🔒 **Consider**: Use Azure Key Vault references for non-Azure secrets (weather API, etc.)

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

**Auth errors**: 
- **With Managed Identity**: Ensure MI has "Cognitive Services User" role
- **With secrets**: Verify Azure CLI is logged in and Container App has ACR credentials

**Secrets not loading**: Verify secret names match env var references (`secretref:secret-name`)

**App not accessible**: Check ingress is set to `external` and firewall rules allow traffic

**Memory errors**: 
- Increase memory: `--memory 2.0Gi` or higher
- Check if large files (ai_research.pdf) cause OOM during vector store creation

---

## 🆕 New Features Documentation

### Conversation Memory (Thread Persistence)

Implemented in 4 scenarios: Thread Management, Azure AI Search, Bing Grounding, File Search

**Technical Implementation:**
- Session state tracks `{scenario}_thread_id` for each memory-enabled scenario
- On first message: `thread = agent.get_new_thread()` creates new thread
- Subsequent messages: `thread = agent.get_new_thread(service_thread_id=stored_id)` reuses thread
- All runs use: `await agent.run(query, thread=thread, store=True)`
- Thread IDs stored in `st.session_state` for persistence
- Clear buttons reset thread_id to `None`, starting fresh conversations

**Files modified:**
- `streamlit_azure_ai_demo.py`: Added thread management logic to 4 scenarios
- Lines updated: Session state init, async functions, UI sections

**User experience:**
- Seamless multi-turn conversations with context
- Follow-up questions reference previous answers
- Clear memory buttons for user control
- Memory persists until cleared or session ends

### Plot Download Button

**Technical Implementation:**
- Code Interpreter saves plots to `/app/generated_plots/` directory
- App scans directory for `.png` files after code execution
- Latest plot detected via `max(glob.glob(...), key=os.path.getctime)`
- Streamlit `st.download_button()` provides instant browser download
- Works with non-root user permissions (appuser:appuser ownership)

**Files modified:**
- `streamlit_azure_ai_demo.py`: Added download button logic to Code Interpreter demo
- `Dockerfile`: Ensured `/app/generated_plots` has correct permissions

**User experience:**
- One-click download of generated visualizations
- PNG format with timestamp-based naming
- Works in both local and Azure Container Apps deployments
- No external storage or blob URLs needed

### Automated Deployment Script

**Script:** `AQ-CODE/deploy-to-azure.sh` (217 lines)

**Features:**
- Automatic timestamp tag generation: `YYYYMMDD-HHMMSS`
- Azure Container Registry build (no local Docker needed)
- Managed Identity configuration and role assignment
- Container App creation or update (idempotent)
- Health check and URL retrieval
- Comprehensive error handling and logging

**Configuration (edit script variables):**
```bash
RESOURCE_GROUP="agent-framework-rg"
LOCATION="eastus"
ACR_NAME="aqr2d2agentframeworkacr007"
CONTAINERAPPS_ENV="agent-framework-env"
APP_NAME="agent-framework-demo"
IMAGE_NAME="agent-framework-demo"
```

**Deployment steps automated:**
1. Generate timestamp tag
2. Build Docker image in ACR (90-120 seconds)
3. Push to registry
4. Update Container App with new image
5. Verify Managed Identity and role assignments
6. Wait for app to be ready
7. Display HTTPS URL

**Usage:**
```bash
cd AQ-CODE
bash deploy-to-azure.sh
```

### Managed Identity Authentication

**Implementation:**
- Container App created with `--system-assigned` identity
- Managed Identity assigned "Cognitive Services User" role
- App uses `DefaultAzureCredential()` from `azure.identity`
- No API keys in environment variables or code

**Code changes:**
```python
from azure.identity import DefaultAzureCredential

# In streamlit_azure_ai_demo.py
credential = DefaultAzureCredential()  # Automatically uses MI in ACA
client = AIProjectClient.from_connection_string(
    endpoint=azure_ai_endpoint,
    credential=credential
)
```

**Security benefits:**
- No secrets in code, config files, or environment
- Automatic credential rotation via Azure AD
- Audit trail via Azure Activity Log
- Least-privilege access (Cognitive Services User only)
- Compliant with enterprise security policies
- Works across Azure services (AI Foundry, OpenAI, Search, etc.)

**Local development fallback:**
- `DefaultAzureCredential` tries multiple auth methods:
  1. Environment variables (if present)
  2. Managed Identity (in Azure)
  3. Azure CLI (`az login`)
  4. Visual Studio Code
  5. Azure PowerShell

---

## Changelog

**October 26, 2025:**
- ✅ Added conversation memory to 4 scenarios (Thread Mgmt, Azure AI Search, Bing, File Search)
- ✅ Implemented plot download button for Code Interpreter
- ✅ Created automated deployment script (`deploy-to-azure.sh`)
- ✅ Migrated to Managed Identity authentication (no more API keys!)
- ✅ Implemented timestamp-based image tagging for ACR
- ✅ Enhanced documentation (README.md, DOCKER_README.md)
- ✅ Deployed live demo to Azure Container Apps

**October 25, 2025:**
- Initial Docker containerization
- Multi-stage Dockerfile with non-root user
- Azure Container Registry integration
- Manual deployment documentation
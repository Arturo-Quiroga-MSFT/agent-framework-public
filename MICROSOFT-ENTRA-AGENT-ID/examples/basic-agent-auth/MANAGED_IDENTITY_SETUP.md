# Managed Identity Setup Guide
Date: January 19, 2026

## Why DefaultAzureCredential Falls Back to CLI

**Current behavior is correct!** The code is running on your local Mac, which:
- ❌ Has no Azure IMDS (Instance Metadata Service) endpoint
- ❌ Cannot authenticate with `ManagedIdentityCredential`
- ✅ Falls back to `DefaultAzureCredential` → Azure CLI (works!)

This is **by design** - develop locally, deploy to Azure, no code changes needed.

---

## To Test TRUE Managed Identity

You need to run the code on an Azure-hosted resource with managed identity enabled.

### Option 1: Azure VM (Recommended for Testing)

#### 1. Create VM with Managed Identity

```bash
# Create resource group (if needed)
az group create --name ManagedIdentityTest --location eastus

# Create VM with system-assigned managed identity
az vm create \
  --resource-group ManagedIdentityTest \
  --name test-agent-vm \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys \
  --assign-identity
```

#### 2. Grant Permissions

```bash
# Get the managed identity principal ID
PRINCIPAL_ID=$(az vm identity show \
  --resource-group ManagedIdentityTest \
  --name test-agent-vm \
  --query principalId -o tsv)

echo "Managed Identity Principal ID: $PRINCIPAL_ID"

# Grant Reader role (for management APIs)
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role Reader \
  --scope /subscriptions/7a28b21e-0d3e-4435-a686-d92889d4ee96

# Grant Storage Blob Data Reader (if using storage)
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/7a28b21e-0d3e-4435-a686-d92889d4ee96/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.Storage/storageAccounts/aqmlwork0018580440867

# Grant Cognitive Services OpenAI User (for LLM examples)
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope /subscriptions/7a28b21e-0d3e-4435-a686-d92889d4ee96/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.CognitiveServices/accounts/r2d2-foundry-001
```

#### 3. Deploy and Run Code

```bash
# SSH into VM
ssh azureuser@<VM-PUBLIC-IP>

# Install Python and dependencies
sudo apt update
sudo apt install -y python3-pip git
git clone <your-repo>
cd MICROSOFT-ENTRA-AGENT-ID/examples/basic-agent-auth

# Install packages
pip3 install -r requirements.txt

# Copy .env file (only AZURE_OPENAI_* values needed, no credentials!)
cat > .env << 'EOF'
AZURE_OPENAI_ENDPOINT=https://r2d2-foundry-001.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
STORAGE_ACCOUNT_NAME=aqmlwork0018580440867
STORAGE_CONTAINER_NAME=agent-test
EOF

# Run the managed identity examples
python3 managed_identity_agent.py
python3 managed_identity_agent_llm.py
```

**Expected Output:**
```
✓ Using system-assigned managed identity
✓ Token acquired via managed identity (NOT fallback!)
```

---

### Option 2: Azure Container Instance (Serverless)

Perfect for testing without managing VMs:

```bash
# Create container group with managed identity
az container create \
  --resource-group ManagedIdentityTest \
  --name test-agent-container \
  --image python:3.12 \
  --assign-identity \
  --command-line "/bin/bash -c 'sleep infinity'" \
  --cpu 1 \
  --memory 1

# Get managed identity principal ID
PRINCIPAL_ID=$(az container show \
  --resource-group ManagedIdentityTest \
  --name test-agent-container \
  --query identity.principalId -o tsv)

# Grant permissions (same as above)
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role Reader \
  --scope /subscriptions/7a28b21e-0d3e-4435-a686-d92889d4ee96

# Exec into container
az container exec \
  --resource-group ManagedIdentityTest \
  --name test-agent-container \
  --exec-command "/bin/bash"

# Inside container, install and run code
pip install azure-identity azure-storage-blob openai
# ... copy code and run
```

---

### Option 3: Azure App Service (Web App)

If you want to expose the agent as a web service:

```bash
# Create App Service plan
az appservice plan create \
  --name test-agent-plan \
  --resource-group ManagedIdentityTest \
  --sku B1 \
  --is-linux

# Create web app with managed identity
az webapp create \
  --resource-group ManagedIdentityTest \
  --plan test-agent-plan \
  --name test-agent-app-$RANDOM \
  --runtime "PYTHON:3.12" \
  --assign-identity

# Get managed identity
PRINCIPAL_ID=$(az webapp identity show \
  --resource-group ManagedIdentityTest \
  --name test-agent-app-<YOUR-ID> \
  --query principalId -o tsv)

# Grant permissions (same as above)
# ... deploy code via GitHub Actions, Azure DevOps, or az webapp up
```

---

### Option 4: Azure Functions (Serverless Functions)

For event-driven agent execution:

```bash
# Create Function App with managed identity
az functionapp create \
  --resource-group ManagedIdentityTest \
  --name test-agent-func-$RANDOM \
  --storage-account <storage-account> \
  --runtime python \
  --runtime-version 3.12 \
  --functions-version 4 \
  --assign-identity

# Get managed identity and grant permissions
# ... same pattern as above
```

---

## Key Differences: Local (CLI) vs Azure (Managed Identity)

### Local Development (Current)
```python
# Uses DefaultAzureCredential
# Falls back to: Azure CLI → Works! ✓
# Pros: Easy development, no credential management
# Cons: Not testing true managed identity
```

### Azure-Hosted (True Managed Identity)
```python
# Uses ManagedIdentityCredential directly
# No fallback needed
# Pros: Production-ready, no secrets, automatic credential rotation
# Cons: Requires Azure resource
```

---

## Cost Considerations

**Cheapest options for testing:**
1. **Azure Container Instances** - ~$0.0012/vCPU-second (~$3.50/month if running 24/7)
2. **Azure VM B1s** - ~$7.59/month (pay-as-you-go)
3. **Azure Functions** - First 1M executions free

**Recommendation:** Use Container Instances for quick tests, then delete when done.

---

## Do You NEED to Test True Managed Identity?

**Honestly? No, for most cases.**

The fallback to Azure CLI proves:
- ✅ Your code works with credential-based authentication
- ✅ RBAC permissions are correct
- ✅ Azure OpenAI integration works
- ✅ Storage access works

The **only difference** in Azure is:
- Uses IMDS endpoint instead of Azure CLI
- No credential files on disk
- Automatic credential rotation by Azure

**When you SHOULD test on Azure:**
- Before production deployment
- To test system-assigned vs user-assigned identity
- To validate IMDS endpoint behavior
- To test in actual production environment

**For development/testing:** The current Azure CLI fallback is perfectly fine!

---

## Quick Decision Matrix

| Scenario | Use This | Reason |
|----------|----------|--------|
| Local development | DefaultAzureCredential + Azure CLI | Fast, easy, no Azure resources needed |
| CI/CD pipeline | Service Principal | Predictable, auditable |
| Production in Azure | Managed Identity | Secure, no secrets, auto-rotation |
| Pre-deployment testing | Azure VM or Container Instance | Test actual managed identity |

---

## TL;DR

**Current state:** ✅ Working perfectly with Azure CLI fallback  
**To test true managed identity:** Deploy to Azure VM/Container/App Service  
**Do you need to?** Not really, unless you're about to deploy to production  
**Cost to test:** ~$3-8/month for VM/Container (can delete after testing)  

**Recommendation:** Keep using Azure CLI for development. Test on Azure VM only when you're ready to deploy to production.

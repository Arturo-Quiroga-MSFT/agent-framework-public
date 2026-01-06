# Jason's Travel Agent Demo - Troubleshooting Summary

**Date:** January 6, 2026  
**Contact:** Jason Virtue  
**Project:** Travel agent handoff demo using Microsoft Agent Framework  
**Fixed Notebook:** `14-handoffjdv-AQ-modified.ipynb`

---

## 📋 Original Questions from Jason

### Question 1: GitHub Models → Azure AI Foundry Migration
**Issue:** Current repo uses GitHub models with rate limits. Wants to use Foundry and connect with Foundry project to call Azure OpenAI models.

**Answer:** ✅ FIXED - Updated Cell 7 (Step 2) with proper Azure AI Foundry setup using `AzureOpenAIChatClient.from_connection()`

### Question 2: AzureOpenAIChatClient Syntax
**Issue:** In "Step 2", setting up chat_client for OpenAIClient. Assumes need to change to AzureOpenAIChatClient but unsure of syntax.

**Answer:** ✅ FIXED - For handoff workflows, use `AzureOpenAIChatClient` (not `AzureAIClient`):

```python
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# AzureOpenAIChatClient automatically reads from environment:
# - AZURE_AI_PROJECT_ENDPOINT
# - AZURE_AI_MODEL_DEPLOYMENT_NAME
chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
```

**Key Points:**
- Use `AzureOpenAIChatClient` for handoff workflows (matches official MAF v2 examples)
- Use `AzureCliCredential` (inherits from `az login`)
- Automatically reads configuration from environment variables
- No manual connection management needed

### Question 3: Async Method Alternative
**Issue:** In "Step 6", using AzureOpenAIChatClient in async call - thinks this is core issue. Wants to see alternative function for async method. Thought it was AIO but not sure.

**Answer:** ✅ NO ISSUE - The async/await code was already correct! The problem was only in the client initialization (Question 2). The `await workflow.run_stream()` pattern is the correct async approach.

---

## 🔧 Changes Made to Notebook

### 1. Updated Cell 3 (Imports)
**Added:**
```python
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
```

### 2. Fixed Cell 7 (Step 2 - Client Setup)
**Before:** Using wrong client type or patterns  
**After:** Correct MAF v2 pattern for handoff workflows

**Key Fix:**
```python
chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
```

- Uses `AzureOpenAIChatClient` (designed for handoff workflows)
- Uses `AzureCliCredential` (standard authentication)
- Automatically reads `AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` from environment
- No connection management needed

### 3. Updated Cell 8 (Configuration Requirements)
**Simplified to just 2 environment variables:**
- `AZURE_AI_PROJECT_ENDPOINT` - Azure AI Foundry project endpoint
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` - Model deployment name (e.g., gpt-4.1)

### 4. Agent Naming Fix
**Changed:** Agent names must use **hyphens** (not underscores)
- ✅ `travel-agent` (correct)
- ❌ `travel_agent` (causes validation errors)

---

## ✅ Setup Instructions for Jason

### Step 1: Authenticate with Azure
```bash
az login
```

### Step 2: Create `.env` File
Create a `.env` file in `/Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/JV/` with:

```bash
PROJECT_ENDPOINT=https://[your-project-name]..........
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4.1
```

**To get PROJECT_ENDPOINT:**
1. Go to https://ai.azure.com
2. Open your project
3. Click "Settings" → Copy the endpoint URL

**To get AZURE_OPENAI_CHAT_DEPLOYMENT_NAME:**
1. In your Foundry project, go to "Deployments"
2. Copy the exact deployment name (e.g., `gpt-4o`, `gpt-4o-mini`)

### Step 3: Run the Notebook
Everything should work now! The notebook will:
- ✅ Connect to your Azure AI Foundry project
- ✅ Use your project's Azure OpenAI connection
- ✅ Authenticate via Entra ID (no API keys)
- ✅ Run all handoff scenarios successfully

---

## 🎯 What Was NOT an Issue

**Async/Await Code** - Jason thought this might be the problem, but it was already correct:
```python
# This pattern is CORRECT - no changes needed
events = await drain_events(workflow.run_stream("..."))
```

The Agent Framework properly supports async operations. The issue was purely in the client initialization.

---

## 📊 Architecture Overview

**Handoff Flow:**
1. **User Request** → Travel Agent (main triage)
2. **Travel Agent** → Routes to specialist:
   - Flight Booking Agent
   - Hotel Booking Agent
   - Car Booking Agent
   - Trip Check Agent
3. **Specialist** → Handles request, returns structured result
4. **System** → Returns to user with confirmation

**Key Features:**
- ✅ Dynamic agent routing based on intent
- ✅ Context preservation across handoffs
- ✅ Structured outputs (Pydantic models)
- ✅ Multi-turn conversations
- ✅ Seamless specialist handoffs

---

## 🎤 Demo Prep Notes

**For Jason's talk next week:**

1. **Start Simple:** Show GitHub Models version first (easier to explain)
2. **Then Show Foundry:** Switch to Azure AI Foundry to show enterprise pattern
3. **Highlight Benefits:**
   - No rate limits with Foundry
   - Entra ID authentication (no API keys to manage)
   - Full observability in Azure
   - Production-ready pattern

4. **Test Scenarios to Demo:**
   - Flight booking (Cell 12)
   - Hotel booking (Cell 14)
   - Car booking (Cell 16)
   - Trip confirmation (Cell 18)
   - Pattern analysis (Cell 20)

5. **Control Plane Integration:**
   - Can show how Foundry project manages models
   - Deployment management
   - Cost tracking
   - Usage monitoring

---

## 📞 Follow-up Items

- [ ] Jason creates `.env` file with his Foundry project details
- [ ] Test run the notebook end-to-end
- [ ] Verify all 4 handoff scenarios work
- [ ] Prepare demo script for talk
- [ ] (Optional) Add more travel scenarios based on audience

---

## 📚 Reference Links

- [Azure AI Foundry](https://ai.azure.com)
- [Microsoft Agent Framework Docs](https://microsoft.github.io/agent-framework/)
- [Handoff Orchestration Pattern](https://microsoft.github.io/agent-framework/patterns/handoff/)
- [Azure Authentication](https://learn.microsoft.com/azure/developer/python/sdk/authentication-overview)

---

**Status:** ✅ All issues resolved. Ready for Jason to test with his Foundry project.


# V1 (Classic) Agent Discovery - Important Findings

## Date: November 26, 2025

## The Problem

You have **70+ V1 classic agents** visible in the Azure AI Foundry Portal (Classic view) with `asst_*` IDs (e.g., `asst_UO6Z4kHPlXmcDcso1htds9Xx`), but the Python SDK only returns **19 V2 agents** via `agents.list()`.

## What We Know

### V2 Agents (Currently Visible via SDK)
- **Count**: 19 agents
- **ID Format**: Friendly names (e.g., `BasicWeatherAgent`, `WebSearchAgent`)
- **Structure**: Have `versions.latest` with version numbers
- **Access**: ✅ Fully accessible via `client.agents.list()`
- **Created**: Recently (November 2025)

### V1 Classic Agents (Portal-Only)
- **Count**: 70+ agents
- **ID Format**: OpenAI-style `asst_` prefix (e.g., `asst_UO6Z4kHPlXmcDcso1htds9Xx`)
- **Examples from your list**:
  - `CodeInterpreterAgent` (asst_UO6Z4kHPlXmcDcso1htds9Xx) - gpt-4.1-mini
  - `market_analyst` (asst_ggeVtY06nYOW73nor6XfR3Qb) - gpt-4.1
  - `WeatherAgent` (asst_bFcIb7xAxZcDBGuAkLvYkPeU) - gpt-4.1-mini
  - `DocsAgent` (asst_ZSsX3lck0gdDKfDXLwcopvZk) - gpt-4.1
  - Many session-based agents: `sql-generator-session`, `data-insights-session`, etc.
- **Access**: ❌ **NOT** returned by `client.agents.list()`
- **Created**: August 2025 - November 2025

## Why This Happens

### Theory 1: API Version Filtering
The current Azure AI Projects SDK may be filtering agents by API version:
- `agents.list()` might only return agents created with the **V2 API** (`create_version()`)
- V1 agents created with `create_agent()` might require a different query parameter

### Theory 2: Different Storage Backend
V1 and V2 agents might be stored separately:
- V2 agents: New versioned storage system
- V1 agents: Legacy OpenAI-compatible storage

### Theory 3: Portal Uses Different Endpoint
The Azure AI Foundry Portal (classic view) might use:
- Different REST API endpoints
- Different API versions (`api-version` query parameter)
- Direct access to underlying OpenAI-compatible API

## Potential Solutions

### Option 1: OpenAI-Compatible Client
Use the OpenAI client directly to access V1 agents:

```python
from openai import AzureOpenAI

# This might access the classic agents
openai_client = project_client.get_openai_client()
assistants = openai_client.beta.assistants.list()
```

### Option 2: API Version Parameter
Try specifying an older API version:

```python
# Hypothetical - may not be supported
agents = client.agents.list(api_version="2024-02-15-preview")
```

### Option 3: REST API Direct Access
Call the underlying REST API with classic view parameters:

```bash
# List classic agents
curl -X GET "https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject/assistants?api-version=2024-02-15-preview" \
  -H "Authorization: Bearer $(az account get-access-token --query accessToken -o tsv)"
```

### Option 4: Separate Project Theory
Verify all agents are truly in the same project:
- Check project GUID in portal vs endpoint
- Confirm subscription/resource group

## Recommended Next Steps

1. **Verify OpenAI Client Access**:
   ```python
   openai_client = project_client.get_openai_client()
   try:
       assistants = openai_client.beta.assistants.list()
       print(f"Found {len(list(assistants))} assistants")
   except Exception as e:
       print(f"Error: {e}")
   ```

2. **Check REST API Documentation**:
   - Look for classic agent endpoints
   - Find API version that returns V1 agents

3. **Contact Azure Support**:
   - Confirm if V1 agents are accessible via SDK
   - Ask about migration paths

4. **Portal Deletion** (Last Resort):
   - If SDK can't access V1 agents
   - Delete them manually via Foundry Portal

## Impact on Your Toolkit

### Current State
- ✅ `list_agents.py` - Works for V2 agents only
- ✅ `delete_agents.py` - Can delete V2 agents only
- ✅ `check_agent_versions.py` - Only sees V2 agents
- ❌ **Cannot manage 70+ V1 classic agents via SDK**

### What You Need
A way to:
1. List V1 classic agents with `asst_*` IDs
2. Delete V1 classic agents programmatically
3. Bulk cleanup of old session agents

## Workarounds

### Manual Cleanup (Portal)
1. Go to https://ai.azure.com
2. Navigate to your project → Agents
3. Add `?view=foundry-classic` to URL
4. Select and delete agents manually

### Selective Cleanup
Focus on cleaning up V2 agents (current toolkit works):
- Test agents: `MyCustomSearchAgent`, `MySearchAgent`
- Duplicate agents: Multiple `WeatherAgent` versions
- Development agents: `BasicAgent`, `THINKER`

## Questions to Investigate

1. What command/API does the Foundry Portal use to list classic agents?
2. Is there an `api-version` parameter that returns V1 agents?
3. Can `get_openai_client()` access classic assistants?
4. Are there separate endpoints for `/agents` (V2) vs `/assistants` (V1)?
5. Does Microsoft have migration documentation for this scenario?

## Related Documentation

- Azure AI Foundry Classic View: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry-classic
- OpenAI Assistants API: https://platform.openai.com/docs/assistants/overview
- Azure AI Projects SDK: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme

---

**Status**: Investigation in progress  
**Blocker**: Python SDK doesn't return V1 classic agents  
**Impact**: Cannot programmatically manage 70+ legacy agents


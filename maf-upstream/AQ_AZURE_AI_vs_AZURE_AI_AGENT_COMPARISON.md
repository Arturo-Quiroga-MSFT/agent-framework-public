# Azure AI vs Azure AI Agent: Detailed Comparison

**Date:** November 21, 2025  
**Purpose:** Understand the differences between the two Azure AI agent implementations in MAF

---

## Overview

The MAF Python framework now has **TWO separate implementations** for Azure AI agents:

| Directory | API | Package | Version | Status |
|-----------|-----|---------|---------|--------|
| `azure_ai/` | `AzureAIClient` | `azure-ai-projects` | 2.x (V2) | **Current/Recommended** |
| `azure_ai_agent/` | `AzureAIAgentClient` | `azure-ai-agents` | 1.x (V1) | Legacy/Backward Compatibility |

---

## Key Differences

### 1. **Client Class Names**
```python
# V2 (azure_ai/) - NEW API
from agent_framework.azure import AzureAIClient

# V1 (azure_ai_agent/) - LEGACY API  
from agent_framework.azure import AzureAIAgentClient
```

### 2. **Underlying SDK**
- **V2 (`AzureAIClient`)**: Uses `azure-ai-projects` 2.x SDK
  - Released: November 11, 2025 (very recent!)
  - [Changelog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/CHANGELOG.md#200b1-2025-11-11)
  
- **V1 (`AzureAIAgentClient`)**: Uses `azure-ai-agents` 1.x SDK
  - Older API surface
  - Maintained for backward compatibility

### 3. **Feature Availability**

#### Features in V2 ONLY (`azure_ai/`)
The following samples exist **ONLY** in the V2 directory:

1. ✅ **`azure_ai_use_latest_version.py`** - Reuse latest agent version
2. ✅ **`azure_ai_with_agent_to_agent.py`** - Agent-to-agent (A2A) protocol
3. ✅ **`azure_ai_with_browser_automation.py`** - Browser automation
4. ✅ **`azure_ai_with_existing_conversation.py`** - Resume conversations (replaces `existing_thread`)
5. ✅ **`azure_ai_with_image_generation.py`** - Image generation tool
6. ✅ **`azure_ai_with_microsoft_fabric.py`** - Microsoft Fabric integration
7. ✅ **`azure_ai_with_response_format.py`** - Structured outputs with Pydantic
8. ✅ **`azure_ai_with_search_context_agentic.py`** - Agentic search (Knowledge Bases)
9. ✅ **`azure_ai_with_search_context_semantic.py`** - Semantic search (RAG)
10. ✅ **`azure_ai_with_sharepoint.py`** - SharePoint grounding
11. ✅ **`azure_ai_with_web_search.py`** - `HostedWebSearchTool`

#### Features in V1 ONLY (`azure_ai_agent/`)
The following samples exist **ONLY** in the V1 directory:

1. ✅ **`azure_ai_with_function_tools.py`** - Explicit function tool patterns
2. ✅ **`azure_ai_with_local_mcp.py`** - Local MCP server integration
3. ✅ **`azure_ai_with_multiple_tools.py`** - Multi-tool coordination
4. ✅ **`azure_ai_with_openapi_tools.py`** - OpenAPI/REST API integration
5. ✅ **`azure_ai_with_existing_thread.py`** - Thread management (old naming)

#### Common Features (in both)
- ✅ Basic agent creation
- ✅ Azure AI Search integration
- ✅ Bing Grounding search
- ✅ Bing Custom Search
- ✅ Code interpreter
- ✅ File search
- ✅ Hosted MCP
- ✅ Thread management
- ✅ Explicit settings configuration
- ✅ Existing agent reuse

---

## Code Comparison: Basic Example

### V2 API (`azure_ai/`)
```python
from agent_framework.azure import AzureAIClient

async with (
    AzureCliCredential() as credential,
    AzureAIClient(async_credential=credential).create_agent(
        name="BasicWeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent,
):
    result = await agent.run(query)
```

### V1 API (`azure_ai_agent/`)
```python
from agent_framework.azure import AzureAIAgentClient

async with (
    AzureCliCredential() as credential,
    AzureAIAgentClient(async_credential=credential).create_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent,
):
    result = await agent.run(query)
```

**Observation:** The API surface is nearly identical! The main difference is the class name.

---

## Migration Strategy

### When to Use V2 (`AzureAIClient`)
✅ **Recommended for:**
- New projects starting from scratch
- Projects needing newer features:
  - Agent-to-agent communication
  - Browser automation
  - Image generation
  - Microsoft Fabric integration
  - SharePoint grounding
  - Structured outputs (response format)
  - Advanced search (agentic/semantic modes)

### When to Use V1 (`AzureAIAgentClient`)
⚠️ **Consider for:**
- Existing projects on V1 that need backward compatibility
- Projects using V1-specific patterns (function tools, OpenAPI tools)
- Transitional period before migrating to V2

### Migration Path: V1 → V2

**Step 1:** Change the import
```python
# Old
from agent_framework.azure import AzureAIAgentClient

# New
from agent_framework.azure import AzureAIClient
```

**Step 2:** Update class instantiation
```python
# Old
AzureAIAgentClient(async_credential=credential)

# New
AzureAIClient(async_credential=credential)
```

**Step 3:** Test functionality
- Most code should work without changes
- Update thread → conversation terminology where needed
- Review new V2-specific features for potential improvements

---

## Notable V2 Improvements

### 1. **Conversation vs Thread Terminology**
V2 uses "conversation" terminology more consistently:
- `azure_ai_with_existing_conversation.py` (V2) vs `azure_ai_with_existing_thread.py` (V1)

### 2. **Agent Version Management**
```python
# V2 introduces version control
AzureAIClient().create_agent(
    use_latest_version=True  # Reuse existing agent instead of creating new version
)
```

### 3. **Advanced Search Modes**
V2 introduces sophisticated search patterns:
- **Agentic mode**: Multi-hop reasoning with Knowledge Bases (more accurate)
- **Semantic mode**: Fast hybrid search with semantic ranking (faster)

### 4. **Structured Outputs**
```python
# V2 supports Pydantic models for response schemas
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    temperature: int
    condition: str

agent = AzureAIClient().create_agent(
    response_format=WeatherResponse
)
```

### 5. **Modern Integrations**
- Browser automation capabilities
- SharePoint content search
- Microsoft Fabric data queries
- Agent-to-agent protocol support

---

## Recommendation

### For Your Migration
Since you're comparing code between old and new:

1. ✅ **Adopt V2 (`AzureAIClient`)** for new development
2. ✅ **Reference V1 (`AzureAIAgentClient`)** samples for patterns not yet in V2:
   - Function tools patterns
   - OpenAPI integration
   - Multi-tool coordination
   - Local MCP servers
3. ✅ **Expect** Microsoft to eventually deprecate V1 in favor of V2

### Priority Samples to Review

**High Priority (New V2 Features):**
1. `azure_ai_with_response_format.py` - Structured outputs
2. `azure_ai_with_search_context_agentic.py` - Advanced RAG
3. `azure_ai_with_agent_to_agent.py` - A2A communication
4. `azure_ai_use_latest_version.py` - Version management
5. `azure_ai_with_existing_conversation.py` - Modern conversation handling

**Medium Priority (Useful V1 Patterns):**
1. `azure_ai_with_function_tools.py` (V1) - Function tool patterns
2. `azure_ai_with_openapi_tools.py` (V1) - REST API integration
3. `azure_ai_with_multiple_tools.py` (V1) - Multi-tool workflows

---

## Summary Table

| Aspect | V2 (`azure_ai/`) | V1 (`azure_ai_agent/`) |
|--------|------------------|------------------------|
| **Class** | `AzureAIClient` | `AzureAIAgentClient` |
| **SDK** | `azure-ai-projects` 2.x | `azure-ai-agents` 1.x |
| **Status** | ✅ Current | ⚠️ Legacy |
| **Release** | Nov 2025 | Earlier |
| **Sample Count** | 22 files | 16 files |
| **New Features** | 11 exclusive samples | 5 exclusive samples |
| **Recommended** | ✅ Yes (for new projects) | ⚠️ For compatibility only |

---

## Next Steps

1. Review V2 basic samples to understand the new API
2. Identify which V2-exclusive features are valuable for your use case
3. Check if any V1-exclusive patterns are needed (function tools, OpenAPI)
4. Plan migration timeline for existing code
5. Test both APIs in your environment to validate compatibility

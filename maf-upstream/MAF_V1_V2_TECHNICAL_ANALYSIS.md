# MAF Azure AI: V1 vs V2 Technical Deep Dive

**Analysis Date:** November 21, 2025  
**Critical Discovery:** Both APIs coexist in the **SAME package** but use **DIFFERENT Azure SDKs**

---

## 🚨 Critical Finding: Dual SDK Architecture

The `agent-framework-azure-ai` package includes **BOTH** implementations in a single package:

```python
# From agent_framework_azure_ai/__init__.py
from ._chat_client import AzureAIAgentClient  # V1 - Legacy
from ._client import AzureAIClient             # V2 - Current

__all__ = [
    "AzureAIAgentClient",  # V1
    "AzureAIClient",        # V2
    "AzureAISettings",
]
```

### Package Dependencies (pyproject.toml)

#### **NEW (maf-upstream)** - Version 1.0.0b251120
```toml
dependencies = [
    "agent-framework-core",
    "azure-ai-projects >= 2.0.0b2",    # ✅ V2 SDK
    "azure-ai-agents == 1.2.0b5",      # ⚠️ V1 SDK (backward compat)
    "aiohttp",
]
```

#### **OLD (your python/)** - Version 1.0.0b251108
```toml
dependencies = [
    "agent-framework-core",
    "azure-ai-projects >= 1.0.0b11",   # ⚠️ V1 SDK (older)
    "azure-ai-agents == 1.2.0b5",      # ⚠️ V1 SDK
    "aiohttp",
]
```

### Key Observation
- **NEW**: Requires `azure-ai-projects >= 2.0.0b2` (released Nov 11, 2025)
- **OLD**: Uses `azure-ai-projects >= 1.0.0b11` (pre-2.0)
- **BOTH**: Include `azure-ai-agents` for backward compatibility

---

## Architecture Comparison

### V2: AzureAIClient (Recommended)

**File:** `_client.py`

```python
class AzureAIClient(OpenAIBaseResponsesClient):
    """Azure AI Agent client."""
    
    def __init__(
        self,
        *,
        project_client: AIProjectClient | None = None,  # azure-ai-projects 2.x
        agent_name: str | None = None,
        agent_version: str | None = None,              # ✅ Version support
        conversation_id: str | None = None,             # ✅ Conversation terminology
        use_latest_version: bool | None = None,        # ✅ Smart version reuse
        # ... other params
    ):
```

**Base Class:** `OpenAIBaseResponsesClient`
- Inherits from OpenAI Responses API pattern
- Uses `azure-ai-projects` 2.x SDK
- Uses `AIProjectClient` for service communication

**Key Features:**
- ✅ Agent versioning (`agent_version`, `use_latest_version`)
- ✅ Conversation-based terminology
- ✅ Structured outputs via Pydantic models
- ✅ Modern integrations (Browser, Fabric, SharePoint)
- ✅ Advanced search modes (agentic/semantic)

### V1: AzureAIAgentClient (Legacy)

**File:** `_chat_client.py`

```python
class AzureAIAgentClient(BaseChatClient):
    """Azure AI Agent Chat client."""
    
    def __init__(
        self,
        *,
        agents_client: AgentsClient | None = None,  # azure-ai-agents 1.x
        agent_id: str | None = None,
        agent_name: str | None = None,
        thread_id: str | None = None,              # ⚠️ Thread terminology
        should_cleanup_agent: bool = True,
        # ... other params
    ):
```

**Base Class:** `BaseChatClient`
- Inherits from MAF's base chat client
- Uses `azure-ai-agents` 1.x SDK
- Uses `AgentsClient` for service communication

**Key Features:**
- ✅ Function tools with explicit patterns
- ✅ OpenAPI/REST integration
- ✅ Multi-tool coordination
- ✅ Local MCP server support
- ⚠️ Thread-based terminology (older)
- ⚠️ No agent versioning
- ⚠️ No structured outputs

---

## SDK Comparison Table

| Aspect | V2 (`AzureAIClient`) | V1 (`AzureAIAgentClient`) |
|--------|---------------------|---------------------------|
| **Implementation File** | `_client.py` | `_chat_client.py` |
| **Base Class** | `OpenAIBaseResponsesClient` | `BaseChatClient` |
| **Azure SDK** | `azure-ai-projects >= 2.0.0b2` | `azure-ai-agents == 1.2.0b5` |
| **SDK Client** | `AIProjectClient` | `AgentsClient` |
| **Import** | `from azure.ai.projects.aio` | `from azure.ai.agents.aio` |
| **Release Date** | Nov 11, 2025 | Earlier (1.x series) |
| **Conversation/Thread** | `conversation_id` | `thread_id` |
| **Versioning** | ✅ Yes (`agent_version`) | ❌ No |
| **Latest Version Reuse** | ✅ `use_latest_version=True` | ❌ No |
| **Structured Outputs** | ✅ Pydantic models | ❌ No |
| **Response Format** | ✅ `ResponseTextFormatConfig` | ⚠️ Limited |
| **Sample Count** | 22 files | 16 files |

---

## Code-Level Differences

### Creating an Agent

#### V2 API
```python
from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential

async with (
    AzureCliCredential() as credential,
    AzureAIClient(
        async_credential=credential,
        agent_name="MyAgent",
        agent_version="1.0",                    # ✅ Version control
        use_latest_version=True,                # ✅ Reuse existing
        conversation_id="existing-conv-123"     # ✅ Resume conversation
    ).create_agent(
        name="MyAgent",
        instructions="You are helpful.",
        tools=my_tool,
    ) as agent,
):
    result = await agent.run("Hello")
```

#### V1 API
```python
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async with (
    AzureCliCredential() as credential,
    AzureAIAgentClient(
        async_credential=credential,
        agent_id="existing-agent-id",           # ⚠️ Agent ID only
        agent_name="MyAgent",
        thread_id="existing-thread-123",        # ⚠️ Thread terminology
        should_cleanup_agent=True               # ⚠️ Manual cleanup control
    ).create_agent(
        name="MyAgent",
        instructions="You are helpful.",
        tools=my_tool,
    ) as agent,
):
    result = await agent.run("Hello")
```

### Structured Outputs (V2 Only)

```python
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    temperature: int
    condition: str
    location: str

async with AzureAIClient().create_agent(
    name="WeatherAgent",
    response_format=WeatherResponse  # ✅ V2: Pydantic model enforcement
) as agent:
    result = await agent.run("What's the weather?")
    # result is guaranteed to match WeatherResponse schema
```

**V1 Limitation:** No structured output support

### Agent Versioning (V2 Only)

```python
# V2: Reuse the latest version instead of creating new one
async with AzureAIClient(
    agent_name="MyAgent",
    use_latest_version=True  # ✅ Smart: reuses latest if exists
).create_agent(...) as agent:
    pass

# V1: Always creates new agent or requires explicit agent_id
async with AzureAIAgentClient(
    agent_id="must-know-id"  # ⚠️ Must specify existing ID manually
).create_agent(...) as agent:
    pass
```

---

## Migration Implications

### For Your Existing Code (`python/`)

Your current code uses `azure-ai-projects >= 1.0.0b11`, which means:

1. **If you're using `AzureAIClient`**: 
   - ⚠️ You're on the **older V1 version** of `azure-ai-projects`
   - ⚠️ You might not have V2 features even though you use `AzureAIClient`
   - ✅ Upgrade to `azure-ai-projects >= 2.0.0b2` to get full V2 features

2. **If you're using `AzureAIAgentClient`**:
   - ✅ You're fine for now (uses `azure-ai-agents` 1.2.0b5)
   - ⚠️ But consider migrating to V2 for new features

### Critical Version Check

```bash
# Check your current version
pip show azure-ai-projects

# If version < 2.0.0, you need to upgrade for V2 features
pip install --upgrade "azure-ai-projects>=2.0.0b2"
```

---

## Recommended Migration Path

### Phase 1: Assessment (Immediate)
1. ✅ **Check current SDK version:**
   ```bash
   pip show azure-ai-projects azure-ai-agents
   ```
2. ✅ **Audit your code:**
   ```bash
   grep -r "AzureAIClient\|AzureAIAgentClient" your_code/
   ```
3. ✅ **Identify which client you're using**

### Phase 2: Test Environment (1-2 days)
1. ✅ **Create test branch**
2. ✅ **Update dependencies:**
   ```toml
   dependencies = [
       "agent-framework-core",
       "azure-ai-projects >= 2.0.0b2",  # Upgrade to V2
       "azure-ai-agents == 1.2.0b5",    # Keep V1 for compatibility
   ]
   ```
3. ✅ **Run existing tests**
4. ✅ **Test V2-specific features in isolation**

### Phase 3: Gradual Migration (ongoing)
1. ✅ **Keep `AzureAIClient` imports** (class name doesn't change!)
2. ✅ **Update to V2 SDK** (`azure-ai-projects >= 2.0.0b2`)
3. ✅ **Add V2 features incrementally:**
   - Agent versioning (`use_latest_version=True`)
   - Structured outputs (Pydantic models)
   - Conversation terminology (if using threads)
4. ✅ **Test thoroughly before production**

### Phase 4: Future-Proofing
1. ⚠️ **Plan to deprecate V1 patterns** eventually
2. ✅ **Use V2-exclusive features** for new code:
   - Browser automation
   - Image generation
   - SharePoint/Fabric integration
   - Agentic search modes

---

## Breaking Changes to Watch

### 1. Thread → Conversation Terminology

**V1:**
```python
AzureAIAgentClient(thread_id="abc123")
```

**V2:**
```python
AzureAIClient(conversation_id="abc123")
```

### 2. Agent Version Management

**V1:** No versioning concept
```python
# Creates new agent every time
agent = AzureAIAgentClient().create_agent(name="MyAgent")
```

**V2:** Smart versioning
```python
# Reuses latest version if exists
agent = AzureAIClient(use_latest_version=True).create_agent(name="MyAgent")
```

### 3. Cleanup Behavior

**V1:** Explicit control
```python
AzureAIAgentClient(should_cleanup_agent=True)  # Default: auto-cleanup
```

**V2:** Managed automatically based on context

---

## Testing Strategy

### Unit Tests
```python
import pytest
from agent_framework.azure import AzureAIClient, AzureAIAgentClient

async def test_v2_basic():
    """Test V2 API basic functionality"""
    async with AzureAIClient().create_agent(name="Test") as agent:
        result = await agent.run("Hello")
        assert result

async def test_v1_basic():
    """Test V1 API basic functionality (compatibility)"""
    async with AzureAIAgentClient().create_agent(name="Test") as agent:
        result = await agent.run("Hello")
        assert result

async def test_v2_structured_output():
    """Test V2-exclusive structured output"""
    from pydantic import BaseModel
    
    class Response(BaseModel):
        answer: str
    
    async with AzureAIClient().create_agent(
        name="Test",
        response_format=Response
    ) as agent:
        result = await agent.run("Hello")
        # Validate structured output
```

### Integration Tests
```python
async def test_migration_compatibility():
    """Ensure V1 code works with V2 SDK"""
    # Use V1 client with V2 SDK installed
    async with AzureAIAgentClient().create_agent(...) as agent:
        result = await agent.run("Test")
        assert result
```

---

## Summary: Decision Matrix

| Scenario | Recommendation | Client to Use | SDK Version |
|----------|---------------|---------------|-------------|
| **New project** | ✅ Use V2 | `AzureAIClient` | `azure-ai-projects >= 2.0.0b2` |
| **Existing V1 code** | ⚠️ Test then migrate | Keep `AzureAIAgentClient`, test V2 | Upgrade SDK gradually |
| **Need V2 features** | ✅ Migrate now | `AzureAIClient` | `azure-ai-projects >= 2.0.0b2` |
| **Need V1 patterns** | ⚠️ Temporary | `AzureAIAgentClient` | Current SDK |
| **Production stability** | ⚠️ Test thoroughly | Test both, choose based on risk | Version lock |

---

## Quick Reference: Import Statements

```python
# ✅ V2 API (Recommended)
from agent_framework.azure import AzureAIClient
from azure.ai.projects.aio import AIProjectClient

# ⚠️ V1 API (Legacy/Compatibility)
from agent_framework.azure import AzureAIAgentClient
from azure.ai.agents.aio import AgentsClient

# Both are in the same package!
from agent_framework.azure import AzureAIClient, AzureAIAgentClient
```

---

## Next Steps for Your Project

1. ✅ **Check your current SDK versions**
   ```bash
   pip show azure-ai-projects azure-ai-agents agent-framework-azure-ai
   ```

2. ✅ **Scan your codebase**
   ```bash
   grep -r "AzureAIClient\|AzureAIAgentClient" .
   ```

3. ✅ **Upgrade SDK to V2**
   ```bash
   pip install --upgrade "azure-ai-projects>=2.0.0b2"
   ```

4. ✅ **Test compatibility**
   - Run existing tests
   - Verify no breaking changes
   - Test V2 features in dev environment

5. ✅ **Gradually adopt V2 features**
   - Start with `use_latest_version=True`
   - Add structured outputs where valuable
   - Explore new tools (browser, image gen, etc.)

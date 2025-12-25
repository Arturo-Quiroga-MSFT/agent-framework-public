# Azure AI Foundry Agent Portals: V1 vs V2 Explained

## The Problem

Your teammate is seeing agents via the API (`project_client.agents.list()`) but they **don't appear in the new Microsoft Foundry portal**. Meanwhile, other agents appear in the old portal but not the new one. Why?

## Root Cause: Two Agent APIs

Azure AI has **two different Agent APIs** that create agents visible in **different portals**:

| API | Portal Visibility | Agent ID Format | SDK / Client |
|-----|------------------|----------------|--------------|
| **V1 Agents** (Legacy Assistants) | ✅ Old Azure AI Foundry Portal<br>❌ New Microsoft Foundry Portal | `asst_CsBpSN8eof0hEnUmOLSOG6Db` | `AgentsClient` from `azure.ai.agents` or Azure OpenAI Assistants API |
| **V2 Agents** (New Control Plane) | ❌ Old Azure AI Foundry Portal<br>✅ New Microsoft Foundry Portal | Human-readable names (e.g., `ISD-AGENT`, `DataAnalysisAgent`) | `AIProjectClient.agents` from `azure.ai.projects` |

---

## Which API Are You Using?

### V1 Agents (Legacy - Old Portal Only)

```python
from azure.ai.agents.aio import AgentsClient  # ❌ OLD API
from azure.identity.aio import DefaultAzureCredential

async with DefaultAzureCredential() as credential:
    async with AgentsClient(endpoint=endpoint, credential=credential) as client:
        # This creates a V1 agent (old portal only)
        agent = await client.create_agent(
            model="gpt-4",
            name="MyAgent",
            instructions="You are helpful."
        )
        print(f"V1 Agent ID: {agent.id}")  # asst_...
```

**Result**: Agent appears in **old Azure AI Foundry portal only**.

---

### V2 Agents (New - New Portal)

```python
from azure.ai.projects import AIProjectClient  # ✅ NEW API
from azure.identity import DefaultAzureCredential

with DefaultAzureCredential() as credential:
    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:
        # This creates a V2 agent (new portal)
        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name="MyNewAgent",
            instructions="You are helpful.",
            description="A persistent agent"
        )
        print(f"V2 Agent ID: {agent.id}")  # Human-readable name
```

**Result**: Agent appears in **new Microsoft Foundry portal** (Control Plane).

---

## How to Create Persistent Agents in the New Portal

### Problem with `create_version()`

The `azure_ai_with_existing_agent.py` sample uses `create_version()` which is for **versioning** an agent. It's useful for:
- Creating new versions of existing agents
- Testing different configurations
- Rolling back to previous versions

**But**: Many samples then **delete** the version in the `finally` block, so it doesn't persist!

```python
finally:
    # ❌ This deletes the agent version!
    await project_client.agents.delete_version(
        agent_name=azure_ai_agent.name, 
        agent_version=azure_ai_agent.version
    )
```

### Solution: Use `create_agent()` Without Deletion

For a **persistent agent** that shows in the **new portal**:

1. **Use `AIProjectClient.agents.create_agent()`** (not `create_version()`)
2. **Don't delete it** in the finally block
3. **Verify** it appears in `project_client.agents.list_agents()`

See the corrected sample: [`azure_ai_persistent_agent_v2.py`](./agents/azure_ai_persistent_agent_v2.py)

---

## Migration Guide

### If You're Using V1 Agents (Old Portal)

**Cleanup V1 agents:**
```bash
python cleanup_v1_agents.py --delete-all
```

**Create new V2 agents:**
```bash
python deploy_new_agents.py
```

### If You're Using `create_version()` and Deleting

**Before (Non-persistent):**
```python
azure_ai_agent = await project_client.agents.create_version(
    agent_name="MyAgent",
    definition=PromptAgentDefinition(model="gpt-4", instructions="...")
)
# ... use agent ...
finally:
    await project_client.agents.delete_version(...)  # ❌ Deletes agent!
```

**After (Persistent):**
```python
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="MyPersistentAgent",
    instructions="You are a helpful assistant.",
    description="Production agent - do not delete"
)
# ... use agent ...
# No deletion in finally block! ✅
```

---

## Verifying Agent Visibility

### Via API

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
agents = list(client.agents.list_agents())

for agent in agents:
    print(f"Name: {agent.name}")
    print(f"ID: {agent.id}")
    print(f"Model: {agent.model}")
    print(f"Created: {agent.created_at}")
    print("-" * 50)
```

### Via Portal

1. Navigate to [Microsoft Foundry Portal](https://ai.azure.com)
2. Select your project
3. Go to **"Agents"** section in left nav
4. Your V2 agents should appear here

**Note**: V1 agents (with `asst_...` IDs) will **not** appear in this new portal.

---

## Quick Reference

| Goal | API to Use | Portal Visibility |
|------|-----------|------------------|
| Create agent for **new portal** | `AIProjectClient.agents.create_agent()` | ✅ New portal |
| Create agent with **versioning** | `AIProjectClient.agents.create_version()` | ✅ New portal (if not deleted) |
| Create agent for **old portal** | `AgentsClient.create_agent()` | ✅ Old portal |
| List agents in **new portal** | `AIProjectClient.agents.list_agents()` | - |
| List agents in **old portal** | `AgentsClient.list_agents()` | - |
| **Recommended** | `AIProjectClient.agents.create_agent()` | ✅ New portal |

---

## Related Scripts

- [`deploy_new_agents.py`](./deploy_new_agents.py) - Deploy 8 sample V2 agents
- [`cleanup_v1_agents.py`](./cleanup_v1_agents.py) - Remove V1 agents (old portal)
- [`cleanup_v1_assistants.py`](./cleanup_v1_assistants.py) - Remove V1 assistants (OpenAI API)
- [`agents/azure_ai_persistent_agent_v2.py`](./agents/azure_ai_persistent_agent_v2.py) - Correct persistent agent sample

---

## FAQ

**Q: I see agents in `list()` output but not in portal. Why?**  
A: You're likely using V1 agents (`asst_...` IDs) which only appear in the **old Azure AI Foundry portal**, not the new Microsoft Foundry portal.

**Q: How do I migrate from V1 to V2?**  
A: Recreate your agents using `AIProjectClient.agents.create_agent()` (V2 API), then delete V1 agents with `cleanup_v1_agents.py`.

**Q: What's the difference between `create_agent()` and `create_version()`?**  
A: 
- `create_agent()` - Creates a new agent (recommended for persistence)
- `create_version()` - Creates a new version of an existing agent (for version management)

**Q: Why does the sample delete the agent in `finally`?**  
A: Many samples are designed for **testing/demo** purposes and clean up after themselves. For production, remove the deletion code.

**Q: Can I use both V1 and V2 agents in the same project?**  
A: Technically yes, but **not recommended**. Standardize on V2 for new development.

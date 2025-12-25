# Quick Reference: Azure AI Agents Portal Visibility

## The Problem
"My agents show in API but not in portal" or "Some agents show in old portal but not new portal"

## The Root Cause
**Two different agent APIs exist with different portal visibility**

---

## V1 vs V2 Agents

| | V1 Agents (Legacy) | V2 Agents (Current) |
|---|---|---|
| **SDK** | `azure.ai.agents` | `azure.ai.projects` |
| **Client** | `AgentsClient` | `AIProjectClient.agents` |
| **Agent ID** | `asst_ABC123...` | Agent name (e.g., `ISD-AGENT`) |
| **Old Portal** | ✅ Visible | ❌ Not visible |
| **New Portal** | ❌ Not visible | ✅ Visible |
| **Recommended** | ❌ Legacy | ✅ Use this |

---

## Portal URLs

- **Old Portal**: Azure AI Foundry (legacy endpoint)
- **New Portal**: https://ai.azure.com ← Use this

---

## Creating Persistent Agents (V2 API)

### ✅ Correct Pattern (Shows in New Portal)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Create agent
agent = client.agents.create_agent(
    model="gpt-4o",
    name="MyPersistentAgent",
    instructions="You are helpful.",
    description="Production agent"
)

print(f"✅ Created: {agent.name} (ID: {agent.id})")

# ✅ NO DELETION - Agent persists in portal!
```

### ❌ Common Mistake (Agent Gets Deleted)

```python
try:
    agent = await project_client.agents.create_version(...)
    # Use agent...
finally:
    # ❌ THIS DELETES THE AGENT!
    await project_client.agents.delete_version(
        agent_name=agent.name, 
        agent_version=agent.version
    )
```

**Fix**: Remove or comment out the `delete_version()` call.

---

## Quick Decision Tree

```
Do you want agents in the NEW portal (ai.azure.com)?
│
├─ YES → Use AIProjectClient.agents.create_agent()
│        Don't delete in finally block
│        ✅ Shows in new portal
│
└─ NO  → Why? (V1 is legacy, use V2)
```

---

## Verification Checklist

- [ ] Using `AIProjectClient` (not `AgentsClient`)
- [ ] Using `create_agent()` method
- [ ] NOT deleting agent in finally block
- [ ] Agent visible via `client.agents.list_agents()`
- [ ] Agent visible in https://ai.azure.com portal

---

## Sample Code Locations

All in: `/Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025/`

| File | Purpose |
|------|---------|
| **`ANSWER_PERSISTENT_AGENTS.md`** | 📚 Complete guide (START HERE) |
| **`agents/azure_ai_persistent_agent_v2.py`** | ✅ Working sample code |
| `AGENT_PORTALS_EXPLAINED.md` | Detailed V1/V2 explanation |
| `deploy_new_agents.py` | Deploy 8 sample agents |
| `cleanup_v1_agents.py` | Remove V1 agents |

---

## One-Liner Fix

**If your code is based on `azure_ai_with_existing_agent.py`:**

Comment out this line in the `finally` block:
```python
# await project_client.agents.delete_version(...)
```

Done! Agent now persists and shows in portal.

---

## Environment Setup

```bash
# Authenticate
az login

# Set variables
export AZURE_AI_PROJECT_ENDPOINT="https://xxx.services.ai.azure.com/api/projects/xxx"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"

# Run sample
python agents/azure_ai_persistent_agent_v2.py

# Verify in portal
open https://ai.azure.com
```

---

## API Quick Reference

### Create Agent (Simple)
```python
agent = client.agents.create_agent(model="gpt-4o", name="MyAgent", instructions="...")
```

### Create Agent with Version
```python
agent = await client.agents.create_version(agent_name="MyAgent", definition=PromptAgentDefinition(...))
```

### List All Agents
```python
for agent in client.agents.list_agents():
    print(agent.name, agent.id)
```

### Delete Agent (Use Sparingly)
```python
client.agents.delete_agent(agent_id)
```

---

## Getting Help

1. Read [`ANSWER_PERSISTENT_AGENTS.md`](ANSWER_PERSISTENT_AGENTS.md) for complete guide
2. Check [`AGENT_PORTALS_EXPLAINED.md`](AGENT_PORTALS_EXPLAINED.md) for V1/V2 differences
3. Run working samples in [`agents/`](agents/) directory
4. Ask on team chat with error details

---

## TL;DR

**Want agents in new portal?**

1. Use `AIProjectClient.agents.create_agent()` ✅
2. Don't delete in `finally` block ✅
3. Agent shows in https://ai.azure.com ✅

**That's it!**

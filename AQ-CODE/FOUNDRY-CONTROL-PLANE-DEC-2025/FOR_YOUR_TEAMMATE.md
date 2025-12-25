# For Your Teammate: Creating Persistent Agents in New Foundry Portal

Hi! Here's the solution to your agent persistence issue.

## The Problem You're Having

You're seeing agents via `project_client.agents.list()` but they:
1. Don't show in the **new Microsoft Foundry portal** (ai.azure.com)
2. Possibly show in the **old portal** but not the new one
3. Disappear after your script runs

## The Root Cause

The sample code you referenced (`azure_ai_with_existing_agent.py`) **deletes the agent** at the end:

```python
finally:
    # ❌ This line deletes your agent!
    await project_client.agents.delete_version(
        agent_name=azure_ai_agent.name, 
        agent_version=azure_ai_agent.version
    )
```

## The Fix

### Option 1: Quick Fix (If you're using the sample code)

Just **comment out or remove** the deletion line in your `finally` block:

```python
finally:
    # ✅ Comment this out to persist agent:
    # await project_client.agents.delete_version(
    #     agent_name=azure_ai_agent.name, 
    #     agent_version=azure_ai_agent.version
    # )
    pass  # Agent now persists!
```

### Option 2: Better Pattern (Recommended)

Use `create_agent()` instead of `create_version()` - simpler and cleaner:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Setup
endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Create persistent agent
agent = client.agents.create_agent(
    model="gpt-4o",  # Your model deployment name
    name="MyPersistentAgent",
    instructions="You are a helpful assistant.",
    description="This agent persists in Azure"
)

print(f"✅ Created: {agent.name}")
print(f"   ID: {agent.id}")
print(f"   View at: https://ai.azure.com")

# Use with agent framework
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIClient

chat_client = AzureAIClient(project_client=client, agent_id=agent.id)
async with ChatAgent(chat_client=chat_client) as chat_agent:
    result = await chat_agent.run("Hello!")
    print(result)

# ✅ NO DELETION - Agent persists in portal!
```

## Verify It Works

### Via API
```python
# List all agents
agents = list(client.agents.list_agents())
print(f"Total agents: {len(agents)}")
for agent in agents:
    print(f"- {agent.name} (ID: {agent.id})")
```

### Via Portal
1. Go to **https://ai.azure.com**
2. Select your **project**
3. Click **"Agents"** in left sidebar
4. Your agent should appear there! ✅

## Why This Happens (V1 vs V2 Agents)

There are **two different agent APIs** with different portal visibility:

| API | Portal | Agent ID Format |
|-----|--------|----------------|
| **V1** (Legacy) | Old portal only | `asst_ABC...` |
| **V2** (Current) | **New portal** ✅ | Agent name |

You need **V2 agents** (`AIProjectClient.agents`) to show in the **new portal** (ai.azure.com).

## Working Sample Code

I've created complete working samples for you in the repo:

```
AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025/
├── ANSWER_PERSISTENT_AGENTS.md          ← Complete guide (read this!)
├── AGENT_PORTALS_EXPLAINED.md           ← V1 vs V2 explained
├── QUICK_REFERENCE.md                   ← Quick lookup
└── agents/
    ├── azure_ai_persistent_agent_v2.py         ← ✅ RECOMMENDED (simple)
    └── azure_ai_persistent_agent_with_version.py  ← With versioning
```

### Run the Sample

```bash
# Set environment
export AZURE_AI_PROJECT_ENDPOINT="https://xxx.services.ai.azure.com/api/projects/xxx"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"

# Authenticate
az login

# Run the sample
cd /path/to/AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025
python agents/azure_ai_persistent_agent_v2.py
```

## C# Equivalent

Since you mentioned the C# repo, here's the pattern:

```csharp
using Azure.AI.Projects;
using Azure.Identity;

var credential = new DefaultAzureCredential();
var client = new AIProjectClient(endpoint, credential);

// Create persistent agent
var agent = client.GetAgentsClient().CreateAgent(
    model: "gpt-4o",
    name: "MyPersistentAgent",
    instructions: "You are helpful.",
    description: "Production agent"
);

Console.WriteLine($"✅ Created: {agent.Value.Name}");
Console.WriteLine($"   ID: {agent.Value.Id}");

// ✅ NO DELETION - Agent persists!
```

## Common Mistakes to Avoid

❌ **Mistake**: Deleting agent in `finally` block  
✅ **Fix**: Remove the deletion code

❌ **Mistake**: Using `AgentsClient` (V1 API - old portal)  
✅ **Fix**: Use `AIProjectClient.agents` (V2 API - new portal)

❌ **Mistake**: Using `create_version()` when you just need simple persistence  
✅ **Fix**: Use `create_agent()` - simpler and cleaner

## Next Steps

1. **Quick fix**: Comment out the `delete_version()` line in your code
2. **Better approach**: Switch to `create_agent()` pattern (see sample)
3. **Verify**: Check that agent appears in https://ai.azure.com
4. **Deep dive**: Read `ANSWER_PERSISTENT_AGENTS.md` for complete details

## Full Documentation

All docs are in: `/Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025/`

- 📚 **ANSWER_PERSISTENT_AGENTS.md** - Complete answer with all details
- 📖 **AGENT_PORTALS_EXPLAINED.md** - V1 vs V2 agents explained
- ⚡ **QUICK_REFERENCE.md** - Quick lookup card
- ✅ **agents/azure_ai_persistent_agent_v2.py** - Working sample (RECOMMENDED)

## Summary

**TL;DR**: The sample code **deletes** the agent at the end. Just **remove the deletion code** and your agent will persist in the portal at https://ai.azure.com.

Hope this helps! Let me know if you need any clarification.

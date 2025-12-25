# Answer: Creating Persistent Agents that Show in New Foundry Portal

## TL;DR - The Fix

**Problem**: Agents created via API don't appear in new Foundry portal  
**Root Cause**: Sample code **deletes** the agent in the `finally` block  
**Solution**: Comment out the deletion code to make agents persistent

### Quick Fix for Your Code

In your `azure_ai_with_existing_agent.py` based code:

```python
finally:
    # ❌ DELETE THIS LINE to make agents persistent:
    # await project_client.agents.delete_version(
    #     agent_name=azure_ai_agent.name, agent_version=azure_ai_agent.version
    # )
    
    # ✅ Or just replace with:
    pass
```

---

## Understanding the Portal Confusion

Your teammate is experiencing confusion because **there are TWO different agent APIs** that show in **different portals**:

### V1 Agents (Legacy) - OLD Portal Only

```python
from azure.ai.agents.aio import AgentsClient  # ❌ OLD API

agent = await AgentsClient(...).create_agent(...)
# Agent ID format: asst_CsBpSN8eof0hEnUmOLSOG6Db
```

**Visibility**: ✅ Old Azure AI Foundry portal | ❌ New Microsoft Foundry portal (ai.azure.com)

### V2 Agents (Current) - NEW Portal

```python
from azure.ai.projects import AIProjectClient  # ✅ NEW API

agent = project_client.agents.create_agent(...)
# Agent ID format: Human-readable name (e.g., MyPersistentAgent)
```

**Visibility**: ❌ Old Azure AI Foundry portal | ✅ New Microsoft Foundry portal (ai.azure.com)

---

## The Sample Code Issue

The sample you referenced (`azure_ai_with_existing_agent.py`) has this pattern:

```python
# Creates agent
azure_ai_agent = await project_client.agents.create_version(...)

try:
    # Use the agent
    async with ChatAgent(chat_client=chat_client) as agent:
        result = await agent.run(query)
        
finally:
    # ❌ THIS IS THE PROBLEM - DELETES THE AGENT!
    await project_client.agents.delete_version(
        agent_name=azure_ai_agent.name, 
        agent_version=azure_ai_agent.version
    )
```

**Why samples delete agents**: They're designed for **testing/demo** purposes and clean up after themselves.

**For production**: You need to **remove the deletion code**.

---

## Complete Working Solutions

### Option 1: Simple Persistent Agent (Recommended)

Use `create_agent()` without versioning - simplest for most cases:

```python
#!/usr/bin/env python3
import asyncio
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIClient

async def main():
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=endpoint, credential=credential)
    
    # Create persistent agent (V2 API)
    agent = project_client.agents.create_agent(
        model="gpt-4o",  # or your model deployment name
        name="MyPersistentAgent",
        instructions="You are a helpful assistant.",
        description="Production agent - persists in Foundry"
    )
    
    print(f"✅ Created agent: {agent.name}")
    print(f"   ID: {agent.id}")
    print(f"   Model: {agent.model}")
    
    # Use the agent
    chat_client = AzureAIClient(
        project_client=project_client,
        agent_id=agent.id
    )
    
    async with ChatAgent(chat_client=chat_client) as chat_agent:
        result = await chat_agent.run("Hello!")
        print(f"   Response: {result}")
    
    # ✅ NO DELETION - Agent persists!
    print("\n🌐 View in portal: https://ai.azure.com")

asyncio.run(main())
```

**Full sample**: [`agents/azure_ai_persistent_agent_v2.py`](./agents/azure_ai_persistent_agent_v2.py)

---

### Option 2: Persistent Agent with Versioning

If you need versioning (multiple versions of same agent), use `create_version()` but don't delete:

```python
import asyncio
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity.aio import AzureCliCredential
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIClient

async def main():
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], 
            credential=credential
        ) as project_client,
    ):
        # Create versioned agent
        azure_ai_agent = await project_client.agents.create_version(
            agent_name="MyVersionedAgent",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="You are helpful. End responses with [VERSION].",
            ),
        )
        
        print(f"✅ Created: {azure_ai_agent.name} v{azure_ai_agent.version}")
        
        # Use the agent
        chat_client = AzureAIClient(
            project_client=project_client,
            agent_name=azure_ai_agent.name,
            agent_version=azure_ai_agent.version,
        )
        
        try:
            async with ChatAgent(chat_client=chat_client) as agent:
                result = await agent.run("How are you?")
                print(f"   Response: {result}")
        finally:
            # ✅ KEY: Comment out deletion for persistence
            # await project_client.agents.delete_version(
            #     agent_name=azure_ai_agent.name,
            #     agent_version=azure_ai_agent.version
            # )
            pass

asyncio.run(main())
```

**Full sample**: [`agents/azure_ai_persistent_agent_with_version.py`](./agents/azure_ai_persistent_agent_with_version.py)

---

## Verifying Agent Persistence

### Check via API

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

# List all agents
agents = list(client.agents.list_agents())
print(f"Total agents: {len(agents)}")

for agent in agents:
    print(f"- {agent.name} (ID: {agent.id}, Model: {agent.model})")
```

### Check in Portal

1. Navigate to **https://ai.azure.com**
2. Select your **AI Project**
3. Click **"Agents"** in left sidebar
4. Your persistent agents should appear here

**Note**: If you see agents in API output but not portal, they might be V1 agents (check if ID starts with `asst_`).

---

## Migration from V1 to V2

If you have V1 agents that only show in the old portal:

### Step 1: List V1 Agents

```python
from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential

async with DefaultAzureCredential() as credential:
    async with AgentsClient(endpoint=endpoint, credential=credential) as client:
        async for agent in client.list_agents():
            print(f"V1 Agent: {agent.name} (ID: {agent.id})")
```

### Step 2: Recreate as V2

Use `AIProjectClient.agents.create_agent()` (shown above)

### Step 3: Cleanup V1 Agents

Use the cleanup script:

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025
python cleanup_v1_agents.py --delete-all
```

---

## Comparison: create_agent() vs create_version()

| Feature | `create_agent()` | `create_version()` |
|---------|------------------|-------------------|
| **Use Case** | New agent creation | Version management |
| **Versioning** | No | Yes (tracks versions) |
| **Simplicity** | ✅ Simpler | More complex |
| **Best For** | Most production cases | When you need versioning |
| **Portal Visibility** | ✅ New portal | ✅ New portal |

**Recommendation**: Start with `create_agent()` unless you specifically need versioning.

---

## Common Mistakes

### ❌ Mistake 1: Deleting in Finally Block

```python
finally:
    await project_client.agents.delete_version(...)  # ❌ Deletes agent!
```

**Fix**: Remove or comment out deletion code.

### ❌ Mistake 2: Using V1 API (AgentsClient)

```python
from azure.ai.agents.aio import AgentsClient  # ❌ OLD API
```

**Fix**: Use `AIProjectClient` from `azure.ai.projects`.

### ❌ Mistake 3: Wrong create Method

```python
await client.create_agent(...)  # ❌ Async on sync client
```

**Fix**: Use sync client → `client.agents.create_agent()` (no await)

---

## C# Equivalent

Your teammate mentioned the C# sample. Here's the pattern:

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

Console.WriteLine($"Created: {agent.Value.Name} (ID: {agent.Value.Id})");

// ✅ NO DELETION - Agent persists!
```

---

## Reference Scripts in This Repo

All scripts are in: `/Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025/`

| Script | Purpose |
|--------|---------|
| [`agents/azure_ai_persistent_agent_v2.py`](./agents/azure_ai_persistent_agent_v2.py) | ✅ **Recommended**: Simple persistent agent |
| [`agents/azure_ai_persistent_agent_with_version.py`](./agents/azure_ai_persistent_agent_with_version.py) | Persistent agent with versioning |
| [`deploy_new_agents.py`](./deploy_new_agents.py) | Deploy 8 sample V2 agents |
| [`cleanup_v1_agents.py`](./cleanup_v1_agents.py) | Clean up V1 agents (old portal) |
| [`AGENT_PORTALS_EXPLAINED.md`](./AGENT_PORTALS_EXPLAINED.md) | Full portal visibility explanation |

---

## Quick Start

1. **Set environment variables**:
   ```bash
   export AZURE_AI_PROJECT_ENDPOINT="https://xxx.services.ai.azure.com/api/projects/xxx"
   export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"
   ```

2. **Authenticate**:
   ```bash
   az login
   ```

3. **Run the persistent agent sample**:
   ```bash
   cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025
   python agents/azure_ai_persistent_agent_v2.py
   ```

4. **Verify in portal**:
   - Go to https://ai.azure.com
   - Select your project
   - Check "Agents" section

---

## Summary

✅ **To create persistent agents in new portal**:
1. Use `AIProjectClient.agents.create_agent()` (V2 API)
2. Don't delete the agent in finally block
3. Agent will appear in https://ai.azure.com

❌ **Avoid**:
1. Using `AgentsClient` (V1 API - old portal only)
2. Deleting agents in finally block (from sample code)
3. Using `create_agent()` on the wrong client

📚 **See**:
- Working samples in [`agents/`](./agents/) directory
- Full explanation in [`AGENT_PORTALS_EXPLAINED.md`](./AGENT_PORTALS_EXPLAINED.md)

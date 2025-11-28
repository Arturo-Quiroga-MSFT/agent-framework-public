# Azure AI Foundry Agents: V1 (Classic) vs V2 (New) API Guide

## Overview

Azure AI Foundry has evolved its agent API. As of November 2025, **all agents use the V2 API** with versioning support:

- **V2 (New/Current)**: Modern agent API using `create_version()` with built-in versioning
- **V1 (Classic/Legacy)**: Original agent API using `create_agent()` - primarily for backward compatibility

**Important**: The management scripts in this directory work with **ALL** agent types automatically!

## Current State (November 2025)

✅ **All agents created in Azure AI Foundry Portal use V2 API**  
✅ **All agents have `versions.latest` structure with version tracking**  
✅ **SDK defaults to V2 API when creating agents**

The documentation below explains both APIs for backward compatibility, but **you're likely working with V2 agents exclusively**.

## Key Differences

### V1 (Classic) Agents
```python
# Creating a V1 agent
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="my-agent",
    instructions="You are a helpful assistant",
    tools=[...],  # Optional
    tool_resources={...}  # Optional
)

# Agent object properties:
# - agent.id (e.g., "asst_abc123")
# - agent.name
# - agent.model
# - agent.created_at
# - agent.object = "assistant"
# - NO agent.version attribute
```

### V2 (New) Agents
```python
from azure.ai.projects.models import PromptAgentDefinition

# Creating a V2 agent
agent = project_client.agents.create_version(
    agent_name="MyAgent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="You are a helpful assistant",
        tools=[...]  # Optional
    ),
    description="Optional description"
)

# Agent object properties:
# - agent.id (e.g., "my-agent:1")
# - agent.name
# - agent.version (e.g., "1", "2")
# - agent.model
# - agent.created_at
# - agent.object = "agent.version"
```

## API Comparison

| Operation | V1 (Classic) | V2 (New) |
|-----------|--------------|----------|
| **Create** | `create_agent(model, name, ...)` | `create_version(agent_name, definition)` |
| **List** | `agents.list()` | `agents.list()` ✅ Same! |
| **Delete** | `delete_agent(agent_id)` | `delete_version(agent_name, version)` |
| **Agent ID Format** | `asst_abc123` | `agent-name:1` |
| **Versioning** | ❌ No versions | ✅ Versioned (1, 2, 3...) |

## Using the Management Scripts

### List All Agents (Both V1 and V2)
```bash
# Basic listing
./list_agents.py

# Detailed view
./list_agents.py --verbose

# Export to JSON
./list_agents.py --output all-agents.json
```

**Example Output:**
```
=== Azure AI Foundry Agents ===
Total Agents: 5

1. MyV2Agent (ID: MyV2Agent:1)        # V2 agent
   Model: gpt-4o
   Created: 2025-11-26 10:30:15

2. ClassicAgent (ID: asst_abc123)     # V1 agent
   Model: gpt-4o
   Created: 2025-11-25 08:15:42
```

### Delete Agents (Both V1 and V2)
```bash
# Preview what will be deleted
./delete_agents.py --all --dry-run

# Delete specific agents (works for both V1 and V2)
./delete_agents.py --names "MyV2Agent" "ClassicAgent"

# Delete all agents (both V1 and V2)
./delete_agents.py --all
```

## How the Scripts Handle Both Versions

The scripts use **safe attribute access** with `getattr()` to handle both agent types:

```python
# Works for both V1 and V2 agents
agent_name = getattr(agent, 'name', 'Unknown')
agent_id = agent.id  # Both have this
model = getattr(agent, 'model', 'Unknown')

# Version only exists for V2 agents
version = getattr(agent, 'version', None)  # None for V1 agents
```

## Migration Considerations

### Why Two APIs Exist

1. **Backward Compatibility**: V1 agents continue to work
2. **New Features**: V2 adds versioning, new tool types, workflows
3. **Gradual Migration**: You can use both in the same project

### When to Use Each

**Use V1 (Classic)** if:
- ✅ Existing code already uses `create_agent()`
- ✅ Don't need agent versioning
- ✅ Simple single-agent scenarios
- ✅ Using OpenAI-compatible code

**Use V2 (New)** if:
- ✅ Need version control for agents
- ✅ Want latest features (workflows, new tools)
- ✅ Building new agents from scratch
- ✅ Need agent-to-agent communication

### Migrating from V1 to V2

```python
# V1 (Classic)
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="my-agent",
    instructions="You are helpful",
)

# Equivalent V2 (New)
from azure.ai.projects.models import PromptAgentDefinition

agent = project_client.agents.create_version(
    agent_name="my-agent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="You are helpful",
    )
)
```

## Deletion Differences

### V1 Agents - Delete by ID
```bash
# V1 agent ID: asst_abc123
./delete_agents.py --names "ClassicAgent"
# Script finds agent by name, deletes using: delete_agent(agent.id)
```

### V2 Agents - Can Delete Multiple Ways

**Option 1: Using Management Scripts (Recommended)**
```bash
./delete_agents.py --names "MyV2Agent"
# Script handles everything automatically
```

**Option 2: Direct API (Advanced)**
```python
# Delete by agent ID (works like V1)
project_client.agents.delete_agent("MyV2Agent:1")

# Delete specific version
project_client.agents.delete_version(
    agent_name="MyV2Agent",
    agent_version="1"
)

# Delete entire agent (all versions)
project_client.agents.delete_agent("MyV2Agent")
```

## Listing Differences

Both agent types are returned by `agents.list()`:

```python
agents = list(project_client.agents.list())

for agent in agents:
    if hasattr(agent, 'version'):
        print(f"V2 Agent: {agent.name} v{agent.version}")
    else:
        print(f"V1 Agent: {agent.name} (ID: {agent.id})")
```

## Best Practices

### 1. Use Management Scripts for Both
✅ **Recommended**: Use `list_agents.py` and `delete_agents.py` - they handle both versions

### 2. Naming Conventions
- **V1 agents**: Use descriptive names (e.g., "WeatherAgent", "CodeHelper")
- **V2 agents**: Use names suitable for versioning (e.g., "ProductionBot", "QAAssistant")

### 3. Documentation
Always document which API version you used when creating agents:
```python
# V1 (Classic) - Created 2025-01-15
agent = project_client.agents.create_agent(...)

# V2 (New) - Created 2025-11-26
agent = project_client.agents.create_version(...)
```

### 4. Testing
Test with both agent types if you have a mixed environment:
```bash
# List both types
./list_agents.py --verbose

# Check specific patterns
./list_agents.py --filter "*Agent"
```

## Troubleshooting

### Issue: "AttributeError: 'AgentObject' object has no attribute 'version'"

**Solution**: This is normal for V1 agents! The scripts handle this automatically.

```python
# ❌ This will fail for V1 agents
version = agent.version

# ✅ This works for both
version = getattr(agent, 'version', 'N/A')
```

### Issue: Cannot find agent by name

**Reason**: V1 agent IDs are random (`asst_abc123`), not based on name

**Solution**: Use the management scripts which map names to IDs:
```bash
./list_agents.py --names-only  # See all agent names
./delete_agents.py --names "SpecificAgent"  # Delete by name
```

## References

- **V2 (New) Documentation**: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry
- **V1 (Classic) Documentation**: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry-classic
- **Migration Guide**: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/migrate?view=foundry

## Quick Reference

```bash
# List all agents (V1 + V2)
./list_agents.py

# Delete all V1 and V2 agents
./delete_agents.py --all --dry-run  # Preview first
./delete_agents.py --all            # Confirm deletion

# Filter by pattern (works for both)
./list_agents.py --filter "Test*"

# Export inventory (both types)
./list_agents.py --output agents.json
```

---

**Last Updated**: November 26, 2025  
**Author**: Azure AI Team

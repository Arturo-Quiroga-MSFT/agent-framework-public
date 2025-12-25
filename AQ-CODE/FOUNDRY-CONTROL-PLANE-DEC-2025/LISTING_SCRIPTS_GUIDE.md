# Agent Listing Scripts - Usage Guide

Two scripts to list your agents and understand portal visibility.

## Scripts

### list_v2_agents.py
Lists **V2 agents** (current API) that show in the **NEW Microsoft Foundry portal** (ai.azure.com)

### list_v1_agents.py
Lists **V1 agents** (legacy API) that show in the **OLD Azure AI Foundry portal** only

---

## Quick Usage

```bash
# List V2 agents (new portal)
python list_v2_agents.py

# List V1 agents (old portal)
python list_v1_agents.py

# JSON output (for scripting)
python list_v2_agents.py --json
python list_v1_agents.py --json

# Detailed output (V2 only)
python list_v2_agents.py --detailed
```

---

## Example Output

### V2 Agents (Current)
```
======================================================================
V2 Agents (Current - New Portal)
======================================================================
Found 18 V2 agent(s):

#    Name                           ID                                     Model               
1    DataAnalysisAgent              DataAnalysisAgent                      gpt-4o
2    ResearchAgent                  ResearchAgent                          gpt-4o
...

Portal Visibility:
  Old Portal: ❌ These agents do NOT show in old portal
  New Portal: ✅ These agents show in https://ai.azure.com
```

### V1 Agents (Legacy)
```
======================================================================
V1 Agents (Legacy - Old Portal Only)
======================================================================
Found 21 V1 agent(s):

#    Name                           ID                                         Model            
1    assistant_agent                asst_qzCKIVj0jUxOlKIsZ9ZXsHkG              gpt-4.1          
2    CodeInterpreterAgent           asst_bC5iLuFFHoltXWzLkhMKZIDw              gpt-4.1-mini     
...

Portal Visibility:
  Old Portal: ✅ These agents show in old Azure AI Foundry portal
  New Portal: ❌ These agents do NOT show in https://ai.azure.com
```

---

## Understanding the Output

### V2 Agents
- **ID Format**: Human-readable agent names
- **Portal**: Show in https://ai.azure.com
- **API**: Created with `AIProjectClient.agents.create_agent()`
- **Status**: ✅ Current, recommended for all new work

### V1 Agents
- **ID Format**: `asst_XXXX...` (28 characters)
- **Portal**: Show in old Azure AI Foundry portal only
- **API**: Created with `AgentsClient.create_agent()`
- **Status**: ❌ Legacy, should be migrated

---

## Common Scenarios

### "I have too many V1 agents"
```bash
# List them
python list_v1_agents.py

# Clean them up
python cleanup_v1_agents.py
```

### "I want to see agent details"
```bash
# V2 agents with full details
python list_v2_agents.py --detailed
```

### "I need JSON for scripting"
```bash
# V2 agents as JSON
python list_v2_agents.py --json > v2_agents.json

# V1 agents as JSON
python list_v1_agents.py --json > v1_agents.json
```

### "Which agents show in the new portal?"
```bash
# These show in new portal (ai.azure.com)
python list_v2_agents.py
```

---

## Prerequisites

Both scripts require:
- Azure CLI authenticated: `az login`
- Environment variable: `AZURE_AI_PROJECT_ENDPOINT`

```bash
export AZURE_AI_PROJECT_ENDPOINT="https://xxx.services.ai.azure.com/api/projects/xxx"
```

---

## Next Steps

Based on what you find:

**If you have V1 agents:**
1. Recreate as V2: `python deploy_new_agents.py` or use samples
2. Delete V1: `python cleanup_v1_agents.py`

**If you have V2 agents:**
✅ You're good! They show in https://ai.azure.com

**If you have no agents:**
- Create some: `python agents/azure_ai_persistent_agent_v2.py`
- Or deploy samples: `python deploy_new_agents.py`

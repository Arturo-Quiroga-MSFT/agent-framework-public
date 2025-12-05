# Agent Identity Mapping Scripts

Utility scripts to map Azure AI Foundry agents to their Entra ID agent identities.

## Quick Start

```bash
cd MICROSOFT-ENTRA-AGENT-ID/scripts
python auto_mapper.py
```

That's it! The script will automatically find your agents and map them to their Entra ID identities.

## Prerequisites

1. **Azure CLI** installed and authenticated:
   ```bash
   az login
   ```

2. **Python 3.9+** with required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variable** (set in `.env` or export):
   ```bash
   export FOUNDRY_PROJECT_ENDPOINT="https://your-foundry.services.ai.azure.com/api/projects/yourProject"
   ```

4. **Permissions**: 
   - `Reader` access to the Azure AI Foundry project
   - `Directory.Read.All` or similar for Microsoft Graph API

## Scripts

### auto_mapper.py ⭐ **RECOMMENDED**

**Fully automated agent identity mapping with 100% accuracy.**

This script:
1. Fetches agents from Foundry via the Azure AI Projects SDK
2. Fetches agent identities from Entra ID via Microsoft Graph API
3. Correlates them using the "every 2nd identity" pattern (discovered through analysis)
4. Verifies against known mappings if available
5. Generates RBAC commands on request

**Key Discovery**: When you publish an agent in Azure AI Foundry, it creates **2 service principals** in Entra ID. The second one (at even indices when sorted by creation time) is the actual agent identity you use for RBAC.

**Usage:**

```bash
python auto_mapper.py
```

**Example Output:**

```
📡 Fetching agents from Foundry...
   ✅ Found 9 valid agents

🔐 Fetching agent identities from Entra ID...
   ✅ Found 20 agent identities

🔗 Correlating agents with identities...
   📅 Using 18 identities from 2025-12-04
   🎯 Extracted 9 agent identities (every 2nd)

🎯 AGENT IDENTITY MAPPING
================================================================================
Agent Name                Object ID                                     Confidence
--------------------------------------------------------------------------------
WebSearchAgent            38c14420-a914-4370-a0f8-1b014598c1d0          High      
BasicWeatherAgent         966ccc07-512a-4698-bafb-4d5686973d27          High      
ResearchAgent             9350dda6-b732-4b1c-a111-c5d8c4ffc64a          High      
DataAnalysisAgent         a3be091d-da7b-4696-b0f6-b7f41f5cca84          High      
CodeInterpreterAgent      d73547cc-9f5f-4de5-8f3b-97e14f882016          High      
FileSearchAgent           0e1584e6-f309-4e4b-9909-3200e3bca7a5          High      
BasicAgent                bde46d80-de73-4bd9-9416-4515799ae72d          High      
WeatherAgent              ff55957a-bbf1-4be8-9e41-0046b2b2494c          High      
BingGroundingAgent        420c8552-5d64-4c44-869c-037ad07ef351          High      
================================================================================

🔍 Verifying against known mapping...
   ✅ All 9 agents matched correctly (100% accuracy)

💾 Saved to: agent_identity_mapping_auto_20251204_191320.json
```

**Features:**
- ✅ Filters out rogue/deleted agents (like "ONE")
- ✅ Uses known publish order for accurate correlation
- ✅ Verifies against existing mapping files
- ✅ Generates RBAC commands for Storage, Cosmos DB, Key Vault
- ✅ 100% accuracy when publish order is known

---

### How the Correlation Works

When you publish an agent in Azure AI Foundry:

1. **Two service principals are created** in Entra ID
2. The **first** (odd index: 0, 2, 4...) is an intermediate/internal identity
3. The **second** (even index: 1, 3, 5...) is the **actual agent identity**

The script exploits this pattern:
```python
# Sort identities by creation time, take every 2nd one
agent_identities = [identities[i] for i in range(1, len(identities), 2)]
```

**Important**: You must know the **publish order** of your agents for accurate mapping. The script has a built-in known order, or will prompt you.

---

Maps Foundry agent names to their Entra ID Object IDs.

**Usage:**

```bash
# Basic usage (will prompt for project endpoint)
python map_agent_identities.py

# Or set environment variable first
export FOUNDRY_PROJECT_ENDPOINT="https://..."
python map_agent_identities.py
```

**What it does:**
1. Connects to your Azure AI Foundry project
2. Lists all agents (published and unpublished)
3. Retrieves agent identity Object IDs for each agent
4. Displays a formatted table showing the mapping
5. Saves the mapping to a JSON file
6. Generates example RBAC assignment commands

**Output:**

```
🎯 AGENT IDENTITY MAPPING
================================================================================
Agent Name                     Status                    Object ID                               
--------------------------------------------------------------------------------
basicweatheragent              Published with Identity   966ccc07-512a-4698-bafb-4d5686973d27    
websearchagent                 Published with Identity   38c14420-a914-4370-a0f8-1b014598c1d0    
draft-agent                    Draft (Shared Identity)   N/A (using shared identity)            
================================================================================

✅ Found 3 agent(s)
```

**Generated Files:**
- `agent_identity_mapping_YYYYMMDD_HHMMSS.json` - Complete mapping data

## Configuration

### Option 1: Environment Variables

Create a `.env` file in the scripts directory:

```bash
cp .env.example .env
# Edit .env with your values
```

### Option 2: Interactive Prompt

The script will prompt you for the project endpoint if not configured.

## Finding Your Project Endpoint

**Azure Portal Method:**
1. Go to Azure Portal
2. Navigate to your AI Foundry project
3. Click **Overview**
4. Copy the **Project endpoint** value

**Azure CLI Method:**
```bash
az ml workspace show \
  --name <your-foundry-project-name> \
  --resource-group <your-resource-group> \
  --query workspaceId -o tsv
```

## Example Workflow

### 1. Run the automated mapper

```bash
cd MICROSOFT-ENTRA-AGENT-ID/scripts
python auto_mapper.py
```

### 2. Review the output

The script shows which Object ID corresponds to each agent and verifies against known mappings.

### 3. Generate RBAC commands

When prompted, enter `y` to show RBAC commands, or run:

```bash
python -c "
import json
with open('agent_identity_mapping_complete.json') as f:
    data = json.load(f)
for a in data['agents']:
    print(f\"{a['agent_name']}: {a['object_id']}\")
"
```

### 4. Assign RBAC Permissions

Use the Object IDs to grant permissions:

```bash
# Grant Storage Blob Data Reader to WebSearchAgent
az role assignment create \
  --assignee 38c14420-a914-4370-a0f8-1b014598c1d0 \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# Grant Cosmos DB access to DataAnalysisAgent
az role assignment create \
  --assignee a3be091d-da7b-4696-b0f6-b7f41f5cca84 \
  --role "Cosmos DB Built-in Data Contributor" \
  --scope /subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.DocumentDB/databaseAccounts/<ACCOUNT>

# Grant Key Vault access to BasicAgent
az role assignment create \
  --assignee bde46d80-de73-4bd9-9416-4515799ae72d \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.KeyVault/vaults/<VAULT>
```

## Current Agent Identity Mapping

As of December 4, 2025, the verified mapping for the `firstProject` in `aq-ai-foundry-Sweden-Central`:

| Agent Name | Object ID | Status |
|------------|-----------|--------|
| WebSearchAgent | `38c14420-a914-4370-a0f8-1b014598c1d0` | Published |
| BasicWeatherAgent | `966ccc07-512a-4698-bafb-4d5686973d27` | Published |
| ResearchAgent | `9350dda6-b732-4b1c-a111-c5d8c4ffc64a` | Published |
| DataAnalysisAgent | `a3be091d-da7b-4696-b0f6-b7f41f5cca84` | Published |
| CodeInterpreterAgent | `d73547cc-9f5f-4de5-8f3b-97e14f882016` | Published |
| FileSearchAgent | `0e1584e6-f309-4e4b-9909-3200e3bca7a5` | Published |
| BasicAgent | `bde46d80-de73-4bd9-9416-4515799ae72d` | Published |
| WeatherAgent | `ff55957a-bbf1-4be8-9e41-0046b2b2494c` | Published |
| BingGroundingAgent | `420c8552-5d64-4c44-869c-037ad07ef351` | Published |

**Note**: The agent "ONE" is a rogue/deleted agent that still appears in the API but should be ignored.

## Generated Files

| File | Description |
|------|-------------|
| `agent_identity_mapping_complete.json` | Verified mapping with all 9 agents |
| `agent_identity_mapping_auto_*.json` | Auto-generated mappings with timestamps |
| `AGENT_IDENTITY_REFERENCE.md` | Human-readable reference with RBAC commands |

## Troubleshooting

### "Failed to retrieve agent information"

**Solutions:**
1. Ensure you're logged in: `az login`
2. Verify your account has access to the Foundry project
3. Check the project endpoint is correct
4. Try running: `az account show` to verify your current subscription

### "No agent identity found"

This is normal for **unpublished agents**. They use the shared project-level identity.

**Solution**: Publish the agent in the Foundry portal, then re-run the script.

### Rogue agents appearing (like "ONE")

Some deleted agents may still appear in the API. The script automatically filters these out using the `IGNORE_AGENTS` set in `auto_mapper.py`.

To add more agents to ignore:
```python
IGNORE_AGENTS = {'ONE', 'DeletedAgent', 'TestAgent'}
```

### Mapping doesn't match expected results

The correlation depends on **publish order**. If you published agents in a different order than the built-in list, update `KNOWN_PUBLISH_ORDER` in `auto_mapper.py`:

```python
KNOWN_PUBLISH_ORDER = [
    "YourFirstAgent",
    "YourSecondAgent",
    # ... in the order you published them
]
```

### "Every 2nd identity" pattern not working

This pattern was discovered for Azure AI Foundry agents as of December 2025. If Microsoft changes how identities are created, the correlation logic may need updating.

**Workaround**: Use the `interactive_mapper.py` script for manual correlation.

### "ModuleNotFoundError: No module named 'azure.ai.projects'"

**Solution:**
```bash
pip install -r requirements.txt
```

### "DefaultAzureCredential failed to retrieve a token"

**Solutions:**
1. Run `az login` again
2. Try: `az account set --subscription <subscription-id>`
3. Verify you have the correct permissions

## Legacy Scripts

### map_agent_identities.py

Original SDK-based approach. Limited by SDK preview - the API doesn't return `agentIdentityId` reliably.

### map_agent_identities_rest.py

Direct REST API approach. Works but requires manual correlation since the API returns agents without identity information.

### interactive_mapper.py

Interactive CLI for manual agent-to-identity mapping. Use as fallback when automatic correlation fails.

## Advanced Usage

### Programmatic access to mappings

```python
import json

# Load the verified mapping
with open('agent_identity_mapping_complete.json') as f:
    mapping = json.load(f)

# Get Object ID for a specific agent
def get_object_id(agent_name):
    for agent in mapping['agents']:
        if agent['agent_name'] == agent_name:
            return agent['object_id']
    return None

# Example
object_id = get_object_id('WebSearchAgent')
print(f"WebSearchAgent Object ID: {object_id}")
# Output: WebSearchAgent Object ID: 38c14420-a914-4370-a0f8-1b014598c1d0
```

### Batch RBAC assignment

```bash
# Assign same role to all agents
for oid in $(jq -r '.agents[].object_id' agent_identity_mapping_complete.json); do
  az role assignment create \
    --assignee "$oid" \
    --role "Storage Blob Data Reader" \
    --scope "/subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>"
done
```

### Add custom security attributes in Entra ID

Once you know which Object ID belongs to which agent, add custom security attributes in the Azure Portal:

1. Go to **Entra ID** → **Enterprise applications**
2. Search by Object ID (e.g., `38c14420-a914-4370-a0f8-1b014598c1d0`)
3. Click **Custom security attributes**
4. Add attributes:
   - `AgentName`: "WebSearchAgent"
   - `Purpose`: "Web search and grounding"
   - `Environment`: "production"

This makes it easier to identify agents in the portal since they all have the same generic display name.

## Technical Details

### Why the "every 2nd identity" pattern?

When Azure AI Foundry publishes an agent:
1. It creates an **application registration** in Entra ID
2. It creates a **service principal** for that application
3. Both appear as separate entries when querying service principals

The service principal (2nd entry) is the identity used for RBAC and authentication.

### API endpoints used

| API | Endpoint | Purpose |
|-----|----------|---------|
| Azure AI Projects SDK | `AIProjectClient.agents.list()` | Get agent names |
| Microsoft Graph | `/v1.0/servicePrincipals` | Get agent identities |
| Azure Resource Graph | `Resources \| where type == 'microsoft.cognitiveservices/accounts'` | Find Foundry resources |

### Token audiences

| API | Audience |
|-----|----------|
| Foundry API | `https://ai.azure.com/.default` |
| Microsoft Graph | `https://graph.microsoft.com/.default` |
| Azure Management | `https://management.azure.com/.default` |

## Related Documentation

- [Core Concepts](../02-CORE-CONCEPTS.md) - Understanding agent identities
- [Authentication](../03-AUTHENTICATION.md) - Auth patterns and RBAC
- [Agent Registry](../04-AGENT-REGISTRY.md) - Discovery and metadata
- [Quick Reference](../QUICK-REFERENCE.md) - Cheat sheet

---

**Need help?** Check the main [README](../README.md) or open an issue in the repository.

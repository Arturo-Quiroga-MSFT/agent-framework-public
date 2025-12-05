# Agent Identity Mapping Scripts

Utility scripts to map Azure AI Foundry agents to their Entra ID agent identities.

## Prerequisites

1. **Azure CLI** installed and authenticated:
   ```bash
   az login
   ```

2. **Python 3.9+** with required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Permissions**: You need at least `Reader` access to the Azure AI Foundry project

## Scripts

### auto_mapper.py ⭐ **RECOMMENDED - Fully Automated**

**The simplest way to map agents to their identities - zero manual work required!**

This script automatically discovers your workspace, queries both Foundry and Entra ID, and intelligently correlates agents with their identities using timestamp matching.

**Usage:**

```bash
# Just run it - that's it!
python auto_mapper.py

# Or with explicit endpoint
export FOUNDRY_PROJECT_ENDPOINT="https://..."
python auto_mapper.py
```

**What it does:**
1. 🔍 Automatically finds your workspace using Azure Resource Graph
2. 📡 Queries Foundry API for all published agents
3. 🔐 Queries Entra ID for all agent identities
4. 🔗 Correlates agents by creation timestamps
5. 🎯 Assigns confidence scores (High/Medium)
6. 💾 Saves complete mapping to JSON file

**Example Output:**

```
Agent Name                     Object ID                                Confidence   Time Diff
--------------------------------------------------------------------------------------------
WebSearchAgent                 38c14420-a914-4370-a0f8-1b014598c1d0     High         2m
BasicWeatherAgent              966ccc07-512a-4698-bafb-4d5686973d27     High         1m
ResearchAgent                  9350dda6-b732-4b1c-a111-c5d8c4ffc64a     High         3m

✅ Successfully mapped: 9 agents
💡 Confidence: High = created within 5 min, Medium = created further apart
```

**Why use this?**
- ✅ No manual correlation needed
- ✅ Handles any number of agents automatically
- ✅ Uses multiple Azure APIs for robustness
- ✅ Confidence scoring helps you verify accuracy
- ✅ Ready-to-use JSON output

---

### map_agent_identities.py (Legacy SDK Approach)

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

### 1. Run the automated mapper (easiest!)

```bash
cd MICROSOFT-ENTRA-AGENT-ID/scripts
python auto_mapper.py
```

The script automatically:
- Finds your workspace
- Gets all agents from Foundry
- Gets all identities from Entra ID
- Correlates them intelligently
- Saves mapping to JSON

### 2. Review the output

The script will show you which Object ID corresponds to each agent name.

### 3. Use Object IDs in Entra ID

Now you can:
- Search for specific Object IDs in the Entra ID portal
- Assign RBAC roles to specific agents
- Create conditional access policies
- Add custom security attributes for better labeling

### 4. Assign RBAC Permissions

Use the generated commands to grant permissions:

```bash
# Grant Storage access to basicweatheragent
az role assignment create \
  --assignee 966ccc07-512a-4698-bafb-4d5686973d27 \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>
```

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

## Advanced Usage

### Save mapping and use in other scripts

```python
import json

# Load the mapping
with open('agent_identity_mapping_20251204_123456.json') as f:
    mapping = json.load(f)

# Get Object ID for a specific agent
for agent in mapping['agents']:
    if agent['agent_name'] == 'basicweatheragent':
        object_id = agent['object_id']
        print(f"Object ID: {object_id}")
```

### Add custom attributes in Entra ID

Once you know which Object ID belongs to which agent, you can add custom security attributes in the Entra ID portal to make them easier to identify:

1. Go to Entra ID → Agent ID → Select the agent
2. Click **Custom security attributes**
3. Add attributes:
   - `AgentName`: "basicweatheragent"
   - `Purpose`: "Weather data retrieval"
   - `Environment`: "production"

## Related Documentation

- [Core Concepts](../02-CORE-CONCEPTS.md) - Understanding agent identities
- [Authentication](../03-AUTHENTICATION.md) - Auth patterns and RBAC
- [Implementation Guide](../06-IMPLEMENTATION-GUIDE.md) - Step-by-step setup

---

**Need help?** Check the main [README](../README.md) or review the [troubleshooting guide](../09-BEST-PRACTICES.md#troubleshooting).

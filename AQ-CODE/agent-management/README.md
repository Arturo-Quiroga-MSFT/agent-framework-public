# Azure AI Foundry Agent Management Scripts

**Last Updated:** November 26, 2025

This directory contains scripts and documentation for managing agents in Azure AI Foundry, including listing, creating, and deleting agents programmatically.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Available Scripts](#available-scripts)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

---

## Overview

Azure AI Foundry agents can be managed through:
1. **Azure Portal** - Manual, GUI-based management
2. **Python SDK** - Programmatic access via `azure-ai-projects`
3. **Azure CLI** - Limited support (authentication only)

This toolkit focuses on **Python SDK** methods for efficient bulk operations.

### 🔄 V1 (Classic) and V2 (New) Agent Support

**These scripts work with BOTH V1 (classic) and V2 (new) agents automatically!**

📖 **See [V1_VS_V2_AGENTS.md](./V1_VS_V2_AGENTS.md) for complete details on:**
- Differences between V1 (classic) and V2 (new) agents
- When to use each version
- Migration considerations
- API comparison tables
- Troubleshooting version-specific issues

---

## Prerequisites

### 1. Python Environment

```bash
# Python 3.9 or later required
python --version

# Install required packages
pip install azure-ai-projects azure-identity
```

### 2. Azure Authentication

**Option A: Azure CLI (Recommended for development)**
```bash
az login
az account show  # Verify logged in
```

**Option B: Service Principal**
```bash
export AZURE_CLIENT_ID="<your-client-id>"
export AZURE_CLIENT_SECRET="<your-client-secret>"
export AZURE_TENANT_ID="<your-tenant-id>"
```

**Option C: Managed Identity**
```bash
# Automatically works on Azure resources (VMs, Container Apps, Functions)
# No additional configuration needed
```

### 3. Environment Variables

```bash
# Required: Your Azure AI Foundry project endpoint
export AZURE_AI_PROJECT_ENDPOINT="https://<your-account>.services.ai.azure.com/api/projects/<your-project>"

# Optional: Default model for agent creation
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
```

**Finding Your Endpoint:**
1. Go to https://ai.azure.com
2. Select your project
3. Click on **"Project settings"** or **"Overview"**
4. Copy the **"Project endpoint"** URL

---

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `list_agents.py` | List all agents with details | `python list_agents.py` |
| `delete_agents.py` | Delete agents (all or specific) | `python delete_agents.py --all` |
| `check_agent_versions.py` | Check which agents are V1 vs V2 | `python check_agent_versions.py` |

**Note:** All scripts automatically support both V1 (classic) and V2 (new) agents.

---

## Quick Start

### Check Agent Versions (V1 vs V2)

```bash
# 1. Authenticate
az login

# 2. Set endpoint
export AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/your-project"

# 3. Check which agents are V1 (classic) vs V2 (new)
python check_agent_versions.py

# 4. Export version report to JSON
python check_agent_versions.py --output version-report.json
```

### Delete All Agents

```bash
# 1. Authenticate
az login

# 2. Set endpoint
export AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/your-project"

# 3. Dry run first (safe preview)
python delete_agents.py --all --dry-run

# 4. Delete all agents
python delete_agents.py --all
```

### Delete Specific Agents

```bash
# Delete single agent
python delete_agents.py --name "MyAgent"

# Delete multiple agents
python delete_agents.py --names "Agent1" "Agent2" "Agent3"
```

### List All Agents

```bash
python list_agents.py

# Export to JSON
python list_agents.py --output agents.json

# Show detailed information
python list_agents.py --verbose
```

---

## Detailed Usage

### `delete_agents.py`

**Full Command Reference:**

```bash
# Delete all agents
python delete_agents.py --all

# Delete all with dry-run (preview only)
python delete_agents.py --all --dry-run

# Delete specific agent by name
python delete_agents.py --name "WeatherAgent"

# Delete multiple specific agents
python delete_agents.py --names "Agent1" "Agent2" "Agent3"

# Show help
python delete_agents.py --help
```

**Arguments:**

| Argument | Type | Description |
|----------|------|-------------|
| `--all` | flag | Delete all agents in the project |
| `--name` | string | Delete a specific agent by name |
| `--names` | list | Delete multiple agents by name |
| `--dry-run` | flag | Preview what would be deleted without actually deleting |

**Examples:**

```bash
# Example 1: Safe preview
$ python delete_agents.py --all --dry-run
Found 5 agent(s):
  - WeatherAgent (version: 1)
  - ResearchAgent (version: 2)
  - CodeAgent (version: 1)
  - SalesAgent (version: 1)
  - SupportAgent (version: 3)

[DRY RUN] No agents were deleted.

# Example 2: Delete all
$ python delete_agents.py --all
Found 5 agent(s):
  - WeatherAgent (version: 1)
  - ResearchAgent (version: 2)
  - CodeAgent (version: 1)
  - SalesAgent (version: 1)
  - SupportAgent (version: 3)

Deleting agents...
✓ Deleted: WeatherAgent
✓ Deleted: ResearchAgent
✓ Deleted: CodeAgent
✓ Deleted: SalesAgent
✓ Deleted: SupportAgent

Completed: 5/5 agents deleted successfully.

# Example 3: Delete specific agents
$ python delete_agents.py --names "TestAgent1" "TestAgent2"
Deleting 2 agent(s)...
✓ Deleted: TestAgent1
✓ Deleted: TestAgent2

Completed: 2/2 agents deleted successfully.
```

---

### `list_agents.py`

**Full Command Reference:**

```bash
# List all agents (basic)
python list_agents.py

# Detailed view with tools and instructions
python list_agents.py --verbose

# Export to JSON
python list_agents.py --output agents.json

# Export to YAML
python list_agents.py --output agents.yaml

# Filter by name pattern
python list_agents.py --filter "Test*"

# Show only agent names
python list_agents.py --names-only
```

**Arguments:**

| Argument | Type | Description |
|----------|------|-------------|
| `--verbose` | flag | Show detailed information (instructions, tools, metadata) |
| `--output` | path | Export agents to JSON or YAML file |
| `--filter` | pattern | Filter agents by name pattern (supports wildcards) |
| `--names-only` | flag | Show only agent names (useful for scripting) |

**Example Output:**

```bash
$ python list_agents.py
=== Azure AI Foundry Agents ===
Project: https://myproject.services.ai.azure.com/api/projects/demo

Total Agents: 3

1. WeatherAgent (version: 1)
   Model: gpt-4o
   Created: 2025-11-25 10:30:15
   Tools: 1 (FunctionTool)

2. ResearchAgent (version: 2)
   Model: gpt-4o-mini
   Created: 2025-11-26 08:15:42
   Tools: 3 (FileSearch, BingGrounding, CodeInterpreter)

3. SalesAgent (version: 1)
   Model: gpt-4o
   Created: 2025-11-26 14:20:33
   Tools: 0
```

**Verbose Output:**

```bash
$ python list_agents.py --verbose
=== Azure AI Foundry Agents ===

Agent: WeatherAgent
  Version: 1
  ID: agent_abc123
  Model: gpt-4o
  Created: 2025-11-25 10:30:15
  Instructions:
    You are a helpful weather assistant. Provide accurate weather
    information for any location requested by the user.
  Tools:
    - FunctionTool: get_weather
      Description: Get current weather for a location
  Metadata:
    department: customer-service
    owner: john.doe@company.com

---

[... additional agents ...]
```

---

### `create_agent.py`

**Full Command Reference:**

```bash
# Create simple agent
python create_agent.py --name "MyAgent" --instructions "You are helpful"

# Create agent with specific model
python create_agent.py --name "MyAgent" --model "gpt-4o"

# Create agent with tools
python create_agent.py --name "CodeAgent" --tools code-interpreter file-search

# Create from configuration file
python create_agent.py --config agent_config.yaml

# Create multiple agents from directory
python create_agent.py --config-dir ./agent-configs/
```

**Arguments:**

| Argument | Type | Description |
|----------|------|-------------|
| `--name` | string | Agent name (required) |
| `--instructions` | string | Agent instructions/system prompt |
| `--model` | string | Model deployment name (default: from env var) |
| `--tools` | list | Tools to enable (code-interpreter, file-search, etc.) |
| `--config` | path | Create from YAML/JSON configuration file |
| `--config-dir` | path | Create multiple agents from config directory |

**Example Configuration File (`agent_config.yaml`):**

```yaml
name: WeatherAgent
instructions: |
  You are a helpful weather assistant. Provide accurate weather
  information for any location requested by the user.
model: gpt-4o
tools:
  - type: function
    function:
      name: get_weather
      description: Get current weather for a location
      parameters:
        type: object
        properties:
          location:
            type: string
            description: City name or coordinates
        required:
          - location
metadata:
  department: customer-service
  version: "1.0"
```

---

### `export_agents.py`

**Full Command Reference:**

```bash
# Export all agents to JSON
python export_agents.py --output agents.json

# Export all agents to YAML
python export_agents.py --output agents.yaml

# Export specific agents
python export_agents.py --names "Agent1" "Agent2" --output selected.json

# Pretty print format
python export_agents.py --output agents.json --pretty

# Include full metadata
python export_agents.py --output agents.json --include-metadata
```

**Use Cases:**
- Backup agent configurations
- Version control for agent definitions
- Migrate agents between projects
- Documentation and auditing

---

## API Reference

### Python SDK Core Methods

#### **Client Initialization**

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Initialize client
client = AIProjectClient(
    endpoint="https://your-project.services.ai.azure.com/api/projects/your-project",
    credential=DefaultAzureCredential()
)
```

#### **List Agents**

```python
# List all agents
agents = client.agents.list_agents()

for agent in agents:
    print(f"Name: {agent.name}, Version: {agent.version}")
```

#### **Get Agent Details**

```python
# Get specific agent by name (latest version)
agent = client.agents.get_agent("MyAgent")

# Get specific version
agent = client.agents.get_version(
    agent_name="MyAgent",
    agent_version="1"
)
```

#### **Create Agent**

```python
from azure.ai.projects.models import PromptAgentDefinition

agent = client.agents.create_version(
    agent_name="MyAgent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="You are a helpful assistant"
    )
)
```

#### **Delete Agent**

```python
# Delete all versions of an agent
client.agents.delete_agent("MyAgent")

# Delete specific version
client.agents.delete_version(
    agent_name="MyAgent",
    agent_version="1"
)
```

#### **Update Agent**

```python
# Create new version (versioning is automatic)
updated_agent = client.agents.create_version(
    agent_name="MyAgent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="Updated instructions"
    )
)
# This creates version 2 automatically
```

---

## Troubleshooting

### Common Issues

#### **Issue: "AZURE_AI_PROJECT_ENDPOINT environment variable not set"**

**Solution:**
```bash
export AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/your-project"
```

#### **Issue: "Authentication failed"**

**Solution:**
```bash
# Re-authenticate with Azure CLI
az login
az account show

# Or check service principal credentials
echo $AZURE_CLIENT_ID
echo $AZURE_TENANT_ID
```

#### **Issue: "ClientAuthenticationError: DefaultAzureCredential failed to retrieve a token"**

**Solution:**
Try explicit authentication:
```python
from azure.identity import AzureCliCredential

# Use Azure CLI credential explicitly
credential = AzureCliCredential()
```

#### **Issue: "Agent not found"**

**Causes:**
- Agent was already deleted
- Wrong agent name (case-sensitive)
- Wrong project endpoint

**Solution:**
```bash
# List all agents to verify name
python list_agents.py --names-only
```

#### **Issue: "ResourceNotFoundError: The specified resource does not exist"**

**Solution:**
Verify your project endpoint is correct:
```bash
# Check endpoint format
echo $AZURE_AI_PROJECT_ENDPOINT

# Should be: https://<account>.services.ai.azure.com/api/projects/<project>
```

#### **Issue: Permission denied / Forbidden**

**Solution:**
Ensure you have the correct RBAC role:
- **Azure AI Developer** - Full access
- **Azure AI Inference Deployment Operator** - Limited access

```bash
# Check your roles in Azure Portal
# Navigate to: AI Foundry Project → Access Control (IAM) → Role assignments
```

---

## Examples

### Example 1: Bulk Delete Test Agents

```bash
# Delete all agents starting with "Test"
python delete_agents.py --names $(python list_agents.py --filter "Test*" --names-only)
```

### Example 2: Backup Before Deletion

```bash
# 1. Export all agents to backup
python export_agents.py --output backup_$(date +%Y%m%d).json

# 2. Delete all agents
python delete_agents.py --all

# 3. Restore if needed
python create_agent.py --config backup_20251126.json
```

### Example 3: Clean Up Old Versions

```python
#!/usr/bin/env python3
"""Delete old agent versions, keep only latest."""

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

# Group agents by name
agents_by_name = {}
for agent in client.agents.list_agents():
    if agent.name not in agents_by_name:
        agents_by_name[agent.name] = []
    agents_by_name[agent.name].append(agent)

# Delete all but the latest version
for name, versions in agents_by_name.items():
    if len(versions) > 1:
        # Sort by version (assuming numeric)
        sorted_versions = sorted(versions, key=lambda a: int(a.version))
        
        # Keep last, delete rest
        for agent in sorted_versions[:-1]:
            print(f"Deleting old version: {name} v{agent.version}")
            client.agents.delete_version(
                agent_name=agent.name,
                agent_version=agent.version
            )
```

### Example 4: Automated Agent Lifecycle

```python
#!/usr/bin/env python3
"""Automated agent lifecycle management."""

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import os

def cleanup_old_agents(days_old: int = 30):
    """Delete agents older than specified days."""
    client = AIProjectClient(
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential()
    )
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    for agent in client.agents.list_agents():
        # Check if agent has creation timestamp in metadata
        created = agent.created_at  # Assuming this field exists
        
        if created and created < cutoff_date:
            print(f"Deleting old agent: {agent.name} (created: {created})")
            client.agents.delete_agent(agent.name)

if __name__ == "__main__":
    cleanup_old_agents(days_old=30)
```

### Example 5: Agent Migration Between Projects

```bash
# Export from Project A
export AZURE_AI_PROJECT_ENDPOINT="https://project-a.services.ai.azure.com/api/projects/proj-a"
python export_agents.py --output project_a_agents.json

# Import to Project B
export AZURE_AI_PROJECT_ENDPOINT="https://project-b.services.ai.azure.com/api/projects/proj-b"
python create_agent.py --config project_a_agents.json
```

---

## Advanced Usage

### Programmatic Agent Management

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import PromptAgentDefinition
import os

class AgentManager:
    """High-level agent management interface."""
    
    def __init__(self):
        self.client = AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
    
    def list_all(self):
        """List all agents."""
        return list(self.client.agents.list_agents())
    
    def delete_all(self, confirm: bool = True):
        """Delete all agents with optional confirmation."""
        agents = self.list_all()
        
        if confirm:
            response = input(f"Delete {len(agents)} agents? (yes/no): ")
            if response.lower() != "yes":
                print("Cancelled.")
                return
        
        for agent in agents:
            self.client.agents.delete_agent(agent.name)
            print(f"Deleted: {agent.name}")
    
    def delete_by_pattern(self, pattern: str):
        """Delete agents matching name pattern."""
        import fnmatch
        
        agents = self.list_all()
        matching = [a for a in agents if fnmatch.fnmatch(a.name, pattern)]
        
        print(f"Found {len(matching)} agents matching '{pattern}'")
        for agent in matching:
            self.client.agents.delete_agent(agent.name)
            print(f"Deleted: {agent.name}")
    
    def create_batch(self, agent_configs: list):
        """Create multiple agents from config list."""
        created = []
        
        for config in agent_configs:
            agent = self.client.agents.create_version(
                agent_name=config["name"],
                definition=PromptAgentDefinition(
                    model=config.get("model", "gpt-4o"),
                    instructions=config.get("instructions", "")
                )
            )
            created.append(agent)
            print(f"Created: {agent.name}")
        
        return created

# Usage
manager = AgentManager()

# List all
agents = manager.list_all()
print(f"Total agents: {len(agents)}")

# Delete by pattern
manager.delete_by_pattern("Test*")

# Create batch
configs = [
    {"name": "Agent1", "instructions": "You are Agent 1"},
    {"name": "Agent2", "instructions": "You are Agent 2"},
]
manager.create_batch(configs)
```

---

## Best Practices

### 1. Always Use Dry Run First

```bash
# Preview before deleting
python delete_agents.py --all --dry-run
```

### 2. Export Before Bulk Operations

```bash
# Backup configurations
python export_agents.py --output backup_$(date +%Y%m%d_%H%M%S).json
```

### 3. Use Naming Conventions

```
<environment>-<purpose>-<version>
Examples:
  - prod-weather-agent-v1
  - dev-test-agent-v2
  - staging-sales-agent-v1
```

### 4. Tag Agents with Metadata

```python
agent = client.agents.create_version(
    agent_name="MyAgent",
    definition=PromptAgentDefinition(
        model="gpt-4o",
        instructions="...",
        metadata={
            "environment": "production",
            "owner": "team-ai",
            "created_by": "deployment-pipeline",
            "version": "1.0.0"
        }
    )
)
```

### 5. Implement Soft Deletion

Instead of immediate deletion, tag agents as deprecated:
```python
# Tag as deprecated instead of deleting
agent = client.agents.get_agent("OldAgent")
client.agents.update(
    agent_name=agent.name,
    metadata={**agent.metadata, "status": "deprecated", "deprecated_at": "2025-11-26"}
)
```

---

## Security Considerations

### 1. Credential Management

**❌ Never hardcode credentials:**
```python
# BAD - Don't do this
credential = ClientSecretCredential(
    tenant_id="hardcoded-tenant",
    client_id="hardcoded-client",
    client_secret="hardcoded-secret"
)
```

**✅ Use environment variables or managed identity:**
```python
# GOOD
credential = DefaultAzureCredential()  # Handles multiple auth methods
```

### 2. Least Privilege Access

Assign minimal necessary RBAC roles:
- **Development**: Azure AI Developer
- **Production**: Azure AI Inference Deployment Operator (read-only)

### 3. Audit Logging

Enable Azure Monitor logs for agent operations:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log all operations
logger.info(f"Deleting agent: {agent_name}")
client.agents.delete_agent(agent_name)
logger.info(f"Successfully deleted: {agent_name}")
```

---

## Related Resources

### Documentation
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)
- [Azure AI Projects SDK Reference](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects)
- [Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)

### Parent Documentation
- [Azure AI Ecosystem Guide](../../docs/AZURE_AI_ECOSYSTEM_GUIDE.md) - Complete guide to Azure AI components

### Code Samples
- [Azure AI Samples](../../python/samples/getting_started/agents/azure_ai/) - Getting started examples
- [Workflow Samples](../../workflow-samples/) - Advanced multi-agent patterns

---

## Support

For issues or questions:

1. **GitHub Issues**: [microsoft/agent-framework](https://github.com/microsoft/agent-framework/issues)
2. **Azure Support**: [Azure Portal Support](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)
3. **Documentation**: [Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-foundry/)

---

**Document Version:** 1.0  
**Last Updated:** November 26, 2025  
**Maintained by:** Azure AI Team

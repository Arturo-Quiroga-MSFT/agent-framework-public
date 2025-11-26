# Quick Start Guide

Get started with Azure AI Foundry agent management in 5 minutes.

---

## 1. Install Dependencies

```bash
pip install azure-ai-projects azure-identity
```

## 2. Authenticate with Azure

```bash
az login
```

## 3. Set Your Project Endpoint

```bash
# Copy your endpoint from: https://ai.azure.com → Your Project → Settings
export AZURE_AI_PROJECT_ENDPOINT="https://your-account.services.ai.azure.com/api/projects/your-project"
```

## 4. List Your Agents

```bash
python list_agents.py
```

## 5. Delete Agents

```bash
# Preview first (safe)
python delete_agents.py --all --dry-run

# Delete all agents
python delete_agents.py --all

# Or delete specific agents
python delete_agents.py --names "TestAgent1" "TestAgent2"
```

---

## Common Commands

```bash
# List all agents
python list_agents.py

# List with details
python list_agents.py --verbose

# Export to JSON
python list_agents.py --output backup.json

# Delete specific agent
python delete_agents.py --name "MyAgent"

# Delete all test agents
python list_agents.py --filter "Test*" --names-only | xargs -I {} python delete_agents.py --name "{}"
```

---

## Troubleshooting

### "AZURE_AI_PROJECT_ENDPOINT not set"

```bash
export AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/your-project"
```

### "Authentication failed"

```bash
az login
az account show  # Verify you're logged in
```

### "Package not found"

```bash
pip install --upgrade azure-ai-projects azure-identity
```

---

For detailed documentation, see [README.md](./README.md)

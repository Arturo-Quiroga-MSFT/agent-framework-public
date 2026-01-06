# ✅ SOLUTION: Correct Setup for Handoff Workflows with Azure AI Foundry

## The Correct Pattern

For **handoff workflows with HandoffBuilder** using Azure AI Foundry, use this pattern:

### Cell 3: Correct Imports
```python
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
```

### Cell 7: Correct Client Initialization
```python
# AzureOpenAIChatClient automatically reads AZURE_AI_PROJECT_ENDPOINT and 
# AZURE_AI_MODEL_DEPLOYMENT_NAME from environment variables
chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
```

## Why This Matters

Based on the official MAF v2 handoff examples (`/maf-upstream/python/samples/getting_started/workflows/orchestration/`):

- ✅ **`AzureOpenAIChatClient`**: For handoff workflows, multi-agent orchestration
- ❌ **`AzureAIClient`**: For single-agent scenarios (NOT for handoff workflows)
- ✅ **`AzureCliCredential`**: Standard authentication for samples (inherits from `az login`)
- ⚠️ **Agent names**: Use hyphens (e.g., `travel-agent`), NOT underscores

## Reference Examples

Your notebook should follow this pattern from `handoff_simple.py`:

```python
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Initialize the client (automatically reads AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME)
chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())

# Create agents
triage_agent = chat_client.create_agent(
    instructions="You are frontline support triage...",
    name="triage-agent",  # Note: Use hyphens, not underscores
)

# Build handoff workflow
workflow = (
    HandoffBuilder(
        name="customer_support_handoff",
        participants=[triage_agent, specialist1, specialist2],
    )
    .set_coordinator(triage_agent)
    .build()
)
```

## Environment Variables Required

```bash
AZURE_AI_PROJECT_ENDPOINT=https://your-project.api.azureml.ms
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1
```

## After the Fix

1. Restart the kernel
2. Re-run all cells
3. It should work! ✅

## Summary

- **Wrong**: `AzureAIClient` → causes "model must be provided" errors
- **Correct**: `AzureOpenAIChatClient` → works with HandoffBuilder

The error you're seeing ("model must be provided when creating a new response") happens because `AzureAIClient` doesn't properly pass the model configuration to the handoff workflow agents.

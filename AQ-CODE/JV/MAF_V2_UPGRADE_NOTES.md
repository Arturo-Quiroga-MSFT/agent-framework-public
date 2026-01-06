# MAF v2 Handoff Workflow Setup for Jason's Travel Agent Demo

## Correct Pattern for Handoff Workflows

For multi-agent handoff orchestration with Azure AI Foundry, use this pattern:

### Correct Implementation ✅
```python
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# AzureOpenAIChatClient automatically reads environment variables:
# - AZURE_AI_PROJECT_ENDPOINT
# - AZURE_AI_MODEL_DEPLOYMENT_NAME
chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())

# Create agents with hyphenated names
travel_agent = chat_client.create_agent(
    instructions="You are a friendly travel agent...",
    name="travel-agent",  # ✅ Use hyphens, not underscores
)

# Build handoff workflow
workflow = (
    HandoffBuilder(
        name="travel_support",
        participants=[travel_agent, specialist1, specialist2],
    )
    .set_coordinator(travel_agent)
    .build()
)
```

### Why This Pattern?

Based on official MAF v2 examples (`/maf-upstream/python/samples/getting_started/workflows/orchestration/`):

- ✅ **`AzureOpenAIChatClient`**: Designed for handoff workflows with `HandoffBuilder`
- ✅ **`AzureCliCredential`**: Standard authentication (inherits from `az login`)
- ✅ **Auto-configuration**: Reads `AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` from environment
- ✅ **Agent naming**: Must use hyphens (e.g., `travel-agent`), not underscores

## Updated Environment Variables

| Old Variable | New Variable |
|--------------|--------------|
| `PROJECT_ENDPOINT` | `AZURE_AI_PROJECT_ENDPOINT` |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | `AZURE_AI_MODEL_DEPLOYMENT_NAME` |

## What You Need to Do

1. **Create/Update `.env` file:**
   ```bash
   AZURE_AI_PROJECT_ENDPOINT=https://your-project-name.api.azureml.ms
   AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
   ```

2. **Authenticate with Azure:**
   ```bash
   az login
   ```

3. **Run the notebook** - It should now work without connection errors!

## Why This Fix Works

The error you saw (`ValueError: No default connection found for type: AzureOpenAI`) was because the old pattern tried to find a "default" Azure OpenAI connection in your project. 

The new MAF v2 pattern doesn't rely on predefined connections - it just needs your project endpoint and model deployment name, and it automatically handles all the connection logic internally.

## References

- MAF v2 examples: `/maf-upstream/python/samples/getting_started/agents/azure_ai/`
- Basic example: `azure_ai_basic.py`
- Environment variables reference: `.env` in the examples folder

## Questions?

This is the current recommended pattern for all Azure AI Foundry projects using MAF. The v1 pattern is deprecated.

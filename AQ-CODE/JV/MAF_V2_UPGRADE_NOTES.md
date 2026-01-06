# MAF v2 Upgrade Notes for Jason's Travel Agent Demo

## What Changed

Your notebook has been updated to use the **Microsoft Agent Framework v2 (MAF v2)** API, which is simpler and more reliable than v1.

## Key Differences

### Old Pattern (MAF v1) ❌
```python
from agent_framework.azure import AzureOpenAIChatClient
from azure.ai.projects import AIProjectClient

project_client = AIProjectClient(endpoint=..., credential=...)
connection = project_client.connections.get_default(connection_type="AzureOpenAI")
chat_client = AzureOpenAIChatClient.from_connection(connection=connection, model=...)
```

**Problems:**
- Required `get_default(connection_type="AzureOpenAI")` which could fail if no default connection exists
- More complex multi-step initialization
- Required explicit connection management

### New Pattern (MAF v2) ✅
```python
from agent_framework.azure import AzureAIClient

chat_client = AzureAIClient(
    credential=DefaultAzureCredential(),
    project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    model_deployment_name=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
)
```

**Benefits:**
- ✅ One-line initialization
- ✅ No connection management needed
- ✅ Automatically discovers project resources using just the endpoint
- ✅ More robust and simpler to use

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

# Azure AI Samples - Environment Configuration Update

## Summary

All Azure AI agent samples in `/python/samples/getting_started/agents/azure_ai/` have been updated to load environment variables from a centralized `.env` file located at `/python/samples/getting_started/agents/.env`.

## Changes Made

### 1. Added dotenv Loading Pattern

All 14 Python samples now include:

```python
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the agents directory
load_dotenv(Path(__file__).parent.parent / ".env")
```

### 2. Updated Documentation

Each sample's docstring now includes clear prerequisites:

```python
"""
[Sample Description]

Prerequisites:
- Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME in .env file
- Run 'az login' for Azure CLI authentication
"""
```

### 3. Files Modified

All 14 Azure AI samples were updated:

1. ✅ `azure_ai_basic.py` - Basic agent usage
2. ✅ `azure_ai_with_azure_ai_search.py` - Azure AI Search integration  
3. ✅ `azure_ai_with_bing_grounding.py` - Bing web search integration
4. ✅ `azure_ai_with_code_interpreter.py` - Code interpreter tool
5. ✅ `azure_ai_with_existing_agent.py` - Reusing existing agents
6. ✅ `azure_ai_with_existing_thread.py` - Reusing conversation threads
7. ✅ `azure_ai_with_explicit_settings.py` - Explicit configuration
8. ✅ `azure_ai_with_file_search.py` - File search capabilities
9. ✅ `azure_ai_with_function_tools.py` - Custom function tools
10. ✅ `azure_ai_with_hosted_mcp.py` - Hosted MCP integration
11. ✅ `azure_ai_with_local_mcp.py` - Local MCP integration
12. ✅ `azure_ai_with_multiple_tools.py` - Multiple tool types
13. ✅ `azure_ai_with_openapi_tools.py` - OpenAPI tool integration
14. ✅ `azure_ai_with_thread.py` - Thread management

## Environment File Structure

The `.env` file at `/python/samples/getting_started/agents/.env` contains:

### Required Variables
- `AZURE_AI_PROJECT_ENDPOINT` - Your Azure AI project endpoint URL
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` - Deployed model name (e.g., gpt-4, gpt-4.1)

### Optional Variables  
- `BING_CONNECTION_ID` - For web search samples
- Tracing/observability settings (ENABLE_CONSOLE_TRACING, ENABLE_AZURE_AI_TRACING, etc.)
- Weather API key for optional real weather data

## Benefits

1. **Centralized Configuration** - All samples share one .env file
2. **Security** - Sensitive values not hardcoded in samples
3. **Ease of Use** - Users only need to configure once
4. **Consistency** - All samples follow the same pattern
5. **Flexibility** - Easy to switch between different Azure AI projects

## Usage

To run any sample:

1. Ensure `.env` file is configured with your Azure AI project details
2. Run `az login` to authenticate with Azure
3. Execute the sample: `python azure_ai_basic.py`

## Testing

Verified that environment variables load correctly:
```
✓ AZURE_AI_PROJECT_ENDPOINT loaded successfully
✓ AZURE_AI_MODEL_DEPLOYMENT_NAME loaded successfully
```

## Next Steps

Consider applying the same pattern to other sample directories:
- `/python/samples/getting_started/agents/openai/`
- `/python/samples/getting_started/agents/azure_openai/`
- Other agent provider samples

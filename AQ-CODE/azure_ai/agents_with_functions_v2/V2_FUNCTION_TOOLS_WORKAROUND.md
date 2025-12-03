# Azure AI Agents V2 Function Tools - Known Issue & Workaround

## Overview

When using the **Microsoft Agent Framework (MAF)** with **Azure AI Agents V2** (`AzureAIClient` from `azure-ai-projects`), you may encounter a `UnicodeDecodeError` when creating agents with function tools.

This document explains the issue, provides the workaround, and links to the official GitHub issue.

---

## The Problem

### Error Message
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b in position 0: invalid start byte
```

### Root Cause
The Azure AI Foundry service returns **gzip-compressed responses** (`Content-Encoding: gzip/br/deflate`), but the `azure-core` SDK's `ContentDecodePolicy` attempts to decode the raw compressed bytes as UTF-8 text, resulting in the decode error.

### Affected Components
- **SDK Version**: `azure-ai-projects 2.0.0b2` (beta)
- **Azure Core**: `1.36.0`
- **Agent Framework**: `1.0.0b251120`
- **Affected Operations**: `agents.create_version()` and other API calls

### Why No V2 Function Tool Samples?
This is likely why the MAF team has not yet released official samples for V2 agents with function tools - the bug blocks basic functionality.

---

## Official GitHub Issue

**Issue #2457**: Python: Registration of Agents v2 in AI Foundry fails because of compressed HTTP errors

🔗 **Link**: https://github.com/microsoft/agent-framework/issues/2457

Opened: November 25, 2025  
Status: Open (as of December 2025)

---

## The Workaround

Add the following code **at the top of your Python file**, before importing `AzureAIClient`:

```python
# ============================================================================
# WORKAROUND for azure-ai-projects 2.0.0b2 gzip encoding bug
# GitHub Issue: https://github.com/microsoft/agent-framework/issues/2457
# This patches the Azure SDK to disable compressed responses which cause
# UnicodeDecodeError when the SDK tries to decode gzip bytes as UTF-8
# ============================================================================
import azure.core.pipeline.policies as policies

_original_on_request = policies.HeadersPolicy.on_request

def _patched_on_request(self, request):
    _original_on_request(self, request)
    request.http_request.headers['Accept-Encoding'] = 'identity'

policies.HeadersPolicy.on_request = _patched_on_request
# ============================================================================
```

### How It Works
The patch sets the `Accept-Encoding: identity` header on all requests, which tells the Azure service to return uncompressed responses that the SDK can properly decode.

---

## Complete Working Example

```python
import asyncio
import os
from typing import Annotated
from pydantic import Field

# WORKAROUND - Must be applied BEFORE importing AzureAIClient
import azure.core.pipeline.policies as policies
_original_on_request = policies.HeadersPolicy.on_request
def _patched_on_request(self, request):
    _original_on_request(self, request)
    request.http_request.headers['Accept-Encoding'] = 'identity'
policies.HeadersPolicy.on_request = _patched_on_request

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is sunny with a high of 25°C."


async def main() -> None:
    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="WeatherAgent",
            instructions="You are a helpful weather assistant.",
            tools=[get_weather],
        ) as agent,
    ):
        result = await agent.run("What's the weather in Seattle?")
        print(f"Agent: {result}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Environment Setup

Ensure you have the following environment variable set:

```bash
# Required - Get from Azure AI Foundry portal
export AZURE_AI_PROJECT_ENDPOINT="https://your-ai-services.services.ai.azure.com/api/projects/your-project"

# Required - Your model deployment name
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"
```

And authenticate via Azure CLI:
```bash
az login
```

---

## When Will This Be Fixed?

The fix will likely come in a future release of `azure-ai-projects` or `azure-core`. Monitor the GitHub issue for updates:

🔗 https://github.com/microsoft/agent-framework/issues/2457

Once fixed, you can remove the workaround patch from your code.

---

## V1 vs V2 API Comparison

| Feature | V1 (Legacy) | V2 (Current) |
|---------|-------------|--------------|
| Client Class | `AzureAIAgentClient` | `AzureAIClient` |
| Package | `azure-ai-agents` | `azure-ai-projects` |
| Function Tools | ✅ Working | ⚠️ Requires workaround |
| Status | Deprecated | Active development |

---

## Files Using This Workaround

In this repository:
- `azure_ai_with_function_tools_v2.py` - Function tools demo
- `azure_ai_with_multiple_tools_v2.py` - Function + MCP + Web Search demo

---

## Questions?

If you encounter issues or have questions:
1. Check the GitHub issue for updates
2. Review the MAF documentation
3. Ensure you're using the correct endpoint format from Azure AI Foundry

---

*Document created: December 2, 2025*  
*Author: Arturo Quiroga*

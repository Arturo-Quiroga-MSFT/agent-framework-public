# Agent Environment Variables - The Complete Guide

**Date**: January 6, 2026  
**Purpose**: Clarify the confusing environment variable naming across Microsoft Agent Framework

---

## ⚠️ The Confusion

Microsoft's documentation shows **different variable names** than what the actual code uses. This can cause your agents to fail with "missing configuration" errors.

## The Three Agent Types & Their Variables

### 1️⃣ Azure AI Agent (`AzureAIClient` or `AzureAIAgentClient`)

**Service**: Azure AI Agents Service (Azure AI Foundry backend)  
**Chat History**: Service-managed only

```bash
AZURE_AI_PROJECT_ENDPOINT="https://your-ai-services.services.ai.azure.com/api/projects/your-project"
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"
```

**Sources**:
- ✅ [Microsoft Docs](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-ai-foundry-agent)
- ✅ MAF samples use these names consistently

---

### 2️⃣ Azure OpenAI Chat Completion (`AzureOpenAIChatClient`)

**Service**: Azure OpenAI Chat Completion API  
**Chat History**: Custom/client-managed only

#### What Microsoft Docs Say:
```bash
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o"  # ✅ Uses CHAT_DEPLOYMENT
AZURE_OPENAI_API_VERSION="2024-10-21"       # Optional
```

#### What MAF Samples Actually Use:
```bash
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o"  # ✅ CONFIRMED in source code
```

**Sources**:
- 📖 [Microsoft Docs](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-openai-chat-completion-agent)
- ✅ Verified in `maf-upstream/python/samples/getting_started/agents/azure_openai/azure_chat_client_with_explicit_settings.py`

---

### 3️⃣ Azure OpenAI Responses (`AzureOpenAIResponsesClient`)

**Service**: Azure OpenAI Responses API  
**Chat History**: Both service-managed AND custom

#### What Microsoft Docs Say:
```bash
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME="gpt-4o"  # ✅ Uses RESPONSES_DEPLOYMENT
AZURE_OPENAI_API_VERSION="2024-10-21"             # Optional
```

#### What MAF Samples Actually Use:
```bash
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME="gpt-4o"  # ✅ CONFIRMED in source code
```

**Sources**:
- 📖 [Microsoft Docs](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-openai-responses-agent)
- ✅ Verified in `maf-upstream/python/samples/getting_started/agents/azure_openai/azure_responses_client_with_explicit_settings.py`

---

## 🎯 Recommended .env File Structure

```bash
# ========================================
# Azure AI Agent (AzureAIClient)
# ========================================
AZURE_AI_PROJECT_ENDPOINT="https://your-ai-services.services.ai.azure.com/api/projects/your-project"
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o"

# ========================================
# Azure OpenAI Chat Completion (AzureOpenAIChatClient)
# ========================================
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o"
AZURE_OPENAI_API_VERSION="2024-10-21"

# ========================================
# Azure OpenAI Responses (AzureOpenAIResponsesClient)
# ========================================
# Uses same AZURE_OPENAI_ENDPOINT as above
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME="gpt-4o"

# ========================================
# Authentication
# ========================================
# Run 'az login' in terminal (preferred)
# OR set AZURE_OPENAI_API_KEY (not recommended for production)
```

---

## 🔍 Why Different Variable Names?

Each client type uses a **specific** deployment variable name to allow you to:
1. **Use different models** for different agent types
2. **Separate configurations** in the same project
3. **Avoid conflicts** when using multiple agent types

Example:
```bash
# Use GPT-4 for chat completions
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4"

# Use GPT-4o for responses (faster, cheaper)
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME="gpt-4o"
```

---

## ✅ Quick Verification Script

Use this to check your environment variables:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(Path.cwd() / '.env')

print("=== Azure AI Agent ===")
print(f"AZURE_AI_PROJECT_ENDPOINT: {os.getenv('AZURE_AI_PROJECT_ENDPOINT', '❌ Not set')}")
print(f"AZURE_AI_MODEL_DEPLOYMENT_NAME: {os.getenv('AZURE_AI_MODEL_DEPLOYMENT_NAME', '❌ Not set')}")

print("\n=== Azure OpenAI Chat Completion ===")
print(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT', '❌ Not set')}")
print(f"AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: {os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME', '❌ Not set')}")

print("\n=== Azure OpenAI Responses ===")
print(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT', '❌ Not set')}")
print(f"AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME: {os.getenv('AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME', '❌ Not set')}")
```

---

## 🚨 Common Errors

### Error: "Missing deployment configuration"
**Cause**: Using wrong variable name  
**Solution**: Check you're using the correct variable for your client type:
- `AzureOpenAIChatClient` → `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`
- `AzureOpenAIResponsesClient` → `AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME`

### Error: "Missing project endpoint"
**Cause**: Using Azure OpenAI variables for Azure AI Agent  
**Solution**: Azure AI Agent needs `AZURE_AI_PROJECT_ENDPOINT`, not `AZURE_OPENAI_ENDPOINT`

---

## 📚 Reference Links

- [Azure AI Foundry Agent](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-ai-foundry-agent?pivots=programming-language-python)
- [Azure OpenAI Chat Completion Agent](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-openai-chat-completion-agent?pivots=programming-language-python)
- [Azure OpenAI Responses Agent](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-openai-responses-agent?pivots=programming-language-python)
- [MAF GitHub Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/agents)

---

## Summary Table

| Agent Type | Client Class | Endpoint Variable | Deployment Variable |
|-----------|--------------|------------------|---------------------|
| Azure AI Agent | `AzureAIClient` | `AZURE_AI_PROJECT_ENDPOINT` | `AZURE_AI_MODEL_DEPLOYMENT_NAME` |
| Azure OpenAI Chat | `AzureOpenAIChatClient` | `AZURE_OPENAI_ENDPOINT` | `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` |
| Azure OpenAI Responses | `AzureOpenAIResponsesClient` | `AZURE_OPENAI_ENDPOINT` | `AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME` |

**Bottom Line**: Each agent type uses **specific** variable names - don't mix them up! 🎯

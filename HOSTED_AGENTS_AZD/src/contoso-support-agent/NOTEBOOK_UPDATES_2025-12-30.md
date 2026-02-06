# Hosted Agents E2E Demo Notebook - Updates Summary

**Date**: December 30, 2025  
**Based on**: Official Microsoft documentation and samples

## Overview

The notebook has been updated to reflect the latest MAF V2 architecture and official Azure AI Foundry hosted agents patterns, based on:

1. **MAF V2 GitHub**: https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/agents/azure_ai
2. **Hosted Agents Docs**: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents
3. **Foundry Samples**: https://github.com/azure-ai-foundry/foundry-samples/tree/hosted-agents/pyaf-samples

## Key Changes

### 1. MAF V2 Client Pattern ✅

**Old Approach**:
```python
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient

agent = ChatAgent(
    chat_client=AzureOpenAIChatClient(
        endpoint=...,
        api_key=...,
    ),
    ...
)
```

**New Approach (V2)**:
```python
from agent_framework.azure import AzureAIClient
from azure.identity import AzureCliCredential

client = AzureAIClient(
    endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    credential=AzureCliCredential(),
)

agent = client.create_agent(
    model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
    instructions="...",
    name="ContosoSupportAgent",
    use_latest_version=True  # Reuse existing agent
)
```

### 2. Official Hosting Adapter ✅

**Package Installation**:
```bash
pip install azure-ai-agentserver-core
pip install azure-ai-agentserver-agentframework
```

**Usage**:
```python
from azure.ai.agentserver.agentframework import from_azure_ai_agent

# Transform agent into hosted service with one line
server = from_azure_ai_agent(agent, client=client)

# Run locally (automatically creates REST endpoints)
server.run(host="0.0.0.0", port=8088)
```

**Benefits**:
- ✅ One-line deployment
- ✅ Auto protocol translation (Foundry ↔ MAF)
- ✅ Built-in OpenTelemetry tracing
- ✅ Streaming support (SSE)
- ✅ Enterprise features (CORS, auth flows)

### 3. Thread-Based Conversations ✅

**V2 Conversation Pattern**:
```python
# Run with thread-based conversation management
run = await client.agents.run(
    agent=agent,
    messages=[{"role": "user", "content": message}],
    # Optional: thread_id="..." to continue conversation
)

response = run.output_text
```

### 4. Updated Dockerfile ✅

**Key Improvements**:
```dockerfile
FROM python:3.11-slim

# Health check for Foundry
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8088/health')"

# Uses app.py with hosting adapter
CMD ["python", "app.py"]
```

### 5. requirements.txt with Official Packages ✅

```txt
# Azure AI Projects SDK V2
azure-ai-projects>=2.0.0b1

# Hosting adapter packages
azure-ai-agentserver-core
azure-ai-agentserver-agentframework

# MAF packages
agent-framework
agent-framework-azure

# Core dependencies
azure-identity>=1.15.0
python-dotenv>=1.0.0

# Optional: OpenTelemetry
opentelemetry-api
opentelemetry-sdk
azure-monitor-opentelemetry
```

### 6. Azure Developer CLI (azd) Deployment ✅

**New azd ai agent Extension**:

```bash
# Install/update azd
curl -fsSL https://aka.ms/install-azd.sh | bash

# Initialize with starter template
azd init -t https://github.com/Azure-Samples/azd-ai-starter-basic

# OR connect to existing project
azd ai agent init --project-id /subscriptions/.../projects/...

# Create agent.yaml configuration
azd ai agent init -m agent.yaml

# Deploy everything (provision + build + deploy)
azd up
```

**agent.yaml Structure**:
```yaml
name: contoso-support-agent
version: 1.0
description: Contoso Electronics customer support agent

image:
  registry: yourregistry.azurecr.io
  repository: contoso-support-agent
  tag: v1

resources:
  cpu: "1"
  memory: "2Gi"

scaling:
  minReplicas: 1
  maxReplicas: 3

protocols:
  - name: responses
    version: v1

environment:
  - name: AZURE_AI_PROJECT_ENDPOINT
    value: "${AZURE_AI_PROJECT_ENDPOINT}"

tools:
  - type: code_interpreter
  - type: web_search
```

### 7. REST API Endpoints

**Hosting Adapter Automatically Provides**:

- `POST /responses` - Main agent interaction (Foundry Responses API)
- `GET /health` - Health check
- SSE streaming support
- OpenTelemetry traces
- Conversation management

**Example Request**:
```bash
curl -X POST http://localhost:8088/responses \
  -H 'Content-Type: application/json' \
  -d '{
    "input": {
      "messages": [
        {"role": "user", "content": "What warranty comes with laptops?"}
      ]
    }
  }'
```

## Updated Environment Variables

```bash
# New V2 variables
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# For containerization
ACR_NAME=yourregistry
FOUNDRY_ACCOUNT_NAME=your-foundry-account
```

## Complete Workflow (5 Stages)

### Stage 1: DEVELOP with MAF V2 ✅
- Use `AzureAIClient` instead of direct chat client
- Create agents with `client.create_agent()`
- Test locally with thread-based conversations

### Stage 2: ADAPT for Hosting ✅
- Install official hosting adapter packages
- Transform agent with `from_azure_ai_agent()`
- Test locally on `localhost:8088`

### Stage 3: CONTAINERIZE ✅
- Create Dockerfile with health checks
- Include hosting adapter in requirements.txt
- Build and test container locally

### Stage 4: DEPLOY to Foundry ✅
- Create `agent.yaml` configuration
- Use `azd ai agent init -m agent.yaml`
- Deploy with `azd up` (all-in-one)

### Stage 5: PUBLISH (Optional) ✅
- Web app preview (automatic)
- Microsoft Teams integration
- Microsoft 365 Copilot integration
- Stable REST API endpoint

## References

### Documentation
- [Hosted Agents Concepts](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry&tabs=cli)
- [MAF V2 Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/agents/azure_ai)
- [Foundry Samples](https://github.com/azure-ai-foundry/foundry-samples/tree/hosted-agents/pyaf-samples)

### Key Samples to Reference
1. **azure_ai_basic.py** - Simple agent creation with V2
2. **azure_ai_with_thread.py** - Thread management
3. **azure_ai_use_latest_version.py** - Agent reuse pattern
4. **Hosted agent samples** - Complete deployment examples

## Next Steps for Notebook Enhancement

1. **Add Conversation Management Examples** ⏭️
   - Show thread creation and reuse
   - Demonstrate conversation persistence
   - Multi-turn conversation patterns

2. **Add Observability Section** ⏭️
   - OpenTelemetry tracing setup
   - Application Insights integration
   - Local tracing with AI Toolkit

3. **Add Tools Integration** ⏭️
   - Code Interpreter
   - Web Search
   - Custom MCP tools

4. **Add Evaluation Examples** ⏭️
   - Azure AI Evaluation SDK
   - Intent resolution metrics
   - Task adherence evaluation

## Breaking Changes from Previous Version

1. ❌ **Removed**: Flask-based custom REST API
   ✅ **Replaced with**: Official hosting adapter

2. ❌ **Removed**: Direct `AzureOpenAIChatClient` instantiation
   ✅ **Replaced with**: `AzureAIClient` wrapper (V2 pattern)

3. ❌ **Removed**: Manual endpoint configuration
   ✅ **Replaced with**: Project-level endpoint from Azure AI

4. ❌ **Removed**: `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`
   ✅ **Replaced with**: `AZURE_AI_PROJECT_ENDPOINT` + managed identity

## Important Notes

- ⚠️ **Package Availability**: Some packages are in preview. Check availability on PyPI or private feeds.
- ⚠️ **Region Availability**: Hosted agents currently in **North Central US** only during preview.
- ⚠️ **Preview Limitations**: Max 2 min replicas, 5 max replicas during preview.
- ⚠️ **Authentication**: Use `AzureCliCredential()` for local development, `DefaultAzureCredential()` for production.

## Testing the Updated Notebook

1. **Install Required Packages**:
   ```bash
   pip install azure-ai-projects>=2.0.0b1
   pip install azure-ai-agentserver-core
   pip install azure-ai-agentserver-agentframework
   pip install agent-framework agent-framework-azure
   ```

2. **Update .env File**:
   ```bash
   AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
   AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
   ```

3. **Authenticate**:
   ```bash
   az login
   ```

4. **Run Notebook Cells Sequentially**:
   - Stage 1: Creates agent with V2 client
   - Stage 2: Tests hosting adapter locally
   - Stage 3: Generates container files
   - Stage 4: Provides deployment scripts
   - Stage 5: Shows publishing options

## Conclusion

The notebook now reflects the **official, production-ready approach** for deploying MAF agents to Azure AI Foundry Hosted Agents service. The updates align with Microsoft's documented best practices and leverage the official hosting adapter for seamless Foundry integration.

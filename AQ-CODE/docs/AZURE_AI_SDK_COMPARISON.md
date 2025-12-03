# Azure AI Projects SDK vs Azure AI Agents SDK Comparison

> **Last Updated:** December 2025  
> **Source Documentation:**  
> - [azure-ai-projects](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python-preview)  
> - [azure-ai-agents](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python-preview)

## Overview

Both SDKs are part of Microsoft's Azure AI Foundry ecosystem for building AI agents, but they serve different purposes and have different scopes.

| Aspect | azure-ai-projects | azure-ai-agents |
|--------|------------------|-----------------|
| **Version (as of Dec 2025)** | 2.0.0b2 (preview) | 1.2.0b6 (preview) |
| **Package Install** | `pip install --pre azure-ai-projects` | `pip install azure-ai-agents` |
| **Scope** | Comprehensive SDK for all AI Foundry operations | Agent-focused SDK specifically for agent operations |

---

## Key Differences

### 1. Client Architecture

**azure-ai-projects:**
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
) as project_client:
    # Access agents via property
    agents_client = project_client.agents
    
    # Access other resources
    deployments = project_client.deployments.list()
    connections = project_client.connections.list()
```

**azure-ai-agents (standalone):**
```python
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```

### 2. Feature Scope

| Feature | azure-ai-projects | azure-ai-agents |
|---------|:-----------------:|:---------------:|
| Agent Creation & Management | ✅ | ✅ |
| Agent Tools (File Search, Code Interpreter, etc.) | ✅ | ✅ |
| Deployments Management | ✅ | ❌ |
| Connections Management | ✅ | ❌ |
| Datasets Operations | ✅ | ❌ |
| Indexes Operations | ✅ | ❌ |
| Evaluations | ✅ | ❌ |
| Fine-tuning | ✅ | ❌ |
| Memory Stores | ✅ | ❌ |
| Red Team Scans | ✅ | ❌ |
| Integrated OpenAI Client | ✅ (`get_openai_client()`) | ❌ |
| Tracing/Telemetry | ✅ | ✅ |

---

## Available Agent Tools (Both SDKs)

### Built-in Tools
- **File Search** - RAG with vector stores
- **Code Interpreter** - Python execution in sandbox
- **Bing Grounding** - Real-time web search
- **Azure AI Search** - Enterprise search integration
- **Function Tools** - Custom function calls
- **MCP (Model Context Protocol)** - External tool integration
- **Browser Automation** - Playwright-based web automation
- **Deep Research** - In-depth topic research
- **OpenAPI** - REST endpoint integration
- **Connected Agents** - Multi-agent orchestration
- **Azure Functions** - Serverless function integration
- **Logic Apps** - Workflow integration
- **Fabric** - Microsoft Fabric data integration

### Connection-Based Tools (azure-ai-projects specific patterns)
- Bing Custom Search
- SharePoint
- Agent-to-Agent (A2A)
- Image Generation
- Computer Use
- Web Search Preview
- Memory Search

---

## Use Case Recommendations

### Use `azure-ai-projects` when:
1. **Building production applications** requiring full AI Foundry access
2. **Managing multiple resources** (deployments, connections, datasets, indexes)
3. **Running evaluations** on agents or GenAI applications
4. **Working with fine-tuning** operations
5. **Managing memory stores** for agent conversations
6. **Need integrated OpenAI client** for Responses API
7. **Comprehensive project management** is required

### Use `azure-ai-agents` when:
1. **Only agent capabilities** are needed without project management
2. **Simple agent-focused prototypes** with minimal dependencies
3. **Lighter dependency footprint** is preferred
4. **Migrating existing code** that uses standalone agent patterns

---

## Microsoft's Official Recommendation

From the azure-ai-agents documentation:

> *"While this package can be used independently, we recommend using the Azure AI Projects client library (azure-ai-projects) for an enhanced experience. The Projects library provides simplified access to advanced functionality, such as creating and managing agents, enumerating AI models, working with datasets and managing search indexes, evaluating generative AI performance, and enabling OpenTelemetry tracing."*

---

## Code Examples

### Creating an Agent with azure-ai-projects

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        credential=credential
    ) as project_client,
):
    # Get OpenAI client for responses
    with project_client.get_openai_client() as openai_client:
        # Create agent
        agent = project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="You are a helpful assistant",
            ),
        )
        
        # Create conversation
        conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": "Hello!"}],
        )
        
        # Get response
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",
        )
        print(response.output_text)
```

### Creating an Agent with azure-ai-agents

```python
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents
    
    # Create agent
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful agent",
    )
    
    # Create thread
    thread = agents_client.threads.create()
    
    # Create message
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, tell me a joke"
    )
    
    # Run and process
    run = agents_client.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )
```

### Adding Tools Example (Both patterns support similar tools)

```python
from azure.ai.agents import FileSearchTool, CodeInterpreterTool, FunctionTool

# File Search
file_search = FileSearchTool(vector_store_ids=[vector_store.id])

# Code Interpreter
code_interpreter = CodeInterpreterTool(file_ids=[file.id])

# Function Tool
functions = FunctionTool(user_functions)

# Create agent with tools
agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are helpful agent",
    tools=file_search.definitions,
    tool_resources=file_search.resources,
)
```

---

## Prerequisites (Both SDKs)

1. **Python 3.9 or later**
2. **Azure subscription**
3. **Azure AI Foundry project**
4. **Entra ID authentication** (DefaultAzureCredential)
5. **Appropriate RBAC role assignments**
6. **Azure CLI** installed and logged in (`az login`)

---

## Environment Variables

```bash
# For azure-ai-projects
export AZURE_AI_PROJECT_ENDPOINT="https://your-ai-services.services.ai.azure.com/api/projects/your-project"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="your-model-deployment"

# For azure-ai-agents (can use same or slightly different)
export PROJECT_ENDPOINT="https://your-ai-services.services.ai.azure.com/api/projects/your-project"
export MODEL_DEPLOYMENT_NAME="your-model-deployment"
```

---

## Related Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Azure AI Projects SDK Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples)
- [Azure AI Agents SDK Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples)
- [AI Starter Template](https://aka.ms/azsdk/azure-ai-agents/python/ai-starter-template)

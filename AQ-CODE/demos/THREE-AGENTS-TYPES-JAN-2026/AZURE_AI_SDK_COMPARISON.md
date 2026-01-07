# Azure AI Projects SDK vs Azure AI Agents SDK Comparison

> **Last Updated:** January 6, 2026  
> **Source Documentation:**  
> - [azure-ai-projects Microsoft Learn](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python-preview)  
> - [azure-ai-agents Microsoft Learn](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python-preview)  
> - [azure-ai-projects GitHub README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/README.md)

## Overview

Both SDKs are part of Microsoft's **Microsoft Foundry** (formerly Azure AI Studio, now also called Azure AI Foundry) ecosystem for building AI agents, but they serve different purposes and have different scopes.

> **Note:** Azure AI Studio has been rebranded to Microsoft Foundry. You may see both names in documentation and code samples.

| Aspect | azure-ai-projects | azure-ai-agents |
|--------|------------------|-----------------||
| **Version (as of Jan 2026)** | 2.0.0b3 (preview) | 1.2.0b6 (preview) |
| **Package Install** | `pip install --pre azure-ai-projects` | `pip install azure-ai-agents` |
| **REST API Version** | [`2025-11-15-preview`](https://aka.ms/azsdk/azure-ai-projects-v2/api-reference-2025-11-15-preview) | - |
| **Scope** | Comprehensive SDK for all Microsoft Foundry operations | Agent-focused SDK specifically for agent operations |

---

## Prerequisites

Both SDKs require:
- **Python 3.9 or later**
- **Azure subscription**
- **Microsoft Foundry project** (create via [Azure Portal](https://learn.microsoft.com/azure/ai-studio/how-to/create-projects))
- **Project endpoint URL** of the form `https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name`
  - Found in your Microsoft Foundry Project overview page
  - Store in environment variable `AZURE_AI_PROJECT_ENDPOINT`
- **Entra ID authentication** with appropriate role assignment (via "Access Control (IAM)" tab)
  - See [RBAC in Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-ai-foundry)
- **Azure CLI** installed and authenticated (`az login`)
- **Model deployment** configured (deployment name stored in `AZURE_AI_MODEL_DEPLOYMENT_NAME`)

---

## Installation

```bash
# Install azure-ai-projects (preview version)
pip install --pre azure-ai-projects

# Install azure-ai-agents
pip install azure-ai-agents

# Additional required packages for azure-ai-projects
pip install openai azure-identity

# Optional: for async support
pip install aiohttp

# Optional: for tracing with Azure Monitor
pip install "azure-ai-projects>=2.0.0b1" azure-identity opentelemetry-sdk \
            azure-core-tracing-opentelemetry azure-monitor-opentelemetry
pip install opentelemetry-exporter-otlp
```

---

## Key Differences

### 1. Client Architecture

**azure-ai-projects:**
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        credential=credential
    ) as project_client,
):
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
| Image Generation Tool | ✅ | ❌ |
| Web Search Tool | ✅ | ❌ |
| Computer Use Tool | ✅ | ❌ |
| Memory Search Tool | ✅ | ❌ |
| Deployments Management | ✅ | ❌ |
| Connections Management | ✅ | ❌ |
| Datasets Operations | ✅ | ❌ |
| Indexes Operations | ✅ | ❌ |
| Evaluations (Evals API) | ✅ (Built-in evaluators: violence, fluency, task_adherence, etc.) | ❌ |
| Fine-tuning | ✅ | ❌ |
| Memory Stores | ✅ | ❌ |
| Red Team Scans | ✅ | ❌ |
| Integrated OpenAI Client | ✅ (`get_openai_client()`) | ❌ |
| Responses & Conversations API | ✅ | ❌ |
| Files Operations | ✅ (Upload, retrieve, list, delete via OpenAI client) | ❌ |
| Fine-tuning Operations | ✅ (SFT, RFT, DPO support) | ❌ |
| Tracing/Telemetry | ✅ (OpenTelemetry + Azure Monitor) | ✅ (OpenTelemetry) |

---

## Available Agent Tools (Both SDKs)

### Built-in Tools (azure-ai-projects v2)
- **File Search** - RAG with vector stores
- **Code Interpreter** - Python execution in sandbox
- **Image Generation** - Generate images from text prompts
- **Web Search** - General web search
- **Computer Use** - Direct computer system interaction
- **MCP (Model Context Protocol)** - External tool integration
- **OpenAPI** - REST endpoint integration
- **Function Tool** - Custom function calls
- **Memory Search Tool** - Agent memory management with scoped storage (e.g., per-user isolation using `scope` parameter)

### Built-in Tools (azure-ai-agents v1)
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

### Connection-Based Tools (azure-ai-projects v2)
- **Azure AI Search** - Enterprise search integration
- **Bing Grounding** - Real-time web search with connections
- **Bing Custom Search** - Domain-specific search
- **Microsoft Fabric** - Fabric data queries
- **SharePoint** - SharePoint document search
- **Browser Automation** - Playwright-based automation
- **MCP with Project Connection** - MCP with connection auth
- **Agent-to-Agent (A2A)** - Multi-agent collaboration
- **OpenAPI with Project Connection** - REST APIs with connection auth

---

## Use Case Recommendations

### Use `azure-ai-projects` when:
1. **Building production applications** requiring full Microsoft Foundry access
2. **Managing multiple resources** (deployments, connections, datasets, indexes)
3. **Running evaluations** on agents or GenAI applications
4. **Working with fine-tuning** operations
5. **Managing memory stores** for agent conversations
6. **Need integrated OpenAI client** for Responses, Conversations, Evals API
7. **Comprehensive project management** is required
8. **Using latest Agent capabilities** (Image Generation, Web Search, Computer Use, Memory Search)
9. **Need Red Team scanning** for security assessment

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

### Using Responses API (Multi-turn conversations without agents)

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
    with project_client.get_openai_client() as openai_client:
        # First turn
        response = openai_client.responses.create(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            input="What is the size of France in square miles?",
        )
        print(f"Response output: {response.output_text}")
        
        # Second turn (maintains context)
        response = openai_client.responses.create(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            input="And what is the capital city?",
            previous_response_id=response.id,  # Links responses for context
        )
        print(f"Response output: {response.output_text}")
```

### Creating an Agent with azure-ai-projects (v2.0.0b3)

```python
import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
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
        # Create agent version
        agent = project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="You are a helpful assistant",
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
        
        # Create conversation with initial message
        conversation = openai_client.conversations.create(
            items=[{"type": "message", "role": "user", "content": "What is the size of France in square miles?"}],
        )
        print(f"Created conversation (id: {conversation.id})")
        
        # Get response using agent reference
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",  # Input is empty when using conversation context
        )
        print(f"Response output: {response.output_text}")
        
        # Add another message to the conversation
        openai_client.conversations.items.create(
            conversation_id=conversation.id,
            items=[{"type": "message", "role": "user", "content": "And what is the capital city?"}],
        )
        
        # Get another response
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",
        )
        print(f"Response output: {response.output_text}")
        
        # Cleanup
        openai_client.conversations.delete(conversation_id=conversation.id)
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
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
# For azure-ai-projects (v2.0.0b3)
export AZURE_AI_PROJECT_ENDPOINT="https://your-ai-services.services.ai.azure.com/api/projects/your-project"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="your-model-deployment"

# For azure-ai-agents (v1.2.0b6 - can use same or slightly different)
export PROJECT_ENDPOINT="https://your-ai-services.services.ai.azure.com/api/projects/your-project"
export MODEL_DEPLOYMENT_NAME="your-model-deployment"
```

---

## Tracing and Observability

### azure-ai-projects Tracing

The azure-ai-projects SDK supports comprehensive tracing with OpenTelemetry and Azure Monitor:

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Enable Azure Monitor tracing
connection_string = project_client.telemetry.get_application_insights_connection_string()
configure_azure_monitor(connection_string=connection_string)

# Create custom spans
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("my_scenario"):
    # Your agent operations here
    pass
```

**Environment Variables:**
- `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` - Enable content recording (captures prompts/responses)
- `AZURE_TRACING_GEN_AI_INSTRUMENT_RESPONSES_API=false` - Disable automatic instrumentation
- `AZURE_TRACING_GEN_AI_INCLUDE_BINARY_DATA=true` - Include binary data (images) in traces

**Installation:**
```bash
pip install "azure-ai-projects>=2.0.0b1" azure-identity opentelemetry-sdk \
            azure-core-tracing-opentelemetry azure-monitor-opentelemetry
pip install opentelemetry-exporter-otlp  # For OTLP export (Aspire Dashboard, etc.)
```

**Important:** To view traces in Microsoft Foundry portal, pass the agent ID in response generation requests.

### azure-ai-agents Tracing

The azure-ai-agents SDK also supports OpenTelemetry tracing but does not include the Azure Monitor integration helper methods.

---

## Additional azure-ai-projects Capabilities

### Files Operations
Upload, retrieve, list, and delete files for fine-tuning and agent operations:

```python
with project_client.get_openai_client() as openai_client:
    # Upload file
    with open(file_path, "rb") as f:
        uploaded_file = openai_client.files.create(file=f, purpose="fine-tune")
    
    # Wait for processing
    processed_file = openai_client.files.wait_for_processing(uploaded_file.id)
    
    # Retrieve file content
    file_content = openai_client.files.content(processed_file.id)
    
    # Delete file
    openai_client.files.delete(processed_file.id)
```

### Fine-tuning Operations
Support for multiple fine-tuning methods (SFT, RFT, DPO):

```python
with project_client.get_openai_client() as openai_client:
    # Create supervised fine-tuning job
    fine_tuning_job = openai_client.fine_tuning.jobs.create(
        training_file=train_file.id,
        validation_file=validation_file.id,
        model=model_name,
        method={
            "type": "supervised",
            "supervised": {
                "hyperparameters": {
                    "n_epochs": 3,
                    "batch_size": 1,
                    "learning_rate_multiplier": 1.0
                }
            }
        },
        extra_body={"trainingType": "GlobalStandard"}
    )
```

### Dataset Operations
Upload and manage datasets:

```python
# Upload single file and create dataset
dataset = project_client.datasets.upload_file(
    name=dataset_name,
    version=dataset_version,
    file_path=data_file,
    connection_name=connection_name,
)

# Upload folder
dataset = project_client.datasets.upload_folder(
    name=dataset_name,
    version=dataset_version_2,
    folder=data_folder,
    connection_name=connection_name,
)
```

### Evaluation Operations
Built-in evaluators for AI quality assessment:

```python
with project_client.get_openai_client() as openai_client:
    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "violence_detection",
            "evaluator_name": "builtin.violence",
            "data_mapping": {"query": "{{item.query}}", "response": "{{sample.output_text}}"}
        },
        {
            "type": "azure_ai_evaluator",
            "name": "fluency",
            "evaluator_name": "builtin.fluency",
            "initialization_parameters": {"deployment_name": model_deployment_name},
            "data_mapping": {"query": "{{item.query}}", "response": "{{sample.output_text}}"}
        }
    ]
    
    eval_object = openai_client.evals.create(
        name="Agent Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
```

---

## Related Resources

- [Microsoft Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Azure AI Projects SDK Samples (v2)](https://aka.ms/azsdk/azure-ai-projects-v2/python/samples/)
- [Azure AI Agents SDK Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples)
- [Azure AI Projects API Reference](https://aka.ms/azsdk/azure-ai-projects-v2/python/api-reference)
- [Azure AI Projects REST API](https://aka.ms/azsdk/azure-ai-projects-v2/api-reference-2025-11-15-preview)
- [Azure AI Projects GitHub README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/README.md) (Updated 4 hours ago)
- [Azure AI Projects SDK Source Code](https://aka.ms/azsdk/azure-ai-projects-v2/python/code)
- [Azure AI Projects Release History](https://aka.ms/azsdk/azure-ai-projects-v2/python/release-history)

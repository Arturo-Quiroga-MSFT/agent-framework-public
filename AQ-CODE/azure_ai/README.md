# Azure AI Agent Examples

This folder contains examples demonstrating different ways to create and use agents with the Azure AI chat client from the `agent_framework.azure` package.

## Examples

| File | Description |
|------|-------------|
| [`azure_ai_basic.py`](azure_ai_basic.py) | The simplest way to create an agent using `ChatAgent` with `AzureAIAgentClient`. It automatically handles all configuration using environment variables. |
| [`azure_ai_with_bing_grounding.py`](azure_ai_with_bing_grounding.py) | Shows how to use Bing Grounding search with Azure AI agents to find real-time information from the web. Demonstrates web search capabilities with proper source citations and comprehensive error handling. |
| [`azure_ai_with_code_interpreter.py`](azure_ai_with_code_interpreter.py) | Shows how to use the HostedCodeInterpreterTool with Azure AI agents to write and execute Python code. Includes helper methods for accessing code interpreter data from response chunks. |
| [`azure_ai_with_existing_agent.py`](azure_ai_with_existing_agent.py) | Shows how to work with a pre-existing agent by providing the agent ID to the Azure AI chat client. This example also demonstrates proper cleanup of manually created agents. |
| [`azure_ai_with_existing_thread.py`](azure_ai_with_existing_thread.py) | Shows how to work with a pre-existing thread by providing the thread ID to the Azure AI chat client. This example also demonstrates proper cleanup of manually created threads. |
| [`azure_ai_with_explicit_settings.py`](azure_ai_with_explicit_settings.py) | Shows how to create an agent with explicitly configured `AzureAIAgentClient` settings, including project endpoint, model deployment, credentials, and agent name. |
| [`azure_ai_with_file_search.py`](azure_ai_with_file_search.py) | Demonstrates how to use the HostedFileSearchTool with Azure AI agents to search through uploaded documents. Shows file upload, vector store creation, and querying document content. Includes both streaming and non-streaming examples. |
| [`azure_ai_with_function_tools.py`](azure_ai_with_function_tools.py) | Demonstrates how to use function tools with agents. Shows both agent-level tools (defined when creating the agent) and query-level tools (provided with specific queries). |
| [`azure_ai_with_hosted_mcp.py`](azure_ai_with_hosted_mcp.py) | Shows how to integrate Azure AI agents with hosted Model Context Protocol (MCP) servers for enhanced functionality and tool integration. Demonstrates remote MCP server connections and tool discovery. |
| [`azure_ai_with_local_mcp.py`](azure_ai_with_local_mcp.py) | Shows how to integrate Azure AI agents with local Model Context Protocol (MCP) servers for enhanced functionality and tool integration. Demonstrates both agent-level and run-level tool configuration. |
| [`azure_ai_with_multiple_tools.py`](azure_ai_with_multiple_tools.py) | Demonstrates how to use multiple tools together with Azure AI agents, including web search, MCP servers, and function tools. Shows coordinated multi-tool interactions and approval workflows. |
| [`azure_ai_with_openapi_tools.py`](azure_ai_with_openapi_tools.py) | Demonstrates how to use OpenAPI tools with Azure AI agents to integrate external REST APIs. Shows OpenAPI specification loading, anonymous authentication, thread context management, and coordinated multi-API conversations using weather and countries APIs. |
| [`azure_ai_with_thread.py`](azure_ai_with_thread.py) | Demonstrates thread management with Azure AI agents, including automatic thread creation for stateless conversations and explicit thread management for maintaining conversation context across multiple interactions. |

## DevUI Gallery (azure_agents/)

A collection of ready-to-use Azure AI agents for interactive testing via DevUI. These agents showcase various Azure AI capabilities in a user-friendly interface.

### Available Agents

| Agent | Description | Key Features |
|-------|-------------|--------------|
| **weather_agent_basic** | Real-time weather queries using OpenWeatherMap API | Function tools, external API integration |
| **weather_agent_functions** | Multi-tool weather and time information | Multiple function tools, coordinated queries |
| **bing_grounding_agent** | Web search with real-time information | HostedWebSearchTool, source citations |
| **code_interpreter_agent** | Python code execution for data analysis | HostedCodeInterpreterTool, computational tasks |
| **code_interpreter_agent_with_images** | Enhanced code execution with automatic plot extraction | Image handling, file saving to generated_plots/ |
| **file_search_agent** | Document search and RAG capabilities | HostedFileSearchTool, vector search, document Q&A |
| **azure_search_agent** | Enterprise search using Azure AI Search | Vector and hybrid search, indexed data queries |
| **openapi_tools_agent** | External REST API integration | OpenAPI spec integration, multi-API orchestration |

### Running the DevUI Gallery

```bash
# From the azure_ai directory
devui azure_agents --port 8100
```

Then open http://localhost:8100 in your browser. All agents will appear in the dropdown menu.

### DevUI Agent Setup Notes

#### Quick Setup for File Search
Run the included setup script to automatically create a vector store:
```bash
cd AQ-CODE/azure_ai
python setup_file_search.py
```
This will upload the sample employee PDF and give you the vector store ID to add to `.env`.

#### File Search Agent
Uses vector search on employee documents (employees.pdf):
- **Auto-setup**: Run `python setup_file_search.py` (recommended)
- **Manual setup**:
  1. Go to [Azure AI Foundry](https://ai.azure.com)
  2. Upload documents to create a vector store
  3. Add `FILE_SEARCH_VECTOR_STORE_ID` to your `.env` file
  4. Restart DevUI

**Try these queries:**
- "Who works in the Engineering department?"
- "List all managers"
- "What is the contact info for [name]?"

#### Azure Search Agent
Requires Azure AI Search connection:
1. Create an Azure AI Search service
2. Connect it to your Azure AI project
3. Create and populate a search index
4. Add `AZURE_SEARCH_INDEX_NAME` to `.env` (default: hotels-sample-index)

#### Code Interpreter with Images
Automatically saves generated plots to `generated_plots/` directory. File paths are provided in responses.

#### Weather Agents
Require `OPENWEATHER_API_KEY` in `.env` for real weather data.

#### Bing Grounding Agent
Requires `BING_CONNECTION_ID` in `.env` for web search capabilities.

## Environment Variables

Before running the examples, you need to set up your environment variables. You can do this in one of two ways:

### Option 1: Using a .env file (Recommended)

1. Copy the `.env.example` file from the `python` directory to create a `.env` file:
   ```bash
   cp ../../.env.example ../../.env
   ```

2. Edit the `.env` file and add your values:
   ```
   AZURE_AI_PROJECT_ENDPOINT="your-project-endpoint"
   AZURE_AI_MODEL_DEPLOYMENT_NAME="your-model-deployment-name"
   ```

3. For samples using Bing Grounding search (like `azure_ai_with_bing_grounding.py` and `azure_ai_with_multiple_tools.py`), you'll also need:
   ```
   BING_CONNECTION_ID="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.CognitiveServices/accounts/{ai-service-name}/projects/{project-name}/connections/{connection-name}"
   ```

   To get your Bing connection ID:
   - Go to [Azure AI Foundry portal](https://ai.azure.com)
   - Navigate to your project's "Connected resources" section
   - Add a new connection for "Grounding with Bing Search"
   - Copy the connection ID

### Option 2: Using environment variables directly

Set the environment variables in your shell:

```bash
export AZURE_AI_PROJECT_ENDPOINT="your-project-endpoint"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="your-model-deployment-name"
export BING_CONNECTION_ID="your-bing-connection-id"  # Optional, only needed for web search samples
```

### Required Variables

- `AZURE_AI_PROJECT_ENDPOINT`: Your Azure AI project endpoint (required for all examples)
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`: The name of your model deployment (required for all examples)

### Optional Variables (for specific examples)

- `BING_CONNECTION_ID`: Your Bing connection ID (required for Bing grounding examples)
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key (required for weather examples)
- `FILE_SEARCH_VECTOR_STORE_ID`: Vector store ID for file search RAG examples
- `AZURE_SEARCH_INDEX_NAME`: Search index name (default: hotels-sample-index) for Azure AI Search examples

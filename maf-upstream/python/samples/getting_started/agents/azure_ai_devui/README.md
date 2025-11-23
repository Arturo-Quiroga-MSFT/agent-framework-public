# Azure AI Examples - DevUI Gallery

This directory contains Azure AI agent examples organized for DevUI's directory-based discovery. All agents will appear in the DevUI dropdown menu.

## Quick Start

```bash
# From the azure_ai_devui directory
cd /Users/arturoquiroga/GITHUB/agent-framework-public/maf-upstream/python/samples/getting_started/agents/azure_ai_devui

# Launch DevUI with all Azure AI agent examples
devui . --port 8195
```

Then open your browser to **http://localhost:8195** and you'll see all 6 agents in the dropdown!

## Available Agents

### 1. **BasicWeatherAgent** (basic_weather_agent)
- Basic Azure AI Agent with real OpenWeatherMap API
- Simple weather queries with real-time data
- Try: "What's the weather in Toronto?"

### 2. **ThreadPersistenceAgent** (thread_persistence_agent)
- Demonstrates conversation memory across multiple queries
- Can compare and remember previous cities
- Try: "What's the weather in Toronto?" then "How about Mexico City?" then "Which is warmer?"

### 3. **WebSearchAgent** (web_search_agent)
- Real-time web search using hosted web search tool
- Generic framework-provided search
- Try: "What are the latest AI news?"

### 4. **CodeInterpreterAgent** (code_interpreter_agent)
- Executes Python code for calculations and analysis
- Perfect for math problems and data tasks
- Try: "Calculate the factorial of 100"

### 5. **BingGroundingAgent** (bing_grounding_agent)
- **Enterprise-grade** web search with SOURCE CITATIONS
- Official Microsoft Bing integration with grounding
- **Key Differentiator**: Provides verifiable sources and attribution
- **Requires**: BING_CONNECTION_ID in `.env`
- Try: "What are the latest Microsoft Azure announcements?"

### 6. **FileSearchAgent** (file_search_agent)
- RAG pattern with vector search through documents
- Searches employee data with semantic matching
- **Requires**: FILE_SEARCH_VECTOR_STORE_ID in `.env`
- Try: "Who is the youngest employee?"

## Prerequisites

### Required Environment Variables

Create a `.env` file in the `azure_ai` directory (parent directory):

```bash
# Azure OpenAI (Required for all agents)
AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"

# Weather API (Required for weather agents)
OPENWEATHER_API_KEY="your-openweathermap-api-key"

# Bing Connection (Required for BingGroundingAgent)
BING_CONNECTION_ID="/subscriptions/.../connections/your-bing-connection"

# File Search (Required for FileSearchAgent)
FILE_SEARCH_VECTOR_STORE_ID="vs_xxx"
```

### Azure Authentication

All agents use Azure CLI authentication:
```bash
az login
```

## Directory Structure

```
azure_ai_devui/
├── basic_weather_agent/
│   └── __init__.py                    # Exports: agent = BasicWeatherAgent
├── thread_persistence_agent/
│   └── __init__.py                    # Exports: agent = ThreadPersistenceAgent
├── web_search_agent/
│   └── __init__.py                    # Exports: agent = WebSearchAgent
├── code_interpreter_agent/
│   └── __init__.py                    # Exports: agent = CodeInterpreterAgent
├── bing_grounding_agent/
│   └── __init__.py                    # Exports: agent = BingGroundingAgent
├── file_search_agent/
│   └── __init__.py                    # Exports: agent = FileSearchAgent
└── README.md                          # This file
```

## Features

✅ **All agents in one UI** - No need to run separate servers  
✅ **Azure CLI authentication** - Uses `AzureCliCredential`  
✅ **Real weather data** - From OpenWeatherMap API  
✅ **Multiple tools** - Weather, web search, code execution, file search  
✅ **Easy switching** - Use dropdown to switch between agents  
✅ **DevUI native** - Directory-based discovery pattern  
✅ **RAG pattern** - Vector search with File Search agent  
✅ **Grounded search** - Bing citations with BingGroundingAgent  

## Demo Scenarios

### Scenario 1: Basic Weather (3 min)
1. Select **BasicWeatherAgent**
2. Ask: "What's the weather in Toronto?"
3. Ask: "How about Guadalajara?"
4. Show real-time weather data

### Scenario 2: Thread Persistence (5 min)
1. Select **ThreadPersistenceAgent**
2. Ask: "What's the weather in Toronto?"
3. Ask: "How about Mexico City?"
4. Ask: "Which one is warmer?"
5. Ask: "What was the first city I asked about?"
6. Show how agent remembers context

### Scenario 3: Web Search (5 min)
1. Select **WebSearchAgent**
2. Ask: "What are the latest AI news?"
3. Ask: "Tell me about Microsoft's recent Azure announcements"
4. Show grounded answers with sources

### Scenario 4: Code Execution (10 min)
1. Select **CodeInterpreterAgent**
2. Ask: "Calculate factorial of 100"
3. Ask: "Generate first 20 Fibonacci numbers"
4. Ask: "Create a plot of y = x^2 from -10 to 10"
5. Show code generation and execution

### Scenario 5: Bing Grounding with Citations (5 min)
1. Select **BingGroundingAgent**
2. Ask: "What are the latest Microsoft Azure announcements?"
3. Ask: "Tell me about recent AI developments"
4. Show grounded answers with source citations

### Scenario 6: RAG with File Search (10 min)
1. Select **FileSearchAgent**
2. Ask: "Who is the youngest employee?"
3. Ask: "Who works in sales?"
4. Ask: "List employees by department"
5. Show semantic search through documents

## Troubleshooting

### "AZURE_OPENAI_ENDPOINT not found"
- Check `.env` file in `azure_ai/` directory (parent directory)
- Make sure endpoint URL is correct
- Ensure both local and parent `.env` files are configured

### "OPENWEATHER_API_KEY not found"
- Get free API key from https://openweathermap.org/api
- Add to `.env` file: `OPENWEATHER_API_KEY=your-key`

### Authentication errors
- Run `az login` to authenticate with Azure CLI
- Ensure you have access to the Azure OpenAI resource

### Agents not appearing in dropdown
- Ensure each subdirectory has `__init__.py` with `agent = ...`
- Check DevUI console output for loading errors
- Verify directory structure matches pattern above

## Comparison with Manual Workflow Script

| Feature | Manual Script | DevUI Discovery |
|---------|--------------|-----------------|
| Agent registration | Manual workflow builder | Automatic directory scan |
| Code organization | Single file with all agents | Separate subdirectories |
| Agent switching | All in dropdown | All in dropdown |
| Maintenance | Update one file | Update individual agents |
| Scalability | Add to workflow code | Add new subdirectory |
| Reusability | Workflow-specific | Agent-specific |

Perfect for Azure AI demos and workshops! 🎯

---

## DevUI vs AG-UI: Understanding the Difference

### What is DevUI?

**DevUI** is a development and testing tool built specifically for Agent Framework. It's what you're using when you run `devui . --port 8195`.

**Key Features:**
- ✅ **Built for Agent Framework** - Native integration, designed specifically for MAF
- ✅ **Zero frontend setup** - Single command launch, no React/Next.js build needed
- ✅ **Native image rendering** - matplotlib plots and images display inline automatically
- ✅ **Built-in tracing** - OpenTelemetry integration with trace visualization in UI
- ✅ **Directory-based discovery** - Automatically finds agents in subdirectories
- ✅ **Developer focused** - Perfect for debugging, testing, and inspection
- ✅ **Python-only stack** - No JavaScript/TypeScript required

**When to use DevUI:**
- 🔧 **Development & debugging** - Test agents during development
- 🧪 **Quick testing** - Rapidly switch between multiple agents
- 📊 **Demos & workshops** - Interactive presentations and training
- 🔍 **Observability** - View traces, tool calls, and agent behavior
- 🎯 **Prototyping** - Quickly iterate on agent designs

### What is AG-UI Protocol + CopilotKit?

**AG-UI** (Agent-User Interaction) is an **open protocol** for communication between AI agents and user interfaces. **CopilotKit** is a production-ready React framework that implements this protocol.

**Key Features:**
- ✅ **Production UI framework** - Professional React components for embedding agents
- ✅ **Protocol interoperability** - Works with LangGraph, CrewAI, Pydantic AI, and other frameworks
- ✅ **Embeddable copilots** - Add AI assistants to existing web applications
- ✅ **Full customization** - Complete control over UI appearance and branding
- ✅ **Multi-framework support** - AG-UI is an open standard, not vendor-locked
- ✅ **Enterprise ready** - Built for production applications with proper React patterns
- ✅ **Client-side integration** - React hooks, components, and state management

**When to use AG-UI + CopilotKit:**
- 🚀 **Production applications** - Embed agents in customer-facing products
- 🎨 **Custom branding** - Full UI control for your brand identity
- 🌐 **Cross-framework compatibility** - Interop with other AI agent frameworks
- 💼 **Enterprise applications** - Integrate into existing React/Next.js apps
- 🔄 **Complex workflows** - Advanced UI interactions and state management
- 📱 **Multi-platform** - Web apps that need responsive, customizable interfaces

### Side-by-Side Comparison

| Feature | DevUI | AG-UI + CopilotKit |
|---------|-------|-------------------|
| **Primary Purpose** | Development/Testing | Production Embedding |
| **Setup Complexity** | Single command | Next.js + FastAPI setup |
| **Technology Stack** | Python only | React + Python (FastAPI) |
| **Target Audience** | Developers | End users |
| **UI Customization** | Limited (built-in theme) | Full control (React components) |
| **Tracing/Observability** | Built-in UI panel | External tools (e.g., Langfuse) |
| **Agent Discovery** | Automatic (directory scan) | Manual routing configuration |
| **Image Display** | Native inline rendering | Requires custom handling |
| **Streaming Support** | Built-in | Server-Sent Events (SSE) |
| **Multi-Agent Support** | Dropdown menu | Custom routing logic |
| **Protocol** | Agent Framework native | AG-UI protocol (open standard) |
| **Framework Compatibility** | Agent Framework only | Multi-framework (LangGraph, etc.) |
| **Installation** | `pip install agent-framework-devui` | npm + pip packages |
| **Best For** | Demos, testing, debugging | Production apps, custom UIs |

### Architecture Overview

**DevUI Architecture:**
```
┌─────────────────────────────────────────┐
│  DevUI (Single Python Process)         │
│  ┌────────────────┐  ┌───────────────┐ │
│  │   Web Server   │  │  Agent Runner │ │
│  │   (Built-in)   │←→│  (Framework)  │ │
│  └────────────────┘  └───────────────┘ │
│         ↕                    ↕          │
│  ┌────────────────┐  ┌───────────────┐ │
│  │   Browser UI   │  │  Your Agents  │ │
│  │  (Auto-open)   │  │  (Directory)  │ │
│  └────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
```

**AG-UI + CopilotKit Architecture:**
```
┌──────────────────┐         ┌──────────────────┐
│   React/Next.js  │         │   FastAPI Server │
│                  │         │                  │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │ CopilotKit │  │  HTTP/  │  │  AG-UI     │  │
│  │ Components │←─┼─ SSE ──→│  │  Endpoint  │  │
│  └────────────┘  │         │  └────────────┘  │
│                  │         │        ↕          │
│  Your Custom UI  │         │  ┌────────────┐  │
│                  │         │  │ MAF Agent  │  │
└──────────────────┘         │  └────────────┘  │
                             └──────────────────┘
     Frontend                      Backend
```

### Protocol Differences

**DevUI Protocol:**
- Native Agent Framework communication
- Direct Python API calls
- Optimized for single-framework usage
- Built-in serialization and streaming

**AG-UI Protocol:**
- Open standard (not framework-specific)
- Event-based streaming protocol
- Server-Sent Events (SSE) transport
- JSON event messages
- Interoperable across frameworks (LangGraph, CrewAI, Pydantic AI, Agent Framework)

### Code Examples

**Launching with DevUI (Development):**
```bash
# Simple - just point to directory with agents
cd /path/to/agents/directory
devui . --port 8195

# DevUI automatically:
# - Scans subdirectories for agents
# - Creates dropdown menu
# - Enables tracing UI
# - Opens browser
```

**Setting up with AG-UI + CopilotKit (Production):**

**1. Backend (FastAPI):**
```python
from fastapi import FastAPI
from agent_framework.hosting.agui import map_agui_agent
from agent_framework.azure import AzureAIClient

app = FastAPI()

# Create agent
client = AzureAIClient(...)
agent = client.create_agent(name="MyAgent", ...)

# Expose via AG-UI protocol
map_agui_agent(app, agent, path="/api/copilotkit")
```

**2. Frontend (Next.js with CopilotKit):**
```typescript
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";

export default function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotSidebar />
      <YourAppContent />
    </CopilotKit>
  );
}
```

### Migration Path: DevUI → Production

**Phase 1: Development (DevUI)**
```bash
# Rapid prototyping and testing
devui . --port 8195
# Benefits: Fast iteration, built-in debugging
```

**Phase 2: Testing (AG-UI with default UI)**
```bash
# Test with CopilotKit's default UI
# Setup FastAPI backend with AG-UI endpoint
# Use CopilotKit's default React components
```

**Phase 3: Production (Custom AG-UI frontend)**
```bash
# Build custom branded UI
# Integrate into existing React app
# Full control over UX/UI
```

### Making the Choice

**Choose DevUI when:**
- ✅ Building and testing agents
- ✅ Running demos or workshops
- ✅ Need quick agent switching
- ✅ Want built-in tracing and debugging
- ✅ Don't need custom UI
- ✅ Python-only environment
- ✅ Working solo or in small team

**Choose AG-UI + CopilotKit when:**
- ✅ Building production applications
- ✅ Need custom branding and UI
- ✅ Embedding in existing React app
- ✅ Require cross-framework compatibility
- ✅ Building for end users (not developers)
- ✅ Need advanced React patterns
- ✅ Have frontend development resources

### Real-World Scenarios

**Scenario 1: Internal Tool Demo (Tomorrow)**
- **Use**: DevUI ✅
- **Why**: Quick setup, built-in tracing, switch between 6 agents instantly
- **Audience**: Technical stakeholders, developers

**Scenario 2: Customer-Facing Product**
- **Use**: AG-UI + CopilotKit ✅
- **Why**: Custom branding, production-ready, embed in existing app
- **Audience**: End customers, non-technical users

**Scenario 3: Research Prototype**
- **Use**: DevUI ✅
- **Why**: Fast iteration, no frontend overhead, focus on agent logic
- **Audience**: Research team, data scientists

**Scenario 4: Enterprise SaaS Platform**
- **Use**: AG-UI + CopilotKit ✅
- **Why**: Multi-tenant, white-label, custom UI/UX requirements
- **Audience**: Enterprise customers

### Resources

**DevUI:**
- Command: `devui --help`
- This demo: `devui . --port 8195`
- Documentation: Agent Framework docs

**AG-UI + CopilotKit:**
- AG-UI Protocol: [Open standard specification]
- CopilotKit: https://docs.copilotkit.ai
- Example: `/AQ-CODE/demos/maf-simple-weather/` in this repo
- Agent Framework AG-UI guide: [Coming in docs]

### Summary

- **DevUI** = Built specifically for Agent Framework development and testing
- **AG-UI** = Open protocol for production agent-to-UI communication
- **CopilotKit** = Production React framework implementing AG-UI protocol

**For your demos tomorrow**: Use DevUI - it's perfect for showcasing Agent Framework capabilities!

**For production apps**: Consider AG-UI + CopilotKit when you need custom UIs and production deployment.

---

## Technical Notes

### DevUI Discovery Pattern

DevUI automatically discovers agents by:
1. Scanning subdirectories in the specified path
2. Looking for `__init__.py` files
3. Importing and finding objects with `agent` attribute
4. Adding each agent to the dropdown menu

### Agent Creation Pattern

Each agent subdirectory must:
- Have an `__init__.py` file
- Export a variable named `agent`
- The agent should be created using `AzureAIClient.create_agent()`

### Environment Variables

Uses cascading `.env` loading:
1. Checks local `azure_ai/.env` first
2. Falls back to parent `getting_started/.env`
3. This allows local overrides while sharing common config

## Cities Updated

All weather examples use the following cities (updated from Seattle/Tokyo):
- **Toronto** (Canada)
- **Mexico City** (Mexico)
- **Guadalajara** (Mexico)
- **Monterrey** (Mexico)
- **Puebla** (Mexico)
- **Cancun** (Mexico)

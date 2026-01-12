# Microsoft Agent Framework (Foundry) vs LangGraph: Comprehensive Comparison

**Last Updated:** January 12, 2026  
**Status:** Both frameworks actively maintained and updated

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [What Are These Frameworks?](#what-are-these-frameworks)
3. [Feature Comparison Matrix](#feature-comparison-matrix)
4. [Architecture Comparison](#architecture-comparison)
5. [Use Case Recommendations](#use-case-recommendations)
6. [Integration & Interoperability](#integration--interoperability)
7. [Migration Considerations](#migration-considerations)
8. [Ecosystem & Community](#ecosystem--community)
9. [Decision Guide](#decision-guide)
10. [Code Examples](#code-examples)

---

## Executive Summary

**Microsoft Agent Framework (MAF)** and **LangGraph** are both production-ready frameworks for building AI agents and multi-agent workflows, but they target different use cases and developer preferences:

| Aspect | Microsoft Agent Framework | LangGraph |
|--------|---------------------------|-----------|
| **Creator** | Microsoft (Semantic Kernel + AutoGen teams) | LangChain (LangChain Inc) |
| **Status** | Public Preview (Jan 2026) | Production Stable |
| **Primary Use Case** | Enterprise multi-agent systems | Stateful agent workflows |
| **Best For** | .NET/Python enterprises, Azure ecosystems | Python-first teams, LangChain users |
| **Learning Curve** | Moderate (enterprise patterns) | Moderate (graph concepts) |
| **Deployment** | Azure + anywhere | Anywhere (cloud-agnostic) |

**Key Insight**: These frameworks can work together! LangGraph agents can be exposed as MCP servers and called by MAF workflows, combining LangGraph's agent intelligence with MAF's enterprise orchestration.

---

## What Are These Frameworks?

### Microsoft Agent Framework (MAF)

Microsoft Agent Framework is the next-generation successor to **Semantic Kernel** and **AutoGen**, created by the same Microsoft teams. It combines:

- AutoGen's simple abstractions for multi-agent patterns
- Semantic Kernel's enterprise features (type safety, telemetry, thread management)
- **New**: Graph-based workflows with explicit control flow
- **New**: Robust checkpointing and state management for long-running processes

**Philosophy**: "Enterprise-grade AI agents with explicit control and type safety"

**Current Version**: Public Preview (rapidly evolving)  
**Installation**: `pip install agent-framework --pre`

**Key Components**:
- **AI Agents**: Individual agents with LLMs, tools, and instructions
- **Workflows**: Graph-based orchestration of agents and functions
- **Threads**: State management for multi-turn conversations
- **Context Providers**: Agent memory capabilities
- **Middleware**: Intercept and modify agent behavior
- **MCP Integration**: Model Context Protocol for tool calling
- **DevUI**: Interactive developer interface for testing

### LangGraph

LangGraph is a framework for building stateful, multi-actor applications with LLMs, built by **LangChain Inc** (creators of LangChain). It provides:

- Graph-based workflow execution (inspired by Pregel and Apache Beam)
- Persistent state across graph executions
- Built-in checkpointing and time-travel debugging
- Human-in-the-loop patterns
- Can be used standalone or with LangChain

**Philosophy**: "Low-level infrastructure for stateful, long-running agent workflows"

**Current Version**: Stable (production-ready)  
**Installation**: `pip install -U langgraph`

**Key Components**:
- **StateGraph**: Define agent workflows as directed graphs
- **Nodes**: Functions that process state
- **Edges**: Connect nodes (direct or conditional)
- **Checkpointers**: Persist state to databases (Postgres, Redis, etc.)
- **ToolNode**: Execute tool calls within graphs
- **MessagesState**: Pre-built state for chat applications
- **LangSmith Integration**: Deep observability and debugging

---

## Feature Comparison Matrix

### Core Capabilities

| Feature | Microsoft Agent Framework | LangGraph | Notes |
|---------|--------------------------|-----------|-------|
| **Graph-Based Workflows** | ✅ Yes | ✅ Yes | Both support node/edge architecture |
| **State Management** | ✅ Thread-based | ✅ StateGraph + Checkpointers | MAF: threads; LG: state classes |
| **Checkpointing** | ✅ Workflow-level | ✅ Graph-level | Both support resume from failures |
| **Conditional Routing** | ✅ Yes | ✅ Yes | Both support dynamic flow control |
| **Parallel Execution** | ✅ Yes | ✅ Yes | Concurrent node execution |
| **Human-in-the-Loop** | ✅ Request/Response pattern | ✅ Built-in interrupt patterns | Both well-supported |
| **Streaming** | ✅ Yes | ✅ Yes | Real-time output streaming |
| **Time-Travel Debugging** | ⚠️ Limited | ✅ Yes | LG has robust replay capabilities |

### Language Support

| Language | Microsoft Agent Framework | LangGraph |
|----------|--------------------------|-----------|
| **Python** | ✅ Full support | ✅ Full support |
| **.NET (C#)** | ✅ Full support | ❌ Not supported |
| **TypeScript/JavaScript** | ❌ Not supported | ✅ Via LangChain.js |
| **API Consistency** | ✅ Identical Python/.NET APIs | Python only |

### Agent Creation

| Feature | Microsoft Agent Framework | LangGraph | Winner |
|---------|--------------------------|-----------|--------|
| **Single Agent Creation** | ✅ `ChatAgent` | ⚠️ Manual StateGraph | MAF (simpler) |
| **Multi-Agent Patterns** | ✅ Built-in orchestration | ⚠️ Build manually | MAF (pre-built) |
| **Agent Instructions** | ✅ First-class property | ⚠️ In system prompt | MAF (cleaner) |
| **Tool Calling** | ✅ MCP + native tools | ✅ LangChain tools | Tie |
| **Agent Memory** | ✅ Context providers | ✅ State + checkpointers | Tie |
| **Thread Management** | ✅ Built-in threads | ⚠️ Manual thread_id | MAF (easier) |

### Workflow Features

| Feature | Microsoft Agent Framework | LangGraph | Winner |
|---------|--------------------------|-----------|--------|
| **Visual Workflow Design** | ✅ DevUI | ⚠️ Via LangSmith Studio | MAF (built-in) |
| **Workflow Composition** | ✅ Nested workflows | ✅ Subgraphs | Tie |
| **Type Safety** | ✅ Strong typing | ⚠️ TypedDict (Python) | MAF (stricter) |
| **Error Handling** | ✅ Middleware | ⚠️ Try/except in nodes | MAF (cleaner) |
| **Retry Logic** | ✅ Built-in | ⚠️ Manual implementation | MAF (easier) |
| **State Persistence** | ✅ Checkpoints | ✅ Checkpointers (Postgres, etc.) | LG (more storage options) |

### Model Providers

| Provider | Microsoft Agent Framework | LangGraph |
|----------|--------------------------|-----------|
| **Azure OpenAI** | ✅ First-class | ✅ Via LangChain |
| **OpenAI** | ✅ First-class | ✅ Via LangChain |
| **Azure AI Foundry** | ✅ Native | ⚠️ Via adapters |
| **Anthropic** | ⚠️ Via adapters | ✅ Via LangChain |
| **Google Gemini** | ⚠️ Via adapters | ✅ Via LangChain |
| **Ollama (local)** | ⚠️ Limited | ✅ Via LangChain |
| **Custom Models** | ✅ Extensible | ✅ Extensible |

**Winner**: LangGraph (broader ecosystem via LangChain)

### Tool Integration

| Feature | Microsoft Agent Framework | LangGraph |
|---------|--------------------------|-----------|
| **Model Context Protocol (MCP)** | ✅ First-class | ⚠️ Manual implementation |
| **Function Calling** | ✅ Yes | ✅ Yes |
| **LangChain Tools** | ⚠️ Via adapters | ✅ Native |
| **Custom Tools** | ✅ Easy | ✅ Easy |
| **Tool Validation** | ✅ Type-based | ⚠️ Manual |

### Observability & Debugging

| Feature | Microsoft Agent Framework | LangGraph | Winner |
|---------|--------------------------|-----------|--------|
| **Built-in Tracing** | ✅ OpenTelemetry | ✅ LangSmith | LG (richer) |
| **Visual Debugging** | ✅ DevUI | ✅ LangSmith Studio | Tie |
| **State Inspection** | ✅ Checkpoints | ✅ Checkpointers + UI | LG (better UI) |
| **Execution Replay** | ⚠️ Limited | ✅ Time-travel | LG (superior) |
| **Log Aggregation** | ✅ Application Insights | ✅ LangSmith | Tie |
| **Custom Metrics** | ✅ Middleware | ⚠️ Callbacks | MAF (cleaner) |

### Enterprise Features

| Feature | Microsoft Agent Framework | LangGraph | Winner |
|---------|--------------------------|-----------|--------|
| **Type Safety** | ✅ Strong (Python + .NET) | ⚠️ TypedDict only | MAF |
| **Middleware/Filters** | ✅ Built-in | ⚠️ Callbacks | MAF |
| **Authentication** | ✅ Azure Entra ID | ⚠️ Custom | MAF |
| **Content Filters** | ✅ Azure AI Safety | ⚠️ Custom | MAF |
| **RBAC** | ✅ Azure native | ⚠️ Custom | MAF |
| **Audit Logging** | ✅ Middleware | ⚠️ Custom | MAF |
| **Compliance** | ✅ Azure ecosystem | ⚠️ Custom | MAF |

**Winner**: MAF (Azure-first, enterprise-grade)

### Deployment & Hosting

| Platform | Microsoft Agent Framework | LangGraph | Notes |
|----------|--------------------------|-----------|-------|
| **Azure (Hosted Agents)** | ✅ One-line deployment | ⚠️ Via adapter | MAF native |
| **Azure Functions** | ✅ Yes | ✅ Yes | Both work |
| **Azure Container Apps** | ✅ Yes | ✅ Yes | Both work |
| **AWS Lambda** | ✅ Yes | ✅ Yes | Both work |
| **GCP Cloud Run** | ✅ Yes | ✅ Yes | Both work |
| **Kubernetes** | ✅ Yes | ✅ Yes | Both work |
| **LangSmith Agent Server** | ❌ No | ✅ Native | LG native |
| **On-Premises** | ✅ Yes | ✅ Yes | Both work |

### Multi-Agent Orchestration

| Pattern | Microsoft Agent Framework | LangGraph | Winner |
|---------|--------------------------|-----------|--------|
| **Sequential** | ✅ Built-in | ⚠️ Build manually | MAF |
| **Concurrent** | ✅ Built-in | ⚠️ Build manually | MAF |
| **Hand-off** | ✅ Built-in | ⚠️ Build manually | MAF |
| **Group Chat** | ✅ Built-in | ⚠️ Build manually | MAF |
| **Supervisor Pattern** | ✅ Built-in (Magentic) | ⚠️ Build manually | MAF |
| **Custom Patterns** | ✅ Workflow graphs | ✅ StateGraph | Tie |

**Winner**: MAF (pre-built patterns for common use cases)

### Performance & Scalability

| Metric | Microsoft Agent Framework | LangGraph | Notes |
|--------|--------------------------|-----------|-------|
| **Latency** | Similar | Similar | Depends on LLM calls |
| **Throughput** | High | High | Both support concurrency |
| **State Size** | No hard limit | No hard limit | Use external storage |
| **Checkpoint Size** | Configurable | Configurable | Both support compression |
| **Cold Start** | Fast | Fast | Similar Python startup |

### Cost Considerations

| Cost Factor | Microsoft Agent Framework | LangGraph |
|-------------|--------------------------|-----------|
| **Framework License** | ✅ Free (MIT) | ✅ Free (MIT) |
| **LLM API Costs** | $$ (same for both) | $$ (same for both) |
| **Observability** | ✅ Free (DevUI) | $$ (LangSmith paid) |
| **Deployment** | $$ (Azure fees) | $ (Any provider) |
| **State Storage** | $ (Azure Cosmos DB) | $ (Postgres/Redis/etc) |

---

## Architecture Comparison

### Microsoft Agent Framework Architecture

```
┌─────────────────────────────────────────────────────┐
│               User Application                      │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│          Microsoft Agent Framework SDK              │
│                                                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │   Agents   │  │ Workflows  │  │   DevUI      │ │
│  │            │  │            │  │              │ │
│  │ • ChatAgent│  │ • Graph    │  │ • Testing    │ │
│  │ • Thread   │  │ • Executors│  │ • Debugging  │ │
│  │ • Context  │  │ • Routing  │  │ • Viz        │ │
│  │ • Tools    │  │ • Parallel │  │              │ │
│  └────────────┘  └────────────┘  └──────────────┘ │
│                                                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │ Middleware │  │   Models   │  │     MCP      │ │
│  │            │  │            │  │              │ │
│  │ • Logging  │  │ • OpenAI   │  │ • Servers    │ │
│  │ • Security │  │ • Azure AI │  │ • Clients    │ │
│  │ • Metrics  │  │ • Foundry  │  │ • Tools      │ │
│  └────────────┘  └────────────┘  └──────────────┘ │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │       OpenTelemetry Integration             │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Key Characteristics**:
- Thread-based state management
- Type-safe message passing
- Middleware for cross-cutting concerns
- DevUI for interactive development
- MCP-first tool integration
- Azure-native features (Entra ID, AI Safety, etc.)

### LangGraph Architecture

```
┌─────────────────────────────────────────────────────┐
│               User Application                      │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│                  LangGraph SDK                      │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │           StateGraph                       │   │
│  │                                            │   │
│  │  ┌──────┐    ┌──────┐    ┌──────┐        │   │
│  │  │ Node │───▶│ Node │───▶│ Node │        │   │
│  │  └──────┘    └──────┘    └──────┘        │   │
│  │      │            │            │          │   │
│  │      └────────────┼────────────┘          │   │
│  │                   │                       │   │
│  │              Conditional                  │   │
│  │                Edges                      │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │   State    │  │Checkpointer│  │   ToolNode   │ │
│  │            │  │            │  │              │ │
│  │ • Messages │  │ • Postgres │  │ • LangChain  │ │
│  │ • Custom   │  │ • Redis    │  │   Tools      │ │
│  │ • Typed    │  │ • Memory   │  │ • Custom     │ │
│  └────────────┘  └────────────┘  └──────────────┘ │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │       LangSmith Integration                 │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Key Characteristics**:
- Graph-based execution model
- Flexible state management (any Python object)
- Persistent checkpointers (database-backed)
- Pregel-inspired parallel processing
- LangChain ecosystem integration
- Time-travel debugging with state replay

### Workflow Execution Comparison

**Microsoft Agent Framework Workflow**:
```python
# MAF uses declarative workflow builders
from agent_framework import SequentialBuilder

workflow = (
    SequentialBuilder()
    .add_executor(agent1)        # Type-safe
    .add_executor(function)      # Mix agents + functions
    .add_executor(agent2)
    .build()
)

result = await workflow.run(input_data)
```

**LangGraph Workflow**:
```python
# LangGraph uses imperative graph construction
from langgraph.graph import StateGraph

graph = StateGraph(State)
graph.add_node("agent1", agent1_function)
graph.add_node("function", function_node)
graph.add_node("agent2", agent2_function)

graph.add_edge("agent1", "function")
graph.add_conditional_edges(
    "function", 
    routing_function,
    {"path_a": "agent2", "path_b": END}
)

app = graph.compile()
result = app.invoke(input_data)
```

---

## Use Case Recommendations

### Choose Microsoft Agent Framework When:

✅ **Enterprise .NET Development**
- Building agents for .NET applications
- Need consistent Python/.NET APIs
- Integrating with existing .NET codebases

✅ **Azure-First Strategy**
- Deploying to Azure (Hosted Agents, Functions, Container Apps)
- Using Azure OpenAI, Azure AI, or Azure AI Foundry
- Need Azure Entra ID authentication
- Require Azure compliance and governance

✅ **Migrating from Semantic Kernel or AutoGen**
- Existing SK/AutoGen codebase
- Microsoft migration guides available
- Familiar patterns and concepts

✅ **Pre-Built Multi-Agent Patterns**
- Need sequential, concurrent, hand-off orchestration
- Building group chat or supervisor patterns
- Want built-in patterns vs building from scratch

✅ **Type Safety & Enterprise Governance**
- Strong typing requirements
- Middleware for compliance, audit logging
- Content filtering and safety guardrails

✅ **Rapid Prototyping with DevUI**
- Interactive agent development
- Visual workflow debugging
- Need built-in testing tools

### Choose LangGraph When:

✅ **Python-First Development**
- Pure Python shop (no .NET requirement)
- Want Python-native idioms
- Prefer imperative programming style

✅ **LangChain Ecosystem User**
- Already using LangChain
- Want LangChain tools and integrations
- Invested in LangSmith for observability

✅ **Complex State Management**
- Need arbitrary state structures
- Require database-backed persistence (Postgres, Redis)
- Building stateful, long-running workflows

✅ **Cloud-Agnostic Deployment**
- Multi-cloud strategy (AWS, GCP, Azure)
- On-premises deployment
- No vendor lock-in requirements

✅ **Time-Travel Debugging**
- Need state replay capabilities
- Complex debugging requirements
- Iterative development with state inspection

✅ **Community Extensions**
- Want broader LLM provider support (Anthropic, Gemini, etc.)
- Need LangChain integrations (loaders, retrievers, etc.)
- Active community contributions

### Use Both Together When:

🤝 **Hybrid Architecture**
- LangGraph agents as specialized reasoning engines
- MAF workflows for enterprise orchestration
- Expose LangGraph agents as MCP servers
- Call from MAF workflows for best of both worlds

**Example Pattern**:
```
┌──────────────────────────────────────────┐
│       MAF Orchestrator                   │
│  • Enterprise features                   │
│  • Azure integration                     │
│  • Multi-agent coordination              │
└──────────────┬───────────────────────────┘
               │ MCP Protocol
┌──────────────▼───────────────────────────┐
│    LangGraph Agent (MCP Server)          │
│  • Complex reasoning                     │
│  • Stateful workflows                    │
│  • LangChain tools                       │
└──────────────────────────────────────────┘
```

**Benefits**:
- ✅ Use LangGraph for complex agent logic
- ✅ Use MAF for enterprise orchestration
- ✅ Standard MCP interface (no tight coupling)
- ✅ Deploy LangGraph agents anywhere
- ✅ Best of both ecosystems

See: [LangGraph + MAF Integration Guide](../AQ-TERADATA/LANGGRAPH_MCP_INTEGRATION.md)

---

## Integration & Interoperability

### Can They Work Together?

**YES!** Microsoft Agent Framework and LangGraph can integrate via the **Model Context Protocol (MCP)**:

1. **LangGraph Agent → MCP Server**
   - Wrap LangGraph agent as MCP server
   - Expose tools via standard MCP interface
   - Deploy anywhere (Azure, AWS, GCP, on-prem)

2. **MAF Workflow → MCP Client**
   - Call LangGraph MCP servers from MAF workflows
   - Use `MCPExecutor` in workflows
   - Standard tool calling interface

3. **Benefits**:
   - ✅ Cloud-agnostic architecture
   - ✅ No vendor lock-in
   - ✅ Language-agnostic communication
   - ✅ Combine strengths of both frameworks

### Integration Patterns

#### Pattern 1: LangGraph as MCP Server

```python
# langgraph_agent_mcp_server.py
from mcp.server import Server
from langgraph.graph import StateGraph
import asyncio

# Create LangGraph agent
graph = StateGraph(AgentState)
graph.add_node("reasoning", reasoning_node)
graph.add_node("tools", tool_execution_node)
# ... build graph
agent = graph.compile()

# Wrap as MCP server
server = Server("langgraph-agent")

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute LangGraph agent via MCP"""
    if name == "langgraph_agent":
        result = await agent.ainvoke(arguments)
        return [TextContent(type="text", text=str(result))]

# Run MCP server
server.run(host="0.0.0.0", port=8080)
```

#### Pattern 2: MAF Calls LangGraph via MCP

```python
# maf_workflow_with_langgraph.py
from agent_framework import SequentialBuilder
from agent_framework.executors import Executor
import httpx

class LangGraphMCPExecutor(Executor):
    """Call LangGraph agent via MCP"""
    
    async def execute(self, input_data, ctx):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://langgraph-service:8080/tools/call",
                json={
                    "name": "langgraph_agent",
                    "arguments": input_data
                }
            )
            result = response.json()
            await ctx.send_message(result)

# Build MAF workflow
workflow = (
    SequentialBuilder()
    .add_executor(maf_agent_1)
    .add_executor(LangGraphMCPExecutor())  # Call LangGraph
    .add_executor(maf_agent_2)
    .build()
)
```

### Shared Concepts

| Concept | Microsoft Agent Framework | LangGraph |
|---------|--------------------------|-----------|
| **State Management** | Thread | StateGraph state |
| **Node Execution** | Executor | Node function |
| **Routing** | Conditional routers | Conditional edges |
| **Persistence** | Checkpoints | Checkpointers |
| **Human-in-Loop** | Request/Response | Interrupt/Resume |
| **Tools** | MCP servers | LangChain tools |
| **Observability** | OpenTelemetry | LangSmith |

---

## Migration Considerations

### From LangGraph to Microsoft Agent Framework

**Why Migrate?**
- Need .NET support
- Azure-first deployment strategy
- Want pre-built multi-agent patterns
- Require enterprise governance features
- Type safety requirements

**Migration Path**:
1. **Conceptual Mapping**:
   - `StateGraph` → `SequentialBuilder` / workflow graph
   - Nodes → Executors or Agent functions
   - State → Thread or WorkflowContext
   - Conditional edges → Routers
   - Checkpointers → Workflow checkpoints

2. **Code Translation**:
   ```python
   # LangGraph
   from langgraph.graph import StateGraph
   
   graph = StateGraph(State)
   graph.add_node("step1", step1_func)
   graph.add_node("step2", step2_func)
   graph.add_edge("step1", "step2")
   app = graph.compile()
   ```
   
   ```python
   # Microsoft Agent Framework
   from agent_framework import SequentialBuilder
   
   workflow = (
       SequentialBuilder()
       .add_executor(step1_executor)
       .add_executor(step2_executor)
       .build()
   )
   ```

3. **Gradual Migration**:
   - Keep LangGraph agents as MCP servers
   - Build new workflows in MAF
   - Gradually port critical components

### From Microsoft Agent Framework to LangGraph

**Why Migrate?**
- Move away from Azure-first strategy
- Need LangChain ecosystem integration
- Python-only requirements (drop .NET)
- Want time-travel debugging
- Multi-cloud deployment

**Migration Path**:
1. **Conceptual Mapping**:
   - `ChatAgent` → LangGraph with agent node
   - Workflow → StateGraph
   - Executors → Node functions
   - Routers → Conditional edges
   - Thread → State + thread_id

2. **Code Translation**:
   ```python
   # Microsoft Agent Framework
   from agent_framework import ChatAgent, SequentialBuilder
   
   agent1 = ChatAgent(...)
   agent2 = ChatAgent(...)
   
   workflow = (
       SequentialBuilder()
       .add_executor(agent1)
       .add_executor(agent2)
       .build()
   )
   ```
   
   ```python
   # LangGraph
   from langgraph.graph import StateGraph, MessagesState
   
   def agent1_node(state: MessagesState):
       # Call LLM with agent1 instructions
       response = llm.invoke(state["messages"])
       return {"messages": [response]}
   
   def agent2_node(state: MessagesState):
       # Call LLM with agent2 instructions
       response = llm.invoke(state["messages"])
       return {"messages": [response]}
   
   graph = StateGraph(MessagesState)
   graph.add_node("agent1", agent1_node)
   graph.add_node("agent2", agent2_node)
   graph.add_edge("agent1", "agent2")
   app = graph.compile()
   ```

3. **Observability Migration**:
   - MAF OpenTelemetry → LangSmith tracing
   - DevUI → LangSmith Studio
   - Application Insights → LangSmith monitoring

---

## Ecosystem & Community

### Microsoft Agent Framework Ecosystem

**Official Resources**:
- 📚 [Microsoft Learn Docs](https://learn.microsoft.com/en-us/agent-framework/)
- 💻 [GitHub Repository](https://github.com/microsoft/agent-framework)
- 💬 [Discord Server](https://discord.gg/b5zjErwbQM) (Azure AI Foundry)
- 📅 Weekly Office Hours
- 🎓 Migration guides from SK/AutoGen

**Integration**:
- ✅ Azure OpenAI
- ✅ Azure AI Foundry
- ✅ Azure Hosted Agents
- ✅ Model Context Protocol (MCP)
- ✅ Application Insights
- ⚠️ LangChain tools (via adapters)

**Community**:
- Growing (newer framework)
- Microsoft-backed
- Enterprise focus
- Active development (public preview)

**Notable Users**:
- Microsoft internal teams
- Enterprise Azure customers
- .NET developers
- Semantic Kernel/AutoGen users

### LangGraph Ecosystem

**Official Resources**:
- 📚 [Official Docs](https://docs.langchain.com/oss/python/langgraph/overview)
- 💻 [GitHub Repository](https://github.com/langchain-ai/langgraph)
- 💬 [Discord Server](https://discord.gg/langchain)
- 🎓 Tutorials and guides
- 🎥 Video tutorials

**Integration**:
- ✅ LangChain (500+ integrations)
- ✅ LangSmith (observability)
- ✅ LangSmith Agent Server (deployment)
- ✅ All major LLM providers
- ✅ Vector databases
- ✅ Document loaders

**Community**:
- Large and active
- LangChain ecosystem (100K+ stars)
- Python-first
- Production-proven

**Notable Users**:
- Startups
- AI-first companies
- Research institutions
- Python data science teams

### Third-Party Tools Compatibility

| Tool | Microsoft Agent Framework | LangGraph |
|------|--------------------------|-----------|
| **LangSmith** | ⚠️ Via custom instrumentation | ✅ Native |
| **Weights & Biases** | ✅ Via OpenTelemetry | ✅ Via callbacks |
| **MLflow** | ✅ Custom logging | ✅ Custom logging |
| **Prometheus** | ✅ Via OpenTelemetry | ⚠️ Custom |
| **Jaeger** | ✅ Via OpenTelemetry | ⚠️ Custom |
| **Datadog** | ✅ Via OpenTelemetry | ⚠️ Custom |

---

## Decision Guide

### Decision Tree

```
Start
  │
  ├─ Need .NET support?
  │   └─ YES → Microsoft Agent Framework ✅
  │   └─ NO → Continue
  │
  ├─ Deploying primarily to Azure?
  │   └─ YES → Microsoft Agent Framework ✅
  │   └─ NO → Continue
  │
  ├─ Already using LangChain?
  │   └─ YES → LangGraph ✅
  │   └─ NO → Continue
  │
  ├─ Need pre-built multi-agent patterns?
  │   └─ YES → Microsoft Agent Framework ✅
  │   └─ NO → Continue
  │
  ├─ Need time-travel debugging?
  │   └─ YES → LangGraph ✅
  │   └─ NO → Continue
  │
  ├─ Want cloud-agnostic deployment?
  │   └─ YES → LangGraph ✅
  │   └─ NO → Continue
  │
  └─ Either works! Choose based on:
      • Team expertise (Python vs .NET)
      • Existing infrastructure
      • Budget (Azure costs vs self-managed)
      • Community preference
```

### Scoring Matrix

Rate your requirements (0-5 scale, 5 = critical):

| Requirement | Score | Favors |
|-------------|-------|--------|
| .NET support | _____ | MAF if > 3 |
| Azure integration | _____ | MAF if > 3 |
| Type safety | _____ | MAF if > 3 |
| Pre-built patterns | _____ | MAF if > 3 |
| LangChain ecosystem | _____ | LG if > 3 |
| Cloud-agnostic | _____ | LG if > 3 |
| Time-travel debug | _____ | LG if > 3 |
| Python-only | _____ | LG if > 3 |

**Recommendation**:
- If MAF scores ≥ 12: Choose Microsoft Agent Framework
- If LG scores ≥ 12: Choose LangGraph
- If tied: Consider using both (MCP integration)

---

## Code Examples

### Example 1: Simple Chat Agent

**Microsoft Agent Framework**:
```python
from agent_framework import create_agent
from agent_framework.models.azure_openai import AzureOpenAIChatCompletion

# Create model
model = AzureOpenAIChatCompletion(
    deployment_name="gpt-4",
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY")
)

# Create agent
agent = create_agent(
    model=model,
    instructions="You are a helpful assistant.",
    name="assistant"
)

# Run agent
response = await agent.run("Hello!")
print(response.messages[-1].content)
```

**LangGraph**:
```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import AzureChatOpenAI

# Create model
model = AzureChatOpenAI(
    deployment_name="gpt-4",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY")
)

# Create agent node
def agent_node(state: MessagesState):
    system_prompt = "You are a helpful assistant."
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# Build graph
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)
app = graph.compile()

# Run agent
result = app.invoke({"messages": [{"role": "user", "content": "Hello!"}]})
print(result["messages"][-1].content)
```

### Example 2: Multi-Step Workflow

**Microsoft Agent Framework**:
```python
from agent_framework import SequentialBuilder, create_agent

# Create agents
research_agent = create_agent(
    model=model,
    instructions="Research the topic and gather information.",
    name="researcher"
)

writer_agent = create_agent(
    model=model,
    instructions="Write a summary based on research.",
    name="writer"
)

# Build workflow
workflow = (
    SequentialBuilder()
    .add_executor(research_agent)
    .add_executor(writer_agent)
    .build()
)

# Run workflow
result = await workflow.run("Tell me about quantum computing")
print(result.messages[-1].content)
```

**LangGraph**:
```python
from langgraph.graph import StateGraph, MessagesState, START, END

# Define agent nodes
def research_node(state: MessagesState):
    system = "Research the topic and gather information."
    messages = [{"role": "system", "content": system}] + state["messages"]
    response = model.invoke(messages)
    return {"messages": state["messages"] + [response]}

def writer_node(state: MessagesState):
    system = "Write a summary based on research."
    messages = [{"role": "system", "content": system}] + state["messages"]
    response = model.invoke(messages)
    return {"messages": state["messages"] + [response]}

# Build graph
graph = StateGraph(MessagesState)
graph.add_node("research", research_node)
graph.add_node("writer", writer_node)
graph.add_edge(START, "research")
graph.add_edge("research", "writer")
graph.add_edge("writer", END)
app = graph.compile()

# Run workflow
result = app.invoke({"messages": [{"role": "user", "content": "Tell me about quantum computing"}]})
print(result["messages"][-1].content)
```

### Example 3: Conditional Routing

**Microsoft Agent Framework**:
```python
from agent_framework import GraphBuilder, ConditionalRouter

def route_by_topic(context):
    """Route to specialist based on topic"""
    last_message = context.messages[-1].content.lower()
    if "python" in last_message:
        return "python_expert"
    elif "javascript" in last_message:
        return "js_expert"
    else:
        return "general_expert"

workflow = (
    GraphBuilder()
    .add_executor("classifier", classifier_agent)
    .add_executor("python_expert", python_agent)
    .add_executor("js_expert", js_agent)
    .add_executor("general_expert", general_agent)
    .add_conditional_router(
        "classifier",
        ConditionalRouter(route_by_topic),
        {
            "python_expert": ["python_expert"],
            "js_expert": ["js_expert"],
            "general_expert": ["general_expert"]
        }
    )
    .build()
)
```

**LangGraph**:
```python
from langgraph.graph import StateGraph, MessagesState, START, END

def route_by_topic(state: MessagesState):
    """Route to specialist based on topic"""
    last_message = state["messages"][-1].content.lower()
    if "python" in last_message:
        return "python_expert"
    elif "javascript" in last_message:
        return "js_expert"
    else:
        return "general_expert"

graph = StateGraph(MessagesState)
graph.add_node("classifier", classifier_node)
graph.add_node("python_expert", python_node)
graph.add_node("js_expert", js_node)
graph.add_node("general_expert", general_node)

graph.add_edge(START, "classifier")
graph.add_conditional_edges(
    "classifier",
    route_by_topic,
    {
        "python_expert": "python_expert",
        "js_expert": "js_expert",
        "general_expert": "general_expert"
    }
)
graph.add_edge("python_expert", END)
graph.add_edge("js_expert", END)
graph.add_edge("general_expert", END)

app = graph.compile()
```

### Example 4: Human-in-the-Loop

**Microsoft Agent Framework**:
```python
from agent_framework import GraphBuilder
from agent_framework.executors import RequestExecutor

workflow = (
    GraphBuilder()
    .add_executor("analysis", analysis_agent)
    .add_executor("approval", RequestExecutor(
        request_name="human_approval",
        instructions="Review and approve the analysis"
    ))
    .add_executor("finalize", finalize_agent)
    .build()
)

# Run workflow
async for event in workflow.run_stream("Analyze sales data"):
    if event.type == "request":
        # Pause for human input
        user_input = input("Approve? (yes/no): ")
        await workflow.respond(event.id, {"approved": user_input == "yes"})
    elif event.type == "message":
        print(event.content)
```

**LangGraph**:
```python
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver

graph = StateGraph(MessagesState)
graph.add_node("analysis", analysis_node)
graph.add_node("finalize", finalize_node)

graph.add_edge(START, "analysis")
graph.add_edge("analysis", "finalize")
graph.add_edge("finalize", END)

# Compile with checkpointer for interrupts
checkpointer = MemorySaver()
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["finalize"]  # Pause before finalize
)

# Run workflow
config = {"configurable": {"thread_id": "1"}}
result = app.invoke({"messages": [{"role": "user", "content": "Analyze sales data"}]}, config)

# Pause here for human approval
user_input = input("Approve? (yes/no): ")

if user_input == "yes":
    # Resume workflow
    result = app.invoke(None, config)
```

---

## Conclusion

Both **Microsoft Agent Framework** and **LangGraph** are excellent choices for building AI agent systems in 2026. Your decision should be based on:

### Choose Microsoft Agent Framework If:
- 🏢 You're an enterprise with Azure infrastructure
- 💻 You need .NET support or have .NET teams
- 🛡️ You require built-in enterprise features (auth, compliance, safety)
- 🚀 You want rapid development with pre-built patterns
- 📊 You're migrating from Semantic Kernel or AutoGen

### Choose LangGraph If:
- 🐍 You're a Python-first team
- 🌐 You need cloud-agnostic deployment
- 🔗 You're already using LangChain ecosystem
- 🔍 You need advanced debugging (time-travel)
- 💰 You want cost-effective, self-managed deployment

### Use Both Together If:
- 🤝 You want best of both worlds
- 🔌 You need flexible architecture
- 🌍 You're building multi-cloud systems
- 🎯 You want specialized agents + enterprise orchestration

**The Future**: Both frameworks are actively developed and converging on similar patterns (graph-based workflows, checkpointing, human-in-loop). The Model Context Protocol (MCP) enables interoperability, so you don't have to choose one exclusively.

**Bottom Line**: There's no universally "better" framework—only the better choice for your specific use case, team, and infrastructure.

---

## Additional Resources

### Microsoft Agent Framework
- 📚 [Official Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- 💻 [GitHub Repository](https://github.com/microsoft/agent-framework)
- 🎓 [Migration from Semantic Kernel](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/)
- 🎓 [Migration from AutoGen](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/)
- 💬 [Discord Community](https://discord.gg/b5zjErwbQM)

### LangGraph
- 📚 [Official Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- 💻 [GitHub Repository](https://github.com/langchain-ai/langgraph)
- 🎓 [Tutorials](https://langchain-tutorials.github.io/)
- 🎥 [Video Guides](https://www.youtube.com/@LangChain)
- 💬 [Discord Community](https://discord.gg/langchain)

### Integration Resources
- 🔌 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- 📖 [LangGraph + MAF Integration Guide](../AQ-TERADATA/LANGGRAPH_MCP_INTEGRATION.md)
- 🏗️ [Multi-Cloud Architecture Patterns](../AQ-TERADATA/ARCHITECTURE_PATTERNS.md)

---

**Document Version:** 1.0  
**Last Updated:** January 12, 2026  
**Author:** Arturo Quiroga, Sr. Partner Solutions Architect, Microsoft  
**Contributors:** Based on official documentation from Microsoft and LangChain  
**Next Review:** April 2026 (or when major versions release)

---

## Feedback & Contributions

This is a living document. If you find inaccuracies, have suggestions, or want to add comparisons:

- 📧 Open an issue on GitHub
- 💬 Discuss in Discord communities
- 🔄 Submit a pull request

**Disclaimer**: Both frameworks are rapidly evolving. Features and APIs may change. Always refer to official documentation for the most current information.

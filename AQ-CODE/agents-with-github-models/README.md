# Using Foundry Agents (V2) with GitHub Models

> **Microsoft Agent Framework (MAF) + Azure AI Foundry Agents V2 + GitHub Models**

This directory contains examples and documentation for using **Azure AI Foundry Agents V2** (backed by the `azure-ai-projects>=2.0.0b1` package), orchestrated by **Microsoft Agent Framework (MAF)**, with **GitHub Models** instead of Azure OpenAI or Azure AI Foundry models.

---

## 📋 Table of Contents

1. [What is This?](#what-is-this)
2. [Why Use GitHub Models?](#why-use-github-models)
3. [Architecture Overview](#architecture-overview)
4. [Prerequisites](#prerequisites)
5. [Quick Start](#quick-start)
6. [Examples Included](#examples-included)
7. [Tracing & Observability](#tracing--observability)
8. [Configuration](#configuration)
9. [Comparison with Other Model Providers](#comparison-with-other-model-providers)
10. [Troubleshooting](#troubleshooting)
11. [References](#references)

---

## What is This?

This demonstrates using **GitHub Models** as the LLM provider for agents built with:

- **Microsoft Agent Framework (MAF)**: The open-source SDK for building AI agents
- **Azure AI Foundry Agents V2**: Server-side agent management using `azure-ai-projects` 2.x package
- **GitHub Models**: Free access to popular models like GPT-4o, Llama, Phi, and more

### Key Insight

GitHub Models provides a **compatible OpenAI-style endpoint** that can be used with MAF's OpenAI clients, enabling:
- Free model access during development
- Easy switching between GitHub Models, Azure OpenAI, and Foundry models
- Same MAF code patterns across all providers

---

## Why Use GitHub Models?

### ✅ Advantages

| Feature | Benefit |
|---------|---------|
| **Free Access** | No Azure subscription required, free API access with rate limits |
| **Multiple Models** | GPT-4o, GPT-4o-mini, Llama 3.1/3.3, Phi-4, Mistral, and more |
| **OpenAI Compatible** | Drop-in replacement for OpenAI endpoints |
| **Quick Prototyping** | Start building immediately without cloud setup |
| **Community Models** | Access to open-source models (Llama, Phi, Mistral) |

### ⚠️ Limitations

| Limitation | Impact |
|------------|--------|
| **Rate Limits** | Lower than paid Azure OpenAI (suitable for dev/testing) |
| **No Enterprise Features** | No VNet, RBAC, or compliance guarantees |
| **Public Preview** | API stability not guaranteed for production |
| **No Foundry-Specific Features** | Can't use Foundry Agents V2 server-side persistence |

### 💡 When to Use

- **Development & Prototyping**: Test agent logic without cloud costs
- **Learning MAF**: Experiment with agent patterns
- **Open-Source Models**: Test Llama, Phi, Mistral models
- **Budget-Conscious Projects**: Free-tier development

### 🚫 When NOT to Use

- **Production Deployments**: Use Azure OpenAI or Foundry instead
- **Enterprise Requirements**: Need compliance, VNet, RBAC
- **High-Volume Applications**: Rate limits too restrictive
- **Foundry V2 Server Agents**: GitHub Models can't create Foundry server agents

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Application                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Microsoft Agent Framework (MAF)                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │   │
│  │  │ ChatAgent    │  │  Workflows   │  │  Tools   │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │   │
│  └────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │  OpenAI-Compatible Client                          │   │
│  │  (OpenAIChatClient / OpenAIResponsesClient)        │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
                 HTTPS (OpenAI Protocol)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              GitHub Models API                               │
│  https://models.inference.ai.azure.com                      │
│                                                              │
│  Models: GPT-4o, GPT-4o-mini, Llama 3.1/3.3,               │
│          Phi-4, Mistral, Cohere, etc.                       │
└─────────────────────────────────────────────────────────────┘
```

### Key Pattern

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# Configure OpenAI client for GitHub Models
client = OpenAIChatClient(
    model_id="gpt-4o-mini",  # GitHub Models model
    api_key="github_pat_YOUR_TOKEN",
    base_url="https://models.inference.ai.azure.com"  # GitHub endpoint
)

# Use with MAF like any other client
agent = ChatAgent(
    chat_client=client,
    instructions="You are a helpful assistant."
)
```

---

## Prerequisites

### 1. GitHub Account & Personal Access Token

1. **Sign up** at [github.com](https://github.com)
2. **Generate a Personal Access Token (PAT)**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Select scopes: (No special scopes needed, just basic authentication)
   - Copy the `github_pat_...` token

3. **Alternative: GitHub Models API Key**
   - Visit: https://github.com/marketplace/models
   - Select a model (e.g., GPT-4o-mini)
   - Click "Get API Key" to generate a dedicated key

### 2. Python Environment

```bash
# Python 3.10 or later required
python --version  # Should be 3.10+

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file:

```bash
# Copy template
cp .env.example .env

# Edit with your values
# Required:
GITHUB_TOKEN=github_pat_YOUR_TOKEN_HERE
GITHUB_MODEL=gpt-4o-mini

# Optional (defaults shown):
# GITHUB_BASE_URL=https://models.inference.ai.azure.com
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd /path/to/agents-with-github-models
pip install -r requirements.txt
```

### 2. Set GitHub Token

```bash
export GITHUB_TOKEN="github_pat_YOUR_TOKEN"
export GITHUB_MODEL="gpt-4o-mini"
```

### 3. Run Basic Example

```bash
python 01_basic_github_agent.py
```

**Expected Output:**
```
🔧 Configuring GitHub Models client...
   Endpoint: https://models.inference.ai.azure.com
   Model: gpt-4o-mini

🤖 Creating MAF agent with GitHub Models...

💬 Running agent...
User: What are the benefits of AI agents?

AI agents offer several benefits including autonomous decision-making, 
24/7 availability, consistency in responses, scalability, and the 
ability to handle complex multi-step tasks...
```

---

## Examples Included

### 📁 File Structure

```
agents-with-github-models/
├── README.md                          # This file
├── COMPARISON.md                      # vs Azure OpenAI/Foundry
├── .env.example                       # Environment template
├── requirements.txt                   # Python dependencies
│
├── 01_basic_github_agent.py          # Basic agent example
├── 02_github_with_tools.py           # Agent with function tools
├── 03_github_multi_agent.py          # Sequential multi-agent workflow
├── 04_github_parallel_agents.py      # Parallel agent execution
├── 05_github_sequential_devui.py     # Sequential workflow with DevUI (simple)
├── 06_github_parallel_devui.py       # Parallel agents with DevUI (simple)
├── 07_github_sequential_workflow.py  # Sequential with WorkflowBuilder + visualization
├── 08_github_parallel_workflow.py    # Parallel with WorkflowBuilder + visualization
├── 09_github_groupchat_workflow.py   # Group Chat with conversational orchestration
│
├── notebooks/
│   └── github_models_walkthrough.ipynb  # Interactive tutorial
│
├── workflow_outputs/                 # Saved workflow results
│
└── samples/
    ├── custom_tools.py                # Custom tool examples
    └── model_comparison.py            # Compare different GitHub models
```

### 🎯 Example 1: Basic Agent

**File:** `01_basic_github_agent.py`

Simple agent using GitHub Models GPT-4o-mini:

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
import os

client = OpenAIChatClient(
    model_id=os.getenv("GITHUB_MODEL", "gpt-4o-mini"),
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

agent = ChatAgent(
    chat_client=client,
    instructions="You are a helpful AI assistant."
)

result = await agent.run("Explain what AI agents are.")
print(result)
```

### 🎯 Example 2: Agent with Tools

**File:** `02_github_with_tools.py`

Agent with custom function tools (weather, calculator, time, knowledge base).

### 🎯 Example 3: Sequential Multi-Agent Workflow

**File:** `03_github_multi_agent.py`

Orchestrates three agents in sequence (Research → Analysis → Writing) where each agent's output feeds into the next.

### 🎯 Example 4: Parallel Agent Execution

**File:** `04_github_parallel_agents.py`

Runs multiple agents concurrently using `asyncio.gather()` for faster execution:

```python
# Create specialized agents
technical_agent = await create_specialized_agent("Technical Analyst", ...)
business_agent = await create_specialized_agent("Business Analyst", ...)
risk_agent = await create_specialized_agent("Risk Analyst", ...)
creative_agent = await create_specialized_agent("Creative Consultant", ...)

# Run all agents in parallel
results = await asyncio.gather(
    analyze_with_agent(technical_agent, topic, "Technical Analyst"),
    analyze_with_agent(business_agent, topic, "Business Analyst"),
    analyze_with_agent(risk_agent, topic, "Risk Analyst"),
    analyze_with_agent(creative_agent, topic, "Creative Consultant"),
    return_exceptions=True
)

# Sequential time: ~45-60s → Parallel time: ~15-20s (3-4x faster)
```

**Key Benefits:**
- 3-4x faster execution vs sequential (example 03)
- Multiple perspectives analyzed simultaneously
- Graceful error handling per agent
- Demonstrates real-world performance optimization

**Agent Roles:**
- Technical Analyst: Architecture and feasibility
- Business Analyst: Market opportunity and ROI
- Risk Analyst: Challenges and mitigation
- Creative Consultant: Innovation and differentiation

### 🎯 Example 5: Sequential Workflow with DevUI

**File:** `05_github_sequential_devui.py`

Interactive version of example 03 with DevUI web interface:

```bash
python 05_github_sequential_devui.py
# Opens browser at http://localhost:8080
```

**DevUI Benefits:**
- ✅ Interactive web interface for testing
- ✅ No hardcoded topics - test any input via browser
- ✅ Visual conversation history
- ✅ Real-time execution monitoring
- ✅ API endpoint for integration testing
- ✅ OpenAI-compatible API at `/v1/chat/completions`

**How It Works:**
1. Opens DevUI web interface
2. Select `sequential_workflow` from dropdown
3. Enter your topic (e.g., "AI education platform")
4. Watch agents execute: Research → Analysis → Writing
5. Get comprehensive report in browser

**When to Use:**
- Development and testing
- Demos and presentations
- Interactive exploration of topics
- Team collaboration

### 🎯 Example 6: Parallel Agents with DevUI

**File:** `06_github_parallel_devui.py`

Interactive version with 4 independent agents in DevUI:

```bash
python 06_github_parallel_devui.py
# Opens browser at http://localhost:8081
```

**Two Usage Modes:**

**Mode 1: Individual Conversations**
- Select one agent from dropdown
- Chat with Technical/Business/Risk/Creative specialist
- Get focused insights from their expertise
- Multi-turn conversations supported

**Mode 2: Parallel Comparison**
- Open 4 browser tabs
- Select different agent in each tab
- Ask same question to all agents
- Compare perspectives side-by-side

**Available Agents:**
- `technical_analyst` - Architecture, scalability, tech stack
- `business_analyst` - Market, revenue, competitive strategy
- `risk_analyst` - Compliance, security, risks
- `creative_consultant` - Innovation, UX, differentiation

**DevUI vs Script Comparison:**

| Feature | Examples 03/04 (Script) | Examples 05/06 (DevUI) |
|---------|------------------------|------------------------|
| Interface | Console/Terminal | Web Browser |
| Input | Hardcoded in Python | Interactive via UI |
| Testing | Edit code + re-run | Type in browser |
| History | Console scroll | Saved conversations |
| API Access | No | Yes (`/v1/*`) |
| Real-time Viz | No | Yes |
| Best For | Automation, CI/CD | Development, demos |

### 🎯 Example 7: Sequential Workflow with Visualization

**File:** `07_github_sequential_workflow.py`

PROPER sequential workflow using MAF's WorkflowBuilder with visual flow diagram:

```bash
python 07_github_sequential_workflow.py
# Opens browser at http://localhost:8082 with workflow visualization
```

**WorkflowBuilder Architecture:**
```
User Input → [Dispatcher] → [Research Agent] → [Analysis Agent] → [Writer Agent] → [Formatter]
```

**Key Features:**
- ✅ Visual workflow diagram in DevUI
- ✅ Proper sequential edges between components
- ✅ Structured input handling (TopicAnalysisInput)
- ✅ Message passing via WorkflowContext
- ✅ Output auto-saved to `workflow_outputs/`
- ✅ Enhanced observability and tracing

**vs Example 05:**
| Feature | Example 05 (Simple) | Example 07 (Workflow) |
|---------|---------------------|------------------------|
| Architecture | Wrapped agent | WorkflowBuilder |
| Visualization | Chat interface | Flow diagram |
| Edges | Manual chaining | Workflow edges |
| Input | Direct message | Structured (Pydantic) |
| Output | Console only | File + console |
| Observability | Basic | Enhanced with tracing |

**When to Use:**
- Need visual workflow representation
- Building complex sequential pipelines
- Require structured input/output
- Want enhanced observability
- Production-ready workflows

### 🎯 Example 8: Parallel Workflow with Visualization

**File:** `08_github_parallel_workflow.py`

PROPER concurrent workflow with fan-out/fan-in pattern and visual diagram:

```bash
python 08_github_parallel_workflow.py
# Opens browser at http://localhost:8083 with parallel workflow visualization
```

**WorkflowBuilder Architecture (Fan-Out/Fan-In):**
```
                  ┌→ Technical Analyst →┐
                  ├→ Business Analyst  →┤
Input → Dispatcher ├→ Risk Analyst     →├→ Aggregator → Output
                  ├→ Creative Consultant→┤
                  └───────────────────┘
```

**Key Features:**
- ✅ Visual fan-out/fan-in diagram in DevUI
- ✅ True parallel execution (all agents simultaneously)
- ✅ Automatic result aggregation
- ✅ Structured input (ProductAnalysisInput)
- ✅ ~15-20s total (vs ~60s sequential)
- ✅ Output auto-saved to `workflow_outputs/`

**vs Example 06:**
| Feature | Example 06 (Individual) | Example 08 (Workflow) |
|---------|-------------------------|------------------------|
| Architecture | 4 separate agents | Unified workflow |
| Visualization | Agent list | Fan-out/fan-in diagram |
| Execution | Manual per agent | One input → all agents |
| Aggregation | None (manual) | Automatic |
| Result Format | Individual chats | Combined analysis |
| Observability | Per-agent | Workflow-level |

**Performance:**
- Sequential (07): ~55-70 seconds (agents wait)
- Parallel (08): ~15-20 seconds (all run simultaneously)
- **Speedup: 3-4x faster!**

**When to Use:**
- Need multiple independent perspectives
- Speed is critical
- Want automatic result aggregation
- Building production workflows
- Require visual representation

### 🎯 Example 9: Group Chat Workflow with Orchestration

**File:** `09_github_groupchat_workflow.py`

Advanced CONVERSATIONAL workflow where agents DISCUSS collaboratively, managed by an orchestrator:

```bash
python 09_github_groupchat_workflow.py
# Opens browser at http://localhost:8084 with group chat visualization
```

**GroupChatBuilder Architecture (Conversational):**
```
User Input → [Orchestrator selects speaker based on context]
                ↓
              [Product Manager: Proposes feature]
                ↓
              [Orchestrator selects next based on discussion]
                ↓
              [Technical Architect: Evaluates feasibility]
                ↓
              [Orchestrator selects next based on discussion]
                ↓
              [UX Designer: Assesses user experience]
                ↓
              [Orchestrator selects next based on discussion]
                ↓
              [Business Analyst: Reviews ROI & recommends]
                ↓
              Final collaborative output
```

**Key Features:**
- ✅ Dynamic CONVERSATION management (not predetermined flow)
- ✅ Agents reference each other's contributions
- ✅ Orchestrator adapts based on discussion state
- ✅ Collaborative decision-making pattern
- ✅ ~60s for 4-person feature review discussion

**Scenario: Product Feature Review**
- **Product Manager**: Proposes feature vision and user value
- **Technical Architect**: Evaluates implementation feasibility
- **UX Designer**: Assesses user experience and design impact
- **Business Analyst**: Reviews market fit, ROI, and recommends

**vs Examples 07/08:**
| Feature | Sequential (07) | Parallel (08) | Group Chat (09) |
|---------|-----------------|---------------|-----------------|
| Flow | A→B→C (linear) | All simultaneously | **Conversation** |
| Interaction | Pass results | Independent | **Build on each other** |
| Manager | None | None | **Orchestrator** |
| Best For | Pipelines | Speed | **Collaboration** |
| Example | ETL, data flow | Independent reviews | **Team discussions** |

**GroupChatBuilder Pattern:**
```python
from agent_framework import GroupChatBuilder, GroupChatStateSnapshot

def select_next_speaker(state: GroupChatStateSnapshot) -> str | None:
    """Control who speaks next based on conversation state.
    
    Returns: Participant name or None to finish
    """
    # Access conversation history, round count, etc.
    # Return next speaker name or None to end
    pass

workflow = (
    GroupChatBuilder()
    .set_select_speakers_func(select_next_speaker, display_name="Orchestrator")
    .participants([pm_agent, tech_agent, ux_agent, biz_agent])
    .build()
)
```

**Example Feature Ideas:**
- "AI-powered personalized learning platform for corporate training"
- "Blockchain-based supply chain transparency system"
- "Telemedicine platform with AI-assisted diagnostics"
- "Voice-activated smart home with privacy-first local processing"

**When to Use:**
- Collaborative problem-solving needed
- Multiple perspectives should interact
- Iterative refinement important
- Mimicking real team discussions
- Building consensus or reviewing ideas

---

## 📊 Workflow Examples Summary

| Example | Type | DevUI | Visualization | Best For |
|---------|------|-------|---------------|----------|
| **03** | Sequential | ❌ | Console | Scripts, automation |
| **04** | Parallel | ❌ | Console | Scripts, comparison |
| **05** | Sequential | ✅ | Chat UI | Interactive testing |
| **06** | Parallel | ✅ | Agent list | Individual conversations |
| **07** | Sequential | ✅ | **Flow diagram** | **Production workflows** |
| **08** | Parallel | ✅ | **Fan-out/fan-in** | **Production workflows** |
| **09** | Group Chat | ✅ | **Conversation** | **Collaborative decision-making** |

**Recommendation:**
- 📜 **Learning:** Start with 01 → 02 → 03 → 04
- 🔧 **Development:** Use 05 or 06 for quick testing
- 🏭 **Production:** Use 07, 08, or 09 depending on pattern:
  - **Sequential (07)**: Linear data pipelines, ETL flows
  - **Parallel (08)**: Independent analyses, speed-critical
  - **Group Chat (09)**: Team collaboration, consensus-building

### 🎯 Example 2 Code Details: Agent with Tools

**File:** `02_github_with_tools.py`

Agent with custom function tools:

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
import os

def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72°F, sunny"

client = OpenAIChatClient(
    model_id="gpt-4o-mini",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

agent = ChatAgent(
    chat_client=client,
    instructions="You are a helpful assistant with weather capabilities.",
    tools=[get_weather]
)

result = await agent.run("What's the weather in Seattle?")
print(result)
```

### 🎯 Example 3: Multi-Agent Workflow

**File:** `03_github_multi_agent.py`

Multiple agents collaborating:

```python
from agent_framework import WorkflowGraph
from agent_framework.openai import OpenAIChatClient
import os

# Create GitHub Models client
github_client = OpenAIChatClient(
    model_id="gpt-4o-mini",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

# Research agent
research_agent = ChatAgent(
    chat_client=github_client,
    instructions="You are a research analyst.",
    name="Researcher"
)

# Writer agent
writer_agent = ChatAgent(
    chat_client=github_client,
    instructions="You are a technical writer.",
    name="Writer"
)

# Create workflow
workflow = WorkflowGraph()
workflow.add_agent("research", research_agent)
workflow.add_agent("write", writer_agent)
workflow.add_edge("research", "write")

result = await workflow.run("Research AI agents and write a summary")
```

---

## Tracing & Observability

Examples 07 and 08 (WorkflowBuilder-based workflows) include **comprehensive tracing support** for observability and debugging.

### Quick Start: Console Tracing

Enable console tracing to see agent execution details in your terminal:

```bash
# Enable console tracing
export ENABLE_CONSOLE_TRACING=true

# Run workflow with tracing
python 07_github_sequential_workflow.py
```

You'll see detailed trace output showing:
- Agent operations and timing
- Workflow stage progression
- Performance metrics per agent
- Overall execution timeline

### Tracing Options

| Mode | Setup | Use Case |
|------|-------|----------|
| **Console** | `ENABLE_CONSOLE_TRACING=true` | Development, debugging |
| **Application Insights** | `APPLICATIONINSIGHTS_CONNECTION_STRING=...` | Production monitoring |
| **OTLP** | `OTLP_ENDPOINT=http://localhost:4317` | Local Jaeger/Zipkin |

### Complete Guide

See [TRACING_GUIDE.md](TRACING_GUIDE.md) for:
- Detailed setup instructions for each tracing backend
- DevUI integration and visualization
- Comparing sequential vs parallel execution traces
- Troubleshooting common issues
- Best practices for development vs production

### DevUI Trace Visualization

When tracing is enabled, DevUI shows:
- ✅ **Operation names** instead of "Unknown Operation"
- ✅ **Execution timeline** with start/end times
- ✅ **Trace details** with span information
- ✅ **Performance metrics** per agent

Example trace output in DevUI:
```
Operation: research_agent        Duration: 18.2s
Operation: analysis_agent        Duration: 15.1s  (waited for research)
Operation: writer_agent          Duration: 19.8s  (waited for analysis)
Total workflow time: 55.3s
```

---

## Configuration

### Available GitHub Models

| Model | ID | Use Case | Rate Limit |
|-------|-----|----------|------------|
| **GPT-4o** | `gpt-4o` | Complex reasoning, latest features | Lower RPM |
| **GPT-4o-mini** | `gpt-4o-mini` | Fast, cost-effective, general use | Higher RPM |
| **Llama 3.3 70B** | `Llama-3.3-70B-Instruct` | Open-source, long context | Medium RPM |
| **Llama 3.1 405B** | `Llama-3.1-405B-Instruct` | Largest Llama, best reasoning | Lower RPM |
| **Phi-4** | `Phi-4` | Small, efficient, code-focused | Higher RPM |
| **Mistral Large 2** | `Mistral-Large-2` | Multilingual, reasoning | Medium RPM |

### Environment Variables

```bash
# Required
GITHUB_TOKEN=github_pat_YOUR_TOKEN         # Your GitHub PAT

# Model Selection
GITHUB_MODEL=gpt-4o-mini                   # Default model
GITHUB_BASE_URL=https://models.inference.ai.azure.com  # GitHub endpoint

# Optional MAF Settings
MAF_LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING
MAF_ENABLE_TRACING=true                    # OpenTelemetry tracing
```

### Rate Limits

GitHub Models free tier has rate limits:

| Model Type | Requests/Minute | Tokens/Minute |
|------------|-----------------|---------------|
| GPT-4o | 15 RPM | 150K TPM |
| GPT-4o-mini | 15 RPM | 150K TPM |
| Llama 3.1/3.3 | 15 RPM | 150K TPM |
| Phi-4 | 15 RPM | 150K TPM |

**Note**: Limits subject to change. Check [GitHub Models documentation](https://docs.github.com/en/github-models).

---

## Comparison with Other Model Providers

### Quick Reference

| Feature | GitHub Models | Azure OpenAI | Azure AI Foundry |
|---------|---------------|--------------|------------------|
| **Cost** | Free (rate-limited) | Pay-per-token | Pay-per-token + service |
| **Setup Complexity** | Minimal (GitHub token) | Moderate (Azure setup) | Complex (Foundry project) |
| **Rate Limits** | ~15 RPM | Much higher | Highest |
| **Models** | GPT-4o, Llama, Phi | GPT-4o, GPT-4, 3.5 | All Azure + custom |
| **Enterprise Features** | None | Yes (VNet, RBAC) | Yes (Full governance) |
| **MAF Integration** | ✅ Full support | ✅ Full support | ✅ Full support |
| **Foundry V2 Agents** | ❌ Client-side only | ❌ Client-side only | ✅ Server-side agents |
| **Production Ready** | ❌ Dev/test only | ✅ Yes | ✅ Yes |

### Detailed Comparison

See [COMPARISON.md](./COMPARISON.md) for in-depth analysis.

---

## Troubleshooting

### Common Issues

#### 1. Authentication Error

```
Error: 401 Unauthorized
```

**Solution:**
- Verify `GITHUB_TOKEN` is set correctly
- Check token hasn't expired
- Ensure token has required permissions

```bash
# Test token
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://models.inference.ai.azure.com/models
```

#### 2. Rate Limit Exceeded

```
Error: 429 Too Many Requests
```

**Solution:**
- Add delays between requests
- Use exponential backoff
- Consider Azure OpenAI for higher limits

```python
import time
import asyncio

# Add delay between calls
await agent.run("Query 1")
await asyncio.sleep(5)  # Wait 5 seconds
await agent.run("Query 2")
```

#### 3. Model Not Found

```
Error: Model 'xyz' not found
```

**Solution:**
- Check [GitHub Models marketplace](https://github.com/marketplace/models) for available models
- Use exact model ID from documentation
- Try default: `gpt-4o-mini`

#### 4. Base URL Issues

```
Error: Connection refused
```

**Solution:**
- Verify `base_url="https://models.inference.ai.azure.com"`
- Check network connectivity
- Try direct curl test

```bash
curl https://models.inference.ai.azure.com/models
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in .env
MAF_LOG_LEVEL=DEBUG
```

---

## Best Practices

### 1. Error Handling

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
import os
import asyncio

async def robust_agent_call():
    client = OpenAIChatClient(
        model_id=os.getenv("GITHUB_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com"
    )
    
    agent = ChatAgent(chat_client=client, instructions="You are helpful.")
    
    try:
        result = await agent.run("Test query")
        return result
    except Exception as e:
        if "429" in str(e):  # Rate limit
            print("Rate limited, waiting...")
            await asyncio.sleep(60)
            return await agent.run("Test query")
        elif "401" in str(e):  # Auth error
            print("Authentication failed, check GITHUB_TOKEN")
            raise
        else:
            print(f"Unexpected error: {e}")
            raise
```

### 2. Rate Limit Management

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, rpm=15):
        self.rpm = rpm
        self.calls = []
    
    async def wait_if_needed(self):
        now = datetime.now()
        # Remove calls older than 1 minute
        self.calls = [c for c in self.calls if now - c < timedelta(minutes=1)]
        
        if len(self.calls) >= self.rpm:
            wait_time = 60 - (now - self.calls[0]).seconds
            print(f"Rate limit reached, waiting {wait_time}s")
            await asyncio.sleep(wait_time)
        
        self.calls.append(now)

limiter = RateLimiter(rpm=15)

async def call_agent(query):
    await limiter.wait_if_needed()
    return await agent.run(query)
```

### 3. Model Selection

```python
# Choose model based on task
def get_client_for_task(task_type):
    models = {
        "simple": "gpt-4o-mini",      # Fast, efficient
        "complex": "gpt-4o",           # Best reasoning
        "code": "Phi-4",               # Code-optimized
        "long_context": "Llama-3.3-70B-Instruct"  # 128K context
    }
    
    return OpenAIChatClient(
        model_id=models.get(task_type, "gpt-4o-mini"),
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com"
    )
```

---

## Migration Path

### From GitHub Models to Azure OpenAI

When ready for production:

```python
# BEFORE (GitHub Models)
from agent_framework.openai import OpenAIChatClient

client = OpenAIChatClient(
    model_id="gpt-4o-mini",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

# AFTER (Azure OpenAI)
from agent_framework.azure import AzureOpenAIChatClient

client = AzureOpenAIChatClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name="gpt-4o-mini",
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

# Agent code stays the same!
agent = ChatAgent(chat_client=client, instructions="...")
```

### From Client-Side to Foundry V2 Server Agents

```python
# BEFORE (Client-side with GitHub Models)
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

client = OpenAIChatClient(...)
agent = ChatAgent(chat_client=client, instructions="...")

# AFTER (Foundry V2 server-side)
from agent_framework.azure import AzureAIClient
from azure.identity import DefaultAzureCredential

client = AzureAIClient(
    endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

agent = client.create_agent(
    model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
    instructions="...",
    name="MyAgent",
    use_latest_version=True
)
```

---

## References

### Official Documentation

- **GitHub Models**: https://github.com/marketplace/models
- **GitHub Models Docs**: https://docs.github.com/en/github-models
- **Microsoft Agent Framework**: https://aka.ms/agent-framework
- **MAF Documentation**: https://learn.microsoft.com/en-us/agent-framework/
- **Azure AI Foundry**: https://learn.microsoft.com/azure/ai-studio/

### Related Resources

- **MAF GitHub Repository**: https://github.com/microsoft/agent-framework
- **OpenAI API Reference**: https://platform.openai.com/docs/api-reference
- **Azure OpenAI Service**: https://learn.microsoft.com/azure/ai-services/openai/

### Community

- **MAF Discord**: https://discord.gg/b5zjErwbQM
- **GitHub Discussions**: https://github.com/microsoft/agent-framework/discussions
- **Stack Overflow**: Tag `agent-framework` or `azure-ai`

---

## Contributing

Found an issue or have suggestions? Please:

1. Check existing examples
2. Test with latest MAF version
3. Open an issue with details
4. Submit a PR with improvements

---

## License

This code follows the Microsoft Agent Framework license. See [LICENSE](../../LICENSE) for details.

---

**Last Updated:** January 1, 2026  
**MAF Version:** 1.0.0b251223  
**Author:** Microsoft Agent Framework Community

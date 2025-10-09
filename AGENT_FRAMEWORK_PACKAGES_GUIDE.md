# Agent Framework Packages Guide

**Generated:** October 8, 2025  
**Purpose:** Understanding installed agent-framework packages and resolving import issues

---

## 🔍 Summary

This repository has **18 agent-framework packages** installed in `.venv`. Many of these packages had **missing descriptions** and some were experiencing **import errors** due to a broken installation.

### Key Finding: Installation Issue Resolved ✅

**Problem:** The `agent_framework/__init__.py` file was empty in the virtual environment, causing import errors:
```python
ImportError: cannot import name 'ChatMessage' from 'agent_framework'
```

**Solution:** Reinstalled `agent-framework-core` in editable mode from source:
```bash
.venv/bin/pip install -e python/packages/core --no-deps --force-reinstall
```

Now all imports work correctly! ✅

---

## 📦 Installed Packages Overview

### Core Framework (Required)
| Package | Version | Status | Description |
|---------|---------|--------|-------------|
| `agent-framework` | 1.0.0b251001 | ✅ Working | Meta-package containing all core abstractions |
| `agent-framework-core` | 1.0.0b251001 | ✅ Working | Core package with all abstractions and implementations |

### Integration Packages (Optional)
| Package | Version | Status | Purpose |
|---------|---------|--------|---------|
| `agent-framework-a2a` | 1.0.0b251001 | ⚠️ Needs Core | Agent-to-Agent communication integration |
| `agent-framework-azure-ai` | 1.0.0b251001 | ⚠️ Needs Core | Azure AI Foundry integration |
| `agent-framework-copilotstudio` | 1.0.0b251001 | ⚠️ Needs Core | Copilot Studio integration |
| `agent-framework-devui` | 1.0.0b251001 | ⚠️ Needs Core | Debug UI with OpenAI-compatible API server |
| `agent-framework-mem0` | 1.0.0b251001 | ⚠️ Needs Core | Mem0 memory integration |
| `agent-framework-redis` | 1.0.0b251001 | ⚠️ Needs Core | Redis storage integration |

### Provider Packages (Placeholder - No Modules)
| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| `agent-framework-anthropic` | 0.0.0a1 | 📦 Placeholder | Anthropic Claude provider (future) |
| `agent-framework-aws` | 0.0.0a1 | 📦 Placeholder | AWS integration (future) |
| `agent-framework-azure` | 0.0.0 | 📦 Placeholder | "Coming soon" |
| `agent-framework-claude` | 0.0.0a1 | 📦 Placeholder | Claude provider (future) |
| `agent-framework-community` | 0.0.0a1 | 📦 Placeholder | Community integrations (future) |
| `agent-framework-gemini` | 0.0.0a1 | 📦 Placeholder | Google Gemini provider (future) |
| `agent-framework-google` | 0.0.0a1 | 📦 Placeholder | Google integration (future) |
| `agent-framework-runtime` | 0.0.0a1 | 📦 Placeholder | Runtime environment (future) |

### Experimental Packages
| Package | Version | Status | Purpose |
|---------|---------|--------|---------|
| `agent-framework-lab` | 0.0.1a0 | 🧪 Experimental | Lab modules (GAIA, Lightning, TAU2) |

---

## 🔧 What Each Package Does

### 1. **agent-framework-core** (Essential)
The foundation package containing:
- **Core Types**: `ChatMessage`, `Role`, `AgentThread`, `AgentRunResponse`
- **Agents**: Base agent classes and client implementations
- **Workflows**: `WorkflowBuilder`, `Executor`, `WorkflowContext`, `handler`
- **Tools**: Function calling, tool protocols, `ai_function` decorator
- **Memory**: Message stores, conversation history
- **Middleware**: Request/response interceptors
- **Telemetry**: Observability and tracing setup
- **MCP**: Model Context Protocol support

**Import from:**
```python
from agent_framework import (
    ChatMessage, Role,
    Executor, WorkflowBuilder, WorkflowContext, handler,
    AgentThread, AgentRunResponse,
    ai_function,
    setup_observability
)
```

### 2. **agent-framework-azure-ai** (Azure AI Foundry)
Azure AI Foundry integration for agents hosted on Azure:
- `AzureOpenAIChatClient`: Create agents using Azure OpenAI
- Integration with Azure AI Projects
- Azure authentication support

**Import from:**
```python
from agent_framework.azure import AzureOpenAIChatClient
```

**Example:**
```python
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient

client = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
)

agent = client.create_agent(
    instructions="You are a helpful assistant",
    name="my_agent"
)
```

### 3. **agent-framework-devui** (Developer UI)
Debug and test UI for agent workflows:
- Web interface on http://localhost:8096 (configurable)
- OpenAI-compatible REST API
- Interactive chat interface
- Trace visualization (when enabled)

**Import from:**
```python
from agent_framework.devui import serve
```

**Example:**
```python
serve(
    entities=[workflow],
    port=8096,
    auto_open=True,
    tracing_enabled=True
)
```

### 4. **agent-framework-a2a** (Agent-to-Agent)
Enable agents to communicate with each other:
- Agent-to-agent protocol support
- Message routing between agents
- Requires A2A SDK (`a2a-sdk`)

### 5. **agent-framework-mem0** (Memory Integration)
Mem0 integration for advanced memory management:
- Long-term memory storage
- Semantic memory retrieval
- User/session-based memory

### 6. **agent-framework-redis** (Redis Storage)
Redis-based storage for agents:
- Message history storage
- Distributed agent state
- Session management

### 7. **agent-framework-lab** (Experimental)
Experimental research modules:

#### Subpackages:
- **`agent_framework_lab_gaia`**: GAIA benchmark scorer for agent evaluation
- **`agent_framework_lab_lightning`**: Training/fine-tuning utilities for agents
- **`agent_framework_lab_tau2`**: Advanced conversation management:
  - `SlidingWindowChatMessageStore`: Memory windowing
  - Message utilities (flipping, logging)
  - Experimental memory strategies

**Import from:**
```python
from agent_framework.lab.gaia import gaia_scorer
from agent_framework.lab.lightning import init as lightning_init
from agent_framework.lab.tau2 import SlidingWindowChatMessageStore
```

### 8. **agent-framework-copilotstudio** (Copilot Studio)
Integration with Microsoft Copilot Studio:
- Copilot Studio agent hosting
- Activity protocol support
- Middleware for Copilot Studio agents

---

## ✅ Correct Import Patterns

### Basic Agent Workflow
```python
from agent_framework import (
    ChatMessage,
    Role,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.devui import serve
from agent_framework.observability import setup_observability
```

### With Tracing
```python
from agent_framework.observability import get_tracer, setup_observability
from opentelemetry.trace import SpanKind

# Setup
setup_observability(
    enable_sensitive_data=True,
    applicationinsights_connection_string=conn_str
)

# Use tracer
tracer = get_tracer(__name__)
with tracer.start_span("my_operation", kind=SpanKind.INTERNAL):
    # ... your code
```

### Custom Executors
```python
from agent_framework import Executor, WorkflowContext, handler
from pydantic import BaseModel

class MyInput(BaseModel):
    text: str

class MyExecutor(Executor):
    @handler
    async def process(self, input_data: MyInput, ctx: WorkflowContext) -> None:
        # Process and dispatch
        await ctx.send_message(...)
```

---

## 🚀 Quick Start: Running Your Workflows

All your workflow files in `AQ-CODE/orchestration/` should now work!

### Test a Workflow
```bash
.venv/bin/python AQ-CODE/orchestration/healthcare_product_launch_devui.py
```

### Example Output
```
📊 Tracing Mode: Application Insights (Direct)
======================================================================
🚀 Launching Healthcare Product Launch Workflow in DevUI
======================================================================
✅ Workflow Type: Healthcare Product Analysis (Fan-out/Fan-in)
✅ Participants: 5 specialized healthcare agents
✅ Web UI: http://localhost:8094
✅ API: http://localhost:8094/v1/*
⌨️  Press Ctrl+C to stop the server
```

### Available Workflows
- `healthcare_product_launch_devui.py` - Healthcare product analysis (5 agents)
- `smart_city_infrastructure_devui.py` - Smart city infrastructure (7 agents)
- Other orchestration examples in `AQ-CODE/orchestration/`

---

## 🐛 Troubleshooting

### "cannot import name 'ChatMessage'"
**Fix:** Reinstall core package in editable mode:
```bash
.venv/bin/pip install -e python/packages/core --no-deps --force-reinstall
```

### "cannot import name 'AzureOpenAIChatClient'"
**Fix:** Check import path (it's in `agent_framework.azure`, not `agent_framework_azure_ai`):
```python
# ❌ Wrong
from agent_framework_azure_ai import AzureOpenAIChatClient

# ✅ Correct
from agent_framework.azure import AzureOpenAIChatClient
```

### Integration packages fail to import
These packages depend on the core package. Make sure core is installed in editable mode first.

### Provider packages (anthropic, claude, etc.) not found
These are placeholder packages with no actual code yet (version 0.0.0a1). They're reserved for future use.

---

## 📊 Package Inventory Tool

A Python script was created to automatically inventory all agent_framework packages:

### Location
```
python/tools/inventory_agent_framework.py
```

### Usage
```bash
# Generate markdown report
.venv/bin/python python/tools/inventory_agent_framework.py \
    --format markdown \
    --output agent_framework_inventory.md

# Generate JSON report
.venv/bin/python python/tools/inventory_agent_framework.py \
    --format json \
    --pretty \
    --output agent_framework_inventory.json
```

### What It Does
- Discovers all `agent-framework-*` distributions
- Attempts to import each module
- Lists public classes and functions
- Captures import errors
- Generates comprehensive reports

The full inventory is available in: `agent_framework_inventory.md` (331 lines)

---

## 🔄 Reinstalling Everything Cleanly

If you encounter persistent issues, here's how to rebuild the environment:

### Option 1: Reinstall Core Only (Recommended)
```bash
.venv/bin/pip install -e python/packages/core --force-reinstall
```

### Option 2: Reinstall All Local Packages
```bash
# Core
.venv/bin/pip install -e python/packages/core --force-reinstall

# Optional: Install other local packages
.venv/bin/pip install -e python/packages/devui
.venv/bin/pip install -e python/packages/azure-ai
.venv/bin/pip install -e python/packages/a2a
# ... etc
```

### Option 3: Full Environment Rebuild
```bash
# Remove and recreate venv
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# Install from source
pip install -e python/packages/core
pip install -r requirements.txt  # if you have one
```

---

## 📚 Further Documentation

### Official Docs
- Check `python/packages/core/README.md` for core package docs
- Check `AQ-CODE/azure_ai/README.md` for Azure AI examples
- Review `docs/` directory for design specs

### Examples
- `AQ-CODE/_start-here/` - Basic tutorials
- `AQ-CODE/azure_ai/` - Azure AI examples
- `AQ-CODE/orchestration/` - Complex workflows
- `AQ-CODE/parallelism/` - Parallel execution patterns

### Community
- Repository: https://github.com/Arturo-Quiroga-MSFT/agent-framework-public
- Issues: Use GitHub Issues for questions

---

## ✨ Key Takeaways

1. **Core package is essential** - Always install `agent-framework-core` first
2. **Use editable mode** - Install from source with `-e` flag for development
3. **Import from `agent_framework`** - Not from `agent_framework_core` or `agent_framework_*`
4. **Provider packages are placeholders** - Anthropic, Claude, etc. are reserved for future
5. **Lab package is experimental** - Use with caution, APIs may change
6. **DevUI is your friend** - Great for testing and debugging workflows

---

**Status:** All import issues resolved ✅  
**Tested:** Healthcare workflow running successfully  
**Next Steps:** Run your other workflows and explore the framework!

# Agent Framework Quick Reference

## 🎯 Essential Imports
```python
# Core types
from agent_framework import ChatMessage, Role, AgentThread, AgentRunResponse

# Workflow building
from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler

# Azure AI client
from agent_framework.azure import AzureOpenAIChatClient

# Developer UI
from agent_framework.devui import serve

# Observability
from agent_framework.observability import setup_observability, get_tracer
```

## 📦 Package Purpose Quick Lookup

| Need to... | Use Package | Import From |
|------------|-------------|-------------|
| Build agents & workflows | `agent-framework-core` | `agent_framework` |
| Use Azure OpenAI | `agent-framework-azure-ai` | `agent_framework.azure` |
| Debug with web UI | `agent-framework-devui` | `agent_framework.devui` |
| Agent-to-agent comms | `agent-framework-a2a` | `agent_framework.a2a` |
| Memory with Mem0 | `agent-framework-mem0` | `agent_framework.mem0` |
| Redis storage | `agent-framework-redis` | `agent_framework.redis` |
| Copilot Studio | `agent-framework-copilotstudio` | `agent_framework.copilotstudio` |
| Experimental features | `agent-framework-lab` | `agent_framework.lab.*` |

## 🔧 Common Patterns

### Create an Azure OpenAI Agent
```python
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient

client = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint="https://your-resource.openai.azure.com",
    deployment_name="gpt-4"
)

agent = client.create_agent(
    instructions="You are a helpful assistant",
    name="my_agent"
)
```

### Build a Simple Workflow
```python
from agent_framework import WorkflowBuilder

builder = WorkflowBuilder()
builder.set_start_executor(dispatcher)
builder.add_fan_out_edges(dispatcher, [agent1, agent2, agent3])
builder.add_fan_in_edges([agent1, agent2, agent3], aggregator)
workflow = builder.build()
```

### Launch DevUI
```python
from agent_framework.devui import serve

serve(
    entities=[workflow],
    port=8096,
    auto_open=True,
    tracing_enabled=True
)
```

### Setup Tracing
```python
from agent_framework.observability import setup_observability

# Console tracing
setup_observability(enable_sensitive_data=True)

# Application Insights
setup_observability(
    enable_sensitive_data=True,
    applicationinsights_connection_string="InstrumentationKey=..."
)

# OTLP (Jaeger, Zipkin)
setup_observability(
    enable_sensitive_data=True,
    otlp_endpoint="http://localhost:4317"
)
```

## 🐛 Quick Fixes

### Import Error: "cannot import name 'ChatMessage'"
```bash
.venv/bin/pip install -e python/packages/core --no-deps --force-reinstall
```

### Wrong Import Path
```python
# ❌ Don't do this
from agent_framework_azure_ai import AzureOpenAIChatClient
from agent_framework_core import ChatMessage

# ✅ Do this
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import ChatMessage
```

## 📁 File Locations

| Item | Path |
|------|------|
| Inventory script | `python/tools/inventory_agent_framework.py` |
| Full inventory | `agent_framework_inventory.md` |
| Complete guide | `AGENT_FRAMEWORK_PACKAGES_GUIDE.md` |
| Core package source | `python/packages/core/` |
| Example workflows | `AQ-CODE/orchestration/` |
| Basic tutorials | `AQ-CODE/_start-here/` |
| Azure AI examples | `AQ-CODE/azure_ai/` |

## 🚀 Test Your Setup

```bash
# Test imports
.venv/bin/python -c "from agent_framework import ChatMessage, Role, Executor; print('✅ OK')"

# Run example workflow
.venv/bin/python AQ-CODE/orchestration/healthcare_product_launch_devui.py

# Run inventory
.venv/bin/python python/tools/inventory_agent_framework.py --format markdown
```

## 📚 Resources

- **Full Guide**: `AGENT_FRAMEWORK_PACKAGES_GUIDE.md`
- **Examples**: `AQ-CODE/` directory
- **Source Code**: `python/packages/`
- **Repository**: github.com/Arturo-Quiroga-MSFT/agent-framework-public

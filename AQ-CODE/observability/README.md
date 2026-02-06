# Observability Samples

Workshop-ready observability demonstrations for Microsoft Agent Framework with Azure AI Foundry.

**Last Updated**: February 2026  
**MAF Observability API**: Current (configure_otel_providers / enable_instrumentation)

## What Changed (Feb 2026 vs Dec 2025)

| Area | December 2025 (Old) | February 2026 (Current) |
|------|---------------------|------------------------|
| **Azure setup** | `setup_observability(appinsights_conn_str=...)` | `AzureAIClient.configure_azure_monitor()` |
| **Generic setup** | `setup_observability()` | `configure_otel_providers()` |
| **OTLP env var** | `OTLP_ENDPOINT` | `OTEL_EXPORTER_OTLP_ENDPOINT` (standard) |
| **Instrumentation** | `ENABLE_OTEL=true` | `ENABLE_INSTRUMENTATION=true` |
| **Console output** | Automatic fallback | `ENABLE_CONSOLE_EXPORTERS=true` (opt-in) |
| **Tool decorator** | Plain function | `@tool(approval_mode="never_require")` |
| **Agent identity** | No `id` param | `id="weather-agent"` for Control Plane |
| **Client class** | `AzureAIAgentClient` + `AgentsClient` | `AzureAIClient(project_client=...)` |
| **Local dev** | DevUI only | Aspire Dashboard, AI Toolkit, DevUI |
| **Dashboards** | Azure Portal only | + Grafana (aka.ms/amg/dash/af-agent) |

## 📁 Contents

| File | Description | Workshop Module |
|------|-------------|-----------------||
| `observability_azure_ai_agent.py` | Azure AI agent with Application Insights integration | Module 4 |
| `observability_workflow.py` | Customer feedback analysis workflow with telemetry | Module 4 |
| `redis_demo_preferences.py` | RedisProvider demo - smart preference memory (console) | Module 5 |
| `redis_demo_persistence.py` | RedisChatMessageStore demo - resume conversations (console) | Module 5 |
| `redis_demo_multi_agent.py` | Multi-agent isolation with separate memory scopes (console) | Module 5 |
| `redis_demo_preferences_devui.py` | RedisProvider demo - interactive UI (port 8000) | Module 5 |
| `redis_demo_persistence_devui.py` | RedisChatMessageStore demo - interactive UI (port 8001) | Module 5 |
| `redis_demo_multi_agent_devui.py` | Multi-agent demo - dual UI (ports 8002 & 8003) | Module 5 |
| `OBSERVABILITY_SAMPLES.md` | Comprehensive documentation (35-minute module) | Reference |
| `REDIS_PERSISTENCE_SAMPLES.md` | Redis persistence workshop (45-minute module) | Reference |
| `.env` | Environment configuration (not committed to git) | - |

## 🚀 Quick Start

### Observability Demos

```bash
# Navigate to observability directory
cd AQ-CODE/observability

# Run Azure AI Agent demo (with real OpenWeatherMap API)
python observability_azure_ai_agent.py

# Run Workflow demo (customer feedback analysis)
python observability_workflow.py
```

### Redis Persistence Demos

```bash
# Start Redis (if not already running)
docker run --name redis -p 6379:6379 -d redis:8.0.3

# Console demos (automated scripts)
python redis_demo_preferences.py
python redis_demo_persistence.py
python redis_demo_multi_agent.py

# DevUI demos (interactive workshops - RECOMMENDED)
python redis_demo_preferences_devui.py      # http://localhost:8000
python redis_demo_persistence_devui.py      # http://localhost:8001
python redis_demo_multi_agent_devui.py      # http://localhost:8002 & 8003
```

## 📋 Prerequisites

### Environment Variables (in `.env`)

```bash
# Required for both samples
AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/..."

# Required for observability_azure_ai_agent.py
OPENWEATHER_API_KEY="your-key-here"  # Get free key at openweathermap.org/api

# Tracing configuration (standard OTEL env vars)
# Option 1: OTLP (Aspire Dashboard, Jaeger, Zipkin)
OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

# Option 2: Console output (simplest for debugging)
ENABLE_CONSOLE_EXPORTERS=true

# Agent Framework instrumentation
ENABLE_INSTRUMENTATION=true
ENABLE_SENSITIVE_DATA=true  # WARNING: dev/test only

# Optional: AI Toolkit for VS Code tracing
# VS_CODE_EXTENSION_PORT=5678

# Optional: Service identification
# OTEL_SERVICE_NAME="my-agent-app"
# OTEL_SERVICE_VERSION="1.0.0"
```

### Azure Setup

1. **Azure CLI Authentication**: `az login`
2. **Application Insights**: Attached to your Azure AI Foundry project
3. **OpenWeather API**: Free key from https://openweathermap.org/api
4. **Packages**: `pip install agent-framework[azure] azure-monitor-opentelemetry`

### Local Development (no Azure required)

For the workflow demo, you can use **Aspire Dashboard** locally:
```bash
docker run --rm -d -p 18888:18888 -p 4317:18889 --name aspire mcr.microsoft.com/dotnet/aspire-dashboard:latest
# Set OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 in .env
# View at http://localhost:18888
```

Or use **AI Toolkit for VS Code** tracing (set `VS_CODE_EXTENSION_PORT` in .env).

### Redis Setup (for persistence demos)

1. **Docker (Development)**: `docker run -p 6379:6379 -d redis:8.0.3`
2. **Redis Cloud**: Free tier at https://redis.io/cloud/
3. **Azure Managed Redis**: See Azure Cache for Redis Enterprise
4. **Packages**: `pip install agent-framework-redis agent-framework-devui`

## 📊 What Each Demo Shows

### `observability_azure_ai_agent.py`
**Single Agent with Tool Calling (AzureAIClient Pattern)**

- AzureAIClient.configure_azure_monitor() for one-line setup
- Agent `id` parameter for Foundry Control Plane fleet tracking
- @tool decorator with approval_mode for production safety
- Real OpenWeatherMap API integration (async httpx)
- Multi-turn conversation tracking
- Trace ID for Azure Portal + Foundry Portal investigation
- Compatible with Grafana Agent dashboard

**Use Case**: Production agent monitoring, Foundry fleet management, debugging LLM interactions

---

### `observability_workflow.py`
**3-Stage Customer Feedback Pipeline (configure_otel_providers Pattern)**

- configure_otel_providers() with standard OTEL env vars
- SentimentAnalyzer -> CategoryClassifier -> ActionRecommender
- Workflow build and execution spans
- Message passing telemetry
- Business metrics (sentiment, categories, priority)
- Works with Aspire Dashboard, Jaeger, Zipkin, console
- Compatible with Grafana Workflow dashboard

**Use Case**: Workflow debugging, performance analysis, multi-stage monitoring

---

### `redis_demo_preferences.py`
**RedisProvider: Smart Preference Memory**

- ✅ Persistent user preferences across sessions
- ✅ User-scoped memory (user_id)
- ✅ Context retrieval for personalization
- ✅ Natural preference learning

**Use Case**: Personal assistants, user profile management, personalized recommendations

---

### `redis_demo_persistence.py`
**RedisChatMessageStore: Resume Conversations**

- ✅ Conversation persistence across restarts
- ✅ Thread-based isolation (ticket ID)
- ✅ Multi-session support
- ✅ Message limits and auto-trimming

**Use Case**: Customer support, long-running conversations, session management

---

### `redis_demo_multi_agent.py`
**Multi-Agent Memory Isolation**

- ✅ Separate memory scopes per agent (agent_id)
- ✅ Personal vs Work assistant scenarios
- ✅ Enterprise multi-tenant patterns
- ✅ Same user, different contexts

**Use Case**: Multi-bot systems, department-specific agents, role-based access

## 🎯 Workshop Integration

**Module 4: Production & Operations** (35 minutes total)

1. **Introduction** (5 min) - Why observability matters
2. **Agent Demo** (10 min) - `observability_azure_ai_agent.py`
3. **Workflow Demo** (10 min) - `observability_workflow.py`
4. **Configuration** (5 min) - Tracing options
5. **Q&A** (5 min) - Troubleshooting

See `OBSERVABILITY_QUICK_REFERENCE.md` in `workshops/` for detailed demo script.

---

**Module 5: Redis Persistence** (45 minutes total)

1. **RedisProvider** (20 min) - Memory & context with `redis_demo_preferences.py` and `redis_demo_multi_agent.py`
2. **RedisChatMessageStore** (20 min) - Conversation persistence with `redis_demo_persistence.py`
3. **Production Setup** (5 min) - Redis options, best practices

See `REDIS_PERSISTENCE_SAMPLES.md` for comprehensive documentation.

## 🔍 Viewing Traces

### Azure Portal (Application Insights)
1. Navigate to **Application Insights** > **Transaction search**
2. Copy Trace ID from console output
3. Paste into search box
4. **Wait 2-5 minutes** for ingestion
5. Try "Oldest first" sorting

### Foundry Portal (Control Plane)
1. Navigate to **Foundry Portal** > **Operate** tab (upper right)
2. Select **Assets** in the left pane
3. Select your agent
4. Select the **Traces** tab
5. Click any Trace ID for the full span tree

### Aspire Dashboard (Local Development)
1. Start dashboard: `docker run -p 18888:18888 -p 4317:18889 mcr.microsoft.com/dotnet/aspire-dashboard:latest`
2. Set `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` in .env
3. Run your sample
4. Navigate to http://localhost:18888

### Grafana Dashboards (Azure Managed Grafana)
- **Agent Overview**: https://aka.ms/amg/dash/af-agent
- **Workflow Overview**: https://aka.ms/amg/dash/af-workflow

### What You'll See
- Request timeline with all operations
- Dependencies (OpenAI API calls, tool executions)
- Custom properties (sentiment, categories, etc.)
- Performance metrics for each stage
- Parent-child span relationships

## 🛠️ Troubleshooting

**No traces appearing?**
- Wait 2-5 minutes for Application Insights ingestion
- Verify `APPLICATIONINSIGHTS_CONNECTION_STRING` in `.env`
- Check Azure Portal for ingestion status

**Import errors?**
- Activate virtual environment: `source ../../.venv/bin/activate`
- Install dependencies: `pip install -r ../../requirements.txt`

**Weather API errors?**
- Verify `OPENWEATHER_API_KEY` in `.env`
- Get free key at https://openweathermap.org/api (1000 calls/day)

**Redis connection errors?**
- Check Redis is running: `docker ps | grep redis`
- Test connection: `telnet localhost 6379`
- Verify port 6379 is accessible

**Redis demos not remembering context?**
- Verify scope parameters (user_id, agent_id, thread_id)
- Check messages are stored: inspect demo console output
- Ensure same thread_id for persistence demos

## 📚 Additional Resources

- **Observability Documentation**: `OBSERVABILITY_SAMPLES.md` (this directory)
- **Redis Persistence Documentation**: `REDIS_PERSISTENCE_SAMPLES.md` (this directory)
- **Quick Reference**: `../workshops/OBSERVABILITY_QUICK_REFERENCE.md`
- **LLMOps Best Practices**: `../docs/MAF_LLMOPS_BEST_PRACTICES.md`
- **Production Examples**: `../llmops/examples/`
- **Redis Package README**: `../../python/packages/redis/README.md`
- **Redis Sample Code**: `../../python/samples/getting_started/context_providers/redis/`

## 🎓 Learning Objectives

### Observability (Module 4)
After running these samples, attendees should understand:
- ✅ How to enable Application Insights for Azure AI agents
- ✅ What telemetry data is collected automatically
- ✅ How to find and analyze traces in Azure Portal
- ✅ Workflow span hierarchy and message passing
- ✅ Custom spans and business metrics
- ✅ Production observability best practices

### Redis Persistence (Module 5)
After running Redis demos, attendees should understand:
- ✅ Difference between RedisProvider and RedisChatMessageStore
- ✅ When to use each component for production applications
- ✅ How to implement persistent memory and preferences
- ✅ Conversation persistence across application restarts
- ✅ Multi-agent memory isolation patterns
- ✅ Production Redis setup options (Docker, Cloud, Azure)

---

**Last Updated**: February 2026  
**Workshop**: Microsoft Agent Framework with Azure AI Foundry  
**Module**: 4 - Production & Operations

# Observability Samples

Workshop-ready observability demonstrations for Microsoft Agent Framework with Azure AI Foundry.

## 📁 Contents

| File | Description | Workshop Module |
|------|-------------|-----------------|
| `observability_azure_ai_agent.py` | Azure AI agent with Application Insights integration | Module 4 |
| `observability_workflow.py` | Customer feedback analysis workflow with telemetry | Module 4 |
| `OBSERVABILITY_SAMPLES.md` | Comprehensive documentation (35-minute module) | Reference |
| `.env` | Environment configuration (not committed to git) | - |

## 🚀 Quick Start

```bash
# Navigate to observability directory
cd AQ-CODE/observability

# Run Azure AI Agent demo (with real OpenWeatherMap API)
python observability_azure_ai_agent.py

# Run Workflow demo (customer feedback analysis)
python observability_workflow.py
```

## 📋 Prerequisites

### Environment Variables (in `.env`)

```bash
# Required for both samples
AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/..."
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1-mini"

# Required for observability_azure_ai_agent.py
OPENWEATHER_API_KEY="your-key-here"  # Get free key at openweathermap.org/api

# Tracing configuration (choose one or more)
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=xxx;..."
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
```

### Azure Setup

1. **Azure CLI Authentication**: `az login`
2. **Application Insights**: Attached to your Azure AI project
3. **OpenWeather API**: Free key from https://openweathermap.org/api

## 📊 What Each Demo Shows

### `observability_azure_ai_agent.py`
**Single Agent with Tool Calling**

- ✅ Automatic Application Insights configuration
- ✅ Real OpenWeatherMap API integration
- ✅ Multi-turn conversation tracking
- ✅ Tool call telemetry
- ✅ Trace ID for Azure Portal investigation

**Use Case**: Production agent monitoring, debugging LLM interactions

---

### `observability_workflow.py`
**3-Stage Customer Feedback Pipeline**

- ✅ SentimentAnalyzer → CategoryClassifier → ActionRecommender
- ✅ Workflow build and execution spans
- ✅ Message passing telemetry
- ✅ Business metrics (sentiment, categories, priority)
- ✅ Realistic business scenario

**Use Case**: Workflow debugging, performance optimization, multi-stage monitoring

## 🎯 Workshop Integration

**Module 4: Production & Operations** (35 minutes total)

1. **Introduction** (5 min) - Why observability matters
2. **Agent Demo** (10 min) - `observability_azure_ai_agent.py`
3. **Workflow Demo** (10 min) - `observability_workflow.py`
4. **Configuration** (5 min) - Tracing options
5. **Q&A** (5 min) - Troubleshooting

See `OBSERVABILITY_QUICK_REFERENCE.md` in `workshops/` for detailed demo script.

## 🔍 Viewing Traces

### Azure Portal
1. Navigate to **Application Insights** → **Transaction search**
2. Copy Trace ID from console output
3. Paste into search box
4. **Wait 2-5 minutes** for ingestion
5. Try "Oldest first" sorting

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

## 📚 Additional Resources

- **Full Documentation**: `OBSERVABILITY_SAMPLES.md` (this directory)
- **Quick Reference**: `../workshops/OBSERVABILITY_QUICK_REFERENCE.md`
- **LLMOps Best Practices**: `../docs/MAF_LLMOPS_BEST_PRACTICES.md`
- **Production Examples**: `../llmops/examples/`

## 🎓 Learning Objectives

After running these samples, attendees should understand:
- ✅ How to enable Application Insights for Azure AI agents
- ✅ What telemetry data is collected automatically
- ✅ How to find and analyze traces in Azure Portal
- ✅ Workflow span hierarchy and message passing
- ✅ Custom spans and business metrics
- ✅ Production observability best practices

---

**Last Updated**: November 2025  
**Workshop**: Microsoft Agent Framework with Azure AI Foundry  
**Module**: 4 - Production & Operations

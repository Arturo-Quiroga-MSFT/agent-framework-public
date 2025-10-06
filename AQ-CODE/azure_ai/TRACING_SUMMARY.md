# 🎯 Complete Tracing Setup Summary

This document provides a quick reference for all tracing options available for your Azure AI agents.

## 📚 Documentation Map

| Document | Purpose | Best For |
|----------|---------|----------|
| **TRACING_QUICKSTART.md** | Quick copy-paste commands | Getting started fast |
| **TRACING_GUIDE.md** | Comprehensive tracing docs | Deep understanding |
| **DEVUI_TRACING_GUIDE.md** | DevUI-specific tracing | Visual debugging |
| **DEVUI_GUIDE.md** | General DevUI usage | DevUI basics |
| This file | Overview of all options | Choosing right approach |

---

## 🚀 Quick Decision Guide

### "I want to see traces immediately"
```bash
echo "ENABLE_CONSOLE_TRACING=true" >> .env
python azure_ai_basic_devui.py --test
```
→ See traces in your terminal instantly

### "I want visual trace debugging in a web UI"
```bash
echo "ENABLE_DEVUI_TRACING=true" >> .env
python azure_ai_basic_devui.py
```
→ See traces in DevUI web interface at http://localhost:8090

### "I want to use open-source tools like Jaeger"
```bash
docker run -d -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one:latest
echo "OTLP_ENDPOINT=http://localhost:4317" >> .env
python azure_ai_basic_devui.py
```
→ Beautiful traces at http://localhost:16686

### "I want production-ready monitoring"
```bash
echo "ENABLE_AZURE_AI_TRACING=true" >> .env
python azure_ai_basic_devui.py
```
→ Traces automatically sent to Application Insights in your Azure AI project

---

## 🎨 Tracing Options Comparison

| Option | Setup | Visualization | Persistence | Production | Best For |
|--------|-------|---------------|-------------|------------|----------|
| **DevUI Tracing** | 30 sec | ⭐⭐⭐⭐⭐ Web UI | ❌ No | ❌ No | Development |
| **Console** | 10 sec | ⭐⭐ Terminal | ❌ No | ❌ No | Quick debug |
| **Jaeger** | 3 min | ⭐⭐⭐⭐⭐ Web UI | ✅ Yes | ⚠️ Maybe | Local dev |
| **Azure AI** | 2 min | ⭐⭐⭐⭐ Portal | ✅ Yes | ✅ Yes | Production |
| **App Insights** | 2 min | ⭐⭐⭐⭐ Portal | ✅ Yes | ✅ Yes | Production |

---

## 📋 All Configuration Options

### Environment Variables Reference

Add these to your `.env` file:

```bash
# ============================================
# OPTION 1: DEVUI TRACING (Visual in Web UI)
# ============================================
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true

# ============================================
# OPTION 2: CONSOLE TRACING (Terminal Output)
# ============================================
ENABLE_CONSOLE_TRACING=true

# ============================================
# OPTION 3: AZURE AI TRACING (Production)
# ============================================
ENABLE_AZURE_AI_TRACING=true

# ============================================
# OPTION 4: OTLP ENDPOINT (Jaeger/Zipkin)
# ============================================
OTLP_ENDPOINT=http://localhost:4317

# ============================================
# OPTION 5: APP INSIGHTS DIRECT
# ============================================
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx
```

---

## 🎯 Use Case Matrix

### Development Phase

| Task | Best Option | Why |
|------|-------------|-----|
| Quick debugging | Console | Immediate feedback |
| Visual debugging | DevUI | See traces in UI |
| Understanding flow | DevUI or Jaeger | Hierarchical view |
| Performance analysis | DevUI or Jaeger | Timing visualization |
| Learning agent behavior | DevUI | Interactive + visual |

### Production Phase

| Task | Best Option | Why |
|------|-------------|-----|
| Monitoring | Azure AI / App Insights | Managed service |
| Alerting | Azure AI / App Insights | Built-in alerts |
| Long-term analysis | Azure AI / App Insights | Data retention |
| Cost tracking | Azure AI / App Insights | Token usage metrics |
| Compliance | Azure AI / App Insights | Audit logs |

---

## 🚀 Quick Start by Method

### 1. DevUI Tracing (Recommended for Development)

**What it does:** Shows traces in the DevUI web interface as you interact with agents.

**Setup:**
```bash
# Configure
echo "ENABLE_DEVUI_TRACING=true" >> .env
echo "ENABLE_OTEL=true" >> .env
echo "ENABLE_SENSITIVE_DATA=true" >> .env

# Run
python azure_ai_basic_devui.py

# View traces at http://localhost:8090
```

**Pros:** 
- ⭐ Best visualization
- ⭐ No external tools
- ⭐ Real-time updates
- ⭐ Interactive UI

**Cons:**
- ❌ Not for production
- ❌ No persistence

---

### 2. Console Tracing (Fastest Setup)

**What it does:** Prints traces to your terminal.

**Setup:**
```bash
# Configure
echo "ENABLE_CONSOLE_TRACING=true" >> .env

# Run
python azure_ai_basic_devui.py --test
```

**Pros:**
- ⭐ Zero dependencies
- ⭐ Immediate output
- ⭐ Works everywhere

**Cons:**
- ❌ Hard to read complex traces
- ❌ No visual hierarchy
- ❌ Can't search

---

### 3. Jaeger (Best Local Visualization)

**What it does:** Sends traces to Jaeger for beautiful visualization.

**Setup:**
```bash
# Start Jaeger
docker run -d --name jaeger \
  -p 4317:4317 -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Configure
echo "OTLP_ENDPOINT=http://localhost:4317" >> .env

# Run
python azure_ai_basic_devui.py

# View traces at http://localhost:16686
```

**Pros:**
- ⭐ Professional UI
- ⭐ Open source
- ⭐ Works offline
- ⭐ Persistent storage

**Cons:**
- ❌ Requires Docker
- ❌ Extra setup
- ❌ Not production-ready by default

---

### 4. Azure AI Tracing (Production)

**What it does:** Automatically sends traces to Application Insights in your Azure AI project.

**Setup:**
```bash
# Ensure App Insights is attached to your Azure AI project
# (Do this in Azure AI Studio → Settings → Application Insights)

# Configure
echo "ENABLE_AZURE_AI_TRACING=true" >> .env

# Run
python azure_ai_basic_devui.py

# View in Azure Portal → Application Insights
```

**Pros:**
- ⭐ Production-ready
- ⭐ Fully managed
- ⭐ Azure integration
- ⭐ Advanced analytics

**Cons:**
- ❌ Requires Azure setup
- ❌ Some delay in viewing
- ❌ Costs money (minimal)

---

### 5. Application Insights Direct

**What it does:** Sends traces directly to an Application Insights resource.

**Setup:**
```bash
# Get connection string from Azure Portal

# Configure
echo 'APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;...' >> .env

# Run
python azure_ai_basic_devui.py
```

**Pros:**
- ⭐ Production-ready
- ⭐ Use existing App Insights
- ⭐ Full Azure features

**Cons:**
- ❌ Need connection string
- ❌ Same as Azure AI tracing

---

## 🔀 Combining Multiple Tracing Options

You can enable **multiple tracing destinations** simultaneously:

```bash
# Example: Console + Jaeger
ENABLE_CONSOLE_TRACING=true
OTLP_ENDPOINT=http://localhost:4317

# Example: DevUI + Azure AI
ENABLE_DEVUI_TRACING=true
ENABLE_AZURE_AI_TRACING=true

# Example: All at once (for maximum observability)
ENABLE_CONSOLE_TRACING=true
ENABLE_DEVUI_TRACING=true
OTLP_ENDPOINT=http://localhost:4317
ENABLE_AZURE_AI_TRACING=true
```

---

## 📊 What Gets Traced

### All Options Trace:
- ✅ **Agent invocations** with name and ID
- ✅ **LLM requests** with model and tokens
- ✅ **Tool executions** with parameters
- ✅ **Duration** of each operation
- ✅ **Success/failure** status
- ✅ **Parent-child** relationships

### With `ENABLE_SENSITIVE_DATA=true`:
- ✅ **User prompts** (full text)
- ✅ **LLM responses** (full text)
- ✅ **Tool parameters** (full JSON)
- ✅ **Tool results** (full data)

---

## 🎯 Recommended Workflows

### Development Workflow
```bash
# Day-to-day development
ENABLE_DEVUI_TRACING=true
ENABLE_CONSOLE_TRACING=true  # Backup in terminal

# Deep debugging session
ENABLE_DEVUI_TRACING=true
OTLP_ENDPOINT=http://localhost:4317  # Jaeger for analysis
ENABLE_SENSITIVE_DATA=true
```

### Testing Workflow
```bash
# Unit tests
ENABLE_CONSOLE_TRACING=true  # Quick feedback

# Integration tests
ENABLE_CONSOLE_TRACING=true
ENABLE_AZURE_AI_TRACING=true  # Log to production backend
```

### Production Workflow
```bash
# Production only
ENABLE_AZURE_AI_TRACING=true
# OR
APPLICATIONINSIGHTS_CONNECTION_STRING=xxx

# Note: Never enable ENABLE_SENSITIVE_DATA in production!
```

---

## 🔍 Finding Traces

### DevUI Traces
1. Open http://localhost:8090
2. Interact with agent
3. Look for "Traces" or "Telemetry" panel in UI
4. Expand spans to see details

### Console Traces
1. Look in terminal output
2. Search for JSON objects with "name", "attributes"
3. Check "duration" and "status" fields

### Jaeger Traces
1. Open http://localhost:16686
2. Select service from dropdown
3. Click "Find Traces"
4. Click trace to see waterfall view

### Azure Application Insights
1. Go to Azure Portal
2. Open Application Insights resource
3. "Transaction Search" → Search by Trace ID
4. Or use "Logs" with KQL queries:
   ```kusto
   traces
   | where customDimensions.["gen_ai.operation.name"] == "invoke_agent"
   | project timestamp, message, customDimensions
   ```

---

## 🛠️ Troubleshooting

### No traces anywhere?

**Check 1:** Environment variables set?
```bash
cat .env | grep -E "TRACING|OTEL"
```

**Check 2:** OpenTelemetry installed?
```bash
pip list | grep opentelemetry
```

**Check 3:** Agent created correctly?
```python
# Make sure you're using agent framework classes
agent = ChatAgent(...)  # ✅ Good
```

### Traces in console but not DevUI?

**Fix:** Enable DevUI tracing specifically:
```bash
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
```

### Traces in DevUI but not Azure?

**Fix 1:** Check App Insights is attached:
- Azure AI Studio → Project → Settings → Application Insights

**Fix 2:** Verify credentials:
```bash
az login
az account show
```

---

## 📈 Next Steps

1. **Try DevUI Tracing First** - Best experience
   ```bash
   echo "ENABLE_DEVUI_TRACING=true" >> .env
   python azure_ai_basic_devui.py
   ```

2. **Experiment with Jaeger** - Beautiful visualization
   ```bash
   docker run -d -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one
   echo "OTLP_ENDPOINT=http://localhost:4317" >> .env
   ```

3. **Set up Azure AI Tracing** - Production ready
   ```bash
   # In Azure AI Studio: attach Application Insights
   echo "ENABLE_AZURE_AI_TRACING=true" >> .env
   ```

4. **Read Full Guides**
   - [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md) - DevUI details
   - [`TRACING_GUIDE.md`](./TRACING_GUIDE.md) - Comprehensive guide
   - [`TRACING_QUICKSTART.md`](./TRACING_QUICKSTART.md) - Quick reference

---

## 🎉 You're Ready!

You now have **5 different ways** to trace your Azure AI agents:

1. ✅ DevUI Tracing - Visual in web UI
2. ✅ Console Tracing - Terminal output
3. ✅ Jaeger - Open source UI
4. ✅ Azure AI - Production monitoring
5. ✅ App Insights - Direct connection

**Choose the one that fits your needs and start tracing!** 🚀

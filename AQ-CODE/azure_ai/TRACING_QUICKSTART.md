# Quick Start: Adding Tracing to Azure AI Agents

## ✅ What I Added

I've enhanced `azure_ai_basic_devui.py` with comprehensive OpenTelemetry tracing support. You can now monitor and debug your agent's behavior with multiple observability backends.

## 🚀 Quick Start (Choose One)

### Option 1: Console Tracing (Easiest)
Perfect for quick debugging and learning.

```bash
# 1. Edit .env file
echo "ENABLE_CONSOLE_TRACING=true" >> .env

# 2. Run the agent
python azure_ai_basic_devui.py --test
```

You'll see detailed trace output in your console showing:
- Agent invocations
- Tool calls
- LLM requests
- Token usage
- Execution times

---

### Option 2: Azure AI Tracing (Recommended for Production)
Sends traces to Application Insights in your Azure AI project.

```bash
# 1. Attach Application Insights to your Azure AI project
# Go to Azure AI Studio → Your Project → Settings → Application Insights

# 2. Edit .env file
echo "ENABLE_AZURE_AI_TRACING=true" >> .env

# 3. Run the agent
python azure_ai_basic_devui.py --test

# 4. View traces in Azure Portal
# Note the Trace ID from console, then:
# Azure Portal → Application Insights → Transaction Search
```

---

### Option 3: Jaeger (Best Visualization)
Open-source distributed tracing with beautiful UI.

```bash
# 1. Start Jaeger
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# 2. Edit .env file
echo "OTLP_ENDPOINT=http://localhost:4317" >> .env

# 3. Run the agent
python azure_ai_basic_devui.py --test

# 4. View traces at http://localhost:16686
```

---

## 📊 What Gets Traced

### Agent Operations
- **Agent Runs**: Every `agent.run()` call
- **Trace ID**: Unique identifier to find your traces
- **Duration**: How long operations take
- **Status**: Success or error states

### Tool Executions
- **Function Name**: Which tool was called
- **Parameters**: Input values (if `enable_sensitive_data=true`)
- **Results**: Return values
- **Timing**: Execution duration

### LLM Interactions
- **Model**: Which model was used (e.g., gpt-4)
- **Tokens**: Input/output token counts
- **Messages**: Prompts and responses (if enabled)
- **Finish Reason**: Why completion ended

---

## 🔍 Finding Your Traces

### Console
Look for JSON objects with span information:
```json
{
  "name": "invoke_agent WeatherAgent",
  "attributes": {
    "gen_ai.operation.name": "invoke_agent",
    "gen_ai.system": "azure_ai",
    "gen_ai.agent.name": "WeatherAgent"
  }
}
```

### Jaeger (http://localhost:16686)
1. Select service from dropdown
2. Click "Find Traces"
3. Click on a trace to see waterfall view
4. Expand spans to see details

### Application Insights
1. **Transaction Search**: Search by Trace ID
2. **Application Map**: See service dependencies  
3. **Performance**: Analyze operation durations
4. **Failures**: Find errors

**Sample KQL Query:**
```kusto
traces
| where customDimensions.["gen_ai.operation.name"] == "invoke_agent"
| project timestamp, message, customDimensions
| order by timestamp desc
```

---

## 🛠️ Configuration Options

### Environment Variables (in `.env`)

```bash
# Option 1: Console output
ENABLE_CONSOLE_TRACING=true

# Option 2: Azure AI (uses App Insights from project)
ENABLE_AZURE_AI_TRACING=true

# Option 3: OTLP endpoint (Jaeger, Zipkin, etc.)
OTLP_ENDPOINT=http://localhost:4317

# Option 4: Application Insights direct
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;...

# Optional: Include prompts/responses in traces
ENABLE_SENSITIVE_DATA=true
```

---

## 💻 Code Examples

### Basic Usage (Already in azure_ai_basic_devui.py)
```python
from agent_framework.observability import setup_observability

# Console tracing
setup_observability(enable_sensitive_data=True)

# Agent automatically traced
agent = await client.create_agent(...)
response = await agent.run("What's the weather?")
```

### Custom Spans (Group Related Operations)
```python
from agent_framework.observability import get_tracer
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id

# Create a span for your business logic
with get_tracer().start_as_current_span("User Request", kind=SpanKind.CLIENT) as span:
    # Get the trace ID for searching later
    trace_id = format_trace_id(span.get_span_context().trace_id)
    print(f"Trace ID: {trace_id}")
    
    # Add custom attributes
    span.set_attribute("user_id", "user123")
    span.set_attribute("query_type", "weather")
    
    # All agent operations will be children of this span
    response = await agent.run("What's the weather in Seattle?")
```

### Azure AI Tracing (Automatic)
```python
from agent_framework.azure import AzureAIAgentClient

async with AzureAIAgentClient(...) as client:
    # This automatically configures tracing to App Insights
    await client.setup_azure_ai_observability()
    
    agent = await client.create_agent(...)
    # All operations now traced to Azure
```

---

## 📁 Files Modified

1. **azure_ai_basic_devui.py**
   - Added `setup_tracing()` function
   - Integrated OpenTelemetry imports
   - Added trace ID output in test mode
   - Configured multiple tracing backends

2. **.env**
   - Added tracing configuration section
   - Documented all 4 tracing options
   - Included examples and comments

3. **TRACING_GUIDE.md** (New)
   - Comprehensive tracing documentation
   - Setup instructions for each backend
   - KQL query examples
   - Troubleshooting guide

4. **TRACING_QUICKSTART.md** (This file)
   - Quick reference guide
   - Copy-paste examples
   - Minimal setup instructions

---

## 🎯 Testing Your Setup

### Test with Console Tracing
```bash
# Enable console tracing
echo "ENABLE_CONSOLE_TRACING=true" >> .env

# Run test mode
python azure_ai_basic_devui.py --test

# You should see trace output
```

### Test with DevUI
```bash
# Enable tracing
echo "ENABLE_CONSOLE_TRACING=true" >> .env

# Launch DevUI
python azure_ai_basic_devui.py

# Traces will appear in console as you interact with the agent
```

---

## 🐛 Troubleshooting

### No traces appearing?
1. Check environment variable is set: `cat .env | grep TRACING`
2. Verify imports work: `python -c "from agent_framework.observability import setup_observability"`
3. Look for error messages during startup

### Azure AI tracing not working?
1. Verify Application Insights is attached to AI project
2. Check Azure credentials: `az login`
3. Look for setup errors in console output

### Jaeger not receiving traces?
1. Verify Jaeger is running: `docker ps | grep jaeger`
2. Check endpoint: `curl http://localhost:4317`
3. Verify OTLP_ENDPOINT in .env

---

## 📚 Learn More

- **Full Documentation**: See `TRACING_GUIDE.md` in this directory
- **More Examples**: Check `../../observability/` directory
- **OpenTelemetry Docs**: https://opentelemetry.io/docs/
- **Azure Monitor**: https://learn.microsoft.com/azure/azure-monitor/

---

## 🎉 Next Steps

1. **Try Console Tracing**: Easiest way to see tracing in action
2. **Explore Jaeger**: Beautiful visualization of distributed traces
3. **Set up Azure Monitor**: Production-ready observability
4. **Add Custom Spans**: Instrument your business logic
5. **Create Dashboards**: Visualize agent performance over time

---

**Need Help?** Check `TRACING_GUIDE.md` for detailed documentation and troubleshooting.

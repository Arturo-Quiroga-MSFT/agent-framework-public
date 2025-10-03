# Azure AI Agent Tracing Guide

This guide explains how to add OpenTelemetry tracing to your Azure AI agents to monitor and debug their behavior.

## Table of Contents
- [Overview](#overview)
- [Tracing Options](#tracing-options)
- [Quick Start](#quick-start)
- [Detailed Configuration](#detailed-configuration)
- [Viewing Traces](#viewing-traces)
- [What Gets Traced](#what-gets-traced)

## Overview

Tracing provides visibility into:
- **Agent invocations**: When and how agents are called
- **Tool executions**: Which tools are used and their inputs/outputs
- **LLM interactions**: Requests to Azure OpenAI with token usage
- **Performance**: Duration of each operation
- **Errors**: Where failures occur in the execution chain

The agent framework uses **OpenTelemetry** (industry standard) for tracing, which works with various observability backends.

## Tracing Options

### Option 1: Console Tracing (Simplest)
**Best for:** Quick debugging, local development

Outputs traces directly to your terminal. No external services needed.

```bash
# In .env file
ENABLE_CONSOLE_TRACING=true
```

**Pros:** Zero setup, immediate feedback
**Cons:** No persistent storage, harder to analyze complex traces

---

### Option 2: Azure AI Tracing (Recommended)
**Best for:** Production use with Azure AI

Automatically sends traces to Application Insights attached to your Azure AI project.

```bash
# In .env file
ENABLE_AZURE_AI_TRACING=true
```

**Prerequisites:**
- Application Insights must be attached to your Azure AI project
- Add in Azure AI Studio: Project Settings → Application Insights

**Pros:** 
- Fully managed service
- Integrated with Azure ecosystem
- Powerful query language (KQL)
- Alerts and dashboards

**Viewing Traces:**
1. Go to Azure Portal
2. Open your Application Insights resource
3. Navigate to "Transaction Search" or "Application Map"
4. Use the Trace ID from console output to find specific traces

---

### Option 3: OTLP Endpoint (Developer Tools)
**Best for:** Local development with open-source tools

Send traces to Jaeger, Zipkin, or any OTLP-compatible receiver.

```bash
# In .env file
OTLP_ENDPOINT=http://localhost:4317
```

**Setup Jaeger locally:**
```bash
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

Then visit: http://localhost:16686

**Pros:** 
- Free and open source
- Great visualization
- Works offline

**Cons:** 
- Requires running additional services
- Data not persistent by default

---

### Option 4: Application Insights Direct
**Best for:** Existing Application Insights resources

Connect directly using a connection string.

```bash
# In .env file
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx
```

Get your connection string from:
Azure Portal → Application Insights → Properties → Connection String

---

## Quick Start

### 1. Enable Console Tracing (Easiest)

Edit `.env`:
```bash
ENABLE_CONSOLE_TRACING=true
```

Run the agent:
```bash
python azure_ai_basic_devui.py --test
```

You'll see trace output like:
```
📊 Tracing Mode: Console Output
🔍 Trace ID: a1b2c3d4e5f6...

{
    'name': 'invoke_agent WeatherAgent',
    'context': {...},
    'kind': 'SpanKind.INTERNAL',
    'attributes': {
        'gen_ai.operation.name': 'invoke_agent',
        'gen_ai.system': 'azure_ai',
        ...
    }
}
```

### 2. Enable Azure AI Tracing (Production)

**Step 1:** Attach Application Insights to Azure AI project
- Go to Azure AI Studio
- Select your project
- Settings → Application Insights
- Create or attach existing resource

**Step 2:** Enable in `.env`:
```bash
ENABLE_AZURE_AI_TRACING=true
```

**Step 3:** Run and find traces:
```bash
python azure_ai_basic_devui.py --test
```

Note the Trace ID from output, then:
1. Azure Portal → Application Insights
2. Transaction Search
3. Paste Trace ID

---

## Detailed Configuration

### In Your Code

The `azure_ai_basic_devui.py` example shows the pattern:

```python
from agent_framework.observability import setup_observability, get_tracer
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id

# 1. Setup observability (early in your app)
setup_observability(
    enable_sensitive_data=True,  # Include prompts/responses in traces
    otlp_endpoint="http://localhost:4317",  # Optional
)

# 2. For Azure AI agents, use built-in method
async with AzureAIAgentClient(...) as client:
    await client.setup_azure_ai_observability()
    agent = await client.create_agent(...)

# 3. Add custom spans for grouping operations
with get_tracer().start_as_current_span("Agent Test Session", kind=SpanKind.CLIENT) as span:
    trace_id = format_trace_id(span.get_span_context().trace_id)
    print(f"Trace ID: {trace_id}")
    
    # All operations here will be grouped under this span
    response = await agent.run("Hello")
```

### Environment Variables Reference

| Variable | Values | Description |
|----------|--------|-------------|
| `ENABLE_CONSOLE_TRACING` | `true`, `false` | Output traces to console |
| `ENABLE_AZURE_AI_TRACING` | `true`, `false` | Use App Insights from AI project |
| `OTLP_ENDPOINT` | URL | OTLP receiver endpoint |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Connection string | Direct App Insights |
| `ENABLE_SENSITIVE_DATA` | `true`, `false` | Include prompts/responses |

---

## Viewing Traces

### Console Output
Traces appear directly in your terminal. Look for JSON objects with:
- `name`: Operation name (e.g., "invoke_agent WeatherAgent")
- `attributes`: Metadata (model, tokens, etc.)
- `start_time`, `end_time`: Timing information

### Jaeger UI (http://localhost:16686)
1. Select "jaeger-query" service
2. Click "Find Traces"
3. Click on a trace to see the waterfall view
4. Expand spans to see details

### Application Insights
1. **Transaction Search**: Search by Trace ID or time range
2. **Application Map**: Visualize service dependencies
3. **Performance**: Analyze operation durations
4. **Failures**: Find errors and exceptions

**KQL Query Examples:**
```kusto
// Find all agent invocations
traces
| where customDimensions.["gen_ai.operation.name"] == "invoke_agent"
| project timestamp, message, customDimensions

// Find slow operations (>5 seconds)
traces
| where duration > 5000
| order by duration desc

// Find traces with errors
traces
| where severityLevel >= 3
| project timestamp, message, severityLevel
```

---

## What Gets Traced

### Agent Invocations
- Agent name and ID
- Thread ID
- Input messages
- Output response
- Total duration
- Finish reason (completed, error, etc.)

**Attributes:**
- `gen_ai.operation.name`: "invoke_agent"
- `gen_ai.system`: "azure_ai"
- `gen_ai.agent.name`: "WeatherAgent"
- `gen_ai.agent.id`: UUID

### Tool Executions
- Tool/function name
- Input parameters
- Return value
- Execution duration

**Attributes:**
- `gen_ai.operation.name`: "execute_tool"
- `gen_ai.tool.name`: "get_weather"

### LLM Chat Completions
- Model name
- Input messages
- Output completion
- Token usage (prompt, completion, total)
- Finish reason

**Attributes:**
- `gen_ai.operation.name`: "chat"
- `gen_ai.system`: "azure_openai"
- `gen_ai.request.model`: "gpt-4"
- `gen_ai.response.model`: "gpt-4"
- `gen_ai.usage.input_tokens`: 123
- `gen_ai.usage.output_tokens`: 456

### Metrics
The framework also exports metrics:
- `gen_ai.client.operation.duration`: Operation latency histogram
- `gen_ai.client.token.usage`: Token usage histogram

---

## Examples

### Example 1: Basic Console Tracing
```python
from agent_framework.observability import setup_observability

# Enable console tracing
setup_observability(enable_sensitive_data=True)

# Your agent code here
agent = await client.create_agent(...)
response = await agent.run("What's the weather?")
```

### Example 2: Custom Span
```python
from agent_framework.observability import get_tracer
from opentelemetry.trace import SpanKind

# Create a custom span for a business operation
with get_tracer().start_as_current_span("Process User Request", kind=SpanKind.CLIENT) as span:
    # Add custom attributes
    span.set_attribute("user_id", "user123")
    span.set_attribute("request_type", "weather")
    
    # All agent operations will be children of this span
    response = await agent.run("What's the weather in Seattle?")
    
    # Add more attributes based on results
    span.set_attribute("cities_queried", 1)
```

### Example 3: Multiple Tracing Backends
```python
# You can export to multiple destinations
setup_observability(
    enable_sensitive_data=True,
    otlp_endpoint="http://localhost:4317",  # Jaeger
    applicationinsights_connection_string="...",  # Azure Monitor
)
```

---

## Troubleshooting

### No traces appearing

**Console tracing:**
- Check `ENABLE_CONSOLE_TRACING=true` is set
- Verify observability is set up before creating agents

**Azure AI tracing:**
- Verify Application Insights is attached to AI project
- Check Azure credentials: `az login`
- Look for error messages during `setup_azure_ai_observability()`

**OTLP endpoint:**
- Verify receiver is running: `docker ps`
- Check endpoint URL is correct
- Test connectivity: `curl http://localhost:4317`

### Sensitive data not showing

Set `ENABLE_SENSITIVE_DATA=true` in environment or:
```python
setup_observability(enable_sensitive_data=True)
```

### Traces are too verbose

Disable console tracing and use a visual tool like Jaeger or Application Insights.

---

## Best Practices

1. **Use Trace IDs**: Always capture and log trace IDs for troubleshooting
2. **Add Custom Spans**: Group related operations under meaningful spans
3. **Set Attributes**: Add business context to spans (user_id, session_id, etc.)
4. **Production Tracing**: Use Azure AI tracing or Application Insights for production
5. **Local Development**: Use console or Jaeger for local development
6. **Sampling**: For high-volume production, consider sampling to reduce costs

---

## Additional Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Azure Monitor OpenTelemetry](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-overview)
- [Agent Framework Observability Samples](../../../observability/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)

---

## Related Files

- `azure_ai_basic_devui.py` - Example with tracing enabled
- `.env` - Configuration for tracing options
- `../../../observability/` - More observability examples

# Observability Samples for Workshop

This directory contains two observability demonstration samples designed for the Microsoft Agent Framework workshop.

## Overview

These samples demonstrate how to implement comprehensive telemetry and tracing for Azure AI agents and workflows, enabling you to monitor, debug, and optimize your AI applications in production.

## Samples

### 1. `observability_azure_ai_agent.py`
**Azure AI Agent with Application Insights Integration**

Demonstrates automatic telemetry setup for Azure AI agents using Application Insights attached to your Azure AI project.

**Features:**
- Automatic Application Insights configuration from Azure AI Project
- Single agent with tool calling (weather function)
- Multi-turn conversation tracking
- Trace ID output for Azure Portal investigation
- Distributed tracing across agent operations

**Use Cases:**
- Production agent monitoring
- Debugging tool calls and LLM interactions
- Tracking conversation flows
- Performance analysis

**Run:**
```bash
cd AQ-CODE/observability
python observability_azure_ai_agent.py
```

**Expected Output:**
```
================================================================================
Azure AI Agent Observability Demo
================================================================================

Azure AI Project: https://your-project.services.ai.azure.com/...
✓ Application Insights connection string retrieved from Azure AI Project
✓ Observability configured - telemetry will be sent to Application Insights

Trace ID: 1234567890abcdef...
Use this Trace ID to find this execution in Azure Portal > Application Insights

User: What's the weather in Amsterdam?
WeatherAgent: The weather in Amsterdam is sunny with a high of 22°C.

User: and in Paris, and which is better?
WeatherAgent: In Paris it's cloudy with a high of 18°C. Amsterdam has better weather today!

User: Why is the sky blue?
WeatherAgent: The sky appears blue because of Rayleigh scattering...

================================================================================
Demo completed!
Check Azure Portal > Application Insights > Transaction Search
Filter by Trace ID: 1234567890abcdef...
================================================================================
```

---

### 2. `observability_workflow.py`
**Sequential Workflow with Telemetry**

Demonstrates telemetry collection across a multi-executor workflow with message passing.

**Features:**
- Sequential workflow pattern (UpperCase → Reverse)
- Executor-level span tracking
- Message passing telemetry
- Workflow build and execution spans
- Multiple tracing backend options

**Use Cases:**
- Workflow debugging and optimization
- Understanding message flow between executors
- Identifying performance bottlenecks
- Multi-stage process monitoring

**Run:**
```bash
cd AQ-CODE/observability
python observability_workflow.py
```

**Expected Output:**
```
================================================================================
Workflow Observability Demo
================================================================================

Tracing Configuration:
--------------------------------------------------------------------------------
✓ Application Insights Direct: Enabled
✓ DevUI tracing: Enabled
--------------------------------------------------------------------------------

✓ Observability setup completed

Trace ID: abcdef1234567890...

Building workflow...
✓ Workflow built

Starting workflow with input: 'hello world'

UpperCaseExecutor: Processing 'hello world'
UpperCaseExecutor: Result 'HELLO WORLD'
ReverseTextExecutor: Processing 'HELLO WORLD'
ReverseTextExecutor: Result 'DLROW OLLEH'

✓ Workflow completed with result: 'DLROW OLLEH'

================================================================================
Demo completed!
Check Azure Portal > Application Insights > Transaction Search
Filter by Trace ID: abcdef1234567890...
================================================================================
```

---

## Configuration

Both samples use the shared `.env` file located at `AQ-CODE/.env`. They automatically load environment variables from this file.

### Required Variables

```bash
# Azure AI Project (Required for observability_azure_ai_agent.py)
AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/..."
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1-mini"
```

### Tracing Options

Choose one or more tracing backends by configuring these variables in `.env`:

#### Option 1: Console Tracing (Simplest)
```bash
ENABLE_CONSOLE_TRACING=true
```
- Outputs traces directly to console
- Best for: Local development, quick debugging
- No additional setup required

#### Option 2: Azure AI Tracing (Recommended for Production)
```bash
ENABLE_AZURE_AI_TRACING=true
```
- Automatically uses Application Insights from your Azure AI project
- Best for: Production monitoring, team collaboration
- Requires: Application Insights attached to Azure AI project

#### Option 3: OTLP Endpoint (Advanced)
```bash
OTLP_ENDPOINT=http://localhost:4317
```
- Sends traces to Jaeger, Zipkin, or other OTLP receivers
- Best for: Custom observability stacks, on-premises deployment
- Requires: OTLP-compatible receiver running

#### Option 4: Application Insights Direct
```bash
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=xxx;IngestionEndpoint=https://..."
```
- Direct connection to Application Insights
- Best for: Existing Application Insights setup
- Get from: Azure Portal > Application Insights > Properties

#### DevUI Tracing (Workshop Demo)
```bash
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
```
- Interactive visualization in DevUI web interface
- Best for: Live demonstrations, interactive debugging
- Shows real-time agent operations and message flow

---

## Workshop Integration

### Module 4: Production & Operations

These samples are designed for **Module 4: Production & Operations** in the workshop agenda.

**Suggested Flow:**

1. **Introduction (5 minutes)**
   - Explain importance of observability in production
   - Show telemetry hierarchy: Spans → Traces → Metrics → Logs
   - Discuss common debugging scenarios

2. **Demo 1: Azure AI Agent Observability (10 minutes)**
   - Run `observability_azure_ai_agent.py`
   - Show Trace ID output
   - Navigate to Azure Portal > Application Insights
   - Filter by Trace ID in Transaction Search
   - Explore: Request telemetry, Dependencies, Tool calls
   - Highlight: LLM latency, Token usage, Error tracking

3. **Demo 2: Workflow Observability (10 minutes)**
   - Run `observability_workflow.py`
   - Show workflow span hierarchy in console
   - Explain parent-child relationships between spans
   - Demonstrate message passing telemetry
   - Compare with Azure AI agent telemetry structure

4. **Configuration Discussion (5 minutes)**
   - Show `.env` tracing options
   - Explain when to use each backend
   - Discuss sensitive data handling (PII, credentials)
   - Best practices for production environments

5. **Q&A and Troubleshooting (5 minutes)**
   - Common issues: Missing Application Insights connection
   - How to find Trace IDs for debugging
   - Setting up alerts and dashboards
   - Integration with existing monitoring tools

---

## Telemetry Data Collected

### Agent Telemetry
- **Agent Creation**: Model configuration, tool registration
- **Message Processing**: Input/output messages, token counts
- **Tool Calls**: Function name, parameters, results, duration
- **LLM Interactions**: Prompts (optional), completions (optional), token usage
- **Thread Management**: Thread creation, message history

### Workflow Telemetry
- **Workflow Build**: Executor configuration, edge definitions
- **Workflow Execution**: Start/end times, input/output data
- **Executor Processing**: Handler invocations, message handling
- **Message Publishing**: Source executor, target executor, message content
- **State Management**: Context updates, workflow state transitions

---

## Viewing Traces in Azure Portal

1. **Navigate to Application Insights**
   - Open Azure Portal
   - Go to your Application Insights resource
   - Select "Transaction search" from the left menu

2. **Filter by Trace ID**
   - Copy the Trace ID from the console output
   - Paste into the search box
   - View the complete trace timeline

3. **Analyze Telemetry**
   - **End-to-end transaction**: See the full request flow
   - **Dependencies**: View LLM API calls, tool executions
   - **Performance**: Identify slow operations
   - **Custom properties**: Examine agent-specific metadata

4. **Create Dashboards**
   - Pin frequently used queries
   - Create alerts for failures or slow requests
   - Monitor token usage and costs
   - Track agent performance over time

---

## Advanced Scenarios

### Sensitive Data Handling

By default, sensitive data (prompts, completions, PII) is NOT logged. To enable for debugging:

```python
await setup_azure_ai_observability(project_client, enable_sensitive_data=True)
```

⚠️ **Security Warning**: Only enable sensitive data logging in non-production environments.

### Custom Spans

Add custom telemetry to your code:

```python
from agent_framework.observability import get_tracer
from opentelemetry.trace import SpanKind

with get_tracer().start_as_current_span("Custom Operation", kind=SpanKind.CLIENT) as span:
    span.set_attribute("custom.property", "value")
    # Your code here
```

### Multiple Tracing Backends

You can enable multiple backends simultaneously:

```bash
# Send to both Application Insights and OTLP
APPLICATIONINSIGHTS_CONNECTION_STRING="..."
OTLP_ENDPOINT=http://localhost:4317
ENABLE_DEVUI_TRACING=true
```

---

## Troubleshooting

### Issue: No Application Insights connection string found
**Solution**: Attach Application Insights to your Azure AI project in Azure AI Studio:
1. Navigate to your project in Azure AI Studio
2. Go to "Settings" > "Connected resources"
3. Add Application Insights resource
4. Restart your application

### Issue: Traces not appearing in Azure Portal
**Possible causes:**
- Application Insights ingestion delay (up to 5 minutes)
- Incorrect connection string
- Network connectivity issues
**Solution**: Wait a few minutes and refresh. Verify connection string in `.env`.

### Issue: DevUI tracing not working
**Solution**: Ensure all three variables are set:
```bash
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
```

### Issue: OTLP endpoint not reachable
**Solution**: Ensure your OTLP receiver (Jaeger/Zipkin) is running:
```bash
# For local Jaeger
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

---

## Additional Resources

- [Azure Monitor Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [Agent Framework Observability Guide](../../docs/observability.md)
- [Production Best Practices](../../AQ-CODE/docs/MAF_LLMOPS_BEST_PRACTICES.md)

---

## Workshop Tips

**For Hands-On Labs:**
1. Pre-configure Application Insights for all attendees
2. Provide sample Trace IDs for exploration
3. Set up shared dashboard for live demo
4. Prepare troubleshooting scenarios

**For Demo-Driven Format:**
1. Run samples with pre-recorded output
2. Show Azure Portal navigation
3. Demonstrate alert configuration
4. Discuss cost implications

**Time Allocation:**
- Setup and introduction: 5 minutes
- observability_azure_ai_agent.py demo: 10 minutes
- observability_workflow.py demo: 10 minutes
- Configuration and best practices: 5 minutes
- Q&A: 5 minutes
- **Total: 35 minutes**

---

## Next Steps

After completing these observability samples, attendees should:
1. Enable Application Insights for their own projects
2. Configure appropriate tracing for their environment
3. Create custom dashboards for monitoring
4. Set up alerts for production issues
5. Implement custom spans for business logic
6. Review telemetry data to optimize performance

For more advanced observability patterns, see:
- `AQ-CODE/llmops/examples/production_agent_enhanced.py` - Production-ready agent with full observability
- `AQ-CODE/llmops/examples/production_agent_with_lifecycle.py` - Lifecycle management with tracing

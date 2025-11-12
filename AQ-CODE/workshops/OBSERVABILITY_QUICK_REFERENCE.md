# Observability Workshop Quick Reference

## Files Location
```
AQ-CODE/observability/
├── observability_azure_ai_agent.py     # Azure AI agent with App Insights
├── observability_workflow.py            # Workflow telemetry demo
└── OBSERVABILITY_SAMPLES.md            # Full documentation
```

## Quick Start

### 1. Verify Environment
```bash
cd AQ-CODE/observability
cat .env | grep -E "AZURE_AI_PROJECT_ENDPOINT|APPLICATIONINSIGHTS"
```

### 2. Run Azure AI Agent Demo
```bash
python observability_azure_ai_agent.py
```
**Shows:** Single agent with tool calling + Application Insights integration

### 3. Run Workflow Demo
```bash
python observability_workflow.py
```
**Shows:** Sequential workflow with executor-level telemetry

---

## Environment Variables (.env)

### Required for Agent Demo
```bash
AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/..."
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1-mini"
```

### Tracing Options (choose one or more)
```bash
# Option 1: Console (simplest)
ENABLE_CONSOLE_TRACING=true

# Option 2: Azure AI (recommended)
ENABLE_AZURE_AI_TRACING=true

# Option 3: OTLP (Jaeger/Zipkin)
OTLP_ENDPOINT=http://localhost:4317

# Option 4: Direct connection
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=xxx;..."

# DevUI (workshop demo)
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
```

---

## Workshop Flow (35 minutes)

### 1. Introduction (5 min)
- Why observability matters for AI agents
- Telemetry hierarchy: Spans → Traces → Metrics
- Common debugging scenarios

### 2. Agent Demo (10 min)
**Run:** `python observability_azure_ai_agent.py`

**Show:**
- ✓ Automatic App Insights configuration
- ✓ Trace ID output
- ✓ Multi-turn conversation
- ✓ Tool call tracking

**Azure Portal:**
1. Copy Trace ID from output
2. Navigate to Application Insights
3. Transaction Search → Filter by Trace ID
4. Show: Request timeline, Dependencies, Tool calls

### 3. Workflow Demo (10 min)
**Run:** `python observability_workflow.py`

**Show:**
- ✓ Workflow build span
- ✓ Executor processing spans
- ✓ Message passing telemetry
- ✓ Parent-child relationships

**Explain:**
- Sequential pattern (UpperCase → Reverse)
- Span hierarchy visualization
- Message flow between executors

### 4. Configuration (5 min)
**Show `.env` options:**
- Console: Development/debugging
- Azure AI: Production monitoring
- OTLP: Custom observability stacks
- DevUI: Interactive demos

**Best Practices:**
- Enable sensitive data ONLY in dev
- Use Application Insights for production
- Set up alerts for failures
- Monitor token usage/costs

### 5. Q&A (5 min)
**Common Questions:**
- How to find traces in Azure Portal?
- What data is logged by default?
- How to add custom telemetry?
- Cost implications?

---

## Key Talking Points

### Agent Telemetry Includes:
- ✓ Agent creation and configuration
- ✓ Message input/output
- ✓ Tool calls (name, params, results)
- ✓ LLM interactions (token counts)
- ✓ Thread management

### Workflow Telemetry Includes:
- ✓ Workflow build configuration
- ✓ Executor processing times
- ✓ Message passing events
- ✓ State transitions
- ✓ Error tracking

---

## Azure Portal Navigation

### Finding Traces
1. **Azure Portal** → **Application Insights**
2. **Left menu** → **Transaction search**
3. **Search box** → Paste Trace ID
4. **View** → End-to-end transaction

### What to Show
- **Request timeline**: Full execution flow
- **Dependencies**: External API calls (OpenAI)
- **Custom properties**: Agent metadata
- **Performance**: Duration of each operation

---

## Demo Script

### Azure AI Agent Demo

```bash
# Terminal 1: Run the agent
python observability_azure_ai_agent.py
```

**Output highlights:**
```
✓ Application Insights connection string retrieved
✓ Observability configured
Trace ID: 1234567890abcdef...

User: What's the weather in Amsterdam?
WeatherAgent: [calls get_weather tool] → sunny, 22°C

User: and in Paris, and which is better?
WeatherAgent: [calls get_weather twice] → Compare results
```

**Azure Portal:**
- Show Trace ID search
- Highlight tool call dependencies
- Display token usage metrics
- Explain span relationships

---

### Workflow Demo

```bash
# Terminal 2: Run the workflow
python observability_workflow.py
```

**Output highlights:**
```
Tracing Configuration:
✓ Application Insights Direct: Enabled

Trace ID: abcdef1234567890...

UpperCaseExecutor: 'hello world' → 'HELLO WORLD'
ReverseTextExecutor: 'HELLO WORLD' → 'DLROW OLLEH'

✓ Workflow completed: 'DLROW OLLEH'
```

**Explain:**
- Parent span: "Sequential Workflow Scenario"
- Child spans: Workflow build, execution
- Grandchild spans: Executor handlers
- Message passing events

---

## Troubleshooting

### "No Application Insights connection string found"
**Fix:** Attach Application Insights to your Azure AI project
1. Azure AI Studio → Your project
2. Settings → Connected resources
3. Add Application Insights

### "Traces not appearing"
**Possible causes:**
- Ingestion delay (wait 2-5 minutes)
- Wrong connection string
- Network issues

### "Import errors"
**Fix:** Install dependencies
```bash
pip install -r requirements.txt
```

---

## Code Snippets for Reference

### Setup Azure AI Observability
```python
from agent_framework.observability import setup_observability
from azure.ai.projects.aio import AIProjectClient

async def setup_azure_ai_observability(project_client: AIProjectClient):
    conn_string = await project_client.telemetry.get_application_insights_connection_string()
    setup_observability(applicationinsights_connection_string=conn_string)
```

### Custom Spans
```python
from agent_framework.observability import get_tracer

with get_tracer().start_as_current_span("Custom Operation") as span:
    span.set_attribute("business.metric", value)
    # Your code here
```

### Get Trace ID
```python
from opentelemetry.trace.span import format_trace_id

with get_tracer().start_as_current_span("Operation") as span:
    trace_id = format_trace_id(span.get_span_context().trace_id)
    print(f"Trace ID: {trace_id}")
```

---

## Workshop Materials Checklist

- [ ] Verify `.env` file has required variables
- [ ] Test both samples before workshop
- [ ] Prepare Azure Portal bookmark (Application Insights)
- [ ] Create sample Trace IDs for attendees
- [ ] Set up shared dashboard (optional)
- [ ] Print this quick reference for attendees
- [ ] Prepare troubleshooting scenarios
- [ ] Have backup OTLP endpoint (Jaeger Docker)

---

## Next Steps for Attendees

After the workshop:
1. Enable Application Insights for your project
2. Run both samples in your environment
3. Explore traces in Azure Portal
4. Create custom dashboard
5. Set up alerts for failures
6. Implement custom spans in your code
7. Review production telemetry patterns in `AQ-CODE/llmops/`

---

## Additional Resources

- **Full Documentation**: `OBSERVABILITY_SAMPLES.md`
- **Production Examples**: `AQ-CODE/llmops/examples/`
- **LLMOps Best Practices**: `AQ-CODE/docs/MAF_LLMOPS_BEST_PRACTICES.md`
- **Azure Monitor**: https://learn.microsoft.com/azure/azure-monitor/
- **OpenTelemetry**: https://opentelemetry.io/docs/instrumentation/python/

---

## Contact & Support

For questions during the workshop:
- Check `OBSERVABILITY_SAMPLES.md` for detailed docs
- Review error messages in console output
- Verify `.env` configuration
- Check Azure Portal for ingestion status

---

**Last Updated**: November 2025
**Workshop Module**: Module 4 - Production & Operations
**Duration**: 35 minutes (includes Q&A)

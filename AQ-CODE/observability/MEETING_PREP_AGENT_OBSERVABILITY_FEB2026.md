# Agent Observability - PSA Meeting Prep

**Date**: February 2026  
**Topic**: Agent Observability in Microsoft Agent Framework + Foundry Control Plane  
**Audience**: Fellow PSAs  
**Prep Materials**: This document + live demos in `AQ-CODE/observability/` and `AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025/`

---

## TL;DR for the Meeting

Observability for agents has matured significantly since our last look (Dec 2025). Three big shifts:

1. **Foundry Control Plane** is now GA-track — unified fleet management UI for agents across Foundry, SRE Agent, Logic Apps, and custom platforms
2. **MAF observability API was revamped** — `setup_observability()` is deprecated, replaced by `configure_otel_providers()` + standard OTEL env vars
3. **New capabilities** — Continuous Evaluation (preview), AI Red Teaming Agent, Grafana dashboards, Custom agent registration, Agent lifecycle management

---

## 1. The Foundry Control Plane (the big picture)

**URL**: https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/overview?view=foundry  
**Portal**: https://ai.azure.com → Operate tab (upper right)

The Control Plane is organized into 4 pillars (see the wheel diagram):

| Pillar | Sub-capabilities | What It Gives You |
|--------|-----------------|-------------------|
| **Fleet Management** | Agent discovery, Inventory, Actions (start/stop/block) | Central view of all agents across projects |
| **Observability** | Traces, Evaluations (continuous), Metrics | Debug + monitor agent quality in production |
| **Compliance** | Guardrails, Policies, Controls | Enforce Responsible AI at fleet scale |
| **Security** | Identity (Entra ID), Access controls | Red teaming, Defender/Purview integration |

### Supported Agent Platforms (expanded since Dec)

| Platform | Auto-discovered | Lifecycle Ops | Notes |
|----------|----------------|---------------|-------|
| Foundry agents (prompt, workflow, hosted) | Yes | Start/Stop | Full observability |
| Azure SRE Agent | Yes | Start/Stop | New addition |
| Azure Logic Apps agent loop | Yes | Start/Stop | No traces/metrics yet |
| Custom agents (any platform) | Manual registration | Block/Unblock | Requires instrumentation |

### Key Portal Features to Demo

1. **Operate > Overview** — Fleet health score, cost trends, run completion, prevented behaviors
2. **Operate > Assets** — Agent inventory table with filtering, health scores, cost, token usage
3. **Operate > Assets > [agent] > Traces** — Click any agent → Traces tab → full span tree
4. **Operate > Compliance** — Policy violations, guardrail assignments, bulk remediation

---

## 2. What Changed in MAF Observability (Code Level)

### The Migration (Old → New)

| Old (Dec 2025) | New (Current) | Notes |
|-----------------|---------------|-------|
| `from agent_framework.observability import setup_observability` | `from agent_framework.observability import configure_otel_providers` | Main entry point |
| `setup_observability(otlp_endpoint=...)` | Standard env: `OTEL_EXPORTER_OTLP_ENDPOINT` | OTEL-compliant |
| `setup_observability(applicationinsights_connection_string=...)` | `AzureAIClient.configure_azure_monitor()` | Azure-specific |
| `OTLP_ENDPOINT` env var | `OTEL_EXPORTER_OTLP_ENDPOINT` | Standard naming |
| `ENABLE_OTEL=true` | `ENABLE_INSTRUMENTATION=true` | Clearer naming |
| Console was automatic fallback | `ENABLE_CONSOLE_EXPORTERS=true` | Now opt-in |
| `AzureAIAgentClient(agents_client=...)` | `AzureAIClient(project_client=...)` | Simpler client |
| Plain function tool | `@tool(approval_mode="never_require")` | Safety controls |
| No agent id | `id="weather-agent"` on ChatAgent | Control Plane tracking |

### Five Observability Patterns (from simplest to most advanced)

**Pattern 1: Standard OTEL env vars** (recommended starting point)
```python
from agent_framework.observability import configure_otel_providers
# Set OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 in .env
configure_otel_providers()
```

**Pattern 2: Custom exporters**
```python
from agent_framework.observability import configure_otel_providers
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
configure_otel_providers(exporters=[OTLPSpanExporter(endpoint="http://localhost:4317")])
```

**Pattern 3: Azure Monitor (for Foundry projects)** ← most relevant for PSAs
```python
from agent_framework.azure import AzureAIClient
async with AzureAIClient(project_client=project_client) as client:
    await client.configure_azure_monitor(enable_live_metrics=True)
```

**Pattern 4: Third-party (Langfuse, etc.)**
```python
from agent_framework.observability import enable_instrumentation
# Set up Langfuse/other SDK first, then:
enable_instrumentation(enable_sensitive_data=False)
```

**Pattern 5: Zero-code auto-instrumentation**
```bash
opentelemetry-instrument --traces_exporter otlp python my_agent.py
```

### New: Grafana Dashboards

Pre-built Grafana dashboards that connect to your Application Insights data:
- **Agent Overview**: https://aka.ms/amg/dash/af-agent — per-agent health, latency, errors, tokens
- **Workflow Overview**: https://aka.ms/amg/dash/af-workflow — workflow execution, executor timing

### New: Aspire Dashboard for Local Dev

No Azure needed — run locally via Docker:
```bash
docker run --rm -d -p 18888:18888 -p 4317:18889 mcr.microsoft.com/dotnet/aspire-dashboard:latest
# Set OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
# Visit http://localhost:18888
```

---

## 3. New: Continuous Evaluation (Preview)

**Docs**: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/continuous-evaluation-agents?view=foundry

Continuous evaluation automatically scores agent interactions at a configurable sampling rate. Evaluators include:

| Evaluator | Category | What It Measures |
|-----------|----------|-----------------|
| Task Adherence | Agent quality | Did the agent follow its instructions? |
| Intent Resolution | Agent quality | Did it resolve the user's request? |
| Tool Call Success | Agent quality | Were tools called correctly? |
| Groundedness | RAG quality | Are responses grounded in retrieved data? |
| Relevance | Quality | Is the response relevant to the query? |
| Fluency | Quality | Is the language natural and clear? |
| Coherence | Quality | Is the reasoning logically consistent? |
| Sensitive Data Leakage | Safety | Did it leak PII or secrets? |
| Jailbreak/XPIA exposure | Safety | Was the agent manipulated? |

### Setup (Python SDK)

```python
from azure.ai.projects.models import EvaluatorIds, AgentEvaluationRequest

evaluators = {
    "Relevance": {"Id": EvaluatorIds.Relevance.value},
    "Fluency": {"Id": EvaluatorIds.Fluency.value},
    "Coherence": {"Id": EvaluatorIds.Coherence.value},
}

project_client.evaluation.create_agent_evaluation(
    AgentEvaluationRequest(
        thread=thread.id,
        run=run.id,
        evaluators=evaluators,
        appInsightsConnectionString=project_client.telemetry.get_application_insights_connection_string(),
    )
)
```

Results flow into Application Insights as `gen_ai.evaluation.result` traces and are visible in the Foundry Portal > Operate > Assets > [agent] > Monitoring tab.

---

## 4. Suggested Demo Flow (30-40 min)

### Part 1: The Why (5 min)
- Show the Control Plane wheel diagram (4 pillars)
- Ask: "How many agents does your org have? Who owns them? Are they compliant?"
- Frame the problem: going from 1 copilot to a fleet of specialized agents

### Part 2: Agent Observability Demo (10 min)
- Run `observability_azure_ai_agent.py` (updated to use AzureAIClient pattern)
- Show Trace ID in console
- Navigate to Foundry Portal > Operate > Assets > WeatherAgent > Traces
- Show the span tree: agent → LLM call → tool call → LLM response
- Highlight: agent `id` parameter ties it to the Control Plane inventory

### Part 3: Workflow Observability Demo (10 min)
- Run `observability_workflow.py` (updated to use configure_otel_providers)
- Show 3-executor span hierarchy in Aspire Dashboard (or App Insights)
- Discuss message passing telemetry between executors
- Show Grafana workflow dashboard if available

### Part 4: Fleet Management & Control Plane (10 min)
- Navigate through Foundry Portal > Operate tabs:
  - **Overview**: Fleet health score, trends
  - **Assets**: Filter by health score, cost, error rate
  - **Compliance**: Show policy violations
- Show agent lifecycle: Start/Stop/Block
- Mention continuous evaluation (preview) for automated quality scoring
- Mention AI Red Teaming Agent for security scanning

### Part 5: Q&A (5 min)
- "How do I instrument MY agents?" → Pattern 3 (AzureAIClient) or Pattern 1 (OTEL)
- "What about non-Foundry agents?" → Custom agent registration
- "What about cost?" → Token tracking in Control Plane + Grafana dashboards

---

## 5. Key Links for Attendees

| Resource | URL |
|----------|-----|
| Control Plane overview | https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/overview?view=foundry |
| Manage agents at scale | https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/how-to-manage-agents?view=foundry |
| Monitor across fleet | https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/monitoring-across-fleet?view=foundry |
| Register custom agents | https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/register-custom-agent?view=foundry |
| Continuous evaluation | https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/continuous-evaluation-agents?view=foundry |
| AI Red Teaming Agent | https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/ai-red-teaming-agent?view=foundry |
| Compliance & security | https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/how-to-manage-compliance-security?view=foundry |
| Cost optimization | https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/how-to-optimize-cost-performance?view=foundry |
| Grafana agent dashboard | https://aka.ms/amg/dash/af-agent |
| Grafana workflow dashboard | https://aka.ms/amg/dash/af-workflow |
| MAF observability samples | `maf-upstream/python/samples/getting_started/observability/` |
| Aspire Dashboard setup | https://learn.microsoft.com/en-us/dotnet/aspire/fundamentals/dashboard/standalone |

---

## 6. Files Updated for This Meeting

| File | What Changed |
|------|-------------|
| `observability/observability_azure_ai_agent.py` | Migrated to `AzureAIClient.configure_azure_monitor()`, `@tool` decorator, agent `id` |
| `observability/observability_workflow.py` | Migrated to `configure_otel_providers()`, standard OTEL env vars |
| `observability/README.md` | Updated env vars, setup patterns, viewing traces section, timestamps |
| `FOUNDRY-CONTROL-PLANE-DEC-2025/README.md` | Added Feb 2026 features, supported platforms, new doc links |
| `observability/observability_azure_ai_agent_dec2025.py` | Backup of previous version |
| `observability/observability_workflow_dec2025.py` | Backup of previous version |

---

## 7. Talking Points / Sound Bites

- "Control Plane turns ad-hoc agent monitoring into fleet-scale governance"
- "One line of code: `await client.configure_azure_monitor()` — and you get traces, metrics, and cost tracking"
- "The `id` parameter on ChatAgent is the bridge between your code and the Control Plane inventory"
- "Continuous evaluation means your agents are being scored for quality and safety automatically in production"
- "Custom agent registration means even non-Foundry agents (CrewAI, LangGraph, etc.) can appear in the fleet view"
- "Grafana dashboards give you the operational view without building custom dashboards"

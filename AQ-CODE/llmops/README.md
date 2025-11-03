# LLMOps for Microsoft Agent Framework (MAF)

This directory contains LLMOps utilities and best practices for production-ready MAF agents.

## 📋 Contents

### Documentation
- **[MAF_LLMOPS_BEST_PRACTICES.md](MAF_LLMOPS_BEST_PRACTICES.md)** - Comprehensive guide (60+ pages) covering:
  - Development best practices
  - Testing & evaluation strategies
  - Deployment & CI/CD
  - Monitoring & observability
  - Governance & compliance
  - Cost management
  - Real-world implementation examples

### LLMOps Modules

#### `observability.py`
Application Insights integration for MAF agents:
- Distributed tracing with OpenTelemetry
- Custom metrics (agent calls, latency, token usage)
- Span creation for detailed tracking

```python
from llmops import MAFObservability

observability = MAFObservability()
observability.track_agent_call(
    agent_name="market_analyst",
    duration_ms=1250.5,
    tokens=850,
    success=True
)
```

#### `cost_tracker.py`
Cost tracking and budget management:
- Real-time cost calculation based on model pricing
- Token usage tracking per agent
- Daily budget enforcement
- Per-request token limits

```python
from llmops import CostTracker, TokenBudgetManager

# Track costs
cost_tracker = CostTracker()
cost_tracker.record_cost(
    model="gpt-4.1",
    prompt_tokens=100,
    completion_tokens=500,
    agent_name="analyst"
)
print(f"Total cost: ${cost_tracker.get_total_cost():.4f}")

# Enforce budgets
budget_manager = TokenBudgetManager()
allowed, message = budget_manager.check_budget(estimated_tokens=800)
if allowed:
    # Proceed with request
    budget_manager.record_usage(request_id, actual_tokens)
```

#### `evaluator.py`
Response quality evaluation:
- Topic coverage analysis
- Citation detection
- Quantitative data presence
- Structure assessment
- Sentiment analysis
- Overall quality scoring

```python
from llmops import AgentEvaluator

evaluator = AgentEvaluator()
metrics = evaluator.evaluate_response(
    response="NVIDIA's P/E ratio is 45.2 as of Q4 2025...",
    expected_topics=["P/E ratio", "NVIDIA", "valuation"]
)
print(f"Quality Score: {metrics['overall_score']:.2f}")
print(f"Quality Label: {evaluator.get_quality_label(metrics['overall_score'])}")
```

### Examples

#### `example_production_agent.py`
Complete working example demonstrating:
- Agent initialization with LLMOps integration
- Budget checking before requests
- Cost tracking with real-time calculations
- Response evaluation with metrics
- Observability tracking
- Structured output with comprehensive logging

**Run the example:**
```bash
python AQ-CODE/llmops/example_production_agent.py
```

**Example output:**
```
================================================================================
🚀 MAF Production Agent with LLMOps - Demo
================================================================================

################################################################################
# Test Query 1/2
################################################################################

================================================================================
🤖 Agent: market_analyst
📝 Query: What is NVIDIA's current P/E ratio and how does it compare to industry averages?
🆔 Request ID: 3f7d8a9b-c4e2-4f8a-b5d3-1e6c9a8b2d4f
================================================================================
✅ Budget Check: OK (estimated 525 tokens)
🔄 Running agent...
💰 Cost Tracking:
   Prompt tokens: 195
   Completion tokens: 750
   Total tokens: 945
   Estimated cost: $0.0285

📊 Quality Evaluation:
   Overall Score: 0.82 (Excellent)
   Topic Coverage: 100%
   Has Citations: ✅
   Has Numbers: ✅
   Well Structured: ✅

⏱️  Duration: 1245ms

💬 Response:
--------------------------------------------------------------------------------
Based on current market data as of November 2025, NVIDIA's P/E ratio is 
approximately 45.2, significantly above the semiconductor industry average 
of 28.5. This premium valuation reflects investor confidence in NVIDIA's 
AI chip dominance...
--------------------------------------------------------------------------------
```

## 🚀 Quick Start

### 1. Install Dependencies
Already included in your `requirements.txt`:
- `opentelemetry-api`
- `opentelemetry-sdk`
- `azure-monitor-opentelemetry`

### 2. Configure Environment
Add to your `.env` file:

```bash
# Monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=<your-app-insights-connection>
ENABLE_TRACING=true

# Cost Controls
DAILY_TOKEN_BUDGET=1000000
MAX_TOKENS_PER_REQUEST=4000

# Model Configuration
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1
```

### 3. Use in Your Agents

```python
from llmops import MAFObservability, CostTracker, TokenBudgetManager, AgentEvaluator

# Initialize LLMOps components
observability = MAFObservability()
cost_tracker = CostTracker()
budget_manager = TokenBudgetManager()
evaluator = AgentEvaluator()

# In your agent workflow
async def run_agent_with_llmops(agent, query: str):
    # Check budget
    estimated_tokens = len(query.split()) * 1.5 + 500
    allowed, msg = budget_manager.check_budget(int(estimated_tokens))
    if not allowed:
        return {"error": msg}
    
    # Run agent with tracking
    start = time.time()
    response = await agent.run(query)
    duration_ms = (time.time() - start) * 1000
    
    # Track costs
    tokens = len(response.split()) * 1.5
    cost_tracker.record_cost("gpt-4.1", 100, int(tokens), "my_agent")
    
    # Evaluate quality
    metrics = evaluator.evaluate_response(response, ["topic1", "topic2"])
    
    # Track observability
    observability.track_agent_call("my_agent", duration_ms, int(tokens), True)
    
    return {"response": response, "metrics": metrics}
```

## 📊 Monitoring

### Application Insights Queries

**Agent Performance:**
```kusto
customMetrics
| where name == "maf.agent.calls"
| summarize 
    TotalCalls = sum(value),
    AvgLatency = avg(todouble(customDimensions["latency_ms"])),
    ErrorRate = todouble(countif(customDimensions["success"] == "false")) / count() * 100
by tostring(customDimensions["agent.name"])
```

**Cost Analysis:**
```kusto
customMetrics
| where name == "maf.tokens.used"
| extend cost = value * 0.00003  // Adjust per your model pricing
| summarize TotalCost = sum(cost) by bin(timestamp, 1h)
```

**Error Tracking:**
```kusto
customMetrics
| where name == "maf.agent.calls" and customDimensions["success"] == "false"
| project timestamp, agent = tostring(customDimensions["agent.name"])
| order by timestamp desc
```

## 🎯 Key Benefits

### For Development
- ✅ Structured code organization
- ✅ Reusable LLMOps components
- ✅ Easy integration into existing agents
- ✅ Clear separation of concerns

### For Operations
- ✅ Real-time cost tracking
- ✅ Budget enforcement
- ✅ Quality monitoring
- ✅ Full observability with App Insights

### For Business
- ✅ Cost control and optimization
- ✅ Quality assurance
- ✅ Audit trails
- ✅ Performance metrics

## 📖 Related Resources

- [MAF Documentation](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry](https://ai.azure.com)
- [Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)

## 🤝 Contributing

When adding new LLMOps capabilities:
1. Create module in `llmops/`
2. Add imports to `__init__.py`
3. Update this README
4. Create example usage
5. Add tests (future)

## 💡 Next Steps

1. **Run the example**: `python AQ-CODE/llmops/example_production_agent.py`
2. **Review best practices**: Read `MAF_LLMOPS_BEST_PRACTICES.md`
3. **Integrate into your agents**: Use the modules in your workflows
4. **Set up monitoring**: Configure Application Insights dashboards
5. **Implement CI/CD**: Follow deployment best practices from docs

---

**Version:** 1.0  
**Last Updated:** November 3, 2025  
**Maintained by:** AI Solutions Architecture Team

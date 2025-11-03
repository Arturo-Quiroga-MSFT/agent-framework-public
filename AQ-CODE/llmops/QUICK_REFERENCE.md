# LLMOps Quick Reference for MAF

> **TL;DR**: This is your cheat sheet for implementing LLMOps in Microsoft Agent Framework projects.

## 🎯 What is LLMOps?

**LLMOps** = Operations practices for Large Language Model applications

Think of it as **DevOps for AI agents**:
- 🔍 **Monitor** agent behavior in production
- 💰 **Control** costs and token usage
- ✅ **Evaluate** response quality
- 🚀 **Deploy** with confidence
- 📊 **Trace** every interaction

---

## ⚡ Quick Setup (5 Minutes)

### 1. Add to `.env`
```bash
# Monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=<from-azure-portal>
ENABLE_TRACING=true

# Cost Limits
DAILY_TOKEN_BUDGET=1000000
MAX_TOKENS_PER_REQUEST=4000
```

### 2. Import LLMOps
```python
from llmops import (
    MAFObservability,      # Tracing & metrics
    CostTracker,           # Cost calculation
    TokenBudgetManager,    # Budget enforcement
    AgentEvaluator         # Quality scoring
)
```

### 3. Initialize Once
```python
# At app startup
observability = MAFObservability()
cost_tracker = CostTracker()
budget_manager = TokenBudgetManager()
evaluator = AgentEvaluator()
```

### 4. Use in Agent Calls
```python
# Before running agent
allowed, msg = budget_manager.check_budget(estimated_tokens=800)

# Run agent
response = await agent.run(query)

# After running agent
cost_tracker.record_cost("gpt-4.1", prompt_tokens, completion_tokens, "agent_name")
metrics = evaluator.evaluate_response(response, expected_topics=["topic1", "topic2"])
observability.track_agent_call("agent_name", duration_ms, tokens, success=True)
```

---

## 📊 Common Patterns

### Pattern 1: Budget-Controlled Agent
```python
async def safe_agent_run(agent, query: str):
    """Run agent with budget protection."""
    
    # Estimate tokens
    est_tokens = len(query.split()) * 1.5 + 500
    
    # Check budget
    allowed, msg = budget_manager.check_budget(int(est_tokens))
    if not allowed:
        return {"error": f"Budget exceeded: {msg}"}
    
    # Run agent
    response = await agent.run(query)
    
    # Record usage
    actual_tokens = len(response.split()) * 1.5
    budget_manager.record_usage(request_id, int(actual_tokens))
    
    return {"response": response}
```

### Pattern 2: Cost-Tracked Agent
```python
async def cost_aware_agent_run(agent, query: str):
    """Run agent with cost tracking."""
    
    response = await agent.run(query)
    
    # Calculate costs
    prompt_tokens = len(query.split()) * 1.5
    completion_tokens = len(response.split()) * 1.5
    
    cost_tracker.record_cost(
        model="gpt-4.1",
        prompt_tokens=int(prompt_tokens),
        completion_tokens=int(completion_tokens),
        agent_name="my_agent"
    )
    
    # Get total cost
    total_cost = cost_tracker.get_total_cost()
    print(f"Total spent: ${total_cost:.4f}")
    
    return response
```

### Pattern 3: Quality-Evaluated Agent
```python
async def quality_checked_agent_run(agent, query: str, expected_topics: list):
    """Run agent with quality evaluation."""
    
    response = await agent.run(query)
    
    # Evaluate response
    metrics = evaluator.evaluate_response(
        response=response,
        expected_topics=expected_topics
    )
    
    # Check if acceptable
    if metrics['overall_score'] < 0.6:
        print(f"⚠️ Low quality response: {metrics['overall_score']:.2f}")
    
    quality_label = evaluator.get_quality_label(metrics['overall_score'])
    print(f"Quality: {quality_label} ({metrics['overall_score']:.2f})")
    
    return {"response": response, "quality": metrics}
```

### Pattern 4: Full LLMOps Agent
```python
async def production_agent_run(agent, query: str):
    """Run agent with full LLMOps pipeline."""
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # 1. Budget check
        est_tokens = len(query.split()) * 1.5 + 500
        allowed, msg = budget_manager.check_budget(int(est_tokens))
        if not allowed:
            return {"error": msg}
        
        # 2. Run agent with tracing
        with observability.create_span("agent.execute"):
            response = await agent.run(query)
        
        # 3. Track costs
        prompt_tokens = int(len(query.split()) * 1.5)
        completion_tokens = int(len(response.split()) * 1.5)
        cost_tracker.record_cost("gpt-4.1", prompt_tokens, completion_tokens, "agent")
        budget_manager.record_usage(request_id, prompt_tokens + completion_tokens)
        
        # 4. Evaluate quality
        metrics = evaluator.evaluate_response(response, ["topic1", "topic2"])
        
        # 5. Track observability
        duration_ms = (time.time() - start_time) * 1000
        observability.track_agent_call(
            "agent", duration_ms, prompt_tokens + completion_tokens, True
        )
        
        return {
            "success": True,
            "response": response,
            "metrics": metrics,
            "cost": cost_tracker.get_total_cost()
        }
        
    except Exception as e:
        # Track failure
        duration_ms = (time.time() - start_time) * 1000
        observability.track_agent_call("agent", duration_ms, 0, False)
        return {"success": False, "error": str(e)}
```

---

## 🔍 Monitoring Cheat Sheet

### Application Insights Queries

**Check agent performance:**
```kusto
customMetrics
| where name == "maf.agent.calls"
| summarize Count = sum(value) by bin(timestamp, 5m)
```

**Track costs:**
```kusto
customMetrics
| where name == "maf.tokens.used"
| extend cost = value * 0.00003
| summarize TotalCost = sum(cost) by bin(timestamp, 1h)
```

**Find errors:**
```kusto
customMetrics
| where name == "maf.agent.calls" and customDimensions["success"] == "false"
| project timestamp, agent = tostring(customDimensions["agent.name"])
```

**P95 latency:**
```kusto
customMetrics
| where name == "maf.agent.latency"
| summarize p95 = percentile(value, 95) by bin(timestamp, 5m)
```

---

## 💰 Cost Management

### Model Pricing (Nov 2025)
| Model | Prompt (per 1K tokens) | Completion (per 1K tokens) |
|-------|------------------------|----------------------------|
| gpt-4.1 | $0.030 | $0.060 |
| gpt-4o | $0.005 | $0.015 |
| gpt-4o-mini | $0.00015 | $0.0006 |
| gpt-5-mini | $0.0001 | $0.0004 |

### Cost Calculation
```python
# Manual calculation
prompt_cost = (prompt_tokens / 1000) * 0.03    # gpt-4.1
completion_cost = (completion_tokens / 1000) * 0.06
total_cost = prompt_cost + completion_cost

# Or use CostTracker
cost_tracker.record_cost("gpt-4.1", prompt_tokens, completion_tokens, "agent")
print(f"Total: ${cost_tracker.get_total_cost():.4f}")
```

### Budget Management
```python
# Set in .env
DAILY_TOKEN_BUDGET=1000000          # 1M tokens per day
MAX_TOKENS_PER_REQUEST=4000         # 4K tokens per request

# Check current usage
stats = budget_manager.get_usage_stats()
print(f"Used: {stats['percentage_used']:.1f}%")
print(f"Remaining: {stats['remaining_tokens']:,} tokens")
```

---

## ✅ Quality Metrics

### Evaluation Scores

| Score | Label | Meaning |
|-------|-------|---------|
| 0.8 - 1.0 | Excellent | Production ready |
| 0.6 - 0.8 | Good | Minor improvements |
| 0.4 - 0.6 | Fair | Needs work |
| 0.0 - 0.4 | Poor | Significant issues |

### What Gets Evaluated

```python
metrics = evaluator.evaluate_response(response, expected_topics)

# Returns:
{
    "topic_coverage": 0.85,      # 85% of topics covered
    "has_citations": True,        # Includes sources/dates
    "has_numbers": True,          # Contains data/metrics
    "has_structure": True,        # Well formatted
    "sentiment_neutral": True,    # Professional tone
    "overall_score": 0.82         # Weighted average
}
```

---

## 🚨 Common Issues & Solutions

### Issue: Budget Exceeded
```python
# Problem
allowed, msg = budget_manager.check_budget(tokens)
# Returns: (False, "Daily budget exceeded")

# Solution 1: Increase budget
# In .env: DAILY_TOKEN_BUDGET=2000000

# Solution 2: Check usage
stats = budget_manager.get_usage_stats()
print(f"Used: {stats['total_tokens']:,} / {stats['budget']:,}")

# Solution 3: Reset (new day)
# Budget resets automatically at midnight UTC
```

### Issue: High Costs
```python
# Problem
cost = cost_tracker.get_total_cost()
# Returns: $45.67 (too high!)

# Solution 1: Check cost by agent
by_agent = cost_tracker.get_cost_by_agent()
print(by_agent)  # {"agent1": 30.50, "agent2": 15.17}

# Solution 2: Switch to cheaper model
# In .env: AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Solution 3: Reduce max tokens
# In .env: MAX_TOKENS_PER_REQUEST=2000
```

### Issue: Low Quality Scores
```python
# Problem
metrics = evaluator.evaluate_response(response, topics)
# Returns: overall_score = 0.45 (Fair)

# Check what's missing
if metrics['topic_coverage'] < 0.7:
    print("❌ Missing topics - improve prompt")
if not metrics['has_citations']:
    print("❌ No sources - add 'cite sources' to instructions")
if not metrics['has_numbers']:
    print("❌ No data - request specific metrics")

# Solution: Update agent instructions
instructions = """
You're an analyst. Always:
- Cover all requested topics
- Cite sources with dates
- Include specific numbers and metrics
- Use structured format
"""
```

### Issue: No Traces in App Insights
```python
# Problem
# No traces appearing in Application Insights

# Solution 1: Check connection string
conn_str = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
print(f"Configured: {bool(conn_str)}")

# Solution 2: Enable tracing
# In .env: ENABLE_TRACING=true

# Solution 3: Verify initialization
observability = MAFObservability()
# Check for startup logs

# Solution 4: Wait 1-2 minutes
# App Insights has slight delay
```

---

## 📚 Learn More

- **Full Guide**: [MAF_LLMOPS_BEST_PRACTICES.md](MAF_LLMOPS_BEST_PRACTICES.md) (60+ pages)
- **Example Code**: [example_production_agent.py](example_production_agent.py)
- **Module Docs**: [README.md](README.md)

---

## 🎓 Customer Conversation Starters

### "How do I monitor my agents in production?"
→ Use MAFObservability + Application Insights
- Real-time tracing of all agent calls
- Custom metrics for latency, tokens, costs
- Dashboards and alerts

### "How do I control AI costs?"
→ Use CostTracker + TokenBudgetManager
- Real-time cost calculation per agent
- Daily budget enforcement
- Per-request token limits
- Cost projection and reporting

### "How do I ensure quality responses?"
→ Use AgentEvaluator
- Automated quality scoring
- Topic coverage analysis
- Citation and data checking
- Regression testing

### "How do I deploy agents safely?"
→ Follow deployment best practices
- CI/CD with automated testing
- Blue-green deployments
- Health checks and monitoring
- Rollback capabilities

---

**Quick Links:**
- 🚀 [Get Started](example_production_agent.py)
- 📖 [Full Documentation](MAF_LLMOPS_BEST_PRACTICES.md)
- 🎯 [Module Reference](README.md)

---

*Last Updated: November 3, 2025*

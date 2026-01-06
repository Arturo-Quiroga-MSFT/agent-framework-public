Here are the KQL queries you can use in Azure Portal → Application Insights → Logs:

## 1. **View All Agent Runs (Last 24 Hours)**
```kql
dependencies
| where timestamp >= ago(24h)
| where type == "GenAI | azure_ai_agents"
| extend props = parse_json(customDimensions)
| project 
    timestamp,
    agent_name = tostring(props["gen_ai.agent.name"]),
    model = tostring(props["gen_ai.request.model"]),
    duration_ms = duration,
    success,
    total_tokens = toint(props["gen_ai.usage.total_tokens"]),
    prompt = tostring(props["gen_ai.prompt"])
| order by timestamp desc
```

## 2. **Agent Performance Summary**
```kql
dependencies
| where timestamp >= ago(24h)
| where type == "GenAI | azure_ai_agents"
| extend props = parse_json(customDimensions)
| extend 
    agent_name = tostring(props["gen_ai.agent.name"]),
    total_tokens = toint(props["gen_ai.usage.total_tokens"])
| summarize 
    total_runs = count(),
    successful_runs = countif(success == true),
    failed_runs = countif(success == false),
    avg_latency_ms = avg(duration),
    p50_latency_ms = percentile(duration, 50),
    p95_latency_ms = percentile(duration, 95),
    total_tokens = sum(total_tokens),
    error_rate_pct = round(100.0 * countif(success == false) / count(), 2)
    by agent_name
| order by total_runs desc
```

## 3. **Token Usage and Estimated Costs by Agent**
```kql
dependencies
| where timestamp >= ago(7d)
| where type == "GenAI | azure_ai_agents"
| extend props = parse_json(customDimensions)
| extend 
    agent_name = tostring(props["gen_ai.agent.name"]),
    model = tostring(props["gen_ai.request.model"]),
    total_tokens = toint(props["gen_ai.usage.total_tokens"])
| summarize 
    total_tokens = sum(total_tokens),
    run_count = count()
    by agent_name, model
| extend estimated_cost_usd = total_tokens * 0.0000004  // Rough estimate
| order by total_tokens desc
```

## 4. **Latency Trends Over Time**
```kql
dependencies
| where timestamp >= ago(24h)
| where type == "GenAI | azure_ai_agents"
| extend props = parse_json(customDimensions)
| extend agent_name = tostring(props["gen_ai.agent.name"])
| summarize 
    avg_latency = avg(duration),
    p95_latency = percentile(duration, 95),
    run_count = count()
    by agent_name, bin(timestamp, 1h)
| order by timestamp desc
| render timechart
```

## 5. **Failed Agent Runs (Errors)**
```kql
dependencies
| where timestamp >= ago(24h)
| where type == "GenAI | azure_ai_agents"
| where success == false
| extend props = parse_json(customDimensions)
| project 
    timestamp,
    agent_name = tostring(props["gen_ai.agent.name"]),
    model = tostring(props["gen_ai.request.model"]),
    duration_ms = duration,
    resultCode,
    data
| order by timestamp desc
```

## 6. **Token Usage Timeline (Daily)**
```kql
dependencies
| where timestamp >= ago(7d)
| where type == "GenAI | azure_ai_agents"
| extend props = parse_json(customDimensions)
| extend 
    agent_name = tostring(props["gen_ai.agent.name"]),
    total_tokens = toint(props["gen_ai.usage.total_tokens"])
| summarize 
    daily_tokens = sum(total_tokens),
    daily_runs = count()
    by agent_name, bin(timestamp, 1d)
| extend estimated_daily_cost = daily_tokens * 0.0000004
| order by timestamp desc
| render columnchart
```

## 7. **Top 10 Slowest Agent Runs**
```kql
dependencies
| where timestamp >= ago(24h)
| where type == "GenAI | azure_ai_agents"
| extend props = parse_json(customDimensions)
| project 
    timestamp,
    agent_name = tostring(props["gen_ai.agent.name"]),
    duration_ms = duration,
    total_tokens = toint(props["gen_ai.usage.total_tokens"]),
    prompt = tostring(props["gen_ai.prompt"])
| top 10 by duration_ms desc
```

## 8. **Agent Activity Heatmap (Runs per Hour)**
```kql
dependencies
| where timestamp >= ago(7d)
| where type == "GenAI | azure_ai_agents"
| extend props = parse_json(customDimensions)
| extend agent_name = tostring(props["gen_ai.agent.name"])
| summarize run_count = count() by agent_name, bin(timestamp, 1h)
| render columnchart
```

**Pro tip:** In the Azure Portal, after running any query:
- Click **"Pin to dashboard"** to create live tiles
- Use **Time range** dropdown to adjust the lookback period
- Click **"Export"** to download results as CSV
- Use **"Columns"** to customize which fields to display
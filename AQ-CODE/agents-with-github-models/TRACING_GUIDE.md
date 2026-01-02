# 📊 Tracing & Observability Guide

This guide explains tracing/observability features in examples 07 and 08 (workflow examples with DevUI).

## 🎯 Built-in DevUI Tracing (Enabled!)

Examples 07 and 08 have **tracing automatically enabled** via the official Microsoft approach:

```python
from agent_framework.devui import serve

serve(
    entities=[workflow],
    port=8082,
    tracing_enabled=True,  # ✅ Official way to enable tracing
)
```

This follows the [official Microsoft documentation](https://learn.microsoft.com/en-us/agent-framework/user-guide/devui/tracing?pivots=programming-language-python) and enables OpenTelemetry tracing for Agent Framework operations.

## What You Get Automatically

When you run the workflows, DevUI captures and displays:

1. **Workflow Visualization** (left panel)
   - Sequential flow diagram (example 07)
   - Fan-out/fan-in diagram (example 08)
   - Real-time execution status

2. **Execution Timeline** (center panel)
   - Operation start/completion times
   - Visual progress indicators
   - Status updates (completed, running)

3. **Trace Details** (right panel - "Traces" tab)
   - Span hierarchy
   - Timing information
   - Agent/workflow events
   - Tool calls and results (if any)

## How It Works

According to Microsoft's docs:

> "DevUI does not create its own spans - it collects the spans that Agent Framework emits during agent and workflow execution, then displays them in the debug panel."

The `tracing_enabled=True` parameter tells DevUI to:
- Capture OpenTelemetry traces from Agent Framework
- Display them in the web interface
- Show execution flow and timing

## Comparing Traces Across Examples

### Example 07 (Sequential)
```
Workflow Execution Flow:
├── input_dispatcher (instant)
├── research executor (~20s)
├── analysis executor (~15s)  ← waits for research
├── writer executor (~20s)     ← waits for analysis
└── output_formatter (instant)
Total: ~55-70s
```

You'll see each operation complete sequentially in the timeline.

### Example 08 (Parallel)
```
Workflow Execution Flow:
├── input_dispatcher (instant)
├── technical executor (15-20s) ┐
├── business executor (15-20s)  ├→ All run simultaneously!
├── risk executor (15-20s)      │
├── creative executor (15-20s)  ┘
└── result_aggregator (instant)
Total: ~15-20s (4x faster!)
```

You'll see all 4 agents executing in parallel in the timeline.

## Exporting to External Observability Tools

DevUI's traces are standard OpenTelemetry format and can be exported to:

- **Jaeger** - Open-source distributed tracing
- **Zipkin** - Distributed tracing system
- **Azure Monitor** - Azure Application Insights
- **Datadog** - Enterprise monitoring platform

### To Export Traces

Set the `OTLP_ENDPOINT` environment variable before running:

```bash
# For Jaeger (running locally)
export OTLP_ENDPOINT="http://localhost:4317"

# Start Jaeger first
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Run your workflow
python 07_github_sequential_workflow.py

# View traces in Jaeger at http://localhost:16686
```

**Note:** Without an OTLP endpoint, traces are captured locally and displayed only in DevUI's web interface (which is perfect for development!).

## How to Use DevUI Traces

### 1. Run a Workflow

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/agents-with-github-models
python 07_github_sequential_workflow.py
```

### 2. Open DevUI

Browser automatically opens to `http://localhost:8082`

### 3. View Traces

- **Right Panel**: "Traces" tab shows execution timeline
- **Click any trace**: See detailed information
- **Watch in real-time**: Traces appear as agents execute

### 4. Analyze Performance

- Compare execution times between runs
- Identify slow agents
- Optimize workflow structure

## Troubleshooting

### No traces visible in DevUI?

**Check 1:** Are you using examples 07 or 08?
- Only workflow examples (07/08) show traces
- Simple examples (05/06) have limited trace info

**Check 2:** Refresh the browser
- Press Cmd/Ctrl + R to refresh
- Click the "Traces" tab in right panel

**Check 3:** Run the workflow
- Traces only appear after executing with input
- Enter a topic/description and submit

### Traces show "Unknown Operation"?

This is normal for some operations and doesn't affect functionality. The important traces (agent executions) will have proper names.

## Performance Tips

### Sequential (Example 07)
- Each agent waits for the previous one
- Total time = sum of all agent times
- Good for dependent tasks

### Parallel (Example 08)
- All agents run simultaneously
- Total time ≈ slowest agent time
- 3-4x faster for independent tasks

## Next Steps

1. **Try Both Examples**: Run 07 and 08 to compare sequential vs parallel
2. **Watch the Traces**: Observe the execution timeline in DevUI
3. **Analyze Performance**: See the speed difference between patterns
4. **Build Your Own**: Use these patterns for your workflows
- Ensure proper permissions on the resource

### OTLP receiver not receiving traces?

- Verify receiver is running: `docker ps` or check process
- Check endpoint URL is correct (including port)
- Ensure no firewall blocking port 4317
- Look for connection errors in console output

## Example: Full Console Tracing Session

```bash
# 1. Enable console tracing
export ENABLE_CONSOLE_TRACING=true

# 2. Run sequential workflow
python 07_github_sequential_workflow.py

# You'll see output like:
# 📊 Tracing Mode: Console Output
#    Traces will be printed to the console
#
# 🔄 Sequential Workflow with Visual Representation - DevUI
# ================================================================================
# 
# [Trace] span_id=abc123 operation=input_dispatcher duration=0.5ms
# [Trace] span_id=def456 operation=research_agent duration=18234ms
# [Trace] span_id=ghi789 operation=analysis_agent duration=15123ms
# [Trace] span_id=jkl012 operation=writer_agent duration=19876ms
# [Trace] span_id=mno345 operation=output_formatter duration=1.2ms
```

## Best Practices

### Development
- Use **console tracing** for quick feedback
- Great for debugging individual workflows
- Easy to enable/disable

### Staging/Testing
- Use **OTLP with Jaeger/Zipkin** for detailed analysis
- Compare performance across runs
- Identify optimization opportunities

### Production
- Use **Application Insights** for enterprise monitoring
- Set up alerts on high latency or errors
- Aggregate metrics across multiple deployments
- Enable for critical workflows only (performance overhead)

## Next Steps

1. **Start Simple**: Try console tracing first with example 07
2. **Compare Patterns**: Run both 07 and 08 to see sequential vs parallel
3. **Go Deeper**: Set up Jaeger locally to visualize traces
4. **Scale Up**: Use Application Insights for production workloads

## Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Azure Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Jaeger Quickstart](https://www.jaegertracing.io/docs/latest/getting-started/)
- [Microsoft Agent Framework Observability](https://github.com/microsoft/maf)

## Questions?

Refer to the main [README.md](README.md) for additional examples and documentation.

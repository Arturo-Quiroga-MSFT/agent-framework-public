# DevUI Tracing Guide - View Traces in the Web Interface

This guide shows you how to **view OpenTelemetry traces directly in the DevUI web interface** as you interact with your agents.

## 🎯 Overview

DevUI has built-in trace visualization that lets you see:
- **Real-time traces** as you interact with agents
- **Agent invocations** with timing and status
- **Tool executions** with inputs and outputs
- **LLM requests** with token usage
- **Nested operations** in a hierarchical view

All without leaving the DevUI web interface! 🎉

---

## 🚀 Quick Start

### Method 1: Using Python Code (Recommended)

```bash
# 1. Enable DevUI tracing in .env
cd /Users/arturoquiroga/GITHUB/agent-framework-public/python/samples/getting_started/agents/azure_ai
echo "ENABLE_DEVUI_TRACING=true" >> .env
echo "ENABLE_OTEL=true" >> .env
echo "ENABLE_SENSITIVE_DATA=true" >> .env

# 2. Run the agent
python azure_ai_basic_devui.py

# 3. Interact with the agent in the web UI
# Traces will appear in real-time in the DevUI interface!
```

### Method 2: Using CLI (Directory-based)

```bash
# 1. Navigate to the devui_agents directory
cd devui_agents

# 2. Launch DevUI with tracing enabled
devui . --port 8090 --tracing

# 3. Open http://localhost:8090 in your browser
# Traces will appear as you interact with agents!
```

---

## 📋 Configuration

### Option 1: Environment Variables (Python Code)

Edit `.env` file:
```bash
# Enable DevUI tracing
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
```

Then run:
```python
python azure_ai_basic_devui.py
```

### Option 2: CLI Flag (Directory Discovery)

```bash
# Enable tracing when launching DevUI
devui ./agents --tracing

# Tracing is automatically configured
```

---

## 🎨 What You'll See in DevUI

When tracing is enabled, the DevUI web interface shows:

### 1. Trace Timeline View
```
┌─────────────────────────────────────────────┐
│ 🔍 Traces (Real-time)                       │
├─────────────────────────────────────────────┤
│ ▼ invoke_agent WeatherAgent                │
│   │ Duration: 2.3s                          │
│   │ Status: ✅ Success                      │
│   │                                         │
│   ├─ chat gpt-4                            │
│   │  │ Tokens: 45 input, 123 output        │
│   │  │ Duration: 1.8s                      │
│   │                                         │
│   └─ execute_tool get_weather              │
│      │ Input: {"location": "Seattle"}      │
│      │ Output: "Weather in Seattle: 72°F"  │
│      │ Duration: 0.3s                      │
└─────────────────────────────────────────────┘
```

### 2. Span Details Panel
Click on any trace span to see:
- **Operation name** (e.g., "invoke_agent", "chat", "execute_tool")
- **Attributes** (model, tokens, agent name, etc.)
- **Start/end time**
- **Duration**
- **Status** (success/error)
- **Parent/child relationships**

### 3. Real-time Updates
- Traces appear as operations complete
- **Streaming responses** show progressive traces
- **Error traces** highlighted in red
- **Performance metrics** for each operation

---

## 🔧 Configuration Details

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `ENABLE_DEVUI_TRACING` | Enable DevUI trace visualization | `false` |
| `ENABLE_OTEL` | Enable OpenTelemetry instrumentation | `false` |
| `ENABLE_SENSITIVE_DATA` | Include prompts/responses in traces | `false` |

### Python Code Configuration

```python
from agent_framework.devui import serve

# Enable tracing when launching DevUI
serve(
    entities=[agent],
    port=8090,
    auto_open=True,
    tracing_enabled=True  # 👈 Enable trace visualization
)
```

### CLI Configuration

```bash
# Long form
devui ./agents --tracing

# Short form (if available)
devui ./agents -t
```

---

## 📊 Understanding Trace Data

### Span Types

#### 1. Agent Invocation Spans
```json
{
  "name": "invoke_agent WeatherAgent",
  "attributes": {
    "gen_ai.operation.name": "invoke_agent",
    "gen_ai.system": "azure_ai",
    "gen_ai.agent.name": "WeatherAgent",
    "gen_ai.agent.id": "uuid-here"
  },
  "duration": 2300  // milliseconds
}
```

#### 2. Chat Completion Spans
```json
{
  "name": "chat gpt-4",
  "attributes": {
    "gen_ai.operation.name": "chat",
    "gen_ai.system": "azure_openai",
    "gen_ai.request.model": "gpt-4",
    "gen_ai.usage.input_tokens": 45,
    "gen_ai.usage.output_tokens": 123
  },
  "duration": 1800
}
```

#### 3. Tool Execution Spans
```json
{
  "name": "execute_tool get_weather",
  "attributes": {
    "gen_ai.operation.name": "execute_tool",
    "gen_ai.tool.name": "get_weather",
    "gen_ai.tool.parameters": "{\"location\": \"Seattle\"}",
    "gen_ai.tool.result": "Weather in Seattle: 72°F"
  },
  "duration": 300
}
```

---

## 🎯 Use Cases

### 1. Debugging Agent Behavior
**Problem:** Agent not using the tool as expected  
**Solution:** Check traces to see:
- Was the tool called?
- What parameters were passed?
- What was the response?

### 2. Performance Optimization
**Problem:** Agent is slow  
**Solution:** Check traces to identify:
- Which operation takes longest?
- How many LLM calls were made?
- Token usage per request

### 3. Error Investigation
**Problem:** Agent fails intermittently  
**Solution:** Check traces to find:
- Which operation failed?
- Error message and stack trace
- State before failure

### 4. Token Usage Tracking
**Problem:** Need to monitor costs  
**Solution:** Check traces for:
- Input/output tokens per request
- Total tokens for conversation
- Model used for each call

---

## 🔍 Viewing Traces in DevUI

### Step-by-Step

1. **Launch DevUI with tracing:**
   ```bash
   python azure_ai_basic_devui.py
   # or
   devui devui_agents --port 8090 --tracing
   ```

2. **Open the web interface:**
   - Navigate to http://localhost:8090
   - You'll see your agent in the entity list

3. **Interact with the agent:**
   - Type a message: "What's the weather in Seattle?"
   - Click "Send" or press Enter

4. **View the traces:**
   - Look for the "Traces" or "Telemetry" panel in the UI
   - Expand spans to see details
   - Click on individual operations for more info

5. **Analyze performance:**
   - Check duration of each operation
   - Review token usage
   - Identify bottlenecks

---

## 🆚 DevUI Tracing vs. Other Tracing Options

| Feature | DevUI Tracing | Console Tracing | Jaeger | App Insights |
|---------|--------------|-----------------|--------|--------------|
| **Real-time view** | ✅ In web UI | ✅ In terminal | ✅ In Jaeger UI | ⚠️ Some delay |
| **Setup complexity** | 🟢 Easy | 🟢 Easiest | 🟡 Moderate | 🟡 Moderate |
| **Persistence** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Visual hierarchy** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Searchable** | ⚠️ Limited | ❌ No | ✅ Yes | ✅ Yes |
| **Production ready** | ❌ No | ❌ No | ⚠️ Maybe | ✅ Yes |
| **Best for** | Development | Quick debug | Local dev | Production |

---

## 🎨 DevUI Trace Visualization Features

### Current Features
- ✅ **Real-time trace display** as operations complete
- ✅ **Hierarchical view** showing parent-child relationships
- ✅ **Span details** with all attributes
- ✅ **Duration metrics** for performance analysis
- ✅ **Error highlighting** for failed operations
- ✅ **Token usage** display for LLM calls
- ✅ **Tool execution** details with inputs/outputs

### Future Enhancements (Potential)
- 🔮 Trace search and filtering
- 🔮 Persistent trace storage
- 🔮 Trace export functionality
- 🔮 Performance charts and graphs
- 🔮 Trace comparison across runs

---

## 🐛 Troubleshooting

### Traces Not Appearing in DevUI

**Check 1: Is tracing enabled?**
```bash
# For Python code
cat .env | grep ENABLE_DEVUI_TRACING

# For CLI
# Make sure you used --tracing flag
```

**Check 2: Are OpenTelemetry packages installed?**
```bash
pip list | grep opentelemetry
```

**Check 3: Check browser console**
- Open DevTools (F12)
- Look for errors in console
- Check Network tab for trace events

**Check 4: Verify agent is instrumented**
```python
# Agent should be created through agent framework
# Not custom implementations
agent = ChatAgent(...)  # ✅ Good
```

### Traces Show But Are Empty

**Issue:** Traces appear but have no details

**Solution 1:** Enable sensitive data
```bash
ENABLE_SENSITIVE_DATA=true
```

**Solution 2:** Check agent framework version
```bash
pip show agent-framework
# Should be recent version with observability support
```

### DevUI UI Not Showing Trace Panel

**Issue:** No trace panel visible in UI

**Solution:** Check DevUI version
```bash
pip show agent-framework-devui
# Update if needed:
pip install --upgrade agent-framework-devui
```

---

## 💻 Code Examples

### Example 1: Enable DevUI Tracing Programmatically

```python
import os
from agent_framework.devui import serve
from agent_framework import ChatAgent

# Set environment variables programmatically
os.environ["ENABLE_OTEL"] = "true"
os.environ["ENABLE_SENSITIVE_DATA"] = "true"

# Create your agent
agent = ChatAgent(...)

# Launch with tracing enabled
serve(
    entities=[agent],
    port=8090,
    tracing_enabled=True  # 👈 Key parameter
)
```

### Example 2: Conditional Tracing

```python
import os

# Check if we're in development mode
is_dev = os.environ.get("ENVIRONMENT") == "development"

serve(
    entities=[agent],
    port=8090,
    tracing_enabled=is_dev  # Only trace in development
)
```

### Example 3: CLI with Environment Variables

```bash
# Set up environment
export ENABLE_OTEL=true
export ENABLE_SENSITIVE_DATA=true

# Launch DevUI
devui ./agents --tracing --port 8090
```

---

## 📚 Related Documentation

- **Main Tracing Guide**: See `TRACING_GUIDE.md` for other tracing options
- **Quick Start**: See `TRACING_QUICKSTART.md` for fastest setup
- **DevUI README**: See DevUI package documentation
- **Agent Framework Observability**: Check samples in `../../../observability/`

---

## 🎯 Best Practices

1. **Enable for Development**: Always use DevUI tracing during development
2. **Disable for Production**: DevUI is not production-ready
3. **Enable Sensitive Data**: For detailed debugging (development only)
4. **Combine with Console**: Use both DevUI and console tracing together
5. **Regular Monitoring**: Check traces regularly to understand agent behavior

---

## 🎉 Summary

DevUI tracing gives you **real-time visibility** into your agent's operations right in the web interface:

```bash
# Quick start
echo "ENABLE_DEVUI_TRACING=true" >> .env
python azure_ai_basic_devui.py

# Or with CLI
devui devui_agents --tracing
```

**Benefits:**
- 🎨 Visual trace hierarchy
- ⚡ Real-time updates
- 🔍 Detailed span information
- 📊 Performance metrics
- 🐛 Easy debugging

**Perfect for:**
- Local development
- Debugging agent logic
- Understanding tool execution
- Performance analysis
- Learning agent behavior

**Not for:**
- Production deployments
- Long-term trace storage
- Advanced trace analytics

---

**Ready to try it?** Run `python azure_ai_basic_devui.py` with `ENABLE_DEVUI_TRACING=true` and see your traces come to life! 🚀

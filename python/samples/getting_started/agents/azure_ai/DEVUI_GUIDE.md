# Using DevUI with Azure AI Agents

This guide shows you how to visualize and debug the `azure_ai_basic.py` agent using DevUI.

## 🎯 What is DevUI?

DevUI is a lightweight web-based interface for running and debugging agents and workflows in the Microsoft Agent Framework. It provides:

- 🔍 **Visual debugging** - See agent execution in real-time
- 📊 **Trace visualization** - View OpenTelemetry traces
- 🧪 **Interactive testing** - Test agents through a web UI
- 🔧 **API access** - OpenAI-compatible REST API

## 📋 Prerequisites

1. **Install DevUI:**
   ```bash
   pip install agent-framework-devui --pre
   ```

2. **Ensure Azure credentials:**
   ```bash
   az login
   ```

3. **Environment variables configured** (already done in `.env` file)

## 🚀 Three Ways to Use DevUI

### **Method 1: Directory-Based Discovery** (Recommended)

DevUI can automatically discover agents in a specific directory structure.

1. **Directory structure created:**
   ```
   devui_agents/
   └── weather_agent/
       ├── __init__.py      # Exports: agent = ChatAgent(...)
       └── agent.py         # Agent implementation
   ```

2. **Launch DevUI:**
   ```bash
   # From the azure_ai directory
   cd /Users/arturoquiroga/GITHUB/agent-framework-public/python/samples/getting_started/agents/azure_ai
   
   # Launch DevUI with directory discovery
   devui devui_agents --port 8090
   ```

3. **Access the UI:**
   - Web UI: http://localhost:8090
   - API: http://localhost:8090/v1/*
   - Entity ID: `agent_WeatherAgent`

### **Method 2: Standalone Script** (Quick Start)

Use the standalone script that launches DevUI programmatically.

1. **Run the DevUI-enabled version:**
   ```bash
   python azure_ai_basic_devui.py
   ```

2. **Or test it first:**
   ```bash
   python azure_ai_basic_devui.py --test
   ```

3. **Browser opens automatically** to http://localhost:8090

### **Method 3: Run Individual Agent** (Development)

Run a single agent directly:

```bash
cd devui_agents/weather_agent
python agent.py
```

## 🎮 Using the DevUI Interface

### **1. Web UI Features:**

- **Chat Interface**: Interact with your agent conversationally
- **Entity Selector**: Choose which agent/workflow to run
- **Message History**: View conversation history
- **Tool Calls**: See when tools are invoked
- **Streaming**: Watch responses generate in real-time

### **2. Test Queries:**

Try these in the DevUI chat:
```
- What's the weather like in Seattle?
- Tell me the weather in New York and Los Angeles
- Is it sunny in Miami?
- Compare weather in Paris and London
```

### **3. API Access:**

Use the OpenAI-compatible API:

```bash
curl -X POST http://localhost:8090/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agent-framework",
    "input": "What is the weather in Seattle?",
    "extra_body": {"entity_id": "agent_WeatherAgent"}
  }'
```

## 📊 Viewing Traces in DevUI

DevUI has **built-in trace visualization** that shows traces directly in the web interface!

### **Quick Start:**

```bash
# Method 1: Using Python script
echo "ENABLE_DEVUI_TRACING=true" >> .env
python azure_ai_basic_devui.py

# Method 2: Using CLI
devui devui_agents --port 8090 --tracing
```

### **What You'll See:**

When tracing is enabled, the DevUI web interface displays:
- 🔍 **Real-time traces** as operations complete
- 📊 **Agent invocations** with timing and status
- 🛠️ **Tool executions** with inputs and outputs
- 💬 **LLM requests** with token usage and model info
- ⏱️ **Performance metrics** for each operation
- 🔗 **Hierarchical view** showing parent-child relationships

### **Enable DevUI Tracing:**

**Option 1: Environment Variables** (for Python script)
```bash
# Add to .env file
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
```

**Option 2: CLI Flag** (for directory discovery)
```bash
devui devui_agents --port 8090 --tracing
```

### **Trace Information Displayed:**

```
🔍 Agent Invocation
  ├─ Operation: invoke_agent WeatherAgent
  ├─ Duration: 2.3s
  ├─ Status: ✅ Success
  │
  ├─ 💬 Chat Completion
  │  ├─ Model: gpt-4
  │  ├─ Input tokens: 45
  │  ├─ Output tokens: 123
  │  └─ Duration: 1.8s
  │
  └─ 🛠️ Tool Execution
     ├─ Tool: get_weather
     ├─ Input: {"location": "Seattle"}
     ├─ Output: "Weather in Seattle: 72°F"
     └─ Duration: 0.3s
```

### **Benefits:**
- ✅ No external tools needed (all in DevUI)
- ✅ Real-time updates as you interact
- ✅ Visual hierarchy of operations
- ✅ Performance analysis at a glance
- ✅ Error highlighting for failed operations

📖 **For detailed DevUI tracing documentation, see [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md)**

## 🔧 DevUI CLI Options

```bash
devui [directory] [options]

Options:
  --port, -p      Port (default: 8080)
  --host          Host (default: 127.0.0.1)
  --headless      API only, no UI
  --tracing       none|framework|workflow|all
  --reload        Enable auto-reload for development
```

## 📁 Files Created

1. **`devui_agents/weather_agent/`** - Directory structure for discovery
   - `__init__.py` - Exports the agent
   - `agent.py` - Agent implementation

2. **`azure_ai_basic_devui.py`** - Standalone script with DevUI integration

## 🎯 Key Differences from Original

### Original `azure_ai_basic.py`:
- ✅ Demonstrates basic usage patterns
- ✅ Shows streaming and non-streaming
- ✅ Runs examples and exits
- ❌ No interactive debugging
- ❌ No visualization

### DevUI Version:
- ✅ **Persistent agent** that stays running
- ✅ **Interactive web interface**
- ✅ **Visual debugging** and tracing
- ✅ **API access** for integration
- ✅ **Real-time testing** without code changes

## 🐛 Debugging Tips

### **View Agent Details:**
```bash
curl http://localhost:8090/v1/entities
curl http://localhost:8090/v1/entities/agent_WeatherAgent/info
```

### **Check Health:**
```bash
curl http://localhost:8090/health
```

### **Enable Verbose Logging:**
```bash
devui devui_agents --port 8090 --tracing all
```

## 🔄 Development Workflow

1. **Make changes** to `agent.py`
2. **Restart DevUI** (or use `--reload` flag)
3. **Test in browser** immediately
4. **View traces** to debug issues
5. **Iterate quickly** without rewriting test code

## 💡 Best Practices

1. **Use directory structure** for multiple agents
2. **Enable tracing** during development
3. **Test with DevUI** before production deployment
4. **Use API mode** (`--headless`) for CI/CD
5. **Keep agents stateless** for better DevUI experience

## 📚 Learn More

- [Agent Framework Documentation](https://github.com/microsoft/agent-framework)
- [DevUI Package](https://pypi.org/project/agent-framework-devui/)
- [OpenTelemetry Tracing](https://opentelemetry.io/)

---

**Ready to explore?** Run `python azure_ai_basic_devui.py` and start debugging! 🚀

# 🎯 DevUI Tracing - 2 Minute Setup

Want to see traces **directly in the DevUI web interface**? Here's how in 2 minutes! ⚡

---

## Method 1: Using Python Script (Easiest)

### Step 1: Enable DevUI Tracing
```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/python/samples/getting_started/agents/azure_ai

# Add these lines to .env
cat >> .env << 'EOF'

# DevUI Tracing
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true
EOF
```

### Step 2: Run the Agent
```bash
python azure_ai_basic_devui.py
```

### Step 3: View Traces
1. Browser opens automatically to http://localhost:8090
2. Type a message: "What's the weather in Seattle?"
3. **Look for the Traces/Telemetry section in the UI** 👀
4. See real-time traces as the agent responds!

**Output you'll see:**
```
📊 Tracing Mode: Console Output
🔍 DevUI Tracing: Enabled
   → Traces will appear in DevUI web interface
🚀 Launching Azure AI Weather Agent in DevUI
✅ Web UI: http://localhost:8090
```

---

## Method 2: Using CLI (Directory-Based)

### Step 1: Navigate to Directory
```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/python/samples/getting_started/agents/azure_ai/devui_agents
```

### Step 2: Launch with Tracing
```bash
devui . --port 8090 --tracing
```

### Step 3: View Traces
1. Open http://localhost:8090 in browser
2. Select the WeatherAgent
3. Type a message
4. **Watch traces appear in real-time** 🎉

---

## 🎨 What You'll See in DevUI

### Trace View Example:
```
┌────────────────────────────────────────────┐
│ 🔍 Traces                                  │
├────────────────────────────────────────────┤
│                                            │
│ ▼ invoke_agent WeatherAgent               │
│   ├─ Duration: 2.3s                       │
│   ├─ Status: ✅ Success                   │
│   │                                        │
│   ├─ 💬 chat gpt-4                        │
│   │  ├─ Input tokens: 45                  │
│   │  ├─ Output tokens: 123                │
│   │  └─ Duration: 1.8s                    │
│   │                                        │
│   └─ 🛠️ execute_tool get_weather         │
│      ├─ Input: {"location": "Seattle"}    │
│      ├─ Result: "Weather: 72°F, sunny"    │
│      └─ Duration: 0.3s                    │
│                                            │
└────────────────────────────────────────────┘
```

### Features:
- ✅ **Real-time updates** as operations complete
- ✅ **Expandable spans** to see details
- ✅ **Color coding** for status (green=success, red=error)
- ✅ **Duration metrics** for performance analysis
- ✅ **Token usage** for each LLM call
- ✅ **Tool parameters** and results

---

## 🎯 Quick Test

### Test Command:
```bash
# All in one command!
cd /Users/arturoquiroga/GITHUB/agent-framework-public/python/samples/getting_started/agents/azure_ai && \
echo "ENABLE_DEVUI_TRACING=true" >> .env && \
echo "ENABLE_OTEL=true" >> .env && \
echo "ENABLE_SENSITIVE_DATA=true" >> .env && \
python azure_ai_basic_devui.py
```

### Test Queries in DevUI:
```
What's the weather in Seattle?
Tell me about weather in Tokyo and Paris
Is it sunny in Miami?
```

**Watch the traces appear in real-time!** 🚀

---

## 📊 Trace Information You'll See

| Field | Description | Example |
|-------|-------------|---------|
| **Operation Name** | What's happening | `invoke_agent WeatherAgent` |
| **Duration** | How long it took | `2.3s` |
| **Status** | Success or error | `✅ Success` |
| **Model** | LLM model used | `gpt-4` |
| **Input Tokens** | Prompt size | `45` |
| **Output Tokens** | Response size | `123` |
| **Tool Name** | Function called | `get_weather` |
| **Parameters** | Tool inputs | `{"location": "Seattle"}` |
| **Result** | Tool output | `"Weather: 72°F"` |

---

## 🐛 Troubleshooting

### Traces not appearing?

**Problem:** DevUI opens but no traces visible

**Solution 1:** Check environment variables
```bash
cat .env | grep -E "DEVUI_TRACING|OTEL"
# Should show:
# ENABLE_DEVUI_TRACING=true
# ENABLE_OTEL=true
```

**Solution 2:** Restart DevUI completely
```bash
# Kill existing process (Ctrl+C)
# Re-run
python azure_ai_basic_devui.py
```

**Solution 3:** Check browser console
- Press F12 in browser
- Look for errors in Console tab
- Check Network tab for trace events

### Traces show but are empty?

**Problem:** Trace spans appear but no details

**Solution:** Enable sensitive data
```bash
echo "ENABLE_SENSITIVE_DATA=true" >> .env
```

---

## 🎓 Learn More

- **Full DevUI Tracing Guide**: [`DEVUI_TRACING_GUIDE.md`](./DEVUI_TRACING_GUIDE.md)
- **All Tracing Options**: [`TRACING_SUMMARY.md`](./TRACING_SUMMARY.md)
- **Quick Reference**: [`TRACING_QUICKSTART.md`](./TRACING_QUICKSTART.md)

---

## ✅ Summary

**To enable DevUI tracing:**
```bash
# 1. Add to .env
ENABLE_DEVUI_TRACING=true
ENABLE_OTEL=true
ENABLE_SENSITIVE_DATA=true

# 2. Run
python azure_ai_basic_devui.py

# 3. Use the agent in the web UI and watch traces appear!
```

**That's it!** 🎉

Now you can see exactly what your agent is doing in real-time with beautiful visual traces! 🚀

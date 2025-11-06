# 🚀 LLMOps Quick Start Guide

## What You Got

✨ **Enhanced Production Agent** - Production-ready agent with:
- Progress callbacks for real-time updates
- Structured responses (`AgentResponse` dataclass)
- Session management & chat history
- Agent presets (Market Analyst, Research Assistant, Technical Advisor)
- Export functionality (JSON)
- Comprehensive error handling

✨ **Streamlit Web UI** - Professional interface with:
- Chat interface with inline metrics
- Real-time analytics dashboard
- Cost & budget tracking with charts
- Quality evaluation visualizations
- Session export button
- Agent preset selector

---

## 🏃 Quick Start

### 1️⃣ Test CLI (30 seconds)

```bash
cd AQ-CODE/llmops
python production_agent_enhanced.py
```

### 2️⃣ Launch UI (2 minutes)

```bash
# Install UI dependencies
pip install -r requirements-ui.txt

# Launch
streamlit run streamlit_production_ui.py
```

Opens at: `http://localhost:8501`

### 3️⃣ Interactive Script

```bash
./quickstart.sh
```

---

## 📁 Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `production_agent_enhanced.py` | 500+ | Enhanced agent with UI support |
| `streamlit_production_ui.py` | 600+ | Web interface |
| `UI_README.md` | 250+ | Complete documentation |
| `ENHANCEMENTS_SUMMARY.md` | 400+ | Detailed comparison |
| `requirements-ui.txt` | 10 | Dependencies |
| `quickstart.sh` | 80 | Interactive launcher |

---

## 🎯 Key Features

### Enhanced Agent
- ✅ Progress callback system
- ✅ Structured `AgentResponse` objects
- ✅ Agent presets (easy configuration)
- ✅ Chat history management
- ✅ Session export (JSON)
- ✅ Budget checking
- ✅ Quality evaluation

### Streamlit UI
- ✅ 3-tab interface (Chat, Analytics, History)
- ✅ Real-time cost tracking
- ✅ Interactive charts (Plotly)
- ✅ Quality score gauges
- ✅ Budget warnings
- ✅ Session download button
- ✅ Agent switching

---

## 💻 Usage Examples

### Basic Usage

```python
from production_agent_enhanced import ProductionAgent

# Create from preset
agent = ProductionAgent.from_preset("market_analyst")

# Run query
response = await agent.run(
    query="What is NVIDIA's P/E ratio?",
    expected_topics=["P/E ratio", "NVIDIA"]
)

# Use response
if response.success:
    print(response.response)
    print(f"Cost: ${response.metrics['tokens']['estimated_cost_usd']:.4f}")
    print(f"Quality: {response.metrics['quality_label']}")
```

### 🆕 Agent Lifecycle Management (Recommended)

**Prevent creating duplicate agents in Azure AI Foundry!**

```python
from production_agent_with_lifecycle import ProductionAgent

# First instance creates agent in Foundry
agent1 = ProductionAgent(
    agent_name="market_analyst",
    instructions="You are a market analyst...",
    enable_web_search=True,
    reuse_agent=True  # Enable agent reuse (default)
)
result1 = await agent1.run("What's NVIDIA's P/E ratio?")
print(f"Agent reused: {result1.agent_reused}")  # False (newly created)

# Second instance REUSES same agent (not created again!)
agent2 = ProductionAgent(
    agent_name="market_analyst",
    instructions="You are a market analyst...",
    enable_web_search=True,
    reuse_agent=True
)
result2 = await agent2.run("What about Microsoft?")
print(f"Agent reused: {result2.agent_reused}")  # True (reused!)

# Monitor usage
from agent_lifecycle_manager import ProductionAgentManager
stats = ProductionAgentManager.get_agent_stats()
print(f"Total agents: {stats['total_agents']}")  # Only 1!
```

### Application-Level Management

```python
from agent_lifecycle_manager import ProductionAgentManager

# Application startup: Pre-warm agents
async def startup():
    await ProductionAgentManager.get_or_create_agent(
        "market_analyst",
        instructions="You are a market analyst...",
        enable_web_search=True
    )
    print("✅ Agents pre-warmed")

# Application shutdown: Cleanup
async def shutdown():
    await ProductionAgentManager.cleanup_all()
    print("✅ All agents cleaned up")

# In your app
await startup()
# ... use agents ...
await shutdown()
```

**Benefits:**
- 🎯 One agent per configuration (not one per instance)
- 💰 Reduced costs from duplicate agent elimination
- 📊 Usage tracking across sessions
- 🧹 Centralized cleanup

---

## 🎭 Agent Presets

**📈 Market Analyst**
- Stock valuations & market data
- Web search: ✅ Enabled

**🔬 Research Assistant**
- Information with citations
- Web search: ✅ Enabled

**💻 Technical Advisor**
- Software development guidance
- Web search: ❌ Disabled

---

## 📊 What's Tracked

- 💰 **Cost** - Real-time USD tracking
- 🎫 **Tokens** - Prompt + completion
- 📊 **Budget** - % of limit used
- ⭐ **Quality** - 0.0 - 1.0 score
- ⏱️ **Duration** - Response time
- 💬 **History** - Full conversation log

---

## 🔧 Customization

### Add Custom Preset

Edit `production_agent_enhanced.py`:

```python
class AgentPreset:
    MY_AGENT = {
        "name": "my_agent",
        "instructions": "Your instructions...",
        "enable_web_search": True,
        "expected_topics": ["topic1", "topic2"]
    }
```

### Change Budget

Edit `.env`:

```bash
TOKEN_BUDGET_LIMIT=2000000
```

---

## 📚 Documentation

- **UI_README.md** - Complete setup & usage guide
- **ENHANCEMENTS_SUMMARY.md** - Detailed comparison with original
- **Code comments** - Inline documentation

---

## ✅ Next Steps

1. ✓ Run CLI demo: `python production_agent_enhanced.py`
2. ✓ Launch UI: `streamlit run streamlit_production_ui.py`
3. ✓ Try different presets
4. ✓ Monitor costs in analytics
5. ✓ Export a session
6. ✓ Add custom presets

**You're ready to build your Streamlit UI!** 🚀

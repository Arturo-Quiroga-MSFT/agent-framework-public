# LLMOps Production Agent UI

A production-ready Streamlit interface for Microsoft Agent Framework with comprehensive LLMOps capabilities.

## 🚀 Features

### Enhanced Agent Implementation (`production_agent_enhanced.py`)

- **Progress Callbacks**: Real-time status updates for UI integration
- **Structured Responses**: `AgentResponse` dataclass with complete metadata
- **Session Management**: Built-in chat history and session tracking
- **Agent Presets**: Pre-configured agents (Market Analyst, Research Assistant, Technical Advisor)
- **Export Functionality**: JSON export of complete session data
- **Error Handling**: User-friendly error messages and recovery

### Streamlit UI (`streamlit_production_ui.py`)

#### 💬 Chat Interface
- Real-time conversation with AI agents
- Message history with metadata
- Per-message metrics display
- Quality evaluation for each response

#### 📊 Analytics Dashboard
- **Token & Cost Tracking**: Real-time cost monitoring
- **Budget Management**: Visual budget usage indicators
- **Quality Trends**: Track response quality over time
- **Cost Breakdown**: Visualize token usage per query

#### 🎭 Agent Management
- Switch between agent presets
- Configure web search capabilities
- Session controls (clear, export)
- Environment information display

## 📋 Setup

### 1. Install Dependencies

```bash
pip install -r requirements-ui.txt
```

### 2. Configure Environment

Create or update `.env` file:

```bash
# Required
AZURE_AI_PROJECT_ENDPOINT=your-endpoint-here
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1

# Optional - Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string

# Optional - Budget Management
TOKEN_BUDGET_LIMIT=1000000  # Default: 1M tokens
```

### 3. Run the Enhanced Agent (CLI)

```bash
python production_agent_enhanced.py
```

**What it demonstrates:**
- Progress callback system
- Structured response handling
- Session management
- Chat history
- Export functionality

### 4. Run the Streamlit UI

```bash
streamlit run streamlit_production_ui.py
```

**Access at:** `http://localhost:8501`

## 🎭 Agent Presets

### 📈 Market Analyst
- **Purpose**: Technology stock valuations and market analysis
- **Web Search**: ✅ Enabled
- **Best For**: Financial queries, market research, P/E ratios

### 🔬 Research Assistant
- **Purpose**: Accurate information with citations
- **Web Search**: ✅ Enabled
- **Best For**: General research, fact-finding, detailed analysis

### 💻 Technical Advisor
- **Purpose**: Software development guidance
- **Web Search**: ❌ Disabled
- **Best For**: Code examples, best practices, architecture advice

## 💡 Usage Examples

### Example 1: Market Analysis

```python
from production_agent_enhanced import ProductionAgent

# Create agent from preset
agent = ProductionAgent.from_preset("market_analyst")

# Run query
response = await agent.run(
    query="What is NVIDIA's current P/E ratio?",
    expected_topics=["P/E ratio", "NVIDIA", "valuation"]
)

# Check response
if response.success:
    print(response.response)
    print(f"Quality: {response.metrics['quality_label']}")
    print(f"Cost: ${response.metrics['tokens']['estimated_cost_usd']:.4f}")
```

### Example 2: Custom Agent with Progress Tracking

```python
from production_agent_enhanced import ProductionAgent, ProgressUpdate

# Define progress callback
def on_progress(update: ProgressUpdate):
    print(f"[{update.status.value}] {update.message}")

# Create custom agent
agent = ProductionAgent(
    agent_name="custom_agent",
    instructions="You are a helpful assistant...",
    enable_web_search=True,
    progress_callback=on_progress
)

# Run with progress updates
response = await agent.run("Your query here")
```

### Example 3: Session Export

```python
# After running multiple queries...
session_data = agent.export_session_data()

# Save to file
import json
with open("session_export.json", "w") as f:
    json.dump(session_data, f, indent=2)

# Session data includes:
# - Full chat history
# - Cost statistics
# - Token usage
# - Configuration details
```

## 📊 UI Components

### Chat Tab
- **Message Display**: Full conversation history
- **Inline Metrics**: Duration, tokens, cost per message
- **Quality Cards**: Evaluation metrics for each response
- **Real-time Dashboard**: Cumulative statistics

### Analytics Tab
- **Metrics Overview**: Cost, tokens, budget, message count
- **Cost Breakdown Chart**: Token usage visualization
- **Budget Status**: Progress bar with warnings
- **Quality Trends**: Line chart of quality metrics

### History Tab
- **Conversation Log**: Complete message history with timestamps
- **Progress Log**: System events and status updates
- **Export Button**: Download session as JSON

## 🔧 Customization

### Add Custom Agent Preset

Edit `production_agent_enhanced.py`:

```python
class AgentPreset:
    # Add new preset
    MY_CUSTOM_AGENT = {
        "name": "my_agent",
        "instructions": "Your custom instructions...",
        "enable_web_search": True,
        "expected_topics": ["topic1", "topic2"]
    }
    
    @classmethod
    def get_preset(cls, preset_name: str):
        presets = {
            # ... existing presets
            "my_agent": cls.MY_CUSTOM_AGENT,
        }
        return presets.get(preset_name, cls.RESEARCH_ASSISTANT)
```

### Customize Evaluation Metrics

Edit `evaluator.py` to add custom quality checks:

```python
def evaluate_response(self, response: str, expected_topics: list) -> dict:
    # Add custom metrics
    has_code_examples = bool(re.search(r'```', response))
    
    return {
        # ... existing metrics
        "has_code_examples": has_code_examples
    }
```

## 📈 Key Enhancements vs Original

| Feature | Original | Enhanced |
|---------|----------|----------|
| Response Format | Print only | Structured `AgentResponse` |
| Progress Updates | Print to console | Callback system for UI |
| Session Management | None | Built-in history & export |
| Agent Configuration | Hardcoded | Preset system |
| Error Handling | Basic exceptions | User-friendly messages |
| Metrics Display | Console output | Interactive dashboard |
| Cost Tracking | Basic logging | Real-time visualization |
| Quality Evaluation | Console summary | Interactive cards & trends |

## 🚀 Deployment

### Option 1: Local Streamlit

```bash
streamlit run streamlit_production_ui.py --server.port 8501
```

### Option 2: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-ui.txt .
RUN pip install -r requirements-ui.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_production_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t llmops-agent-ui .
docker run -p 8501:8501 --env-file .env llmops-agent-ui
```

### Option 3: Azure Container Apps

Use the existing `deploy-to-azure.sh` script with modifications for this UI.

## 🐛 Troubleshooting

### Issue: Agent not initializing
- **Solution**: Check Azure credentials: `az login`
- Verify `AZURE_AI_PROJECT_ENDPOINT` in `.env`

### Issue: Budget warnings
- **Solution**: Increase `TOKEN_BUDGET_LIMIT` in `.env`
- Or clear session to reset token counter

### Issue: Slow responses
- **Solution**: Check Azure region latency
- Consider using faster model deployment

### Issue: Progress updates not showing
- **Solution**: Ensure `progress_callback` is passed to agent
- Check Streamlit session state

## 📚 Architecture

```
┌─────────────────────────────────────┐
│     Streamlit UI Layer              │
│  - Chat interface                   │
│  - Analytics dashboard              │
│  - Session management               │
└────────────┬────────────────────────┘
             │
             │ Callbacks & Async
             ▼
┌─────────────────────────────────────┐
│  ProductionAgent (Enhanced)         │
│  - Progress callbacks               │
│  - Structured responses             │
│  - Session tracking                 │
└────────────┬────────────────────────┘
             │
             │ Orchestrates
             ▼
┌─────────────────────────────────────┐
│     LLMOps Components               │
│  - MAFObservability                 │
│  - CostTracker                      │
│  - TokenBudgetManager               │
│  - AgentEvaluator                   │
└────────────┬────────────────────────┘
             │
             │ Monitors & Evaluates
             ▼
┌─────────────────────────────────────┐
│   Azure AI Agent Framework          │
│  - AzureAIAgentClient               │
│  - HostedWebSearchTool              │
│  - Agent execution                  │
└─────────────────────────────────────┘
```

## 🎯 Next Steps

1. **Test the Enhanced Agent**: Run `production_agent_enhanced.py`
2. **Launch UI**: Run `streamlit run streamlit_production_ui.py`
3. **Try Different Presets**: Switch between agents in UI
4. **Monitor Costs**: Watch analytics dashboard
5. **Export Session**: Download conversation data
6. **Customize**: Add your own agent presets

## 📝 File Structure

```
llmops/
├── production_agent_enhanced.py    # Enhanced agent with UI support
├── streamlit_production_ui.py      # Streamlit interface
├── requirements-ui.txt             # UI dependencies
├── UI_README.md                    # This file
├── observability.py                # Telemetry & tracing
├── cost_tracker.py                 # Cost & budget tracking
├── evaluator.py                    # Quality evaluation
└── example_production_agent.py     # Original example
```

## 🤝 Contributing

Suggestions for additional features:
- [ ] Multi-agent comparison mode
- [ ] Batch query processing
- [ ] Custom evaluation metrics editor
- [ ] Response caching
- [ ] RAG integration for context
- [ ] A/B testing framework

## 📄 License

Same as Microsoft Agent Framework repository.

---

**Built with ❤️ using Microsoft Agent Framework**

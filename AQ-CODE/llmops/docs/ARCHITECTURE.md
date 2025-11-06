# 🏗️ Architecture Overview

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                       │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │           Streamlit Web UI (streamlit_production_ui.py)     │  │
│  │                                                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │  │
│  │  │   Chat   │  │Analytics │  │ History  │                 │  │
│  │  │   Tab    │  │   Tab    │  │   Tab    │                 │  │
│  │  └──────────┘  └──────────┘  └──────────┘                 │  │
│  │                                                              │  │
│  │  • Message display         • Cost charts                    │  │
│  │  • Input field             • Quality trends                 │  │
│  │  • Metrics cards           • Budget monitor                 │  │
│  │  • Quality evaluation      • Token breakdown                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│                              │ Async calls + Callbacks            │
│                              ▼                                    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     AGENT ORCHESTRATION LAYER                     │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │      ProductionAgent (production_agent_enhanced.py)        │  │
│  │                                                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │  │
│  │  │  Progress   │  │   Session   │  │   Agent     │        │  │
│  │  │  Callbacks  │  │  Management │  │   Presets   │        │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │  │
│  │                                                              │  │
│  │  • ProgressUpdate dataclass                                 │  │
│  │  • AgentResponse dataclass                                  │  │
│  │  • Chat history tracking                                    │  │
│  │  • Session export                                           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│                              │ Orchestrates                       │
│                              ▼                                    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        LLMOPS COMPONENTS                          │
│                                                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ MAFObserv- │  │    Cost    │  │   Token    │  │   Agent    │ │
│  │  ability   │  │  Tracker   │  │   Budget   │  │ Evaluator  │ │
│  │            │  │            │  │  Manager   │  │            │ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │
│                                                                    │
│  • Application Insights traces                                    │
│  • Real-time cost calculation                                     │
│  • Budget enforcement                                             │
│  • Quality metrics evaluation                                     │
│                              │                                    │
│                              │ Monitors & Evaluates               │
│                              ▼                                    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  AZURE AI AGENT FRAMEWORK                         │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               AzureAIAgentClient                            │  │
│  │                                                              │  │
│  │  ┌────────────────┐  ┌────────────────┐                   │  │
│  │  │  ChatAgent     │  │ HostedWebSearch│                   │  │
│  │  │  Execution     │  │     Tool       │                   │  │
│  │  └────────────────┘  └────────────────┘                   │  │
│  │                                                              │  │
│  │  • Agent creation & management                              │  │
│  │  • Tool integration                                         │  │
│  │  • Response generation                                      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│                              │ API Calls                          │
│                              ▼                                    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        AZURE SERVICES                             │
│                                                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │  Azure AI  │  │   Azure    │  │ Application│  │   Bing     │ │
│  │  Foundry   │  │  OpenAI    │  │  Insights  │  │  Search    │ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │
│                                                                    │
│  • Model hosting                                                  │
│  • Inference endpoints                                            │
│  • Telemetry collection                                           │
│  • Web search capabilities                                        │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Query Flow (User → Response)

```
1. USER INPUTS QUERY
   │
   │ Streamlit chat input
   │
   ▼
2. UI CALLS AGENT
   │
   │ asyncio.run(agent.run(query))
   │
   ▼
3. AGENT INITIALIZES
   │
   ├─► Progress: "INITIALIZING" → UI
   ├─► Create Azure client
   └─► Create agent with tools
   │
   ▼
4. BUDGET CHECK
   │
   ├─► Progress: "CHECKING_BUDGET" → UI
   ├─► TokenBudgetManager.check_budget()
   └─► Estimate tokens
   │
   ▼
5. EXECUTE AGENT
   │
   ├─► Progress: "RUNNING" → UI
   ├─► MAFObservability.create_span()
   ├─► Agent.run(query) → Azure AI
   └─► Get response
   │
   ▼
6. TRACK COSTS
   │
   ├─► Calculate tokens
   ├─► CostTracker.record_cost()
   └─► TokenBudgetManager.record_usage()
   │
   ▼
7. EVALUATE QUALITY
   │
   ├─► Progress: "EVALUATING" → UI
   ├─► AgentEvaluator.evaluate_response()
   └─► Calculate quality score
   │
   ▼
8. BUILD RESPONSE
   │
   ├─► Create AgentResponse object
   ├─► Include all metrics
   └─► Progress: "COMPLETED" → UI
   │
   ▼
9. UPDATE UI
   │
   ├─► Display response text
   ├─► Show quality evaluation
   ├─► Update metrics dashboard
   └─► Add to chat history
```

### Progress Update Flow

```
Agent Internal State
       │
       │ Creates ProgressUpdate
       │
       ▼
progress_callback(update)
       │
       │ Stores in session_state
       │
       ▼
UI Re-renders
       │
       ├─► Status badges
       ├─► Progress log
       └─► Real-time metrics
```

### Session Export Flow

```
User Clicks "Export"
       │
       ▼
agent.export_session_data()
       │
       ├─► Gather chat history
       ├─► Collect statistics
       ├─► Include configuration
       │
       ▼
Generate JSON
       │
       ▼
st.download_button()
       │
       ▼
User Downloads File
```

## 🆕 Agent Lifecycle Management Architecture

### Overview
```
┌───────────────────────────────────────────────────────────┐
│              Production Application                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  ProductionAgent Instances (Multiple Sessions)      │  │
│  │  - agent1 (session_1) ──┐                           │  │
│  │  - agent2 (session_2) ──┼─► Same agent config      │  │
│  │  - agent3 (session_3) ──┘                           │  │
│  └─────────────────────────────────────────────────────┘  │
│                       ↓ ↓ ↓                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  ProductionAgentManager (Centralized Registry)      │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │ In-Memory Registry                            │  │  │
│  │  │  {                                            │  │  │
│  │  │    "market_analyst": (agent, cred, client)   │  │  │
│  │  │    "tech_advisor": (agent, cred, client)     │  │  │
│  │  │  }                                            │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │ Metadata & Usage Tracking                     │  │  │
│  │  │  - Creation timestamps                        │  │  │
│  │  │  - Usage counts per agent                     │  │  │
│  │  │  - Session tracking                           │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                       ↓                                    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Azure AI Foundry                                   │  │
│  │  - market_analyst (created ONCE)                    │  │
│  │  - tech_advisor (created ONCE)                      │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

### Key Benefits
- **Before**: N instances → N agents in Foundry (resource proliferation)
- **After**: N instances → 1 agent in Foundry (agent reuse)
- **Result**: ~90% reduction in Foundry resources

### Lifecycle Flow
```
1. First ProductionAgent instantiation
   ├─► Check registry: agent NOT found
   ├─► Create new agent in Foundry
   ├─► Store in registry
   └─► Return agent reference

2. Subsequent ProductionAgent instantiations (same config)
   ├─► Check registry: agent FOUND
   ├─► Update usage metadata
   └─► Return existing agent reference

3. Application shutdown
   ├─► ProductionAgentManager.cleanup_all()
   ├─► Release all Azure resources
   └─► Clear registry
```

---

## Component Responsibilities

### ProductionAgentManager 🆕
- **Registry**: Maintain map of agent_name → (agent, credential, client)
- **Reuse**: Get existing agent or create new one
- **Thread Safety**: Lock-protected concurrent access
- **Tracking**: Usage statistics and session metadata
- **Cleanup**: Release Azure resources on shutdown

### ProductionAgent
- **Initialize**: Azure client, credentials, tools (via manager if reuse enabled)
- **Execute**: Run queries, manage threads
- **Track**: Chat history, session state
- **Callback**: Emit progress updates
- **Export**: Serialize session data
- **Lifecycle**: Use ProductionAgentManager for agent reuse

### LLMOps Components

#### MAFObservability
- Create trace spans
- Track agent calls
- Send to Application Insights
- Duration metrics

#### CostTracker
- Calculate token costs
- Track per-agent costs
- Maintain cumulative total
- Cost by model

#### TokenBudgetManager
- Enforce token limits
- Track usage per request
- Calculate percentages
- Remaining budget

#### AgentEvaluator
- Analyze response quality
- Check topic coverage
- Verify citations
- Structure evaluation

### Streamlit UI
- **Render**: Chat, analytics, history
- **Handle**: User input
- **Display**: Metrics, charts
- **Manage**: Session state
- **Control**: Agent selection

## State Management

### Session State (st.session_state)

```python
{
    "agent": ProductionAgent,          # Current agent instance
    "chat_history": [                  # Message history
        {"role": "user", "content": "...", "timestamp": "..."},
        {"role": "assistant", "content": "...", "metadata": {...}}
    ],
    "progress_updates": [               # Progress events
        ProgressUpdate(...),
        ProgressUpdate(...)
    ],
    "responses": [                      # AgentResponse objects
        AgentResponse(...),
        AgentResponse(...)
    ],
    "selected_preset": "market_analyst", # Current preset
    "agent_initialized": True           # Init status
}
```

### Agent Internal State

```python
class ProductionAgent:
    self.observability: MAFObservability
    self.cost_tracker: CostTracker
    self.budget_manager: TokenBudgetManager
    self.evaluator: AgentEvaluator
    
    self._client: AzureAIAgentClient
    self._agent: ChatAgent
    self._credential: DefaultAzureCredential
    
    self.chat_history: List[Dict]
    self.session_id: str
```

## Extension Points

### 1. Add Custom Agent Preset
```python
# In AgentPreset class
MY_PRESET = {
    "name": "...",
    "instructions": "...",
    "enable_web_search": bool,
    "expected_topics": [...]
}
```

### 2. Custom Progress Callback
```python
def my_callback(update: ProgressUpdate):
    # Custom handling
    log_to_system(update)
    notify_user(update)
```

### 3. Custom Evaluation Metric
```python
# In AgentEvaluator
def evaluate_response(self, response, topics):
    # Add custom check
    my_metric = custom_check(response)
    return {..., "my_metric": my_metric}
```

### 4. Custom UI Tab
```python
# In Streamlit UI
with tab4:
    st.markdown("### My Custom View")
    # Custom visualization
```

## Security Considerations

1. **Authentication**: DefaultAzureCredential (Managed Identity recommended)
2. **API Keys**: Stored in `.env`, never committed
3. **Session Data**: Kept in memory, optional export
4. **Budget Limits**: Enforced before execution
5. **Error Messages**: No sensitive data exposed

## Performance Notes

- **Async Operations**: All Azure calls are async
- **Progress Callbacks**: Non-blocking updates
- **Chart Rendering**: Only on tab switch
- **History Display**: Last N items only
- **Session State**: In-memory only

---

**This architecture provides:**
✅ Clean separation of concerns
✅ Easy extensibility
✅ Production-ready error handling
✅ Comprehensive observability
✅ User-friendly interface

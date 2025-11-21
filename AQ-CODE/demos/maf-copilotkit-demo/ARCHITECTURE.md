# MAF + CopilotKit Demo - Architecture

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     BROWSER (User)                            │
│                   http://localhost:3000                       │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ User interacts
                       │
┌──────────────────────▼───────────────────────────────────────┐
│              Next.js Frontend (React)                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  CopilotKit Components                                 │  │
│  │  - CopilotSidebar (chat interface)                     │  │
│  │  - Agent selector dropdown                             │  │
│  │  - useCopilotAction hooks                              │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Custom UI Components (Generative UI)                  │  │
│  │  - WeatherCard (temp, icon, humidity)                  │  │
│  │  - CodeApprovalDialog (HITL)                           │  │
│  │  - ChartDisplay (matplotlib outputs)                   │  │
│  │  - SearchResultCard (citations)                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ AG-UI Protocol
                       │ (HTTP POST + Server-Sent Events)
                       │
┌──────────────────────▼───────────────────────────────────────┐
│           FastAPI Server (Python Backend)                     │
│                http://localhost:8000                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  AG-UI Integration (agent-framework-ag-ui)             │  │
│  │  - add_agent_framework_fastapi_endpoint()              │  │
│  │  - Handles SSE streaming                               │  │
│  │  - Manages thread context                              │  │
│  │  - Converts MAF ↔ AG-UI events                        │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Agent Endpoints                                        │  │
│  │  /agents/weather        - OpenWeatherMap API            │  │
│  │  /agents/code           - Code interpreter (HITL)       │  │
│  │  /agents/bing-search    - Bing web search              │  │
│  │  /agents/azure-ai-search - Hotels index                │  │
│  │  /agents/firecrawl      - Web scraping MCP             │  │
│  │  /agents/microsoft-learn - MS docs MCP                 │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ MAF ChatClient
                       │
┌──────────────────────▼───────────────────────────────────────┐
│         Microsoft Agent Framework (MAF)                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  ChatAgent Orchestration                                │  │
│  │  - Instructions (system prompts)                        │  │
│  │  - Tool execution (@ai_function)                        │  │
│  │  - Thread management (conversation memory)             │  │
│  │  - State tracking (shared state)                        │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Tools                                                   │  │
│  │  - Custom functions (get_weather)                       │  │
│  │  - Hosted tools (CodeInterpreter, FileSearch)           │  │
│  │  - Hosted MCP (Firecrawl, MS Learn)                     │  │
│  │  - Web search (Bing grounding)                          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ Chat Completion API
                       │
┌──────────────────────▼───────────────────────────────────────┐
│              Azure OpenAI / OpenAI                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  LLM (gpt-4o, gpt-4o-mini)                              │  │
│  │  - Text generation                                       │  │
│  │  - Function calling                                      │  │
│  │  - Streaming responses                                   │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Example: Weather Query

```
1. User types: "What's the weather in Tokyo?"
   └─> Frontend: CopilotSidebar captures input

2. Frontend → Backend (HTTP POST)
   └─> POST http://localhost:8000/agents/weather
   └─> Body: { "message": "What's the weather in Tokyo?" }

3. Backend: FastAPI receives request
   └─> AG-UI integration extracts message
   └─> Routes to weather_agent

4. MAF: ChatAgent processes
   └─> Sends to Azure OpenAI
   └─> LLM decides to call get_weather("Tokyo")
   └─> Function executes, fetches from OpenWeatherMap API
   └─> Returns: { "temp": 22, "description": "clear", ... }

5. MAF → AG-UI: Converts response
   └─> Streams events via Server-Sent Events (SSE)
   └─> Events: TOOL_CALL_START, TOOL_CALL_RESULT, TEXT_MESSAGE_CONTENT

6. Frontend: Listens to SSE stream
   └─> Receives TOOL_CALL_RESULT for get_weather
   └─> useCopilotAction hook catches it
   └─> Renders WeatherCard component

7. User sees: Beautiful weather card with icon, temp, humidity
   └─> Not just text - custom UI component! ✨
```

---

## 🎭 Component Interactions

### Weather Agent (Simple Flow)
```
User Query
   ↓
CopilotSidebar
   ↓ AG-UI POST
FastAPI Endpoint (/agents/weather)
   ↓
AgentFrameworkAgent (AG-UI wrapper)
   ↓
ChatAgent (MAF)
   ↓ Function call
get_weather() → OpenWeatherMap API
   ↓ JSON response
ChatAgent formats response
   ↓ SSE Stream
Frontend receives TOOL_CALL_RESULT
   ↓
useCopilotAction matches tool name
   ↓
WeatherCard renders
   ↓
User sees custom UI
```

### Code Interpreter (HITL Flow)
```
User Query: "Plot a sine wave"
   ↓
CopilotSidebar
   ↓ AG-UI POST
FastAPI Endpoint (/agents/code)
   ↓
AgentFrameworkAgent (require_confirmation=True)
   ↓
ChatAgent (MAF)
   ↓ Wants to call execute_code()
AgentFrameworkAgent intercepts
   ↓ Sends APPROVAL_REQUEST event (SSE)
Frontend receives event
   ↓
CodeApprovalDialog renders
   ↓
User clicks "Approve"
   ↓ Sends approval (HTTP POST)
AgentFrameworkAgent receives approval
   ↓
ChatAgent executes code
   ↓ Code runs in sandbox
matplotlib generates plot
   ↓ Image bytes returned
ChatAgent streams result
   ↓ SSE with image data
Frontend receives TOOL_CALL_RESULT
   ↓
ChartDisplay renders image
   ↓
User sees plot + download button
```

---

## 🔌 Protocol Details

### AG-UI Events (Backend → Frontend via SSE)

```
TEXT_MESSAGE_CONTENT      # Streaming text chunks
TOOL_CALL_START           # Tool execution begins
TOOL_CALL_RESULT          # Tool execution complete
APPROVAL_REQUEST          # Needs user approval (HITL)
STATE_UPDATE              # Shared state changed
AGENT_STATE_UPDATE        # Agent internal state
CONVERSATION_COMPLETE     # Turn finished
```

### AG-UI Messages (Frontend → Backend via HTTP)

```
POST /agents/{agent_name}
{
  "messages": [...],        # Conversation history
  "thread_id": "...",       # For memory
  "state": {...}            # Shared state
}
```

---

## 📦 Technology Stack

### Frontend
- **Framework:** Next.js 15
- **UI Library:** React 19
- **Agent Integration:** CopilotKit
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **Icons:** Lucide React

### Backend
- **Framework:** FastAPI
- **Agent Framework:** Microsoft Agent Framework (MAF)
- **Protocol:** AG-UI (agent-framework-ag-ui)
- **LLM Client:** Azure OpenAI / OpenAI
- **Web Server:** Uvicorn
- **Authentication:** Azure DefaultAzureCredential

### External Services
- **LLM:** Azure OpenAI (gpt-4o)
- **Weather:** OpenWeatherMap API
- **Code Execution:** Azure AI Code Interpreter
- **Web Search:** Bing Grounding
- **Search Index:** Azure AI Search
- **Web Scraping:** Firecrawl MCP
- **Documentation:** Microsoft Learn MCP

---

## 🔐 Security Layers

```
┌────────────────────────────────────────┐
│  Frontend (Public)                     │
│  - Client-side validation              │
│  - HTTPS in production                 │
└──────────┬─────────────────────────────┘
           │
           │ CORS protection
           │
┌──────────▼─────────────────────────────┐
│  FastAPI Backend                       │
│  - API authentication (can add JWT)   │
│  - Rate limiting (can add)             │
│  - Input validation                    │
└──────────┬─────────────────────────────┘
           │
           │ Azure DefaultAzureCredential
           │
┌──────────▼─────────────────────────────┐
│  Azure Services                        │
│  - Role-based access (RBAC)            │
│  - Private endpoints (can enable)      │
│  - Audit logging                       │
└────────────────────────────────────────┘
```

---

## 🚀 Deployment Architecture

### Development (Current)
```
Laptop
├── Backend:  http://localhost:8000
└── Frontend: http://localhost:3000
```

### Production (Example)
```
Azure
├── Backend:  Azure Container Apps
│   └── Image: maf-copilotkit-backend:latest
│   └── Env: .env secrets
│   └── Scale: 0-10 instances
│
└── Frontend: Azure Static Web Apps
    └── Build: Next.js static export
    └── CDN: Azure CDN
    └── Domain: agents.teradata.com
```

---

## 📊 Scalability

### Backend Scaling
- **Horizontal:** Add more FastAPI instances
- **Load balancer:** Azure Load Balancer
- **Session:** Redis for shared state
- **Limits:** 100+ concurrent users per instance

### Frontend Scaling
- **CDN:** Static files cached globally
- **SSE connections:** Persistent to backend
- **Bundle size:** ~200KB initial load
- **Performance:** < 2s first contentful paint

---

**This architecture separates concerns, enables scaling, and uses open standards! 🎯**

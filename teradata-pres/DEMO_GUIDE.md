# CopilotKit + MAF Demo Guide

## 🎯 Demo Purpose
This project demonstrates how **Microsoft Agent Framework (MAF)** integrates with **CopilotKit** to build production-ready agent UIs using the **AG-UI protocol**.

## ✨ Features Demonstrated

### 1. **Agentic Chat with Streaming**
- Real-time conversation with streaming responses
- Built-in typing indicators and animations

### 2. **Shared State (Bidirectional Sync)**
- **Proverbs List**: Agent can read/write, UI can display
- State syncs automatically between frontend and backend
- Demo: "Add a proverb about AI" → Updates both sides

### 3. **Generative UI (Custom Components)**
- **Weather Card**: Agent calls `get_weather()` → Renders custom React component
- **Moon Card**: Agent calls `go_to_moon()` → Renders approval dialog
- Demo: "Get the weather in San Francisco" → Beautiful weather card appears

### 4. **Human-in-the-Loop (HITL)**
- **Moon Mission**: Requires explicit user approval before proceeding
- Agent requests, UI shows approval dialog, user clicks approve/deny
- Demo: "Please go to the moon" → Approval dialog with rocket emoji

### 5. **Frontend Actions**
- **Theme Changer**: `setThemeColor()` runs in browser (not backend)
- Instant UI updates without backend roundtrip
- Demo: "Set the theme to green" → Page color changes immediately

### 6. **Backend Tool Rendering**
- Tools execute on server, results stream to client
- `update_proverbs()` runs in Python, UI updates in React
- Demo: "Remove a random proverb" → Server logic, client update

## 🏃 Running the Demo

### Prerequisites
1. **Edit** `agent/.env` with your Azure OpenAI or OpenAI credentials
2. Install dependencies (one-time):
   ```bash
   cd teradata-pres
   npm install  # or pnpm/yarn/bun
   ```

### Start Development Servers
```bash
npm run dev
```

This starts:
- **Frontend**: http://localhost:3000 (Next.js)
- **Backend**: http://localhost:8000 (FastAPI + MAF agent)

## 🎬 Demo Script for Presentations

### **Scene 1: Setup & Introduction** (2 minutes)
```bash
# Show the architecture
cat README.md

# Show the agent code
cat agent/src/agent.py
```

**Talking Points:**
- "This is a complete MAF agent with 3 tools"
- "Backend is pure Python, frontend is React"
- "AG-UI protocol connects them"

---

### **Scene 2: Start the Demo** (1 minute)
```bash
npm run dev
# Wait for both servers to start
```

**Talking Points:**
- "Two commands: install and dev"
- "Backend runs on 8000, frontend on 3000"
- "Everything is ready to go"

---

### **Scene 3: Live Interactions** (5-7 minutes)

#### **3.1: Basic Chat**
Type in UI: *"Hi, what can you do?"*

**Show:**
- Streaming response
- Agent explains capabilities

---

#### **3.2: Shared State (Write)**
Type: *"Add a proverb about data platforms"*

**Show:**
- Agent calls `update_proverbs()` tool
- Proverb card updates on the left
- State persists across messages

**Talking Points:**
- "State syncs bidirectionally"
- "Agent wrote to state, UI reflected it"

---

#### **3.3: Shared State (Read)**
Type: *"What are my proverbs?"*

**Show:**
- Agent reads current state
- Lists all proverbs from shared context

---

#### **3.4: Generative UI**
Type: *"Get the weather in San Francisco"*

**Show:**
- Agent calls `get_weather()` tool
- **Custom weather card appears inline in chat**
- Not just text—actual React component

**Talking Points:**
- "Agent can render custom UI components"
- "WeatherCard is defined in frontend, triggered by backend"
- "This is Generative UI—AI creates interface elements"

---

#### **3.5: Human-in-the-Loop**
Type: *"Please go to the moon"*

**Show:**
- Agent calls `go_to_moon()` tool
- **Approval dialog appears with rocket icon**
- Click "Approve" → Agent proceeds
- Click "Deny" → Agent cancels

**Talking Points:**
- "Critical actions require approval"
- "Tool has `approval_mode='always_require'`"
- "Perfect for financial transactions, data deletion, etc."

---

#### **3.6: Frontend Actions**
Type: *"Set the theme to green"*

**Show:**
- Page background changes to green **instantly**
- No backend roundtrip
- `setThemeColor()` runs in browser

**Talking Points:**
- "Some actions should run client-side"
- "Frontend tools for instant UI updates"

---

#### **3.7: State Removal**
Type: *"Remove a random proverb"*

**Show:**
- Agent removes one proverb
- Updates state with remaining ones
- Card reflects changes

---

### **Scene 4: Code Deep Dive** (3-5 minutes)

#### **Backend Agent** (`agent/src/agent.py`)
```python
# Show the 3 tools
@ai_function(name="update_proverbs", ...)
def update_proverbs(proverbs: list[str]) -> str:
    return f"Proverbs updated. Tracking {len(proverbs)} item(s)."

@ai_function(name="get_weather", ...)
def get_weather(location: str) -> str:
    return "Weather in {location} is mild..."

@ai_function(
    name="go_to_moon",
    approval_mode="always_require",  # ← HITL
)
def go_to_moon() -> str:
    return "Mission control requested..."
```

**Talking Points:**
- "Standard MAF `@ai_function` decorators"
- "Approval mode on moon function"
- "State schema defines shared state structure"

---

#### **Frontend Integration** (`src/app/page.tsx`)
```tsx
// Shared State
const { state, setState } = useCoAgent<AgentState>({
  name: "my_agent",
  initialState: { proverbs: [...] },
})

// Generative UI for weather
useCopilotAction({
  name: "get_weather",
  available: "disabled",  // Backend-only
  render: ({ args }) => (
    <WeatherCard location={args.location} />
  ),
})

// HITL for moon
useCopilotAction({
  name: "go_to_moon",
  available: "disabled",
  renderAndWaitForResponse: ({ respond, status }) => (
    <MoonCard status={status} respond={respond} />
  ),
})

// Frontend Action for theme
useCopilotAction({
  name: "setThemeColor",
  handler({ themeColor }) {
    setThemeColor(themeColor);  // ← Runs in browser
  },
})
```

**Talking Points:**
- "`useCoAgent` for shared state"
- "`available: disabled` means backend-only"
- "`renderAndWaitForResponse` for HITL"
- "Frontend handler for instant actions"

---

#### **FastAPI Server** (`agent/src/main.py`)
```python
# 10 lines to expose MAF agent via AG-UI
app = FastAPI()
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=my_agent,
    path="/",
)
```

**Talking Points:**
- "Single function call to expose agent"
- "AG-UI protocol handles all the complexity"
- "CORS, SSE streaming, thread management—all built-in"

---

## 🎓 Key Takeaways for Teradata

1. **Developer Velocity**
   - From idea to working demo: < 10 minutes
   - `npx copilotkit@latest init` → Complete stack

2. **Production-Ready Out of the Box**
   - CORS, streaming, error handling
   - Type-safe state management
   - Observability hooks

3. **Best of Both Worlds**
   - MAF: Enterprise-grade agent orchestration
   - CopilotKit: Consumer-grade UX
   - AG-UI: Open protocol (not vendor lock-in)

4. **Extensible Architecture**
   - Add new tools → Automatically available in UI
   - Custom UI components → Just React
   - Works with any LLM (Azure OpenAI, OpenAI, etc.)

5. **Real-World Use Cases**
   - Customer support with approval workflows
   - Data analysis with custom visualizations
   - Internal tools with state persistence
   - Multi-agent systems with progress tracking

## 📊 Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│  Browser (React + CopilotKit)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ CopilotSidebar│  │ WeatherCard  │  │ ProverbsCard │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         └──────────────────┴──────────────────┘         │
└────────────────────┬───────────────────────────────────┘
                     │ AG-UI Protocol
                     │ (HTTP POST + Server-Sent Events)
┌────────────────────▼───────────────────────────────────┐
│  FastAPI Server (Python)                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ add_agent_framework_fastapi_endpoint            │   │
│  │  - Handles SSE streaming                        │   │
│  │  - Manages thread context                       │   │
│  │  - Converts MAF events ↔ AG-UI events          │   │
│  └──────────────────┬──────────────────────────────┘   │
└────────────────────┬───────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────┐
│  Microsoft Agent Framework (MAF)                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ChatAgent                                       │   │
│  │  - Instructions (system prompt)                 │   │
│  │  - Tools: update_proverbs, get_weather,        │   │
│  │           go_to_moon                            │   │
│  │  - State schema for shared context             │   │
│  └──────────────────┬──────────────────────────────┘   │
└────────────────────┬───────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────┐
│  Azure OpenAI / OpenAI                                 │
│  - GPT-4o-mini (or any model)                          │
│  - Function calling for tool execution                 │
└────────────────────────────────────────────────────────┘
```

## 🔗 Resources

- **MAF Docs**: https://learn.microsoft.com/en-us/agent-framework/
- **AG-UI Protocol**: https://docs.ag-ui.com/introduction
- **CopilotKit Docs**: https://docs.copilotkit.ai
- **MAF + CopilotKit**: https://docs.copilotkit.ai/microsoft-agent-framework
- **AG-UI Dojo** (live examples): https://dojo.ag-ui.com/microsoft-agent-framework-dotnet

## 🎤 Presentation Tips

1. **Start with a question**: "How long do you think it takes to build this?" 
2. **Reveal**: "10 minutes and 1 command"
3. **Show the code**: "This is standard MAF—nothing special"
4. **Run the demo**: Let them see the magic
5. **Close with**: "Now imagine your Teradata agents with this UX"

---

**Ready to blow minds! 🚀**

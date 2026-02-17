# AG-UI Pattern Demos

Four Python demos showing how agentic UIs go beyond streaming text tokens to streaming **structured state changes**.

## The Core Idea

Traditional chat UIs stream text. But when agents control dashboards, plans, or workflows, you need to stream **state**. These demos show the AG-UI approach: server pushes JSON Patch deltas instead of full state, giving real-time UI updates with ~80% less bandwidth than polling.

---

## 1. Predictive State Updates (`agui-predictive-state`)

**No Azure credentials needed.** Best demo to run first.

```bash
cd AQ-CODE/agui-predictive-state && python predictive_state_agent.py
```

**What it does:** Simulates a 5-task deployment workflow (Build Docker → Security Scan → Push → Deploy → Integration Tests). Each task streams state transitions via JSON Patch:

```
PENDING → ANALYZING → IN_PROGRESS (25%→50%→75%→100%) → COMPLETED
```

**What to notice:**
- Progress bars fill in real-time (streaming, not polling)
- 47 small patches (~80 bytes each) vs 47 full-state polls (~1288 bytes each)
- Ends with a side-by-side comparison: traditional polling = 10KB, predictive = 2KB

**Key concept:** A `StateUpdate` contains JSON Patch operations (RFC 6902):
```python
StateUpdate(operations=[
    {"op": "replace", "path": "/tasks/2/status", "value": "in_progress"},
    {"op": "replace", "path": "/tasks/2/progress", "value": 75}
])
```
The client applies each patch to its local state copy and re-renders. Any frontend (React, Streamlit, terminal) can consume the same patches.

---

## 2. Agentic UI — Planning Agent (`agui-agentic-ui`)

**Requires Azure OpenAI.** Uses `AQ-CODE/.env` automatically.

```bash
cd AQ-CODE/agui-agentic-ui && python planning_agent.py
```

**What it does:** An LLM agent generates structured `Plan` objects (not just text) with actionable steps, then simulates execution with streaming status updates.

**What to notice:**
- Agent calls `create_plan` tool → returns a typed `Plan` with `Step` objects
- Agent calls `update_step_status` tool → sends JSON Patch to update individual steps
- The UI is data-driven: the agent controls structured state, not raw text

**Key concept:** The agent's tools produce structured data that drives the UI:
```python
@tool
async def create_plan_tool(self, title, description, steps) -> str:
    # Creates Plan object with typed Steps — not free-form text
```

**Test without Azure:** `python test_models.py` validates data models and rendering.

---

## 3. Backend Tool Rendering (`agui-backend-tools`)

**Requires Azure OpenAI.** Uses `AQ-CODE/.env` automatically.

```bash
cd AQ-CODE/agui-backend-tools && python backend_tools_agent.py
```

**What it does:** Agent executes tools server-side where credentials (API keys, DB passwords) never leave the server. Three example tools: weather API, database query, notifications.

**What to notice:**
- Client sends natural language → Agent picks tools → Tools run on server with secure credentials → Structured response returned
- API keys and connection strings are never exposed to the client
- Multi-tool orchestration: "Get weather for Seattle and notify admin if it's raining"

**Key concept:** Backend vs frontend tool execution:
| | Frontend Tools | Backend Tools |
|---|---|---|
| Credentials | Exposed to client | Secure on server |
| Business logic | Visible in browser | Hidden |
| Audit trail | Limited | Full server logs |

**Test without Azure:** `python test_backend_tools.py` demos the architecture in demo mode.

---

## 4. AG-UI Client/Server Protocol (`agui-clientserver`)

**Requires Azure AI Foundry project.** Uses its own `.env`.

```bash
# Terminal 1: Start server
cd AQ-CODE/agui-clientserver && python agui_server.py

# Terminal 2: Run client
cd AQ-CODE/agui-clientserver && python agui_client.py
```

**What it does:** Full AG-UI protocol implementation — FastAPI server hosts a MAF agent, console client communicates via HTTP POST + Server-Sent Events (SSE).

**What to notice:**
- Server streams SSE events: `thread.run.created` → `thread.message.delta` (token-by-token) → `thread.run.completed`
- Thread IDs persist across turns for multi-turn conversations
- Health endpoint at `/health`, API docs at `/docs`

**Key concept:** The AG-UI transport layer:
```
Client → HTTP POST (messages) → Server
Client ← SSE stream (events)  ← Server ← MAF Agent ← Azure AI
```

---

## Configuration

All demos except `agui-clientserver` load environment variables from `AQ-CODE/.env`. The clientserver has its own `.env` with the Foundry project endpoint.

Key variables:
- `AZURE_OPENAI_ENDPOINT` — Used by demos #2 and #3
- `AZURE_OPENAI_DEPLOYMENT_NAME` — Model name (default: `gpt-4.1`)
- `AZURE_AI_PROJECT_ENDPOINT` — Used by demo #4 (Foundry)

Authentication: All demos use `DefaultAzureCredential` — run `az login` first.

## How They Fit Together

```
┌─────────────────┐   ┌──────────────────┐   ┌─────────────────────┐
│  #1 Predictive  │   │  #2 Agentic UI   │   │  #3 Backend Tools   │
│  State Updates  │   │  (Planning)      │   │  (Secure Execution) │
│  ─────────────  │   │  ─────────────   │   │  ─────────────────  │
│  JSON Patch     │   │  Structured      │   │  Server-side creds  │
│  streaming      │   │  Plan objects    │   │  + type-safe tools  │
└────────┬────────┘   └────────┬─────────┘   └──────────┬──────────┘
         │                     │                        │
         └─────────────────────┼────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │  #4 Client/Server   │
                    │  (AG-UI Protocol)   │
                    │  ────────────────   │
                    │  HTTP + SSE         │
                    │  transport layer    │
                    └─────────────────────┘
```

Demos #1-#3 show *what* to stream (state patches, plans, tool results). Demo #4 shows *how* to transport it (AG-UI protocol over SSE).

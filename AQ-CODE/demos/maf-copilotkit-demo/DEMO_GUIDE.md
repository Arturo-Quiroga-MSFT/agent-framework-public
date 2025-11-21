# Demo Guide: MAF + CopilotKit for Teradata

## 🎯 Presentation Positioning

**Key Message**: "Enterprise agent backends meet consumer-grade UX"

This demo showcases how **Microsoft Agent Framework** + **CopilotKit** delivers:
- Production-ready agent experiences
- Beautiful, interactive UIs without reinventing the wheel
- Open standards (AG-UI, MCP) = no vendor lock-in
- From idea to working demo in minutes

---

## 📊 Demo Flow (15-20 minutes)

### Part 1: Introduction (2 min)

**What You're Showing:**
"This is the evolution of our Streamlit demo - same powerful MAF agents, but with a modern, production-ready UI using CopilotKit and the AG-UI protocol."

**Screen:**
- Show side-by-side: Streamlit (old) vs CopilotKit (new)
- Highlight the architecture diagram

**Talk Track:**
- "Previously: Streamlit for quick demos"
- "Now: Production-ready web app with rich UI"
- "Same agents, better experience"

---

### Part 2: Architecture Overview (3 min)

**What You're Showing:**
Architecture diagram in README.md

**Key Points:**
1. **Backend**: Python/FastAPI with MAF agents
   - Multiple agents exposed via AG-UI protocol
   - Each agent is an HTTP endpoint

2. **Protocol**: AG-UI (open standard)
   - Not vendor-specific
   - Works with any agent framework
   - HTTP + Server-Sent Events for streaming

3. **Frontend**: Next.js + CopilotKit
   - Pre-built React components
   - Generative UI capabilities
   - Human-in-the-loop dialogs

**Talk Track:**
"Three layers: MAF for orchestration, AG-UI for communication, CopilotKit for UI. This separation means you can swap any layer independently."

---

### Part 3: Live Demo - Weather Agent (2 min)

**What You're Showing:**
Generative UI with custom weather cards

**Steps:**
1. Open app at `http://localhost:3000`
2. Select "Weather Agent" from dropdown
3. Type: *"What's the weather in Tokyo?"*

**What Happens:**
- Agent streams response
- Custom weather card appears with:
  - Weather icon
  - Temperature (actual and feels-like)
  - Humidity percentage
  - Wind speed
  - Beautiful styling

**Key Point:**
"This isn't just text - the agent is generating a custom UI component with structured data. This is **Generative UI** in action."

---

### Part 4: Live Demo - Code Interpreter with HITL (4 min)

**What You're Showing:**
Human-in-the-Loop approval workflow

**Steps:**
1. Switch to "Code Interpreter" agent
2. Type: *"Create a 3D surface plot of z = sin(x) * cos(y) for x and y from -5 to 5"*

**What Happens:**
- Agent writes Python code
- **Approval dialog appears** with code preview
- Show the code to audience
- Click "Approve"
- Code executes on backend
- Beautiful 3D plot appears inline in chat
- Download button available

**Key Points:**
1. "For critical operations, we want human approval"
2. "This is **Human-in-the-Loop** (HITL) - built into the protocol"
3. "Code runs on secure backend, results stream to UI"
4. "Perfect for financial transactions, data deletion, etc."

**Follow-up Question:**
Type: *"Now create a polar plot of r = sin(5θ) to make a flower pattern"*
- Show that conversation context is maintained
- New approval dialog appears
- Beautiful flower pattern renders

---

### Part 5: Live Demo - Bing Search (3 min)

**What You're Showing:**
Web grounding with conversation memory

**Steps:**
1. Switch to "Bing Search" agent
2. Type: *"What are the latest developments in AI agents?"*

**What Happens:**
- Agent searches Bing
- Returns current information with citations
- Shows [1], [2], [3] reference markers
- Source URLs displayed at bottom

**Follow-up:**
Type: *"Tell me more about the first one"*
- Agent remembers previous search
- Provides details about the first result
- Demonstrates **conversation memory**

**Key Point:**
"The agent maintains context across the conversation. Notice I didn't repeat the question - it knew what 'first one' meant."

---

### Part 6: Live Demo - Azure AI Search (2 min)

**What You're Showing:**
Structured search results from indexed data

**Steps:**
1. Switch to "Azure AI Search" agent
2. Type: *"Search for luxury hotels with good ratings"*

**What Happens:**
- Agent queries hotels-sample-index
- Returns structured hotel information
- Clean, organized presentation

**Key Point:**
"This is Azure AI Search integration - searching pre-indexed data. Same agent interface, different data source."

---

### Part 7: Code Deep Dive (4 min)

**What You're Showing:**
How easy it is to build this

#### Backend Agent (show `weather_agent.py`):
```python
@ai_function(name="get_weather", ...)
def get_weather(location: str) -> str:
    # Call OpenWeatherMap API
    return structured_json_response

def create_weather_agent(chat_client):
    return AgentFrameworkAgent(
        agent=ChatAgent(...),
        require_confirmation=False,
    )
```

**Talk Track:**
"Standard MAF `@ai_function` decorator. Nothing special here."

#### FastAPI Integration (show `main.py`):
```python
weather_agent = create_weather_agent(chat_client)
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=weather_agent,
    path="/agents/weather",
)
```

**Talk Track:**
"One function call to expose agent via AG-UI. That's it."

#### Frontend Integration (show conceptual React):
```tsx
useCopilotAction({
  name: "get_weather",
  available: "disabled",  // Backend-only
  render: ({ args }) => (
    <WeatherCard data={args} />
  ),
})
```

**Talk Track:**
"Frontend listens for tool calls. When agent calls `get_weather`, we render our custom card. That's Generative UI."

---

### Part 8: Key Differentiators (2 min)

**Show Comparison Table from README:**

| Feature | Streamlit | CopilotKit |
|---------|-----------|------------|
| Generative UI | ✗ | ✓ |
| HITL | ✗ | ✓ |
| Production-Ready | Demo-grade | Production-grade |
| Protocol | Streamlit-specific | AG-UI (open) |

**Talk Track:**
1. "Streamlit is great for prototypes"
2. "CopilotKit is built for production"
3. "AG-UI is an open standard - not locked to CopilotKit"
4. "You could swap CopilotKit for any AG-UI client"

---

## 🎤 Presentation Tips

### Opening Hook
"How long do you think it took to build what you're about to see?"
- Let them guess
- Reveal: "The agents were already written. Adding the UI took 20 minutes."

### During Demo
- **Pause for reactions** after Generative UI appears
- **Ask audience**: "Notice anything different about this weather display?"
- **Highlight speed**: "Look how fast that code approval dialog appeared"

### Technical Details
When showing code:
- "This is standard Python - nothing proprietary"
- "MAF handles the orchestration"
- "AG-UI handles the communication"
- "CopilotKit handles the UI"
- "Each layer is replaceable"

### Closing Points
1. **Developer Experience**: "From agent to UI in minutes, not weeks"
2. **Open Standards**: "AG-UI works with 10+ agent frameworks"
3. **Production Ready**: "This isn't a demo - it's deployable today"
4. **Teradata Context**: "Imagine your data agents with this UX"

---

## 🚨 Troubleshooting During Demo

### If Weather API Fails
**Fallback**: "The weather API might be rate-limited. Let me show you the code interpreter instead - that's even more impressive."

### If Code Execution is Slow
**Talk Track**: "Code is running in a secure sandbox on Azure. This is production security, not demo magic."

### If Bing Search Returns No Results
**Fallback**: "Let me try a different query" or switch to Azure AI Search demo.

---

## 🎯 Teradata-Specific Talking Points

### For Data Platform Teams
"Imagine your SQL agents with approval workflows - users could review queries before execution, see results in custom charts, all with this UI."

### For Analytics Teams
"Your data visualizations could be generated dynamically by agents - not static dashboards, but AI-driven insights."

### For Business Users
"This is the kind of UX your users expect. They don't want to write code or learn complex tools - they want natural language and beautiful results."

---

## 📋 Pre-Demo Checklist

- [ ] Backend running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:3000`
- [ ] `.env` file configured with valid API keys
- [ ] Test each agent beforehand
- [ ] Browser zoom set to 100% (or 125% for visibility)
- [ ] Close unnecessary tabs/windows
- [ ] Have fallback demos ready
- [ ] Code files bookmarked for quick access
- [ ] README.md open for architecture diagram

---

## 🎬 Post-Demo Q&A Prep

### Expected Questions

**Q: "How hard is it to deploy to production?"**
A: "Standard containerized deployment. Backend is a FastAPI app, frontend is Next.js - both have established deployment patterns on Azure, AWS, or any cloud."

**Q: "What about authentication/security?"**
A: "MAF integrates with Azure AD/Entra ID. You can add auth middleware to the FastAPI app and Next.js supports all major auth providers."

**Q: "Can we customize the UI further?"**
A: "Absolutely. CopilotKit is React - you have full control. The weather card you saw? That's just a React component. Style it however you want."

**Q: "Does this work with our existing agents?"**
A: "If they're MAF agents, yes - just add the AG-UI wrapper. If they're other frameworks, AG-UI has adapters for LangChain, Semantic Kernel, and others."

**Q: "What's the performance impact?"**
A: "Minimal. AG-UI uses Server-Sent Events for streaming - very efficient. The UI is client-side React, so it's fast. Backend processing time is the same as any agent."

**Q: "Can we use this internally without internet?"**
A: "Yes. You can self-host everything - the backend, the frontend, and use Azure OpenAI in your own network."

---

**Good luck with your demo! 🚀**

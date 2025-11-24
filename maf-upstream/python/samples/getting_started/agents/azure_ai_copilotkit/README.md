# Azure AI Weather Agent - CopilotKit Demo

Production-ready Azure AI agent with CopilotKit UI. This demonstrates the **same weather agent** from DevUI, now running in a production-ready web interface using the AG-UI protocol.

## 🎯 Purpose

Show the complete journey from development (DevUI) to production (AG-UI + CopilotKit):
- **DevUI version**: `/maf-upstream/python/samples/getting_started/agents/azure_ai_devui/basic_weather_agent/`
- **CopilotKit version**: This directory

Both use the **exact same Azure AI agent** with real OpenWeatherMap API.

## ✨ What This Demonstrates

### Architecture
```
┌──────────────────┐         ┌──────────────────┐
│   React/Next.js  │         │   FastAPI Server │
│                  │         │                  │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │ CopilotKit │  │  HTTP/  │  │  AG-UI     │  │
│  │ Components │←─┼─ SSE ──→│  │  Endpoint  │  │
│  └────────────┘  │         │  └────────────┘  │
│                  │         │        ↕          │
│  Custom UI       │         │  ┌────────────┐  │
│  (Tailwind CSS)  │         │  │ Azure AI   │  │
└──────────────────┘         │  │ Agent      │  │
     Frontend                │  └────────────┘  │
  (Port 3200)                └──────────────────┘
                                  Backend
                               (Port 8200)
```

### Features Showcased
- ✅ **AG-UI Protocol** - Open standard for agent-to-UI communication
- ✅ **Production UI** - Custom branded interface with React/Next.js
- ✅ **Same Agent** - Identical weather agent from DevUI demo
- ✅ **Real Tools** - OpenWeatherMap API integration
- ✅ **Streaming** - Server-Sent Events (SSE) for real-time responses
- ✅ **Embeddable** - Can be integrated into existing web applications

## 📋 Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **Azure CLI** (run `az login` before starting)
- **Azure AI Project** with GPT-4 deployment
- **OpenWeatherMap API Key** (free tier works fine)

## 🚀 Quick Start

### Option A: One-command startup (recommended for testing)

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/maf-upstream/python/samples/getting_started/agents/azure_ai_copilotkit
./start.sh
# When finished
./stop.sh
```

`start.sh` automatically stops any previous processes, starts backend + frontend in the background, and streams logs to `logs/backend.log` and `logs/frontend.log`. Use `restart.sh` to cycle both quickly.

### Option B: Manual steps

### 1. Install Dependencies

**Backend (Python):**
```bash
cd agent
pip install -e .
# Or with uv:
uv sync
```

**Frontend (Node.js):**
```bash
cd ui
npm install
# Or with pnpm:
pnpm install
```

### 2. Configure Environment

Backend `.env` is already configured with:
```bash
# agent/.env
AZURE_AI_PROJECT_ENDPOINT="https://aq-ai-foundry-sweden-central.services.ai.azure.com/api/projects/firstProject"
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"
OPENWEATHER_API_KEY="e672c48b8c4e39c289d2de26c5e7b6ae"
AGENT_HOST="0.0.0.0"
AGENT_PORT="8200"
```

### 3. Start the Backend

```bash
cd agent
python src/main.py
```

You should see:
```
🚀 Starting Azure AI Weather Agent on http://0.0.0.0:8200
📡 AG-UI endpoint available at http://0.0.0.0:8200/
📖 API docs at http://0.0.0.0:8200/docs
```

### 4. Start the Frontend

In a new terminal:
```bash
cd ui
npm run dev
# Or: pnpm dev
```

You should see:
```
▲ Next.js 15.1.3
- Local: http://localhost:3200
```

### 5. Open Your Browser

Navigate to: **http://localhost:3200**

The CopilotKit sidebar will be open on the right. Try these queries:
- "What's the weather in Toronto?"
- "How's the weather in Mexico City?"
- "Compare weather in Guadalajara and Monterrey"

## 🎭 Demo Flow for Presentation

### Part 1: Show DevUI (5 min)
```bash
cd ../azure_ai_devui
devui . --port 8195
```
- Open http://localhost:8195
- Show 6 agents in dropdown
- Demonstrate weather agent
- Show tracing in UI
- "This is how we **develop and test**"

### Part 2: Show CopilotKit (5 min)
- Keep this running (backend + frontend)
- Open http://localhost:3200
- Show custom branded UI
- Try same weather queries
- Explain it's the **same agent**, different UI
- "This is how **customers would use it**"

### Part 3: Explain Differences (2 min)
Refer to the comparison table in `azure_ai_devui/README.md`:
- **DevUI**: Development tool, Python-only, built-in tracing
- **AG-UI + CopilotKit**: Production framework, React UI, custom branding

## 🛠️ Technology Stack

### Backend
- **Agent Framework** - Microsoft's agent development framework
- **FastAPI** - Modern Python web framework
- **Azure AI** - GPT-4 model deployment
- **AG-UI Protocol** - Open standard for agent communication
- **OpenWeatherMap** - Real weather data API

### Frontend
- **Next.js 15** - React framework for production
- **React 19** - Latest React with server components
- **CopilotKit** - Agent UI components and integration
- **Tailwind CSS** - Utility-first CSS framework
- **TypeScript** - Type-safe JavaScript

## 📁 Project Structure

```
azure_ai_copilotkit/
├── agent/                    # Backend (Python)
│   ├── src/
│   │   ├── main.py          # FastAPI app with AG-UI endpoint
│   │   └── weather_agent.py # Azure AI weather agent
│   ├── pyproject.toml       # Python dependencies
│   ├── .env                 # Configuration (pre-configured)
│   └── .gitignore
│
├── ui/                       # Frontend (Next.js)
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx     # Main page with CopilotKit
│   │       ├── layout.tsx   # App layout
│   │       └── globals.css  # Tailwind styles
│   ├── package.json         # Node dependencies
│   ├── next.config.js       # Next.js configuration
│   ├── tsconfig.json        # TypeScript configuration
│   └── tailwind.config.js   # Tailwind configuration
│
└── README.md                # This file
```

## 🔧 How It Works

### 1. Agent Creation (Same as DevUI)
```python
# weather_agent.py
from agent_framework.azure import AzureAIClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
azure_agent = AzureAIClient(credential=credential).create_agent(
    name="WeatherAgent",
    description="Get real-time weather information for any city",
    instructions="Use the get_weather function...",
    tools=get_weather,  # OpenWeatherMap API function
)
```

### 2. AG-UI Protocol Wrapper
```python
# main.py
from agent_framework_ag_ui import AgentFrameworkAgent, add_agent_framework_fastapi_endpoint

# Wrap agent for AG-UI protocol
ag_ui_agent = AgentFrameworkAgent(
    agent=azure_agent,
    name="AzureAIWeatherAgent",
    description="Azure AI-powered weather agent",
)

# Expose via FastAPI
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=ag_ui_agent,
    path="/",
)
```

### 3. CopilotKit Frontend Integration
```tsx
// page.tsx
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";

export default function Home() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="weather_agent">
      <CopilotSidebar defaultOpen={true}>
        <YourCustomUI />
      </CopilotSidebar>
    </CopilotKit>
  );
}

// CopilotKit runtime proxy lives in ui/src/app/api/copilotkit/route.ts
// Override backend location with AGENT_RUNTIME_URL if needed.
```

### 4. Communication Flow
```
User Query → CopilotKit → HTTP/SSE → FastAPI → AG-UI Endpoint 
→ Azure AI Agent → get_weather() tool → OpenWeatherMap API 
→ Response → AG-UI → SSE → CopilotKit → User
```

## 🎨 Customization

### Change UI Appearance
Edit `ui/src/app/page.tsx`:
- Modify Tailwind classes for styling
- Add custom React components
- Change sidebar labels and initial message
- Add your company branding

### Add More Tools
Edit `agent/src/weather_agent.py`:
```python
@ai_function(name="your_tool", description="...")
def your_tool(param: str) -> str:
    return "result"

# Add to agent
azure_agent = AzureAIClient(...).create_agent(
    tools=[get_weather, your_tool],
)
```

### Change Ports
```bash
# Backend
export AGENT_PORT=8300

# Frontend (edit package.json)
"dev": "next dev --port 3300"
```

## 🐛 Troubleshooting

### Backend Issues

**"Connection refused" or "Agent not responding"**
- Ensure backend is running: `python agent/src/main.py`
- Check http://localhost:8200/docs works
- Verify `.env` file has correct Azure credentials

**"Authentication failed"**
- Run `az login` before starting
- Verify Azure AI project endpoint and deployment name

**"Weather API error"**
- Check `OPENWEATHER_API_KEY` in `.env`
- Test manually: `curl "http://api.openweathermap.org/data/2.5/weather?q=Toronto&appid=YOUR_KEY"`

### Frontend Issues

**"Cannot find module @copilotkit/..."**
- Run `npm install` in `ui/` directory
- Try `rm -rf node_modules && npm install`

**"Connection error" in UI**
- Ensure backend is running on port 8200
- Check browser console for CORS errors
- Verify `runtimeUrl="http://localhost:8200"` in `page.tsx`

**"Page not loading"**
- Check Next.js terminal for build errors
- Try `npm run dev` again
- Clear `.next/` folder: `rm -rf .next`

## 📊 Comparison: DevUI vs CopilotKit

| Aspect | DevUI | This (CopilotKit) |
|--------|-------|-------------------|
| **Purpose** | Development/Testing | Production Deployment |
| **Setup** | Single command | Backend + Frontend |
| **Stack** | Python only | Python + React |
| **Customization** | Limited theme | Full UI control |
| **Tracing** | Built-in panel | External tools |
| **Agent Discovery** | Automatic (directories) | Manual routing |
| **Best For** | Demos, debugging | Customer-facing apps |

## 🎯 When to Use Each

### Use DevUI when:
- ✅ Developing and testing agents
- ✅ Running demos or workshops
- ✅ Need quick agent switching
- ✅ Want built-in tracing/debugging
- ✅ Python-only environment

### Use CopilotKit when:
- ✅ Building production applications
- ✅ Need custom branding/UI
- ✅ Embedding in existing React app
- ✅ Serving end users (not developers)
- ✅ Require advanced UI interactions

## 📚 Resources

- **Agent Framework**: https://aka.ms/agent-framework
- **CopilotKit**: https://docs.copilotkit.ai
- **AG-UI Protocol**: See `/maf-upstream/docs/decisions/0010-ag-ui-support.md`
- **DevUI Demo**: `../azure_ai_devui/` (6 agents including this weather one)
- **Azure AI Studio**: https://ai.azure.com

## 🔗 Related Demos

- **DevUI Gallery**: `../azure_ai_devui/` - 6 agents in development UI
- **Simple Weather**: `/AQ-CODE/demos/maf-simple-weather/` - Original CopilotKit template
- **Streamlit Demo**: `/AQ-CODE/demos/streamlit_azure_ai_demo.py` - Alternative UI approach

## 📝 Notes for Tomorrow's Demo

**Key Points to Emphasize:**
1. **Same Agent, Different UI** - Show it's the exact same weather agent
2. **Development → Production** - DevUI for dev, CopilotKit for production
3. **AG-UI Protocol** - Open standard enabling this flexibility
4. **Real Tools** - Not fake data, actual OpenWeatherMap API
5. **Azure AI Powered** - Using Microsoft's agent framework and Azure AI

**Demo Script:**
1. Show DevUI first (already setup) - "Development workflow"
2. Show this CopilotKit version - "Production deployment"
3. Highlight same queries work in both
4. Explain AG-UI protocol enables portability
5. Mention customization possibilities (branding, embedding)

Good luck with your presentation! 🚀

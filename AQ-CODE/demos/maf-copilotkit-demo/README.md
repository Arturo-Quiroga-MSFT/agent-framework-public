# MAF + CopilotKit Demo

A modern, production-ready demo showcasing **Microsoft Agent Framework (MAF)** with **CopilotKit** for rich, interactive agent UIs. This replaces the Streamlit-based demo with a professional web application featuring:

- 🎨 **Generative UI** - Custom React components rendered by agents
- 👤 **Human-in-the-Loop** - Approval workflows for critical operations
- 🔄 **Shared State** - Bidirectional state synchronization
- 🌊 **Real-time Streaming** - Live agent responses with SSE
- 🎯 **AG-UI Protocol** - Open standard for agent-UI communication

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  Next.js + CopilotKit (Frontend)        │
│  - Agent selection UI                   │
│  - Weather cards, chart displays        │
│  - Code execution approval dialogs      │
│  - Search result visualizations         │
│  Port: 3000                              │
└──────────────┬──────────────────────────┘
               │ AG-UI Protocol
               │ (HTTP + Server-Sent Events)
┌──────────────▼──────────────────────────┐
│  FastAPI + AG-UI (Backend)              │
│  - Weather Agent (/agents/weather)      │
│  - Code Agent (/agents/code)            │
│  - Bing Search (/agents/bing-search)    │
│  - Azure AI Search                      │
│  - Firecrawl MCP                        │
│  - Microsoft Learn MCP                  │
│  Port: 8000                              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  MAF + Azure OpenAI / OpenAI            │
│  - ChatAgent orchestration              │
│  - Tool execution (functions, hosted)  │
│  - Thread management                    │
└─────────────────────────────────────────┘
```

## ✨ Features

### Agents Available

1. **Weather Agent** 🌤️
   - Real-time weather data via OpenWeatherMap API
   - Custom weather card with icon, temperature, humidity
   - **Generative UI**: Weather card component

2. **Code Interpreter** 💻
   - Execute Python code for calculations and visualizations
   - Generate matplotlib plots and charts
   - **Human-in-the-Loop**: Approval required before code execution
   - **Generative UI**: Chart displays, code output cards

3. **Bing Search** 🔍
   - Web search with Bing grounding
   - Current, real-time information retrieval
   - Citations and source links
   - Conversation memory for follow-up questions

4. **Azure AI Search** 🏨
   - Search indexed hotel database
   - Find hotels by location, amenities, ratings
   - Structured search results

5. **Firecrawl MCP** 🔥
   - Advanced web scraping
   - Extract clean content from any website
   - Handle JavaScript-heavy sites
   - **Requires**: Firecrawl API key

6. **Microsoft Learn MCP** 📚
   - Search Microsoft documentation
   - Azure, .NET, Microsoft 365 docs
   - Code examples and best practices

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 20+** & npm/pnpm/yarn
- **Azure OpenAI** or **OpenAI** API access
- **OpenWeatherMap API key** (free tier available)
- **Firecrawl API key** (optional)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   # or with uv:
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

   **Required variables:**
   ```bash
   # Azure OpenAI (recommended)
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
   
   # OR OpenAI
   OPENAI_API_KEY=sk-...
   OPENAI_CHAT_MODEL_ID=gpt-4o-mini
   
   # Azure AI Project (for hosted tools)
   AZURE_AI_PROJECT_ENDPOINT=https://your-project.azure.com/
   
   # External APIs
   OPENWEATHER_API_KEY=your-key-here
   FIRECRAWL_API_KEY=your-key-here  # Optional
   ```

4. **Start the backend server:**
   ```bash
   cd src
   python main.py
   ```

   Server will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or: pnpm install, yarn install, bun install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   Frontend will start on `http://localhost:3000`

### Access the Demo

Open your browser to **http://localhost:3000**

## 🎮 Usage Guide

### Weather Agent Demo

**Try these:**
- "What's the weather in Tokyo?"
- "Tell me the weather in Paris"
- "How's the weather in New York City?"

**What happens:**
- Agent calls `get_weather()` function
- Custom weather card appears with icon, temp, humidity
- Beautiful UI instead of plain text

### Code Interpreter Demo

**Try these:**
- "Plot a sine wave from 0 to 2π"
- "Create a 3D surface plot of z = sin(x) * cos(y)"
- "Generate the Fibonacci sequence up to 1000"
- "Create a histogram of 1000 random normal values"

**What happens:**
- Agent writes Python code
- **Approval dialog appears** (Human-in-the-Loop)
- Click "Approve" to execute
- Chart/plot displays inline in chat
- Can download generated images

### Bing Search Demo

**Try these:**
- "What are the latest developments in AI?"
- "Who won the most recent Nobel Prize in Physics?"
- "What's happening in tech news today?"
- **Follow-up**: "Tell me more about that"

**What happens:**
- Agent searches Bing for current information
- Provides answer with citations
- Follow-up questions use conversation memory

### Azure AI Search Demo

**Try these:**
- "Search for luxury hotels with good ratings"
- "Find hotels near the beach"
- "Show me budget-friendly hotels"

**What happens:**
- Agent searches hotels-sample-index
- Returns structured hotel information
- Can compare multiple results

### Firecrawl MCP Demo

**Try these:**
- "Scrape https://news.ycombinator.com and summarize top stories"
- "What are the latest articles on https://techcrunch.com about AI?"
- "Extract content from https://example.com/article"

**What happens:**
- Agent uses Firecrawl to scrape website
- Extracts clean, LLM-ready content
- Summarizes key information

### Microsoft Learn MCP Demo

**Try these:**
- "How do I create an Azure storage account using az cli?"
- "What is the Microsoft Agent Framework?"
- "Explain Azure OpenAI Service capabilities"

**What happens:**
- Agent searches Microsoft Learn docs
- Provides official documentation excerpts
- Includes code examples when relevant

## 🎨 Customization

### Adding New Agents

1. **Create agent module** in `backend/src/agents/`:
   ```python
   from agent_framework import ChatAgent, ai_function
   from agent_framework_ag_ui import AgentFrameworkAgent
   
   def create_my_agent(chat_client):
       base_agent = ChatAgent(
           name="my_agent",
           instructions="...",
           chat_client=chat_client,
           tools=[my_function],
       )
       
       return AgentFrameworkAgent(
           agent=base_agent,
           name="MyAgent",
           description="...",
           state_schema={},
           require_confirmation=False,
       )
   ```

2. **Register in `main.py`:**
   ```python
   my_agent = create_my_agent(chat_client)
   add_agent_framework_fastapi_endpoint(
       app=app,
       agent=my_agent,
       path="/agents/my-agent",
   )
   ```

3. **Add frontend UI** in `frontend/src/app/page.tsx`

### Creating Custom UI Cards

Add generative UI components for agent tools:

```tsx
useCopilotAction({
  name: "my_function",
  available: "disabled",  // Backend-only
  render: ({ args }) => (
    <MyCustomCard data={args.data} />
  ),
})
```

## 📊 Comparison to Streamlit Demo

| Feature | Streamlit Demo | CopilotKit Demo |
|---------|----------------|-----------------|
| **UI Framework** | Streamlit (Python) | Next.js + React |
| **Styling** | Limited customization | Fully customizable |
| **Real-time Streaming** | ✓ Basic | ✓ Advanced (SSE) |
| **Generative UI** | ✗ Text only | ✓ Custom components |
| **Human-in-the-Loop** | ✗ Manual | ✓ Built-in dialogs |
| **Shared State** | ✗ Session-based | ✓ Bidirectional sync |
| **Production Ready** | Demo-grade | Production-grade |
| **Mobile Support** | Limited | Responsive |
| **Extensibility** | Moderate | High |
| **Protocol** | Streamlit-specific | AG-UI (open standard) |

## 🔧 Troubleshooting

### Backend Issues

**"Unable to initialize chat client"**
- Check `.env` file exists and has correct credentials
- Verify `AZURE_OPENAI_ENDPOINT` or `OPENAI_API_KEY` is set
- Try `az login` if using Azure authentication

**"Weather API error"**
- Verify `OPENWEATHER_API_KEY` is set in `.env`
- Get free API key at https://openweathermap.org/api

**"Bing grounding not available"**
- Ensure Bing connection configured in Azure AI Foundry
- Check `BING_CONNECTION_NAME` or use default

### Frontend Issues

**"Cannot connect to agent"**
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in backend `main.py`
- Verify agent path in frontend config

**"Agent not responding"**
- Check browser console for errors
- Verify AG-UI endpoint URL
- Restart both backend and frontend

## 📚 Resources

- **MAF Documentation**: https://learn.microsoft.com/agent-framework
- **AG-UI Protocol**: https://docs.ag-ui.com/introduction
- **CopilotKit Docs**: https://docs.copilotkit.ai
- **MAF + CopilotKit Integration**: https://docs.copilotkit.ai/microsoft-agent-framework

## 🎯 Key Takeaways

1. **AG-UI Protocol** - Open standard, not vendor lock-in
2. **Generative UI** - Agents create custom UI components
3. **Human-in-the-Loop** - Built-in approval workflows
4. **Production-Ready** - Professional UX out of the box
5. **Extensible** - Easy to add new agents and UI components

## 🚀 For Teradata Presentation

This demo showcases:
- ✅ Enterprise agent backends (MAF)
- ✅ Consumer-grade UX (CopilotKit)
- ✅ All features from Streamlit demo + more
- ✅ Production-ready architecture
- ✅ Open standards (AG-UI, MCP)

**Perfect for demonstrating how Teradata can build modern agent experiences!**

---

Built with ❤️ using Microsoft Agent Framework + CopilotKit

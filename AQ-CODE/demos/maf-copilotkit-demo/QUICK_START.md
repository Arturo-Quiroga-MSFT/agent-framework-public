# Quick Start Guide

## ⚡ Fast Setup (5 minutes)

### 1. Install Prerequisites
```bash
# Check Python 3.12+
python3 --version

# Check Node.js 20+
node --version
```

### 2. Run Setup Script
```bash
cd /path/to/maf-copilotkit-demo
chmod +x setup.sh
./setup.sh
```

### 3. Configure Environment
Edit `backend/.env`:
```bash
# Minimum required
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
AZURE_AI_PROJECT_ENDPOINT=https://your-project.azure.com/
OPENWEATHER_API_KEY=your-key
```

### 4. Start Servers

**Terminal 1 (Backend):**
```bash
cd backend/src
python main.py
```
Wait for: `🎉 Server ready!`

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
Wait for: `Ready on http://localhost:3000`

### 5. Open Browser
Navigate to: **http://localhost:3000**

---

## 🎮 Quick Demo Script

### Weather (30 seconds)
1. Select "Weather Agent"
2. Ask: "What's the weather in Tokyo?"
3. Watch custom weather card appear ✨

### Code Interpreter (1 minute)
1. Select "Code Interpreter"
2. Ask: "Plot a sine wave"
3. Approve execution in dialog 👍
4. See chart inline in chat 📊

### Bing Search (30 seconds)
1. Select "Bing Search"
2. Ask: "Latest AI news?"
3. See citations and sources 🔍

---

## 🔧 Common Issues

### Backend won't start
```bash
# Check .env file exists
ls backend/.env

# Verify credentials
cat backend/.env | grep AZURE_OPENAI_ENDPOINT

# Try Azure login
az login
```

### Frontend connection error
```bash
# Verify backend is running
curl http://localhost:8000/

# Check CORS settings in backend/src/main.py
```

### Weather API not working
```bash
# Test API key directly
curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"

# Get new key at: https://openweathermap.org/api
```

---

## 📁 Project Structure

```
maf-copilotkit-demo/
├── backend/
│   ├── .env                  # Your credentials
│   ├── pyproject.toml        # Python dependencies
│   └── src/
│       ├── main.py           # FastAPI server
│       └── agents/           # Agent definitions
│           ├── weather_agent.py
│           ├── code_agent.py
│           ├── search_agent.py
│           ├── file_agent.py
│           ├── azure_search_agent.py
│           └── mcp_agent.py
├── frontend/
│   ├── package.json          # npm dependencies
│   └── src/
│       ├── app/
│       │   └── page.tsx      # Main UI
│       └── components/       # UI components
├── README.md                 # Full documentation
├── DEMO_GUIDE.md            # Presentation guide
└── setup.sh                 # Setup script
```

---

## 🎯 Agent Endpoints

All agents available at `http://localhost:8000/agents/`:

| Agent | Endpoint | Description |
|-------|----------|-------------|
| Weather | `/agents/weather` | Real-time weather data |
| Code | `/agents/code` | Python code execution |
| Bing | `/agents/bing-search` | Web search |
| Azure AI Search | `/agents/azure-ai-search` | Hotel search |
| Firecrawl | `/agents/firecrawl` | Web scraping |
| MS Learn | `/agents/microsoft-learn` | Docs search |

---

## 🚀 Quick Commands

```bash
# Backend
cd backend/src && python main.py

# Frontend  
cd frontend && npm run dev

# Test backend health
curl http://localhost:8000/

# View API docs
open http://localhost:8000/docs

# Install dependencies
cd backend && pip install -e .
cd frontend && npm install
```

---

## 📚 Key Concepts

**AG-UI Protocol**
- Open standard for agent↔UI communication
- HTTP + Server-Sent Events
- Not vendor-specific

**Generative UI**
- Agents render custom React components
- Not just text responses
- Example: Weather card, charts

**Human-in-the-Loop (HITL)**
- Approval workflows for critical actions
- Built into AG-UI protocol
- Example: Code execution approval

**Shared State**
- Bidirectional state synchronization
- Frontend and backend stay in sync
- Example: Conversation history

---

## 🎬 Demo Tips

**Before presenting:**
- Test all agents
- Clear browser cache
- Set browser zoom to 125%
- Close unnecessary tabs

**During demo:**
- Start with weather (quick win)
- Show code interpreter approval (impressive)
- Mention open standards (important)

**If something fails:**
- Have backup agent ready
- Blame "demo gods" 😄
- Show code instead

---

Need more help? See **README.md** for full documentation!

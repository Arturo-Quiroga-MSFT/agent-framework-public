# DevUI Guide for GitHub Models Examples

This guide explains how to use the DevUI-enabled examples (05 and 06) to visualize and interact with your GitHub Models agents through a web interface.

---

## 📋 Table of Contents

1. [What is DevUI?](#what-is-devui)
2. [Installation](#installation)
3. [Example 05: Sequential Workflow](#example-05-sequential-workflow)
4. [Example 06: Parallel Agents](#example-06-parallel-agents)
5. [DevUI Features](#devui-features)
6. [Comparison: Scripts vs DevUI](#comparison-scripts-vs-devui)
7. [API Access](#api-access)
8. [Troubleshooting](#troubleshooting)

---

## What is DevUI?

**DevUI** (Development UI) is Microsoft Agent Framework's interactive web interface for testing, debugging, and visualizing AI agents.

### Key Benefits

✅ **Interactive Testing** - Test agents via web browser, no code changes needed  
✅ **Visual Interface** - See conversation history, agent responses, and execution flow  
✅ **Real-time Monitoring** - Watch agents execute in real-time  
✅ **API Access** - OpenAI-compatible API endpoint for programmatic access  
✅ **Multi-turn Conversations** - Maintain conversation history across interactions  
✅ **Multiple Agents** - Switch between agents in a dropdown  

### When to Use DevUI vs Scripts

| Use Case | Best Choice |
|----------|-------------|
| **Development & Testing** | 🌐 DevUI (Examples 05/06) |
| **Interactive Demos** | 🌐 DevUI (Examples 05/06) |
| **Team Collaboration** | 🌐 DevUI (Examples 05/06) |
| **Quick Prototyping** | 🌐 DevUI (Examples 05/06) |
| **Automation & CI/CD** | 📄 Scripts (Examples 03/04) |
| **Batch Processing** | 📄 Scripts (Examples 03/04) |
| **Production Deployment** | 📄 Scripts (Examples 03/04) |

---

## Installation

### 1. Install DevUI Package

```bash
pip install agent-framework-devui --pre
```

### 2. Verify Installation

```bash
devui --version
```

### 3. Prerequisites

- All prerequisites from main [README.md](./README.md)
- `GITHUB_TOKEN` configured in `.env`
- Python 3.10+

---

## Example 05: Sequential Workflow

### What It Does

Runs a 3-agent sequential workflow interactively:
1. **Research Agent** - Gathers information
2. **Analysis Agent** - Generates insights (uses research)
3. **Writer Agent** - Creates final report (uses both)

### Launch DevUI

```bash
cd /path/to/agents-with-github-models
python 05_github_sequential_devui.py
```

**Expected Output:**
```
================================================================================
🚀 Sequential Multi-Agent Workflow - DevUI
================================================================================

📋 Workflow: Research → Analysis → Writing (Sequential)
🔧 Using: GitHub Models with Microsoft Agent Framework

🌐 Starting DevUI server...

✅ Sequential workflow created

================================================================================
🎯 DevUI Interface
================================================================================

🌐 Web UI:  http://localhost:8080
📡 API:     http://localhost:8080/v1/*
🔍 Entity:  sequential_workflow
```

### How to Use

1. **Open Browser**  
   Navigate to [http://localhost:8080](http://localhost:8080)

2. **Select Agent**  
   Choose `sequential_workflow` from the dropdown

3. **Enter Topic**  
   Examples:
   - "AI-powered personal learning assistant for professionals"
   - "Blockchain-based supply chain tracking system"
   - "Sustainable urban farming marketplace"

4. **Watch Execution**  
   See agents execute sequentially:
   ```
   User Query → Research Agent (30s)
              → Analysis Agent (20s)  
              → Writer Agent (25s)
              → Final Report
   ```

5. **Review Results**  
   Read comprehensive report in the chat interface

### Example Conversation

**You:** Analyze the potential of AI-powered code review tools

**Sequential Workflow:**
- 🔬 Research Agent gathers market data, existing solutions, trends
- 📊 Analysis Agent identifies patterns, opportunities, risks
- ✍️ Writer Agent synthesizes into structured report with recommendations

**Output:** Complete analysis report with executive summary, findings, and recommendations

---

## Example 06: Parallel Agents

### What It Does

Provides 4 independent specialist agents that can:
- Work individually for focused insights
- Work in parallel for multiple perspectives

### The 4 Specialists

1. **🔧 Technical Analyst**
   - Architecture & tech stack
   - Scalability & performance
   - Implementation complexity

2. **💼 Business Analyst**
   - Market opportunity
   - Revenue models
   - Competitive strategy

3. **⚖️ Risk Analyst**
   - Regulatory compliance
   - Security & privacy
   - Risk mitigation

4. **🎨 Creative Consultant**
   - Innovation & UX
   - Differentiation
   - Emerging trends

### Launch DevUI

```bash
cd /path/to/agents-with-github-models
python 06_github_parallel_devui.py
```

**Expected Output:**
```
================================================================================
⚡ Parallel Multi-Agent Analysis - DevUI
================================================================================

📋 Agents: 4 specialists (Technical, Business, Risk, Creative)
🔧 Using: GitHub Models with Microsoft Agent Framework

🌐 Starting DevUI server...

✅ All agents created:
   • Technical Analyst
   • Business Analyst
   • Risk Analyst
   • Creative Consultant

🌐 Web UI:  http://localhost:8081
```

### How to Use

#### Mode 1: Individual Agent Conversations

1. **Open Browser** - [http://localhost:8081](http://localhost:8081)
2. **Select ONE Agent** from dropdown:
   - `technical_analyst`
   - `business_analyst`
   - `risk_analyst`
   - `creative_consultant`
3. **Chat with Specialist** - Get focused insights from their domain
4. **Ask Follow-ups** - Multi-turn conversations supported

**Example:**
```
You → technical_analyst: "AI code review tool architecture"

Technical Analyst:
- Microservices architecture recommended
- Python/TypeScript stack
- GitHub API integration
- ML model for code analysis
- Redis for caching
- Estimated 3-6 months development

You: "What about scalability for 1000+ repos?"

Technical Analyst:
- Horizontal scaling with Kubernetes
- Queue-based processing (RabbitMQ/SQS)
- Distributed caching strategy
- ...
```

#### Mode 2: Parallel Perspective Comparison

1. **Open 4 Browser Tabs/Windows**
2. **Select Different Agent** in each tab:
   - Tab 1: `technical_analyst`
   - Tab 2: `business_analyst`
   - Tab 3: `risk_analyst`
   - Tab 4: `creative_consultant`
3. **Ask SAME Question** to all agents
4. **Compare Side-by-Side** - See different perspectives

**Example Topic:** "AI-powered mental health therapy app"

| Agent | Focus Area |
|-------|-----------|
| 🔧 Technical | Architecture, AI models, privacy tech, mobile stack |
| 💼 Business | Market size ($3B), B2C pricing, insurance integration |
| ⚖️ Risk | HIPAA compliance, liability, data security, disclaimers |
| 🎨 Creative | Empathetic UX, gamification, community features, AR therapy |

---

## DevUI Features

### Chat Interface

- **Conversation History** - All messages saved per session
- **Multi-turn Dialogs** - Context maintained across exchanges
- **Streaming Responses** - See agent output in real-time
- **Markdown Support** - Formatted responses with code blocks, lists, etc.

### Agent Selection

- **Dropdown Menu** - Switch between agents/workflows
- **Entity IDs** - Unique identifier for each agent
- **Multiple Entities** - Run multiple agents simultaneously (different ports)

### Visual Feedback

- **Typing Indicators** - Shows when agent is thinking
- **Error Messages** - Clear error display with troubleshooting
- **Execution Time** - See how long each response takes

### Developer Tools

- **API Endpoints** - OpenAI-compatible REST API
- **Request Inspection** - View raw requests/responses
- **Conversation Export** - Save conversation history
- **Health Checks** - Monitor server status

---

## Comparison: Scripts vs DevUI

### Example 03 (Script) vs Example 05 (DevUI)

| Aspect | 03 (Script) | 05 (DevUI) |
|--------|-------------|------------|
| **Interface** | Terminal/Console | Web Browser |
| **Input Method** | Hardcoded in Python | Type in UI |
| **Testing New Topics** | Edit code → Run script | Just type in browser |
| **Output** | Console text | Formatted chat UI |
| **History** | Scroll terminal | Saved conversations |
| **Multi-turn** | Not supported | Fully supported |
| **API Access** | No | Yes (`/v1/*`) |
| **Use Case** | Automation | Development/Testing |

### Example 04 (Script) vs Example 06 (DevUI)

| Aspect | 04 (Script) | 06 (DevUI) |
|--------|-------------|------------|
| **Execution** | Runs all 4 agents once | Interactive individual agents |
| **Input** | Hardcoded topic | Chat interface |
| **Output** | All 4 results printed | Select agent, chat individually |
| **Comparison** | Manual (read console) | Open 4 tabs, compare live |
| **Follow-ups** | Not supported | Multi-turn per agent |
| **Workflow** | Single batch run | Ongoing conversations |

---

## API Access

Both DevUI examples expose OpenAI-compatible API endpoints.

### Example 05 API (Sequential Workflow)

**Endpoint:** `http://localhost:8080/v1/chat/completions`

**Request:**
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sequential_workflow",
    "messages": [
      {"role": "user", "content": "Analyze AI education platforms"}
    ]
  }'
```

**Response:**
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1704067200,
  "model": "sequential_workflow",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "EXECUTIVE SUMMARY\n\n[Comprehensive report from 3-agent workflow]\n\n..."
    },
    "finish_reason": "stop"
  }]
}
```

### Example 06 API (Parallel Agents)

**Endpoint:** `http://localhost:8081/v1/chat/completions`

**Request (Technical Analyst):**
```bash
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "technical_analyst",
    "messages": [
      {"role": "user", "content": "Architecture for AI code review"}
    ]
  }'
```

**Request (Business Analyst):**
```bash
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "business_analyst",
    "messages": [
      {"role": "user", "content": "Market size for AI code review"}
    ]
  }'
```

### List Available Agents

```bash
# Example 05
curl http://localhost:8080/v1/entities

# Example 06
curl http://localhost:8081/v1/entities
```

**Response:**
```json
{
  "entities": [
    {
      "id": "technical_analyst",
      "type": "agent",
      "name": "technical_analyst"
    },
    {
      "id": "business_analyst",
      "type": "agent",
      "name": "business_analyst"
    }
    // ...
  ]
}
```

---

## Troubleshooting

### Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or use different port
# Edit the script and change: port=8080 → port=8082
```

### DevUI Not Installed

**Error:**
```
ModuleNotFoundError: No module named 'agent_framework.devui'
```

**Solution:**
```bash
pip install agent-framework-devui --pre
```

### Browser Doesn't Auto-Open

**Issue:** DevUI server starts but browser doesn't open automatically.

**Solution:**
```bash
# Manually open browser to:
http://localhost:8080  # Example 05
# or
http://localhost:8081  # Example 06
```

### Agent Not Responding

**Issue:** Agent selected but no response after submitting message.

**Troubleshooting:**
1. Check terminal for error messages
2. Verify `GITHUB_TOKEN` in `.env` file
3. Test token: `curl -H "Authorization: Bearer $GITHUB_TOKEN" https://models.inference.ai.azure.com/info`
4. Check rate limits (15 requests/min)
5. Try refreshing browser

### Slow Response Times

**Issue:** Agents taking 60+ seconds to respond.

**Causes:**
- GitHub Models rate limiting (15 req/min)
- Network latency
- Model processing time
- Sequential workflow accumulation (05 only)

**Solutions:**
- Wait 5 seconds between requests
- Use smaller prompts for faster responses
- Consider Azure OpenAI for production (higher limits)
- Use parallel agents (06) instead of sequential (05)

### Conversation History Lost

**Issue:** Refresh browser and conversation disappears.

**Explanation:** DevUI stores conversations in memory (not persisted to disk).

**Workaround:**
- Copy/paste important conversations before closing
- Use API to save responses programmatically
- Keep browser tab open during testing session

---

## Next Steps

### 1. Try Both Examples

```bash
# Terminal 1: Sequential workflow
python 05_github_sequential_devui.py

# Terminal 2: Parallel agents
python 06_github_parallel_devui.py
```

Open both in different browser tabs and compare!

### 2. Customize Agents

Edit the agent instructions in 05/06 to change:
- Agent personality and tone
- Output format and length
- Expertise areas and focus
- Domain-specific knowledge

### 3. Build Your Own

Use 05/06 as templates to create DevUI versions of your own agents:
- Copy the structure
- Modify agent instructions
- Change port number
- Add your specialized agents

### 4. Production Migration

When ready for production:
- Use examples 03/04 for automation
- Switch to Azure OpenAI for higher limits
- Add authentication and rate limiting
- Deploy as API service

---

## Resources

- [Main README](./README.md) - Complete guide and setup
- [COMPARISON.md](./COMPARISON.md) - GitHub Models vs Azure OpenAI vs Foundry
- [INDEX.md](./INDEX.md) - Navigation and learning paths
- [DevUI Documentation](https://github.com/microsoft/agent-framework/tree/main/python/packages/devui) - Official DevUI docs

---

## Summary

| Example | Type | Port | Best For |
|---------|------|------|----------|
| **05** | Sequential Workflow | 8080 | Comprehensive analysis, dependent steps |
| **06** | Parallel Agents | 8081 | Multiple perspectives, focused insights |

**Key Takeaway:** DevUI transforms your scripts into interactive web apps with zero additional code—just wrap your agents with `serve()` and you get a full UI + API!


# Azure AI Agents - DevUI Gallery

This directory contains Azure AI demo agents organized for DevUI's directory-based discovery. All agents will appear in the DevUI dropdown menu.

## Quick Start

```bash
# From the azure_ai directory
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/azure_ai

# Launch DevUI with all Azure AI agents
devui azure_agents --port 8100
```

Then open your browser to **http://localhost:8100** and you'll see all 4 agents in the dropdown!

## Available Agents

### 1. **WeatherAgent** (weather_agent_basic)
- Basic Azure AI Agent with real weather data
- Uses OpenWeatherMap API via `get_real_weather()` function
- Try: "What's the weather in Seattle?"

### 2. **WeatherTimeAgent** (weather_agent_functions)
- Multi-function agent with weather AND time capabilities
- Demonstrates multiple tool usage in one agent
- Try: "What's the weather in London and what time is it?"

### 3. **BingSearchAgent** (bing_grounding_agent)
- Web search using Bing Grounding
- Real-time information from the web
- **Requires**: BING_CONNECTION_ID in `.env`
- Try: "What are the latest news about AI?"

### 4. **CodeInterpreterAgent** (code_interpreter_agent)
- Executes Python code for calculations
- Perfect for math problems and algorithms
- Try: "Calculate the factorial of 100"

### 5. **CodeInterpreterWithImages** (code_interpreter_agent_with_images)
- ✨ **NEW**: Enhanced Code Interpreter with automatic plot display!
- Extracts and embeds generated plots in responses
- Saves plots to `generated_plots/` directory
- Base64 encodes images for DevUI inline display
- Try: "Create a plot of y = x^2 from -10 to 10"

## Prerequisites

### Required Environment Variables
```bash
# Azure AI Project (Required for all agents)
AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/yourProject"
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1-mini"

# Weather API (Required for weather agents)
OPENWEATHER_API_KEY="your-openweathermap-api-key"

# Bing Search (Required only for BingSearchAgent)
BING_CONNECTION_ID="/subscriptions/.../connections/your-bing-connection"
```

### Azure Authentication
All agents use Azure CLI authentication:
```bash
az login
```

## Directory Structure

```
azure_agents/
├── weather_agent_basic/
│   └── __init__.py                          # Exports: agent = WeatherAgent
├── weather_agent_functions/
│   └── __init__.py                          # Exports: agent = WeatherTimeAgent
├── bing_grounding_agent/
│   └── __init__.py                          # Exports: agent = BingSearchAgent
├── code_interpreter_agent/
│   └── __init__.py                          # Exports: agent = CodeInterpreterAgent
└── code_interpreter_agent_with_images/
    └── __init__.py                          # Exports: agent = CodeInterpreterWithImages
```

## Features

✅ **All agents in one UI** - No need to run separate servers  
✅ **Azure CLI authentication** - Uses `DefaultAzureCredential`  
✅ **Real weather data** - From OpenWeatherMap API  
✅ **Multiple tools** - Weather, time, web search, code execution  
✅ **Easy switching** - Use dropdown to switch between agents  
✨ **Plot display** - Automatic image extraction for Code Interpreter plots  

## Demo Scenarios

### Scenario 1: Basic Weather (5 min)
1. Select **WeatherAgent**
2. Ask: "What's the weather in Seattle?"
3. Ask: "How about Tokyo?"
4. Show real-time data updates

### Scenario 2: Multi-Tool Agent (5 min)
1. Select **WeatherTimeAgent**
2. Ask: "What's the weather in London and what time is it?"
3. Show how agent uses multiple tools in one query

### Scenario 3: Web Search (5 min)
1. Select **BingSearchAgent**
2. Ask: "What are the latest AI news?"
3. Show grounded answers with sources

### Scenario 4: Code Execution (10 min)
1. Select **CodeInterpreterAgent**
2. Ask: "Calculate factorial of 100"
3. Ask: "Generate first 20 Fibonacci numbers"
4. Show code generation and execution

### Scenario 5: Plot Generation with Auto-Display (10 min)
1. Select **CodeInterpreterWithImages**
2. Ask: "Create a plot of y = x^2 from -10 to 10"
3. Wait for response - plot will automatically appear inline!
4. Ask: "Create a bar chart showing values [5, 10, 15, 20]"
5. Show how multiple plots are embedded
6. Check `generated_plots/` directory for saved images

## Troubleshooting

### "AZURE_AI_PROJECT_ENDPOINT not found"
- Check `.env` file in `AQ-CODE/azure_ai/` directory
- Make sure endpoint URL is correct

### "OPENWEATHER_API_KEY not found"
- Get free API key from https://openweathermap.org/api
- Add to `.env` file: `OPENWEATHER_API_KEY=your-key`

### "BING_CONNECTION_ID not found"
- Only needed for BingSearchAgent
- Configure in Azure AI Foundry portal
- Skip this agent if you don't have Bing connection

### Authentication errors
- Run `az login` to authenticate with Azure CLI
- Ensure you have access to the Azure AI project

### Images not displaying
- Check browser developer console for base64 decoding errors
- Verify plots are being saved to `generated_plots/` directory
- Try the regular **CodeInterpreterAgent** if issues persist

## Comparison with Standalone Scripts

| Feature | Standalone Scripts | DevUI Gallery |
|---------|-------------------|---------------|
| Agent switching | Need to stop/start scripts | Dropdown menu |
| Port management | Manual (different ports) | Single port (8100) |
| Multi-agent testing | Run multiple terminals | Click dropdown |
| Conversation history | Manual management | Automatic |
| Demo presentation | Switch between files | Switch in browser |
| Plot display | Manual file handling | Automatic inline display ✨ |

Perfect for workshop presentations and customer demos! 🎯

## Technical Notes

### Image Display Implementation

The **CodeInterpreterWithImages** agent uses a custom wrapper that:
1. Runs the base Code Interpreter agent normally
2. After execution, queries the thread for image file outputs
3. Downloads image files using Azure AI SDK
4. Converts images to base64 for inline embedding
5. Appends markdown with data URIs to the response

**Limitations:**
- Images only appear after full response completion (not during streaming)
- Base64 encoding increases response size
- DevUI must support rendering markdown images

**For production:**
- Consider storing images externally (Azure Blob Storage)
- Use CDN URLs instead of base64 embedding
- Implement image caching and cleanup policies

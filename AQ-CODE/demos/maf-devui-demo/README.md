# MAF DevUI Demo

Quick demo of Microsoft Agent Framework with DevUI showing:
- ✅ Code Interpreter with inline matplotlib plots
- ✅ Real weather data from OpenWeatherMap API
- ✅ Native image rendering (no CopilotKit needed)

## Setup

1. **Install dependencies:**
```bash
pip install agent-framework-core agent-framework-devui httpx python-dotenv
```

2. **Configure `.env` file:**
```bash
# Already configured for your Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://aq-ai-foundry-sweden-central.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4.1-mini

# Add your OpenWeather API key (free from https://openweathermap.org/api)
OPENWEATHER_API_KEY=your_actual_key_here
```

3. **Authenticate with Azure:**
```bash
az login
```

## Run

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/demos/maf-devui-demo
python agent.py
```

Browser will open automatically at http://localhost:8090

## Try These Prompts

**Weather:**
- "What's the weather in San Francisco?"
- "Compare weather in London and Paris"

**Code Interpreter (plots display inline!):**
- "Create a bar chart showing sales data for Q1, Q2, Q3, Q4 with values 100, 150, 120, 180"
- "Plot a sine and cosine wave from 0 to 2π"
- "Generate a scatter plot of 50 random points colored by quadrant"
- "Create a histogram of 1000 random normal distributed values"
- "Make a pie chart of market share: Apple 30%, Samsung 25%, Google 20%, Others 25%"

**Combined:**
- "Get weather for Miami and create a line chart showing temperature, humidity, and wind speed"

## Features

### DevUI Advantages over CopilotKit:
- ✅ **Native image rendering** - matplotlib plots display inline automatically
- ✅ **Simpler setup** - single Python file, no frontend build
- ✅ **Built for Agent Framework** - designed specifically for MAF
- ✅ **OpenTelemetry tracing** - built-in observability
- ✅ **API-compatible** - OpenAI Responses API format

### What You Get:
- Real-time streaming responses
- Tool call visibility
- Image outputs rendered inline
- Clean, modern UI
- API access at http://localhost:8090/v1/*

## Project Structure

```
maf-devui-demo/
├── agent.py          # Main agent with Code Interpreter + Weather
├── .env              # Azure and OpenWeather configuration
└── README.md         # This file
```

## Next Steps

To add more features:
1. Add Bing Search: `HostedWebSearchTool()`
2. Add File Search: `HostedFileSearchTool()`
3. Add Azure AI Search: Configure connection in .env
4. Add more custom tools with `@ai_function`

## Troubleshooting

**Images not displaying?**
- DevUI automatically renders Code Interpreter images
- Make sure you're using `HostedCodeInterpreterTool()` (not a custom wrapper)
- Check that matplotlib is installed: `pip install matplotlib`

**Weather not working?**
- Get free API key: https://openweathermap.org/api
- Update `.env` with your key
- Restart the agent

**Azure authentication errors?**
- Run `az login` in terminal
- Verify credentials: `az account show`

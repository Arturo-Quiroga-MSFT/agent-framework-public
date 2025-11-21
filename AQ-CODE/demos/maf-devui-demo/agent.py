"""
MAF DevUI Demo Agent with Code Interpreter and Real Weather
Shows matplotlib plots inline in DevUI interface
"""
import os
from typing import Annotated

import httpx
from agent_framework import ChatAgent, HostedCodeInterpreterTool, ai_function
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from pydantic import Field

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
deployment_name = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

if not endpoint or not deployment_name:
    raise ValueError(
        "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_CHAT_DEPLOYMENT_NAME must be set in .env"
    )


@ai_function
def get_weather(
    location: Annotated[str, Field(description="The city to get weather for")],
) -> str:
    """Get real-time weather for a location using OpenWeatherMap API."""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OPENWEATHER_API_KEY not configured. Please set it in your .env file."

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=imperial"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        return f"""{{
    "location": "{data['name']}",
    "temperature": {data['main']['temp']},
    "condition": "{data['weather'][0]['description']}",
    "humidity": {data['main']['humidity']},
    "wind_speed": {data['wind']['speed']},
    "feels_like": {data['main']['feels_like']}
}}"""
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"


# Create Azure OpenAI chat client
chat_client = AzureOpenAIChatClient(
    credential=DefaultAzureCredential(),
    endpoint=endpoint,
    deployment_name=deployment_name,
)

# Create agent with ONLY Code Interpreter (remove weather to avoid confusion)
agent = ChatAgent(
    name="CodeInterpreterAgent",
    instructions="""You are a Python code execution assistant specialized in data visualization and analysis.

You can:
- Create any type of plot or chart using matplotlib
- Perform mathematical calculations with numpy
- Generate visualizations of fractals (Mandelbrot, Julia sets, etc.)
- Analyze data and create statistical plots
- Solve complex math problems

Always:
- Use matplotlib for visualizations
- Add clear titles, labels, and legends
- Use appropriate color schemes
- For fractals, use numpy for efficient computation
- Show your work by explaining the code

Create beautiful, well-documented visualizations!""",
    chat_client=chat_client,
    tools=[HostedCodeInterpreterTool()],  # ONLY Code Interpreter
)

if __name__ == "__main__":
    # For standalone testing
    from agent_framework.devui import serve

    print("=" * 70)
    print("🚀 MAF DevUI Demo - Code Interpreter + Real Weather")
    print("=" * 70)
    print("✅ Code Interpreter: Enabled (matplotlib plots display inline)")
    print("✅ Real Weather: Enabled (OpenWeatherMap API)")
    print("✅ Web UI: http://localhost:8090")
    print("✅ API: http://localhost:8090/v1/*")
    print("=" * 70)
    print("\n💡 Try these prompts:")
    print('   - "What\'s the weather in Tokyo?"')
    print('   - "Create a bar chart of Q1-Q4 sales: 100, 150, 120, 180"')
    print('   - "Plot a sine wave from 0 to 2π"')
    print('   - "Generate a scatter plot of 50 random points"')
    print("\n🖼️  Images will display inline in DevUI!\n")

    serve(entities=[agent], port=8090, auto_open=True)

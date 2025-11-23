"""
Azure AI Agent: Thread Persistence Agent

Demonstrates conversation memory across multiple queries.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Annotated
import httpx
from pydantic import Field

from agent_framework.azure import AzureAIClient
from agent_framework.observability import setup_observability
from azure.identity.aio import AzureCliCredential

# Load environment variables
local_env_path = Path(__file__).parent.parent.parent / "azure_ai" / ".env"
parent_env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=local_env_path)
load_dotenv(dotenv_path=parent_env_path)

# Setup observability for tracing
if os.getenv("ENABLE_OTEL", "").lower() == "true":
    app_insights_conn = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn:
        setup_observability(
            enable_sensitive_data=os.getenv("ENABLE_SENSITIVE_DATA", "").lower() == "true",
            applicationinsights_connection_string=app_insights_conn,
        )


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the current weather for a given location using OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return f"Error: OPENWEATHER_API_KEY not found in environment variables."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        return f"The weather in {location} is {description} with a temperature of {temp}°C (feels like {feels_like}°C) and {humidity}% humidity."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{location}' not found."
        return f"Error fetching weather data: {e}"
    except Exception as e:
        return f"Error: {str(e)}"


# Create the agent
credential = AzureCliCredential()

agent = AzureAIClient(async_credential=credential).create_agent(
    name="ThreadPersistenceAgent",
    description=(
        "Thread Persistence Agent - Multi-Turn Conversations\n"
        "\n"
        "Demonstrates conversation memory across multiple queries.\n"
        "\n"
        "TRY THESE:\n"
        "  1. What's the weather in Toronto?\n"
        "  2. How about Mexico City?\n"
        "  3. Which one is warmer?\n"
        "  4. What was the first city I asked about?\n"
        "\n"
        "FEATURES:\n"
        "  • Remembers previous queries\n"
        "  • Can compare across conversations\n"
        "  • Maintains context\n"
        "  • Multi-turn dialogue support"
    ),
    instructions="You are a helpful weather agent. Remember previous cities asked about and can compare them. Use the get_weather function to provide accurate weather information.",
    tools=get_weather,
)

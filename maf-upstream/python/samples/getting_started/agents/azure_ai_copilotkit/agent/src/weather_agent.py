"""
Azure AI Weather Agent with real OpenWeatherMap API.
This is the same agent from DevUI, adapted for AG-UI/CopilotKit.
"""
import os
from typing import Annotated
import httpx
from pydantic import Field
from dotenv import load_dotenv

from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.ag_ui import AgentFrameworkAgent
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()


@ai_function(
    name="get_weather",
    description="Get the current weather for a given location using OpenWeatherMap API.",
)
def get_weather(
    location: Annotated[str, Field(description="The city or location to get weather for. Use full names.")],
) -> str:
    """Get real-time weather data from OpenWeatherMap."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OPENWEATHER_API_KEY not found in environment variables."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        
        return f"""{{
    "location": "{data['name']}",
    "temperature": {temp},
    "condition": "{description}",
    "humidity": {humidity},
    "wind_speed": {wind_speed},
    "feels_like": {feels_like}
}}"""
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{location}' not found."
        return f"Error fetching weather data: {e}"
    except Exception as e:
        return f"Error: {str(e)}"


def create_weather_agent() -> AgentFrameworkAgent:
    """Create the Azure AI Weather Agent wrapped for AG-UI protocol."""
    
    # Get Azure configuration from environment
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    deployment = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    if not endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
    
    # Create chat client
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
        deployment_name=deployment,
        endpoint=endpoint,
    )
    
    # Create base agent
    base_agent = ChatAgent(
        name="WeatherAgent",
        instructions=(
            "You are a helpful weather assistant. Use the get_weather function to provide "
            "accurate, real-time weather information. Always format responses in a clear, "
            "friendly manner. Include temperature, conditions, humidity, and wind speed."
        ),
        chat_client=chat_client,
        tools=[get_weather],
    )
    
    # Wrap for AG-UI protocol (CopilotKit compatibility)
    return AgentFrameworkAgent(
        agent=base_agent,
        name="AzureAIWeatherAgent",
        description="Azure AI-powered weather agent with real OpenWeatherMap data",
        require_confirmation=False,
    )

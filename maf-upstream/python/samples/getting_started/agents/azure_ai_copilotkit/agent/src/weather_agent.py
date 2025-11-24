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


@ai_function(
    name="compare_weather",
    description="Compare weather conditions between multiple cities. Returns weather data for all cities in a structured format.",
)
def compare_weather(
    cities: Annotated[list[str], Field(description="List of cities to compare weather for. Use full city names.")],
) -> str:
    """Compare weather across multiple cities."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OPENWEATHER_API_KEY not found in environment variables."
    
    results = []
    for city in cities:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            results.append({
                "location": data["name"],
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "feels_like": data["main"]["feels_like"]
            })
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                results.append({"location": city, "error": "Location not found"})
            else:
                results.append({"location": city, "error": f"Error: {e}"})
        except Exception as e:
            results.append({"location": city, "error": str(e)})
    
    import json
    return json.dumps(results, indent=2)


def create_weather_agent() -> AgentFrameworkAgent:
    """Create the Azure AI Weather Agent wrapped for AG-UI protocol."""
    
    # Get Azure OpenAI configuration from environment
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-01-preview")
    
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
    
    # Create chat client with DefaultAzureCredential
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
        deployment_name=deployment,
        endpoint=endpoint,
        api_version=api_version,
    )
    
    # Create base agent
    base_agent = ChatAgent(
        name="WeatherAgent",
        instructions=(
            "You are a helpful weather assistant with access to real-time weather data. "
            "Use get_weather for single city queries and compare_weather when users ask to compare multiple cities. "
            "Always provide temperature, conditions, humidity, and wind speed. "
            "When comparing cities, highlight the differences and make helpful observations."
        ),
        chat_client=chat_client,
        tools=[get_weather, compare_weather],
    )
    
    # Wrap for AG-UI protocol (CopilotKit compatibility)
    return AgentFrameworkAgent(
        agent=base_agent,
        name="AzureAIWeatherAgent",
        description="Azure AI-powered weather agent with real OpenWeatherMap data",
        require_confirmation=False,
    )

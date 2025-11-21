"""
Weather Agent with Real OpenWeatherMap API Integration
"""

import os
from typing import Annotated

import httpx
from agent_framework import ChatAgent, ai_function
from agent_framework._clients import ChatClientProtocol
from agent_framework_ag_ui import AgentFrameworkAgent
from pydantic import Field


@ai_function(
    name="get_weather",
    description="Get the current weather for any location using real-time weather data.",
)
def get_weather(
    location: Annotated[
        str, Field(description="The location to get the weather for (city name or coordinates).")
    ],
) -> str:
    """Fetch real-time weather data from OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return "❌ Error: OPENWEATHER_API_KEY not found in environment variables."
    
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
        icon = data["weather"][0]["icon"]
        
        # Return structured data that frontend can parse for rich UI
        return f"""{{
            "location": "{location}",
            "temperature": {temp},
            "feels_like": {feels_like},
            "description": "{description}",
            "humidity": {humidity},
            "wind_speed": {wind_speed},
            "icon": "{icon}",
            "summary": "The weather in {location} is {description} with a temperature of {temp}°C (feels like {feels_like}°C), {humidity}% humidity, and wind speed of {wind_speed} m/s."
        }}"""
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"❌ Error: Location '{location}' not found."
        return f"❌ Error fetching weather data: {e}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def create_weather_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create weather agent with real-time weather API integration."""
    
    base_agent = ChatAgent(
        name="weather_agent",
        instructions="""You are a helpful weather assistant with access to real-time weather data.

When asked about weather:
1. ALWAYS use the get_weather function to fetch current weather data
2. Parse the JSON response and present it in a friendly, conversational way
3. Include temperature, conditions, humidity, and wind speed
4. Never apologize or say you can't access weather data - you have the function

Remember previous weather queries in the conversation for context.
""",
        chat_client=chat_client,
        tools=[get_weather],
    )
    
    return AgentFrameworkAgent(
        agent=base_agent,
        name="WeatherAgent",
        description="Real-time weather agent with OpenWeatherMap integration",
        state_schema={},  # No shared state needed for this agent
        require_confirmation=False,
    )

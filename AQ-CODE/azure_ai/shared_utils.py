# Copyright (c) Microsoft. All rights reserved.

"""
Shared utility functions for Azure AI agent samples.

This module provides reusable tools and utilities that can be used
across multiple agent samples in this directory.
"""

import os
from typing import Annotated

import httpx
from pydantic import Field


def get_real_weather(
    location: Annotated[str, Field(description="The city name or location to get weather for (e.g., 'Seattle', 'London', 'Tokyo')")]
) -> str:
    """Get real weather information for a location using OpenWeatherMap API.
    
    This function fetches current weather data from OpenWeatherMap API.
    Requires OPENWEATHER_API_KEY environment variable to be set.
    
    Args:
        location: The city name or location to get weather for
        
    Returns:
        A formatted string with current weather information including:
        - Temperature (Celsius and Fahrenheit)
        - Weather conditions (description)
        - Humidity
        - Wind speed
        
    Examples:
        >>> get_real_weather("Seattle")
        'Weather in Seattle, US: 15°C (59°F), partly cloudy. Humidity: 65%, Wind: 12 km/h'
        
    Note:
        - Get your free API key from: https://openweathermap.org/api
        - Add to .env file: OPENWEATHER_API_KEY=your_key_here
        - Free tier includes 1000 API calls per day
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    
    if not api_key:
        return (
            "❌ OpenWeatherMap API key not found. "
            "Please set OPENWEATHER_API_KEY in your .env file. "
            "Get a free API key at: https://openweathermap.org/api"
        )
    
    try:
        # OpenWeatherMap API endpoint
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Make API request
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric"  # Use Celsius
        }
        
        response = httpx.get(base_url, params=params, timeout=10.0)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract weather information
        city_name = data["name"]
        country = data["sys"]["country"]
        temp_celsius = data["main"]["temp"]
        temp_fahrenheit = (temp_celsius * 9/5) + 32
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        wind_speed = data["main"].get("speed", 0)
        
        # Format the response
        weather_info = (
            f"🌤️ Weather in {city_name}, {country}:\n"
            f"🌡️ Temperature: {temp_celsius:.1f}°C ({temp_fahrenheit:.1f}°F)\n"
            f"🤔 Feels like: {feels_like:.1f}°C\n"
            f"☁️ Conditions: {description.capitalize()}\n"
            f"💧 Humidity: {humidity}%\n"
            f"💨 Wind: {wind_speed:.1f} m/s"
        )
        
        return weather_info
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"❌ Location '{location}' not found. Please check the spelling or try a different city name."
        elif e.response.status_code == 401:
            return "❌ Invalid API key. Please check your OPENWEATHER_API_KEY in .env file."
        else:
            return f"❌ Error fetching weather data: {e.response.status_code} - {e.response.text}"
            
    except httpx.RequestError as e:
        return f"❌ Network error while fetching weather data: {str(e)}"
        
    except KeyError as e:
        return f"❌ Unexpected response format from weather API: missing {str(e)}"
        
    except Exception as e:
        return f"❌ Unexpected error getting weather: {str(e)}"


def get_mock_weather(
    location: Annotated[str, Field(description="The location to get weather for.")]
) -> str:
    """Get mock weather information for a location (for testing without API key).
    
    This is a simple mock function that returns randomized weather data.
    Useful for testing agents without requiring an API key.
    
    Args:
        location: The location to get weather for
        
    Returns:
        A formatted string with mock weather information
    """
    from random import randint
    
    conditions = ["sunny", "partly cloudy", "cloudy", "rainy", "stormy"]
    temp_c = randint(10, 30)
    temp_f = (temp_c * 9/5) + 32
    humidity = randint(40, 90)
    
    return (
        f"🌤️ Weather in {location}:\n"
        f"🌡️ Temperature: {temp_c}°C ({temp_f:.1f}°F)\n"
        f"☁️ Conditions: {conditions[randint(0, len(conditions)-1)].capitalize()}\n"
        f"💧 Humidity: {humidity}%\n"
        f"📝 Note: This is mock data for testing"
    )


# For backwards compatibility, provide the original mock function
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")]
) -> str:
    """Get weather for a given location (mock data).
    
    Deprecated: Use get_real_weather() for real data or get_mock_weather() for testing.
    This function is kept for backwards compatibility with existing samples.
    """
    from random import randint
    
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."

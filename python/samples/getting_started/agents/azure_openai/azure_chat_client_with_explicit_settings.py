# Copyright (c) Microsoft. All rights reserved.

import asyncio
import httpx
import os
from random import randint
from typing import Annotated
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from getting_started/.env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Chat Client with Explicit Settings Example

This sample demonstrates creating Azure OpenAI Chat Client with explicit configuration
settings rather than relying on environment variable defaults.
"""


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
async def main() -> None:
    print("=== Azure Chat Client with Explicit Settings ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = AzureOpenAIChatClient(
        deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        credential=AzureCliCredential(),
    ).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    result = await agent.run("What's the weather like in New York?")
    print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

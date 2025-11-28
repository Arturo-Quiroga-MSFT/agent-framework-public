# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import httpx
from typing import Annotated
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from local azure_ai/.env first, then fall back to getting_started/.env
local_env_path = Path(__file__).parent / ".env"
parent_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=local_env_path)  # Load local first
load_dotenv(dotenv_path=parent_env_path)  # Then parent (won't override existing vars)

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent Latest Version Example

This sample demonstrates how to reuse the latest version of an existing agent
instead of creating a new agent version on each instantiation. The first call creates a new agent,
while subsequent calls with `use_latest_version=True` reuse the latest agent version.
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
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with AzureCliCredential() as credential:
        async with (
            AzureAIClient(
                async_credential=credential,
            ).create_agent(
                name="MyWeatherAgent",
                instructions="You are a helpful weather agent.",
                tools=get_weather,
            ) as agent,
        ):
            # First query will create a new agent
            query = "What's the weather like in Toronto?"
            print(f"User: {query}")
            result = await agent.run(query)
            print(f"Agent: {result}\n")

        # Create a new agent instance
        async with (
            AzureAIClient(
                async_credential=credential,
                # This parameter will allow to re-use latest agent version
                # instead of creating a new one
                use_latest_version=True,
            ).create_agent(
                name="MyWeatherAgent",
                instructions="You are a helpful weather agent.",
                tools=get_weather,
            ) as agent,
        ):
            query = "What's the weather like in Mexico City?"
            print(f"User: {query}")
            result = await agent.run(query)
            print(f"Agent: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

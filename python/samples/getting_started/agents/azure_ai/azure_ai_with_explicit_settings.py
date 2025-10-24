# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from pathlib import Path
from typing import Annotated

import httpx
from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

# Load environment variables from getting_started/.env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

"""
Azure AI Agent with Explicit Settings Example

This sample demonstrates creating Azure AI Agents with explicit configuration
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
    print("=== Azure AI Chat Client with Explicit Settings ===")

    # Since no Agent ID is provided, the agent will be automatically created
    # and deleted after getting a response
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(
                project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
                model_deployment_name=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                async_credential=credential,
                agent_name="WeatherAgent",
            ),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        result = await agent.run("What's the weather like in New York?")
        print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

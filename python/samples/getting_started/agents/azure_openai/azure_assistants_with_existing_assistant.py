# Copyright (c) Microsoft. All rights reserved.

import asyncio
import httpx
import os
from typing import Annotated
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from getting_started/.env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIAssistantsClient
from azure.identity import AzureCliCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from pydantic import Field

"""
Azure OpenAI Assistants with Existing Assistant Example

This sample demonstrates working with pre-existing Azure OpenAI Assistants
using existing assistant IDs rather than creating new ones.
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
    print("=== Azure OpenAI Assistants Chat Client with Existing Assistant ===")

    token_provider = get_bearer_token_provider(AzureCliCredential(), "https://cognitiveservices.azure.com/.default")

    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token_provider=token_provider,
        api_version="2025-01-01-preview",
    )

    # Create an assistant that will persist
    created_assistant = await client.beta.assistants.create(
        model=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"], name="WeatherAssistant"
    )

    try:
        async with ChatAgent(
            chat_client=AzureOpenAIAssistantsClient(async_client=client, assistant_id=created_assistant.id),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent:
            result = await agent.run("What's the weather like in Tokyo?")
            print(f"Result: {result}\n")
    finally:
        # Clean up the assistant manually
        await client.beta.assistants.delete(created_assistant.id)


if __name__ == "__main__":
    asyncio.run(main())

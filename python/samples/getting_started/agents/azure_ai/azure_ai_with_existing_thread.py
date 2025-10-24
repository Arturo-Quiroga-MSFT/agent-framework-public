# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from pathlib import Path
from typing import Annotated

import httpx
from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

# Load environment variables from getting_started/.env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

"""
Azure AI Agent with Existing Thread Example

This sample demonstrates working with pre-existing conversation threads
by providing thread IDs for thread reuse patterns.
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
    print("=== Azure AI Chat Client with Existing Thread ===")

    # Create the client
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as client,
    ):
        # Create an thread that will persist
        created_thread = await client.agents.threads.create()

        try:
            async with ChatAgent(
                # passing in the client is optional here, so if you take the agent_id from the portal
                # you can use it directly without the two lines above.
                chat_client=AzureAIAgentClient(project_client=client),
                instructions="You are a helpful weather agent.",
                tools=get_weather,
            ) as agent:
                thread = agent.get_new_thread(service_thread_id=created_thread.id)
                assert thread.is_initialized
                result = await agent.run("What's the weather like in Tokyo?", thread=thread)
                print(f"Result: {result}\n")
        finally:
            # Clean up the thread manually
            await client.agents.threads.delete(created_thread.id)


if __name__ == "__main__":
    asyncio.run(main())

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
Azure AI Agent with Thread Management Example

This sample demonstrates thread management with Azure AI Agent, showing
persistent conversation capabilities using service-managed threads as well as storing messages in-memory.
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


async def example_with_automatic_thread_creation() -> None:
    """Example showing automatic thread creation."""
    print("=== Automatic Thread Creation Example ===")

    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="BasicWeatherAgent",
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        # First conversation - no thread provided, will be created automatically
        query1 = "What's the weather like in Toronto?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1.text}")

        # Second conversation - still no thread provided, will create another new thread
        query2 = "What was the last city I asked about?"
        print(f"\nUser: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2.text}")
        print("Note: Each call creates a separate thread, so the agent doesn't remember previous context.\n")


async def example_with_thread_persistence_in_memory() -> None:
    """
    Example showing thread persistence across multiple conversations.
    In this example, messages are stored in-memory.
    """
    print("=== Thread Persistence Example (In-Memory) ===")

    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="BasicWeatherAgent",
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        # Create a new thread that will be reused
        thread = agent.get_new_thread()

        # First conversation
        query1 = "What's the weather like in Mexico City?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, thread=thread, store=False)
        print(f"Agent: {result1.text}")

        # Second conversation using the same thread - maintains context
        query2 = "How about Guadalajara?"
        print(f"\nUser: {query2}")
        result2 = await agent.run(query2, thread=thread, store=False)
        print(f"Agent: {result2.text}")

        # Third conversation - agent should remember both previous cities
        query3 = "Which of the cities I asked about has better weather?"
        print(f"\nUser: {query3}")
        result3 = await agent.run(query3, thread=thread, store=False)
        print(f"Agent: {result3.text}")
        print("Note: The agent remembers context from previous messages in the same thread.\n")


async def example_with_existing_thread_id() -> None:
    """
    Example showing how to work with an existing thread ID from the service.
    In this example, messages are stored on the server.
    """
    print("=== Existing Thread ID Example ===")

    # First, create a conversation and capture the thread ID
    existing_thread_id = None

    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="BasicWeatherAgent",
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        # Start a conversation and get the thread ID
        thread = agent.get_new_thread()

        query1 = "What's the weather in Monterrey?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, thread=thread)
        print(f"Agent: {result1.text}")

        # The thread ID is set after the first response
        existing_thread_id = thread.service_thread_id
        print(f"Thread ID: {existing_thread_id}")

        if existing_thread_id:
            print("\n--- Continuing with the same thread ID in a new agent instance ---")

            async with (
                AzureAIClient(async_credential=credential).create_agent(
                    name="BasicWeatherAgent",
                    instructions="You are a helpful weather agent.",
                    tools=get_weather,
                ) as agent,
            ):
                # Create a thread with the existing ID
                thread = agent.get_new_thread(service_thread_id=existing_thread_id)

                query2 = "What was the last city I asked about?"
                print(f"User: {query2}")
                result2 = await agent.run(query2, thread=thread)
                print(f"Agent: {result2.text}")
                print("Note: The agent continues the conversation from the previous thread by using thread ID.\n")


async def main() -> None:
    print("=== Azure AI Agent Thread Management Examples ===\n")

    await example_with_automatic_thread_creation()
    await example_with_thread_persistence_in_memory()
    await example_with_existing_thread_id()


if __name__ == "__main__":
    asyncio.run(main())

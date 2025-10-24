# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from datetime import datetime, timezone
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
Azure AI Agent with Function Tools Example

This sample demonstrates function tool integration with Azure AI Agents,
showing both agent-level and query-level tool configuration patterns.
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


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a helpful assistant that can provide weather and time information.",
            tools=[get_weather, get_time],  # Tools defined at agent creation
        ) as agent,
    ):
        # First query - agent can use weather tool
        query1 = "What's the weather like in New York?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1}\n")

        # Second query - agent can use time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2}\n")

        # Third query - agent can use both tools if needed
        query3 = "What's the weather in London and what's the current UTC time?"
        print(f"User: {query3}")
        result3 = await agent.run(query3)
        print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")

    # Agent created without tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a helpful assistant.",
            # No tools defined here
        ) as agent,
    ):
        # First query with weather tool
        query1 = "What's the weather like in Toronto?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
        print(f"Agent: {result1}\n")

        # Second query with time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
        print(f"Agent: {result2}\n")

        # Third query with multiple tools
        query3 = "What's the weather in Chicago and what's the current UTC time?"
        print(f"User: {query3}")
        result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
        print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")

    # Agent created with some base tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a comprehensive assistant that can help with various information requests.",
            tools=[get_weather],  # Base tool available for all queries
        ) as agent,
    ):
        # Query using both agent tool and additional run-method tools
        query = "What's the weather in Denver and what's the current UTC time?"
        print(f"User: {query}")

        # Agent has access to get_weather (from creation) + additional tools from run method
        result = await agent.run(
            query,
            tools=[get_time],  # Additional tools for this specific query
        )
        print(f"Agent: {result}\n")


async def main() -> None:
    print("=== Azure AI Chat Client Agent with Function Tools Examples ===\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()


if __name__ == "__main__":
    asyncio.run(main())

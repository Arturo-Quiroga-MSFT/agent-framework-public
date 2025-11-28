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
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent Existing Conversation Example

This sample demonstrates usage of AzureAIClient with existing conversation created on service side.
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


async def example_with_client() -> None:
    """Example shows how to specify existing conversation ID when initializing Azure AI Client."""
    print("=== Azure AI Agent With Existing Conversation and Client ===")
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
    ):
        # Create a conversation using OpenAI client
        openai_client = await project_client.get_openai_client()
        conversation = await openai_client.conversations.create()
        conversation_id = conversation.id
        print(f"Conversation ID: {conversation_id}")

        async with AzureAIClient(
            project_client=project_client,
            # Specify conversation ID on client level
            conversation_id=conversation_id,
        ).create_agent(
            name="BasicAgent",
            instructions="You are a helpful agent.",
            tools=get_weather,
        ) as agent:
            query = "What's the weather like in Guadalajara?"
            print(f"User: {query}")
            result = await agent.run(query)
            print(f"Agent: {result.text}\n")

            query = "What was my last question?"
            print(f"User: {query}")
            result = await agent.run(query)
            print(f"Agent: {result.text}\n")


async def example_with_thread() -> None:
    """This example shows how to specify existing conversation ID with AgentThread."""
    print("=== Azure AI Agent With Existing Conversation and Thread ===")
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
        AzureAIClient(project_client=project_client).create_agent(
            name="BasicAgent",
            instructions="You are a helpful agent.",
            tools=get_weather,
        ) as agent,
    ):
        # Create a conversation using OpenAI client
        openai_client = await project_client.get_openai_client()
        conversation = await openai_client.conversations.create()
        conversation_id = conversation.id
        print(f"Conversation ID: {conversation_id}")

        # Create a thread with the existing ID
        thread = agent.get_new_thread(service_thread_id=conversation_id)

        query = "What's the weather like in Puebla?"
        print(f"User: {query}")
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result.text}\n")

        query = "What was my last question?"
        print(f"User: {query}")
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result.text}\n")


async def main() -> None:
    await example_with_client()
    await example_with_thread()


if __name__ == "__main__":
    asyncio.run(main())

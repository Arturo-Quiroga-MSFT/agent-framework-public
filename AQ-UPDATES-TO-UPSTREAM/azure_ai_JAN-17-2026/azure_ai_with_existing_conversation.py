# Copyright (c) Microsoft. All rights reserved.
import asyncio
import os
import sys
from pathlib import Path

from agent_framework.azure import AzureAIProjectAgentProvider
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Add weather_tool to path and import real weather function
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "AQ-CODE" / "azure_ai" / "weather_tool"))
from shared_utils import get_real_weather as get_weather

"""
Azure AI Agent Existing Conversation Example

This sample demonstrates usage of AzureAIProjectAgentProvider with existing conversation created on service side.
"""


async def example_with_conversation_id() -> None:
    """Example shows how to use existing conversation ID with the provider."""
    print("=== Azure AI Agent With Existing Conversation ===")
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
    ):
        # Create a conversation using OpenAI client
        openai_client = project_client.get_openai_client()
        conversation = await openai_client.conversations.create()
        conversation_id = conversation.id
        print(f"Conversation ID: {conversation_id}")

        provider = AzureAIProjectAgentProvider(project_client=project_client)
        agent = await provider.create_agent(
            name="BasicAgent",
            instructions="You are a helpful agent.",
            tools=get_weather,
        )

        # Pass conversation_id at run level
        query = "What's the weather like in Regina?"
        print(f"User: {query}")
        result = await agent.run(query, conversation_id=conversation_id)
        print(f"Agent: {result.text}\n")

        query = "What was my last question?"
        print(f"User: {query}")
        result = await agent.run(query, conversation_id=conversation_id)
        print(f"Agent: {result.text}\n")


async def example_with_thread() -> None:
    """This example shows how to specify existing conversation ID with AgentThread."""
    print("=== Azure AI Agent With Existing Conversation and Thread ===")
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
    ):
        provider = AzureAIProjectAgentProvider(project_client=project_client)
        agent = await provider.create_agent(
            name="BasicAgent",
            instructions="You are a helpful agent.",
            tools=get_weather,
        )

        # Create a conversation using OpenAI client
        openai_client = project_client.get_openai_client()
        conversation = await openai_client.conversations.create()
        conversation_id = conversation.id
        print(f"Conversation ID: {conversation_id}")

        # Create a thread with the existing ID
        thread = agent.get_new_thread(service_thread_id=conversation_id)

        query = "What's the weather like in Saskatoon?"
        print(f"User: {query}")
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result.text}\n")

        query = "What was my last question?"
        print(f"User: {query}")
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result.text}\n")


async def main() -> None:
    await example_with_conversation_id()
    await example_with_thread()


if __name__ == "__main__":
    asyncio.run(main())

# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import sys
from pathlib import Path

from agent_framework.azure import AzureAIProjectAgentProvider
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Add weather_tool to path and import real weather function
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent.parent / "weather_tool"))
from shared_utils import get_real_weather as get_weather

"""
Azure AI Agent Latest Version Example

This sample demonstrates how to reuse the latest version of an existing agent
instead of creating a new agent version on each instantiation. The first call creates a new agent,
while subsequent calls with `get_agent()` reuse the latest agent version.
"""


async def main() -> None:
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIProjectAgentProvider(credential=credential) as provider,
    ):
        # First call creates a new agent
        agent = await provider.create_agent(
            name="MyWeatherAgent",
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        )

        query = "What's the weather like in Seattle?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

        # Second call retrieves the existing agent (latest version) instead of creating a new one
        # This is useful when you want to reuse an agent that was created earlier
        agent2 = await provider.get_agent(
            name="MyWeatherAgent",
            tools=get_weather,  # Tools must be provided for function tools
        )

        query = "What's the weather like in Tokyo?"
        print(f"User: {query}")
        result = await agent2.run(query)
        print(f"Agent: {result}\n")

        print(f"First agent ID with version: {agent.id}")
        print(f"Second agent ID with version: {agent2.id}")


if __name__ == "__main__":
    asyncio.run(main())

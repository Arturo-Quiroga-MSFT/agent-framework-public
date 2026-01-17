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
Azure AI Agent with Explicit Settings Example

This sample demonstrates creating Azure AI Agents with explicit configuration
settings rather than relying on environment variable defaults.
"""


async def main() -> None:
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIProjectAgentProvider(
            project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            credential=credential,
        ) as provider,
    ):
        agent = await provider.create_agent(
            name="WeatherAgent",
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        )

        query = "What's the weather like in New York?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

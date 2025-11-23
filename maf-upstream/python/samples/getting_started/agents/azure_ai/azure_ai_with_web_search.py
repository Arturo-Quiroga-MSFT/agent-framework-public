# Copyright (c) Microsoft. All rights reserved.

import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from local azure_ai/.env first, then fall back to getting_started/.env
local_env_path = Path(__file__).parent / ".env"
parent_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=local_env_path)  # Load local first
load_dotenv(dotenv_path=parent_env_path)  # Then parent (won't override existing vars)

from agent_framework import HostedWebSearchTool
from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent With Web Search

This sample demonstrates basic usage of AzureAIClient to create an agent
that can perform web searches using the HostedWebSearchTool.

Pre-requisites:
- Make sure to set up the AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME
  environment variables before running this sample.
"""


async def main() -> None:
    # Since no Agent ID is provided, the agent will be automatically created.
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="WebsearchAgent",
            instructions="You are a helpful assistant that can search the web",
            tools=[HostedWebSearchTool()],
        ) as agent,
    ):
        query = "What's the weather today in Toronto?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

    """
    Sample output:
    User: What's the weather today in Toronto?
    Agent: Here is the updated weather forecast for Toronto: The current temperature is approximately 15°C,
           partly cloudy conditions, with moderate winds. Check out more details
           at the [Weather Network](https://www.theweathernetwork.com/ca/weather/ontario/toronto).
    """


if __name__ == "__main__":
    asyncio.run(main())

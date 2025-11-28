# Copyright (c) Microsoft. All rights reserved.
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from local azure_ai/.env first, then fall back to getting_started/.env
local_env_path = Path(__file__).parent / ".env"
parent_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=local_env_path)  # Load local first
load_dotenv(dotenv_path=parent_env_path)  # Then parent (won't override existing vars)

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent with Bing Grounding Example

This sample demonstrates usage of AzureAIClient with Bing Grounding
to search the web for current information and provide grounded responses.

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables.
2. Ensure you have a Bing connection configured in your Azure AI project
   and set BING_PROJECT_CONNECTION_ID environment variable.

To get your Bing connection ID:
- Go to Azure AI Foundry portal (https://ai.azure.com)
- Navigate to your project's "Connected resources" section
- Add a new connection for "Grounding with Bing Search"
- Copy the connection ID and set it as the BING_PROJECT_CONNECTION_ID environment variable
"""


async def main() -> None:
    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="MyBingGroundingAgent",
            instructions="""You are a helpful assistant that can search the web for current information.
            Use the Bing search tool to find up-to-date information and provide accurate, well-sourced answers.
            Always cite your sources when possible.""",
            tools={
                "type": "bing_grounding",
                "bing_grounding": {
                    "search_configurations": [
                        {
                            "project_connection_id": os.environ["BING_PROJECT_CONNECTION_ID"],
                        }
                    ]
                },
            },
        ) as agent,
    ):
        query = "What is today's date and weather in Toronto?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

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
Azure AI Agent with Bing Custom Search Example

This sample demonstrates usage of AzureAIClient with Bing Custom Search
to search custom search instances and provide responses with relevant results.

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables.
2. Ensure you have a Bing Custom Search connection configured in your Azure AI project
   and set BING_CUSTOM_SEARCH_PROJECT_CONNECTION_ID and BING_CUSTOM_SEARCH_INSTANCE_NAME environment variables.
"""


async def main() -> None:
    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="MyCustomSearchAgent",
            instructions="""You are a helpful agent that can use Bing Custom Search tools to assist users.
            Use the available Bing Custom Search tools to answer questions and perform tasks.""",
            tools={
                "type": "bing_custom_search_preview",
                "bing_custom_search_preview": {
                    "search_configurations": [
                        {
                            "project_connection_id": os.environ["BING_CUSTOM_SEARCH_PROJECT_CONNECTION_ID"],
                            "instance_name": os.environ["BING_CUSTOM_SEARCH_INSTANCE_NAME"],
                        }
                    ]
                },
            },
        ) as agent,
    ):
        query = "Tell me more about foundry agent service"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

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
Azure AI Agent with Microsoft Fabric Example

This sample demonstrates usage of AzureAIClient with Microsoft Fabric
to query Fabric data sources and provide responses based on data analysis.

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables.
2. Ensure you have a Microsoft Fabric connection configured in your Azure AI project
   and set FABRIC_PROJECT_CONNECTION_ID environment variable.
"""


async def main() -> None:
    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="MyFabricAgent",
            instructions="You are a helpful assistant.",
            tools={
                "type": "fabric_dataagent_preview",
                "fabric_dataagent_preview": {
                    "project_connections": [
                        {
                            "project_connection_id": os.environ["FABRIC_PROJECT_CONNECTION_ID"],
                        }
                    ]
                },
            },
        ) as agent,
    ):
        query = "Tell me about sales records"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

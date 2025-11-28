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
Azure AI Agent with SharePoint Example

This sample demonstrates usage of AzureAIClient with SharePoint
to search through SharePoint content and answer user questions about it.

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables.
2. Ensure you have a SharePoint connection configured in your Azure AI project
    and set SHAREPOINT_PROJECT_CONNECTION_ID environment variable.
"""


async def main() -> None:
    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="MySharePointAgent",
            instructions="""You are a helpful agent that can use SharePoint tools to assist users.
            Use the available SharePoint tools to answer questions and perform tasks.""",
            tools={
                "type": "sharepoint_grounding_preview",
                "sharepoint_grounding_preview": {
                    "project_connection_id": os.environ["SHAREPOINT_PROJECT_CONNECTION_ID"]
                },
            },
        ) as agent,
    ):
        query = "What is Contoso whistleblower policy?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())

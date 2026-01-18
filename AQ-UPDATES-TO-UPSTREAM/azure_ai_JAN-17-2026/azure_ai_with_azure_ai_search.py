# Copyright (c) Microsoft. All rights reserved.
import asyncio
import os
from pathlib import Path
import re

from agent_framework.azure import AzureAIProjectAgentProvider
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

"""
Azure AI Agent with Azure AI Search Example

This sample demonstrates usage of AzureAIProjectAgentProvider with Azure AI Search
to search through indexed data and answer user questions about it.

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables.
2. Ensure you have an Azure AI Search connection configured in your Azure AI project
    and set AI_SEARCH_PROJECT_CONNECTION_ID and AI_SEARCH_INDEX_NAME environment variable.
"""


def _normalize_citations(text: str) -> str:
    # Some models emit citations using full-width brackets like: .
    # Normalize to the requested ASCII format: [5:0†source].
    return re.sub(r"【([^】]+)】", r"[\1]", text)


async def main() -> None:
    async with (
        AzureCliCredential() as credential,
        AzureAIProjectAgentProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="MySearchAgent",
            instructions="""You are a helpful assistant.

You must ALWAYS call the Azure AI Search tool before answering.

Only answer using information returned by the tool. If the tool returns no relevant results, say you don't have
enough information in the connected search index to answer.

Every answer MUST include at least one citation rendered using ASCII brackets exactly like:
[message_idx:search_idx†source]
(do not use other bracket styles).""",
            tools={
                "type": "azure_ai_search",
                "azure_ai_search": {
                    "indexes": [
                        {
                            "project_connection_id": os.environ["AI_SEARCH_PROJECT_CONNECTION_ID"],
                            "index_name": os.environ["AI_SEARCH_INDEX_NAME"],
                            # For query_type=vector, ensure your index has a field with vectorized data.
                            "query_type": "simple",
                        }
                    ]
                },
            },
        )

        query = "According to the HR handbook in the search index, what insurance options are offered?"
        print(f"User: {query}")
        result = await agent.run(query)
    text = getattr(result, "text", str(result))
    print(f"Result: {_normalize_citations(text)}\n")


if __name__ == "__main__":
    asyncio.run(main())

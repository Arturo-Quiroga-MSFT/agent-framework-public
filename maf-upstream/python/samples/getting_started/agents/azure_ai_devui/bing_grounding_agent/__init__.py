"""
Azure AI Agent: Bing Grounding Agent

Demonstrates web search with Bing Grounding for current information with citations.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from agent_framework.azure import AzureAIClient
from agent_framework.observability import setup_observability
from azure.identity.aio import AzureCliCredential

# Load environment variables
local_env_path = Path(__file__).parent.parent.parent / "azure_ai" / ".env"
parent_env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=local_env_path)
load_dotenv(dotenv_path=parent_env_path)

# Setup observability for tracing
if os.getenv("ENABLE_OTEL", "").lower() == "true":
    app_insights_conn = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn:
        setup_observability(
            enable_sensitive_data=os.getenv("ENABLE_SENSITIVE_DATA", "").lower() == "true",
            applicationinsights_connection_string=app_insights_conn,
        )

# Create the agent
credential = AzureCliCredential()

# Get Bing connection ID (use BING_CONNECTION_ID or BING_PROJECT_CONNECTION_ID)
bing_connection_id = os.getenv("BING_CONNECTION_ID") or os.getenv("BING_PROJECT_CONNECTION_ID")

if not bing_connection_id:
    raise ValueError(
        "BING_CONNECTION_ID not found in environment variables. "
        "Configure Bing Grounding connection in Azure AI Foundry portal."
    )

agent = AzureAIClient(async_credential=credential).create_agent(
    name="BingGroundingAgent",
    description=(
        "Bing Grounding Agent - Enterprise Search with Citations\n"
        "\n"
        "Microsoft Bing-powered search with SOURCE CITATIONS and grounding.\n"
        "Ideal for enterprise scenarios requiring transparency and attribution.\n"
        "\n"
        "TRY THESE:\n"
        "  • What are the latest AI developments?\n"
        "  • Tell me about recent Microsoft Azure announcements\n"
        "  • What's the current weather in Mexico City?\n"
        "  • Find information about Agent Framework\n"
        "  • What are today's top technology news?\n"
        "\n"
        "FEATURES:\n"
        "  • ✨ Grounded answers with SOURCE CITATIONS\n"
        "  • Official Microsoft Bing integration\n"
        "  • Enterprise-grade with attribution\n"
        "  • Azure AI Foundry connection\n"
        "  • Compliance & audit ready\n"
        "\n"
        "KEY DIFFERENCE: Unlike generic web search, provides verifiable sources."
    ),
    instructions=(
        "You are a helpful assistant that can search the web for current information. "
        "Use the Bing search tool to find up-to-date information and provide accurate, well-sourced answers. "
        "Always cite your sources when possible."
    ),
    tools={
        "type": "bing_grounding",
        "bing_grounding": {
            "search_configurations": [
                {
                    "project_connection_id": bing_connection_id,
                }
            ]
        },
    },
)

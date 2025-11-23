"""
Azure AI Agent: Web Search Agent

Demonstrates web search capabilities using Bing Grounding.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from agent_framework import HostedWebSearchTool
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

agent = AzureAIClient(async_credential=credential).create_agent(
    name="WebSearchAgent",
    description=(
        "Web Search Agent - Generic Hosted Search\n"
        "\n"
        "Quick web search using hosted search tool (framework-provided).\n"
        "\n"
        "TRY THESE:\n"
        "  • What are the latest AI news?\n"
        "  • Tell me about recent Microsoft announcements\n"
        "  • What's trending in technology today?\n"
        "  • Find information about Azure AI services\n"
        "\n"
        "FEATURES:\n"
        "  • Real-time web search\n"
        "  • Generic hosted tool\n"
        "  • Simple implementation\n"
        "  • Current events and news\n"
        "\n"
        "NOTE: For enterprise scenarios with source citations, use BingGroundingAgent instead."
    ),
    instructions="You are a helpful assistant that can search the web for current information.",
    tools=[HostedWebSearchTool()],
)

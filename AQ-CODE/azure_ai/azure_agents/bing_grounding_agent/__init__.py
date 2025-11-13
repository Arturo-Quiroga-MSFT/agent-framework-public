"""
Azure AI Agent: Bing Web Search Assistant

Demonstrates Azure AI Agent with Bing Grounding for real-time web search.
Requires Bing Search connection configured in Azure AI project.
"""

import os
from pathlib import Path

from agent_framework import HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables - go up to azure_ai/ directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check required environment variables
project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

if not project_endpoint:
    raise ValueError("AZURE_AI_PROJECT_ENDPOINT not found in environment")

if not os.getenv("BING_CONNECTION_ID"):
    raise ValueError(
        "BING_CONNECTION_ID not found in environment. "
        "Please configure Bing Grounding in Azure AI Foundry portal."
    )

# Create Bing Grounding search tool
bing_search_tool = HostedWebSearchTool(
    name="BingGroundingSearch",
    description="Search the web for current information using Bing",
)

# Create Azure AI Agent with Bing search
credential = DefaultAzureCredential()

agent = AzureAIAgentClient(
    project_endpoint=project_endpoint,
    model_deployment_name=model_deployment_name,
    async_credential=credential
).create_agent(
    name="BingSearchAgent",
    description=(
        "AZURE AI DEMO: Bing Web Search Assistant\n"
        "\n"
        "Shows Azure AI Agent with Bing Grounding for real-time web information.\n"
        "\n"
        "TRY THESE QUERIES:\n"
        "  • What are the latest news about AI?\n"
        "  • Who won the most recent NBA championship?\n"
        "  • What's trending on social media today?\n"
        "  • Find information about recent tech announcements.\n"
        "  • What are the current stock prices for Microsoft?\n"
        "\n"
        "FEATURES:\n"
        "  • Real-time web search using Bing\n"
        "  • Access to current information and news\n"
        "  • Grounded answers with source citations\n"
        "  • Up-to-date facts and data\n"
        "\n"
        "REQUIREMENTS:\n"
        "  • Bing Search connection configured in Azure AI project\n"
        "  • BING_CONNECTION_ID environment variable set"
    ),
    instructions=(
        "You are a helpful assistant that can search the web for current information. "
        "Use the Bing search tool to find up-to-date information and provide accurate, "
        "well-sourced answers. Always cite your sources when possible."
    ),
    tools=bing_search_tool,
)

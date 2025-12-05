"""
Research Agent - Real-time web search and fact-checking

Uses Bing Search (HostedWebSearchTool) for finding current information,
fact-checking, and researching topics with proper source citations.
"""

import os
from pathlib import Path

from agent_framework import HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check required environment variables
project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

if not project_endpoint:
    raise ValueError("AZURE_AI_PROJECT_ENDPOINT not found in environment")

# Create Web Search tool
web_search_tool = HostedWebSearchTool(
    name="Bing Search",
    description="Search the web for current information, news, and facts using Bing"
)

# Create Azure AI Agent with Web Search
credential = DefaultAzureCredential()

agent = AzureAIAgentClient(
    project_endpoint=project_endpoint,
    model_deployment_name=model_deployment_name,
    async_credential=credential
).create_agent(
    name="ResearchAgent",
    description=(
        "Research Agent - Real-time Information Gathering\n"
        "\n"
        "Searches the web for current information and provides sourced answers.\n"
        "\n"
        "TRY THESE:\n"
        "  • What are the latest developments in quantum computing?\n"
        "  • Find the current stock price of Microsoft\n"
        "  • What's the weather like in Paris today?\n"
        "  • Who won the most recent Nobel Prize in Physics?\n"
        "  • What are the top technology trends in 2024?\n"
        "\n"
        "FEATURES:\n"
        "  • Real-time web search\n"
        "  • Current news and events\n"
        "  • Fact-checking with sources\n"
        "  • Market data and statistics\n"
        "  • Comprehensive research summaries\n"
        "\n"
        "TOOLS:\n"
        "  • Bing Search: Real-time web search with source citations\n"
    ),
    instructions=(
        "You are a research assistant that can search the web for current information. "
        "Always use the Bing Search tool to find up-to-date information. "
        "Provide clear, well-organized answers with proper source citations. "
        "When presenting multiple sources, synthesize the information coherently. "
        "If information conflicts, note the discrepancies and their sources."
    ),
    tools=web_search_tool,
)

# Export the agent
__all__ = ["agent"]

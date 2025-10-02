# Copyright (c) Microsoft. All rights reserved.
"""Sample Bing search agent for Agent Framework Debug UI."""

import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from agent_framework import ChatAgent, HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity import DefaultAzureCredential

# Load environment variables from .env file in the samples directory
load_dotenv(Path(__file__).parent.parent / ".env")


def get_current_news(
    topic: Annotated[str, "The topic to search for current news about"],
    region: Annotated[str, "The region to focus the news search on"] = "global",
) -> str:
    """Get current news about a specific topic."""
    # This is a placeholder function that would normally call a news API
    # In the actual implementation, this would be handled by the HostedWebSearchTool
    return f"Here are the latest news articles about {topic} in {region}. [This would be enhanced by web search tool]"


def search_web_info(
    query: Annotated[str, "The search query to look up current information"],
    search_type: Annotated[str, "Type of search: 'general', 'news', 'academic'"] = "general",
) -> str:
    """Search the web for current information on any topic."""
    # This is a placeholder function - the actual web search is handled by HostedWebSearchTool
    return f"Web search results for '{query}' (type: {search_type}). [Enhanced by Bing search integration]"


# Create the Bing search tool
bing_search_tool = HostedWebSearchTool(
    name="Bing Grounding Search",
    description="Search the web for current information using Bing",
)

# Agent instance following Agent Framework conventions
agent = ChatAgent(
    name="BingSearchAgent",
    description="An intelligent agent that can search the web for current information using Bing",
    instructions="""
    You are a web research assistant with access to current information through Bing search.
    
    Your capabilities:
    - Search the web for current, up-to-date information on any topic
    - Find recent news articles and developments
    - Look up facts, statistics, and current events
    - Provide well-sourced, accurate answers with citations when possible
    
    Guidelines:
    - Always use the web search tool when users ask for current information
    - Cite your sources when providing information from search results
    - Be clear about when information comes from search vs. your training data
    - If search results are unclear, ask clarifying questions
    - Provide comprehensive but concise answers
    """,
    chat_client=AzureAIAgentClient(
        async_credential=DefaultAzureCredential(),
        # These will be picked up from environment variables or Azure CLI
        project_endpoint=os.environ.get("AZURE_AI_PROJECT_ENDPOINT", ""),
        model_deployment_name=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", ""),
    ),
    tools=[bing_search_tool, get_current_news, search_web_info],
)


def main():
    """Launch the Bing search agent in DevUI."""
    import logging

    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Bing Search Agent")
    logger.info("Available at: http://localhost:8090")
    logger.info("Entity ID: agent_BingSearchAgent")
    logger.info("")
    logger.info("This agent can search the web for current information using Bing.")
    logger.info("Try asking questions like:")
    logger.info("  - What's the latest news about AI?")
    logger.info("  - What's the weather in Paris today?")
    logger.info("  - Who won the Nobel Prize this year?")
    logger.info("  - What are the current stock prices for major tech companies?")

    # Launch server with the agent
    serve(entities=[agent], port=8090, auto_open=True)


if __name__ == "__main__":
    main()
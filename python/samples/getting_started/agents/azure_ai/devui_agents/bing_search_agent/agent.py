# Copyright (c) Microsoft. All rights reserved.
"""Bing search agent for DevUI - Azure AI version with web search capabilities."""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Load environment variables from parent .env file
load_dotenv(Path(__file__).parent.parent.parent / ".env")


# For DevUI discovery, we need to create a lazy-loading agent factory
# This avoids the asyncio.run() issue during module import
class BingSearchAgentFactory:
    """Factory for creating the Bing search agent lazily."""
    
    def __init__(self):
        self._agent = None
        self._credential = None
        self._client = None
        self._bing_tool = None
    
    async def _create_agent(self):
        """Actually create the agent (async)."""
        if self._agent is not None:
            return self._agent
        
        # Initialize async credential
        self._credential = AzureCliCredential()
        
        # Initialize Azure AI client with async credential
        self._client = AzureAIAgentClient(
            async_credential=self._credential,
            project_endpoint=os.environ.get("AZURE_AI_PROJECT_ENDPOINT"),
            model_deployment_name=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        )
        
        # Create Bing Grounding search tool
        self._bing_tool = HostedWebSearchTool(
            name="BingGroundingSearch",
            description="Search the web for current information using Bing",
        )
        
        # Create agent with the client and search tool
        self._agent = await self._client.create_agent(
            name="BingSearchAgent",
            instructions="""
            You are a helpful research assistant with access to real-time web search through Bing.
            
            Your capabilities:
            - Search the web for current, up-to-date information
            - Find recent news and current events
            - Look up facts that may have changed recently
            - Research topics requiring fresh information
            
            Guidelines:
            - Use the search tool when asked about current events or recent information
            - Cite your sources and mention where information comes from
            - Be clear when information is from web search vs. training data
            - Provide well-organized, informative responses
            """,
            tools=self._bing_tool,
        )
        
        return self._agent
    
    async def __call__(self, *args, **kwargs):
        """Make the factory callable like an agent."""
        agent = await self._create_agent()
        return await agent(*args, **kwargs)
    
    def run(self, *args, **kwargs):
        """Run method for DevUI compatibility."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, create one
            return asyncio.run(self._run_async(*args, **kwargs))
        else:
            # Event loop is running, create a task
            return asyncio.create_task(self._run_async(*args, **kwargs))
    
    async def _run_async(self, *args, **kwargs):
        """Async implementation of run."""
        agent = await self._create_agent()
        return await agent.run(*args, **kwargs)
    
    def run_stream(self, *args, **kwargs):
        """Run stream method for DevUI compatibility."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            raise RuntimeError("run_stream requires an existing event loop")
        
        return self._run_stream_async(*args, **kwargs)
    
    async def _run_stream_async(self, *args, **kwargs):
        """Async implementation of run_stream."""
        agent = await self._create_agent()
        async for update in agent.run_stream(*args, **kwargs):
            yield update
    
    @property
    def name(self):
        """Agent name for DevUI."""
        return "BingSearchAgent"
    
    @property
    def display_name(self):
        """Display name for DevUI."""
        return "Bing Search Agent"
    
    @property
    def description(self):
        """Agent description for DevUI."""
        return "A research assistant with real-time web search capabilities using Bing Grounding"
    
    async def cleanup(self):
        """Clean up resources."""
        if self._agent:
            try:
                await self._agent.__aexit__(None, None, None)
            except Exception:
                pass
            self._agent = None
        
        if self._client:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception:
                pass
            self._client = None
        
        if self._credential:
            try:
                await self._credential.__aexit__(None, None, None)
            except Exception:
                pass
            self._credential = None


# Export the factory instance as 'agent' for DevUI discovery
agent = BingSearchAgentFactory()


def main():
    """Launch the Bing search agent in DevUI."""
    import logging

    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Azure AI Bing Search Agent")
    logger.info("Available at: http://localhost:8091")
    logger.info("Entity ID: agent_BingSearchAgent")

    # Launch server with the agent factory
    serve(entities=[agent], port=8091, auto_open=True)


if __name__ == "__main__":
    main()

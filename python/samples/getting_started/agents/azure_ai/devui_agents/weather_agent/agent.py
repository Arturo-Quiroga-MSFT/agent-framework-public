# Copyright (c) Microsoft. All rights reserved.
"""Weather agent for DevUI - Azure AI version with real weather data support."""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Load environment variables from parent .env file
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Add parent directory to path to import shared_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared_utils import get_real_weather, get_mock_weather


# For DevUI discovery, we need to create a lazy-loading agent factory
# This avoids the asyncio.run() issue during module import
class WeatherAgentFactory:
    """Factory for creating the weather agent lazily."""
    
    def __init__(self):
        self._agent = None
        self._credential = None
        self._client = None
    
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
        
        # Determine which weather function to use
        has_api_key = bool(os.environ.get("OPENWEATHER_API_KEY"))
        weather_function = get_real_weather if has_api_key else get_mock_weather
        weather_type = "real-time" if has_api_key else "mock"
        
        # Create agent with the client
        self._agent = await self._client.create_agent(
            name="WeatherAgent",
            instructions=f"""
            You are a helpful weather assistant. You can provide weather information
            for any location using the weather tool.
            
            Note: You are currently using {weather_type} weather data.
            
            Guidelines:
            - Always be friendly and informative
            - When users ask about weather, use the tool to get the information
            - Present the weather information in a clear, easy-to-read format
            - If asked about multiple locations, check each one
            """,
            tools=weather_function,
        )
        
        return self._agent
    
    async def __call__(self, *args, **kwargs):
        """Make the factory callable like an agent."""
        agent = await self._create_agent()
        return await agent(*args, **kwargs)
    
    def run(self, *args, **kwargs):
        """Delegate run to the actual agent."""
        async def _run():
            agent = await self._create_agent()
            return await agent.run(*args, **kwargs)
        
        # Check if we're in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, create a task
            return asyncio.create_task(_run())
        except RuntimeError:
            # No event loop, use asyncio.run
            return asyncio.run(_run())
    
    def run_stream(self, *args, **kwargs):
        """Delegate run_stream to the actual agent."""
        async def _run_stream():
            agent = await self._create_agent()
            async for chunk in agent.run_stream(*args, **kwargs):
                yield chunk
        
        return _run_stream()
    
    @property
    def name(self):
        """Return the agent name."""
        return "WeatherAgent"
    
    @property
    def description(self):
        """Return the agent description."""
        return "A helpful weather agent that provides weather information for any location"
    
    async def cleanup(self):
        """Clean up resources."""
        if self._agent:
            await self._agent.__aexit__(None, None, None)
        if self._client:
            await self._client.__aexit__(None, None, None)
        if self._credential:
            await self._credential.__aexit__(None, None, None)


# Export the factory as 'agent' for DevUI discovery
agent = WeatherAgentFactory()


def main():
    """Launch the weather agent in DevUI."""
    import logging

    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Azure AI Weather Agent")
    logger.info("Available at: http://localhost:8090")
    logger.info("Entity ID: agent_WeatherAgent")

    # Launch server with the agent factory
    serve(entities=[agent], port=8090, auto_open=True)


if __name__ == "__main__":
    main()

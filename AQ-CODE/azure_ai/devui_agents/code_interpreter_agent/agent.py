# Copyright (c) Microsoft. All rights reserved.
"""Code interpreter agent for DevUI - Azure AI version with Python code execution."""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import HostedCodeInterpreterTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Load environment variables from parent .env file
load_dotenv(Path(__file__).parent.parent.parent / ".env")


# For DevUI discovery, we need to create a lazy-loading agent factory
# This avoids the asyncio.run() issue during module import
class CodeInterpreterAgentFactory:
    """Factory for creating the code interpreter agent lazily."""
    
    def __init__(self):
        self._agent = None
        self._credential = None
        self._client = None
        self._code_tool = None
    
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
        
        # Create Code Interpreter tool
        self._code_tool = HostedCodeInterpreterTool()
        
        # Create agent with the client and code interpreter tool (not awaitable)
        self._agent = self._client.create_agent(
            name="CodeInterpreterAgent",
            instructions="""
            You are an expert programming assistant with access to a Python code interpreter.
            
            Your capabilities:
            - Write and execute Python code to solve complex problems
            - Perform data analysis and create visualizations
            - Implement algorithms and mathematical computations
            - Debug and optimize code
            - Explain your code and approach clearly
            
            Guidelines:
            - Always show your code before executing it
            - Explain your approach and reasoning
            - Break down complex problems into steps
            - Provide well-commented, clean code
            - Use appropriate data structures and algorithms
            - Create visualizations when helpful
            - Handle edge cases and errors gracefully
            """,
            tools=self._code_tool,
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
        return "CodeInterpreterAgent"
    
    @property
    def display_name(self):
        """Display name for DevUI."""
        return "Code Interpreter Agent"
    
    @property
    def description(self):
        """Agent description for DevUI."""
        return "An expert programming assistant with Python code execution capabilities"
    
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
agent = CodeInterpreterAgentFactory()


def main():
    """Launch the code interpreter agent in DevUI."""
    import logging

    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Azure AI Code Interpreter Agent")
    logger.info("Available at: http://localhost:8092")
    logger.info("Entity ID: agent_CodeInterpreterAgent")

    # Launch server with the agent factory
    serve(entities=[agent], port=8092, auto_open=True)


if __name__ == "__main__":
    main()

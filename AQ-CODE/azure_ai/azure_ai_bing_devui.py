# Copyright (c) Microsoft. All rights reserved.

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from agent_framework import ChatAgent, HostedWebSearchTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Load environment variables from .env file in the current directory
load_dotenv(Path(__file__).parent / ".env")

"""
Azure AI Agent with Bing Grounding - DEVUI Compatible Version

This module provides a DEVUI-compatible interface for creating and using Azure AI agents
with Bing Grounding search capabilities. Designed for interactive use in development
environments and UI tools.

Prerequisites:
1. A connected Grounding with Bing Search resource in your Azure AI project
2. BING_CONNECTION_ID environment variable set in .env file
3. AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME configured

Usage:
    agent_manager = AzureAIBingAgent()
    await agent_manager.initialize()
    response = await agent_manager.search_and_chat("What's the weather like today?")
    await agent_manager.cleanup()
"""


class AzureAIBingAgent:
    """
    DEVUI-compatible Azure AI Agent with Bing search capabilities.
    
    This class provides a structured interface for creating and managing
    Azure AI agents with web search functionality, suitable for use in
    development UI tools and interactive environments.
    """
    
    def __init__(self):
        """Initialize the Azure AI Bing Agent manager."""
        self.client: Optional[AzureAIAgentClient] = None
        self.agent: Optional[ChatAgent] = None
        self.credential: Optional[AzureCliCredential] = None
        self.bing_search_tool: Optional[HostedWebSearchTool] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the Azure AI client and agent with Bing search capabilities.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            # Initialize Azure CLI credential
            self.credential = AzureCliCredential()
            
            # Create Bing Grounding search tool
            self.bing_search_tool = HostedWebSearchTool(
                name="Bing Grounding Search",
                description="Search the web for current information using Bing",
            )
            
            # Initialize Azure AI client
            self.client = AzureAIAgentClient(async_credential=self.credential)
            
            # Create the chat agent with web search capabilities
            self.agent = ChatAgent(
                chat_client=self.client,
                name="BingSearchAgent",
                instructions=(
                    "You are a helpful assistant that can search the web for current information. "
                    "Use the Bing search tool to find up-to-date information and provide accurate, "
                    "well-sourced answers. Always cite your sources when possible. "
                    "Be concise but thorough in your responses."
                ),
                tools=self.bing_search_tool,
            )
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing Azure AI Bing Agent: {e}")
            return False
    
    async def search_and_chat(self, query: str) -> str:
        """
        Send a query to the agent with web search capabilities.
        
        Args:
            query (str): The user's question or request.
            
        Returns:
            str: The agent's response with web search results.
            
        Raises:
            RuntimeError: If the agent is not initialized.
        """
        if not self._initialized or not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        try:
            response = await self.agent.run(query)
            return response.text
        except Exception as e:
            return f"Error processing query: {e}"
    
    async def chat_without_search(self, query: str) -> str:
        """
        Send a query to the agent without using web search (for comparison).
        
        Args:
            query (str): The user's question or request.
            
        Returns:
            str: The agent's response without web search.
            
        Raises:
            RuntimeError: If the client is not initialized.
        """
        if not self._initialized or not self.client:
            raise RuntimeError("Client not initialized. Call initialize() first.")
        
        try:
            # Create a temporary agent without search tools
            async with ChatAgent(
                chat_client=self.client,
                name="BasicAgent", 
                instructions="You are a helpful assistant. Answer based on your training data only.",
            ) as basic_agent:
                response = await basic_agent.run(query)
                return response.text
        except Exception as e:
            return f"Error processing query without search: {e}"
    
    async def get_agent_info(self) -> dict:
        """
        Get information about the current agent configuration.
        
        Returns:
            dict: Agent configuration and status information.
        """
        return {
            "initialized": self._initialized,
            "has_client": self.client is not None,
            "has_agent": self.agent is not None,
            "has_search_tool": self.bing_search_tool is not None,
            "agent_name": "BingSearchAgent" if self.agent else None,
            "search_tool_name": "Bing Grounding Search" if self.bing_search_tool else None,
        }
    
    async def test_connection(self) -> bool:
        """
        Test the connection to Azure AI services.
        
        Returns:
            bool: True if connection is working, False otherwise.
        """
        if not self._initialized:
            return False
        
        try:
            response = await self.search_and_chat("Hello, can you hear me?")
            return len(response) > 0
        except Exception:
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources and close connections."""
        if self.agent:
            try:
                await self.agent.__aexit__(None, None, None)
            except Exception:
                pass
            self.agent = None
        
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception:
                pass
            self.client = None
        
        if self.credential:
            try:
                await self.credential.__aexit__(None, None, None)
            except Exception:
                pass
            self.credential = None
        
        self.bing_search_tool = None
        self._initialized = False


# DEVUI Helper Functions
async def create_agent() -> AzureAIBingAgent:
    """
    DEVUI helper: Create and initialize a new Azure AI Bing Agent.
    
    Returns:
        AzureAIBingAgent: Initialized agent ready for use.
    """
    agent = AzureAIBingAgent()
    success = await agent.initialize()
    if not success:
        raise RuntimeError("Failed to initialize Azure AI Bing Agent")
    return agent


async def quick_search(query: str) -> str:
    """
    DEVUI helper: Quick search function for one-off queries.
    
    Args:
        query (str): Search query.
        
    Returns:
        str: Search response.
    """
    agent = await create_agent()
    try:
        response = await agent.search_and_chat(query)
        return response
    finally:
        await agent.cleanup()


# Example usage for DEVUI
async def demo_usage():
    """Demonstrate usage patterns for DEVUI integration."""
    print("=== Azure AI Bing Agent - DEVUI Demo ===\n")
    
    # Method 1: Using the class directly
    agent = AzureAIBingAgent()
    
    if await agent.initialize():
        print("✅ Agent initialized successfully")
        
        # Get agent info
        info = await agent.get_agent_info()
        print(f"Agent info: {info}")
        
        # Test connection
        if await agent.test_connection():
            print("✅ Connection test passed")
        
        # Example queries
        queries = [
            "What's the latest news about AI?",
            "Who won the Nobel Prize in Physics this year?",
            "What's the current weather in Seattle?"
        ]
        
        for query in queries:
            print(f"\n🔍 Query: {query}")
            response = await agent.search_and_chat(query)
            print(f"📝 Response: {response[:200]}..." if len(response) > 200 else f"📝 Response: {response}")
        
        await agent.cleanup()
        print("\n✅ Agent cleaned up successfully")
    
    else:
        print("❌ Failed to initialize agent")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_usage())
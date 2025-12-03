# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import httpx
from datetime import datetime
from typing import Any, Annotated
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
local_env_path = Path(__file__).parent / ".env"
parent_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=local_env_path)
load_dotenv(dotenv_path=parent_env_path)

# ============================================================================
# WORKAROUND for azure-ai-projects 2.0.0b2 gzip encoding bug
# GitHub Issue: https://github.com/microsoft/agent-framework/issues/2457
# This patches the Azure SDK to disable compressed responses which cause
# UnicodeDecodeError when the SDK tries to decode gzip bytes as UTF-8
# ============================================================================
import azure.core.pipeline.policies as policies
_original_on_request = policies.HeadersPolicy.on_request
def _patched_on_request(self, request):
    _original_on_request(self, request)
    request.http_request.headers['Accept-Encoding'] = 'identity'
policies.HeadersPolicy.on_request = _patched_on_request
# ============================================================================

from agent_framework import (
    AgentProtocol,
    AgentThread,
    ChatAgent,
    HostedMCPTool,
    HostedWebSearchTool,
)
from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent with Multiple Tools Example (V2 API)

This sample demonstrates integrating multiple tool types with Azure AI Agents V2:
- Real function tools (weather, news, calculations)
- Hosted MCP tools (Microsoft Learn documentation)
- Hosted Web Search tools (Bing search)
- User approval workflows for function call security

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT environment variable
2. Run 'az login' for authentication
3. Optional: Set OPENWEATHER_API_KEY for weather data
4. Optional: Set NEWS_API_KEY for news headlines
5. Optional: Set BING_CONNECTION_ID for web search
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the current weather for a given location using OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather API key not configured. Set OPENWEATHER_API_KEY to enable this feature."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        return (
            f"Weather in {location}: {description.title()}\n"
            f"Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"Humidity: {humidity}%"
        )
    except Exception as e:
        return f"Error fetching weather: {str(e)}"


def get_news_headlines(
    category: Annotated[str, Field(description="News category: business, technology, science, health, sports, entertainment")] = "technology",
    country: Annotated[str, Field(description="Two-letter country code (e.g., us, gb, ca)")] = "us",
) -> str:
    """Get top news headlines from NewsAPI.org."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "News API key not configured. Get one free at https://newsapi.org/register"
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?category={category}&country={country}&apiKey={api_key}"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "ok" or not data["articles"]:
            return f"No {category} news found for {country.upper()}"
        
        headlines = []
        for i, article in enumerate(data["articles"][:5], 1):
            title = article["title"]
            source = article["source"]["name"]
            url = article["url"]
            headlines.append(f"{i}. {title} ({source})\n   {url}")
        
        return f"Top {category.title()} Headlines ({country.upper()}):\n\n" + "\n\n".join(headlines)
    except Exception as e:
        return f"Error fetching news: {str(e)}"


def calculate(
    expression: Annotated[str, Field(description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5 + 3')")],
) -> str:
    """Safely evaluate mathematical expressions."""
    try:
        # Safe evaluation - only allow basic math operations
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters. Only numbers and +, -, *, /, (, ) are allowed."
        
        # Evaluate safely
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error calculating: {str(e)}"


def get_time_info() -> str:
    """Get current UTC time and date information."""
    now = datetime.utcnow()
    return (
        f"Current UTC Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Day of Week: {now.strftime('%A')}\n"
        f"Week Number: {now.strftime('%W')}\n"
        f"Day of Year: {now.strftime('%j')}"
    )


def get_system_info() -> str:
    """Get basic system information."""
    import platform
    import sys
    
    return (
        f"Python Version: {sys.version.split()[0]}\n"
        f"Platform: {platform.system()} {platform.release()}\n"
        f"Architecture: {platform.machine()}\n"
        f"Processor: {platform.processor() or 'Unknown'}"
    )


async def handle_approvals_with_thread(query: str, agent: "AgentProtocol", thread: "AgentThread"):
    """Handle function call approvals in a loop with user interaction."""
    from agent_framework import ChatMessage

    result = await agent.run(query, thread=thread, store=True)
    
    while len(result.user_input_requests) > 0:
        new_input: list[Any] = []
        
        for user_input_needed in result.user_input_requests:
            func_name = user_input_needed.function_call.name
            func_args = user_input_needed.function_call.arguments
            
            print(f"\n🔔 Function Call Request:")
            print(f"   Function: {func_name}")
            print(f"   Arguments: {func_args}")
            
            # Auto-approve for demo purposes (in production, ask user)
            # user_approval = input("   Approve? (y/n): ").strip().lower()
            user_approval = "y"  # Auto-approve for demo
            print(f"   Auto-approved: yes\n")
            
            approved = user_approval == "y"
            new_input.append(
                ChatMessage(
                    role="user",
                    contents=[user_input_needed.create_response(approved)],
                )
            )
        
        result = await agent.run(new_input, thread=thread, store=True)
    
    return result


async def example_with_function_tools() -> None:
    """Example using only function tools."""
    print("=" * 80)
    print("Example 1: Function Tools Only")
    print("=" * 80)
    
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIClient(async_credential=credential),
            name="FunctionToolsAgent",
            instructions=(
                "You are a helpful assistant with access to weather, news, calculations, "
                "time, and system information. Use the appropriate tools to answer questions."
            ),
            tools=[get_weather, get_news_headlines, calculate, get_time_info, get_system_info],
        ) as agent,
    ):
        thread = agent.get_new_thread()
        
        # Query 1: Weather
        query1 = "What's the weather in San Francisco?"
        print(f"\nUser: {query1}")
        result1 = await handle_approvals_with_thread(query1, agent, thread)
        print(f"Agent: {result1}\n")
        
        # Query 2: Calculation
        query2 = "What's 15% of 250?"
        print(f"User: {query2}")
        result2 = await handle_approvals_with_thread(query2, agent, thread)
        print(f"Agent: {result2}\n")


async def example_with_hosted_mcp() -> None:
    """Example using Hosted MCP tools for Microsoft Learn documentation."""
    print("=" * 80)
    print("Example 2: Hosted MCP Tool (Microsoft Learn)")
    print("=" * 80)
    
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIClient(async_credential=credential),
            name="MCPDocsAgent",
            instructions=(
                "You are a helpful assistant that can search Microsoft Learn documentation. "
                "Use the MCP tool to find accurate, up-to-date information from official docs."
            ),
            tools=[
                HostedMCPTool(
                    name="Microsoft Learn MCP",
                    url="https://learn.microsoft.com/api/mcp",
                ),
                get_time_info,  # Also include a function tool
            ],
        ) as agent,
    ):
        thread = agent.get_new_thread()
        
        query = "How do I create an Azure Storage account using Azure CLI? Also tell me what time it is."
        print(f"\nUser: {query}")
        result = await handle_approvals_with_thread(query, agent, thread)
        print(f"Agent: {result}\n")


async def example_with_web_search() -> None:
    """Example using Hosted Web Search tool."""
    print("=" * 80)
    print("Example 3: Hosted Web Search Tool")
    print("=" * 80)
    
    # Check if BING_CONNECTION_ID is set
    bing_conn = os.getenv("BING_CONNECTION_ID")
    if not bing_conn:
        print("⚠️  BING_CONNECTION_ID not set. Skipping web search example.")
        print("   To enable: Set BING_CONNECTION_ID in your .env file")
        print("   Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{ai-service}/projects/{project}/connections/{connection}\n")
        return
    
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIClient(async_credential=credential),
            name="WebSearchAgent",
            instructions=(
                "You are a helpful assistant that can search the web for current information. "
                "Use web search to find up-to-date facts and news."
            ),
            tools=[
                HostedWebSearchTool(count=5),
                get_time_info,
            ],
        ) as agent,
    ):
        thread = agent.get_new_thread()
        
        query = "What are the latest developments in AI agent frameworks? Also tell me the current time."
        print(f"\nUser: {query}")
        result = await handle_approvals_with_thread(query, agent, thread)
        print(f"Agent: {result}\n")


async def example_with_all_tools() -> None:
    """Example combining all tool types."""
    print("=" * 80)
    print("Example 4: All Tools Combined")
    print("=" * 80)
    
    tools = [
        # Function tools
        get_weather,
        get_news_headlines,
        calculate,
        get_time_info,
        get_system_info,
        # Hosted MCP
        HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ),
    ]
    
    # Add web search if configured
    if os.getenv("BING_CONNECTION_ID"):
        tools.append(HostedWebSearchTool(count=5))
    
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIClient(async_credential=credential),
            name="MultiToolAgent",
            instructions=(
                "You are a comprehensive assistant with access to weather data, news, "
                "calculations, system info, Microsoft Learn docs, and web search. "
                "Use the most appropriate tools to provide accurate, helpful responses."
            ),
            tools=tools,
        ) as agent,
    ):
        thread = agent.get_new_thread()
        
        # Complex query using multiple tools
        query = (
            "What's the weather in New York, what are the latest technology news headlines, "
            "calculate 1024 * 768, and tell me the current time."
        )
        print(f"\nUser: {query}")
        result = await handle_approvals_with_thread(query, agent, thread)
        print(f"Agent: {result}\n")
        
        # Follow-up question
        query2 = "What's 15% of the result you just calculated?"
        print(f"User: {query2}")
        result2 = await handle_approvals_with_thread(query2, agent, thread)
        print(f"Agent: {result2}\n")


async def main() -> None:
    print("\n")
    print("=" * 80)
    print("Azure AI V2 Agent with Multiple REAL Tools Examples")
    print("=" * 80)
    print()
    print("📋 Setup Instructions:")
    print("1. Run 'az login' to authenticate")
    print("2. Set AZURE_AI_PROJECT_ENDPOINT in environment")
    print("3. Optional: Set OPENWEATHER_API_KEY (get free at openweathermap.org)")
    print("4. Optional: Set NEWS_API_KEY (get free at newsapi.org)")
    print("5. Optional: Set BING_CONNECTION_ID for web search")
    print("=" * 80)
    print()

    try:
        await example_with_function_tools()
        print("\n")
        
        await example_with_hosted_mcp()
        print("\n")
        
        await example_with_web_search()
        print("\n")
        
        await example_with_all_tools()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("- Ensure you've run 'az login'")
        print("- Check AZURE_AI_PROJECT_ENDPOINT is set correctly")
        print("- Verify your Azure subscription has access to Azure AI services")


if __name__ == "__main__":
    asyncio.run(main())

# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import sys
import httpx
from datetime import datetime, timezone
from typing import Annotated
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
local_env_path = Path(__file__).parent / ".env"
parent_env_path = Path(__file__).parent.parent / ".env"
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

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent with Function Tools Example (V2 API)

This sample demonstrates function tool integration with Azure AI Agents V2,
showing both agent-level and query-level tool configuration patterns using
REAL, FUNCTIONAL tools that perform actual operations.

Features:
- Real weather data from OpenWeatherMap API
- Current UTC time calculation
- Currency conversion via API
- File system operations (safe read-only)
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the current weather for a given location using OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OPENWEATHER_API_KEY not set. Get one free at https://openweathermap.org/api"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        
        return (
            f"Current weather in {location}: {description.title()}\n"
            f"Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s"
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{location}' not found. Please check the spelling."
        return f"Error fetching weather: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_time(
    timezone_name: Annotated[str, Field(description="Timezone name (e.g., 'UTC', 'America/New_York', 'Europe/London')")] = "UTC"
) -> str:
    """Get the current time in a specific timezone."""
    try:
        from zoneinfo import ZoneInfo
        
        if timezone_name.upper() == "UTC":
            tz = timezone.utc
        else:
            tz = ZoneInfo(timezone_name)
        
        current_time = datetime.now(tz)
        return (
            f"Current time in {timezone_name}: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            f"Day of week: {current_time.strftime('%A')}"
        )
    except Exception as e:
        return f"Error getting time for timezone '{timezone_name}': {str(e)}\nTry 'UTC', 'America/New_York', 'Europe/London', or 'Asia/Tokyo'"


def convert_currency(
    amount: Annotated[float, Field(description="The amount to convert")],
    from_currency: Annotated[str, Field(description="Source currency code (e.g., USD, EUR, GBP)")],
    to_currency: Annotated[str, Field(description="Target currency code (e.g., USD, EUR, GBP)")],
) -> str:
    """Convert currency using real-time exchange rates from exchangerate-api.com."""
    try:
        # Using free tier of exchangerate-api.com (no API key needed for basic usage)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        if to_currency.upper() not in data["rates"]:
            return f"Error: Currency code '{to_currency}' not found"
        
        rate = data["rates"][to_currency.upper()]
        converted = amount * rate
        
        return (
            f"{amount:.2f} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}\n"
            f"Exchange rate: 1 {from_currency.upper()} = {rate:.4f} {to_currency.upper()}\n"
            f"Last updated: {data['date']}"
        )
    except httpx.HTTPStatusError as e:
        return f"Error: Invalid currency code or API error (HTTP {e.response.status_code})"
    except Exception as e:
        return f"Error converting currency: {str(e)}"


def list_files(
    directory: Annotated[str, Field(description="Directory path to list files from (use '.' for current directory)")],
) -> str:
    """List files in a directory (read-only, safe operation)."""
    try:
        path = Path(directory).resolve()
        
        # Safety check: only allow listing in current working directory and subdirectories
        cwd = Path.cwd()
        if not str(path).startswith(str(cwd)):
            return f"Error: Can only list files in current directory and subdirectories for safety"
        
        if not path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        if not path.is_dir():
            return f"Error: '{directory}' is not a directory"
        
        files = []
        dirs = []
        
        for item in sorted(path.iterdir()):
            if item.is_file():
                size = item.stat().st_size
                files.append(f"  📄 {item.name} ({size:,} bytes)")
            elif item.is_dir():
                dirs.append(f"  📁 {item.name}/")
        
        result = f"Contents of '{directory}':\n\n"
        if dirs:
            result += "Directories:\n" + "\n".join(dirs) + "\n\n"
        if files:
            result += "Files:\n" + "\n".join(files)
        
        if not dirs and not files:
            result += "(empty directory)"
        
        return result
    except Exception as e:
        return f"Error listing directory: {str(e)}"


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")
    print("The agent has access to all tools for any query during its lifetime.\n")

    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="MultiToolAgent",
            instructions=(
                "You are a helpful assistant with access to weather data, time information, "
                "currency conversion, and file system operations. Use the appropriate tools "
                "to answer user questions accurately."
            ),
            tools=[get_weather, get_time, convert_currency, list_files],  # All tools available
        ) as agent,
    ):
        # Query 1: Weather tool
        query1 = "What's the weather like in London?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1}\n")

        # Query 2: Time tool
        query2 = "What time is it in Tokyo right now?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2}\n")

        # Query 3: Currency conversion
        query3 = "How much is 100 USD in EUR?"
        print(f"User: {query3}")
        result3 = await agent.run(query3)
        print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")
    print("Different tools can be provided for each specific query.\n")

    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="DynamicToolAgent",
            instructions="You are a helpful assistant that uses the tools provided for each query.",
        ) as agent,
    ):
        # Query 1: Only weather tool
        query1 = "What's the weather in Paris?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, tools=[get_weather])
        print(f"Agent: {result1}\n")

        # Query 2: Only time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, tools=[get_time])
        print(f"Agent: {result2}\n")

        # Query 3: Currency tool
        query3 = "Convert 50 GBP to USD"
        print(f"User: {query3}")
        result3 = await agent.run(query3, tools=[convert_currency])
        print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")
    print("Agent has base tools, additional tools can be added per query.\n")

    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="HybridToolAgent",
            instructions=(
                "You are a comprehensive assistant that can help with weather, time, "
                "currency, and file operations."
            ),
            tools=[get_weather, get_time],  # Base tools available for all queries
        ) as agent,
    ):
        # Query uses both base tools and additional run-time tools
        query = "What's the weather in Seattle, what time is it there, and convert 100 USD to CAD?"
        print(f"User: {query}")
        
        # Agent has get_weather and get_time from creation
        # We add convert_currency for this specific query
        result = await agent.run(
            query,
            tools=[convert_currency],  # Additional tool for this query
        )
        print(f"Agent: {result}\n")


async def streaming_with_tools() -> None:
    """Example showing streaming responses with function tools."""
    print("=== Streaming Response with Tools ===")
    print("Watch the agent think and call tools in real-time.\n")

    async with (
        AzureCliCredential() as credential,
        AzureAIClient(async_credential=credential).create_agent(
            name="StreamingToolAgent",
            instructions="You are a helpful assistant that provides detailed, streaming responses.",
            tools=[get_weather, convert_currency],
        ) as agent,
    ):
        query = "What's the weather in Tokyo and how much is 1000 JPY in USD?"
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


async def main() -> None:
    print("=" * 80)
    print("Azure AI V2 Agent with REAL Function Tools Examples")
    print("=" * 80)
    print()
    print("📋 Setup Instructions:")
    print("1. Run 'az login' to authenticate")
    print("2. Set OPENWEATHER_API_KEY in .env file (optional, get free at openweathermap.org)")
    print("3. Ensure AZURE_AI_PROJECT_ENDPOINT is set in environment")
    print("=" * 80)
    print()

    try:
        await tools_on_agent_level()
        print("\n" + "=" * 80 + "\n")
        
        await tools_on_run_level()
        print("\n" + "=" * 80 + "\n")
        
        await mixed_tools_example()
        print("\n" + "=" * 80 + "\n")
        
        await streaming_with_tools()
    
    except UnicodeDecodeError as e:
        print("\n" + "=" * 80)
        print("⚠️  KNOWN ISSUE: Azure SDK Gzip Encoding Error")
        print("=" * 80)
        print(f"\nError: {str(e)}")
        print("\nThis is a known issue with azure-ai-projects 2.0.0b2 (beta).")
        print("\nPossible solutions:")
        print("1. Try upgrading the Azure SDK:")
        print("   pip install --upgrade azure-ai-projects")
        print("\n2. Or downgrade to a stable version:")
        print("   pip install azure-ai-projects==1.0.0")
        print("\n3. Wait for the next beta release with the fix")
        print("\n4. Check your endpoint format - it should be:")
        print("   https://your-project.cognitiveservices.azure.com/")
        print("   (without /api/projects/projectname)")
        print("\nCurrent endpoint:")
        endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "Not set")
        print(f"   {endpoint}")
        print("=" * 80)
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("- Ensure you've run 'az login'")
        print("- Check AZURE_AI_PROJECT_ENDPOINT is set correctly")
        print("- Verify your Azure subscription has access to Azure AI services")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

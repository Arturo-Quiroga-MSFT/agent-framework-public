#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Agent with Function Tools - GitHub Models

This example demonstrates creating an AI agent with custom function tools
using GitHub Models. The agent can call Python functions to get real-time data.

Key Concepts:
    - Function calling with GitHub Models
    - Custom tool definition
    - Tool execution and response handling
    - Combining LLM reasoning with programmatic actions

Prerequisites:
    - GITHUB_TOKEN environment variable set
    - agent-framework package installed

Usage:
    python 02_github_with_tools.py
"""

import asyncio
import os
from datetime import datetime
from typing import Annotated
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

load_dotenv()


# ============================================================================
# TOOL DEFINITIONS - Functions the agent can call
# ============================================================================

def get_weather(
    location: Annotated[str, "The city and state, e.g. San Francisco, CA"]
) -> str:
    """Get the current weather for a given location.
    
    Args:
        location: The city and state to get weather for
        
    Returns:
        Current weather conditions as a string
    """
    # Simulated weather data (in production, would call real API)
    weather_data = {
        "Seattle, WA": "🌧️ Rainy, 52°F, Wind 15mph",
        "San Francisco, CA": "☁️ Partly cloudy, 65°F, Wind 8mph",
        "New York, NY": "❄️ Cold, 32°F, Wind 12mph",
        "Miami, FL": "☀️ Sunny, 82°F, Wind 5mph",
        "Austin, TX": "🌤️ Mostly sunny, 75°F, Wind 10mph"
    }
    
    result = weather_data.get(location, f"Weather data not available for {location}")
    print(f"   🔧 Tool called: get_weather('{location}') → {result}")
    return result


def calculate_cost(
    hours: Annotated[float, "Number of hours worked"],
    hourly_rate: Annotated[float, "Hourly rate in dollars"]
) -> str:
    """Calculate the total cost based on hours and hourly rate.
    
    Args:
        hours: Number of hours worked
        hourly_rate: Rate per hour in dollars
        
    Returns:
        Total cost calculation
    """
    total = hours * hourly_rate
    result = f"Total cost: ${total:,.2f} ({hours} hours × ${hourly_rate}/hour)"
    print(f"   🔧 Tool called: calculate_cost({hours}, {hourly_rate}) → {result}")
    return result


def get_current_time(
    timezone: Annotated[str, "Timezone (UTC, PST, EST, etc.)"] = "UTC"
) -> str:
    """Get the current time in a specific timezone.
    
    Args:
        timezone: The timezone to get time for
        
    Returns:
        Current time as a string
    """
    # Simplified implementation (production would use pytz)
    now = datetime.now()
    result = f"Current time in {timezone}: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"   🔧 Tool called: get_current_time('{timezone}') → {result}")
    return result


def search_knowledge_base(
    query: Annotated[str, "The search query"]
) -> str:
    """Search a simulated knowledge base for information.
    
    Args:
        query: What to search for
        
    Returns:
        Search results
    """
    # Simulated knowledge base
    kb = {
        "github models": "GitHub Models provides free access to popular AI models including GPT-4o, Llama, and Phi through an OpenAI-compatible API.",
        "maf": "Microsoft Agent Framework (MAF) is an open-source SDK for building AI agents and multi-agent workflows.",
        "foundry": "Azure AI Foundry is a platform for deploying and managing AI agents in production.",
        "rate limits": "GitHub Models free tier has approximately 15 requests per minute and 150K tokens per minute."
    }
    
    # Simple keyword matching
    query_lower = query.lower()
    for key, value in kb.items():
        if key in query_lower:
            result = value
            print(f"   🔧 Tool called: search_knowledge_base('{query}') → Found match")
            return result
    
    result = f"No information found for: {query}"
    print(f"   🔧 Tool called: search_knowledge_base('{query}') → {result}")
    return result


# ============================================================================
# MAIN DEMO
# ============================================================================

async def main():
    """Run an agent with tools using GitHub Models."""
    
    # Configuration
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    model_id = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
    base_url = os.getenv("GITHUB_BASE_URL", "https://models.inference.ai.azure.com")
    
    print("=" * 70)
    print("🚀 MAF Agent with Tools - GitHub Models")
    print("=" * 70)
    print(f"\n🔧 Configuration:")
    print(f"   Model: {model_id}")
    print(f"   Tools: 4 custom functions")
    print()
    
    # Create client
    chat_client = OpenAIChatClient(
        model_id=model_id,
        api_key=github_token,
        base_url=base_url
    )
    
    # Create agent with tools
    print("🤖 Creating agent with tools...")
    agent = ChatAgent(
        chat_client=chat_client,
        instructions=(
            "You are a helpful assistant with access to tools. "
            "Use the provided tools to answer user questions accurately. "
            "When you use a tool, explain what you're doing."
        ),
        tools=[
            get_weather,
            calculate_cost,
            get_current_time,
            search_knowledge_base
        ],
        name="ToolEnabledAgent"
    )
    
    # Test queries that require tool usage
    queries = [
        "What's the weather like in Seattle, WA?",
        "If I work 40 hours at $75 per hour, what's my total pay?",
        "What time is it in PST?",
        "Tell me about GitHub Models.",
        "What's the weather in Miami and what's the current time in EST?"
    ]
    
    print("\n💬 Running queries that require tool usage...")
    print("=" * 70)
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}/{len(queries)}:")
        print(f"   User: {query}")
        print()
        
        try:
            result = await agent.run(query)
            
            print(f"\n   Assistant: {result}")
            print()
            
            if i < len(queries):
                print("   ⏳ Waiting 5 seconds...\n")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            if "429" in str(e):
                print("   💡 Rate limit exceeded - waiting 60 seconds...")
                await asyncio.sleep(60)
    
    print("=" * 70)
    print("✅ Tool demo completed!")
    print()
    print("💡 Key Observations:")
    print("   - Agent automatically decides which tool to call")
    print("   - Tools are executed in Python, results sent back to LLM")
    print("   - Agent combines tool outputs with reasoning")
    print("   - Multiple tools can be called in sequence")
    print()
    print("📚 Next Steps:")
    print("   - Add your own custom tools")
    print("   - Try 03_github_multi_agent.py for multi-agent workflows")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

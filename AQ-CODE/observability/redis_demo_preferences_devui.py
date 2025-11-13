#!/usr/bin/env python3
"""
Redis Demo 1: Smart Preference Memory (DevUI Interactive)

DevUI-enabled interactive demo showing how RedisProvider enables agents to
remember user preferences across sessions with real-time visualization.

Features:
- Interactive chat interface with real-time responses
- Visual display of stored preferences in Redis
- Multi-session simulation with memory persistence
- Context retrieval visualization

Prerequisites:
- Redis running on localhost:6379 (docker run -p 6379:6379 -d redis:8.0.3)
- Environment variables in .env file (OPENAI_API_KEY, OPENAI_CHAT_MODEL_ID)
- pip install agent-framework-redis agent-framework-devui

Usage:
    python redis_demo_preferences_devui.py
    
Then open: http://localhost:8000
"""

import asyncio
import os
from pathlib import Path

from agent_framework import ChatAgent
from agent_framework.devui import serve
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework_redis._provider import RedisProvider
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


async def create_preference_agent(user_id: str = "alice_123") -> ChatAgent:
    """Create an agent with RedisProvider for preference memory."""
    
    # Create RedisProvider with user scope
    provider = RedisProvider(
        redis_url="redis://localhost:6379",
        index_name="preferences_devui_demo",
        prefix="prefs_devui",
        application_id="devui_workshop",
        agent_id="personal_assistant",
        user_id=user_id,
        overwrite_index=True,  # Fresh start for demo
    )

    # Create agent with RedisProvider
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model_id = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    client = AzureOpenAIChatClient(
        endpoint=azure_endpoint,
        deployment_name=model_id,
        credential=DefaultAzureCredential(),
    )
    agent = client.create_agent(
        name="PreferenceAssistant",
        instructions=(
            "You are a helpful personal assistant that remembers user preferences. "
            "Use the provided context to personalize your responses. "
            "When learning new preferences, acknowledge them warmly. "
            "When making recommendations, always consider stored preferences. "
            "Be concise but friendly."
        ),
        context_providers=provider,
    )
    
    return agent


async def main() -> None:
    """Launch DevUI for Redis preference memory demo."""
    
    print("=" * 70)
    print("REDIS DEMO 1: SMART PREFERENCE MEMORY (DevUI Interactive)")
    print("=" * 70)
    print("\nThis demo provides an interactive UI for testing RedisProvider")
    print("with persistent preference memory.\n")
    
    # Check environment variables
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        print("❌ ERROR: AZURE_OPENAI_ENDPOINT not found in .env file")
        return
    
    # Check Redis connection
    try:
        test_provider = RedisProvider(
            redis_url="redis://localhost:6379",
            index_name="test_connection",
            agent_id="test",
            user_id="test",
        )
        await test_provider.redis_index.create(overwrite=True)
        await test_provider.redis_index.delete()
        print("✓ Redis connection successful")
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to Redis: {e}")
        print("Please ensure Redis is running: docker run -p 6379:6379 -d redis:8.0.3")
        return
    
    print("✓ Environment configured")
    print("\n" + "=" * 70)
    print("CREATING AGENT WITH REDIS MEMORY")
    print("=" * 70)
    print("\nConfiguration:")
    print("  • Provider: RedisProvider")
    print("  • User ID: alice_123")
    print("  • Agent ID: personal_assistant")
    print("  • Memory Scope: User-specific preferences")
    
    # Create agent
    agent = await create_preference_agent()
    print("\n✓ Agent created successfully")
    
    print("\n" + "=" * 70)
    print("STARTING DEVUI SERVER")
    print("=" * 70)
    print("\n🚀 DevUI will start on http://localhost:8000")
    print("\n📝 Try these conversation flows:")
    print("\nSession 1 - Learning preferences:")
    print("  1. Hi! I'm Alice. I'm vegetarian and love Italian food.")
    print("  2. I also prefer organic ingredients when possible.")
    print("  3. I live in Seattle, Washington.")
    
    print("\nSession 2 - Using stored preferences:")
    print("  4. Can you recommend a restaurant for dinner tonight?")
    print("  5. What do you remember about my food preferences?")
    
    print("\nSession 3 - Adding more details:")
    print("  6. I should mention I'm allergic to nuts.")
    print("  7. I prefer restaurants with outdoor seating.")
    
    print("\nSession 4 - Comprehensive personalization:")
    print("  8. Recommend a restaurant considering everything you know.")
    print("  9. What's your complete understanding of my preferences?")
    
    print("\n💡 Tips:")
    print("  • Each message is automatically stored in Redis")
    print("  • Preferences persist across page refreshes")
    print("  • Try closing and reopening - memory remains!")
    print("  • Agent retrieves context automatically for each query")
    
    print("\n" + "=" * 70)
    print("🎯 Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    return agent


if __name__ == "__main__":
    # Create agent asynchronously
    agent = asyncio.run(main())
    
    # Start DevUI server synchronously
    serve(entities=[agent], port=8000, auto_open=True)

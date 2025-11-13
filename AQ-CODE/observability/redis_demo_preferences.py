#!/usr/bin/env python3
"""
Redis Demo 1: Smart Preference Memory

This demo shows how RedisProvider enables agents to remember user preferences
across multiple sessions. The agent learns about user preferences and uses them
to personalize responses.

Scenario: Personal assistant that remembers dietary preferences, location,
          and other user details to provide personalized recommendations.

Key Concepts:
- RedisProvider for persistent memory
- User-scoped memory (user_id)
- Context retrieval across sessions
- Natural preference learning

Prerequisites:
- Redis running on localhost:6379 (docker run -p 6379:6379 -d redis:8.0.3)
- Environment variables in .env file (OPENAI_API_KEY, OPENAI_CHAT_MODEL_ID)
- pip install agent-framework-redis

Usage:
    python redis_demo_preferences.py
"""

import asyncio
import os
from pathlib import Path

from agent_framework import ChatMessage, Role
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework_redis._provider import RedisProvider
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


async def simulate_session(
    session_num: int,
    agent,
    queries: list[str],
) -> None:
    """Simulate a conversation session with the agent."""
    print(f"\n{'='*60}")
    print(f"SESSION {session_num}")
    print(f"{'='*60}")

    for i, query in enumerate(queries, 1):
        print(f"\n[Message {i}]")
        print(f"User: {query}")

        result = await agent.run(query)
        print(f"Agent: {result.text}")

    print(f"\n{'='*60}")
    print(f"SESSION {session_num} COMPLETE")
    print(f"{'='*60}")


async def main() -> None:
    """Demo RedisProvider with user preference memory."""

    print("=" * 60)
    print("REDIS DEMO 1: SMART PREFERENCE MEMORY")
    print("=" * 60)
    print("\nThis demo shows how agents remember user preferences")
    print("across multiple sessions using RedisProvider.\n")

    # Check environment variables
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model_id = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

    if not azure_endpoint:
        print("❌ ERROR: AZURE_OPENAI_ENDPOINT not found in .env file")
        return

    print(f"✓ Using Azure OpenAI model: {model_id}")

    # Check Redis connection
    try:
        test_provider = RedisProvider(
            redis_url="redis://localhost:6379",
            index_name="test_connection",
            agent_id="test",
            user_id="test",
        )
        # Test connection by creating index
        await test_provider.redis_index.create(overwrite=True)
        await test_provider.redis_index.delete()
        print("✓ Redis connection successful\n")
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to Redis: {e}")
        print("Please ensure Redis is running: docker run -p 6379:6379 -d redis:8.0.3")
        return

    # Create RedisProvider with user scope
    print("Creating RedisProvider with user scope...")
    provider = RedisProvider(
        redis_url="redis://localhost:6379",
        index_name="preferences_demo",
        prefix="prefs",
        application_id="workshop_app",
        agent_id="personal_assistant",
        user_id="alice_123",  # Scoped to specific user
        overwrite_index=True,  # Fresh start for demo
    )

    print(f"✓ Provider configured:")
    print(f"  - Index: preferences_demo")
    print(f"  - User: alice_123")
    print(f"  - Agent: personal_assistant\n")

    # Create agent with RedisProvider
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
            "When making recommendations, always consider stored preferences."
        ),
        context_providers=provider,
    )

    print("✓ Agent created with memory capabilities\n")

    # SESSION 1: Learning user preferences
    session1_queries = [
        "Hi! I'm Alice. I'm vegetarian and I love Italian food.",
        "I also prefer organic ingredients when possible.",
        "I live in Seattle, Washington.",
    ]

    await simulate_session(1, agent, session1_queries)

    # SESSION 2: Using stored preferences (simulating new session)
    print("\n[SIMULATING NEW SESSION - Agent retrieves stored memories]\n")

    session2_queries = [
        "Can you recommend a restaurant for dinner tonight?",
        "What do you remember about my food preferences?",
    ]

    await simulate_session(2, agent, session2_queries)

    # SESSION 3: Adding more preferences
    print("\n[THIRD SESSION - Learning additional preferences]\n")

    session3_queries = [
        "I should mention I'm allergic to nuts.",
        "I also prefer restaurants with outdoor seating.",
    ]

    await simulate_session(3, agent, session3_queries)

    # SESSION 4: Comprehensive personalization
    print("\n[FOURTH SESSION - Full personalization]\n")

    session4_queries = [
        "Now recommend a restaurant considering everything you know about me.",
        "What's your complete understanding of my preferences?",
    ]

    await simulate_session(4, agent, session4_queries)

    # Show stored context (optional debug info)
    print("\n" + "=" * 60)
    print("DEMO INSIGHTS")
    print("=" * 60)
    print("\nThe agent successfully:")
    print("✓ Stored preferences across 4 sessions")
    print("✓ Retrieved context for personalized responses")
    print("✓ Built a comprehensive user profile over time")
    print("✓ Applied memory to recommendations")

    print("\nKey Benefits:")
    print("• Preferences persist across application restarts")
    print("• Natural conversation flow without explicit 'save' commands")
    print("• Context grows organically with each interaction")
    print("• Agent provides increasingly personalized experiences")

    # Cleanup
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)
    await provider.redis_index.delete()
    print("✓ Cleaned up Redis index")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Try redis_demo_persistence.py for conversation persistence")
    print("2. Try redis_demo_multi_agent.py for multi-agent isolation")
    print("3. Explore vector search by adding embeddings to the provider")


if __name__ == "__main__":
    asyncio.run(main())

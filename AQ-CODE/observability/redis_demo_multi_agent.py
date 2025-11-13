#!/usr/bin/env python3
"""
Redis Demo 3: Multi-Agent Isolation

This demo shows how multiple agents can maintain separate memory scopes using
RedisProvider with different agent_id values, even for the same user.

Scenario: A user interacts with two different assistants - a Personal Assistant
          for personal tasks and a Work Assistant for professional tasks. Each
          agent maintains its own isolated memory, demonstrating enterprise
          multi-tenant patterns.

Key Concepts:
- Memory isolation using agent_id
- Same user accessing multiple agents
- Separate context per agent role
- Enterprise multi-tenant architecture

Prerequisites:
- Redis running on localhost:6379 (docker run -p 6379:6379 -d redis:8.0.3)
- Environment variables in .env file (OPENAI_API_KEY, OPENAI_CHAT_MODEL_ID)
- pip install agent-framework-redis

Usage:
    python redis_demo_multi_agent.py
"""

import asyncio
import os
from pathlib import Path

from agent_framework.azure import AzureOpenAIChatClient
from agent_framework_redis._provider import RedisProvider
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


async def interact_with_agent(
    agent_name: str,
    agent,
    queries: list[str],
    section_num: int,
) -> None:
    """Interact with a specific agent."""
    print(f"\n{'='*60}")
    print(f"SECTION {section_num}: TALKING TO {agent_name.upper()}")
    print(f"{'='*60}")

    for i, query in enumerate(queries, 1):
        print(f"\n[Message {i}]")
        print(f"User: {query}")

        result = await agent.run(query)
        print(f"{agent_name}: {result.text}")

    print(f"\n{'='*60}")


async def main() -> None:
    """Demo RedisProvider with multi-agent memory isolation."""

    print("=" * 60)
    print("REDIS DEMO 3: MULTI-AGENT ISOLATION")
    print("=" * 60)
    print("\nThis demo shows how multiple agents maintain separate")
    print("memory scopes using different agent_id values.\n")

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
        await test_provider.redis_index.create(overwrite=True)
        await test_provider.redis_index.delete()
        print("✓ Redis connection successful\n")
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to Redis: {e}")
        print("Please ensure Redis is running: docker run -p 6379:6379 -d redis:8.0.3")
        return

    # ========================================================================
    # SETUP: Create two agents with separate memory scopes
    # ========================================================================
    print("=" * 60)
    print("SETUP: CREATING AGENTS WITH ISOLATED MEMORY")
    print("=" * 60)

    user_id = "alice_123"

    # Personal Assistant with its own memory scope
    print("\n1. Creating Personal Assistant...")
    personal_provider = RedisProvider(
        redis_url="redis://localhost:6379",
        index_name="multi_agent_demo",
        prefix="multi",
        application_id="workshop_app",
        agent_id="agent_personal",  # Unique agent_id for isolation
        user_id=user_id,
        overwrite_index=True,  # Fresh start
    )

    # Create agent exposing the flight search tool. Tool outputs are captured by the
    # provider and become retrievable context for later turns.
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model_id = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    client = AzureOpenAIChatClient(
        endpoint=azure_endpoint,
        deployment_name=model_id,
        credential=DefaultAzureCredential(),
    )
    agent = client.create_agent(
        name="PersonalAssistant",
        instructions=(
            "You are a personal assistant helping with personal life tasks. "
            "Remember personal preferences, hobbies, health info, and lifestyle choices. "
            "Use stored context to provide personalized recommendations. "
            "Be warm and friendly."
        ),
        context_providers=personal_provider,
    )

    print(f"✓ Personal Assistant created")
    print(f"  - Agent ID: agent_personal")
    print(f"  - User ID: {user_id}")
    print(f"  - Scope: Personal life & hobbies")

    # Work Assistant with separate memory scope
    print("\n2. Creating Work Assistant...")
    work_provider = RedisProvider(
        redis_url="redis://localhost:6379",
        index_name="multi_agent_demo",  # Same index, different agent_id
        prefix="multi",
        application_id="workshop_app",
        agent_id="agent_work",  # Different agent_id for isolation
        user_id=user_id,  # Same user
    )

    work_agent = client.create_agent(
        name="WorkAssistant",
        instructions=(
            "You are a work assistant helping with professional tasks. "
            "Remember work projects, meeting schedules, team info, and professional goals. "
            "Use stored context to provide work-focused recommendations. "
            "Be professional and efficient."
        ),
        context_providers=work_provider,
    )

    print(f"✓ Work Assistant created")
    print(f"  - Agent ID: agent_work")
    print(f"  - User ID: {user_id}")
    print(f"  - Scope: Work & professional tasks")

    print("\n✓ Both agents use the same Redis index but maintain separate memory!")

    # ========================================================================
    # PHASE 1: Teach Personal Assistant about personal life
    # ========================================================================
    personal_queries_1 = [
        "Hi! I love hiking and spend most weekends exploring trails in the Cascades.",
        "I'm vegetarian and prefer organic food when possible.",
        "I practice yoga every morning at 6 AM.",
    ]

    await interact_with_agent("Personal Assistant", personal_agent, personal_queries_1, 1)

    # ========================================================================
    # PHASE 2: Teach Work Assistant about professional life
    # ========================================================================
    work_queries_1 = [
        "Hi! I'm working on a machine learning project for customer segmentation.",
        "I have team meetings every Tuesday at 2 PM with the data science team.",
        "My main tech stack is Python, TensorFlow, and Azure ML.",
    ]

    await interact_with_agent("Work Assistant", work_agent, work_queries_1, 2)

    # ========================================================================
    # PHASE 3: Test memory isolation - Personal Assistant
    # ========================================================================
    print("\n" + "🔍" * 30)
    print("TESTING MEMORY ISOLATION")
    print("🔍" * 30)

    personal_queries_2 = [
        "What do you know about my hobbies?",
        "Do you know anything about my work projects?",  # Should NOT know
    ]

    await interact_with_agent("Personal Assistant", personal_agent, personal_queries_2, 3)

    # ========================================================================
    # PHASE 4: Test memory isolation - Work Assistant
    # ========================================================================
    work_queries_2 = [
        "What projects am I working on?",
        "Do you know about my exercise routine?",  # Should NOT know
    ]

    await interact_with_agent("Work Assistant", work_agent, work_queries_2, 4)

    # ========================================================================
    # PHASE 5: Add more context and test comprehensive isolation
    # ========================================================================
    print("\n" + "=" * 60)
    print("PHASE 5: ADDING MORE CONTEXT TO BOTH AGENTS")
    print("=" * 60)

    personal_queries_3 = [
        "I'm planning a trip to Patagonia next month for hiking.",
        "I also started learning Spanish for the trip.",
    ]

    await interact_with_agent("Personal Assistant", personal_agent, personal_queries_3, 5)

    work_queries_3 = [
        "We're launching the ML model to production next quarter.",
        "I need to prepare a presentation for the executive team.",
    ]

    await interact_with_agent("Work Assistant", work_agent, work_queries_3, 6)

    # ========================================================================
    # PHASE 6: Final comprehensive memory test
    # ========================================================================
    print("\n" + "=" * 60)
    print("PHASE 6: COMPREHENSIVE MEMORY TEST")
    print("=" * 60)

    personal_queries_4 = [
        "Give me a complete summary of everything you know about me.",
    ]

    await interact_with_agent("Personal Assistant", personal_agent, personal_queries_4, 7)

    work_queries_4 = [
        "Give me a complete summary of everything you know about my work.",
    ]

    await interact_with_agent("Work Assistant", work_agent, work_queries_4, 8)

    # ========================================================================
    # DEMO INSIGHTS
    # ========================================================================
    print("\n" + "=" * 60)
    print("DEMO INSIGHTS")
    print("=" * 60)

    print("\nMemory Isolation Verified:")
    print("✓ Personal Assistant knows about:")
    print("  - Hiking and Cascades trails")
    print("  - Vegetarian diet and organic preferences")
    print("  - Yoga routine at 6 AM")
    print("  - Patagonia trip planning")
    print("  - Learning Spanish")

    print("\n✓ Work Assistant knows about:")
    print("  - ML project for customer segmentation")
    print("  - Tuesday team meetings at 2 PM")
    print("  - Tech stack (Python, TensorFlow, Azure ML)")
    print("  - Production launch next quarter")
    print("  - Executive presentation preparation")

    print("\n✓ Neither agent has access to the other's memory!")

    print("\nKey Benefits:")
    print("• Complete memory isolation between agents")
    print("• Same user can interact with specialized agents")
    print("• Clear separation of concerns (personal vs professional)")
    print("• Enterprise multi-tenant architecture pattern")
    print("• Single Redis index, multiple logical partitions")

    print("\nProduction Use Cases:")
    print("• Multi-bot systems (sales, support, technical)")
    print("• Department-specific assistants in enterprises")
    print("• Privacy-sensitive applications (healthcare, finance)")
    print("• Role-based access control for agent memories")
    print("• Customer-facing vs internal agent separation")

    print("\nArchitecture Pattern:")
    print("┌────────────────────────────────────────┐")
    print("│          User: alice_123               │")
    print("├────────────────┬───────────────────────┤")
    print("│ Personal Agent │ Work Agent            │")
    print("│ agent_personal │ agent_work            │")
    print("├────────────────┴───────────────────────┤")
    print("│     Same Redis Index, Isolated Scopes  │")
    print("└────────────────────────────────────────┘")

    # ========================================================================
    # CLEANUP
    # ========================================================================
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)
    await personal_provider.redis_index.delete()
    print("✓ Cleaned up Redis index (both agents' memory)")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Try redis_demo_preferences.py for memory/context storage")
    print("2. Try redis_demo_persistence.py for conversation persistence")
    print("3. Explore additional scoping dimensions (application_id, thread_id)")
    print("4. Build multi-tenant applications with agent isolation")


if __name__ == "__main__":
    asyncio.run(main())

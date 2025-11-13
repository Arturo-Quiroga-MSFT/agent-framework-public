#!/usr/bin/env python3
"""
Redis Demo 2: Resume Conversations

This demo shows how RedisChatMessageStore enables conversations to persist
across application restarts. A customer support bot can resume conversations
from previous sessions.

Scenario: Customer support bot handling a support ticket that spans multiple
          sessions, with the agent remembering previous conversation context
          even after application restarts.

Key Concepts:
- RedisChatMessageStore for persistent chat history
- Thread-based conversation isolation (thread_id)
- Resuming conversations across sessions
- Message limits and automatic trimming

Prerequisites:
- Redis running on localhost:6379 (docker run -p 6379:6379 -d redis:8.0.3)
- Environment variables in .env file (OPENAI_API_KEY, OPENAI_CHAT_MODEL_ID)
- pip install agent-framework-redis

Usage:
    python redis_demo_persistence.py
"""

import asyncio
import os
from pathlib import Path

from agent_framework import ChatMessage, Role
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework_redis._chat_message_store import RedisChatMessageStore
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


async def simulate_session(
    session_num: int,
    agent,
    thread: AgentThread,
    queries: list[str],
    show_history: bool = False,
) -> None:
    """Simulate a conversation session with the agent."""
    print(f"\n{'='*60}")
    print(f"SESSION {session_num}")
    print(f"{'='*60}")

    # Show message count at start of session
    if thread.message_store:
        messages = await thread.message_store.list_messages()  # type: ignore
        print(f"Messages in history: {len(messages)}")

    for i, query in enumerate(queries, 1):
        print(f"\n[Message {i}]")
        print(f"Customer: {query}")

        result = await agent.run(query, thread=thread)
        print(f"Support Agent: {result.text}")

    # Show message history if requested
    if show_history and thread.message_store:
        print(f"\n[Message History]")
        messages = await thread.message_store.list_messages()  # type: ignore
        print(f"Total messages stored: {len(messages)}")
        for idx, msg in enumerate(messages[-6:], 1):  # Show last 6 messages
            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            text_preview = msg.text[:60] + "..." if len(msg.text) > 60 else msg.text
            print(f"  {idx}. [{role}] {text_preview}")

    print(f"\n{'='*60}")
    print(f"SESSION {session_num} COMPLETE")
    print(f"{'='*60}")


async def simulate_app_restart() -> None:
    """Simulate application restart with a delay."""
    print("\n" + "🔄" * 30)
    print("SIMULATING APPLICATION RESTART")
    print("(In production, this would be an actual app restart)")
    print("🔄" * 30)
    await asyncio.sleep(1)  # Brief pause for effect


async def main() -> None:
    """Demo RedisChatMessageStore with conversation persistence."""

    print("=" * 60)
    print("REDIS DEMO 2: RESUME CONVERSATIONS")
    print("=" * 60)
    print("\nThis demo shows how conversations persist across")
    print("application restarts using RedisChatMessageStore.\n")

    # Check environment variables
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model_id = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

    if not azure_endpoint:
        print("❌ ERROR: AZURE_OPENAI_ENDPOINT not found in .env file")
        return

    print(f"✓ Using Azure OpenAI model: {model_id}")

    # Check Redis connection
    try:
        test_store = RedisChatMessageStore(
            redis_url="redis://localhost:6379",
            thread_id="test_connection",
        )
        await test_store.ping()
        await test_store.clear()
        await test_store.aclose()
        print("✓ Redis connection successful\n")
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to Redis: {e}")
        print("Please ensure Redis is running: docker run -p 6379:6379 -d redis:8.0.3")
        return

    # Define support ticket ID (simulates a real ticket number)
    ticket_id = "TICKET-12345"

    # ========================================================================
    # PHASE 1: Initial customer contact
    # ========================================================================
    print("=" * 60)
    print("PHASE 1: INITIAL CUSTOMER CONTACT")
    print("=" * 60)

    print(f"\nCreating conversation thread for {ticket_id}...")
    store1 = RedisChatMessageStore(
        redis_url="redis://localhost:6379",
        thread_id=f"support_{ticket_id}",
        max_messages=20,  # Keep last 20 messages
    )

    thread1 = AgentThread(message_store=store1)
    print(f"✓ Thread created: {store1.thread_id}")
    print(f"✓ Message limit: 20 messages (auto-trimming enabled)\n")

    # Create support agent
    client = AzureOpenAIChatClient(
        endpoint=azure_endpoint,
        deployment_name=model_id,
        credential=DefaultAzureCredential(),
    )
    agent = client.create_agent(
        name="SupportBot",
        instructions=(
            f"You are a helpful customer support agent working on ticket {ticket_id}. "
            "Be professional, empathetic, and thorough. Track all customer details. "
            "When resuming conversations, acknowledge the previous context naturally."
        ),
    )

    print("✓ Support agent created\n")

    # Session 1: Customer reports issue
    session1_queries = [
        "Hi, I'm having issues with my order. Order number is ORD-98765.",
        "The product arrived damaged - the screen has a crack.",
        "I ordered it on November 1st and it arrived yesterday.",
    ]

    await simulate_session(1, agent, thread1, session1_queries, show_history=True)

    # Close the first connection
    await store1.aclose()
    print("\n✓ Session 1 connection closed (simulating end of work session)")

    # ========================================================================
    # PHASE 2: Resume conversation after "restart"
    # ========================================================================
    await simulate_app_restart()

    print("\n" + "=" * 60)
    print("PHASE 2: RESUMING CONVERSATION (AFTER RESTART)")
    print("=" * 60)

    print(f"\nReconnecting to conversation thread {ticket_id}...")
    store2 = RedisChatMessageStore(
        redis_url="redis://localhost:6379",
        thread_id=f"support_{ticket_id}",  # Same thread_id loads history!
        max_messages=20,
    )

    thread2 = AgentThread(message_store=store2)

    # Verify history loaded
    loaded_messages = await store2.list_messages()
    print(f"✓ Loaded {len(loaded_messages)} messages from previous session\n")

    # Session 2: Customer follows up
    session2_queries = [
        "Hi, I'm following up on my damaged order. Did you find anything?",
        "What are my options for replacement or refund?",
    ]

    await simulate_session(2, agent, thread2, session2_queries, show_history=True)

    # Close the second connection
    await store2.aclose()
    print("\n✓ Session 2 connection closed")

    # ========================================================================
    # PHASE 3: Another restart, final resolution
    # ========================================================================
    await simulate_app_restart()

    print("\n" + "=" * 60)
    print("PHASE 3: FINAL RESOLUTION (AFTER ANOTHER RESTART)")
    print("=" * 60)

    print(f"\nReconnecting to conversation thread {ticket_id}...")
    store3 = RedisChatMessageStore(
        redis_url="redis://localhost:6379",
        thread_id=f"support_{ticket_id}",
        max_messages=20,
    )

    thread3 = AgentThread(message_store=store3)

    loaded_messages = await store3.list_messages()
    print(f"✓ Loaded {len(loaded_messages)} messages from all previous sessions\n")

    # Session 3: Resolution
    session3_queries = [
        "I'd like to proceed with the replacement option.",
        "Can you summarize everything we've discussed about this issue?",
    ]

    await simulate_session(3, agent, thread3, session3_queries, show_history=True)

    # ========================================================================
    # DEMO INSIGHTS
    # ========================================================================
    print("\n" + "=" * 60)
    print("DEMO INSIGHTS")
    print("=" * 60)

    final_messages = await store3.list_messages()
    print(f"\nConversation Statistics:")
    print(f"✓ Total sessions: 3")
    print(f"✓ Total messages: {len(final_messages)}")
    print(f"✓ Application restarts survived: 2")
    print(f"✓ Ticket ID: {ticket_id}")

    print("\nKey Benefits:")
    print("• Full conversation context preserved across restarts")
    print("• Natural conversation flow without re-explaining issues")
    print("• Customer doesn't need to repeat information")
    print("• Support agents can pick up where others left off")
    print("• Automatic message trimming prevents memory overflow")

    print("\nProduction Use Cases:")
    print("• Customer support ticketing systems")
    print("• Multi-session user interactions")
    print("• Handoff between human and AI agents")
    print("• Long-running conversations over days/weeks")

    # ========================================================================
    # CLEANUP
    # ========================================================================
    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)
    await store3.clear()
    await store3.aclose()
    print(f"✓ Cleared conversation history for {ticket_id}")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Try redis_demo_preferences.py for memory/context storage")
    print("2. Try redis_demo_multi_agent.py for multi-agent isolation")
    print("3. Explore message limits and trimming strategies")
    print("4. Test thread serialization for distributed systems")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Redis Demo 2: Resume Conversations (DevUI Interactive)

DevUI-enabled interactive demo showing how RedisChatMessageStore enables
conversations to persist across application restarts.

Features:
- Interactive chat with persistent conversation history
- Visual demonstration of "resuming" conversations
- Support ticket scenario with ticket ID tracking
- Message history display in DevUI

Prerequisites:
- Redis running on localhost:6379 (docker run -p 6379:6379 -d redis:8.0.3)
- Environment variables in .env file (OPENAI_API_KEY, OPENAI_CHAT_MODEL_ID)
- pip install agent-framework-redis agent-framework-devui

Usage:
    # Session 1: Start conversation
    python redis_demo_persistence_devui.py
    
    # Session 2: After stopping (Ctrl+C), run again
    python redis_demo_persistence_devui.py
    
    # Notice: Previous conversation history is preserved!
    
Then open: http://localhost:8001
"""

import asyncio
import os
from pathlib import Path

from agent_framework import ChatAgent
from agent_framework.devui import serve
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework_redis._chat_message_store import RedisChatMessageStore
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Support ticket ID for this demo
TICKET_ID = "TICKET-12345"


async def create_support_agent() -> tuple[ChatAgent, AgentThread]:
    """Create a support agent with persistent chat history."""
    
    # Create RedisChatMessageStore with ticket-based thread ID
    store = RedisChatMessageStore(
        redis_url="redis://localhost:6379",
        thread_id=f"support_{TICKET_ID}",
        max_messages=50,  # Keep last 50 messages
    )
    
    # Create thread with persistent store
    thread = AgentThread(message_store=store)
    
    # Create support agent
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model_id = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    client = AzureOpenAIChatClient(
        azure_endpoint=azure_endpoint,
        model_id=model_id,
    )
    agent = client.create_agent(
        name="SupportBot",
        instructions=(
            f"You are a helpful customer support agent working on ticket {TICKET_ID}. "
            "Be professional, empathetic, and thorough. Track all customer details. "
            "When resuming conversations, acknowledge the previous context naturally. "
            "Always reference the ticket number when appropriate."
        ),
    )
    
    return agent, thread


async def main() -> None:
    """Launch DevUI for Redis conversation persistence demo."""
    
    print("=" * 70)
    print("REDIS DEMO 2: RESUME CONVERSATIONS (DevUI Interactive)")
    print("=" * 70)
    print("\nThis demo shows conversation persistence across app restarts")
    print("using RedisChatMessageStore.\n")
    
    # Check environment variables
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not azure_endpoint:
        print("❌ ERROR: AZURE_OPENAI_ENDPOINT not found in .env file")
        return
    
    # Check Redis connection
    try:
        test_store = RedisChatMessageStore(
            redis_url="redis://localhost:6379",
            thread_id="test_connection",
        )
        await test_store.ping()
        await test_store.clear()
        await test_store.aclose()
        print("✓ Redis connection successful")
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to Redis: {e}")
        print("Please ensure Redis is running: docker run -p 6379:6379 -d redis:8.0.3")
        return
    
    print("✓ Environment configured")
    
    print("\n" + "=" * 70)
    print("CREATING SUPPORT AGENT WITH PERSISTENT HISTORY")
    print("=" * 70)
    print(f"\nTicket ID: {TICKET_ID}")
    
    # Create agent and thread
    agent, thread = await create_support_agent()
    
    # Check if there's existing conversation history
    if thread.message_store:
        existing_messages = await thread.message_store.list_messages()  # type: ignore
        message_count = len(existing_messages)
        
        if message_count > 0:
            print(f"\n🔄 RESUMING CONVERSATION")
            print(f"  • Found {message_count} messages from previous session(s)")
            print(f"  • Thread ID: support_{TICKET_ID}")
            print(f"  • The agent will remember your previous conversation!")
        else:
            print(f"\n🆕 NEW CONVERSATION")
            print(f"  • No previous history found")
            print(f"  • Thread ID: support_{TICKET_ID}")
            print(f"  • Starting fresh conversation")
    
    print("\nConfiguration:")
    print("  • Store: RedisChatMessageStore")
    print(f"  • Thread ID: support_{TICKET_ID}")
    print("  • Message Limit: 50 messages (auto-trimming)")
    print("  • Persistence: Survives app restarts")
    
    print("\n✓ Agent created successfully")
    
    print("\n" + "=" * 70)
    print("STARTING DEVUI SERVER")
    print("=" * 70)
    print("\n🚀 DevUI will start on http://localhost:8001")
    print("\n📝 Try this conversation flow:")
    
    print("\n🎬 First Session - Report Issue:")
    print("  1. Hi, I'm having issues with my order. Order number is ORD-98765.")
    print("  2. The product arrived damaged - the screen has a crack.")
    print("  3. I ordered it on November 1st and it arrived yesterday.")
    
    print("\n⏸️  Then: Stop server (Ctrl+C) and restart this script")
    
    print("\n🎬 Second Session - Follow Up:")
    print("  4. Hi, I'm following up on my damaged order. Did you find anything?")
    print("  5. What are my options for replacement or refund?")
    
    print("\n⏸️  Then: Stop server (Ctrl+C) and restart again")
    
    print("\n🎬 Third Session - Resolution:")
    print("  6. I'd like to proceed with the replacement option.")
    print("  7. Can you summarize everything we've discussed about this issue?")
    
    print("\n💡 Key Features:")
    print("  • Full conversation history preserved across restarts")
    print("  • Agent maintains context from previous sessions")
    print("  • No need to re-explain issues")
    print("  • Natural conversation flow across sessions")
    
    print("\n🧹 Cleanup:")
    print("  • To start fresh, delete the Redis key manually:")
    print(f"    redis-cli DEL support_{TICKET_ID}")
    
    print("\n" + "=" * 70)
    print("🎯 Press Ctrl+C to stop the server (then restart to test persistence!)")
    print("=" * 70)
    print()
    
    # Note: DevUI serve() doesn't directly support passing threads,
    # so we'll attach the thread to the agent for the demo
    # In production, you'd use the factory pattern with chat_message_store_factory
    agent._thread = thread  # type: ignore
    
    return agent


if __name__ == "__main__":
    # Create agent asynchronously
    agent = asyncio.run(main())
    
    # Start DevUI server synchronously
    serve(entities=[agent], port=8001, auto_open=True)
    asyncio.run(main())

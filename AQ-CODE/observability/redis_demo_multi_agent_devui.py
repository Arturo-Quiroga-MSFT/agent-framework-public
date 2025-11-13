#!/usr/bin/env python3
"""
Redis Demo 3: Multi-Agent Isolation (DevUI Interactive)

DevUI-enabled interactive demo showing how multiple agents maintain separate
memory scopes using RedisProvider with different agent_id values.

This demo runs TWO DevUI servers simultaneously:
- Port 8002: Personal Assistant (agent_personal)
- Port 8003: Work Assistant (agent_work)

Features:
- Side-by-side agent comparison
- Same user, different memory scopes
- Visual demonstration of memory isolation
- Enterprise multi-tenant pattern

Prerequisites:
- Redis running on localhost:6379 (docker run -p 6379:6379 -d redis:8.0.3)
- Environment variables in .env file (OPENAI_API_KEY, OPENAI_CHAT_MODEL_ID)
- pip install agent-framework-redis agent-framework-devui

Usage:
    python redis_demo_multi_agent_devui.py
    
Then open:
    Personal Assistant: http://localhost:8002
    Work Assistant:     http://localhost:8003
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

USER_ID = "alice_123"


async def create_personal_agent() -> ChatAgent:
    """Create personal assistant with isolated memory."""
    
    provider = RedisProvider(
        redis_url="redis://localhost:6379",
        index_name="multi_agent_devui_demo",
        prefix="multi_devui",
        application_id="devui_workshop",
        agent_id="agent_personal",  # Unique scope
        user_id=USER_ID,
        overwrite_index=True,  # Fresh start
    )
    
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
            "Be warm and friendly. ONLY know about personal life - you have NO access "
            "to work-related information."
        ),
        context_providers=provider,
    )
    
    return agent


async def create_work_agent() -> ChatAgent:
    """Create work assistant with isolated memory."""
    
    provider = RedisProvider(
        redis_url="redis://localhost:6379",
        index_name="multi_agent_devui_demo",  # Same index
        prefix="multi_devui",
        application_id="devui_workshop",
        agent_id="agent_work",  # Different scope!
        user_id=USER_ID,  # Same user
    )
    
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    model_id = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    client = AzureOpenAIChatClient(
        endpoint=azure_endpoint,
        deployment_name=model_id,
        credential=DefaultAzureCredential(),
    )
    agent = client.create_agent(
        name="WorkAssistant",
        instructions=(
            "You are a work assistant helping with professional tasks. "
            "Remember work projects, meeting schedules, team info, and professional goals. "
            "Use stored context to provide work-focused recommendations. "
            "Be professional and efficient. ONLY know about work - you have NO access "
            "to personal life information."
        ),
        context_providers=provider,
    )
    
    return agent


async def main() -> None:
    """Launch both DevUI servers for multi-agent isolation demo."""
    
    print("=" * 70)
    print("REDIS DEMO 3: MULTI-AGENT ISOLATION (DevUI Interactive)")
    print("=" * 70)
    print("\nThis demo runs TWO agents simultaneously with separate memory.")
    print("Same user, different contexts - complete memory isolation!\n")
    
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
    print("CREATING AGENTS WITH ISOLATED MEMORY")
    print("=" * 70)
    
    print(f"\nUser ID: {USER_ID}")
    print("\n1️⃣  Personal Assistant:")
    print("    • Agent ID: agent_personal")
    print("    • Scope: Personal life, hobbies, health")
    print("    • Port: 8002")
    
    print("\n2️⃣  Work Assistant:")
    print("    • Agent ID: agent_work")
    print("    • Scope: Professional tasks, projects")
    print("    • Port: 8003")
    
    print("\n✓ Both agents use the same Redis index but maintain separate memory!")
    
    # Create both agents
    print("\nCreating agents...")
    personal_agent = await create_personal_agent()
    print("✓ Personal Assistant created")
    
    work_agent = await create_work_agent()
    print("✓ Work Assistant created")
    
    print("\n" + "=" * 70)
    print("STARTING DEVUI SERVERS")
    print("=" * 70)
    print("\n🚀 Opening TWO browser tabs:")
    print("    • Personal Assistant: http://localhost:8002")
    print("    • Work Assistant:     http://localhost:8003")
    
    print("\n📝 Try this conversation flow:")
    
    print("\n🏠 In Personal Assistant (port 8002):")
    print("  1. Hi! I love hiking and spend weekends in the Cascades.")
    print("  2. I'm vegetarian and prefer organic food.")
    print("  3. I practice yoga every morning at 6 AM.")
    print("  4. What do you know about my hobbies?")
    print("  5. Do you know anything about my work projects? (should say NO)")
    
    print("\n💼 In Work Assistant (port 8003):")
    print("  1. Hi! I'm working on an ML project for customer segmentation.")
    print("  2. I have team meetings every Tuesday at 2 PM.")
    print("  3. My tech stack is Python, TensorFlow, and Azure ML.")
    print("  4. What projects am I working on?")
    print("  5. Do you know about my exercise routine? (should say NO)")
    
    print("\n💡 Key Features:")
    print("  • Personal Assistant ONLY knows personal information")
    print("  • Work Assistant ONLY knows work information")
    print("  • Complete memory isolation despite same user")
    print("  • Same Redis index, different logical partitions")
    
    print("\n🎯 Architecture:")
    print("  ┌────────────────────────────────────────┐")
    print(f"  │          User: {USER_ID}           │")
    print("  ├────────────────┬───────────────────────┤")
    print("  │ Personal Agent │ Work Agent            │")
    print("  │ agent_personal │ agent_work            │")
    print("  │ Port: 8002     │ Port: 8003            │")
    print("  ├────────────────┴───────────────────────┤")
    print("  │     Same Redis Index, Isolated Scopes  │")
    print("  └────────────────────────────────────────┘")
    
    print("\n" + "=" * 70)
    print("USAGE INSTRUCTIONS")
    print("=" * 70)
    print("\n🚀 You need to run TWO separate terminal windows:")
    print("\n   Terminal 1 (Personal Assistant):")
    print("   python redis_demo_multi_agent_devui.py --agent personal")
    print("   Opens: http://localhost:8002")
    print("\n   Terminal 2 (Work Assistant):")
    print("   python redis_demo_multi_agent_devui.py --agent work")
    print("   Opens: http://localhost:8003")
    
    print("\n💡 Note: DevUI serve() runs synchronously, so we can't run")
    print("   both servers in one process.")
    
    print("\n" + "=" * 70)
    print("🎯 Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    return personal_agent, work_agent


if __name__ == "__main__":
    # Create agents asynchronously
    personal_agent, work_agent = asyncio.run(main())
    
    # Determine which agent to start based on command line argument
    import sys
    agent_choice = "personal"  # default
    
    if "--agent" in sys.argv:
        idx = sys.argv.index("--agent")
        if idx + 1 < len(sys.argv):
            agent_choice = sys.argv[idx + 1].lower()
    
    # Start appropriate DevUI server synchronously
    if agent_choice == "work":
        print("💼 Starting Work Assistant on port 8003...\n")
        serve(entities=[work_agent], port=8003, auto_open=True)
    else:
        print("🏠 Starting Personal Assistant on port 8002...\n")
        serve(entities=[personal_agent], port=8002, auto_open=True)

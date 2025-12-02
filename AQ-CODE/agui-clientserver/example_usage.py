#!/usr/bin/env python3
"""
Example: Using AG-UI Client programmatically.

This example shows how to use the AGUIClient class in your own Python code
for programmatic access to AG-UI servers.
"""

import asyncio
from agui_client import AGUIClient


async def example_single_query():
    """Example: Send a single query."""
    print("Example 1: Single Query")
    print("-" * 60)
    
    client = AGUIClient()
    
    try:
        await client.send_message("What is the capital of France?")
    finally:
        await client.close()


async def example_conversation():
    """Example: Multi-turn conversation with thread continuity."""
    print("\n\nExample 2: Multi-turn Conversation")
    print("-" * 60)
    
    client = AGUIClient()
    
    try:
        # First message
        await client.send_message("What are the primary colors?")
        
        # Follow-up (uses same thread)
        await client.send_message("How do you mix them?")
        
        # Another follow-up
        await client.send_message("What is the color wheel?")
        
        print(f"\nThread ID: {client.thread_id}")
    finally:
        await client.close()


async def example_with_context():
    """Example: Send query with additional context."""
    print("\n\nExample 3: Query with Context")
    print("-" * 60)
    
    client = AGUIClient()
    
    try:
        context = {
            "user_level": "beginner",
            "language": "en",
            "format": "bullet_points"
        }
        
        await client.send_message(
            "Explain machine learning",
            context=context
        )
    finally:
        await client.close()


async def example_parallel_clients():
    """Example: Multiple clients with different threads."""
    print("\n\nExample 4: Parallel Clients")
    print("-" * 60)
    
    client1 = AGUIClient()
    client2 = AGUIClient()
    
    try:
        # Run two queries in parallel
        await asyncio.gather(
            client1.send_message("Tell me about Python programming"),
            client2.send_message("Tell me about JavaScript programming")
        )
        
        print(f"\nClient 1 Thread: {client1.thread_id}")
        print(f"Client 2 Thread: {client2.thread_id}")
    finally:
        await client1.close()
        await client2.close()


async def main():
    """Run all examples."""
    print("=" * 80)
    print("AG-UI Client - Programmatic Usage Examples")
    print("=" * 80)
    
    # Check if server is available
    client = AGUIClient()
    if not await client.check_health():
        print("\n❌ Server is not available. Please start the server first:")
        print("   python agui_server.py")
        await client.close()
        return
    await client.close()
    
    print("✅ Server is available\n")
    
    # Run examples
    await example_single_query()
    await example_conversation()
    await example_with_context()
    await example_parallel_clients()
    
    print("\n" + "=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

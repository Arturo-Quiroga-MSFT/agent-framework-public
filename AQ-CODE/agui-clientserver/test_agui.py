#!/usr/bin/env python3
"""
Test script for AG-UI Client-Server implementation.

This script runs automated tests against the AG-UI server to verify
functionality and demonstrate usage patterns.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agui_client import AGUIClient, Colors


async def test_health_check(client: AGUIClient):
    """Test server health check."""
    print(f"\n{Colors.BOLD}Test 1: Health Check{Colors.RESET}")
    print("-" * 60)
    
    is_healthy = await client.check_health()
    if is_healthy:
        print(f"{Colors.GREEN}✅ Server is healthy{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}❌ Server health check failed{Colors.RESET}")
        return False


async def test_simple_query(client: AGUIClient):
    """Test simple query without thread."""
    print(f"\n{Colors.BOLD}Test 2: Simple Query (No Thread){Colors.RESET}")
    print("-" * 60)
    
    query = "What is the capital of France?"
    print(f"Query: {query}\n")
    
    await client.send_message(query)
    print(f"\n{Colors.GREEN}✅ Simple query completed{Colors.RESET}")


async def test_threaded_conversation(client: AGUIClient):
    """Test multi-turn conversation with thread continuity."""
    print(f"\n{Colors.BOLD}Test 3: Multi-turn Conversation{Colors.RESET}")
    print("-" * 60)
    
    queries = [
        "What are the primary colors?",
        "How do you mix them to create secondary colors?",
        "What is the color wheel?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{Colors.BOLD}Turn {i}:{Colors.RESET} {query}\n")
        await client.send_message(query)
        await asyncio.sleep(1)  # Brief pause between queries
    
    print(f"\n{Colors.GREEN}✅ Multi-turn conversation completed{Colors.RESET}")
    print(f"Thread ID: {client.thread_id}")


async def test_technical_query(client: AGUIClient):
    """Test technical/coding query."""
    print(f"\n{Colors.BOLD}Test 4: Technical Query{Colors.RESET}")
    print("-" * 60)
    
    query = "Write a Python function to calculate factorial recursively"
    print(f"Query: {query}\n")
    
    await client.send_message(query)
    print(f"\n{Colors.GREEN}✅ Technical query completed{Colors.RESET}")


async def test_complex_query(client: AGUIClient):
    """Test complex multi-part query."""
    print(f"\n{Colors.BOLD}Test 5: Complex Multi-part Query{Colors.RESET}")
    print("-" * 60)
    
    query = "Explain quantum computing in simple terms, then list 3 real-world applications with brief descriptions"
    print(f"Query: {query}\n")
    
    await client.send_message(query)
    print(f"\n{Colors.GREEN}✅ Complex query completed{Colors.RESET}")


async def run_all_tests():
    """Run all tests."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("=" * 80)
    print("🧪 AG-UI Client-Server Test Suite")
    print("=" * 80)
    print(f"{Colors.RESET}")
    
    # Initialize client
    client = AGUIClient()
    
    try:
        # Test 1: Health check
        healthy = await test_health_check(client)
        if not healthy:
            print(f"\n{Colors.RED}❌ Server is not available. Please start the server first.{Colors.RESET}")
            print(f"\n{Colors.YELLOW}To start the server:{Colors.RESET}")
            print(f"   cd AQ-CODE/agui-clientserver")
            print(f"   python agui_server.py")
            return
        
        # Test 2: Simple query
        await test_simple_query(client)
        
        # Test 3: Multi-turn conversation
        client_threaded = AGUIClient()  # New client for threaded conversation
        await test_threaded_conversation(client_threaded)
        await client_threaded.close()
        
        # Test 4: Technical query
        await test_technical_query(client)
        
        # Test 5: Complex query
        await test_complex_query(client)
        
        # Summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}")
        print("=" * 80)
        print("✅ All Tests Completed Successfully!")
        print("=" * 80)
        print(f"{Colors.RESET}\n")
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test suite failed: {e}{Colors.RESET}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run_all_tests())

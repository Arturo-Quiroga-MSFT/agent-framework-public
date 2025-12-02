#!/usr/bin/env python3
"""
Basic Routing Example

Simple demonstration of the dynamic workflow router.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflow_router import DynamicWorkflowRouter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def main():
    """Run basic routing examples."""
    print("=" * 80)
    print("🚀 Dynamic Workflow Router - Basic Example")
    print("=" * 80)
    print()
    
    # Initialize router
    router = DynamicWorkflowRouter(
        enable_cache=True,
        cache_ttl_seconds=300
    )
    
    # Example queries
    test_queries = [
        "I need help with my order #12345",
        "How do I integrate your API with Python?",
        "I want to buy the enterprise plan",
        "My product stopped working and I need assistance"
    ]
    
    try:
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*80}")
            print(f"Example {i}/{len(test_queries)}")
            print(f"{'='*80}")
            print(f"Query: {query}\n")
            
            # Route and execute
            full_response = ""
            async for chunk in router.route_and_execute(query, stream=True):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print("\n")
        
        # List available workflows
        print("\n" + "=" * 80)
        print("📋 Available Workflows")
        print("=" * 80)
        
        workflows = await router.list_workflows()
        for wf in workflows:
            status = "✅" if wf.get("metadata", {}).get("enabled", True) else "❌"
            print(f"{status} {wf['id']}")
            print(f"   Category: {wf.get('category', 'N/A')}")
            print(f"   Description: {wf.get('description', 'N/A')[:80]}...")
            print()
    
    finally:
        # Cleanup
        await router.cleanup()
    
    print("=" * 80)
    print("✅ Examples complete!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Azure AI V1 Agents Cleanup Script

This script lists and deletes V1 Agents (legacy Assistants) created through
the Azure AI Agents API. These show up in the old Azure AI Foundry portal
but NOT in the new Microsoft Foundry portal.

V1 Agents have IDs like: asst_CsBpSN8eof0hEnUmOLSOG6Db
V2 Agents (new) are managed through Azure AI Projects SDK.

Usage:
    python cleanup_v1_agents.py
    python cleanup_v1_agents.py --delete-all
    python cleanup_v1_agents.py --pattern "DBA_UI"
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential


async def list_v1_agents() -> list:
    """List all V1 agents using AgentsClient."""
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ AZURE_AI_PROJECT_ENDPOINT not set")
        return []
    
    agents = []
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(endpoint=endpoint, credential=credential) as client:
            async for agent in client.list_agents():
                agents.append(agent)
    
    return agents


async def delete_agents_batch(agents: list) -> tuple[int, int]:
    """Delete multiple agents with a single client connection."""
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    deleted = 0
    failed = 0
    
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(endpoint=endpoint, credential=credential) as client:
            for agent in agents:
                try:
                    await client.delete_agent(agent.id)
                    print(f"  ✅ Deleted: {agent.name or agent.id}")
                    deleted += 1
                except Exception as e:
                    print(f"  ❌ Failed: {agent.name or agent.id} - {str(e)[:50]}")
                    failed += 1
    
    return deleted, failed


async def main():
    print("=" * 70)
    print("  Azure AI V1 Agents Cleanup (Legacy Assistants)")
    print("=" * 70)
    print()
    
    # Check for command line args
    delete_all = "--delete-all" in sys.argv
    pattern = None
    for i, arg in enumerate(sys.argv):
        if arg == "--pattern" and i + 1 < len(sys.argv):
            pattern = sys.argv[i + 1]
    
    print("📋 Fetching V1 agents...")
    agents = await list_v1_agents()
    
    if not agents:
        print("✅ No V1 agents found")
        return
    
    print(f"\nFound {len(agents)} V1 agent(s):\n")
    print(f"{'#':<4} {'Name':<25} {'ID':<40} {'Model'}")
    print("-" * 90)
    
    for i, agent in enumerate(agents[:40], 1):
        name = (agent.name or "(unnamed)")[:24]
        print(f"{i:<4} {name:<25} {agent.id:<40} {agent.model}")
    
    if len(agents) > 40:
        print(f"... and {len(agents) - 40} more")
    
    # Group by name for summary
    print("\n" + "=" * 70)
    print("  Summary by Name:")
    print("=" * 70)
    
    name_counts = {}
    for agent in agents:
        name = agent.name or "(unnamed)"
        name_counts[name] = name_counts.get(name, 0) + 1
    
    for name, count in sorted(name_counts.items(), key=lambda x: -x[1]):
        print(f"  {name}: {count}")
    
    # Handle command line deletion
    if delete_all:
        print(f"\n⚠️  --delete-all: Deleting ALL {len(agents)} agents...")
        deleted, failed = await delete_agents_batch(agents)
        print(f"\n✅ Deleted: {deleted}, Failed: {failed}")
        return
    
    if pattern:
        matches = [a for a in agents if pattern.lower() in (a.name or "").lower()]
        print(f"\n⚠️  --pattern '{pattern}': Found {len(matches)} matching agents...")
        if matches:
            deleted, failed = await delete_agents_batch(matches)
            print(f"\n✅ Deleted: {deleted}, Failed: {failed}")
        return
    
    # Interactive mode
    print("\n" + "=" * 70)
    print("  Options:")
    print("=" * 70)
    print("  1. Delete ALL agents")
    print("  2. Delete by name pattern (e.g., 'DBA_UI', 'InteractiveDBA')")
    print("  3. Keep specific names, delete the rest")
    print("  4. Exit without deleting")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        confirm = input(f"\n⚠️  Delete ALL {len(agents)} agents? Type 'DELETE ALL' to confirm: ")
        if confirm == "DELETE ALL":
            deleted, failed = await delete_agents_batch(agents)
            print(f"\n✅ Deleted: {deleted}, Failed: {failed}")
        else:
            print("Cancelled.")
            
    elif choice == "2":
        pattern = input("Enter name pattern to delete (e.g., 'DBA_UI'): ").strip()
        if not pattern:
            print("No pattern entered. Cancelled.")
            return
            
        matches = [a for a in agents if pattern.lower() in (a.name or "").lower()]
        print(f"\nFound {len(matches)} agents matching '{pattern}':")
        for a in matches[:10]:
            print(f"  - {a.name} ({a.id})")
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more")
        
        if matches:
            confirm = input(f"\nDelete these {len(matches)} agents? (yes/no): ")
            if confirm.lower() == "yes":
                deleted, failed = await delete_agents_batch(matches)
                print(f"\n✅ Deleted: {deleted}, Failed: {failed}")
            else:
                print("Cancelled.")
                
    elif choice == "3":
        keep_names = input("Enter names to KEEP (comma-separated): ").strip()
        keep_list = [n.strip() for n in keep_names.split(",") if n.strip()]
        
        if not keep_list:
            print("No names entered. Cancelled.")
            return
            
        to_delete = [a for a in agents if a.name not in keep_list]
        to_keep = [a for a in agents if a.name in keep_list]
        
        print(f"\nWill KEEP {len(to_keep)} agents:")
        for a in to_keep[:5]:
            print(f"  ✅ {a.name}")
        if len(to_keep) > 5:
            print(f"  ... and {len(to_keep) - 5} more")
            
        print(f"\nWill DELETE {len(to_delete)} agents:")
        for a in to_delete[:10]:
            print(f"  ❌ {a.name or a.id}")
        if len(to_delete) > 10:
            print(f"  ... and {len(to_delete) - 10} more")
        
        confirm = input(f"\nProceed with deletion? (yes/no): ")
        if confirm.lower() == "yes":
            deleted, failed = await delete_agents_batch(to_delete)
            print(f"\n✅ Deleted: {deleted}, Failed: {failed}")
        else:
            print("Cancelled.")
            
    else:
        print("Exiting without changes.")


if __name__ == "__main__":
    asyncio.run(main())

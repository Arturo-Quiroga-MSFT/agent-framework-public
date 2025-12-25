#!/usr/bin/env python3
"""
List V1 Agents (Legacy - Old Portal Only)

This script lists all V1 agents created with the legacy AgentsClient API.
These agents:
- Have IDs like: asst_CsBpSN8eof0hEnUmOLSOG6Db
- Show in OLD Azure AI Foundry portal only
- Do NOT show in NEW Microsoft Foundry portal (ai.azure.com)

PREREQUISITES:
    - Azure CLI: az login
    - Environment: AZURE_AI_PROJECT_ENDPOINT

USAGE:
    python list_v1_agents.py
    python list_v1_agents.py --json
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from azure.ai.agents.aio import AgentsClient
    from azure.identity.aio import DefaultAzureCredential
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Install with: pip install azure-ai-agents azure-identity")
    sys.exit(1)


async def list_v1_agents(output_json: bool = False):
    """List all V1 agents."""
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ AZURE_AI_PROJECT_ENDPOINT not set")
        print("Set it with: export AZURE_AI_PROJECT_ENDPOINT='https://xxx.services.ai.azure.com/api/projects/xxx'")
        return
    
    if not output_json:
        print("=" * 70)
        print("V1 Agents (Legacy - Old Portal Only)")
        print("=" * 70)
        print(f"Endpoint: {endpoint}")
        print()
    
    agents = []
    try:
        async with DefaultAzureCredential() as credential:
            async with AgentsClient(endpoint=endpoint, credential=credential) as client:
                async for agent in client.list_agents():
                    agents.append({
                        "id": agent.id,
                        "name": agent.name or "(unnamed)",
                        "model": agent.model,
                        "created_at": agent.created_at.isoformat() if agent.created_at else None,
                        "description": agent.description or "",
                        "tools": len(agent.tools) if agent.tools else 0
                    })
    except Exception as e:
        if not output_json:
            print(f"❌ Error listing V1 agents: {e}")
        else:
            print(json.dumps({"error": str(e)}))
        return
    
    if output_json:
        print(json.dumps({
            "count": len(agents),
            "agents": agents
        }, indent=2))
        return
    
    if not agents:
        print("✅ No V1 agents found")
        print()
        print("This is expected if you:")
        print("  - Recently migrated to V2 API")
        print("  - Only create agents with AIProjectClient (V2 API)")
        print("  - Already cleaned up V1 agents")
        return
    
    print(f"Found {len(agents)} V1 agent(s):")
    print()
    print(f"{'#':<4} {'Name':<30} {'ID':<42} {'Model':<20}")
    print("-" * 110)
    
    for i, agent in enumerate(agents, 1):
        name = agent["name"][:29]
        agent_id = agent["id"][:41]
        model = agent["model"][:19]
        print(f"{i:<4} {name:<30} {agent_id:<42} {model:<20}")
    
    print()
    print("=" * 70)
    print("Portal Visibility:")
    print("=" * 70)
    print("  Old Portal: ✅ These agents show in old Azure AI Foundry portal")
    print("  New Portal: ❌ These agents do NOT show in https://ai.azure.com")
    print()
    print("To migrate to V2:")
    print("  1. Recreate agents using AIProjectClient (see list_v2_agents.py)")
    print("  2. Delete V1 agents with: python cleanup_v1_agents.py")
    print()
    
    # Group by name
    name_counts = {}
    for agent in agents:
        name = agent["name"]
        name_counts[name] = name_counts.get(name, 0) + 1
    
    if len(name_counts) < len(agents):
        print("Summary by Name:")
        print("-" * 70)
        for name, count in sorted(name_counts.items(), key=lambda x: -x[1]):
            print(f"  {name}: {count} instance(s)")
        print()


async def main():
    output_json = "--json" in sys.argv
    await list_v1_agents(output_json)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
List V2 Agents (Current - New Portal)

This script lists all V2 agents created with the AIProjectClient API.
These agents:
- Have human-readable names as IDs
- Show in NEW Microsoft Foundry portal (ai.azure.com)
- Do NOT show in old Azure AI Foundry portal
- Can be 'prompt', 'hosted', or 'workflow' kind

PREREQUISITES:
    - Azure CLI: az login
    - Environment: AZURE_AI_PROJECT_ENDPOINT

USAGE:
    python list_v2_agents.py
    python list_v2_agents.py --json
    python list_v2_agents.py --detailed

UPDATED: February 2026
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Install with: pip install azure-ai-projects azure-identity")
    sys.exit(1)


def list_v2_agents(output_json: bool = False, detailed: bool = False):
    """List all V2 agents."""
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ AZURE_AI_PROJECT_ENDPOINT not set")
        print("Set it with: export AZURE_AI_PROJECT_ENDPOINT='https://xxx.services.ai.azure.com/api/projects/xxx'")
        return
    
    if not output_json:
        print("=" * 70)
        print("V2 Agents (Current - New Portal)")
        print("=" * 70)
        print(f"Endpoint: {endpoint}")
        print()
    
    agents = []
    try:
        credential = DefaultAzureCredential()
        client = AIProjectClient(endpoint=endpoint, credential=credential)
        
        for agent in client.agents.list():
            # V2 agents store details in versions.latest
            versions = getattr(agent, 'versions', {})
            latest = versions.get('latest', {})
            definition = latest.get('definition', {})
            
            # Extract real agent ID (name:version format or just name)
            agent_id = getattr(agent, 'id', 'unknown')
            version_id = latest.get('id', agent_id)  # e.g., "AgentName:5"
            
            agent_data = {
                "id": version_id,
                "name": getattr(agent, 'name', '(unnamed)'),
                "model": definition.get('model') or '(none)',
                "kind": definition.get('kind', 'unknown'),
                "version": latest.get('version', 'unknown'),
                "created_at": latest.get('created_at', None),
                "description": latest.get('description', ''),
            }
            
            if detailed:
                agent_data.update({
                    "instructions": definition.get('instructions', '')[:200] if definition.get('instructions') else "",
                    "tools": len(definition.get('tools', [])),
                    "kind": definition.get('kind', 'unknown'),
                })
            
            agents.append(agent_data)
            
    except Exception as e:
        if not output_json:
            print(f"❌ Error listing V2 agents: {e}")
            print()
            print("Troubleshooting:")
            print("  1. Verify you're authenticated: az login")
            print("  2. Check endpoint is correct")
            print("  3. Ensure you have access to the project")
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
        print("✅ No V2 agents found")
        print()
        print("To create V2 agents:")
        print("  1. Run: python agents/azure_ai_persistent_agent_v2.py")
        print("  2. Or: python deploy_new_agents.py")
        print()
        print("V2 agents will show in: https://ai.azure.com")
        return
    
    print(f"Found {len(agents)} V2 agent(s):")
    print()
    
    if detailed:
        for i, agent in enumerate(agents, 1):
            print(f"{i}. {agent['name']}")
            print(f"   ID: {agent['id']}")
            print(f"   Model: {agent['model']}")
            print(f"   Version: {agent['version']}")
            if agent.get('created_at'):
                from datetime import datetime
                created = datetime.fromtimestamp(agent['created_at']).isoformat()
                print(f"   Created: {created}")
            if agent.get('description'):
                print(f"   Description: {agent['description']}")
            if agent.get('kind'):
                print(f"   Kind: {agent['kind']}")
            if agent.get('tools'):
                print(f"   Tools: {agent['tools']}")
            if agent.get('instructions'):
                instructions = agent['instructions'][:100] + "..." if len(agent['instructions']) > 100 else agent['instructions']
                print(f"   Instructions: {instructions}")
            print()
    else:
        print(f"{'#':<4} {'Name':<30} {'ID':<38} {'Model':<20} {'Kind':<10} {'Ver':<5}")
        print("-" * 120)
        
        for i, agent in enumerate(agents, 1):
            name = agent["name"][:29]
            agent_id = agent["id"][:37]
            model = agent["model"][:19]
            kind = agent.get("kind", "?")[:9]
            version = str(agent["version"])[:4]
            print(f"{i:<4} {name:<30} {agent_id:<38} {model:<20} {kind:<10} {version:<5}")
        print()
    
    print("=" * 70)
    print("Portal Visibility:")
    print("=" * 70)
    print("  Old Portal: ❌ These agents do NOT show in old portal")
    print("  New Portal: ✅ These agents show in https://ai.azure.com")
    print()
    print("To view in portal:")
    print("  1. Go to https://ai.azure.com")
    print("  2. Select your project")
    print("  3. Navigate to 'Agents' section")
    print()
    
    # Summary by model
    model_counts = {}
    for agent in agents:
        model = agent["model"]
        model_counts[model] = model_counts.get(model, 0) + 1
    
    if len(model_counts) > 1:
        print("Summary by Model:")
        print("-" * 70)
        for model, count in sorted(model_counts.items(), key=lambda x: -x[1]):
            print(f"  {model}: {count} agent(s)")
        print()


def main():
    output_json = "--json" in sys.argv
    detailed = "--detailed" in sys.argv
    list_v2_agents(output_json, detailed)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
List ALL agents (V1 classic + V2 new) in Azure AI Foundry project.

This script detects both:
- V2 agents: Modern versioned agents (what we currently see)
- V1 classic agents: Legacy assistants with asst_* IDs

Author: Azure AI Team
Last Updated: November 26, 2025
"""

import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)

# Load environment
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment variables from: {env_path}\n")

# Get endpoint
endpoint = os.getenv('AZURE_AI_PROJECT_ENDPOINT')
if not endpoint:
    print("Error: AZURE_AI_PROJECT_ENDPOINT not set")
    sys.exit(1)

print(f"🔄 Connecting to: {endpoint}\n")
credential = DefaultAzureCredential()
client = AIProjectClient(endpoint=endpoint, credential=credential)

print("="*80)
print("DETECTING ALL AGENTS (V1 + V2)")
print("="*80)

# Method 1: List V2 agents (current method)
print("\n📦 V2 AGENTS (Versioned, via agents.list()):")
print("-"*80)
v2_agents = list(client.agents.list())
print(f"Found {len(v2_agents)} V2 agents\n")

for idx, agent in enumerate(v2_agents[:5], 1):  # Show first 5
    name = getattr(agent, 'name', 'Unknown')
    agent_id = agent.id
    
    # Get version info
    version = 'N/A'
    model = 'Unknown'
    created_at = None
    
    if hasattr(agent, 'versions') and agent.versions:
        latest = agent.versions.get('latest', {})
        version = latest.get('version', 'N/A')
        created_at = latest.get('created_at')
        definition = latest.get('definition', {})
        if isinstance(definition, dict):
            model = definition.get('model', 'Unknown')
    
    print(f"{idx}. {name}")
    print(f"   ID: {agent_id}")
    print(f"   Version: {version}")
    print(f"   Model: {model}")
    if created_at:
        dt = datetime.fromtimestamp(created_at)
        print(f"   Created: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

if len(v2_agents) > 5:
    print(f"... and {len(v2_agents) - 5} more V2 agents\n")

# Try to access V1 classic agents
print("\n📦 V1 CLASSIC AGENTS (Legacy assistants with asst_* IDs):")
print("-"*80)
print("Attempting to detect V1 agents...")

# Check if any V2 agents have asst_ IDs (unlikely but possible)
v1_like_agents = [a for a in v2_agents if a.id.startswith('asst_')]
if v1_like_agents:
    print(f"✅ Found {len(v1_like_agents)} agents with asst_ IDs in V2 list!")
    for agent in v1_like_agents[:3]:
        print(f"   - {getattr(agent, 'name', 'Unknown')} (ID: {agent.id})")
else:
    print("⚠️  No asst_* IDs found in current agent list.")
    print("\n💡 V1 classic agents might be:")
    print("   1. In a different project/subscription")
    print("   2. Requires different API endpoint/version")
    print("   3. Accessible only via Foundry Portal UI")
    print("\n   To verify:")
    print("   - Check Azure AI Foundry Portal (https://ai.azure.com)")
    print("   - Navigate to 'Agents' with view=foundry-classic")
    print("   - Compare agent lists between portal and SDK")

print("\n" + "="*80)
print(f"SUMMARY: Found {len(v2_agents)} total agents via SDK")
print("="*80)

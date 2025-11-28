#!/usr/bin/env python3
"""
Diagnostic script to inspect the actual structure of agent objects.
This helps debug what attributes are available on agents returned from the API.
"""

import os
import sys
from pathlib import Path

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

# Get endpoint
endpoint = os.getenv('AZURE_AI_PROJECT_ENDPOINT')
if not endpoint:
    print("Error: AZURE_AI_PROJECT_ENDPOINT not set")
    sys.exit(1)

# Connect
print(f"Connecting to: {endpoint}\n")
credential = DefaultAzureCredential()
client = AIProjectClient(endpoint=endpoint, credential=credential)

# List agents
agents = list(client.agents.list())
if not agents:
    print("No agents found")
    sys.exit(0)

# Inspect first agent
agent = agents[0]
print(f"=== Inspecting Agent: {getattr(agent, 'name', 'Unknown')} ===\n")

print("Available attributes:")
for attr in dir(agent):
    if not attr.startswith('_'):
        try:
            value = getattr(agent, attr)
            if not callable(value):
                print(f"  {attr}: {type(value).__name__} = {repr(value)[:100]}")
        except:
            pass

print("\n" + "="*70)
print("Agent object type:", type(agent))
print("Agent object repr:", repr(agent)[:500])

# Try to access as dict
if hasattr(agent, '__dict__'):
    print("\n__dict__ contents:")
    for key, value in agent.__dict__.items():
        print(f"  {key}: {type(value).__name__} = {repr(value)[:100]}")

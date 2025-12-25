#!/usr/bin/env python3
"""
Debug V2 Agent Attributes

Quick script to see what attributes V2 agent objects actually have.
"""
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv()

endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
credential = DefaultAzureCredential()
client = AIProjectClient(endpoint=endpoint, credential=credential)

print("Fetching first agent to inspect attributes...")
agents = list(client.agents.list())

if agents:
    agent = agents[0]
    print(f"\nAgent object type: {type(agent)}")
    print(f"Agent object dir():\n")
    
    # Print all attributes
    for attr in sorted(dir(agent)):
        if not attr.startswith('_'):
            try:
                value = getattr(agent, attr, None)
                if not callable(value):
                    print(f"  {attr}: {value}")
            except:
                print(f"  {attr}: <error accessing>")
    
    print("\n\nRaw representation:")
    print(f"{agent}")
    
    # Try common attributes
    print("\n\nTrying common attributes:")
    attrs_to_try = ['id', 'name', 'model', 'model_name', 'deployment_name', 
                    'agent_id', 'created_at', 'description', 'instructions']
    for attr in attrs_to_try:
        val = getattr(agent, attr, '<not found>')
        print(f"  {attr}: {val}")
else:
    print("No agents found")

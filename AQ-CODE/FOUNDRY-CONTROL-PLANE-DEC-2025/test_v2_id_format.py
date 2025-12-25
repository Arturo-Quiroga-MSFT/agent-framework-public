#!/usr/bin/env python3
"""
Test V2 Agent Creation - Check actual ID format

This script creates a temporary agent to see what ID format is actually returned.
"""
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv()

endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
credential = DefaultAzureCredential()
client = AIProjectClient(endpoint=endpoint, credential=credential)

print("Creating a test agent to check ID format...\n")

# Create a test agent
agent = client.agents.create_agent(
    model="gpt-4o",
    name="TestIDFormatAgent_Temp",
    instructions="Temporary test agent",
    description="For ID format testing"
)

print("Agent created!")
print(f"Type: {type(agent)}")
print(f"\nAgent attributes:")
for attr in ['id', 'name', 'model', 'object']:
    val = getattr(agent, attr, '<not found>')
    print(f"  {attr}: {val}")

print(f"\nFull agent object:")
print(agent)

# Check if there's a versions structure
if hasattr(agent, 'versions'):
    print(f"\nVersions structure:")
    print(agent.versions)

# Clean up
print(f"\n\nDeleting test agent...")
try:
    client.agents.delete_agent(agent.id)
    print("✅ Test agent deleted")
except Exception as e:
    print(f"⚠️ Could not delete: {e}")
    print(f"Manual cleanup: client.agents.delete_agent('{agent.id}')")

#!/usr/bin/env python3
"""Test if a prompt agent works on this project - isolates whether the issue is hosted-agent-specific"""

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

client = AIProjectClient(
    endpoint="https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project",
    credential=DefaultAzureCredential(),
)
openai_client = client.get_openai_client()

# Create a prompt agent
print("Creating prompt agent...")
agent = client.agents.create_version(
    agent_name="test-prompt-quick",
    definition=PromptAgentDefinition(
        model="gpt-4.1",
        instructions="You are a helpful assistant. Always respond briefly.",
    ),
)
print(f"Created: {agent.name} v{agent.version}")

# Create conversation
print("Creating conversation...")
conversation = openai_client.conversations.create()
print(f"Conversation: {conversation.id}")

# Invoke
print("Invoking prompt agent...")
response = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    input="Say hello in one sentence.",
)
print(f"PROMPT AGENT RESPONSE: {response.output_text}")

# Now test the hosted agent with the same pattern
print("\nInvoking HOSTED agent with same pattern...")
try:
    response2 = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": "contoso-support-agent", "type": "agent_reference"}},
        input="Hello! What can you help me with?",
    )
    print(f"HOSTED AGENT RESPONSE: {response2.output_text}")
except Exception as e:
    print(f"HOSTED AGENT ERROR: {e}")

# Clean up
client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("\nCleaned up prompt agent")

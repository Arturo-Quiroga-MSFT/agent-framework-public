#!/usr/bin/env python3
"""
Invoke hosted agent - based on official foundry-samples quickstart
https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/quickstart/quickstart-chat-with-agent.py
"""

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Configuration
PROJECT_ENDPOINT = "https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"
AGENT_NAME = "contoso-support-agent"

# Initialize the client
client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
openai_client = client.get_openai_client()

# Step 1: Create a conversation
conversation = openai_client.conversations.create()
print(f"Created conversation (id: {conversation.id})")

# Step 2: Chat with the agent
response = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent": {"name": AGENT_NAME, "type": "agent_reference"}},
    input="Hello! What products do you support?",
)
print(f"Agent response: {response.output_text}")

# Step 3: Follow-up question
response = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent": {"name": AGENT_NAME, "type": "agent_reference"}},
    input="Can you check the status of order ORD-12345?",
)
print(f"Follow-up response: {response.output_text}")

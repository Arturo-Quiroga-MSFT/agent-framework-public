"""
Redis Demo: Conversation Persistence

Shows how RedisChatMessageStore enables agents to persist conversation
history across sessions and application restarts.
"""

import os
from pathlib import Path

from agent_framework import AgentThread
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework_redis._chat_message_store import RedisChatMessageStore
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Get environment variables
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_id = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

if not azure_endpoint:
    raise ValueError("AZURE_OPENAI_ENDPOINT not found in environment")

TICKET_ID = "TICKET-12345"

# Create RedisChatMessageStore
store = RedisChatMessageStore(
    redis_url="redis://localhost:6379",
    thread_id=f"support_{TICKET_ID}",
    max_messages=50,
)

thread = AgentThread(message_store=store)

# Create Azure OpenAI client
client = AzureOpenAIChatClient(
    endpoint=azure_endpoint,
    deployment_name=model_id,
    credential=DefaultAzureCredential(),
)

# Create and export agent
agent = client.create_agent(
    name="SupportBot",
    description=(
        "**Redis Demo: Conversation Persistence**\n\n"
        f"Shows how RedisChatMessageStore persists conversations across sessions (Ticket: {TICKET_ID}).\n\n"
        "**Session 1 - Report Issue:**\n"
        "1. Hi, I'm having issues with my order. Order number is ORD-98765.\n"
        "2. The product arrived damaged - the screen has a crack.\n"
        "3. I ordered it on November 1st and it arrived yesterday.\n\n"
        "**Then:** Refresh the page (conversation persists!)\n\n"
        "**Session 2 - Follow Up:**\n"
        "4. Hi, I'm following up on my damaged order. What are my options?\n"
        "5. Can you remind me what we discussed?\n\n"
        "**Persistence Test:** Stop DevUI server (Ctrl+C), restart, and continue the conversation!"
    ),
    instructions=(
        f"You are a helpful customer support agent working on ticket {TICKET_ID}. "
        "Be professional, empathetic, and thorough. Track all customer details. "
        "When resuming conversations, acknowledge the previous context naturally."
    ),
)

# Attach thread to agent for DevUI (note: this is a workaround for the demo)
agent._thread = thread  # type: ignore

"""
Redis Demo: Personal Assistant (Multi-Agent Isolation)

Personal assistant with isolated memory scope.
Demonstrates how different agents maintain separate memory using agent_id.
"""

import os
from pathlib import Path

from agent_framework.azure import AzureOpenAIChatClient
from agent_framework_redis._provider import RedisProvider
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

USER_ID = "alice_123"

# Create RedisProvider with personal scope
provider = RedisProvider(
    redis_url="redis://localhost:6379",
    index_name="multi_agent_devui_demo",
    prefix="multi_devui",
    application_id="devui_workshop",
    agent_id="agent_personal",  # Unique scope
    user_id=USER_ID,
    overwrite_index=False,  # Keep data across restarts
)

# Create Azure OpenAI client
client = AzureOpenAIChatClient(
    endpoint=azure_endpoint,
    deployment_name=model_id,
    credential=DefaultAzureCredential(),
)

# Create and export agent
agent = client.create_agent(
    name="PersonalAssistant",
    description=(
        "REDIS DEMO: Multi-Agent Isolation (Personal)\n"
        "\n"
        "Personal assistant with ISOLATED memory - only knows personal life info.\n"
        "\n"
        "TELL ME ABOUT YOUR PERSONAL LIFE:\n"
        "  • I love hiking and yoga on weekends.\n"
        "  • I'm training for a marathon in March.\n"
        "  • My favorite hobby is photography.\n"
        "  • I have a golden retriever named Max.\n"
        "\n"
        "THEN SWITCH TO WorkAssistant AND ASK:\n"
        "  • What do you know about my hobbies? (should say NO)\n"
        "\n"
        "SWITCH BACK AND ASK:\n"
        "  • What do you know about my personal interests?\n"
        "  • Do you know about my work projects? (should say NO)\n"
        "\n"
        "ISOLATION TEST:\n"
        "Personal info stays here, work info stays in WorkAssistant!"
    ),
    instructions=(
        "You are a personal assistant helping with personal life tasks. "
        "Remember personal preferences, hobbies, health info, and lifestyle choices. "
        "Use stored context to provide personalized recommendations. "
        "Be warm and friendly. ONLY know about personal life - you have NO access "
        "to work-related information."
    ),
    context_providers=provider,
)

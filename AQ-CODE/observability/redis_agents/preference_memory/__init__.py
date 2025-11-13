"""
Redis Demo: Smart Preference Memory

Shows how RedisProvider enables agents to remember user preferences
across sessions with persistent memory storage.
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

# Create RedisProvider with user scope
provider = RedisProvider(
    redis_url="redis://localhost:6379",
    index_name="preferences_devui_demo",
    prefix="prefs_devui",
    application_id="devui_workshop",
    agent_id="personal_assistant",
    user_id="alice_123",
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
    name="PreferenceAssistant",
    description=(
        "REDIS DEMO: Smart Preference Memory\n"
        "\n"
        "Shows how RedisProvider remembers user preferences across sessions.\n"
        "\n"
        "TRY THESE QUERIES:\n"
        "\n"
        "Session 1 - Learning:\n"
        "  • Hi! I'm Alice. I'm vegetarian and love Italian food.\n"
        "  • I prefer organic ingredients when possible.\n"
        "  • I live in Seattle, Washington.\n"
        "\n"
        "Session 2 - Using Memory:\n"
        "  • Can you recommend a restaurant for dinner tonight?\n"
        "  • What do you remember about my food preferences?\n"
        "\n"
        "Session 3 - Adding Details:\n"
        "  • I should mention I'm allergic to nuts.\n"
        "  • I prefer restaurants with outdoor seating.\n"
        "\n"
        "Session 4 - Full Personalization:\n"
        "  • Recommend a restaurant considering everything you know.\n"
        "\n"
        "MEMORY TEST: Refresh the page - preferences persist!"
    ),
    instructions=(
        "You are a helpful personal assistant that remembers user preferences. "
        "Use the provided context to personalize your responses. "
        "When learning new preferences, acknowledge them warmly. "
        "When making recommendations, always consider stored preferences. "
        "Be concise but friendly."
    ),
    context_providers=provider,
)

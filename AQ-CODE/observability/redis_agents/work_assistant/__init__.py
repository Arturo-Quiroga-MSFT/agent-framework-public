"""
Redis Demo: Work Assistant (Multi-Agent Isolation)

Work assistant with isolated memory scope.
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

# Create RedisProvider with work scope
provider = RedisProvider(
    redis_url="redis://localhost:6379",
    index_name="multi_agent_devui_demo",  # Same index
    prefix="multi_devui",
    application_id="devui_workshop",
    agent_id="agent_work",  # Different scope!
    user_id=USER_ID,  # Same user
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
    name="WorkAssistant",
    description=(
        "**Redis Demo: Multi-Agent Isolation (Work)**\n\n"
        "Work assistant with ISOLATED memory - only knows work/professional info.\n\n"
        "**Tell me about your work:**\n"
        "1. I'm working on an ML project for customer segmentation.\n"
        "2. I have team meetings every Tuesday at 2 PM.\n"
        "3. My tech stack is Python, TensorFlow, and Azure ML.\n"
        "4. I'm presenting at a conference next month.\n\n"
        "**Then switch to PersonalAssistant and ask:**\n"
        "• \"What do you know about my work projects?\" (should say NO)\n\n"
        "**Switch back and ask:**\n"
        "5. What projects am I working on?\n"
        "6. Do you know about my exercise routine? (should say NO)\n\n"
        "**Isolation Test:** Same user (alice_123), completely separate memories!"
    ),
    instructions=(
        "You are a work assistant helping with professional tasks. "
        "Remember work projects, meeting schedules, team info, and professional goals. "
        "Use stored context to provide work-focused recommendations. "
        "Be professional and efficient. ONLY know about work - you have NO access "
        "to personal life information."
    ),
    context_providers=provider,
)

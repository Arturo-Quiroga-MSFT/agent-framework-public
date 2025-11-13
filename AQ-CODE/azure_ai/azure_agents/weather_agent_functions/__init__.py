"""
Azure AI Agent: Weather & Time Assistant

Demonstrates Azure AI Agent with multiple function tools.
Uses real weather data and UTC time information.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path to import shared_utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
from shared_utils import get_real_weather

# Load environment variables - go up to azure_ai/ directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check required environment variables
project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

if not project_endpoint:
    raise ValueError("AZURE_AI_PROJECT_ENDPOINT not found in environment")


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC."


# Create Azure AI Agent with multiple tools
credential = DefaultAzureCredential()

agent = AzureAIAgentClient(
    project_endpoint=project_endpoint,
    model_deployment_name=model_deployment_name,
    async_credential=credential
).create_agent(
    name="WeatherTimeAgent",
    description=(
        "AZURE AI DEMO: Multi-Function Weather & Time Assistant\n"
        "\n"
        "Shows Azure AI Agent with multiple function tools for weather and time.\n"
        "\n"
        "TRY THESE QUERIES:\n"
        "  • What's the weather like in Seattle?\n"
        "  • What's the current UTC time?\n"
        "  • Tell me the weather in London and the current time.\n"
        "  • Compare weather in New York vs Los Angeles.\n"
        "  • What time is it now, and how's the weather in Tokyo?\n"
        "\n"
        "FEATURES:\n"
        "  • Real-time weather from OpenWeatherMap API\n"
        "  • Current UTC time\n"
        "  • Can combine multiple tools in one query\n"
        "  • Intelligent tool selection based on query\n"
        "\n"
        "TOOLS:\n"
        "  1. get_real_weather - Fetches live weather data\n"
        "  2. get_time - Returns current UTC time"
    ),
    instructions=(
        "You are a helpful assistant that provides weather and time information. "
        "Use the get_real_weather function for weather queries and get_time for time queries. "
        "You can use multiple tools in a single response if needed. "
        "Be friendly, accurate, and concise."
    ),
    tools=[get_real_weather, get_time],
)

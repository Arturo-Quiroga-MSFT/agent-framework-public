"""
Azure AI Agent: Basic Weather Assistant

Demonstrates basic Azure AI Agent with real weather data from OpenWeatherMap API.
Uses AzureCliCredential for authentication.
"""

import os
import sys
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

# Create Azure AI Agent with real weather function
credential = DefaultAzureCredential()

agent = AzureAIAgentClient(
    project_endpoint=project_endpoint,
    model_deployment_name=model_deployment_name,
    async_credential=credential
).create_agent(
    name="WeatherAgent",
    description=(
        "AZURE AI DEMO: Basic Weather Assistant\n"
        "\n"
        "Shows Azure AI Agent with real weather data from OpenWeatherMap API.\n"
        "\n"
        "TRY THESE QUERIES:\n"
        "  • What's the weather like in Seattle?\n"
        "  • How's the weather in London today?\n"
        "  • Tell me about the weather in Tokyo.\n"
        "  • Compare weather in New York and Los Angeles.\n"
        "\n"
        "FEATURES:\n"
        "  • Real-time weather data from OpenWeatherMap\n"
        "  • Temperature in Celsius and Fahrenheit\n"
        "  • Humidity and wind speed\n"
        "  • Weather conditions description\n"
        "\n"
        "AUTHENTICATION: Uses Azure CLI credentials (az login)"
    ),
    instructions="You are a helpful weather assistant. Use the get_real_weather function to provide accurate, real-time weather information. Be friendly and concise.",
    tools=get_real_weather,
)

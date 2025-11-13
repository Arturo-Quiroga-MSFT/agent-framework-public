"""
Azure AI Agent: OpenAPI Tools Integration

Demonstrates external API integration using OpenAPI specifications.
Calls REST APIs (wttr.in for weather, restcountries.com for country info)
and combines data from multiple sources intelligently.
"""

import json
import os
from pathlib import Path

from agent_framework.azure import AzureAIAgentClient
from azure.ai.agents.models import OpenApiAnonymousAuthDetails, OpenApiTool
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables - go up to azure_ai/ directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check required environment variables
project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

if not project_endpoint:
    raise ValueError("AZURE_AI_PROJECT_ENDPOINT not found in environment")

# Load OpenAPI specifications
resources_dir = Path(__file__).parent.parent.parent.parent.parent / "python" / "samples" / "getting_started" / "agents" / "resources"
weather_spec_path = resources_dir / "weather.json"
countries_spec_path = resources_dir / "countries.json"

# Create Azure AI Agent with OpenAPI tools
credential = DefaultAzureCredential()

# Load OpenAPI specs and create tools
openapi_tools = []
tool_definitions = []

try:
    if weather_spec_path.exists():
        with open(weather_spec_path) as f:
            weather_spec = json.load(f)
        
        openapi_weather = OpenApiTool(
            name="wttr_weather",
            spec=weather_spec,
            description="Get current weather information for any city or location worldwide",
            auth=OpenApiAnonymousAuthDetails()
        )
        tool_definitions.extend(openapi_weather.definitions)
    
    if countries_spec_path.exists():
        with open(countries_spec_path) as f:
            countries_spec = json.load(f)
        
        openapi_countries = OpenApiTool(
            name="restcountries",
            spec=countries_spec,
            description="Get information about countries including capital cities, currencies, population, and more",
            auth=OpenApiAnonymousAuthDetails()
        )
        tool_definitions.extend(openapi_countries.definitions)
    
    tools_available = len(tool_definitions) > 0
except Exception as e:
    print(f"Note: Could not load OpenAPI specs: {e}")
    tools_available = False

# Create agent with or without tools
if tools_available:
    agent = AzureAIAgentClient(
        project_endpoint=project_endpoint,
        model_deployment_name=model_deployment_name,
        async_credential=credential
    ).create_agent(
        name="OpenAPIToolsAgent",
        description=(
            "AZURE AI DEMO: OpenAPI Tools & API Integration\n"
            "\n"
            "Calls external REST APIs using OpenAPI specifications.\n"
            "Integrated APIs: wttr.in (weather), restcountries.com (country info)\n"
            "\n"
            "TRY THESE QUERIES:\n"
            "  • What's the weather in Bangkok?\n"
            "  • What is the capital of Thailand?\n"
            "  • What's the weather in the capital of Thailand?\n"
            "  • Which country uses THB currency?\n"
            "  • Tell me about Mexico and its current weather\n"
            "  • What's the weather in the capital of the country that uses EUR?\n"
            "\n"
            "INTEGRATED APIS:\n"
            "  • wttr.in - Real-time weather data\n"
            "  • restcountries.com - Country information database\n"
            "\n"
            "FEATURES:\n"
            "  • Multi-API orchestration\n"
            "  • Automatic request/response handling\n"
            "  • Combines data intelligently\n"
            "  • No authentication required (public APIs)\n"
            "\n"
            "EXAMPLE WORKFLOW:\n"
            "  Query: \"Weather in capital of Thailand?\"\n"
            "  1. Call countries API to find Thailand's capital (Bangkok)\n"
            "  2. Call weather API for Bangkok\n"
            "  3. Combine and present results\n"
            "\n"
            "USE CASES:\n"
            "  • Multi-source data queries\n"
            "  • API orchestration\n"
            "  • External system integration\n"
            "  • Real-time information lookup"
        ),
        instructions=(
            "You are a helpful assistant with access to external REST APIs through OpenAPI specifications. "
            "You can call the weather API (wttr.in) to get current weather for any location, "
            "and the countries API (restcountries.com) to get information about countries including their capitals, currencies, and more. "
            "\n\n"
            "When answering questions that require multiple API calls:\n"
            "1. Break down the question into steps\n"
            "2. Call the appropriate APIs in sequence\n"
            "3. Combine the results intelligently\n"
            "4. Provide a clear, comprehensive answer\n"
            "\n"
            "Always explain which APIs you're using and why. "
            "The weather API returns simple text format, while the countries API returns detailed JSON."
        ),
        tools=tool_definitions,
    )
else:
    agent = AzureAIAgentClient(
        project_endpoint=project_endpoint,
        model_deployment_name=model_deployment_name,
        async_credential=credential
    ).create_agent(
        name="OpenAPIToolsAgent",
        description=(
            "AZURE AI DEMO: OpenAPI Tools & API Integration\n"
            "\n"
            "⚠️ OpenAPI specs not found\n"
            f"Expected locations:\n"
            f"  • {weather_spec_path}\n"
            f"  • {countries_spec_path}\n"
            "\n"
            "This agent demonstrates external API integration using OpenAPI specifications."
        ),
        instructions=(
            "⚠️ OpenAPI tools are not configured. The OpenAPI specification files (weather.json, countries.json) "
            "could not be found. Please ensure the samples/resources directory contains these files. "
            "For now, I can only provide general information about OpenAPI integration."
        ),
    )

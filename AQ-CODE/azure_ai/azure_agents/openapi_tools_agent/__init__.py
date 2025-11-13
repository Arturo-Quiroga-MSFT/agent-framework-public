"""
Azure AI Agent: OpenAPI Tools Integration

Demonstrates external API integration using OpenAPI specifications.
Shows how to call REST APIs and combine data from multiple sources.
"""

import os
from pathlib import Path

from agent_framework.azure import AzureAIAgentClient
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

# Create Azure AI Agent with OpenAPI capabilities
credential = DefaultAzureCredential()

# Note: OpenAPI tool configuration requires OpenAPI spec files
# For DevUI, we create a basic agent that explains the setup
# In a full implementation, you would load OpenAPI specs and configure tools

agent = AzureAIAgentClient(
    project_endpoint=project_endpoint,
    model_deployment_name=model_deployment_name,
    async_credential=credential
).create_agent(
    name="OpenAPIToolsAgent",
    description=(
        "AZURE AI DEMO: OpenAPI Tools & API Integration\n"
        "\n"
        "Demonstrates calling external REST APIs using OpenAPI specifications.\n"
        "\n"
        "FEATURES:\n"
        "  • Automatic API integration from OpenAPI specs\n"
        "  • Multi-API orchestration\n"
        "  • Anonymous or authenticated API calls\n"
        "  • Request/response validation\n"
        "\n"
        "EXAMPLE USE CASES:\n"
        "  • Weather + Country Info API\n"
        "    Query: \"What's the weather in the capital of Thailand?\"\n"
        "    - Uses countries API to find capital\n"
        "    - Uses weather API to get current weather\n"
        "    - Combines results intelligently\n"
        "\n"
        "  • E-commerce Integration\n"
        "    - Product catalog API\n"
        "    - Inventory API\n"
        "    - Pricing API\n"
        "\n"
        "  • Business Systems\n"
        "    - CRM integration\n"
        "    - ERP systems\n"
        "    - Custom internal APIs\n"
        "\n"
        "SETUP STEPS:\n"
        "  1. Obtain OpenAPI spec (JSON/YAML)\n"
        "  2. Configure authentication (if needed)\n"
        "  3. Add API endpoints to your project\n"
        "  4. Create OpenApiTool objects\n"
        "  5. Pass tools to agent\n"
        "\n"
        "API EXAMPLES:\n"
        "  • wttr.in - Weather data\n"
        "  • restcountries.com - Country information\n"
        "  • Any OpenAPI-compliant REST API\n"
        "\n"
        "BENEFITS:\n"
        "  ✓ No manual function writing\n"
        "  ✓ Automatic parameter validation\n"
        "  ✓ Multi-step API workflows\n"
        "  ✓ Real-time data integration"
    ),
    instructions=(
        "You are a helpful assistant that can integrate with external REST APIs using OpenAPI specifications. "
        "You can call multiple APIs and combine their results to answer complex questions. "
        "Always explain which APIs you're using and how you're combining the data. "
        "\n\n"
        "Note: In this demo environment, OpenAPI tools need to be configured with actual API specifications. "
        "The full implementation requires OpenAPI spec files and may require API authentication. "
        "For a working example, refer to the azure_ai_with_openapi_tools.py sample in the samples directory."
    ),
)

"""
Azure AI Agent: Azure AI Search Integration

Demonstrates enterprise search using Azure AI Search service.
Searches indexed data with vector and hybrid search capabilities.
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
search_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "hotels-sample-index")

if not project_endpoint:
    raise ValueError("AZURE_AI_PROJECT_ENDPOINT not found in environment")

# Note: This agent requires Azure AI Search to be configured in your project
# For demo purposes, you'll need to have an Azure AI Search connection set up
# Instructions are provided in the agent description

credential = DefaultAzureCredential()

# Create agent with Azure AI Search tool
# Note: The actual search connection and tool configuration needs to be done
# through the Azure AI project setup. This is a simplified version for DevUI.
agent = AzureAIAgentClient(
    project_endpoint=project_endpoint,
    model_deployment_name=model_deployment_name,
    async_credential=credential
).create_agent(
    name="AzureSearchAgent",
    description=(
        "AZURE AI DEMO: Azure AI Search Integration\n"
        "\n"
        "Enterprise search using Azure AI Search with vector and hybrid capabilities.\n"
        "\n"
        "SETUP REQUIRED:\n"
        "  1. Create Azure AI Search service\n"
        "  2. Connect it to your Azure AI project in Foundry\n"
        "  3. Create and populate a search index\n"
        "  4. Add AZURE_SEARCH_INDEX_NAME to .env (default: hotels-sample-index)\n"
        "\n"
        "TRY THESE QUERIES (with hotels-sample-index):\n"
        "  • Find hotels near the beach\n"
        "  • Show me luxury hotels with high ratings\n"
        "  • Which hotels have pools?\n"
        "  • Find budget-friendly hotels in downtown\n"
        "\n"
        "FEATURES:\n"
        "  • Vector search for semantic matching\n"
        "  • Hybrid search (keyword + semantic)\n"
        "  • Filters and facets\n"
        "  • Relevance scoring\n"
        "\n"
        "USE CASES:\n"
        "  • Enterprise knowledge search\n"
        "  • Product catalog search\n"
        "  • Document retrieval\n"
        "  • Customer support\n"
        "\n"
        "SEARCH TYPES:\n"
        "  • Vector: Semantic similarity search\n"
        "  • Keyword: Traditional text search\n"
        "  • Hybrid: Combines both approaches"
    ),
    instructions=(
        "You are a helpful assistant that searches indexed data using Azure AI Search. "
        f"Search the '{search_index_name}' index to find relevant information. "
        "Provide detailed answers based on the search results and cite your sources. "
        "If you cannot find information, let the user know what data is available."
    ),
)

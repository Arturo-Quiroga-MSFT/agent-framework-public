"""
Azure AI Agent: File Search (RAG)

Demonstrates document search and RAG capabilities with Azure AI File Search.
Uses a sample employee PDF to answer questions about employee data.
Note: Requires vector store setup - see instructions in agent description.
"""

import os
from pathlib import Path

from agent_framework import HostedFileSearchTool, HostedVectorStoreContent
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

# Create Azure AI Agent with File Search
credential = DefaultAzureCredential()

# Check if vector store ID is configured
vector_store_id = os.getenv("FILE_SEARCH_VECTOR_STORE_ID")

# Create agent with or without file search
if vector_store_id:
    file_search_tool = HostedFileSearchTool(inputs=[HostedVectorStoreContent(vector_store_id=vector_store_id)])
    instructions_text = (
        "You are a helpful assistant that can search through uploaded employee documents to answer questions. "
        "The document contains information about Contoso Electronics employees including names, roles, departments, and contact information. "
        "Use the file search tool to find relevant information from the documents. "
        "Always cite your sources and provide specific details from the documents when available."
    )
else:
    file_search_tool = None
    sample_pdf = Path(__file__).parent.parent.parent.parent.parent / "python" / "samples" / "getting_started" / "agents" / "resources" / "employees.pdf"
    instructions_text = (
        "⚠️ FILE SEARCH NOT CONFIGURED\n\n"
        "To set up file search with the sample employee document:\n\n"
        "OPTION 1 - Run the sample script to create vector store:\n"
        f"  cd python/samples/getting_started/agents/azure_ai\n"
        f"  python azure_ai_with_file_search.py\n"
        f"  (This will create a vector store and show you the ID)\n\n"
        "OPTION 2 - Manual setup in Azure AI Foundry:\n"
        "  1. Go to https://ai.azure.com\n"
        f"  2. Upload the PDF: {sample_pdf}\n"
        "  3. Create a vector store\n"
        "  4. Copy the vector store ID\n\n"
        "Then add to your .env file:\n"
        "  FILE_SEARCH_VECTOR_STORE_ID=your-vector-store-id\n\n"
        "Restart DevUI after adding the ID.\n\n"
        "For now, I can only provide general responses without document search."
    )

agent = AzureAIAgentClient(
    project_endpoint=project_endpoint,
    model_deployment_name=model_deployment_name,
    async_credential=credential
).create_agent(
    name="FileSearchAgent",
    description=(
        "AZURE AI DEMO: File Search & RAG\n"
        "\n"
        "Searches employee documents using vector search and RAG.\n"
        "Automatically sets up vector store with sample employee PDF.\n"
        "\n"
        "TRY THESE QUERIES:\n"
        "  • Who works in the Engineering department?\n"
        "  • What is the contact information for [name]?\n"
        "  • List all managers\n"
        "  • Who has expertise in [skill]?\n"
        "  • Summarize the employee roster\n"
        "\n"
        "FEATURES:\n"
        "  • Vector search across documents\n"
        "  • Automatic document chunking\n"
        "  • Source citations in responses\n"
        "  • Semantic search capabilities\n"
        "\n"
        "DOCUMENT: employees.pdf (Contoso Electronics)\n"
        "Contains employee directory with names, roles, departments, and contact info.\n"
        "\n"
        "USE CASES:\n"
        "  • Employee directory search\n"
        "  • HR information lookup\n"
        "  • Knowledge base queries\n"
        "  • Document Q&A"
    ),
    instructions=instructions_text,
    tools=[file_search_tool] if file_search_tool else None,
)

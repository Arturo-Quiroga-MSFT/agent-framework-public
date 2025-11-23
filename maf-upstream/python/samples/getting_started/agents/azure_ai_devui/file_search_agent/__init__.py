"""
Azure AI Agent: File Search Agent

Demonstrates RAG (Retrieval-Augmented Generation) with file search using vector stores.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from agent_framework import HostedFileSearchTool, HostedVectorStoreContent
from agent_framework.azure import AzureAIClient
from agent_framework.observability import setup_observability
from azure.identity.aio import AzureCliCredential

# Load environment variables
local_env_path = Path(__file__).parent.parent.parent / "azure_ai" / ".env"
parent_env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=local_env_path)
load_dotenv(dotenv_path=parent_env_path)

# Setup observability for tracing
if os.getenv("ENABLE_OTEL", "").lower() == "true":
    app_insights_conn = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn:
        setup_observability(
            enable_sensitive_data=os.getenv("ENABLE_SENSITIVE_DATA", "").lower() == "true",
            applicationinsights_connection_string=app_insights_conn,
        )

# Get vector store ID
vector_store_id = os.getenv("FILE_SEARCH_VECTOR_STORE_ID")

if not vector_store_id:
    raise ValueError(
        "FILE_SEARCH_VECTOR_STORE_ID not found in environment variables. "
        "Run the setup_file_search.py script to create a vector store with sample data."
    )

# Create file search tool
file_search_tool = HostedFileSearchTool(
    inputs=[HostedVectorStoreContent(vector_store_id=vector_store_id)]
)

# Create the agent
credential = AzureCliCredential()

agent = AzureAIClient(async_credential=credential).create_agent(
    name="FileSearchAgent",
    description=(
        "File Search Agent - RAG with Vector Search\n"
        "\n"
        "Searches through uploaded documents using vector search (RAG pattern).\n"
        "\n"
        "TRY THESE:\n"
        "  • Who is the youngest employee?\n"
        "  • Who works in sales?\n"
        "  • Tell me about employees in the engineering department\n"
        "  • What are the contact details for employees?\n"
        "  • List all employees by department\n"
        "\n"
        "FEATURES:\n"
        "  • Vector search through documents\n"
        "  • RAG (Retrieval-Augmented Generation)\n"
        "  • Semantic similarity matching\n"
        "  • Citation of source documents\n"
        "\n"
        "NOTE: Uses pre-configured vector store with sample employee data."
    ),
    instructions=(
        "You are a helpful assistant that can search through uploaded employee files "
        "to answer questions about employees. Use the file search tool to find relevant "
        "information and provide accurate answers based on the documents."
    ),
    tools=file_search_tool,
)

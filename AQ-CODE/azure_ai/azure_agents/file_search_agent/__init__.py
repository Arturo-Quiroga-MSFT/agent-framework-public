"""
Azure AI Agent: File Search (RAG)

Demonstrates document search and RAG capabilities with Azure AI File Search.
Uses a sample employee PDF to answer questions about employee data.
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

# Note: This agent requires a pre-created vector store with uploaded documents
# For demo purposes, you'll need to create this in Azure AI Foundry first
vector_store_id = os.getenv("FILE_SEARCH_VECTOR_STORE_ID")

# Create Azure AI Agent with File Search
credential = DefaultAzureCredential()

# If no vector store ID is provided, create agent without it (will show instructions)
if vector_store_id:
    file_search_tool = HostedFileSearchTool(inputs=[HostedVectorStoreContent(vector_store_id=vector_store_id)])
    instructions_text = (
        "You are a helpful assistant that can search through uploaded documents to answer questions. "
        "Use the file search tool to find relevant information from the documents. "
        "Always cite your sources when providing answers."
    )
else:
    file_search_tool = None
    instructions_text = (
        "⚠️ FILE SEARCH NOT CONFIGURED\n\n"
        "To use file search, you need to:\n"
        "1. Go to Azure AI Foundry (https://ai.azure.com)\n"
        "2. Upload documents to create a vector store\n"
        "3. Add FILE_SEARCH_VECTOR_STORE_ID to your .env file\n"
        "4. Restart DevUI\n\n"
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
        "Demonstrates document search and retrieval-augmented generation (RAG).\n"
        "\n"
        "SETUP REQUIRED:\n"
        "  1. Create vector store in Azure AI Foundry\n"
        "  2. Upload documents (PDF, TXT, DOCX, etc.)\n"
        "  3. Add FILE_SEARCH_VECTOR_STORE_ID to .env\n"
        "  4. Restart DevUI\n"
        "\n"
        "TRY THESE QUERIES (after setup):\n"
        "  • What information is in the documents?\n"
        "  • Summarize the key points from the files\n"
        "  • Find specific information about [topic]\n"
        "  • Who/what is mentioned in the documents?\n"
        "\n"
        "FEATURES:\n"
        "  • Vector search across uploaded documents\n"
        "  • Automatic chunking and embedding\n"
        "  • Source citations in responses\n"
        "  • Supports PDF, TXT, DOCX, and more\n"
        "\n"
        "USE CASES:\n"
        "  • Document Q&A\n"
        "  • Knowledge base search\n"
        "  • Research assistance\n"
        "  • Policy/procedure lookup"
    ),
    instructions=instructions_text,
    tools=file_search_tool,
)

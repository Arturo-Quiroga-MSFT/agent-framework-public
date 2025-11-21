"""
File Search Agent with Vector Store Q&A
"""

from pathlib import Path

from agent_framework import ChatAgent, HostedFileSearchTool, HostedVectorStoreContent
from agent_framework._clients import ChatClientProtocol
from agent_framework_ag_ui import AgentFrameworkAgent


async def create_file_search_agent(
    chat_client: ChatClientProtocol,
    file_path: str | Path,
    document_name: str,
) -> AgentFrameworkAgent:
    """
    Create file search agent for document Q&A.
    
    Args:
        chat_client: MAF chat client
        file_path: Path to the document file
        document_name: Display name of the document
    """
    
    # Upload file and create vector store
    file = await chat_client.project_client.agents.files.upload_and_poll(
        file_path=str(file_path), purpose="assistants"
    )
    
    vector_store = await chat_client.project_client.agents.vector_stores.create_and_poll(
        file_ids=[file.id], name=f"copilotkit_demo_{document_name}"
    )
    
    # Create file search tool
    file_search_tool = HostedFileSearchTool(
        inputs=[HostedVectorStoreContent(vector_store_id=vector_store.id)]
    )
    
    # Customize instructions based on document type
    if "employee" in document_name.lower():
        doc_context = "employee files to answer questions about employees"
    elif "product" in document_name.lower():
        doc_context = "product catalogs to help customers find products"
    elif "research" in document_name.lower() or "ai" in document_name.lower():
        doc_context = "AI research papers, citing sections when possible"
    else:
        doc_context = "document files to answer questions"
    
    base_agent = ChatAgent(
        name="file_search_agent",
        instructions=f"""You are a helpful assistant that can search through {doc_context}.

Your capabilities:
- Search and retrieve information from uploaded documents
- Answer questions based on document content
- Provide specific quotes and references from the documents
- Cite page numbers or sections when available

Best practices:
1. ALWAYS base your answers on the document content provided
2. Never use general knowledge - only information from the files
3. Quote directly when possible and indicate the source
4. If information isn't in the document, say so clearly
5. For follow-up questions, reference previous answers for context

Current document: {document_name}

Remember previous questions and answers in this conversation.
""",
        chat_client=chat_client,
        tools=file_search_tool,
    )
    
    return AgentFrameworkAgent(
        agent=base_agent,
        name="FileSearchAgent",
        description=f"Document Q&A agent for {document_name}",
        state_schema={
            "document_name": {
                "type": "string",
                "description": "Name of the current document being searched",
            }
        },
        require_confirmation=False,
    )

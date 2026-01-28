"""
Streamlit Demo App for Azure AI Agent Samples

This interactive app demonstrates various Azure AI agent capabilities including:
- Basic chat interactions
- Function tools (weather API)
- Thread management for conversation context

Run with: streamlit run streamlit_azure_ai_demo.py
"""

import asyncio
import os
import sys
from pathlib import Path
from io import BytesIO
from datetime import datetime
import re

import httpx
import streamlit as st
from dotenv import load_dotenv
from pydantic import Field
from typing import Annotated
from PIL import Image

# Add parent directories to path to import agent framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_framework import ChatAgent, HostedCodeInterpreterTool, HostedWebSearchTool, HostedFileSearchTool, HostedVectorStoreContent, AgentResponse, HostedMCPTool, ChatMessage
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential, AzureCliCredential
from azure.ai.agents.models import FileInfo, VectorStore

# Load environment variables - use absolute path
env_path = Path(__file__).resolve().parent.parent / ".env"
print(f"[DEBUG] Loading .env from: {env_path}")
print(f"[DEBUG] .env exists: {env_path.exists()}")
load_dotenv(dotenv_path=env_path)
print(f"[DEBUG] OPENWEATHER_API_KEY loaded: {bool(os.getenv('OPENWEATHER_API_KEY'))}")
print(f"[DEBUG] FIRECRAWL_API_KEY loaded: {bool(os.getenv('FIRECRAWL_API_KEY'))}")
print(f"[DEBUG] AZURE_AI_PROJECT_ENDPOINT loaded: {bool(os.getenv('AZURE_AI_PROJECT_ENDPOINT'))}")

# Create output directory for generated images
OUTPUT_DIR = Path(__file__).resolve().parent / "generated_plots"
OUTPUT_DIR.mkdir(exist_ok=True)

# Ensure minimal session state keys exist early (prevents AttributeError on first run)
if "messages" not in st.session_state:
    st.session_state.messages = {}
if "service_thread_id" not in st.session_state:
    st.session_state.service_thread_id = None
if "azureaisearch_thread_id" not in st.session_state:
    st.session_state.azureaisearch_thread_id = None
if "bing_thread_id" not in st.session_state:
    st.session_state.bing_thread_id = None
if "filesearch_thread_id" not in st.session_state:
    st.session_state.filesearch_thread_id = None


# Page config
st.set_page_config(
    page_title="Azure AI Agent Demo",
    page_icon="🤖",
    layout="wide"
)

# Real weather function
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the current weather for a given location using OpenWeatherMap API."""
    print(f"[DEBUG] get_weather function called with location: {location}")
    api_key = os.getenv("OPENWEATHER_API_KEY")
    print(f"[DEBUG] API key present: {bool(api_key)}")
    
    if not api_key:
        return f"Error: OPENWEATHER_API_KEY not found in environment variables."
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        result = f"The weather in {location} is {description} with a temperature of {temp}°C (feels like {feels_like}°C) and {humidity}% humidity."
        print(f"[DEBUG] Weather result: {result}")
        return result
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{location}' not found."
        return f"Error fetching weather data: {e}"
    except Exception as e:
        print(f"[DEBUG] Exception in get_weather: {e}")
        return f"Error: {str(e)}"


async def run_basic_chat(user_query: str, demo_type: str) -> str:
    """Run a basic chat interaction without persistent thread."""
    client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
    
    if demo_type == "weather":
        instructions = "You are a helpful weather assistant. When asked about weather, ALWAYS use the get_weather function to fetch real-time weather data. Never apologize or say you can't access weather data - you have the get_weather function available."
    else:
        instructions = "You are a helpful assistant that can answer questions."
    
    async with ChatAgent(
        chat_client=client,
        instructions=instructions,
        tools=[get_weather] if demo_type == "weather" else None,
    ) as agent:
        result = await agent.run(user_query)
        return str(result.text)


async def run_threaded_chat(user_query: str) -> str:
    """Run chat with persistent thread for conversation context."""
    client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
    
    async with ChatAgent(
        chat_client=client,
        instructions="You are a helpful weather assistant. When asked about weather, ALWAYS use the get_weather function to fetch real-time weather data. Remember previous conversations in this thread.",
        tools=[get_weather],
    ) as agent:
        # Create or reuse thread
        if st.session_state.service_thread_id:
            thread = agent.get_new_thread(service_thread_id=st.session_state.service_thread_id)
        else:
            thread = agent.get_new_thread()
        
        result = await agent.run(user_query, thread=thread, store=True)
        
        # Store thread ID for next message
        if thread.service_thread_id:
            st.session_state.service_thread_id = thread.service_thread_id
        
        return str(result.text)


async def run_code_interpreter(user_query: str) -> tuple[str, list[bytes]]:
    """Run agent with code interpreter capability. Returns (text_response, list_of_image_bytes)."""
    async with AzureCliCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as chat_client:
            agent = chat_client.create_agent(
                name="CodingAgent",
                instructions="You are a helpful assistant that can write and execute Python code to solve problems. When asked to perform calculations or data analysis, write Python code and execute it using the code interpreter. Always describe what the code does and show the results.",
                tools=HostedCodeInterpreterTool(),
            )
            
            # Create a thread and run the agent
            thread = agent.get_new_thread()
            result = await agent.run(user_query, thread=thread, store=True)
            
            result_text = str(result.text)
            image_data_list = []
            
            # Get messages from the thread to check for image outputs
            try:
                messages_iterator = chat_client.project_client.agents.messages.list(thread_id=thread.service_thread_id)
                
                async for message in messages_iterator:
                    for content_item in message.content:
                        if hasattr(content_item, 'image_file') and content_item.image_file:
                            file_id = content_item.image_file.file_id
                            
                            try:
                                file_content_stream = await chat_client.project_client.agents.files.get_content(file_id)
                                chunks = []
                                async for chunk in file_content_stream:
                                    chunks.append(chunk)
                                
                                file_content = b''.join(chunks)
                                image_data_list.append(file_content)
                                
                                # Save the image
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"plot_{timestamp}_{file_id}.png"
                                filepath = OUTPUT_DIR / filename
                                with open(filepath, 'wb') as f:
                                    f.write(file_content)
                                
                                result_text += f"\n\n📊 **Plot generated successfully!**\n*Saved to: `{filepath.name}`*"
                            except Exception as e:
                                result_text += f"\n\n⚠️ **Note:** Found image (ID: {file_id}), but couldn't download: {str(e)}"
                
            except Exception as e:
                print(f"[DEBUG] Error retrieving messages: {e}")
            
            return result_text, image_data_list


async def run_bing_grounding(user_query: str) -> tuple[str, dict]:
    """Run agent with Bing grounding/web search capability.
    
    Returns:
        Tuple of (response_text, metadata) where metadata contains timing and token usage.
    """
    import time
    start_time = time.time()
    
    client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
    
    bing_search_tool = HostedWebSearchTool(
        name="Bing Grounding Search",
        description="Search the web for current information using Bing",
    )
    
    async with ChatAgent(
        chat_client=client,
        name="BingSearchAgent",
        instructions="You are a helpful assistant that can search the web for current information. Use the Bing search tool to find up-to-date information and provide accurate, well-sourced answers. Always cite your sources when possible. Remember previous searches and questions in this conversation.",
        tools=bing_search_tool,
    ) as agent:
        # Create or reuse thread for conversation memory
        if st.session_state.bing_thread_id:
            thread = agent.get_new_thread(service_thread_id=st.session_state.bing_thread_id)
        else:
            thread = agent.get_new_thread()
        
        result = await agent.run(user_query, thread=thread, store=True)
                
        # Store thread ID for next message to maintain conversation history
        if thread.service_thread_id:
            st.session_state.bing_thread_id = thread.service_thread_id
        
        # Get the response text
        response_text = str(result.text)
    
    # Extract timing and token usage
    elapsed_time = time.time() - start_time
    metadata = {
        'elapsed_time': elapsed_time,
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'total_tokens': 0
    }
            
    # Extract token usage from result.usage_details
    if hasattr(result, 'usage_details') and result.usage_details:
        usage = result.usage_details
        metadata['prompt_tokens'] = (
            getattr(usage, 'input_token_count', None) or
            getattr(usage, 'input_tokens', None) or
            getattr(usage, 'prompt_tokens', 0)
        )
        metadata['completion_tokens'] = (
            getattr(usage, 'output_token_count', None) or
            getattr(usage, 'output_tokens', None) or
            getattr(usage, 'completion_tokens', 0)
        )
        metadata['total_tokens'] = (
            getattr(usage, 'total_token_count', None) or
            getattr(usage, 'total_tokens', 0)
        )
    
    # Simply replace citation markers with numbered references
    # Pattern: 【3:0†source】
    citation_pattern = r'【[^】]+】'
    citation_counter = 0
    
    def replace_citation(match):
        nonlocal citation_counter
        citation_counter += 1
        return f'[{citation_counter}]'
    
    response_text = re.sub(citation_pattern, replace_citation, response_text)
    
    # Add note about citations
    if citation_counter > 0:
        response_text += f"\n\n*Note: Response includes {citation_counter} citations from web sources*"
    
    # Add usage stats at the bottom
    response_text += f"\n\n⏱️ Time: {elapsed_time:.2f}s | 🔢 Tokens: {metadata['total_tokens']} (↑{metadata['prompt_tokens']} ↓{metadata['completion_tokens']})"
    
    return response_text, metadata


async def run_file_search(query: str, document_name: str = "employees.pdf") -> tuple[str, dict]:
    """
    Run file search agent to answer questions about uploaded documents.
    
    Args:
        query: User's question
        document_name: Name of the document to search (employees.pdf, product_catalog.txt, or ai_research.pdf)
    """
    import time
    
    start_time = time.time()
    client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
    file: FileInfo | None = None
    vector_store: VectorStore | None = None
    
    try:
        # Determine file path based on selection
        if document_name == "employees.pdf":
            file_path = Path(__file__).resolve().parent.parent / "python" / "samples" / "getting_started" / "agents" / "resources" / "employees.pdf"
            instructions = "You are a helpful assistant that can search through employee files to answer questions about employees. Always base your answers on the file content provided."
        elif document_name == "product_catalog.txt":
            file_path = Path(__file__).resolve().parent / "sample_documents" / "product_catalog.txt"
            instructions = "You are a helpful sales assistant that can search through product catalogs to help customers. Always base your answers on the product catalog file provided, not on general knowledge."
        elif document_name == "ai_research.pdf":
            file_path = Path(__file__).resolve().parent / "sample_documents" / "ai_research.pdf"
            instructions = "You are a research assistant that can search through AI research papers. Always base your answers on the specific paper provided, citing sections when possible."
        else:
            return f"❌ Error: Unknown document '{document_name}'", {}
        
        if not file_path.exists():
            return f"❌ Error: Document not found at {file_path}", {}
        
        print(f"[DEBUG] Uploading file: {file_path.name}")
        
        # Upload file
        file = await client.project_client.agents.files.upload_and_poll(
            file_path=str(file_path), purpose="assistants"
        )
        print(f"[DEBUG] File uploaded, ID: {file.id}")
        
        # Create vector store
        vector_store = await client.project_client.agents.vector_stores.create_and_poll(
            file_ids=[file.id], name=f"streamlit_demo_{document_name}"
        )
        print(f"[DEBUG] Vector store created, ID: {vector_store.id}")
        
        # Create file search tool
        file_search_tool = HostedFileSearchTool(
            inputs=[HostedVectorStoreContent(vector_store_id=vector_store.id)]
        )
        print(f"[DEBUG] File search tool created with vector store")
        
        # Create agent with file search
        async with ChatAgent(
            chat_client=client,
            name="FileSearchAgent",
            instructions=instructions + " Remember previous questions and answers in this conversation to provide contextual responses.",
            tools=file_search_tool,
        ) as agent:
            # Create or reuse thread for conversation memory
            if st.session_state.filesearch_thread_id:
                thread = agent.get_new_thread(service_thread_id=st.session_state.filesearch_thread_id)
            else:
                thread = agent.get_new_thread()
            
            print(f"[DEBUG] Running query against {document_name}...")
            result: AgentResponse = await agent.run(query, thread=thread, store=True)
            
            # Store thread ID for next message to maintain conversation history
            if thread.service_thread_id:
                st.session_state.filesearch_thread_id = thread.service_thread_id
            
            response_text = str(result.text)
            print(f"[DEBUG] Got response, length: {len(response_text)} chars")
            
            # Extract timing and token usage
            elapsed_time = time.time() - start_time
            metadata = {
                'elapsed_time': elapsed_time,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0
            }
            
            # Extract token usage
            if hasattr(result, 'usage_details') and result.usage_details:
                usage = result.usage_details
                metadata['prompt_tokens'] = (
                    getattr(usage, 'input_token_count', None) or
                    getattr(usage, 'input_tokens', None) or
                    getattr(usage, 'prompt_tokens', 0)
                )
                metadata['completion_tokens'] = (
                    getattr(usage, 'output_token_count', None) or
                    getattr(usage, 'output_tokens', None) or
                    getattr(usage, 'completion_tokens', 0)
                )
                metadata['total_tokens'] = (
                    getattr(usage, 'total_token_count', None) or
                    getattr(usage, 'total_tokens', 0)
                )
            
            # Add document info and usage stats
            response_text += f"\n\n📄 Source: {document_name}"
            response_text += f"\n⏱️ Time: {elapsed_time:.2f}s | 🔢 Tokens: {metadata['total_tokens']} (↑{metadata['prompt_tokens']} ↓{metadata['completion_tokens']})"
            
            # Cleanup inside the agent context
            try:
                print(f"[DEBUG] Cleaning up vector store and file...")
                if vector_store:
                    await client.project_client.agents.vector_stores.delete(vector_store.id)
                if file:
                    await client.project_client.agents.files.delete(file.id)
                print(f"[DEBUG] Cleanup successful")
            except Exception as e:
                print(f"[DEBUG] Cleanup error (inside context): {e}")
            
            return response_text, metadata
            
    except Exception as e:
        print(f"[DEBUG] Error in file search: {e}")
        return f"❌ Error: {str(e)}", {}
    finally:
        # Final cleanup - refresh client if needed
        try:
            if vector_store or file:
                # Refresh client since ChatAgent may have closed it
                cleanup_client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
                try:
                    if vector_store:
                        await cleanup_client.project_client.agents.vector_stores.delete(vector_store.id)
                    if file:
                        await cleanup_client.project_client.agents.files.delete(file.id)
                except Exception as e:
                    # Ignore cleanup errors
                    pass
                finally:
                    await cleanup_client.close()
        except Exception:
            pass


async def run_azure_ai_search(query: str) -> tuple[str, dict]:
    """
    Run agent with Azure AI Search for searching indexed hotel data.
    
    Args:
        query: User's search query
    
    Returns:
        Tuple of (response_text, metadata) with timing and token usage.
    """
    import time
    
    start_time = time.time()
    
    client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
    
    # Create Azure AI Search tool
    azure_ai_search_tool = HostedFileSearchTool(
        additional_properties={
            "index_name": "hotels-sample-index",  # Name of your search index
            "query_type": "simple",  # Use simple search
            "top_k": 10,  # Get more comprehensive results
        },
    )
    
    async with ChatAgent(
        chat_client=client,
        name="HotelSearchAgent",
        instructions="You are a helpful travel assistant that searches hotel information. Provide detailed, accurate information based on the search results. Remember previous searches and questions in this conversation.",
        tools=azure_ai_search_tool,
    ) as agent:
        # Create or reuse thread for conversation memory
        if st.session_state.azureaisearch_thread_id:
            thread = agent.get_new_thread(service_thread_id=st.session_state.azureaisearch_thread_id)
        else:
            thread = agent.get_new_thread()
        
        # Run the agent with the query
        result = await agent.run(query, thread=thread, store=True)
        response_text = str(result.text)
        
        # Store thread ID for next message to maintain conversation history
        if thread.service_thread_id:
            st.session_state.azureaisearch_thread_id = thread.service_thread_id
    
    # Extract timing and token usage
    elapsed_time = time.time() - start_time
    metadata = {
        'elapsed_time': elapsed_time,
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'total_tokens': 0
    }
    
    # Extract token usage from result.usage_details
    if hasattr(result, 'usage_details') and result.usage_details:
        usage = result.usage_details
        metadata['prompt_tokens'] = (
            getattr(usage, 'input_token_count', None) or
            getattr(usage, 'input_tokens', None) or
            getattr(usage, 'prompt_tokens', 0)
        )
        metadata['completion_tokens'] = (
            getattr(usage, 'output_token_count', None) or
            getattr(usage, 'output_tokens', None) or
            getattr(usage, 'completion_tokens', 0)
        )
        metadata['total_tokens'] = (
            getattr(usage, 'total_token_count', None) or
            getattr(usage, 'total_tokens', 0)
        )
    
    # Add search indicator and usage stats
    response_text += f"\n\n🔍 Powered by: Azure AI Search (hotels-sample-index)"
    response_text += f"\n⏱️ Time: {elapsed_time:.2f}s | 🔢 Tokens: {metadata['total_tokens']} (↑{metadata['prompt_tokens']} ↓{metadata['completion_tokens']})"
    
    return response_text, metadata


async def run_firecrawl_mcp(query: str, api_key: str) -> tuple[str, dict]:
    """
    Run agent with Firecrawl MCP for web scraping and content extraction.
    
    Args:
        query: User's question or URL to scrape
        api_key: Firecrawl API key
    
    Returns:
        Tuple of (response_text, metadata) with timing and token usage.
    """
    import time
    from agent_framework import ChatMessage
    
    start_time = time.time()
    
    client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
    
    # Create Firecrawl MCP tool
    # Firecrawl hosted MCP server format: https://mcp.firecrawl.dev/{API_KEY}/v2/mcp
    firecrawl_url = f"https://mcp.firecrawl.dev/{api_key}/v2/mcp"
    firecrawl_tool = HostedMCPTool(
        name="Firecrawl Web Scraper",
        url=firecrawl_url,
    )
    
    async with ChatAgent(
        chat_client=client,
        name="FirecrawlAgent",
        instructions="You are a helpful web research assistant with access to Firecrawl for web scraping and content extraction. Use Firecrawl to fetch web pages, extract clean content, and provide accurate information from websites. Always cite your sources.",
        tools=firecrawl_tool,
    ) as agent:
        # Create a thread for this conversation
        thread = agent.get_new_thread()
        
        # Run the agent with the query
        result = await agent.run(query, thread=thread, store=True)
                
        # Handle any user input requests (function call approvals)
        # For demo purposes, we auto-approve all function calls
        while len(result.user_input_requests) > 0:
            new_input = []
            for user_input_needed in result.user_input_requests:
                # Auto-approve the function call for demo purposes
                print(f"[DEBUG] Auto-approving Firecrawl function call: {user_input_needed.function_call.name}")
                new_input.append(
                    ChatMessage(
                        role="user",
                        contents=[user_input_needed.create_response(True)],  # Auto-approve
                    )
                )
            
            # Continue the run with approvals
            result = await agent.run(new_input, thread=thread, store=True)
    
    response_text = str(result.text)
    
    # Extract timing and token usage
    elapsed_time = time.time() - start_time
    metadata = {
        'elapsed_time': elapsed_time,
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'total_tokens': 0
    }
    
    # Extract token usage from result.usage_details
    if hasattr(result, 'usage_details') and result.usage_details:
        usage = result.usage_details
        metadata['prompt_tokens'] = (
            getattr(usage, 'input_token_count', None) or
            getattr(usage, 'input_tokens', None) or
            getattr(usage, 'prompt_tokens', 0)
        )
        metadata['completion_tokens'] = (
            getattr(usage, 'output_token_count', None) or
            getattr(usage, 'output_tokens', None) or
            getattr(usage, 'completion_tokens', 0)
        )
        metadata['total_tokens'] = (
            getattr(usage, 'total_token_count', None) or
            getattr(usage, 'total_tokens', 0)
        )
    
    # Add Firecrawl indicator and usage stats
    response_text += f"\n\n🔥 Powered by: Firecrawl MCP (Web Scraper)"
    response_text += f"\n⏱️ Time: {elapsed_time:.2f}s | 🔢 Tokens: {metadata['total_tokens']} (↑{metadata['prompt_tokens']} ↓{metadata['completion_tokens']})"
    
    return response_text, metadata


async def run_hosted_mcp(query: str) -> tuple[str, dict]:
    """
    Run agent with Hosted MCP capability (Model Context Protocol).
    Demonstrates connection to hosted MCP servers like Microsoft Learn.
    
    Returns:
        Tuple of (response_text, metadata) with timing and token usage.
    """
    import time
    from agent_framework import ChatMessage
    
    start_time = time.time()
    
    client = AzureAIAgentClient(async_credential=DefaultAzureCredential())
    
    # Create Hosted MCP tool connected to Microsoft Learn MCP server
    mcp_tool = HostedMCPTool(
        name="Microsoft Learn MCP",
        url="https://learn.microsoft.com/api/mcp",
    )
    
    async with ChatAgent(
        chat_client=client,
        name="MCPAgent",
        instructions="You are a helpful assistant with access to Microsoft Learn documentation through MCP (Model Context Protocol). Use the MCP tool to search Microsoft's official documentation to provide accurate, up-to-date information about Microsoft products, Azure services, and developer technologies.",
        tools=mcp_tool,
    ) as agent:
        # Create a thread for this conversation
        thread = agent.get_new_thread()
        
        # Run the agent with the query
        result = await agent.run(query, thread=thread, store=True)
        
        # Handle any user input requests (function call approvals)
        # For demo purposes, we auto-approve all function calls
        while len(result.user_input_requests) > 0:
            new_input = []
            for user_input_needed in result.user_input_requests:
                # Auto-approve the function call for demo purposes
                print(f"[DEBUG] Auto-approving MCP function call: {user_input_needed.function_call.name}")
                new_input.append(
                    ChatMessage(
                        role="user",
                        contents=[user_input_needed.create_response(True)],  # Auto-approve
                    )
                )
            
            # Continue the run with approvals
            result = await agent.run(new_input, thread=thread, store=True)
    
    response_text = str(result.text)
    
    # Extract timing and token usage
    elapsed_time = time.time() - start_time
    metadata = {
        'elapsed_time': elapsed_time,
        'prompt_tokens': 0,
        'completion_tokens': 0,
        'total_tokens': 0
    }
    
    # Extract token usage from result.usage_details
    if hasattr(result, 'usage_details') and result.usage_details:
        usage = result.usage_details
        metadata['prompt_tokens'] = (
            getattr(usage, 'input_token_count', None) or
            getattr(usage, 'input_tokens', None) or
            getattr(usage, 'prompt_tokens', 0)
        )
        metadata['completion_tokens'] = (
            getattr(usage, 'output_token_count', None) or
            getattr(usage, 'output_tokens', None) or
            getattr(usage, 'completion_tokens', 0)
        )
        metadata['total_tokens'] = (
            getattr(usage, 'total_token_count', None) or
            getattr(usage, 'total_tokens', 0)
        )
    
    # Add MCP indicator and usage stats
    response_text += f"\n\n🔗 Powered by: Microsoft Learn MCP (Hosted)"
    response_text += f"\n⏱️ Time: {elapsed_time:.2f}s | 🔢 Tokens: {metadata['total_tokens']} (↑{metadata['prompt_tokens']} ↓{metadata['completion_tokens']})"
    
    return response_text, metadata


def main():
    st.title("🤖 Azure AI Agent Demo")
    st.markdown("Interactive demo of Azure AI Agent Framework capabilities")
    
    # Sidebar for demo selection
    st.sidebar.header("Demo Selection")
    demo_mode = st.sidebar.radio(
        "Choose a demo:",
        [
            "Basic Chat",
            "Weather Function Tool",
            "Threaded Conversation",
            "Code Interpreter",
            "Bing Grounding",
            "File Search",
            "Azure AI Search",
            "Firecrawl MCP",
            "Hosted MCP"
        ]
    )
    
    # Display demo description
    if demo_mode == "Basic Chat":
        st.subheader("Basic Chat Demo")
        st.markdown("""
        This demo shows a simple chat interaction with an Azure AI agent.
        Each query is independent (no conversation history).
        """)
        
        st.markdown("**Example:**")
        if st.button("💬 Tell me a fun fact about artificial intelligence", key="basic_ex1"):
            st.session_state.current_prompt = "Tell me a fun fact about artificial intelligence"
            st.rerun()
        
        demo_key = "basic"
        
    elif demo_mode == "Weather Function Tool":
        st.subheader("Weather Function Tool Demo")
        st.markdown("""
        This demo showcases function calling with a real weather API.
        The agent can fetch live weather data using the OpenWeatherMap API.
        """)
        
        st.markdown("**Example:**")
        if st.button("🌤️ What's the weather like in Toronto?", key="weather_ex1"):
            st.session_state.current_prompt = "What's the weather like in Toronto?"
            st.rerun()
        
        demo_key = "weather"
        
    elif demo_mode == "Threaded Conversation":
        st.subheader("Threaded Conversation Demo")
        st.markdown("""
        This demo maintains conversation context across multiple queries.
        The agent remembers previous messages and can reference them.
        """)
        
        st.markdown("**Examples (try in order):**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("1️⃣ What's the weather in Toronto?", key="thread_ex1"):
                st.session_state.current_prompt = "What's the weather in Toronto?"
                st.rerun()
        with col2:
            if st.button("2️⃣ What about Mexico City?", key="thread_ex2"):
                st.session_state.current_prompt = "What about Mexico City?"
                st.rerun()
        with col3:
            if st.button("3️⃣ Which one is warmer?", key="thread_ex3"):
                st.session_state.current_prompt = "Which one is warmer?"
                st.rerun()
        
        demo_key = "thread"
        
        if st.sidebar.button("🔄 Reset Conversation"):
            st.session_state.service_thread_id = None
            st.session_state.messages[demo_key] = []
            st.rerun()
    
    elif demo_mode == "Code Interpreter":
        st.subheader("Code Interpreter Demo")
        st.markdown("""
        This demo shows the agent's ability to write and execute Python code.
        Perfect for mathematical calculations, data analysis, and visualizations.
        
        **Try these examples (click to use):** 
        """)
        
        # Create expandable sections for different categories
        with st.expander("📊 Mathematical Visualizations", expanded=True):
            if st.button("🌀 Plot the Mandelbrot set fractal", key="code_ex_mandel"):
                st.session_state.current_prompt = "Plot the Mandelbrot set fractal"
                st.rerun()
            if st.button("🎯 Create a 3D surface plot of z = sin(x) * cos(y) for x and y from -5 to 5", key="code_ex_3d"):
                st.session_state.current_prompt = "Create a 3D surface plot of z = sin(x) * cos(y) for x and y from -5 to 5"
                st.rerun()
            if st.button("🌺 Create a polar plot of r = sin(5θ) to make a flower pattern", key="code_ex_polar"):
                st.session_state.current_prompt = "Create a polar plot of r = sin(5θ) to make a flower pattern"
                st.rerun()
            if st.button("🔢 Visualize the Fibonacci spiral with the first 15 numbers", key="code_ex_fib"):
                st.session_state.current_prompt = "Visualize the Fibonacci spiral with the first 15 numbers"
                st.rerun()
            if st.button("🔥 Plot a heatmap of a correlation matrix for 5 random variables", key="code_ex_heat"):
                st.session_state.current_prompt = "Plot a heatmap of a correlation matrix for 5 random variables"
                st.rerun()
        
        with st.expander("📈 Data Analysis Plots"):
            if st.button("📊 Generate 1000 points with scatter plot and regression line", key="code_ex_scatter"):
                st.session_state.current_prompt = "Generate a dataset of 1000 points and create a scatter plot with a regression line"
                st.rerun()
            if st.button("📦 Create box plots comparing three normal distributions", key="code_ex_box"):
                st.session_state.current_prompt = "Create box plots comparing three normal distributions with different means"
                st.rerun()
            if st.button("📉 Generate histogram with KDE overlay for bimodal distribution", key="code_ex_hist"):
                st.session_state.current_prompt = "Generate a histogram with kernel density estimation overlay for a bimodal distribution"
                st.rerun()
        
        with st.expander("🎨 Creative Visualizations"):
            if st.button("🥧 Create pie chart with exploded slices", key="code_ex_pie"):
                st.session_state.current_prompt = "Create a pie chart with exploded slices showing market share data"
                st.rerun()
            if st.button("🎲 Generate a Voronoi diagram with 20 random points", key="code_ex_voronoi"):
                st.session_state.current_prompt = "Generate a Voronoi diagram with 20 random points"
                st.rerun()
        
        with st.expander("🔬 Scientific Plots"):
            if st.button("🎯 Plot projectile trajectory with different launch angles", key="code_ex_proj"):
                st.session_state.current_prompt = "Plot the trajectory of a projectile with different launch angles"
                st.rerun()
            if st.button("🦋 Visualize the Lorenz attractor (butterfly effect)", key="code_ex_lorenz"):
                st.session_state.current_prompt = "Visualize the Lorenz attractor (butterfly effect)"
                st.rerun()
            if st.button("⚡ Create phase diagram for damped harmonic oscillator", key="code_ex_phase"):
                st.session_state.current_prompt = "Create a phase diagram for a damped harmonic oscillator"
                st.rerun()
        
        with st.expander("🌈 Patterns & Geometry"):
            if st.button("🎨 Create colormap visualization showing matplotlib colormaps", key="code_ex_cmap"):
                st.session_state.current_prompt = "Create a colormap visualization showing different matplotlib colormaps"
                st.rerun()
            if st.button("🌀 Generate a spirograph pattern", key="code_ex_spiro"):
                st.session_state.current_prompt = "Generate a spirograph pattern with different parameters"
                st.rerun()
        
        with st.expander("🧮 Simple Examples"):
            if st.button("💯 Calculate the factorial of 100", key="code_ex_fact"):
                st.session_state.current_prompt = "Calculate the factorial of 100"
                st.rerun()
            if st.button("🔢 Generate Fibonacci sequence up to 1000", key="code_ex_fib_seq"):
                st.session_state.current_prompt = "Generate the Fibonacci sequence up to 1000"
                st.rerun()
            if st.button("📐 Create a plot of y = x^2 from -10 to 10", key="code_ex_simple"):
                st.session_state.current_prompt = "Create a plot of y = x^2 from -10 to 10"
                st.rerun()
        
        demo_key = "code"
    
    elif demo_mode == "Bing Grounding":
        st.subheader("Bing Grounding Demo")
        st.markdown("""
        This demo uses Bing web search to find current, real-time information.
        The agent can search the web and provide up-to-date answers with sources.
        
        💬 **Conversation Memory:** This scenario maintains conversation history, so you can ask
        follow-up questions and the agent will remember previous searches and context.
        
        **Examples (click to use):** 
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 What are the latest developments in AI?", key="bing_ex1"):
                st.session_state.current_prompt = "What are the latest developments in AI?"
                st.rerun()
            if st.button("🌤️ What's the current weather forecast for next week?", key="bing_ex3"):
                st.session_state.current_prompt = "What's the current weather forecast for next week?"
                st.rerun()
        with col2:
            if st.button("🏆 Who won the most recent Nobel Prize in Physics?", key="bing_ex2"):
                st.session_state.current_prompt = "Who won the most recent Nobel Prize in Physics?"
                st.rerun()
            if st.button("💬 Tell me more about that", key="bing_ex4"):
                st.session_state.current_prompt = "Tell me more about that"
                st.rerun()
        
        st.markdown("**Note:** Requires Bing Grounding connection configured in Azure AI Foundry.")
        demo_key = "bing"
        
        # Add clear memory button
        if st.button("🔄 Clear Conversation Memory", key="clear_bing_memory"):
            st.session_state.bing_thread_id = None
            st.success("✅ Conversation memory cleared! Starting fresh.")
    
    elif demo_mode == "File Search":
        st.subheader("File Search Demo")
        st.markdown("""
        This demo demonstrates document search and Q&A capabilities.
        Select a document and ask questions about its content.
        
        💬 **Conversation Memory:** This scenario maintains conversation history, so you can ask
        follow-up questions that reference previous answers from the same document.
        """)
        
        # Document selector
        selected_doc = st.selectbox(
            "Choose a document:",
            ["employees.pdf", "product_catalog.txt", "ai_research.pdf"],
            help="Select which document to search"
        )
        
        # Add clear memory button
        if st.button("🔄 Clear Conversation Memory", key="clear_filesearch_memory"):
            st.session_state.filesearch_thread_id = None
            st.success("✅ Conversation memory cleared! Starting fresh.")
        
        # Show relevant example questions based on selected document with clickable buttons
        if selected_doc == "employees.pdf":
            st.markdown("**Example questions about employees (click to use):**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👶 Who is the youngest employee?", key="file_emp1"):
                    st.session_state.current_prompt = "Who is the youngest employee?"
                    st.rerun()
                if st.button("📊 List all employees in marketing", key="file_emp3"):
                    st.session_state.current_prompt = "List all employees in marketing"
                    st.rerun()
                if st.button("🤝 I have a customer request, who can help me?", key="file_emp5"):
                    st.session_state.current_prompt = "I have a customer request, who can help me?"
                    st.rerun()
            with col2:
                if st.button("💼 Who works in sales?", key="file_emp2"):
                    st.session_state.current_prompt = "Who works in sales?"
                    st.rerun()
                if st.button("🏆 Who has the most experience?", key="file_emp4"):
                    st.session_state.current_prompt = "Who has the most experience?"
                    st.rerun()
        elif selected_doc == "product_catalog.txt":
            st.markdown("**Example questions about products (click to use):**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💻 What laptops do you have available?", key="file_prod1"):
                    st.session_state.current_prompt = "What laptops do you have available?"
                    st.rerun()
                if st.button("💰 What's the most expensive product?", key="file_prod3"):
                    st.session_state.current_prompt = "What's the most expensive product?"
                    st.rerun()
                if st.button("🎧 What accessories are available?", key="file_prod5"):
                    st.session_state.current_prompt = "What accessories are available?"
                    st.rerun()
            with col2:
                if st.button("💵 Show me all products under $500", key="file_prod2"):
                    st.session_state.current_prompt = "Show me all products under $500"
                    st.rerun()
                if st.button("📱 Do you have any smartphones in stock?", key="file_prod4"):
                    st.session_state.current_prompt = "Do you have any smartphones in stock?"
                    st.rerun()
                if st.button("📋 What's the warranty policy?", key="file_prod6"):
                    st.session_state.current_prompt = "What's the warranty policy?"
                    st.rerun()
        else:  # ai_research.pdf
            st.markdown("**Example questions about the research paper (click to use):**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 What is this paper about?", key="file_ai1"):
                    st.session_state.current_prompt = "What is this paper about?"
                    st.rerun()
                if st.button("🔍 What are the main contributions of this paper?", key="file_ai3"):
                    st.session_state.current_prompt = "What are the main contributions of this paper?"
                    st.rerun()
                if st.button("📊 What datasets were used in the experiments?", key="file_ai5"):
                    st.session_state.current_prompt = "What datasets were used in the experiments?"
                    st.rerun()
            with col2:
                if st.button("🤖 What is the Transformer architecture?", key="file_ai2"):
                    st.session_state.current_prompt = "What is the Transformer architecture?"
                    st.rerun()
                if st.button("⚡ How does the attention mechanism work?", key="file_ai4"):
                    st.session_state.current_prompt = "How does the attention mechanism work?"
                    st.rerun()
        
        demo_key = "filesearch"
        
        # Store selected document in session state
        if "selected_document" not in st.session_state:
            st.session_state.selected_document = selected_doc
        else:
            st.session_state.selected_document = selected_doc
    
    elif demo_mode == "Azure AI Search":
        st.subheader("Azure AI Search Demo")
        st.markdown("""
        This demo uses **Azure AI Search** to search through indexed hotel data.
        The agent can search and retrieve information from the hotels-sample-index.
        
        🔍 **What is Azure AI Search?** A powerful search service that enables full-text search,
        semantic search, and vector search over your indexed content.
        
        💬 **Conversation Memory:** This scenario maintains conversation history, so you can ask
        follow-up questions and the agent will remember previous searches and context.
        
        **Example questions (click to use):**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏨 Search for Stay-Kay City Hotel details", key="search_ex1"):
                st.session_state.current_prompt = "Search the hotel database for Stay-Kay City Hotel and give me detailed information"
                st.rerun()
            if st.button("🏖️ Hotels available near the beach?", key="search_ex3"):
                st.session_state.current_prompt = "What hotels are available near the beach?"
                st.rerun()
            if st.button("🎯 Hotels with conference facilities?", key="search_ex5"):
                st.session_state.current_prompt = "Tell me about hotels with conference facilities"
                st.rerun()
        with col2:
            if st.button("⭐ Find luxury hotels with good ratings", key="search_ex2"):
                st.session_state.current_prompt = "Find luxury hotels with good ratings"
                st.rerun()
            if st.button("💰 Show me budget-friendly hotels", key="search_ex4"):
                st.session_state.current_prompt = "Show me budget-friendly hotels"
                st.rerun()
            if st.button("🔍 Which has the best rating?", key="search_ex6"):
                st.session_state.current_prompt = "Which of those has the best rating?"
                st.rerun()
        
        st.markdown("**Note:** Requires Azure AI Search connection configured in your Azure AI project with the 'hotels-sample-index' deployed.")
        demo_key = "azureaisearch"
        
        # Add clear memory button
        if st.button("🔄 Clear Conversation Memory", key="clear_azureaisearch_memory"):
            st.session_state.azureaisearch_thread_id = None
            st.success("✅ Conversation memory cleared! Starting fresh.")
    
    elif demo_mode == "Firecrawl MCP":
        st.subheader("Firecrawl MCP Demo")
        st.markdown("""
        This demo uses **Firecrawl** through MCP for advanced web scraping and content extraction.
        Firecrawl can extract clean, LLM-ready content from any website.
        
        🔥 **What is Firecrawl?** Firecrawl is a powerful web scraping service that converts 
        websites into clean markdown, handles JavaScript rendering, and bypasses bot detection.
        
        **Example questions (click to use):**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📰 Scrape and summarize Hacker News top stories", key="fire_ex1"):
                st.session_state.current_prompt = "Scrape the content from https://news.ycombinator.com and summarize the top stories"
                st.rerun()
            if st.button("📄 Extract content from example.com/article", key="fire_ex3"):
                st.session_state.current_prompt = "Extract and analyze the main content from https://example.com/article"
                st.rerun()
            if st.button("📚 Summarize Python documentation", key="fire_ex5"):
                st.session_state.current_prompt = "Summarize the documentation at https://docs.python.org/3/"
                st.rerun()
        with col2:
            if st.button("🤖 Latest TechCrunch AI articles", key="fire_ex2"):
                st.session_state.current_prompt = "What are the latest articles on https://techcrunch.com about AI?"
                st.rerun()
            if st.button("💰 Get OpenAI pricing information", key="fire_ex4"):
                st.session_state.current_prompt = "Get the pricing information from https://openai.com/pricing"
                st.rerun()
        
        st.markdown("**Note:** API key is loaded from .env file (FIRECRAWL_API_KEY)")
        
        # Load API key from environment
        firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        
        if not firecrawl_api_key:
            st.warning("⚠️ Firecrawl API key not found in .env file.")
            st.info("💡 Please add FIRECRAWL_API_KEY to your .env file. Get an API key at [firecrawl.dev](https://firecrawl.dev)")
        else:
            st.success("✅ Firecrawl API key loaded from .env file")
        
        demo_key = "firecrawl"
        
        # Store API key in session state
        st.session_state.firecrawl_api_key = firecrawl_api_key
    
    else:  # Hosted MCP
        st.subheader("Hosted MCP Demo")
        st.markdown("""
        This demo uses **Model Context Protocol (MCP)** to connect to hosted external tools.
        Currently connected to **Microsoft Learn MCP** for searching official Microsoft documentation.
        
        🔗 **What is MCP?** MCP is a standardized protocol that allows AI agents to connect to 
        external tools and data sources. [Learn more](./MCP_EXPLAINED.md)
        
        **Example questions (click to use):**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Create Azure storage account using az cli", key="mcp_ex1"):
                st.session_state.current_prompt = "How do I create an Azure storage account using az cli?"
                st.rerun()
            if st.button("🌐 Deploy Python web app to Azure", key="mcp_ex3"):
                st.session_state.current_prompt = "How do I deploy a Python web app to Azure?"
                st.rerun()
            if st.button("🤖 Azure OpenAI Service capabilities", key="mcp_ex5"):
                st.session_state.current_prompt = "Explain Azure OpenAI Service capabilities"
                st.rerun()
        with col2:
            if st.button("🤖 What is the Microsoft Agent Framework?", key="mcp_ex2"):
                st.session_state.current_prompt = "What is the Microsoft Agent Framework?"
                st.rerun()
            if st.button("⚡ Azure Functions best practices", key="mcp_ex4"):
                st.session_state.current_prompt = "What are the best practices for Azure Functions?"
                st.rerun()
            if st.button("🔐 Set up Azure resource authentication", key="mcp_ex6"):
                st.session_state.current_prompt = "How do I set up authentication for Azure resources?"
                st.rerun()
        
        st.markdown("**Note:** This uses a **hosted** MCP server (managed by Microsoft). For the difference between hosted and local MCP, see `MCP_EXPLAINED.md`.")
        demo_key = "hostedmcp"
    
    # Initialize message history for this demo
    # Ensure session state containers exist before accessing them (fixes AttributeError when session state is empty)
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    if "service_thread_id" not in st.session_state:
        st.session_state.service_thread_id = None
    if demo_key not in st.session_state.messages:
        st.session_state.messages[demo_key] = []
    
    # Display chat history
    for message in st.session_state.messages[demo_key]:
        with st.chat_message(message["role"]):
            if demo_key == "bing":
                st.markdown(message["content"], unsafe_allow_html=True)
            else:
                st.markdown(message["content"])
    
    # Check if there's a prompt from a button click
    if "current_prompt" in st.session_state and st.session_state.current_prompt:
        prompt = st.session_state.current_prompt
        st.session_state.current_prompt = None  # Clear it so it doesn't repeat
    else:
        # Chat input
        prompt = st.chat_input("Ask me anything...")
    
    if prompt:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages[demo_key].append({"role": "user", "content": prompt})
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if demo_key == "thread":
                        response = asyncio.run(run_threaded_chat(prompt))
                        st.markdown(response)
                        st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    elif demo_key == "code":
                        response, images = asyncio.run(run_code_interpreter(prompt))
                        st.markdown(response)
                        
                        # Display any generated images
                        if images:
                            for img_data in images:
                                try:
                                    image = Image.open(BytesIO(img_data))
                                    st.image(image, caption="Generated Plot", use_column_width=True)
                                    # Provide an immediate download button for the generated plot (per-session)
                                    try:
                                        # Construct a friendly filename using timestamp
                                        file_name = f"plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                                        st.download_button(
                                            label="Download plot",
                                            data=img_data,
                                            file_name=file_name,
                                            mime="image/png",
                                        )
                                    except Exception as e:
                                        # If download button fails for any reason, show a small warning but continue
                                        st.warning(f"Could not create download button: {e}")
                                except Exception as e:
                                    st.warning(f"Could not display image: {e}")
                        
                        st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    elif demo_key == "bing":
                        response, metadata = asyncio.run(run_bing_grounding(prompt))
                        
                        # Display with proper markdown rendering for citations
                        st.markdown(response, unsafe_allow_html=True)
                        st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    elif demo_key == "filesearch":
                        selected_document = st.session_state.get("selected_document", "employees.pdf")
                        response, metadata = asyncio.run(run_file_search(prompt, selected_document))
                        st.markdown(response)
                        st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    elif demo_key == "azureaisearch":
                        response, metadata = asyncio.run(run_azure_ai_search(prompt))
                        st.markdown(response)
                        st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    elif demo_key == "firecrawl":
                        # Check if API key is loaded from environment
                        firecrawl_key = st.session_state.get("firecrawl_api_key", "")
                        if not firecrawl_key:
                            error_msg = "❌ Error: Firecrawl API key not found in .env file. Please add FIRECRAWL_API_KEY to your .env file."
                            st.error(error_msg)
                            st.session_state.messages[demo_key].append({"role": "assistant", "content": error_msg})
                        else:
                            response, metadata = asyncio.run(run_firecrawl_mcp(prompt, firecrawl_key))
                            st.markdown(response)
                            st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    elif demo_key == "hostedmcp":
                        response, metadata = asyncio.run(run_hosted_mcp(prompt))
                        st.markdown(response)
                        st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    else:
                        response = asyncio.run(run_basic_chat(prompt, demo_key))
                        st.markdown(response)
                        st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages[demo_key].append({"role": "assistant", "content": error_msg})
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ About")
    st.sidebar.markdown("""
    This demo uses:
    - **Azure AI Agent Framework**
    - **OpenWeatherMap API** (for weather data)
    - **Code Interpreter** (for Python execution)
    - **Bing Grounding** (for web search)
    - **File Search** (for document Q&A)
    - **Azure AI Search** (for hotel search)
    - **Firecrawl MCP** (web scraping)
    - **Hosted MCP** (Model Context Protocol)
    - **Azure CLI Authentication**
    
    Make sure you're logged in with `az login` before running.
    
    📚 Learn about [MCP and Web Scraping](./MCP_EXPLAINED.md)
    """)
    
    # Display environment info
    with st.sidebar.expander("Environment Info"):
        st.text(f"Endpoint: {os.getenv('AZURE_AI_PROJECT_ENDPOINT', 'Not set')[:50]}...")
        st.text(f"Model: {os.getenv('AZURE_AI_MODEL_DEPLOYMENT_NAME', 'Not set')}")
        st.text(f"Weather API: {'✓ Configured' if os.getenv('OPENWEATHER_API_KEY') else '✗ Not set'}")
        bing_conn = os.getenv('BING_CONNECTION_NAME') or os.getenv('BING_CONNECTION_ID')
        st.text(f"Bing Grounding: {'✓ Configured' if bing_conn else '✗ Not set'}")
        st.text(f"Plots saved to: {OUTPUT_DIR.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()

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

from agent_framework import ChatAgent, HostedCodeInterpreterTool, HostedWebSearchTool, HostedFileSearchTool, HostedVectorStoreContent, AgentRunResponse, HostedMCPTool, ChatMessage
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import FileInfo, VectorStore

# Load environment variables - use absolute path
env_path = Path(__file__).resolve().parent.parent / "python" / "samples" / "getting_started" / ".env"
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
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            if demo_type == "weather":
                instructions = "You are a helpful weather assistant. When asked about weather, ALWAYS use the get_weather function to fetch real-time weather data. Never apologize or say you can't access weather data - you have the get_weather function available."
            else:
                instructions = "You are a helpful assistant that can answer questions."
            
            agent = ChatAgent(
                chat_client=client,
                instructions=instructions,
                tools=[get_weather] if demo_type == "weather" else None,
            )
            
            result = await agent.run(user_query)
            return str(result.text)


async def run_threaded_chat(user_query: str) -> str:
    """Run chat with persistent thread for conversation context."""
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            agent = ChatAgent(
                chat_client=client,
                instructions="You are a helpful weather assistant. When asked about weather, ALWAYS use the get_weather function to fetch real-time weather data. Remember previous conversations in this thread.",
                tools=[get_weather],
            )
            
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
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            agent = client.create_agent(
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
                messages_iterator = client.project_client.agents.messages.list(thread_id=thread.service_thread_id)
                
                async for message in messages_iterator:
                    for content_item in message.content:
                        if hasattr(content_item, 'image_file') and content_item.image_file:
                            file_id = content_item.image_file.file_id
                            
                            try:
                                file_content_stream = await client.project_client.agents.files.get_content(file_id)
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
    
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            bing_search_tool = HostedWebSearchTool(
                name="Bing Grounding Search",
                description="Search the web for current information using Bing",
            )
            
            agent = ChatAgent(
                chat_client=client,
                name="BingSearchAgent",
                instructions="You are a helpful assistant that can search the web for current information. Use the Bing search tool to find up-to-date information and provide accurate, well-sourced answers. Always cite your sources when possible. Remember previous searches and questions in this conversation.",
                tools=bing_search_tool,
            )
            
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
                # Try different attribute name patterns
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
            
            # Extract citation URLs from the response
            citations_map = {}
            
            # Try method 1: Extract from result.raw_representation.messages (ChatMessage objects)
            if hasattr(result, 'raw_representation') and hasattr(result.raw_representation, 'messages'):
                messages = result.raw_representation.messages
                print(f"[DEBUG] Found {len(messages)} ChatMessage objects")
                
                for msg_idx, msg in enumerate(messages):
                    if hasattr(msg, 'contents'):
                        contents = msg.contents
                        print(f"[DEBUG] Message has {len(contents)} content items")
                        
                        for content_idx, content in enumerate(contents):
                            print(f"[DEBUG] Content {content_idx}: type={type(content).__name__}")
                            
                            # Check what attributes the TextContent object has
                            if hasattr(content, '__dict__'):
                                attrs = [attr for attr in dir(content) if not attr.startswith('_')]
                                print(f"[DEBUG] TextContent attributes: {attrs}")
                            
                            # Try different ways to access annotations:
                            # 1. Direct annotations attribute on content
                            if hasattr(content, 'annotations'):
                                annotations = content.annotations
                                print(f"[DEBUG] Found {len(annotations) if annotations else 0} annotations on content.annotations")
                                
                                if annotations:
                                    for ann in annotations:
                                        if hasattr(ann, 'type') and ann.type == 'url_citation':
                                            citation_text = getattr(ann, 'text', '')
                                            if hasattr(ann, 'url_citation'):
                                                url_cit = ann.url_citation
                                                url = getattr(url_cit, 'url', '')
                                                title = getattr(url_cit, 'title', url)
                                                if citation_text and url:
                                                    citations_map[citation_text] = {'url': url, 'title': title}
                                                    print(f"[DEBUG] ✓ Extracted: {citation_text} -> {url[:50]}...")
                            
                            # 2. Check content.text if it's an object (not just string)
                            elif hasattr(content, 'text'):
                                text_obj = content.text
                                if hasattr(text_obj, 'annotations'):
                                    annotations = text_obj.annotations
                                    print(f"[DEBUG] Found {len(annotations) if annotations else 0} annotations on content.text.annotations")
            
            # Try method 2: Check raw_representation list (this is where the raw event stream is)
            if not citations_map and hasattr(result, 'raw_representation'):
                raw_obj = result.raw_representation
                if hasattr(raw_obj, 'raw_representation'):
                    raw_list = raw_obj.raw_representation
                    
                    if isinstance(raw_list, list) and len(raw_list) > 0:
                        print(f"[DEBUG] Searching {len(raw_list)} items in raw_list for ThreadMessage objects")
                        
                        # Look for ThreadMessage objects (these are agent_framework objects, not dicts)
                        for idx, item in enumerate(reversed(raw_list)):
                            # Check if it's a ThreadMessage object
                            if type(item).__name__ == 'ThreadMessage':
                                status = getattr(item, 'status', None)
                                status_str = str(status) if status else 'unknown'
                                
                                # Check if status indicates completion (handle both enum and string)
                                is_completed = (
                                    'COMPLETED' in status_str.upper() or
                                    status_str == 'completed' or
                                    (hasattr(status, 'value') and status.value == 'completed')
                                )
                                
                                if is_completed:
                                    msg_id = getattr(item, 'id', 'unknown')
                                    print(f"[DEBUG] Found completed ThreadMessage: id={msg_id}")
                                    
                                    # Try to get annotations from raw_representation of the ThreadMessage
                                    if hasattr(item, 'raw_representation') and item.raw_representation:
                                        raw_msg = item.raw_representation
                                        print(f"[DEBUG] ThreadMessage.raw_representation type: {type(raw_msg)}")
                                        print(f"[DEBUG] ThreadMessage.raw_representation is dict: {isinstance(raw_msg, dict)}")
                                        
                                        # If raw_representation is a dict with content
                                        if isinstance(raw_msg, dict):
                                            print(f"[DEBUG] Raw dict keys: {list(raw_msg.keys())}")
                                            content_list = raw_msg.get('content', [])
                                            print(f"[DEBUG] Raw dict has {len(content_list)} content items")
                                            
                                            if content_list:
                                                import json
                                                print(f"[DEBUG] Full content structure:")
                                                print(json.dumps(content_list, indent=2, default=str))
                                            
                                            for content in content_list:
                                                if isinstance(content, dict) and content.get('type') == 'text':
                                                    text_data = content.get('text', {})
                                                    annotations = text_data.get('annotations', [])
                                                    print(f"[DEBUG] Found {len(annotations)} annotations in raw dict")
                                                    
                                                    for ann in annotations:
                                                        if isinstance(ann, dict) and ann.get('type') == 'url_citation':
                                                            citation_text = ann.get('text', '')
                                                            url_citation = ann.get('url_citation', {})
                                                            url = url_citation.get('url', '')
                                                            title = url_citation.get('title', url)
                                                            if citation_text and url:
                                                                citations_map[citation_text] = {'url': url, 'title': title}
                                                                print(f"[DEBUG] ✓ Extracted: {citation_text} -> {url[:50]}...")
                                        else:
                                            print(f"[DEBUG] raw_representation is not a dict, trying to convert...")
                                            if hasattr(raw_msg, '__dict__'):
                                                raw_dict = vars(raw_msg)
                                                print(f"[DEBUG] Converted to dict, keys: {list(raw_dict.keys())}")
                                    else:
                                        print(f"[DEBUG] ThreadMessage has no raw_representation or it's None")
                                    
                                    # If we found citations, stop searching
                                    if citations_map:
                                        break
            
            if citations_map:
                print(f"✓ Extracted {len(citations_map)} citations from Bing response")
            
            # Now replace citations in the response text with numbered references
            citation_counter = 0
            citation_references = []
            
            def replace_citation(match):
                nonlocal citation_counter
                citation_text = match.group(0)  # e.g., 【3:0†source】
                
                if citation_text in citations_map:
                    citation_counter += 1
                    citation_info = citations_map[citation_text]
                    url = citation_info['url']
                    title = citation_info['title']
                    citation_references.append({'num': citation_counter, 'url': url, 'title': title})
                    return f'[{citation_counter}]'
                else:
                    citation_counter += 1
                    return f'[{citation_counter}]'
            
            # Pattern: 【3:0†source】
            citation_pattern = r'【[^】]+】'
            response_text = re.sub(citation_pattern, replace_citation, response_text)
            
            # Add references section at the bottom
            if citation_references:
                response_text += "\n\n---\n**References:**\n\n"
                for ref in citation_references:
                    response_text += f"[{ref['num']}] {ref['title']}  \n{ref['url']}\n\n"
            
            # Add usage statistics
            response_text += "---\n"
            response_text += f"⏱️ **Time:** {metadata['elapsed_time']:.2f}s | "
            response_text += f"🔢 **Tokens:** {metadata['total_tokens']} "
            response_text += f"(↑{metadata['prompt_tokens']} ↓{metadata['completion_tokens']})"

            # Debug prints for verification
            print(f"[DEBUG] Extracted token metadata: {metadata}")
            print(f"[DEBUG] Extracted {len(citation_references)} citation references")

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
            result: AgentRunResponse = await agent.run(query, thread=thread, store=True)
            
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
    
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            # Create Azure AI Search tool
            azure_ai_search_tool = HostedFileSearchTool(
                additional_properties={
                    "index_name": "hotels-sample-index",  # Name of your search index
                    "query_type": "simple",  # Use simple search
                    "top_k": 10,  # Get more comprehensive results
                },
            )
            
            agent = ChatAgent(
                chat_client=client,
                name="HotelSearchAgent",
                instructions="You are a helpful travel assistant that searches hotel information. Provide detailed, accurate information based on the search results. Remember previous searches and questions in this conversation.",
                tools=azure_ai_search_tool,
            )
            
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
    
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            # Create Firecrawl MCP tool
            # Firecrawl hosted MCP server format: https://mcp.firecrawl.dev/{API_KEY}/v2/mcp
            firecrawl_url = f"https://mcp.firecrawl.dev/{api_key}/v2/mcp"
            firecrawl_tool = HostedMCPTool(
                name="Firecrawl Web Scraper",
                url=firecrawl_url,
            )
            
            agent = ChatAgent(
                chat_client=client,
                name="FirecrawlAgent",
                instructions="You are a helpful web research assistant with access to Firecrawl for web scraping and content extraction. Use Firecrawl to fetch web pages, extract clean content, and provide accurate information from websites. Always cite your sources.",
                tools=firecrawl_tool,
            )
            
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
    
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            # Create Hosted MCP tool connected to Microsoft Learn MCP server
            mcp_tool = HostedMCPTool(
                name="Microsoft Learn MCP",
                url="https://learn.microsoft.com/api/mcp",
            )
            
            agent = ChatAgent(
                chat_client=client,
                name="MCPAgent",
                instructions="You are a helpful assistant with access to Microsoft Learn documentation through MCP (Model Context Protocol). Use the MCP tool to search Microsoft's official documentation to provide accurate, up-to-date information about Microsoft products, Azure services, and developer technologies.",
                tools=mcp_tool,
            )
            
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
        
        **Example:** Try asking "Tell me a fun fact about artificial intelligence"
        """)
        demo_key = "basic"
        
    elif demo_mode == "Weather Function Tool":
        st.subheader("Weather Function Tool Demo")
        st.markdown("""
        This demo showcases function calling with a real weather API.
        The agent can fetch live weather data using the OpenWeatherMap API.
        
        **Example:** Try "What's the weather like in Toronto?"
        """)
        demo_key = "weather"
        
    elif demo_mode == "Threaded Conversation":
        st.subheader("Threaded Conversation Demo")
        st.markdown("""
        This demo maintains conversation context across multiple queries.
        The agent remembers previous messages and can reference them.
        
        **Example:** 
        1. "What's the weather in Toronto?"
        2. "What about Mexico City?"
        3. "Which one is warmer?"
        """)
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
        
        **Try these examples:** 
        """)
        
        # Create expandable sections for different categories
        with st.expander("📊 Mathematical Visualizations"):
            st.markdown("""
            - "Create a 3D surface plot of z = sin(x) * cos(y) for x and y from -5 to 5"
            - "Plot the Mandelbrot set fractal"
            - "Create a polar plot of r = sin(5θ) to make a flower pattern"
            - "Visualize the Fibonacci spiral with the first 15 numbers"
            - "Plot a heatmap of a correlation matrix for 5 random variables"
            """)
        
        with st.expander("📈 Data Analysis Plots"):
            st.markdown("""
            - "Generate a dataset of 1000 points and create a scatter plot with a regression line"
            - "Create box plots comparing three normal distributions with different means"
            - "Generate a histogram with kernel density estimation overlay for a bimodal distribution"
            """)
        
        with st.expander("🎨 Creative Visualizations"):
            st.markdown("""
            - "Create a pie chart with exploded slices showing market share data"
            - "Generate a Voronoi diagram with 20 random points"
            """)
        
        with st.expander("🔬 Scientific Plots"):
            st.markdown("""
            - "Plot the trajectory of a projectile with different launch angles"
            - "Visualize the Lorenz attractor (butterfly effect)"
            - "Create a phase diagram for a damped harmonic oscillator"
            """)
        
        with st.expander("🌈 Patterns & Geometry"):
            st.markdown("""
            - "Create a colormap visualization showing different matplotlib colormaps"
            - "Generate a spirograph pattern with different parameters"
            """)
        
        with st.expander("🧮 Simple Examples"):
            st.markdown("""
            - "Calculate the factorial of 100"
            - "Generate the Fibonacci sequence up to 1000"
            - "Create a plot of y = x^2 from -10 to 10"
            """)
        
        demo_key = "code"
    
    elif demo_mode == "Bing Grounding":
        st.subheader("Bing Grounding Demo")
        st.markdown("""
        This demo uses Bing web search to find current, real-time information.
        The agent can search the web and provide up-to-date answers with sources.
        
        💬 **Conversation Memory:** This scenario maintains conversation history, so you can ask
        follow-up questions and the agent will remember previous searches and context.
        
        **Example:** 
        - "What are the latest developments in AI?"
        - "Who won the most recent Nobel Prize in Physics?"
        - "What's the current weather forecast for next week?"
        - **Follow-up:** "Tell me more about that" (references previous search)
        
        **Note:** Requires Bing Grounding connection configured in Azure AI Foundry.
        """)
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
        
        # Show relevant example questions based on selected document
        if selected_doc == "employees.pdf":
            st.markdown("""
            **Example questions about employees:**
            - "Who is the youngest employee?"
            - "Who works in sales?"
            - "List all employees in marketing"
            - "Who has the most experience?"
            - "I have a customer request, who can help me?"
            """)
        elif selected_doc == "product_catalog.txt":
            st.markdown("""
            **Example questions about products:**
            - "What laptops do you have available?"
            - "Show me all products under $500"
            - "What's the most expensive product?"
            - "Do you have any smartphones in stock?"
            - "What accessories are available?"
            - "What's the warranty policy?"
            """)
        else:  # ai_research.pdf
            st.markdown("""
            **Example questions about the research paper:**
            - "What is this paper about?"
            - "What is the Transformer architecture?"
            - "What are the main contributions of this paper?"
            - "How does the attention mechanism work?"
            - "What datasets were used in the experiments?"
            """)
        
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
        
        **Example questions:**
        - "Search the hotel database for Stay-Kay City Hotel and give me detailed information"
        - "Find luxury hotels with good ratings"
        - "What hotels are available near the beach?"
        - "Show me budget-friendly hotels"
        - "Tell me about hotels with conference facilities"
        - **Follow-up:** "Which of those has the best rating?" (references previous results)
        
        **Note:** Requires Azure AI Search connection configured in your Azure AI project
        with the 'hotels-sample-index' deployed.
        """)
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
        
        **Example questions:**
        - "Scrape the content from https://news.ycombinator.com and summarize the top stories"
        - "What are the latest articles on https://techcrunch.com about AI?"
        - "Extract and analyze the main content from https://example.com/article"
        - "Get the pricing information from https://openai.com/pricing"
        - "Summarize the documentation at https://docs.python.org/3/"
        
        **Note:** API key is loaded from .env file (FIRECRAWL_API_KEY)
        """)
        
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
        
        **Example questions:**
        - "How do I create an Azure storage account using az cli?"
        - "What is the Microsoft Agent Framework?"
        - "How do I deploy a Python web app to Azure?"
        - "What are the best practices for Azure Functions?"
        - "Explain Azure OpenAI Service capabilities"
        - "How do I set up authentication for Azure resources?"
        
        **Note:** This uses a **hosted** MCP server (managed by Microsoft).
        For the difference between hosted and local MCP, see `MCP_EXPLAINED.md`.
        """)
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
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
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

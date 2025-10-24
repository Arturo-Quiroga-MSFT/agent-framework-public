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

import httpx
import streamlit as st
from dotenv import load_dotenv
from pydantic import Field
from typing import Annotated
from PIL import Image

# Add parent directories to path to import agent framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_framework import ChatAgent, HostedCodeInterpreterTool, HostedWebSearchTool, AgentRunResponse
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Load environment variables - use absolute path
env_path = Path(__file__).resolve().parent.parent / "python" / "samples" / "getting_started" / ".env"
print(f"[DEBUG] Loading .env from: {env_path}")
print(f"[DEBUG] .env exists: {env_path.exists()}")
load_dotenv(dotenv_path=env_path)
print(f"[DEBUG] OPENWEATHER_API_KEY loaded: {bool(os.getenv('OPENWEATHER_API_KEY'))}")
print(f"[DEBUG] AZURE_AI_PROJECT_ENDPOINT loaded: {bool(os.getenv('AZURE_AI_PROJECT_ENDPOINT'))}")

# Create output directory for generated images
OUTPUT_DIR = Path(__file__).resolve().parent / "generated_plots"
OUTPUT_DIR.mkdir(exist_ok=True)


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


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = {}
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "agent" not in st.session_state:
    st.session_state.agent = None


async def run_basic_chat(user_query: str, demo_type: str) -> str:
    """Run a basic chat interaction without persistent thread."""
    async with AzureCliCredential() as credential:
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
    # Check if we have an existing thread ID to continue conversation
    if "service_thread_id" not in st.session_state:
        st.session_state.service_thread_id = None
    
    async with AzureCliCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            agent = ChatAgent(
                chat_client=client,
                instructions="You are a helpful weather assistant. When asked about weather, ALWAYS use the get_weather function to fetch real-time weather data. Never apologize or say you can't access weather data - you have the get_weather function available. Remember previous conversations in this thread.",
                tools=[get_weather],
            )
            
            # Create or reuse thread
            if st.session_state.service_thread_id:
                # Continue existing conversation with the service thread ID
                thread = agent.get_new_thread(service_thread_id=st.session_state.service_thread_id)
            else:
                # Start new conversation
                thread = agent.get_new_thread()
            
            result = await agent.run(user_query, thread=thread, store=True)
            
            # Store thread ID for next message
            if thread.service_thread_id:
                st.session_state.service_thread_id = thread.service_thread_id
            
            return str(result.text)


async def run_code_interpreter(user_query: str) -> tuple[str, list[bytes]]:
    """Run agent with code interpreter capability. Returns (text_response, list_of_image_bytes)."""
    async with AzureCliCredential() as credential:
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
                print(f"[DEBUG] Checking for image outputs in thread: {thread.service_thread_id}")
                
                # messages.list() returns an async iterator, not an awaitable
                messages_iterator = client.project_client.agents.messages.list(thread_id=thread.service_thread_id)
                
                # Iterate through messages
                async for message in messages_iterator:
                    print(f"[DEBUG] Message role: {message.role}")
                    
                    # Check content items in the message
                    for content_item in message.content:
                        content_type = type(content_item).__name__
                        print(f"[DEBUG] Content type: {content_type}")
                        
                        # Check if it's an image file content
                        if hasattr(content_item, 'image_file') and content_item.image_file:
                            file_id = content_item.image_file.file_id
                            print(f"[DEBUG] Found image file ID: {file_id}")
                            
                            try:
                                # Get file content - it returns an async generator
                                file_content_stream = await client.project_client.agents.files.get_content(file_id)
                                
                                # Read all chunks from the async generator
                                chunks = []
                                async for chunk in file_content_stream:
                                    chunks.append(chunk)
                                
                                # Combine all chunks into bytes
                                file_content = b''.join(chunks)
                                print(f"[DEBUG] Downloaded image, size: {len(file_content)} bytes")
                                image_data_list.append(file_content)
                                
                                # Save the image to local directory
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"plot_{timestamp}_{file_id}.png"
                                filepath = OUTPUT_DIR / filename
                                with open(filepath, 'wb') as f:
                                    f.write(file_content)
                                print(f"[DEBUG] Saved image to: {filepath}")
                                
                                result_text += f"\n\n📊 **Plot generated successfully!**\n*Saved to: `{filepath.name}`*"
                            except Exception as e:
                                print(f"[DEBUG] Error downloading file {file_id}: {e}")
                                result_text += f"\n\n⚠️ **Note:** Found image (ID: {file_id}), but couldn't download: {str(e)}"
                
                print(f"[DEBUG] Total images found: {len(image_data_list)}")
                
            except Exception as e:
                print(f"[DEBUG] Error retrieving messages: {e}")
                import traceback
                traceback.print_exc()
            
            return result_text, image_data_list


async def run_bing_grounding(user_query: str) -> str:
    """Run agent with Bing grounding/web search capability."""
    async with AzureCliCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            bing_search_tool = HostedWebSearchTool(
                name="Bing Grounding Search",
                description="Search the web for current information using Bing",
            )
            
            agent = ChatAgent(
                chat_client=client,
                name="BingSearchAgent",
                instructions="You are a helpful assistant that can search the web for current information. Use the Bing search tool to find up-to-date information and provide accurate, well-sourced answers. Always cite your sources when possible.",
                tools=bing_search_tool,
            )
            
            result = await agent.run(user_query)
            return str(result.text)


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
            "Bing Grounding"
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
    
    else:  # Bing Grounding
        st.subheader("Bing Grounding Demo")
        st.markdown("""
        This demo uses Bing web search to find current, real-time information.
        The agent can search the web and provide up-to-date answers with sources.
        
        **Example:** 
        - "What are the latest developments in AI?"
        - "Who won the most recent Nobel Prize in Physics?"
        - "What's the current weather forecast for next week?"
        
        **Note:** Requires Bing Grounding connection configured in Azure AI Foundry.
        """)
        demo_key = "bing"
    
    # Initialize message history for this demo
    if demo_key not in st.session_state.messages:
        st.session_state.messages[demo_key] = []
    
    # Display chat history
    for message in st.session_state.messages[demo_key]:
        with st.chat_message(message["role"]):
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
                                    st.image(image, caption="Generated Plot", width="stretch")
                                except Exception as e:
                                    st.warning(f"Could not display image: {e}")
                        
                        st.session_state.messages[demo_key].append({"role": "assistant", "content": response})
                    elif demo_key == "bing":
                        response = asyncio.run(run_bing_grounding(prompt))
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
    - **Azure CLI Authentication**
    
    Make sure you're logged in with `az login` before running.
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

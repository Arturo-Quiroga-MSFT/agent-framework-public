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

import httpx
import streamlit as st
from dotenv import load_dotenv
from pydantic import Field
from typing import Annotated

# Add parent directories to path to import agent framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Load environment variables - use absolute path
env_path = Path(__file__).resolve().parent.parent / "python" / "samples" / "getting_started" / ".env"
print(f"[DEBUG] Loading .env from: {env_path}")
print(f"[DEBUG] .env exists: {env_path.exists()}")
load_dotenv(dotenv_path=env_path)
print(f"[DEBUG] OPENWEATHER_API_KEY loaded: {bool(os.getenv('OPENWEATHER_API_KEY'))}")
print(f"[DEBUG] AZURE_AI_PROJECT_ENDPOINT loaded: {bool(os.getenv('AZURE_AI_PROJECT_ENDPOINT'))}")


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
            "Threaded Conversation"
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
        
    else:  # Threaded Conversation
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
    - **Azure CLI Authentication**
    
    Make sure you're logged in with `az login` before running.
    """)
    
    # Display environment info
    with st.sidebar.expander("Environment Info"):
        st.text(f"Endpoint: {os.getenv('AZURE_AI_PROJECT_ENDPOINT', 'Not set')[:50]}...")
        st.text(f"Model: {os.getenv('AZURE_AI_MODEL_DEPLOYMENT_NAME', 'Not set')}")
        st.text(f"Weather API: {'✓ Configured' if os.getenv('OPENWEATHER_API_KEY') else '✗ Not set'}")


if __name__ == "__main__":
    main()

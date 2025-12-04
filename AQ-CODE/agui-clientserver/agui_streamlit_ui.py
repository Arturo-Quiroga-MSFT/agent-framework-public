#!/usr/bin/env python3
"""
AG-UI Streamlit Client - Web UI for interacting with AG-UI protocol servers.

This Streamlit application provides a modern chat interface for the AG-UI server
with real-time streaming responses, conversation history, and telemetry integration.
"""

import asyncio
import os
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

import streamlit as st
import httpx
from httpx_sse import aconnect_sse
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_SERVER_URL = "http://localhost:5100"
AGUI_SERVER_URL = os.getenv("AGUI_SERVER_URL", DEFAULT_SERVER_URL)


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="AG-UI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# Custom CSS
# ============================================================================

st.markdown("""
<style>
    /* Main chat container */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* User message */
    [data-testid="stChatMessageContent"] {
        padding: 0.5rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #28a745;
    }
    
    .status-offline {
        background-color: #dc3545;
    }
    
    /* Metrics cards */
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Session State Initialization
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"thread_{uuid.uuid4().hex[:8]}"

if "server_url" not in st.session_state:
    st.session_state.server_url = AGUI_SERVER_URL

if "server_status" not in st.session_state:
    st.session_state.server_status = "unknown"

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

if "total_requests" not in st.session_state:
    st.session_state.total_requests = 0


# ============================================================================
# Helper Functions
# ============================================================================

async def check_server_health(server_url: str) -> bool:
    """Check if the AG-UI server is healthy."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{server_url}/health")
            return response.status_code == 200
    except Exception:
        return False


async def send_message_to_agui(
    server_url: str,
    message: str,
    thread_id: str,
    placeholder
) -> tuple[str, int]:
    """
    Send a message to the AG-UI server and stream the response.
    
    Returns:
        Tuple of (full_response, token_count)
    """
    full_response = ""
    token_count = 0
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    
    payload = {
        "threadId": thread_id,
        "runId": run_id,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "context": {}
    }
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with aconnect_sse(
                client,
                "POST",
                server_url,
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as event_source:
                async for event in event_source.aiter_sse():
                    if event.event == "thread.message.delta":
                        data = json.loads(event.data)
                        if "delta" in data and "content" in data["delta"]:
                            content = data["delta"]["content"]
                            full_response += content
                            # Update the placeholder with streaming text
                            placeholder.markdown(full_response + "▌")
                    
                    elif event.event == "thread.run.completed":
                        # Final update without cursor
                        placeholder.markdown(full_response)
                        break
                    
                    elif event.event == "error":
                        data = json.loads(event.data)
                        error_msg = data.get("error", "Unknown error")
                        placeholder.error(f"Error: {error_msg}")
                        break
        
        # Estimate token count (rough approximation)
        token_count = len(message.split()) + len(full_response.split()) * 2
        
    except httpx.ConnectError:
        placeholder.error("❌ Failed to connect to server. Make sure it's running.")
    except httpx.ReadTimeout:
        placeholder.error("⏱️ Request timed out. The server might be overloaded.")
    except Exception as e:
        placeholder.error(f"❌ Error: {str(e)}")
    
    return full_response, token_count


def run_async(coro):
    """Run async coroutine in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.title("🤖 AG-UI Chat")
    st.markdown("---")
    
    # Server Configuration
    st.subheader("⚙️ Server Configuration")
    
    server_url = st.text_input(
        "Server URL",
        value=st.session_state.server_url,
        help="URL of the AG-UI server"
    )
    
    if server_url != st.session_state.server_url:
        st.session_state.server_url = server_url
        st.rerun()
    
    # Check server status
    if st.button("🔍 Check Server Status", use_container_width=True):
        with st.spinner("Checking server..."):
            is_healthy = run_async(check_server_health(st.session_state.server_url))
            st.session_state.server_status = "online" if is_healthy else "offline"
    
    # Display server status
    status_class = "status-online" if st.session_state.server_status == "online" else "status-offline"
    status_text = "🟢 Online" if st.session_state.server_status == "online" else "🔴 Offline"
    
    st.markdown(f"**Server Status:** {status_text}")
    
    st.markdown("---")
    
    # Session Information
    st.subheader("📊 Session Info")
    st.markdown(f"**Thread ID:** `{st.session_state.thread_id[:12]}...`")
    st.markdown(f"**Messages:** {len(st.session_state.messages)}")
    st.markdown(f"**Total Requests:** {st.session_state.total_requests}")
    st.markdown(f"**Total Tokens:** {st.session_state.total_tokens:,}")
    
    st.markdown("---")
    
    # Actions
    st.subheader("🔧 Actions")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.session_state.total_requests = 0
        st.rerun()
    
    if st.button("🔄 New Thread", use_container_width=True):
        st.session_state.thread_id = f"thread_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.session_state.total_requests = 0
        st.rerun()
    
    st.markdown("---")
    
    # Quick Tips
    with st.expander("💡 Quick Tips"):
        st.markdown("""
        - Type your message and press Enter or click Send
        - Use **New Thread** to start a fresh conversation
        - **Clear Chat History** removes messages from UI only
        - Check **Server Status** to verify connectivity
        - Monitor **Total Tokens** for usage tracking
        """)
    
    st.markdown("---")
    
    # About
    with st.expander("ℹ️ About"):
        st.markdown("""
        **AG-UI Streamlit Client**
        
        A modern web interface for the AG-UI protocol server.
        
        - Real-time streaming responses
        - Conversation history
        - Thread management
        - Server health monitoring
        
        Built with Streamlit and the AG-UI protocol.
        """)


# ============================================================================
# Main Chat Interface
# ============================================================================

st.title("🤖 AG-UI Chat Interface")
st.caption(f"Connected to: {st.session_state.server_url}")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Send message and get streaming response
        response, tokens = run_async(
            send_message_to_agui(
                st.session_state.server_url,
                prompt,
                st.session_state.thread_id,
                message_placeholder
            )
        )
        
        if response:
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.total_tokens += tokens
            st.session_state.total_requests += 1


# ============================================================================
# Footer
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💬 Messages",
        value=len(st.session_state.messages)
    )

with col2:
    st.metric(
        label="🎯 Requests",
        value=st.session_state.total_requests
    )

with col3:
    st.metric(
        label="🪙 Total Tokens",
        value=f"{st.session_state.total_tokens:,}"
    )

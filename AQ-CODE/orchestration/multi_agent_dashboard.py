#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Multi-Agent Dashboard - Streamlit Interface

A side-by-side dashboard for interacting with all 5 agents simultaneously.
Connects to the DevUI backend (port 8092) and provides a grid layout for
concurrent conversations with multiple agents.

PREREQUISITES:
- concurrent_agents_interactive_devui.py must be running on port 8092
- streamlit installed: pip install streamlit

USAGE:
    streamlit run AQ-CODE/orchestration/multi_agent_dashboard.py --server.port 8091

FEATURES:
- 5 side-by-side chat columns (one per agent)
- Independent conversation threads for each agent
- Real-time message streaming
- Conversation history per agent
- Auto-scroll to latest messages
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
import httpx
import streamlit as st
from datetime import datetime

# DevUI Backend Configuration
DEVUI_BASE_URL = "http://localhost:8092"
DEVUI_API_BASE = f"{DEVUI_BASE_URL}/v1"

# Agent Configuration - Will be populated from backend
AGENT_NAMES = [
    {
        "name": "Market_Researcher",
        "display_name": "🔬 Market Researcher",
        "description": "Market analysis & insights",
        "color": "#1E90FF"  # Dodger Blue
    },
    {
        "name": "Marketing_Strategist", 
        "display_name": "📢 Marketing Strategist",
        "description": "Strategy & positioning",
        "color": "#FF6347"  # Tomato
    },
    {
        "name": "Legal_Compliance_Advisor",
        "display_name": "⚖️ Legal Advisor",
        "description": "Compliance & risk",
        "color": "#32CD32"  # Lime Green
    },
    {
        "name": "Financial_Analyst",
        "display_name": "💰 Financial Analyst",
        "description": "Revenue & ROI analysis",
        "color": "#FFD700"  # Gold
    },
    {
        "name": "Technical_Architect",
        "display_name": "🏗️ Technical Architect",
        "description": "Architecture & tech stack",
        "color": "#9370DB"  # Medium Purple
    }
]


class DevUIClient:
    """Client for interacting with DevUI backend API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=120.0)  # 2 minutes for LLM responses
        
    def get_entities(self) -> List[Dict]:
        """Fetch available entities from DevUI."""
        try:
            response = self.client.get(f"{self.base_url}/entities")
            response.raise_for_status()
            data = response.json()
            return data.get("entities", [])
        except Exception as e:
            st.error(f"Failed to fetch entities: {e}")
            return []
    
    def create_conversation(self, agent_id: str) -> Optional[str]:
        """Create a new conversation for an agent."""
        try:
            response = self.client.post(
                f"{self.base_url}/conversations",
                json={"metadata": {"agent_id": agent_id}}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("id")
        except Exception as e:
            st.error(f"Failed to create conversation for {agent_id}: {e}")
            return None
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Get messages from a conversation."""
        try:
            response = self.client.get(
                f"{self.base_url}/conversations/{conversation_id}/items"
            )
            response.raise_for_status()
            items = response.json()
            return items if isinstance(items, list) else []
        except Exception as e:
            # 404 is expected for new conversations
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 404:
                return []
            return []
    
    def send_message(self, agent_id: str, conversation_id: str, message: str) -> Optional[str]:
        """Send a message and return the assistant's response."""
        try:
            # Send message via DevUI responses endpoint
            response = self.client.post(
                f"{self.base_url}/responses",
                json={
                    "input": message,
                    "stream": False,
                    "metadata": {
                        "entity_id": agent_id,
                        "conversation_id": conversation_id
                    }
                },
                timeout=120.0  # 2 minutes for LLM responses
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract assistant message from response
            # DevUI returns: {"output": [{"content": [{"text": "...", "type": "output_text"}], "role": "assistant"}]}
            if "output" in data and isinstance(data["output"], list) and len(data["output"]) > 0:
                first_output = data["output"][0]
                if "content" in first_output and isinstance(first_output["content"], list):
                    for content_item in first_output["content"]:
                        if content_item.get("type") == "output_text" and "text" in content_item:
                            return content_item["text"]
            
            # Fallback for other formats
            if "message" in data:
                return data["message"]
            elif "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0].get("message", {}).get("content")
            
            # Log the response structure for debugging
            st.warning(f"Unexpected response format: {list(data.keys())}")
            return str(data)
            
        except httpx.TimeoutException as e:
            st.error(f"⏱️ Request timed out. The agent may be processing a complex request.")
            return None
        except httpx.HTTPStatusError as e:
            st.error(f"❌ HTTP error {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            st.error(f"❌ Failed to send message: {type(e).__name__}: {e}")
            return None


def init_session_state():
    """Initialize Streamlit session state."""
    if "client" not in st.session_state:
        st.session_state.client = DevUIClient(DEVUI_API_BASE)
    
    if "agents" not in st.session_state:
        st.session_state.agents = []
    
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    
    if "backend_connected" not in st.session_state:
        st.session_state.backend_connected = False


def load_agents():
    """Load agents from DevUI backend and match with display config."""
    entities = st.session_state.client.get_entities()
    agents = []
    
    # Filter to only agents (not workflows) and match with our config
    for entity in entities:
        if entity.get("type") == "agent":
            entity_name = entity.get("name")
            entity_id = entity.get("id")
            
            # Find matching config
            config = next((a for a in AGENT_NAMES if a["name"] == entity_name), None)
            if config:
                agents.append({
                    "id": entity_id,  # Use the full UUID from backend
                    "name": config["display_name"],
                    "description": config["description"],
                    "color": config["color"]
                })
    
    st.session_state.agents = agents
    
    # Initialize conversations for all agents
    if not st.session_state.conversations:
        st.session_state.conversations = {
            agent["id"]: {
                "conversation_id": None,
                "messages": []
            }
            for agent in agents
        }


def check_backend_connection() -> bool:
    """Check if DevUI backend is running."""
    try:
        response = httpx.get(f"{DEVUI_BASE_URL}/health", timeout=5.0)
        return response.status_code == 200
    except:
        return False


def ensure_conversation(agent_id: str):
    """Ensure a conversation exists for the agent."""
    conv_data = st.session_state.conversations[agent_id]
    if conv_data["conversation_id"] is None:
        conv_id = st.session_state.client.create_conversation(agent_id)
        if conv_id:
            conv_data["conversation_id"] = conv_id
            st.session_state.conversations[agent_id] = conv_data


def render_agent_column(agent: Dict, col):
    """Render a single agent's chat column."""
    with col:
        # Agent header
        st.markdown(f"""
        <div style="background-color: {agent['color']}22; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="margin: 0; color: {agent['color']};">{agent['name']}</h4>
            <p style="margin: 0; font-size: 0.8em; color: #666;">{agent['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        agent_id = agent["id"]
        conv_data = st.session_state.conversations[agent_id]
        
        # Chat history container (fixed height with scroll)
        chat_container = st.container()
        with chat_container:
            st.markdown(f'<div style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px;" id="chat_{agent_id}">', unsafe_allow_html=True)
            
            if len(conv_data["messages"]) == 0:
                st.markdown(f'<p style="color: #999; text-align: center; margin-top: 100px;">Start a conversation with {agent["name"].split(" ", 1)[1]}</p>', unsafe_allow_html=True)
            else:
                for msg in conv_data["messages"]:
                    role = msg["role"]
                    content = msg["content"]
                    timestamp = msg.get("timestamp", "")
                    
                    if role == "user":
                        st.markdown(f"""
                        <div style="background-color: #E3F2FD; padding: 8px; border-radius: 8px; margin-bottom: 8px; text-align: right;">
                            <div style="font-size: 0.7em; color: #666; margin-bottom: 4px;">{timestamp}</div>
                            <div style="color: #1976D2; font-weight: 500;">You</div>
                            <div>{content}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:  # assistant
                        st.markdown(f"""
                        <div style="background-color: #F5F5F5; padding: 8px; border-radius: 8px; margin-bottom: 8px;">
                            <div style="font-size: 0.7em; color: #666; margin-bottom: 4px;">{timestamp}</div>
                            <div style="color: {agent['color']}; font-weight: 500;">{agent['name'].split(' ', 1)[1]}</div>
                            <div>{content}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Input area
        with st.form(key=f"form_{agent_id}", clear_on_submit=True):
            user_input = st.text_area(
                "Message",
                key=f"input_{agent_id}",
                height=80,
                placeholder=f"Ask {agent['name'].split(' ', 1)[1]}...",
                label_visibility="collapsed"
            )
            submit = st.form_submit_button("Send", use_container_width=True)
            
            if submit and user_input.strip():
                # Ensure conversation exists
                ensure_conversation(agent_id)
                conv_id = conv_data["conversation_id"]
                
                if conv_id:
                    # Add user message to history
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    conv_data["messages"].append({
                        "role": "user",
                        "content": user_input.strip(),
                        "timestamp": timestamp
                    })
                    
                    # Send message and get response
                    with st.spinner(f"💭 {agent['name'].split(' ', 1)[1]} is thinking..."):
                        response = st.session_state.client.send_message(
                            agent_id, 
                            conv_id, 
                            user_input.strip()
                        )
                    
                    if response:
                        # Add assistant response to history
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        conv_data["messages"].append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": timestamp
                        })
                        st.session_state.conversations[agent_id] = conv_data
                        st.rerun()
                    else:
                        st.error("Failed to get response")


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Multi-Agent Dashboard",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stTextArea textarea {
        font-size: 0.9em;
    }
    h4 {
        margin-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize
    init_session_state()
    
    # Header
    st.title("🤖 Multi-Agent Dashboard")
    st.markdown("Interact with all 5 expert agents side-by-side")
    
    # Check backend connection
    if not st.session_state.backend_connected:
        st.session_state.backend_connected = check_backend_connection()
        
        if not st.session_state.backend_connected:
            st.error("⚠️ Cannot connect to DevUI backend at http://localhost:8092")
            st.info("Make sure concurrent_agents_interactive_devui.py is running:\n\n```bash\npython AQ-CODE/orchestration/concurrent_agents_interactive_devui.py\n```")
            
            if st.button("Retry Connection"):
                st.rerun()
            return
    
    # Load agents from backend
    if not st.session_state.agents:
        load_agents()
        
        if not st.session_state.agents:
            st.error("⚠️ No agents found in DevUI backend")
            return
    
    st.success(f"✅ Connected to DevUI backend - {len(st.session_state.agents)} agents available")
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🗑️ Clear All", use_container_width=True):
            # Clear all conversations
            st.session_state.conversations = {
                agent["id"]: {
                    "conversation_id": None,
                    "messages": []
                }
                for agent in st.session_state.agents
            }
            st.rerun()
    
    st.divider()
    
    # Create 5 columns for agents
    cols = st.columns(5)
    
    # Render each agent in its column
    for i, agent in enumerate(st.session_state.agents):
        render_agent_column(agent, cols[i])


if __name__ == "__main__":
    main()

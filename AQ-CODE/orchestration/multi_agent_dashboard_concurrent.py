#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Multi-Agent Dashboard - Concurrent Version with Threading

A side-by-side dashboard for interacting with all 5 agents simultaneously.
This version uses threading to allow concurrent message sending without blocking the UI.

PREREQUISITES:
- concurrent_agents_interactive_devui.py must be running on port 8092
- streamlit installed: pip install streamlit

USAGE:
    streamlit run AQ-CODE/orchestration/multi_agent_dashboard_concurrent.py --server.port 8095

FEATURES:
- 5 side-by-side chat columns (one per agent)
- TRUE CONCURRENT interactions - send to all agents at once!
- Independent conversation threads for each agent
- Real-time message streaming
- Non-blocking UI during agent processing
"""

import asyncio
import json
import os
import threading
import queue
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
            return []
    
    def send_message(self, agent_id: str, conversation_id: str, message: str) -> Optional[str]:
        """Send a message and return the assistant's response."""
        try:
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
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract assistant message from response
            if "output" in data and isinstance(data["output"], list) and len(data["output"]) > 0:
                first_output = data["output"][0]
                if "content" in first_output and isinstance(first_output["content"], list):
                    for content_item in first_output["content"]:
                        if content_item.get("type") == "output_text" and "text" in content_item:
                            return content_item["text"]
            
            return None
            
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"


def send_message_threaded(client: DevUIClient, agent_id: str, agent_name: str, 
                          conversation_id: str, message: str, result_queue: queue.Queue):
    """Send message in a background thread."""
    try:
        response = client.send_message(agent_id, conversation_id, message)
        result_queue.put({
            "agent_id": agent_id,
            "agent_name": agent_name,
            "success": True,
            "response": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    except Exception as e:
        result_queue.put({
            "agent_id": agent_id,
            "agent_name": agent_name,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })


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
    
    if "pending_requests" not in st.session_state:
        st.session_state.pending_requests = {}  # agent_id -> {thread, queue, message}


def check_backend_connection() -> bool:
    """Check if DevUI backend is running."""
    try:
        response = httpx.get(f"{DEVUI_BASE_URL}/health", timeout=5.0)
        return response.status_code == 200
    except:
        return False


def load_agents():
    """Load agents from DevUI backend and match with display config."""
    entities = st.session_state.client.get_entities()
    agents = []
    
    for entity in entities:
        if entity.get("type") == "agent":
            entity_name = entity.get("name")
            entity_id = entity.get("id")
            
            config = next((a for a in AGENT_NAMES if a["name"] == entity_name), None)
            if config:
                agents.append({
                    "id": entity_id,
                    "name": config["display_name"],
                    "description": config["description"],
                    "color": config["color"]
                })
    
    st.session_state.agents = agents
    
    if not st.session_state.conversations:
        st.session_state.conversations = {
            agent["id"]: {
                "conversation_id": None,
                "messages": []
            }
            for agent in agents
        }


def ensure_conversation(agent_id: str):
    """Ensure a conversation exists for the agent."""
    conv_data = st.session_state.conversations[agent_id]
    if conv_data["conversation_id"] is None:
        conv_id = st.session_state.client.create_conversation(agent_id)
        if conv_id:
            conv_data["conversation_id"] = conv_id
            st.session_state.conversations[agent_id] = conv_data


def check_pending_requests():
    """Check for completed threaded requests and update UI."""
    completed = []
    
    for agent_id, pending in st.session_state.pending_requests.items():
        result_queue = pending["queue"]
        
        try:
            # Non-blocking check if result is ready
            result = result_queue.get_nowait()
            
            # Add user message if not already added
            conv_data = st.session_state.conversations[agent_id]
            user_msg_text = pending["message"]
            
            # Check if user message already exists
            if not any(m["content"] == user_msg_text and m["role"] == "user" 
                      for m in conv_data["messages"][-1:]):
                conv_data["messages"].append({
                    "role": "user",
                    "content": user_msg_text,
                    "timestamp": pending["timestamp"]
                })
            
            # Add assistant response
            if result["success"] and result["response"]:
                conv_data["messages"].append({
                    "role": "assistant",
                    "content": result["response"],
                    "timestamp": result["timestamp"]
                })
            else:
                conv_data["messages"].append({
                    "role": "assistant",
                    "content": f"Error: {result.get('error', 'Unknown error')}",
                    "timestamp": result["timestamp"]
                })
            
            st.session_state.conversations[agent_id] = conv_data
            completed.append(agent_id)
            
        except queue.Empty:
            # Still processing, check if thread is alive
            if not pending["thread"].is_alive():
                # Thread died without result
                completed.append(agent_id)
    
    # Remove completed requests
    for agent_id in completed:
        del st.session_state.pending_requests[agent_id]
    
    return len(completed) > 0


def render_agent_column(agent: Dict, col):
    """Render a single agent's chat column."""
    with col:
        agent_id = agent["id"]
        
        # Agent header
        st.markdown(f"""
        <div style="background-color: {agent['color']}22; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="margin: 0; color: {agent['color']};">{agent['name']}</h4>
            <p style="margin: 0; font-size: 0.8em; color: #666;">{agent['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        conv_data = st.session_state.conversations[agent_id]
        is_pending = agent_id in st.session_state.pending_requests
        
        # Chat history container - scrollable
        chat_height = "450px" if not is_pending else "430px"
        
        if len(conv_data["messages"]) == 0 and not is_pending:
            st.markdown(f'<div style="height: {chat_height}; display: flex; align-items: center; justify-content: center; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;"><p style="color: #999; text-align: center;">Start a conversation with {agent["name"].split(" ", 1)[1]}</p></div>', unsafe_allow_html=True)
        else:
            # Scrollable container with full messages
            for msg in conv_data["messages"]:
                role = msg["role"]
                content = str(msg["content"])
                timestamp = msg.get("timestamp", "")
                
                if role == "user":
                    # Show first 200 chars of user message
                    display_content = content[:200] + '...' if len(content) > 200 else content
                    st.markdown(f"""
                    <div style="background-color: #E3F2FD; padding: 8px; border-radius: 8px; margin-bottom: 8px;">
                        <div style="font-size: 0.7em; color: #666; margin-bottom: 4px;">{timestamp} - You</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.text(display_content)
                else:
                    # Show FULL agent response using st.text_area for proper scrolling
                    st.markdown(f"""
                    <div style="background-color: #F5F5F5; padding: 4px 8px; border-radius: 8px; margin-bottom: 4px;">
                        <div style="font-size: 0.7em; color: {agent['color']}; font-weight: 500;">{timestamp} - {agent['name'].split(' ', 1)[1]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.text_area(
                        label="response",
                        value=content,
                        height=300,
                        key=f"msg_{agent_id}_{timestamp}",
                        label_visibility="collapsed",
                        disabled=True
                    )
        
        # Show thinking indicator
        if is_pending:
            st.info(f"💭 {agent['name'].split(' ', 1)[1]} is thinking...")
        
        # Input area
        input_disabled = is_pending
        
        with st.form(key=f"form_{agent_id}", clear_on_submit=True):
            user_input = st.text_area(
                "Message",
                key=f"input_{agent_id}",
                height=80,
                placeholder=f"Ask {agent['name'].split(' ', 1)[1]}..." if not input_disabled else "Waiting for response...",
                label_visibility="collapsed",
                disabled=input_disabled
            )
            submit = st.form_submit_button("Send", use_container_width=True, disabled=input_disabled)
            
            if submit and user_input.strip() and not input_disabled:
                ensure_conversation(agent_id)
                conv_id = conv_data["conversation_id"]
                
                if conv_id:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Create result queue and start thread
                    result_queue = queue.Queue()
                    thread = threading.Thread(
                        target=send_message_threaded,
                        args=(st.session_state.client, agent_id, agent["name"], 
                              conv_id, user_input.strip(), result_queue)
                    )
                    thread.daemon = True
                    thread.start()
                    
                    # Store pending request
                    st.session_state.pending_requests[agent_id] = {
                        "thread": thread,
                        "queue": result_queue,
                        "message": user_input.strip(),
                        "timestamp": timestamp
                    }
                    
                    st.rerun()


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Multi-Agent Dashboard (Concurrent)",
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
    st.title("🤖 Multi-Agent Dashboard (Concurrent)")
    st.markdown("**Interact with all 5 agents simultaneously!** Send messages to multiple agents at once.")
    
    # Check backend
    if not st.session_state.backend_connected:
        st.session_state.backend_connected = check_backend_connection()
        
        if not st.session_state.backend_connected:
            st.error("⚠️ Cannot connect to DevUI backend at http://localhost:8092")
            st.info("Make sure concurrent_agents_interactive_devui.py is running:\n\n```bash\npython AQ-CODE/orchestration/concurrent_agents_interactive_devui.py\n```")
            
            if st.button("Retry Connection"):
                st.rerun()
            return
    
    # Load agents
    if not st.session_state.agents:
        load_agents()
        
        if not st.session_state.agents:
            st.error("⚠️ No agents found in DevUI backend")
            return
    
    # Check for completed requests
    if check_pending_requests():
        st.rerun()
    
    pending_count = len(st.session_state.pending_requests)
    status_msg = f"✅ Connected - {len(st.session_state.agents)} agents"
    if pending_count > 0:
        status_msg += f" | 💭 {pending_count} agent(s) thinking..."
    st.success(status_msg)
    
    # Control buttons
    col1, col2, col3, col4 = st.columns([1, 1, 2, 6])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.conversations = {
                agent["id"]: {
                    "conversation_id": None,
                    "messages": []
                }
                for agent in st.session_state.agents
            }
            st.session_state.pending_requests = {}
            st.rerun()
    with col3:
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔁 Auto-refresh", value=True, 
                                   help="Automatically check for completed responses every 2 seconds")
    
    st.divider()
    
    # Example questions section
    st.markdown("**💡 Quick Start - Ask all agents simultaneously:**")
    
    example_questions = [
        "🚲 Launching a budget-friendly electric bike for urban commuters with a range of 50 miles, priced at $1,200, targeting millennials in major cities.",
        "🏥 Telemedicine platform for rural healthcare connecting patients with doctors via video, mobile app, targeting underserved communities.",
        "🌾 Smart irrigation system using AI and IoT sensors to optimize water usage for small to medium farms, reducing water consumption by 40%.",
        "🏠 Smart home security system with AI detection, 24/7 monitoring, and integration with existing smart home devices, priced at $299 + $15/month.",
        "📚 AI-powered personalized learning platform for K-12 students with adaptive curriculum and real-time progress tracking for parents and teachers."
    ]
    
    cols_examples = st.columns(len(example_questions))
    for idx, (col, question) in enumerate(zip(cols_examples, example_questions)):
        with col:
            # Extract emoji and first few words for button label
            parts = question.split(" ", 2)
            emoji = parts[0]
            short_label = " ".join(parts[1:3]) if len(parts) > 2 else parts[1]
            
            if st.button(f"{emoji} {short_label}...", key=f"ex_{idx}", use_container_width=True, 
                        help=question):
                # Send to all agents simultaneously
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                for agent in st.session_state.agents:
                    agent_id = agent["id"]
                    
                    # Skip if already processing
                    if agent_id in st.session_state.pending_requests:
                        continue
                    
                    # Ensure conversation exists
                    ensure_conversation(agent_id)
                    conv_data = st.session_state.conversations[agent_id]
                    conv_id = conv_data["conversation_id"]
                    
                    if conv_id:
                        # Create result queue and start thread
                        result_queue = queue.Queue()
                        thread = threading.Thread(
                            target=send_message_threaded,
                            args=(st.session_state.client, agent_id, agent["name"], 
                                  conv_id, question, result_queue)
                        )
                        thread.daemon = True
                        thread.start()
                        
                        # Store pending request
                        st.session_state.pending_requests[agent_id] = {
                            "thread": thread,
                            "queue": result_queue,
                            "message": question,
                            "timestamp": timestamp
                        }
                
                st.rerun()
    
    st.divider()
    
    # Auto-refresh logic
    if auto_refresh and pending_count > 0:
        import time
        time.sleep(2)
        st.rerun()
    
    # Create 5 columns for agents
    cols = st.columns(5)
    
    # Render each agent in its column
    for i, agent in enumerate(st.session_state.agents):
        render_agent_column(agent, cols[i])


if __name__ == "__main__":
    main()

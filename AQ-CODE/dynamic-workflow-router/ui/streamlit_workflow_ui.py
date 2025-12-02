#!/usr/bin/env python3
"""
Streamlit UI for Dynamic Workflow Router

Interactive web interface for testing and managing dynamic workflows.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

import streamlit as st
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflow_router import DynamicWorkflowRouter
from dotenv import load_dotenv

# Load environment
load_dotenv()


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Dynamic Workflow Router",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# Session State Initialization
# ============================================================================

if "router" not in st.session_state:
    st.session_state.router = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "workflows" not in st.session_state:
    st.session_state.workflows = []

if "routing_stats" not in st.session_state:
    st.session_state.routing_stats = []


# ============================================================================
# Helper Functions
# ============================================================================

async def initialize_router():
    """Initialize the workflow router."""
    if st.session_state.router is None:
        with st.spinner("🔄 Initializing router..."):
            try:
                router = DynamicWorkflowRouter(
                    enable_cache=True,
                    cache_ttl_seconds=300
                )
                st.session_state.router = router
                st.success("✅ Router initialized!")
                return True
            except Exception as e:
                st.error(f"❌ Failed to initialize router: {e}")
                return False
    return True


async def load_workflows():
    """Load workflows from Cosmos DB."""
    if st.session_state.router:
        try:
            workflows = await st.session_state.router.list_workflows()
            st.session_state.workflows = workflows
            return workflows
        except Exception as e:
            st.error(f"❌ Error loading workflows: {e}")
            return []
    return []


async def send_message(user_input: str, context: Optional[Dict[str, Any]] = None):
    """Send message and get response."""
    if not st.session_state.router:
        st.error("Router not initialized")
        return
    
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Create placeholder for streaming response
    response_placeholder = st.empty()
    full_response = ""
    
    try:
        # Get routing decision first
        with st.spinner("🔍 Routing..."):
            workflow_id = await st.session_state.router.classify_intent(user_input, context)
        
        # Track routing decision
        st.session_state.routing_stats.append({
            "query": user_input,
            "workflow_id": workflow_id,
            "timestamp": datetime.now()
        })
        
        # Show routing decision
        st.info(f"📍 Routed to: **{workflow_id}**")
        
        # Stream response
        async for chunk in st.session_state.router.execute_workflow(
            workflow_id=workflow_id,
            user_input=user_input,
            context=context,
            stream=True
        ):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
        
        # Final response
        response_placeholder.markdown(full_response)
        
        # Add assistant message to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_response,
            "workflow_id": workflow_id,
            "timestamp": datetime.now()
        })
        
    except Exception as e:
        st.error(f"❌ Error: {e}")


# ============================================================================
# Main UI
# ============================================================================

def main():
    """Main application."""
    
    # Header
    st.title("🔀 Dynamic Workflow Router")
    st.markdown("**Multi-workflow orchestration with Azure Cosmos DB**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Environment status
        st.subheader("Environment")
        project_conn = os.getenv("PROJECT_CONNECTION_STRING")
        cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
        
        if project_conn:
            st.success("✅ Azure AI Foundry configured")
        else:
            st.error("❌ PROJECT_CONNECTION_STRING not set")
        
        if cosmos_endpoint:
            st.success("✅ Cosmos DB configured")
        else:
            st.error("❌ COSMOS_DB_ENDPOINT not set")
        
        st.divider()
        
        # Initialize router button
        if st.button("🚀 Initialize Router", use_container_width=True):
            asyncio.run(initialize_router())
        
        # Load workflows button
        if st.button("📥 Load Workflows", use_container_width=True):
            workflows = asyncio.run(load_workflows())
            if workflows:
                st.success(f"✅ Loaded {len(workflows)} workflows")
        
        # Clear history button
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.routing_stats = []
            st.rerun()
        
        st.divider()
        
        # Workflow count
        if st.session_state.workflows:
            st.metric("Total Workflows", len(st.session_state.workflows))
            enabled = sum(1 for w in st.session_state.workflows if w.get("metadata", {}).get("enabled", True))
            st.metric("Enabled Workflows", enabled)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📋 Workflows", "📊 Analytics", "🛠️ Workflow Editor"])
    
    # ========================================================================
    # Tab 1: Chat Interface
    # ========================================================================
    
    with tab1:
        st.header("Interactive Chat")
        
        # Check if router is initialized
        if not st.session_state.router:
            st.warning("⚠️ Router not initialized. Click 'Initialize Router' in the sidebar.")
            if st.button("🚀 Initialize Now"):
                if asyncio.run(initialize_router()):
                    st.rerun()
        else:
            # Chat history
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and "workflow_id" in msg:
                        st.caption(f"🔀 Workflow: {msg['workflow_id']}")
            
            # Chat input
            if prompt := st.chat_input("Enter your message..."):
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    asyncio.run(send_message(prompt))
            
            # Example queries
            st.divider()
            st.subheader("💡 Example Queries")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🛒 Order Status", use_container_width=True):
                    st.session_state.example_query = "Where is my order #12345?"
                    st.rerun()
                
                if st.button("🔧 Technical Support", use_container_width=True):
                    st.session_state.example_query = "My API integration is returning 401 errors"
                    st.rerun()
            
            with col2:
                if st.button("💰 Sales Inquiry", use_container_width=True):
                    st.session_state.example_query = "I want to buy the enterprise plan"
                    st.rerun()
                
                if st.button("🆘 Customer Support", use_container_width=True):
                    st.session_state.example_query = "My product stopped working and I need help"
                    st.rerun()
            
            # Handle example query
            if "example_query" in st.session_state:
                query = st.session_state.example_query
                del st.session_state.example_query
                
                with st.chat_message("user"):
                    st.markdown(query)
                
                with st.chat_message("assistant"):
                    asyncio.run(send_message(query))
    
    # ========================================================================
    # Tab 2: Workflow Browser
    # ========================================================================
    
    with tab2:
        st.header("Workflow Browser")
        
        if not st.session_state.workflows:
            st.info("No workflows loaded. Click 'Load Workflows' in the sidebar.")
        else:
            # Filter controls
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                search_term = st.text_input("🔍 Search workflows", placeholder="Enter keyword...")
            
            with col2:
                categories = list(set(w.get("category", "uncategorized") for w in st.session_state.workflows))
                selected_category = st.selectbox("📁 Category", ["All"] + sorted(categories))
            
            with col3:
                show_disabled = st.checkbox("Show disabled", value=False)
            
            # Filter workflows
            filtered_workflows = st.session_state.workflows
            
            if search_term:
                filtered_workflows = [
                    w for w in filtered_workflows
                    if search_term.lower() in w.get("name", "").lower()
                    or search_term.lower() in w.get("description", "").lower()
                    or search_term.lower() in w.get("id", "").lower()
                ]
            
            if selected_category != "All":
                filtered_workflows = [
                    w for w in filtered_workflows
                    if w.get("category") == selected_category
                ]
            
            if not show_disabled:
                filtered_workflows = [
                    w for w in filtered_workflows
                    if w.get("metadata", {}).get("enabled", True)
                ]
            
            st.markdown(f"**Found {len(filtered_workflows)} workflows**")
            st.divider()
            
            # Display workflows
            for workflow in filtered_workflows:
                enabled = workflow.get("metadata", {}).get("enabled", True)
                status_icon = "✅" if enabled else "❌"
                
                with st.expander(f"{status_icon} **{workflow.get('name', workflow['id'])}**"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**ID:** `{workflow['id']}`")
                        st.markdown(f"**Category:** {workflow.get('category', 'N/A')}")
                        st.markdown(f"**Description:** {workflow.get('description', 'N/A')}")
                        
                        # Tags
                        tags = workflow.get("metadata", {}).get("tags", [])
                        if tags:
                            st.markdown(f"**Tags:** {', '.join(tags)}")
                    
                    with col2:
                        st.markdown(f"**Model:** {workflow.get('agent_config', {}).get('model', 'N/A')}")
                        st.markdown(f"**Version:** {workflow.get('version', 'N/A')}")
                        
                        # Temperature
                        temp = workflow.get('agent_config', {}).get('temperature', 'N/A')
                        st.markdown(f"**Temperature:** {temp}")
                    
                    # Tools
                    tools = workflow.get('agent_config', {}).get('tools', [])
                    if tools:
                        st.markdown("**Tools:**")
                        for tool in tools:
                            st.markdown(f"- `{tool.get('type', 'unknown')}`")
                    
                    # Routing info
                    if "routing" in workflow:
                        st.markdown("**Routing Keywords:**")
                        keywords = workflow['routing'].get('keywords', [])
                        st.markdown(f"{', '.join(keywords[:10])}")
                    
                    # Test button
                    if st.button(f"🧪 Test Workflow", key=f"test_{workflow['id']}"):
                        st.info(f"Switch to Chat tab to test {workflow['id']}")
    
    # ========================================================================
    # Tab 3: Analytics
    # ========================================================================
    
    with tab3:
        st.header("Routing Analytics")
        
        if not st.session_state.routing_stats:
            st.info("No routing data yet. Send some messages in the Chat tab.")
        else:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Queries", len(st.session_state.routing_stats))
            
            with col2:
                unique_workflows = len(set(s['workflow_id'] for s in st.session_state.routing_stats))
                st.metric("Workflows Used", unique_workflows)
            
            with col3:
                avg_length = sum(len(s['query']) for s in st.session_state.routing_stats) / len(st.session_state.routing_stats)
                st.metric("Avg Query Length", f"{avg_length:.0f} chars")
            
            st.divider()
            
            # Workflow distribution
            st.subheader("📊 Workflow Distribution")
            
            workflow_counts = {}
            for stat in st.session_state.routing_stats:
                wf_id = stat['workflow_id']
                workflow_counts[wf_id] = workflow_counts.get(wf_id, 0) + 1
            
            df = pd.DataFrame([
                {"Workflow": k, "Count": v}
                for k, v in workflow_counts.items()
            ])
            
            st.bar_chart(df.set_index("Workflow"))
            
            st.divider()
            
            # Recent routing decisions
            st.subheader("🕐 Recent Routing Decisions")
            
            recent_stats = st.session_state.routing_stats[-10:]
            for stat in reversed(recent_stats):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Query:** {stat['query']}")
                    with col2:
                        st.markdown(f"**→** `{stat['workflow_id']}`")
                    st.caption(stat['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
                    st.divider()
    
    # ========================================================================
    # Tab 4: Workflow Editor (Simple)
    # ========================================================================
    
    with tab4:
        st.header("Workflow Editor")
        st.info("💡 For advanced editing, modify workflows directly in Cosmos DB or use the JSON files in `schemas/examples/`")
        
        st.subheader("Create New Workflow")
        
        with st.form("new_workflow_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                workflow_id = st.text_input("Workflow ID*", placeholder="my_custom_workflow")
                workflow_name = st.text_input("Name*", placeholder="My Custom Workflow")
                category = st.selectbox("Category*", ["support", "sales", "technical", "operations", "other"])
            
            with col2:
                model = st.selectbox("Model*", ["gpt-4o", "gpt-4", "gpt-4o-mini", "gpt-35-turbo"])
                temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
                version = st.text_input("Version", value="1.0")
            
            description = st.text_area("Description*", placeholder="What does this workflow do?")
            instructions = st.text_area("Agent Instructions*", placeholder="You are a helpful assistant that...")
            
            keywords = st.text_input("Keywords (comma-separated)", placeholder="help, support, issue")
            
            enable_web_search = st.checkbox("Enable Web Search (Bing Grounding)")
            enable_code_interpreter = st.checkbox("Enable Code Interpreter")
            
            submit = st.form_submit_button("Create Workflow", use_container_width=True)
            
            if submit:
                if not all([workflow_id, workflow_name, category, description, instructions]):
                    st.error("Please fill in all required fields (*)")
                else:
                    # Build workflow config
                    tools = []
                    if enable_web_search:
                        tools.append({"type": "bing_grounding"})
                    if enable_code_interpreter:
                        tools.append({"type": "code_interpreter"})
                    
                    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
                    
                    workflow_config = {
                        "id": workflow_id,
                        "partitionKey": [category, workflow_id],
                        "type": "workflow",
                        "category": category,
                        "name": workflow_name,
                        "description": description,
                        "version": version,
                        "agent_config": {
                            "model": model,
                            "instructions": instructions,
                            "tools": tools,
                            "temperature": temperature
                        },
                        "routing": {
                            "keywords": keyword_list
                        },
                        "metadata": {
                            "created_at": datetime.utcnow().isoformat(),
                            "updated_at": datetime.utcnow().isoformat(),
                            "author": "Streamlit UI",
                            "tags": keyword_list,
                            "enabled": True
                        }
                    }
                    
                    st.success("✅ Workflow configuration generated!")
                    st.json(workflow_config)
                    st.info("💡 To add this workflow, save the JSON above to a file and load it into Cosmos DB using `scripts/load_workflows.py`")


# ============================================================================
# Footer
# ============================================================================

def show_footer():
    """Show footer."""
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>Dynamic Workflow Router v1.0 | Built with Microsoft Agent Framework</p>
        <p>For questions or issues, see <a href='../README.md'>README.md</a></p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    main()
    show_footer()

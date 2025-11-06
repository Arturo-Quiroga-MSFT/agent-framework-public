"""
Streamlit UI for Production-Ready MAF Agent with LLMOps

Features:
- Multi-agent preset selection
- Real-time progress updates
- Cost and token tracking dashboard
- Quality evaluation display
- Chat history management
- Session export
- Budget monitoring

Run: streamlit run AQ-CODE/llmops/streamlit_production_ui.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.production_agent_enhanced import (
    ProductionAgent,
    AgentPreset,
    AgentStatus,
    ProgressUpdate,
    AgentResponse
)

# Page configuration
st.set_page_config(
    page_title="LLMOps Production Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin: 5px 0;
    }
    .status-initializing { background-color: #ffd700; color: black; }
    .status-running { background-color: #1e90ff; color: white; }
    .status-completed { background-color: #32cd32; color: white; }
    .status-error { background-color: #ff4500; color: white; }
    .quality-excellent { color: #32cd32; font-weight: bold; }
    .quality-good { color: #1e90ff; font-weight: bold; }
    .quality-needs-improvement { color: #ffa500; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "progress_updates" not in st.session_state:
    st.session_state.progress_updates = []
if "responses" not in st.session_state:
    st.session_state.responses = []
if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = "market_analyst"
if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False
if "next_prompt" not in st.session_state:
    st.session_state.next_prompt = None


def progress_callback(update: ProgressUpdate):
    """Callback to capture progress updates."""
    st.session_state.progress_updates.append(update)


def create_agent(preset_name: str):
    """Create or recreate agent with selected preset."""
    # Release old agent reference - cleanup happens in ProductionAgent.__del__
    st.session_state.agent = None
    
    # Create new agent
    st.session_state.agent = ProductionAgent.from_preset(
        preset_name,
        progress_callback=progress_callback
    )
    st.session_state.selected_preset = preset_name
    st.session_state.agent_initialized = True
    st.session_state.chat_history = []
    st.session_state.responses = []
    st.session_state.progress_updates = []


def display_metrics_dashboard(stats: Dict[str, Any]):
    """Display metrics dashboard."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Total Cost",
            f"${stats['total_cost_usd']:.4f}",
            help="Cumulative cost for this session"
        )
    
    with col2:
        st.metric(
            "🎫 Total Tokens",
            f"{stats['total_tokens']:,}",
            help="Total tokens used (prompt + completion)"
        )
    
    with col3:
        budget_pct = stats['budget_stats']['percentage_used']
        delta_color = "off" if budget_pct < 50 else "normal"
        st.metric(
            "📊 Budget Used",
            f"{budget_pct:.1f}%",
            f"{stats['budget_stats']['remaining_tokens']:,} remaining",
            delta_color=delta_color
        )
    
    with col4:
        st.metric(
            "💬 Messages",
            stats['chat_history_length'],
            help="Total messages in conversation"
        )


def display_evaluation_card(metrics: Dict[str, Any]):
    """Display quality evaluation card."""
    st.markdown("### 📊 Quality Evaluation")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        quality_label = metrics['quality_label']
        score = metrics['evaluation']['overall_score']
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Quality Score"},
            gauge={
                'axis': {'range': [None, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.6], 'color': "lightgray"},
                    {'range': [0.6, 0.8], 'color': "lightblue"},
                    {'range': [0.8, 1], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.9
                }
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        quality_class = quality_label.lower().replace(" ", "-")
        st.markdown(f'<p class="quality-{quality_class}">📈 {quality_label}</p>', unsafe_allow_html=True)
    
    with col2:
        eval_data = metrics['evaluation']
        
        st.markdown("#### Quality Indicators")
        
        indicators = [
            ("📝 Topic Coverage", f"{eval_data['topic_coverage']:.0%}", eval_data['topic_coverage'] > 0.7),
            ("📚 Has Citations", "Yes" if eval_data['has_citations'] else "No", eval_data['has_citations']),
            ("🔢 Has Numbers", "Yes" if eval_data['has_numbers'] else "No", eval_data['has_numbers']),
            ("🏗️ Well Structured", "Yes" if eval_data['has_structure'] else "No", eval_data['has_structure']),
        ]
        
        for label, value, is_good in indicators:
            icon = "✅" if is_good else "⚠️"
            st.write(f"{icon} **{label}**: {value}")


def display_cost_breakdown(stats: Dict[str, Any]):
    """Display cost breakdown chart."""
    st.markdown("### 💰 Cost Analysis")
    
    if st.session_state.responses:
        # Extract token data from responses
        data = []
        for i, resp in enumerate(st.session_state.responses):
            if resp.success and resp.metrics:
                tokens = resp.metrics['tokens']
                data.append({
                    'Query': f"Q{i+1}",
                    'Prompt Tokens': tokens['prompt_tokens'],
                    'Completion Tokens': tokens['completion_tokens']
                })
        
        if data:
            df = pd.DataFrame(data)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Prompt Tokens',
                x=df['Query'],
                y=df['Prompt Tokens'],
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                name='Completion Tokens',
                x=df['Query'],
                y=df['Completion Tokens'],
                marker_color='darkblue'
            ))
            
            fig.update_layout(
                barmode='stack',
                title='Token Usage per Query',
                xaxis_title='Query Number',
                yaxis_title='Tokens',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost data available yet. Submit a query to see analytics.")
    else:
        st.info("No queries submitted yet.")


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🤖 LLMOps Production Agent")
    st.markdown("**Production-ready AI agent with observability, cost tracking, and quality evaluation**")
    
    # Show a success message that nest-asyncio is active (helps with debugging)
    # This can be removed later, but helps confirm the fix is working
    if "startup_message_shown" not in st.session_state:
        st.session_state.startup_message_shown = True
        # Don't show message, just mark as shown
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Agent Preset Selection
        st.subheader("🎭 Agent Preset")
        presets = AgentPreset.list_presets()
        preset_labels = {
            "market_analyst": "📈 Market Analyst",
            "research_assistant": "🔬 Research Assistant",
            "technical_advisor": "💻 Technical Advisor"
        }
        
        selected_preset = st.selectbox(
            "Choose agent type:",
            presets,
            format_func=lambda x: preset_labels.get(x, x),
            index=presets.index(st.session_state.selected_preset) if st.session_state.selected_preset in presets else 0
        )
        
        if st.button("🔄 Initialize/Switch Agent", use_container_width=True):
            with st.spinner("Initializing agent..."):
                try:
                    create_agent(selected_preset)
                    st.success(f"✅ {preset_labels[selected_preset]} ready!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Initialization error: {str(e)}")
                    st.info("💡 Try: Stop server (Ctrl+C) and restart with `streamlit run streamlit_production_ui.py`")
        
        # Display current agent info
        if st.session_state.agent_initialized:
            st.success(f"🟢 {preset_labels[st.session_state.selected_preset]} Active")
            preset_config = AgentPreset.get_preset(st.session_state.selected_preset)
            st.caption(f"🔍 Web Search: {'Enabled' if preset_config['enable_web_search'] else 'Disabled'}")
        else:
            st.warning("⚪ No agent initialized")
        
        st.markdown("---")
        
        # Session Controls
        st.subheader("🎮 Session Controls")
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            if st.session_state.agent:
                st.session_state.agent.clear_history()
            st.session_state.chat_history = []
            st.session_state.responses = []
            st.session_state.progress_updates = []
            st.success("Chat cleared!")
            st.rerun()
        
        if st.button("📥 Export Session", use_container_width=True) and st.session_state.agent:
            session_data = st.session_state.agent.export_session_data()
            json_str = json.dumps(session_data, indent=2)
            st.download_button(
                label="💾 Download JSON",
                data=json_str,
                file_name=f"session_{session_data['session_id'][:8]}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Environment Info
        with st.expander("ℹ️ Environment"):
            import os
            st.caption(f"**Endpoint**: {os.getenv('AZURE_AI_PROJECT_ENDPOINT', 'Not set')[:50]}...")
            st.caption(f"**Model**: {os.getenv('AZURE_AI_MODEL_DEPLOYMENT_NAME', 'Not set')}")
    
    # Main Content
    if not st.session_state.agent_initialized:
        st.info("👈 Please initialize an agent from the sidebar to get started.")
        
        # Show preset descriptions
        st.markdown("### 📚 Available Agent Presets")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📈 Market Analyst")
            st.write("Specializes in technology stock valuations, market data analysis, and financial metrics.")
            st.caption("✓ Web Search Enabled")
        
        with col2:
            st.markdown("#### 🔬 Research Assistant")
            st.write("Helps find accurate information with detailed citations and well-structured responses.")
            st.caption("✓ Web Search Enabled")
        
        with col3:
            st.markdown("#### 💻 Technical Advisor")
            st.write("Provides technical guidance for software development with best practices and examples.")
            st.caption("○ Web Search Disabled")
        
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analytics", "📋 History"])
    
    with tab1:
        # Chat Interface
        st.markdown("### 💬 Chat with Agent")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and "metadata" in msg:
                        with st.expander("📊 View Metrics"):
                            metadata = msg["metadata"]
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("⏱️ Duration", f"{metadata.get('duration_ms', 0):.0f}ms")
                            with col2:
                                st.metric("🎫 Tokens", f"{metadata.get('total_tokens', 0):,}")
                            with col3:
                                st.metric("💰 Cost", f"${metadata.get('cost', 0):.4f}")
        
        # Display follow-up questions for the last assistant message
        if st.session_state.chat_history:
            last_msg = st.session_state.chat_history[-1]
            if last_msg["role"] == "assistant" and "follow_up_questions" in last_msg:
                follow_ups = last_msg["follow_up_questions"]
                if follow_ups:
                    st.markdown("---")
                    st.markdown("**💡 Suggested follow-up questions:**")
                    cols = st.columns(len(follow_ups))
                    for i, (col, question) in enumerate(zip(cols, follow_ups), 1):
                        with col:
                            if st.button(f"{i}. {question}", key=f"followup_{len(st.session_state.chat_history)}_{i}", use_container_width=True):
                                # Use the question as the next prompt
                                st.session_state.next_prompt = question
                                st.rerun()
        
        # Chat input (check for pre-filled prompt from follow-up question)
        default_prompt = st.session_state.next_prompt
        if default_prompt:
            st.session_state.next_prompt = None
            prompt = default_prompt
        else:
            prompt = st.chat_input("Ask me anything...")
        
        if prompt:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get and display assistant response with streaming
            with st.chat_message("assistant"):
                progress_placeholder = st.empty()
                response_placeholder = st.empty()
                
                # Clear previous progress updates
                st.session_state.progress_updates = []
                
                # Variables for streaming
                full_response = ""
                response_data = None
                has_error = False
                
                # Run agent with streaming
                async def stream_response():
                    nonlocal full_response, response_data, has_error
                    
                    async for chunk in st.session_state.agent.run_stream(
                        query=prompt,
                        expected_topics=AgentPreset.get_preset(st.session_state.selected_preset)["expected_topics"]
                    ):
                        chunk_type = chunk.get("type")
                        
                        if chunk_type == "progress":
                            progress_placeholder.info(f"⏳ {chunk.get('message', '')}")
                        
                        elif chunk_type == "token":
                            # Accumulate and display tokens in real-time
                            full_response += chunk.get("token", "")
                            response_placeholder.markdown(full_response + "▌")
                        
                        elif chunk_type == "complete":
                            # Final response
                            response_data = chunk
                            response_placeholder.markdown(full_response)
                            progress_placeholder.empty()
                        
                        elif chunk_type == "error":
                            has_error = True
                            error_msg = f"❌ Error: {chunk.get('error', 'Unknown error')}"
                            response_placeholder.error(error_msg)
                            progress_placeholder.empty()
                            return error_msg
                    
                    return response_data
                
                # Execute streaming
                result = asyncio.run(stream_response())
                
                if has_error:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result
                    })
                elif response_data:
                    # Store response for analytics
                    st.session_state.responses.append(AgentResponse(
                        success=True,
                        response=response_data["response"],
                        request_id=response_data["request_id"],
                        agent_name=response_data["agent_name"],
                        query=response_data["query"],
                        follow_up_questions=response_data["follow_up_questions"],
                        metrics=response_data["metrics"]
                    ))
                    
                    # Add to chat history with metadata
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response_data["response"],
                        "metadata": {
                            "duration_ms": response_data["metrics"]['duration_ms'],
                            "total_tokens": response_data["metrics"]['tokens']['total_tokens'],
                            "cost": response_data["metrics"]['tokens']['estimated_cost_usd'],
                            "quality_label": response_data["metrics"]['quality_label']
                        },
                        "follow_up_questions": response_data["follow_up_questions"]
                    })
                    
                    # Display evaluation
                    with st.expander("📊 Quality Evaluation", expanded=True):
                        display_evaluation_card(response_data["metrics"])
            
            st.rerun()
        
        # Display current statistics
        if st.session_state.agent:
            st.markdown("---")
            stats = st.session_state.agent.get_cumulative_stats()
            display_metrics_dashboard(stats)
    
    with tab2:
        # Analytics Dashboard
        st.markdown("### 📊 Analytics Dashboard")
        
        if st.session_state.agent:
            stats = st.session_state.agent.get_cumulative_stats()
            
            # Metrics Overview
            display_metrics_dashboard(stats)
            
            st.markdown("---")
            
            # Cost Breakdown
            col1, col2 = st.columns([2, 1])
            
            with col1:
                display_cost_breakdown(stats)
            
            with col2:
                st.markdown("### 💳 Budget Status")
                
                budget_stats = stats['budget_stats']
                
                # Budget progress bar
                progress_pct = budget_stats['percentage_used'] / 100
                st.progress(progress_pct)
                
                st.metric("Used", f"{budget_stats['total_tokens']:,} tokens")
                st.metric("Budget", f"{budget_stats['budget']:,} tokens")
                st.metric("Remaining", f"{budget_stats['remaining_tokens']:,} tokens")
                
                # Warning if budget is running low
                if budget_stats['percentage_used'] > 80:
                    st.error("⚠️ Budget usage above 80%!")
                elif budget_stats['percentage_used'] > 60:
                    st.warning("⚡ Budget usage above 60%")
            
            st.markdown("---")
            
            # Response Quality Trends
            if st.session_state.responses:
                st.markdown("### 📈 Quality Trends")
                
                quality_data = []
                for i, resp in enumerate(st.session_state.responses):
                    if resp.success and resp.metrics:
                        eval_data = resp.metrics['evaluation']
                        quality_data.append({
                            'Query': f"Q{i+1}",
                            'Overall Score': eval_data['overall_score'],
                            'Topic Coverage': eval_data['topic_coverage']
                        })
                
                if quality_data:
                    df = pd.DataFrame(quality_data)
                    
                    fig = px.line(
                        df,
                        x='Query',
                        y=['Overall Score', 'Topic Coverage'],
                        title='Quality Metrics Over Time',
                        labels={'value': 'Score', 'variable': 'Metric'}
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No analytics data available yet.")
    
    with tab3:
        # History View
        st.markdown("### 📋 Conversation History")
        
        if st.session_state.agent:
            history = st.session_state.agent.get_history()
            
            if history:
                for i, msg in enumerate(history):
                    with st.expander(f"**{msg['role'].upper()}** - {msg['timestamp']}", expanded=False):
                        st.markdown(msg['content'])
            else:
                st.info("No conversation history yet. Start chatting to see history.")
        else:
            st.info("Agent not initialized.")
        
        # Progress Log
        st.markdown("### 🔄 Progress Log")
        
        if st.session_state.progress_updates:
            for update in st.session_state.progress_updates[-10:]:  # Show last 10
                status_class = update.status.value
                st.markdown(
                    f'<div class="status-badge status-{status_class}">{update.status.value.upper()}</div>',
                    unsafe_allow_html=True
                )
                st.caption(f"{update.timestamp}: {update.message}")
        else:
            st.info("No progress updates yet.")


if __name__ == "__main__":
    main()

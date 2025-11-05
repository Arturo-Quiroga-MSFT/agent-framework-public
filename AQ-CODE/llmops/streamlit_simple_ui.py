"""
Streamlit UI for MAF Agent with LLMOps Features

Progressive enhancement starting from working basic pattern.
Features added incrementally: cost tracking, observability, quality evaluation.

Run: streamlit run AQ-CODE/llmops/streamlit_simple_ui.py
"""

import asyncio
import logging
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Dict, Any

# Suppress specific benign warnings at the logging level
logging.getLogger('azure.monitor.opentelemetry.exporter.statsbeat._manager').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=DeprecationWarning, module='streamlit')

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_framework import ChatAgent, HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

# Import LLMOps components
from observability import MAFObservability
from cost_tracker import CostTracker
from evaluator import AgentEvaluator

# Load environment
load_dotenv(Path(__file__).parent.parent / "orchestration" / ".env")

# Page config
st.set_page_config(
    page_title="Simple MAF Agent",
    page_icon="🤖",
    layout="wide"
)

# Agent Presets
AGENT_PRESETS = {
    "market_analyst": {
        "name": "Market Analyst",
        "icon": "📈",
        "instructions": """You are an expert financial market analyst. Provide detailed market analysis, 
        stock comparisons, financial metrics, and investment insights. Always use web search to get the 
        latest market data, stock prices, and financial news. Include specific numbers, P/E ratios, 
        market caps, and historical performance data in your responses.""",
        "enable_web_search": True,
        "expected_topics": ["stock prices", "financial metrics", "market analysis", "investment recommendations"]
    },
    "research_assistant": {
        "name": "Research Assistant",
        "icon": "🔬",
        "instructions": """You are a thorough research assistant. Help users find and synthesize information 
        from multiple sources. Always use web search to gather current, accurate information. Provide 
        well-structured responses with clear citations and sources. Organize information logically and 
        highlight key findings.""",
        "enable_web_search": True,
        "expected_topics": ["research findings", "citations", "data synthesis", "key insights"]
    },
    "technical_advisor": {
        "name": "Technical Advisor",
        "icon": "💻",
        "instructions": """You are an expert technical advisor specializing in software development, 
        cloud architecture, and technology solutions. Provide detailed technical explanations, code 
        examples when appropriate, best practices, and architectural guidance. You don't need web search 
        for most technical questions as you have comprehensive knowledge.""",
        "enable_web_search": False,
        "expected_topics": ["technical solutions", "code examples", "best practices", "architecture"]
    },
    "business_consultant": {
        "name": "Business Consultant",
        "icon": "💼",
        "instructions": """You are a strategic business consultant. Help with business strategy, market 
        analysis, competitive positioning, and operational improvements. Use web search when needed for 
        current market trends, competitor information, or industry insights. Provide actionable 
        recommendations backed by data.""",
        "enable_web_search": True,
        "expected_topics": ["business strategy", "market trends", "recommendations", "analysis"]
    },
    "general_assistant": {
        "name": "General Assistant",
        "icon": "🤖",
        "instructions": """You are a helpful AI assistant. Provide clear, accurate, and helpful responses 
        to a wide variety of questions. Use web search when you need current information or when asked 
        about recent events. Be conversational and adapt your style to the user's needs.""",
        "enable_web_search": True,
        "expected_topics": []
    }
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "cost_tracker" not in st.session_state:
    st.session_state.cost_tracker = CostTracker()
if "observability" not in st.session_state:
    st.session_state.observability = MAFObservability()
if "evaluator" not in st.session_state:
    st.session_state.evaluator = AgentEvaluator()
if "analytics" not in st.session_state:
    st.session_state.analytics = []
if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = "general_assistant"


async def run_agent(user_query: str, preset_key: str = "general_assistant", 
                    stream_container=None) -> Dict[str, Any]:
    """Run agent with conversation history, streaming, and LLMOps tracking."""
    start_time = time.time()
    preset = AGENT_PRESETS[preset_key]
    
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            # Create tools if enabled
            tools = None
            if preset["enable_web_search"]:
                tools = HostedWebSearchTool(
                    name="Web Search",
                    description="Search the web for current information"
                )
            
            # Create agent with preset instructions
            agent = ChatAgent(
                chat_client=client,
                instructions=preset["instructions"],
                tools=tools,
            )
            
            # Create or reuse thread for conversation history
            if st.session_state.thread_id:
                thread = agent.get_new_thread(service_thread_id=st.session_state.thread_id)
            else:
                thread = agent.get_new_thread()
            
            # Run agent with streaming and observability
            full_response = ""
            with st.session_state.observability.create_span("agent.run_stream"):
                async for chunk in agent.run_stream(user_query, thread=thread, store=True):
                    if chunk.text:
                        full_response += chunk.text
                        # Update streaming display in real-time if container provided
                        if stream_container:
                            stream_container.markdown(full_response + "▌")
            
            # Final update without cursor
            if stream_container:
                stream_container.markdown(full_response)
            
            # Store thread ID for next message
            if thread.service_thread_id:
                st.session_state.thread_id = thread.service_thread_id
            
            response_text = full_response
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Track costs (rough estimates)
            prompt_tokens = int(len(user_query.split()) * 1.5)
            completion_tokens = int(len(response_text.split()) * 1.5)
            total_tokens = prompt_tokens + completion_tokens
            
            model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4")
            st.session_state.cost_tracker.record_cost(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                agent_name="SimpleAgent"
            )
            
            # Quality evaluation with preset topics
            evaluation = st.session_state.evaluator.evaluate_response(
                response=response_text,
                expected_topics=preset["expected_topics"] if preset["expected_topics"] else None
            )
            
            # Store analytics
            analytics_data = {
                "query": user_query[:50] + "..." if len(user_query) > 50 else user_query,
                "duration_ms": duration_ms,
                "tokens": total_tokens,
                "cost_usd": st.session_state.cost_tracker.get_total_cost(),
                "quality_score": evaluation["overall_score"]
            }
            st.session_state.analytics.append(analytics_data)
            
            return {
                "response": response_text,
                "duration_ms": duration_ms,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens
                },
                "cost_usd": st.session_state.cost_tracker.get_total_cost(),
                "evaluation": evaluation
            }


def main():
    st.title("🤖 MAF Agent with LLMOps")
    st.markdown("Chat with conversation history + cost tracking + quality evaluation")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analytics", "📋 History"])
    
    with tab1:
        # Sidebar in chat tab
        with st.sidebar:
            st.header("Settings")
            
            # Agent Preset Selection
            st.markdown("### Agent Preset")
            preset_options = {k: f"{v['icon']} {v['name']}" for k, v in AGENT_PRESETS.items()}
            selected_preset = st.selectbox(
                "Choose agent role:",
                options=list(preset_options.keys()),
                format_func=lambda x: preset_options[x],
                index=list(preset_options.keys()).index(st.session_state.selected_preset)
            )
            
            # Update preset and reset conversation if changed
            if selected_preset != st.session_state.selected_preset:
                st.session_state.selected_preset = selected_preset
                st.session_state.thread_id = None
                st.session_state.messages = []
                st.success(f"Switched to {AGENT_PRESETS[selected_preset]['name']}!")
                st.rerun()
            
            # Show current preset info
            current_preset = AGENT_PRESETS[st.session_state.selected_preset]
            st.info(f"**Web Search:** {'✅ Enabled' if current_preset['enable_web_search'] else '❌ Disabled'}")
            
            st.markdown("---")
            
            if st.button("🔄 Clear Conversation"):
                st.session_state.thread_id = None
                st.session_state.messages = []
                st.success("Conversation cleared!")
                st.rerun()
            
            # Display metrics
            st.markdown("### Session Metrics")
            total_cost = st.session_state.cost_tracker.get_total_cost()
            st.metric("Total Cost", f"${total_cost:.4f}")
            st.metric("Messages", len(st.session_state.messages))
            
            if st.session_state.analytics:
                avg_quality = sum(a["quality_score"] for a in st.session_state.analytics) / len(st.session_state.analytics)
                st.metric("Avg Quality", f"{avg_quality:.2f}/5")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "metadata" in message:
                    with st.expander("📊 Details"):
                        meta = message["metadata"]
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Duration", f"{meta['duration_ms']}ms")
                        col2.metric("Tokens", meta['tokens']['total'])
                        col3.metric("Quality", f"{meta['evaluation']['overall_score']:.1f}/5")
        
        # Chat input
        if prompt := st.chat_input("Ask me anything..."):
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Get and display assistant response with streaming
            with st.chat_message("assistant"):
                # Create a container for streaming updates
                stream_container = st.empty()
                
                try:
                    # Run agent with streaming container
                    result = asyncio.run(run_agent(
                        prompt, 
                        st.session_state.selected_preset,
                        stream_container=stream_container
                    ))
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "metadata": result
                    })
                    
                    # Show quick stats
                    with st.expander("📊 Details"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Duration", f"{result['duration_ms']}ms")
                        col2.metric("Tokens", result['tokens']['total'])
                        col3.metric("Quality", f"{result['evaluation']['overall_score']:.1f}/5")
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    with tab2:
        st.markdown("### 📊 Analytics Dashboard")
        
        if st.session_state.analytics:
            df = pd.DataFrame(st.session_state.analytics)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Cost Over Time")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=df['cost_usd'],
                    mode='lines+markers',
                    name='Cumulative Cost'
                ))
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Quality Scores")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=df['quality_score'],
                    mode='lines+markers',
                    name='Quality',
                    line=dict(color='green')
                ))
                fig.update_layout(height=300, showlegend=False, yaxis_range=[0, 5])
                st.plotly_chart(fig, width='stretch')
            
            st.markdown("#### Token Usage")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['tokens'],
                name='Tokens per Query'
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, width='stretch')
            
            st.markdown("#### Data Table")
            st.dataframe(df, width='stretch')
        else:
            st.info("No analytics data yet. Start chatting to see metrics!")
    
    with tab3:
        st.markdown("### 📋 Conversation History")
        
        if st.session_state.messages:
            for i, msg in enumerate(st.session_state.messages):
                with st.expander(f"{msg['role'].upper()} - Message {i+1}", expanded=False):
                    st.markdown(msg['content'])
                    if 'metadata' in msg:
                        st.json(msg['metadata'])
        else:
            st.info("No messages yet. Start chatting!")
        
        # Export button
        if st.session_state.messages:
            if st.button("📥 Export Conversation"):
                import json
                export_data = {
                    "messages": st.session_state.messages,
                    "analytics": st.session_state.analytics,
                    "total_cost": st.session_state.cost_tracker.get_total_cost()
                }
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name="conversation_export.json",
                    mime="application/json"
                )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Fleet Health Dashboard - Control Plane Integration

A Streamlit dashboard that provides real-time visibility into your AI agent fleet,
integrating data from the Microsoft Foundry Control Plane sources:

- Agent inventory and versions from Azure AI Projects SDK
- Performance metrics from Application Insights
- Alerts from Defender and Application Insights
- Cost trends and token usage
- Compliance status and policy violations

PREREQUISITES:
- Azure CLI authenticated: `az login`
- Environment variables configured (see .env.example)
- Required packages: streamlit, azure-ai-projects, azure-monitor-query

USAGE:
    streamlit run AQ-CODE/control-plane/fleet_health_dashboard.py --server.port 8099

FEATURES:
- Fleet Overview with health scores and KPIs
- Agent inventory with status indicators
- Alert summaries by severity
- Cost trends visualization
- Compliance posture tracking
- Drill-down to individual agent metrics
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fleet_health_client import (
    FleetHealthClient,
    FleetHealthSummary,
    AgentHealthMetrics,
    HealthStatus,
    get_fleet_health_sync
)

# Page configuration
st.set_page_config(
    page_title="Fleet Health Dashboard",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    if "fleet_data" not in st.session_state:
        st.session_state.fleet_data = None
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = None
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = None
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False
    if "client" not in st.session_state:
        st.session_state.client = None


def get_client() -> FleetHealthClient:
    """Get or create fleet health client."""
    if st.session_state.client is None:
        st.session_state.client = FleetHealthClient()
    return st.session_state.client


async def fetch_fleet_data() -> Optional[FleetHealthSummary]:
    """Fetch fleet health data asynchronously."""
    try:
        client = get_client()
        return await client.get_fleet_health_summary()
    except Exception as e:
        st.error(f"Error fetching fleet data: {e}")
        return None


def run_async(coro):
    """Run async coroutine in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def get_status_color(status: HealthStatus) -> str:
    """Get color for health status."""
    colors = {
        HealthStatus.HEALTHY: "#28a745",    # Green
        HealthStatus.WARNING: "#ffc107",    # Yellow
        HealthStatus.CRITICAL: "#dc3545",   # Red
        HealthStatus.UNKNOWN: "#6c757d"     # Gray
    }
    return colors.get(status, "#6c757d")


def get_status_emoji(status: HealthStatus) -> str:
    """Get emoji for health status."""
    emojis = {
        HealthStatus.HEALTHY: "✅",
        HealthStatus.WARNING: "⚠️",
        HealthStatus.CRITICAL: "🔴",
        HealthStatus.UNKNOWN: "❓"
    }
    return emojis.get(status, "❓")


def render_kpi_card(title: str, value: str, subtitle: str = "", delta: str = "", color: str = "#1E90FF"):
    """Render a KPI card with custom styling."""
    delta_html = f'<span style="font-size: 0.8em; color: {"#28a745" if delta.startswith("+") else "#dc3545" if delta.startswith("-") else "#6c757d"};">{delta}</span>' if delta else ""
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
        border-left: 4px solid {color};
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 10px;
    ">
        <div style="font-size: 0.9em; color: #666; margin-bottom: 5px;">{title}</div>
        <div style="font-size: 2em; font-weight: bold; color: #333;">{value} {delta_html}</div>
        <div style="font-size: 0.8em; color: #888;">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_fleet_overview(summary: FleetHealthSummary):
    """Render the fleet overview section."""
    st.markdown("## 📊 Fleet Overview")
    
    # Top-level KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        render_kpi_card(
            "Fleet Health Score",
            f"{summary.fleet_health_score:.1f}%",
            f"{summary.active_agents} active agents",
            color="#1E90FF"
        )
    
    with col2:
        render_kpi_card(
            "Total Agents",
            str(summary.total_agents),
            f"✅ {summary.healthy_agents} | ⚠️ {summary.warning_agents} | 🔴 {summary.critical_agents}",
            color="#28a745"
        )
    
    with col3:
        render_kpi_card(
            "Success Rate",
            f"{summary.avg_success_rate * 100:.1f}%",
            f"{summary.total_runs_24h:,} runs (24h)",
            color="#17a2b8"
        )
    
    with col4:
        render_kpi_card(
            "Cost (7d)",
            f"${summary.total_cost_7d:.2f}",
            f"${summary.total_cost_24h:.2f}/day avg",
            delta=f"{summary.cost_trend_pct:+.1f}%" if summary.cost_trend_pct else "",
            color="#ffc107"
        )
    
    with col5:
        total_alerts = summary.critical_alerts + summary.high_alerts + summary.medium_alerts + summary.low_alerts
        render_kpi_card(
            "Active Alerts",
            str(total_alerts),
            f"🔴 {summary.critical_alerts} | 🟠 {summary.high_alerts} | 🟡 {summary.medium_alerts}",
            color="#dc3545" if summary.critical_alerts > 0 else "#ffc107" if summary.high_alerts > 0 else "#28a745"
        )


def render_health_distribution(summary: FleetHealthSummary):
    """Render health distribution chart."""
    import plotly.graph_objects as go
    
    st.markdown("### 🏥 Health Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Donut chart
        fig = go.Figure(data=[go.Pie(
            labels=["Healthy", "Warning", "Critical"],
            values=[summary.healthy_agents, summary.warning_agents, summary.critical_agents],
            hole=0.6,
            marker_colors=["#28a745", "#ffc107", "#dc3545"],
            textinfo="value+percent",
            textposition="outside"
        )])
        
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            annotations=[dict(
                text=f"{summary.fleet_health_score:.0f}%",
                x=0.5, y=0.5,
                font_size=24,
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        **Health Score Factors:**
        - ✅ Error Rate < 5%
        - ✅ Latency < 2s
        - ✅ No compliance violations
        - ✅ Active in last 24h
        """)
        
        st.markdown("---")
        
        st.markdown("**Quick Actions:**")
        if summary.critical_agents > 0:
            st.warning(f"🔴 {summary.critical_agents} agent(s) need attention!")
        if summary.non_compliant_agents > 0:
            st.info(f"⚠️ {summary.non_compliant_agents} compliance issues to review")


def render_alerts_summary(summary: FleetHealthSummary):
    """Render alerts summary section."""
    st.markdown("### 🚨 Alerts Summary (24h)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Critical", summary.critical_alerts, 
                  delta=None,
                  delta_color="inverse")
        if summary.critical_alerts > 0:
            st.markdown('<div style="background: #dc354522; padding: 10px; border-radius: 5px;">⚡ Immediate action required</div>', unsafe_allow_html=True)
    
    with col2:
        st.metric("High", summary.high_alerts)
        if summary.high_alerts > 0:
            st.markdown('<div style="background: #fd7e1422; padding: 10px; border-radius: 5px;">📋 Review within 4h</div>', unsafe_allow_html=True)
    
    with col3:
        st.metric("Medium", summary.medium_alerts)
    
    with col4:
        st.metric("Low", summary.low_alerts)


def render_compliance_status(summary: FleetHealthSummary):
    """Render compliance status section."""
    st.markdown("### 🛡️ Compliance Posture")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        compliant_pct = (summary.compliant_agents / max(summary.total_agents, 1)) * 100
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {'#28a74522' if compliant_pct >= 80 else '#ffc10722' if compliant_pct >= 50 else '#dc354522'} 0%, transparent 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        ">
            <div style="font-size: 3em; font-weight: bold; color: {'#28a745' if compliant_pct >= 80 else '#ffc107' if compliant_pct >= 50 else '#dc3545'};">
                {compliant_pct:.0f}%
            </div>
            <div style="color: #666;">Compliance Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Compliance Breakdown:**")
        
        col2a, col2b = st.columns(2)
        with col2a:
            st.metric("✅ Compliant", summary.compliant_agents)
        with col2b:
            st.metric("❌ Non-Compliant", summary.non_compliant_agents)
        
        if summary.total_policy_violations > 0:
            st.warning(f"**{summary.total_policy_violations}** policy violations detected")
            st.markdown("*Go to Compliance tab for details*")


def render_agent_inventory(summary: FleetHealthSummary):
    """Render agent inventory table."""
    st.markdown("### 📋 Agent Inventory")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=["Healthy", "Warning", "Critical", "Unknown"],
            default=["Healthy", "Warning", "Critical"]
        )
    
    with col2:
        search = st.text_input("Search agents", placeholder="Enter agent name...")
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            options=["Health Score", "Name", "Total Runs", "Error Rate", "Cost"]
        )
    
    # Filter and sort agents
    filtered_agents = summary.agents
    
    # Apply status filter
    status_map = {
        "Healthy": HealthStatus.HEALTHY,
        "Warning": HealthStatus.WARNING,
        "Critical": HealthStatus.CRITICAL,
        "Unknown": HealthStatus.UNKNOWN
    }
    filtered_agents = [a for a in filtered_agents if a.status in [status_map.get(s) for s in status_filter]]
    
    # Apply search filter
    if search:
        filtered_agents = [a for a in filtered_agents if search.lower() in a.agent_name.lower()]
    
    # Sort
    sort_keys = {
        "Health Score": lambda a: -a.health_score,
        "Name": lambda a: a.agent_name,
        "Total Runs": lambda a: -a.total_runs,
        "Error Rate": lambda a: -a.error_rate,
        "Cost": lambda a: -a.estimated_cost_usd
    }
    filtered_agents.sort(key=sort_keys.get(sort_by, lambda a: a.agent_name))
    
    # Render table
    if not filtered_agents:
        st.info("No agents match the current filters")
        return
    
    # Header
    cols = st.columns([0.5, 2, 1, 1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown("**Status**")
    with cols[1]:
        st.markdown("**Agent Name**")
    with cols[2]:
        st.markdown("**Model**")
    with cols[3]:
        st.markdown("**Health**")
    with cols[4]:
        st.markdown("**Runs (24h)**")
    with cols[5]:
        st.markdown("**Error Rate**")
    with cols[6]:
        st.markdown("**Tokens**")
    with cols[7]:
        st.markdown("**Cost**")
    
    st.markdown("---")
    
    # Rows
    for agent in filtered_agents:
        cols = st.columns([0.5, 2, 1, 1, 1, 1, 1, 1])
        
        with cols[0]:
            st.markdown(get_status_emoji(agent.status))
        
        with cols[1]:
            if st.button(f"📊 {agent.agent_name}", key=f"agent_{agent.agent_id}", use_container_width=True):
                st.session_state.selected_agent = agent
        
        with cols[2]:
            st.markdown(f"`{agent.model}`")
        
        with cols[3]:
            color = get_status_color(agent.status)
            st.markdown(f'<span style="color: {color}; font-weight: bold;">{agent.health_score:.0f}%</span>', unsafe_allow_html=True)
        
        with cols[4]:
            st.markdown(f"{agent.total_runs:,}")
        
        with cols[5]:
            error_color = "#dc3545" if agent.error_rate > 0.1 else "#ffc107" if agent.error_rate > 0.05 else "#28a745"
            st.markdown(f'<span style="color: {error_color};">{agent.error_rate*100:.1f}%</span>', unsafe_allow_html=True)
        
        with cols[6]:
            st.markdown(f"{agent.total_tokens:,}")
        
        with cols[7]:
            st.markdown(f"${agent.estimated_cost_usd:.4f}")


def render_agent_details(agent: AgentHealthMetrics):
    """Render detailed view for a single agent."""
    st.markdown(f"### 🔍 Agent Details: {agent.agent_name}")
    
    # Back button
    if st.button("← Back to Inventory"):
        st.session_state.selected_agent = None
        st.rerun()
    
    st.markdown("---")
    
    # Agent info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Agent ID:**")
        st.code(agent.agent_id)
    
    with col2:
        st.markdown("**Version:**")
        st.markdown(f"v{agent.agent_version}")
    
    with col3:
        st.markdown("**Model:**")
        st.markdown(f"`{agent.model}`")
    
    with col4:
        st.markdown("**Status:**")
        st.markdown(f"{get_status_emoji(agent.status)} {agent.status.value.title()}")
    
    st.markdown("---")
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_kpi_card(
            "Health Score",
            f"{agent.health_score:.1f}%",
            agent.status.value.title(),
            color=get_status_color(agent.status)
        )
    
    with col2:
        render_kpi_card(
            "Success Rate",
            f"{(1-agent.error_rate)*100:.1f}%",
            f"{agent.successful_runs}/{agent.total_runs} runs",
            color="#28a745" if agent.error_rate < 0.05 else "#ffc107"
        )
    
    with col3:
        render_kpi_card(
            "Avg Latency",
            f"{agent.avg_latency_ms:.0f}ms",
            f"P95: {agent.p95_latency_ms:.0f}ms",
            color="#17a2b8"
        )
    
    with col4:
        render_kpi_card(
            "Token Usage",
            f"{agent.total_tokens:,}",
            f"Est. ${agent.estimated_cost_usd:.4f}",
            color="#ffc107"
        )
    
    # Compliance
    st.markdown("### Compliance Status")
    
    if agent.compliance_status == "compliant":
        st.success("✅ This agent is compliant with all policies")
    else:
        st.warning(f"⚠️ {agent.policy_violations} policy violation(s) detected")
        st.markdown("**Recommended Actions:**")
        st.markdown("- Review agent instructions and system prompt")
        st.markdown("- Check guardrail configurations")
        st.markdown("- Verify metadata is properly set")
    
    # Actions
    st.markdown("### Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.button("📈 View Traces", disabled=True, help="Open in Application Insights")
    with col2:
        st.button("🔧 Edit Agent", disabled=True, help="Open in AI Foundry")
    with col3:
        st.button("🧪 Run Evaluation", disabled=True, help="Trigger evaluation run")
    with col4:
        st.button("🛑 Block Agent", disabled=True, help="Block incoming requests")


def render_cost_analysis(summary: FleetHealthSummary):
    """Render cost analysis section."""
    st.markdown("### 💰 Cost Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        import plotly.graph_objects as go
        
        # Cost by agent (top 10)
        agents_by_cost = sorted(summary.agents, key=lambda a: -a.estimated_cost_usd)[:10]
        
        fig = go.Figure(data=[
            go.Bar(
                x=[a.agent_name for a in agents_by_cost],
                y=[a.estimated_cost_usd for a in agents_by_cost],
                marker_color="#1E90FF"
            )
        ])
        
        fig.update_layout(
            title="Cost by Agent (Top 10)",
            xaxis_title="Agent",
            yaxis_title="Estimated Cost ($)",
            height=300,
            margin=dict(t=40, b=40, l=40, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Cost Breakdown:**")
        st.metric("Total (7 days)", f"${summary.total_cost_7d:.2f}")
        st.metric("Daily Average", f"${summary.total_cost_24h:.2f}")
        st.metric("Total Tokens (24h)", f"{summary.total_tokens_24h:,}")
        
        st.markdown("---")
        
        st.markdown("**Cost Optimization Tips:**")
        st.markdown("- Switch to smaller models for simple tasks")
        st.markdown("- Implement caching for repeated queries")
        st.markdown("- Set token limits per request")


def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.markdown("## 🎛️ Control Plane")
        st.markdown("Fleet Health Dashboard")
        
        st.markdown("---")
        
        # Refresh controls
        st.markdown("### 🔄 Data Refresh")
        
        if st.button("Refresh Now", use_container_width=True):
            with st.spinner("Fetching fleet data..."):
                st.session_state.fleet_data = run_async(fetch_fleet_data())
                st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        st.session_state.auto_refresh = st.checkbox(
            "Auto-refresh (60s)",
            value=st.session_state.auto_refresh
        )
        
        if st.session_state.last_refresh:
            st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📍 Navigation")
        
        page = st.radio(
            "View",
            options=["Overview", "Agents", "Alerts", "Compliance", "Cost Analysis"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Environment info
        st.markdown("### ⚙️ Configuration")
        
        endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "Not configured")
        if endpoint and len(endpoint) > 50:
            endpoint = endpoint[:50] + "..."
        st.caption(f"**Endpoint:** {endpoint}")
        
        subscription = os.environ.get("AZURE_SUBSCRIPTION_ID", "Not configured")
        if subscription and len(subscription) > 20:
            subscription = subscription[:20] + "..."
        st.caption(f"**Subscription:** {subscription}")
        
        st.markdown("---")
        
        # Links
        st.markdown("### 🔗 Quick Links")
        st.markdown("[📊 Azure Portal](https://portal.azure.com)")
        st.markdown("[🤖 AI Foundry](https://ai.azure.com)")
        st.markdown("[📈 Application Insights](https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents)")
        
        return page


def main():
    """Main application entry point."""
    # Initialize
    init_session_state()
    
    # Render sidebar and get current page
    current_page = render_sidebar()
    
    # Header
    st.title("🎛️ Fleet Health Dashboard")
    st.caption("Microsoft Foundry Control Plane Integration")
    
    # Check for environment configuration
    if not os.environ.get("AZURE_AI_PROJECT_ENDPOINT"):
        st.error("⚠️ AZURE_AI_PROJECT_ENDPOINT environment variable not set")
        st.info("""
        **To configure:**
        1. Set your Azure AI Project endpoint in `.env`:
           ```
           AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
           ```
        2. Run `az login` to authenticate
        3. Restart the dashboard
        """)
        
        st.markdown("---")
        st.markdown("### 🎮 Demo Mode")
        st.info("Running in demo mode with sample data...")
        
        # Create demo data
        if st.session_state.fleet_data is None:
            st.session_state.fleet_data = create_demo_data()
    
    # Fetch data if needed
    if st.session_state.fleet_data is None:
        with st.spinner("Fetching fleet health data..."):
            st.session_state.fleet_data = run_async(fetch_fleet_data())
            st.session_state.last_refresh = datetime.now()
    
    # Check if we have data
    if st.session_state.fleet_data is None:
        st.warning("Unable to fetch fleet data. Check your configuration and try again.")
        return
    
    summary = st.session_state.fleet_data
    
    # Check if viewing specific agent
    if st.session_state.selected_agent:
        render_agent_details(st.session_state.selected_agent)
        return
    
    # Render based on current page
    if current_page == "Overview":
        render_fleet_overview(summary)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            render_health_distribution(summary)
        with col2:
            render_alerts_summary(summary)
        
        st.markdown("---")
        render_compliance_status(summary)
        
    elif current_page == "Agents":
        render_agent_inventory(summary)
        
    elif current_page == "Alerts":
        render_alerts_summary(summary)
        st.markdown("---")
        st.info("Detailed alert management coming soon. Use Azure Portal for full alert investigation.")
        
    elif current_page == "Compliance":
        render_compliance_status(summary)
        st.markdown("---")
        
        if summary.total_policy_violations > 0:
            st.markdown("### Policy Violations")
            for agent in summary.agents:
                if agent.compliance_status != "compliant":
                    with st.expander(f"⚠️ {agent.agent_name} - {agent.policy_violations} violation(s)"):
                        st.markdown("**Recommended fixes:**")
                        st.markdown("- Add comprehensive instructions/system prompt")
                        st.markdown("- Configure appropriate tools")
                        st.markdown("- Add metadata for governance tracking")
        else:
            st.success("✅ All agents are compliant!")
        
    elif current_page == "Cost Analysis":
        render_cost_analysis(summary)
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        import time
        time.sleep(60)
        st.session_state.fleet_data = None
        st.rerun()


def create_demo_data() -> FleetHealthSummary:
    """Create demo data for testing without Azure connection."""
    demo_agents = [
        AgentHealthMetrics(
            agent_id="demo-agent-1",
            agent_name="Market_Researcher",
            agent_version="2",
            model="gpt-4o-mini",
            status=HealthStatus.HEALTHY,
            health_score=92.0,
            total_runs=156,
            successful_runs=152,
            failed_runs=4,
            error_rate=0.026,
            avg_latency_ms=1250,
            p95_latency_ms=2100,
            total_tokens=45000,
            prompt_tokens=30000,
            completion_tokens=15000,
            estimated_cost_usd=0.045,
            compliance_status="compliant",
            policy_violations=0
        ),
        AgentHealthMetrics(
            agent_id="demo-agent-2",
            agent_name="Marketing_Strategist",
            agent_version="1",
            model="gpt-4o",
            status=HealthStatus.HEALTHY,
            health_score=88.0,
            total_runs=89,
            successful_runs=85,
            failed_runs=4,
            error_rate=0.045,
            avg_latency_ms=1800,
            p95_latency_ms=3200,
            total_tokens=62000,
            prompt_tokens=40000,
            completion_tokens=22000,
            estimated_cost_usd=0.85,
            compliance_status="compliant",
            policy_violations=0
        ),
        AgentHealthMetrics(
            agent_id="demo-agent-3",
            agent_name="Legal_Compliance_Advisor",
            agent_version="3",
            model="gpt-4o",
            status=HealthStatus.WARNING,
            health_score=72.0,
            total_runs=45,
            successful_runs=40,
            failed_runs=5,
            error_rate=0.111,
            avg_latency_ms=2500,
            p95_latency_ms=4500,
            total_tokens=38000,
            prompt_tokens=25000,
            completion_tokens=13000,
            estimated_cost_usd=0.52,
            compliance_status="non-compliant",
            policy_violations=1
        ),
        AgentHealthMetrics(
            agent_id="demo-agent-4",
            agent_name="Financial_Analyst",
            agent_version="1",
            model="gpt-4o-mini",
            status=HealthStatus.HEALTHY,
            health_score=95.0,
            total_runs=234,
            successful_runs=232,
            failed_runs=2,
            error_rate=0.009,
            avg_latency_ms=980,
            p95_latency_ms=1500,
            total_tokens=72000,
            prompt_tokens=48000,
            completion_tokens=24000,
            estimated_cost_usd=0.072,
            compliance_status="compliant",
            policy_violations=0
        ),
        AgentHealthMetrics(
            agent_id="demo-agent-5",
            agent_name="Technical_Architect",
            agent_version="2",
            model="gpt-4o",
            status=HealthStatus.CRITICAL,
            health_score=45.0,
            total_runs=67,
            successful_runs=52,
            failed_runs=15,
            error_rate=0.224,
            avg_latency_ms=3500,
            p95_latency_ms=6000,
            total_tokens=55000,
            prompt_tokens=35000,
            completion_tokens=20000,
            estimated_cost_usd=0.75,
            compliance_status="non-compliant",
            policy_violations=2
        ),
    ]
    
    return FleetHealthSummary(
        total_agents=5,
        active_agents=5,
        healthy_agents=3,
        warning_agents=1,
        critical_agents=1,
        fleet_health_score=78.4,
        avg_success_rate=0.917,
        total_runs_24h=591,
        total_errors_24h=30,
        total_cost_24h=2.24,
        total_cost_7d=15.68,
        total_tokens_24h=272000,
        cost_trend_pct=-5.2,
        compliant_agents=3,
        non_compliant_agents=2,
        total_policy_violations=3,
        critical_alerts=2,
        high_alerts=5,
        medium_alerts=8,
        low_alerts=12,
        generated_at=datetime.now(),
        agents=demo_agents
    )


if __name__ == "__main__":
    main()

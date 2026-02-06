#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Fleet Health Dashboard - Dash Version

A sophisticated Dash dashboard providing real-time visibility into your AI agent fleet,
integrating data from the Microsoft Foundry Control Plane sources.

PREREQUISITES:
- Azure CLI authenticated: `az login`
- Environment variables configured (see .env.example)
- Required packages: dash, dash-bootstrap-components, plotly, pandas

USAGE:
    python AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025/fleet_health_dashboard_dash.py

    Or with custom port:
    python fleet_health_dashboard_dash.py --port 8099

FEATURES:
- Modern responsive UI with Bootstrap theming
- Fleet Overview with health scores and KPIs
- Interactive agent inventory with filtering/sorting  
- Real-time alerts with drill-down
- Compliance posture tracking
- Cost analysis visualizations
- Continuous Evaluation summary (Feb 2026)
- Grafana dashboard links
- Agent lifecycle actions (start/stop/block)

Updated: February 2026 - aligned with Foundry Control Plane GA-track features
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import argparse

# Dash imports
from dash import Dash, html, dcc, callback, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Load environment variables
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

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

# Theme colors
COLORS = {
    "primary": "#0d6efd",
    "success": "#198754",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#0dcaf0",
    "secondary": "#6c757d",
    "dark": "#212529",
    "light": "#f8f9fa",
    "bg_card": "#ffffff",
    "bg_dark": "#1a1a2e",
    "text_muted": "#6c757d",
}

STATUS_COLORS = {
    HealthStatus.HEALTHY: COLORS["success"],
    HealthStatus.WARNING: COLORS["warning"],
    HealthStatus.CRITICAL: COLORS["danger"],
    HealthStatus.UNKNOWN: COLORS["secondary"],
}

STATUS_ICONS = {
    HealthStatus.HEALTHY: "✅",
    HealthStatus.WARNING: "⚠️",
    HealthStatus.CRITICAL: "🔴",
    HealthStatus.UNKNOWN: "❓",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def run_async(coro, timeout: float = 90.0):
    """Run async coroutine in sync context with timeout."""
    import concurrent.futures
    import threading
    
    result = [None]
    exception = [None]
    
    def run_in_thread():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result[0] = loop.run_until_complete(coro)
            finally:
                loop.close()
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        print(f"⏱️ Async operation timed out after {timeout}s")
        return None
    
    if exception[0]:
        print(f"❌ Async operation error: {exception[0]}")
        return None
    
    return result[0]


def fetch_telemetry_from_app_insights() -> Dict[str, Dict[str, Any]]:
    """Fetch agent telemetry from Application Insights using Kusto query."""
    telemetry = {}
    try:
        from azure.monitor.query import LogsQueryClient
        from azure.identity import DefaultAzureCredential
        from datetime import timedelta
        
        workspace_id = os.environ.get("LOG_ANALYTICS_WORKSPACE_ID")
        if not workspace_id:
            print("⚠️ LOG_ANALYTICS_WORKSPACE_ID not set, skipping telemetry")
            return telemetry
        
        credential = DefaultAzureCredential()
        logs_client = LogsQueryClient(credential)
        
        # Kusto query to aggregate metrics by agent
        query = '''
        AppDependencies
        | where TimeGenerated >= ago(24h)
        | where DependencyType == "GenAI | azure_ai_agents"
        | extend props = parse_json(Properties)
        | extend agent_name = tostring(props["gen_ai.agent.name"])
        | extend model = tostring(props["gen_ai.request.model"])
        | extend tokens = toint(props["gen_ai.usage.total_tokens"])
        | summarize 
            total_runs = count(),
            successful_runs = countif(Success == true),
            failed_runs = countif(Success == false),
            avg_latency = avg(DurationMs),
            p95_latency = percentile(DurationMs, 95),
            total_tokens = sum(tokens)
            by agent_name, model
        '''
        
        response = logs_client.query_workspace(
            workspace_id=workspace_id,
            query=query,
            timespan=timedelta(hours=24)
        )
        
        if response.tables:
            for row in response.tables[0].rows:
                agent_name = row[0] or 'Unknown'
                telemetry[agent_name] = {
                    'model': row[1] or 'unknown',
                    'total_runs': int(row[2] or 0),
                    'successful_runs': int(row[3] or 0),
                    'failed_runs': int(row[4] or 0),
                    'avg_latency_ms': float(row[5] or 0),
                    'p95_latency_ms': float(row[6] or 0),
                    'total_tokens': int(row[7] or 0),
                }
            print(f"📊 Fetched telemetry for {len(telemetry)} agents from App Insights")
    except Exception as e:
        print(f"⚠️ Error fetching telemetry: {e}")
    
    return telemetry


def fetch_fleet_data_sync() -> Optional[FleetHealthSummary]:
    """Fetch fleet health data synchronously."""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.ai.projects import AIProjectClient
        
        endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
        if not endpoint:
            print("No endpoint configured")
            return None
        
        credential = DefaultAzureCredential()
        client = AIProjectClient(endpoint=endpoint, credential=credential)
        
        # Get all agents from the project (no hardcoded filter - show everything from Foundry)
        all_agents = list(client.agents.list())
        # Filter out agents with no name or placeholder names
        agents_list = [a for a in all_agents if getattr(a, 'name', '') and getattr(a, 'name', '') not in ('ONE', 'NONE', '')]
        print(f"📡 Found {len(all_agents)} agents from Azure, showing {len(agents_list)} valid agents")
        
        if not agents_list:
            return None
        
        # Fetch telemetry from Application Insights
        telemetry = fetch_telemetry_from_app_insights()
        
        # Build agent metrics
        agent_metrics = []
        total_runs_24h = 0
        total_errors_24h = 0
        total_tokens_24h = 0
        
        for agent in agents_list:
            name = getattr(agent, 'name', 'Unknown')
            agent_id = getattr(agent, 'id', name)
            
            # Extract model and version from versions.latest.definition (V2 agents)
            model = "unknown"
            version = "1"
            instructions = ""
            tools = []
            
            versions = getattr(agent, 'versions', None)
            if versions and isinstance(versions, dict) and 'latest' in versions:
                latest = versions['latest']
                definition = latest.get('definition', {}) if isinstance(latest, dict) else {}
                model = definition.get('model', 'unknown')
                instructions = definition.get('instructions', '') or ''
                tools_data = definition.get('tools', []) or []
                version = str(latest.get('version', '1'))
                
                # Extract tool types
                for t in tools_data:
                    if isinstance(t, dict):
                        tools.append(t.get('type', str(t)))
                    elif hasattr(t, 'type'):
                        tools.append(t.type)
                    else:
                        tools.append(str(t))
            
            # Get telemetry data for this agent
            agent_telemetry = telemetry.get(name, {})
            runs = agent_telemetry.get('total_runs', 0)
            successful = agent_telemetry.get('successful_runs', 0)
            failed = agent_telemetry.get('failed_runs', 0)
            avg_latency = agent_telemetry.get('avg_latency_ms', 0.0)
            p95_latency = agent_telemetry.get('p95_latency_ms', 0.0)
            tokens = agent_telemetry.get('total_tokens', 0)
            
            # Use model from agent definition (matches Foundry portal)
            
            # Calculate error rate
            error_rate = (failed / runs * 100) if runs > 0 else 0.0
            
            # Estimate cost (rough: $0.01 per 1K tokens for gpt-4)
            cost_per_1k = 0.01 if 'gpt-4' in model else 0.002
            estimated_cost = (tokens / 1000) * cost_per_1k
            
            # Calculate health based on error rate and whether agent has instructions
            has_instructions = bool(instructions and len(instructions) > 10)
            if error_rate > 10:
                health_score = 60.0
                status = HealthStatus.CRITICAL
            elif error_rate > 5 or not has_instructions:
                health_score = 80.0
                status = HealthStatus.WARNING
            else:
                health_score = 100.0
                status = HealthStatus.HEALTHY
            
            # Accumulate totals
            total_runs_24h += runs
            total_errors_24h += failed
            total_tokens_24h += tokens
            
            agent_metrics.append(AgentHealthMetrics(
                agent_id=agent_id,
                agent_name=name,
                agent_version=version,
                model=model,
                status=status,
                health_score=health_score,
                tools=tools,
                total_runs=runs,
                successful_runs=successful,
                failed_runs=failed,
                error_rate=error_rate,
                avg_latency_ms=avg_latency,
                p95_latency_ms=p95_latency,
                total_tokens=tokens,
                prompt_tokens=0,
                completion_tokens=0,
                estimated_cost_usd=estimated_cost,
                compliance_status="compliant" if has_instructions else "non-compliant",
                policy_violations=0 if has_instructions else 1,
            ))
            print(f"   ✅ {name} ({model}) - {runs} runs, {tokens} tokens")
        
        # Build summary
        healthy = sum(1 for a in agent_metrics if a.status == HealthStatus.HEALTHY)
        warning = sum(1 for a in agent_metrics if a.status == HealthStatus.WARNING)
        critical = sum(1 for a in agent_metrics if a.status == HealthStatus.CRITICAL)
        compliant = sum(1 for a in agent_metrics if a.compliance_status == "compliant")
        
        avg_health = sum(a.health_score for a in agent_metrics) / len(agent_metrics) if agent_metrics else 0
        avg_success = (total_runs_24h - total_errors_24h) / total_runs_24h if total_runs_24h > 0 else 1.0
        total_cost = sum(a.estimated_cost_usd for a in agent_metrics)
        
        summary = FleetHealthSummary(
            total_agents=len(agent_metrics),
            active_agents=sum(1 for a in agent_metrics if a.total_runs > 0),
            healthy_agents=healthy,
            warning_agents=warning,
            critical_agents=critical,
            fleet_health_score=avg_health,
            avg_success_rate=avg_success,
            total_runs_24h=total_runs_24h,
            total_errors_24h=total_errors_24h,
            total_cost_24h=total_cost,
            total_cost_7d=total_cost * 7,  # Estimate
            total_tokens_24h=total_tokens_24h,
            cost_trend_pct=0.0,
            compliant_agents=compliant,
            non_compliant_agents=len(agent_metrics) - compliant,
            total_policy_violations=len(agent_metrics) - compliant,
            critical_alerts=critical,
            high_alerts=0,
            medium_alerts=warning,
            low_alerts=0,
            agents=agent_metrics,
        )
        
        return summary
        
    except Exception as e:
        import traceback
        print(f"❌ Error fetching fleet data: {e}")
        traceback.print_exc()
        return None


async def fetch_fleet_data() -> Optional[FleetHealthSummary]:
    """Fetch fleet health data asynchronously."""
    try:
        client = FleetHealthClient()
        return await client.get_fleet_health_summary()
    except Exception as e:
        print(f"Error fetching fleet data: {e}")
        return None


def create_demo_data() -> FleetHealthSummary:
    """Create demo data for testing without Azure connection (Feb 2026 scenario)."""
    demo_agents = [
        AgentHealthMetrics(
            agent_id="demo-agent-1",
            agent_name="Market_Researcher",
            agent_version="2",
            model="gpt-4.1-mini",
            status=HealthStatus.HEALTHY,
            health_score=92.0,
            tools=["web_search", "file_search"],
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
            model="gpt-4.1",
            status=HealthStatus.HEALTHY,
            health_score=88.0,
            tools=["code_interpreter"],
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
            model="gpt-4.1",
            status=HealthStatus.WARNING,
            health_score=72.0,
            tools=["file_search"],
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
            model="gpt-4.1-mini",
            status=HealthStatus.HEALTHY,
            health_score=95.0,
            tools=["code_interpreter", "file_search"],
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
            model="gpt-4.1",
            status=HealthStatus.CRITICAL,
            health_score=45.0,
            tools=["code_interpreter", "web_search"],
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
        AgentHealthMetrics(
            agent_id="demo-agent-6",
            agent_name="Customer_Support_Bot",
            agent_version="4",
            model="gpt-4.1-mini",
            status=HealthStatus.HEALTHY,
            health_score=91.0,
            tools=["file_search"],
            total_runs=512,
            successful_runs=498,
            failed_runs=14,
            error_rate=0.027,
            avg_latency_ms=850,
            p95_latency_ms=1200,
            total_tokens=125000,
            prompt_tokens=80000,
            completion_tokens=45000,
            estimated_cost_usd=0.125,
            compliance_status="compliant",
            policy_violations=0
        ),
        AgentHealthMetrics(
            agent_id="demo-agent-7",
            agent_name="SRE_Monitoring_Agent",
            agent_version="1",
            model="gpt-4.1",
            status=HealthStatus.HEALTHY,
            health_score=94.0,
            tools=["code_interpreter", "web_search"],
            total_runs=320,
            successful_runs=315,
            failed_runs=5,
            error_rate=0.016,
            avg_latency_ms=1100,
            p95_latency_ms=1800,
            total_tokens=89000,
            prompt_tokens=58000,
            completion_tokens=31000,
            estimated_cost_usd=0.89,
            compliance_status="compliant",
            policy_violations=0
        ),
        AgentHealthMetrics(
            agent_id="demo-agent-8",
            agent_name="Custom_RAG_Agent",
            agent_version="2",
            model="gpt-4o",
            status=HealthStatus.HEALTHY,
            health_score=87.0,
            tools=["file_search", "web_search"],
            total_runs=178,
            successful_runs=170,
            failed_runs=8,
            error_rate=0.045,
            avg_latency_ms=1450,
            p95_latency_ms=2400,
            total_tokens=96000,
            prompt_tokens=62000,
            completion_tokens=34000,
            estimated_cost_usd=0.96,
            compliance_status="compliant",
            policy_violations=0
        ),
    ]
    
    # Create sample alerts
    alerts = [
        {"timestamp": datetime.now() - timedelta(hours=1), "message": "High latency detected", 
         "severity": "high", "agent_name": "Technical_Architect", "source": "application_insights"},
        {"timestamp": datetime.now() - timedelta(hours=2), "message": "Rate limit reached", 
         "severity": "critical", "agent_name": "Customer_Support_Bot", "source": "application_insights"},
        {"timestamp": datetime.now() - timedelta(hours=3), "message": "Token quota warning", 
         "severity": "medium", "agent_name": "Marketing_Strategist", "source": "application_insights"},
    ]
    
    # Create sample compliance data
    violations = [
        {"agent_name": "Technical_Architect", "rule": "missing_instructions", 
         "severity": "critical", "message": "Missing system prompt", 
         "recommendation": "Add clear instructions to define agent behavior"},
        {"agent_name": "Legal_Compliance_Advisor", "rule": "deprecated_model", 
         "severity": "high", "message": "Using deprecated model configuration", 
         "recommendation": "Review and update model settings"},
    ]
    
    warnings = [
        {"agent_name": "Market_Researcher", "rule": "high_risk_tools_no_safety", 
         "severity": "medium", "message": "Web search tool without safety instructions", 
         "recommendation": "Add content safety guidelines"},
    ]
    
    return FleetHealthSummary(
        total_agents=8,
        active_agents=8,
        healthy_agents=6,
        warning_agents=1,
        critical_agents=1,
        fleet_health_score=83.0,
        avg_success_rate=0.940,
        total_runs_24h=1601,
        total_errors_24h=53,
        total_cost_24h=4.21,
        total_cost_7d=29.47,
        total_tokens_24h=582000,
        cost_trend_pct=-3.8,
        compliant_agents=6,
        non_compliant_agents=2,
        total_policy_violations=3,
        critical_alerts=1,
        high_alerts=1,
        medium_alerts=1,
        low_alerts=2,
        generated_at=datetime.now(),
        agents=demo_agents,
        alerts=alerts,
        compliance_violations=violations,
        compliance_warnings=warnings
    )


# Global variable to track data source
_DATA_SOURCE = "unknown"

def get_data_source() -> str:
    """Get the current data source."""
    return _DATA_SOURCE

def get_data(use_demo: bool = False) -> FleetHealthSummary:
    """Get fleet data - either from Azure or demo data.
    
    Args:
        use_demo: If True, skip Azure and use demo data directly
    """
    global _DATA_SOURCE
    
    if use_demo:
        print("Demo mode requested, using demo data")
        _DATA_SOURCE = "demo"
        return create_demo_data()
    
    # Check if Azure is configured and try to fetch
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if endpoint:
        print(f"="*60)
        print(f"📡 Fetching data from Azure AI Foundry...")
        print(f"   Endpoint: {endpoint[:60]}..." if len(endpoint) > 60 else f"   Endpoint: {endpoint}")
        
        try:
            # Use synchronous fetch which is more reliable in Dash
            data = fetch_fleet_data_sync()
            if data and data.total_agents > 0:
                print(f"✅ Successfully loaded {data.total_agents} agents from Azure")
                _DATA_SOURCE = "azure"
                print(f"="*60)
                return data
            else:
                print("⚠️ No agents found in Azure project")
                _DATA_SOURCE = "demo (no agents)"
        except Exception as e:
            import traceback
            print(f"❌ Azure fetch failed: {e}")
            traceback.print_exc()
            _DATA_SOURCE = f"demo (error)"
    else:
        print("⚠️ No AZURE_AI_PROJECT_ENDPOINT set")
        _DATA_SOURCE = "demo (no endpoint)"
    
    print(f"Using demo data")
    print(f"="*60)
    return create_demo_data()


# =============================================================================
# COMPONENT BUILDERS
# =============================================================================

def create_kpi_card(title: str, value: str, subtitle: str = "", 
                    icon: str = "📊", color: str = COLORS["primary"],
                    delta: str = None, delta_positive: bool = True) -> dbc.Card:
    """Create a styled KPI card."""
    delta_element = None
    if delta:
        delta_color = COLORS["success"] if delta_positive else COLORS["danger"]
        delta_element = html.Span(delta, className="ms-2", 
                                  style={"color": delta_color, "fontSize": "0.8em"})
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, className="me-2", style={"fontSize": "1.5em"}),
                html.Span(title, className="text-muted", style={"fontSize": "0.9em"})
            ]),
            html.Div([
                html.Span(value, style={
                    "fontSize": "2.2em", 
                    "fontWeight": "bold",
                    "color": color
                }),
                delta_element
            ], className="my-2"),
            html.Small(subtitle, className="text-muted")
        ])
    ], className="h-100 shadow-sm", style={
        "borderLeft": f"4px solid {color}",
        "borderRadius": "8px"
    })


def create_health_gauge(score: float) -> go.Figure:
    """Create a gauge chart for health score."""
    # Determine color based on score
    if score >= 80:
        color = COLORS["success"]
    elif score >= 50:
        color = COLORS["warning"]
    else:
        color = COLORS["danger"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        number={"suffix": "%", "font": {"size": 40}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": "white",
            "steps": [
                {"range": [0, 50], "color": "#ffebee"},
                {"range": [50, 80], "color": "#fff8e1"},
                {"range": [80, 100], "color": "#e8f5e9"}
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": score
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS["dark"]}
    )
    
    return fig


def create_health_distribution_chart(summary: FleetHealthSummary) -> go.Figure:
    """Create a donut chart for health distribution."""
    labels = ["Healthy", "Warning", "Critical"]
    values = [summary.healthy_agents, summary.warning_agents, summary.critical_agents]
    colors = [COLORS["success"], COLORS["warning"], COLORS["danger"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker_colors=colors,
        textinfo="value+percent",
        textposition="outside",
        pull=[0.02, 0.02, 0.05]  # Slightly pull out critical slice
    )])
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=30, b=50),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{summary.fleet_health_score:.0f}%</b><br>Health",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )]
    )
    
    return fig


def create_cost_by_agent_chart(agents: List[AgentHealthMetrics]) -> go.Figure:
    """Create a bar chart for cost by agent."""
    # Sort by cost and take top 10
    sorted_agents = sorted(agents, key=lambda a: -a.estimated_cost_usd)[:10]
    
    fig = go.Figure(data=[
        go.Bar(
            x=[a.agent_name for a in sorted_agents],
            y=[a.estimated_cost_usd for a in sorted_agents],
            marker_color=COLORS["primary"],
            text=[f"${a.estimated_cost_usd:.3f}" for a in sorted_agents],
            textposition="outside"
        )
    ])
    
    fig.update_layout(
        title="Cost by Agent (Top 10)",
        xaxis_title="Agent",
        yaxis_title="Estimated Cost ($)",
        height=350,
        margin=dict(l=40, r=20, t=50, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-45
    )
    
    return fig


def create_runs_by_agent_chart(agents: List[AgentHealthMetrics]) -> go.Figure:
    """Create a bar chart for runs by agent."""
    sorted_agents = sorted(agents, key=lambda a: -a.total_runs)[:10]
    
    fig = go.Figure(data=[
        go.Bar(
            name="Successful",
            x=[a.agent_name for a in sorted_agents],
            y=[a.successful_runs for a in sorted_agents],
            marker_color=COLORS["success"]
        ),
        go.Bar(
            name="Failed",
            x=[a.agent_name for a in sorted_agents],
            y=[a.failed_runs for a in sorted_agents],
            marker_color=COLORS["danger"]
        )
    ])
    
    fig.update_layout(
        title="Runs by Agent (24h)",
        xaxis_title="Agent",
        yaxis_title="Number of Runs",
        barmode="stack",
        height=350,
        margin=dict(l=40, r=20, t=50, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_alerts_severity_chart(summary: FleetHealthSummary) -> go.Figure:
    """Create a pie chart for alerts by severity."""
    labels = ["Critical", "High", "Medium", "Low"]
    values = [summary.critical_alerts, summary.high_alerts, 
              summary.medium_alerts, summary.low_alerts]
    colors = [COLORS["danger"], "#fd7e14", COLORS["warning"], COLORS["info"]]
    
    # Filter out zero values
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if not filtered:
        filtered = [("No Alerts", 1, COLORS["success"])]
    
    fig = go.Figure(data=[go.Pie(
        labels=[f[0] for f in filtered],
        values=[f[1] for f in filtered],
        hole=0.5,
        marker_colors=[f[2] for f in filtered]
    )])
    
    fig.update_layout(
        title="Alerts by Severity",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig


def create_agent_table(agents: List[AgentHealthMetrics]) -> dbc.Table:
    """Create a styled agent inventory table."""
    header = html.Thead(html.Tr([
        html.Th("Status", style={"width": "60px"}),
        html.Th("Agent Name"),
        html.Th("Model"),
        html.Th("Version"),
        html.Th("Health"),
        html.Th("Runs (24h)"),
        html.Th("Error Rate"),
        html.Th("Avg Latency"),
        html.Th("Tokens"),
        html.Th("Cost"),
    ]))
    
    rows = []
    for agent in agents:
        status_color = STATUS_COLORS.get(agent.status, COLORS["secondary"])
        status_icon = STATUS_ICONS.get(agent.status, "❓")
        
        error_color = COLORS["danger"] if agent.error_rate > 0.1 else \
                     COLORS["warning"] if agent.error_rate > 0.05 else COLORS["success"]
        
        rows.append(html.Tr([
            html.Td(status_icon),
            html.Td(html.Strong(agent.agent_name)),
            html.Td(html.Code(agent.model, style={"fontSize": "0.85em"})),
            html.Td(f"v{agent.agent_version}"),
            html.Td(
                html.Span(f"{agent.health_score:.0f}%", 
                         style={"color": status_color, "fontWeight": "bold"})
            ),
            html.Td(f"{agent.total_runs:,}"),
            html.Td(
                html.Span(f"{agent.error_rate*100:.1f}%", style={"color": error_color})
            ),
            html.Td(f"{agent.avg_latency_ms:.0f}ms"),
            html.Td(f"{agent.total_tokens:,}"),
            html.Td(f"${agent.estimated_cost_usd:.4f}"),
        ]))
    
    return dbc.Table([header, html.Tbody(rows)], 
                     striped=True, bordered=True, hover=True, responsive=True,
                     className="align-middle")


def create_alerts_table(alerts: List[Dict]) -> html.Div:
    """Create a styled alerts table."""
    if not alerts:
        return dbc.Alert("🎉 No active alerts in the last 24 hours!", color="success")
    
    severity_badges = {
        "critical": dbc.Badge("Critical", color="danger", className="me-1"),
        "high": dbc.Badge("High", color="warning", text_color="dark", className="me-1"),
        "medium": dbc.Badge("Medium", color="info", className="me-1"),
        "low": dbc.Badge("Low", color="secondary", className="me-1"),
    }
    
    rows = []
    for alert in alerts[:20]:  # Limit to 20
        severity = alert.get("severity", "low")
        timestamp = alert.get("timestamp", "")
        if hasattr(timestamp, 'strftime'):
            time_str = timestamp.strftime("%H:%M:%S %m/%d")
        else:
            time_str = str(timestamp)[:19]
        
        rows.append(html.Tr([
            html.Td(severity_badges.get(severity, severity_badges["low"])),
            html.Td(time_str),
            html.Td(alert.get("message", "No message")[:80]),
            html.Td(alert.get("agent_name", "System")),
            html.Td(alert.get("source", "unknown").replace("_", " ").title()),
        ]))
    
    header = html.Thead(html.Tr([
        html.Th("Severity"),
        html.Th("Time"),
        html.Th("Message"),
        html.Th("Agent"),
        html.Th("Source"),
    ]))
    
    return dbc.Table([header, html.Tbody(rows)], 
                     striped=True, bordered=True, hover=True, responsive=True)


def create_compliance_section(summary: FleetHealthSummary) -> html.Div:
    """Create the compliance section with violations and warnings."""
    violations = getattr(summary, 'compliance_violations', [])
    warnings = getattr(summary, 'compliance_warnings', [])
    
    compliance_pct = (summary.compliant_agents / max(summary.total_agents, 1)) * 100
    
    # Status card
    status_color = COLORS["success"] if compliance_pct >= 80 else \
                  COLORS["warning"] if compliance_pct >= 50 else COLORS["danger"]
    
    status_card = dbc.Card([
        dbc.CardBody([
            html.H1(f"{compliance_pct:.0f}%", 
                   style={"color": status_color, "textAlign": "center", "fontSize": "3em"}),
            html.P("Compliance Score", className="text-center text-muted"),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.H4(summary.compliant_agents, className="text-center"),
                    html.Small("Compliant", className="text-success d-block text-center")
                ]),
                dbc.Col([
                    html.H4(summary.non_compliant_agents, className="text-center"),
                    html.Small("Non-Compliant", className="text-danger d-block text-center")
                ]),
            ])
        ])
    ], className="shadow-sm")
    
    # Violations list
    violations_list = []
    if violations:
        for v in violations:
            violations_list.append(
                dbc.Alert([
                    html.Strong(f"❌ {v.get('agent_name', 'Unknown')}"),
                    html.Span(f" - {v.get('message', 'Violation')}", className="ms-2"),
                    html.Br(),
                    html.Small(f"💡 {v.get('recommendation', 'Review this issue')}", 
                              className="text-muted")
                ], color="danger", className="mb-2")
            )
    else:
        violations_list.append(
            dbc.Alert("✅ No policy violations! All agents meet required compliance standards.", 
                     color="success")
        )
    
    # Warnings list
    warnings_list = []
    if warnings:
        for w in warnings:
            warnings_list.append(
                dbc.Alert([
                    html.Strong(f"⚠️ {w.get('agent_name', 'Unknown')}"),
                    html.Span(f" - {w.get('message', 'Warning')}", className="ms-2"),
                    html.Br(),
                    html.Small(f"💡 {w.get('recommendation', 'Review this configuration')}", 
                              className="text-muted")
                ], color="warning", className="mb-2")
            )
    else:
        warnings_list.append(
            dbc.Alert("No additional warnings. All recommended practices are followed.", 
                     color="info")
        )
    
    return html.Div([
        dbc.Row([
            dbc.Col(status_card, md=4),
            dbc.Col([
                html.H5("🔴 Policy Violations", className="mb-3"),
                html.Div(violations_list),
                html.H5("🟡 Compliance Warnings", className="mt-4 mb-3"),
                html.Div(warnings_list)
            ], md=8)
        ])
    ])


# =============================================================================
# LAYOUT
# =============================================================================

def create_layout() -> html.Div:
    """Create the main application layout."""
    return html.Div([
        # Store for data
        dcc.Store(id="fleet-data-store"),
        
        # Auto-refresh interval (every 60 seconds)
        dcc.Interval(id="refresh-interval", interval=60*1000, n_intervals=0, disabled=True),
        
        # Navbar
        dbc.Navbar(
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.Span("🎛️", style={"fontSize": "1.5em"}),
                        dbc.NavbarBrand("Microsoft Foundry Control Plane", className="ms-2 fw-bold")
                    ], width="auto"),
                ], align="center", className="g-0"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button([
                            html.I(className="bi bi-arrow-clockwise me-1"),
                            "Refresh"
                        ], id="refresh-btn", color="light", size="sm", className="me-2"),
                        dbc.Switch(
                            id="auto-refresh-switch",
                            label="Auto-refresh",
                            value=False,
                            className="d-inline-block text-white"
                        ),
                    ], width="auto")
                ], align="center")
            ], fluid=True),
            color="dark",
            dark=True,
            className="mb-4 shadow"
        ),
        
        # Main content
        dbc.Container([
            # Last refresh indicator
            html.Div([
                html.Small(id="last-refresh-time", className="text-muted")
            ], className="text-end mb-2"),
            
            # Navigation tabs
            dbc.Tabs([
                dbc.Tab(label="📊 Overview", tab_id="tab-overview"),
                dbc.Tab(label="🤖 Agents", tab_id="tab-agents"),
                dbc.Tab(label="🚨 Alerts", tab_id="tab-alerts"),
                dbc.Tab(label="🛡️ Compliance", tab_id="tab-compliance"),
                dbc.Tab(label="💰 Cost Analysis", tab_id="tab-cost"),
                dbc.Tab(label="🔍 Evaluation", tab_id="tab-evaluation"),
            ], id="main-tabs", active_tab="tab-overview", className="mb-4"),
            
            # Tab content
            html.Div(id="tab-content"),
            
            # Footer
            html.Footer([
                html.Hr(),
                html.Div([
                    html.A("📊 Azure Portal", href="https://portal.azure.com", 
                          target="_blank", className="me-4"),
                    html.A("🤖 Foundry Portal (Operate)", href="https://ai.azure.com", 
                          target="_blank", className="me-4"),
                    html.A("📈 Application Insights", 
                          href="https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents",
                          target="_blank", className="me-4"),
                    html.A("📊 Grafana Agent Dashboard", 
                          href="https://aka.ms/amg/dash/af-agent",
                          target="_blank", className="me-4"),
                    html.A("📊 Grafana Workflow Dashboard", 
                          href="https://aka.ms/amg/dash/af-workflow",
                          target="_blank"),
                ], className="text-center text-muted"),
                html.Div([
                    html.Small("Microsoft Foundry Control Plane • February 2026", 
                              className="text-muted")
                ], className="text-center mt-2")
            ], className="mt-5 mb-3")
            
        ], fluid=True)
    ])


def create_overview_content(summary: FleetHealthSummary) -> html.Div:
    """Create the overview tab content."""
    total_alerts = summary.critical_alerts + summary.high_alerts + \
                  summary.medium_alerts + summary.low_alerts
    
    return html.Div([
        # KPI Row
        dbc.Row([
            dbc.Col(create_kpi_card(
                "Fleet Health Score",
                f"{summary.fleet_health_score:.1f}%",
                f"{summary.active_agents} active agents",
                "🎯",
                COLORS["primary"]
            ), md=2, className="mb-4"),
            
            dbc.Col(create_kpi_card(
                "Total Agents",
                str(summary.total_agents),
                f"✅{summary.healthy_agents} ⚠️{summary.warning_agents} 🔴{summary.critical_agents}",
                "🤖",
                COLORS["success"]
            ), md=2, className="mb-4"),
            
            dbc.Col(create_kpi_card(
                "Success Rate",
                f"{summary.avg_success_rate * 100:.1f}%",
                f"{summary.total_runs_24h:,} runs (24h)",
                "📈",
                COLORS["info"]
            ), md=2, className="mb-4"),
            
            dbc.Col(create_kpi_card(
                "Cost (7d)",
                f"${summary.total_cost_7d:.2f}",
                f"${summary.total_cost_24h:.2f}/day avg",
                "💵",
                COLORS["warning"],
                delta=f"{summary.cost_trend_pct:+.1f}%" if summary.cost_trend_pct else None,
                delta_positive=summary.cost_trend_pct < 0 if summary.cost_trend_pct else True
            ), md=2, className="mb-4"),
            
            dbc.Col(create_kpi_card(
                "Active Alerts",
                str(total_alerts),
                f"🔴{summary.critical_alerts} 🟠{summary.high_alerts} 🟡{summary.medium_alerts}",
                "🚨",
                COLORS["danger"] if summary.critical_alerts > 0 else 
                COLORS["warning"] if summary.high_alerts > 0 else COLORS["success"]
            ), md=2, className="mb-4"),
            
            dbc.Col(create_kpi_card(
                "Compliance",
                f"{summary.compliant_agents}/{summary.total_agents}",
                f"{summary.total_policy_violations} violations",
                "🛡️",
                COLORS["success"] if summary.non_compliant_agents == 0 else COLORS["warning"]
            ), md=2, className="mb-4"),
        ]),
        
        # Charts Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🏥 Health Distribution"),
                    dbc.CardBody(dcc.Graph(
                        figure=create_health_distribution_chart(summary),
                        config={"displayModeBar": False}
                    ))
                ], className="shadow-sm h-100")
            ], md=4, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Runs by Agent (24h)"),
                    dbc.CardBody(dcc.Graph(
                        figure=create_runs_by_agent_chart(summary.agents),
                        config={"displayModeBar": False}
                    ))
                ], className="shadow-sm h-100")
            ], md=4, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🚨 Alerts by Severity"),
                    dbc.CardBody(dcc.Graph(
                        figure=create_alerts_severity_chart(summary),
                        config={"displayModeBar": False}
                    ))
                ], className="shadow-sm h-100")
            ], md=4, className="mb-4"),
        ]),
        
        # Quick Status Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("⚡ Quick Actions"),
                    dbc.CardBody([
                        dbc.Button([
                            html.I(className="bi bi-graph-up me-2"),
                            "View Traces in Portal"
                        ], color="primary", outline=True, className="me-2 mb-2",
                        href="https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents",
                        target="_blank"),
                        dbc.Button([
                            html.I(className="bi bi-robot me-2"),
                            "Foundry Operate Tab"
                        ], color="dark", outline=True, className="me-2 mb-2",
                        href="https://ai.azure.com",
                        target="_blank"),
                        dbc.Button([
                            html.I(className="bi bi-bar-chart me-2"),
                            "Grafana Agent Dashboard"
                        ], color="info", outline=True, className="me-2 mb-2",
                        href="https://aka.ms/amg/dash/af-agent",
                        target="_blank"),
                        dbc.Button([
                            html.I(className="bi bi-shield-check me-2"),
                            "Security Overview"
                        ], color="success", outline=True, className="me-2 mb-2",
                        href="https://portal.azure.com/#blade/Microsoft_Azure_Security/SecurityMenuBlade/overview",
                        target="_blank"),
                    ])
                ], className="shadow-sm h-100")
            ], md=6, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📋 Health Score Factors"),
                    dbc.CardBody([
                        html.Ul([
                            html.Li([html.Strong("Error Rate < 5%"), " - Low failure rate"]),
                            html.Li([html.Strong("Latency < 2s"), " - Fast response times"]),
                            html.Li([html.Strong("No violations"), " - Compliance maintained"]),
                            html.Li([html.Strong("Active in 24h"), " - Recent activity"]),
                            html.Li([html.Strong("Has instructions"), " - System prompt defined"]),
                        ], className="mb-0"),
                        html.Hr(),
                        html.Small([
                            html.Strong("New in Feb 2026: "), 
                            "Continuous Evaluation, AI Red Teaming Agent, Grafana dashboards, ",
                            "Agent lifecycle (start/stop/block), Custom agent registration"
                        ], className="text-muted")
                    ])
                ], className="shadow-sm h-100")
            ], md=6, className="mb-4"),
        ])
    ])


def create_agents_content(summary: FleetHealthSummary) -> html.Div:
    """Create the agents tab content."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H4("📋 Agent Inventory", className="mb-3"),
                html.P(f"Showing {len(summary.agents)} agents", className="text-muted")
            ])
        ]),
        
        # Filters
        dbc.Row([
            dbc.Col([
                dbc.Label("Filter by Status"),
                dbc.Checklist(
                    options=[
                        {"label": " ✅ Healthy", "value": "healthy"},
                        {"label": " ⚠️ Warning", "value": "warning"},
                        {"label": " 🔴 Critical", "value": "critical"},
                    ],
                    value=["healthy", "warning", "critical"],
                    id="status-filter",
                    inline=True
                )
            ], md=6),
            dbc.Col([
                dbc.Label("Search"),
                dbc.Input(id="agent-search", placeholder="Search agents...", type="text")
            ], md=4),
            dbc.Col([
                dbc.Label("Sort by"),
                dbc.Select(
                    id="agent-sort",
                    options=[
                        {"label": "Health Score", "value": "health"},
                        {"label": "Name", "value": "name"},
                        {"label": "Runs", "value": "runs"},
                        {"label": "Error Rate", "value": "error"},
                        {"label": "Cost", "value": "cost"},
                    ],
                    value="health"
                )
            ], md=2),
        ], className="mb-4"),
        
        # Table
        dbc.Card([
            dbc.CardBody([
                html.Div(id="agents-table-container")
            ])
        ], className="shadow-sm")
    ])


def create_alerts_content(summary: FleetHealthSummary) -> html.Div:
    """Create the alerts tab content."""
    total_alerts = summary.critical_alerts + summary.high_alerts + \
                  summary.medium_alerts + summary.low_alerts
    
    alerts = getattr(summary, 'alerts', [])
    
    return html.Div([
        # Summary cards
        dbc.Row([
            dbc.Col(create_kpi_card("Critical", str(summary.critical_alerts), 
                                   "Immediate action required", "🔴", COLORS["danger"]), md=3),
            dbc.Col(create_kpi_card("High", str(summary.high_alerts), 
                                   "Review within 4h", "🟠", "#fd7e14"), md=3),
            dbc.Col(create_kpi_card("Medium", str(summary.medium_alerts), 
                                   "Monitor closely", "🟡", COLORS["warning"]), md=3),
            dbc.Col(create_kpi_card("Low", str(summary.low_alerts), 
                                   "Informational", "🔵", COLORS["info"]), md=3),
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Alert Distribution"),
                    dbc.CardBody(dcc.Graph(
                        figure=create_alerts_severity_chart(summary),
                        config={"displayModeBar": False}
                    ))
                ], className="shadow-sm")
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(f"📋 Recent Alerts ({len(alerts)})"),
                    dbc.CardBody(create_alerts_table(alerts))
                ], className="shadow-sm")
            ], md=8),
        ])
    ])


def create_compliance_content(summary: FleetHealthSummary) -> html.Div:
    """Create the compliance tab content."""
    return html.Div([
        html.H4("🛡️ Compliance Posture", className="mb-4"),
        create_compliance_section(summary),
        
        html.Hr(className="my-4"),
        
        # Model Governance Reference
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("✅ Approved Models"),
                    dbc.CardBody([
                        html.Code("gpt-4o, gpt-4o-mini", className="d-block mb-1"),
                        html.Code("gpt-4.1, gpt-4.1-mini, gpt-4.1-nano", className="d-block mb-1"),
                        html.Code("gpt-5-chat, gpt-5.1-chat", className="d-block mb-1"),
                        html.Code("o1, o1-mini, o1-preview, o3-mini", className="d-block"),
                    ])
                ], className="shadow-sm h-100")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("❌ Deprecated Models"),
                    dbc.CardBody([
                        html.Code("gpt-3.5-turbo, gpt-3.5-turbo-16k", className="d-block mb-1 text-danger"),
                        html.Code("gpt-4-32k, gpt-4-vision-preview", className="d-block mb-1 text-danger"),
                        html.Code("text-davinci-003, text-davinci-002", className="d-block text-danger"),
                    ])
                ], className="shadow-sm h-100")
            ], md=6),
        ])
    ])


def create_cost_content(summary: FleetHealthSummary) -> html.Div:
    """Create the cost analysis tab content."""
    return html.Div([
        # KPIs
        dbc.Row([
            dbc.Col(create_kpi_card("Total Cost (7d)", f"${summary.total_cost_7d:.2f}", 
                                   "All agents combined", "💵", COLORS["primary"]), md=3),
            dbc.Col(create_kpi_card("Daily Average", f"${summary.total_cost_24h:.2f}", 
                                   "Cost per day", "📅", COLORS["info"]), md=3),
            dbc.Col(create_kpi_card("Total Tokens (24h)", f"{summary.total_tokens_24h:,}", 
                                   "Tokens consumed", "🔢", COLORS["secondary"]), md=3),
            dbc.Col(create_kpi_card("Cost Trend", f"{summary.cost_trend_pct:+.1f}%", 
                                   "vs previous period", "📈", 
                                   COLORS["success"] if summary.cost_trend_pct < 0 else COLORS["danger"]), md=3),
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("💰 Cost by Agent"),
                    dbc.CardBody(dcc.Graph(
                        figure=create_cost_by_agent_chart(summary.agents),
                        config={"displayModeBar": False}
                    ))
                ], className="shadow-sm")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Token Usage by Agent"),
                    dbc.CardBody(dcc.Graph(
                        figure=go.Figure(data=[
                            go.Bar(
                                x=[a.agent_name for a in sorted(summary.agents, key=lambda x: -x.total_tokens)[:10]],
                                y=[a.total_tokens for a in sorted(summary.agents, key=lambda x: -x.total_tokens)[:10]],
                                marker_color=COLORS["info"],
                                text=[f"{a.total_tokens:,}" for a in sorted(summary.agents, key=lambda x: -x.total_tokens)[:10]],
                                textposition="outside"
                            )
                        ]).update_layout(
                            title="Token Usage (Top 10)",
                            xaxis_title="Agent",
                            yaxis_title="Tokens",
                            height=350,
                            margin=dict(l=40, r=20, t=50, b=80),
                            paper_bgcolor="rgba(0,0,0,0)",
                            xaxis_tickangle=-45
                        ),
                        config={"displayModeBar": False}
                    ))
                ], className="shadow-sm")
            ], md=6),
        ], className="mb-4"),
        
        # Cost Optimization Tips
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("💡 Cost Optimization Tips"),
                    dbc.CardBody([
                        html.Ul([
                            html.Li("Switch to smaller models (gpt-4o-mini) for simple tasks"),
                            html.Li("Implement response caching for repeated queries"),
                            html.Li("Set maximum token limits per request"),
                            html.Li("Use batch processing for bulk operations"),
                            html.Li("Monitor and alert on unusual cost spikes"),
                        ])
                    ])
                ], className="shadow-sm")
            ])
        ])
    ])


# =============================================================================
# CALLBACKS
# =============================================================================

def create_evaluation_content(summary: FleetHealthSummary) -> html.Div:
    """Create the Continuous Evaluation tab content (Feb 2026)."""
    return html.Div([
        html.H4("🔍 Continuous Evaluation (Preview)", className="mb-3"),
        dbc.Alert([
            html.Strong("New in Feb 2026: "),
            "Continuous Evaluation runs AI-assisted evaluators automatically on agent sessions ",
            "in production. Results appear in the Foundry Portal under Operate > Assets > [agent] > Evaluations."
        ], color="info", className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📊 Evaluation Metrics"),
                    dbc.CardBody([
                        html.P("Continuous Evaluation measures agent quality in production using these evaluators:", 
                               className="text-muted"),
                        dbc.Table([
                            html.Thead(html.Tr([
                                html.Th("Evaluator"), html.Th("What It Measures"), html.Th("Category")
                            ])),
                            html.Tbody([
                                html.Tr([html.Td("Task Adherence"), html.Td("Did the agent follow its instructions?"), html.Td(dbc.Badge("Quality", color="primary"))]),
                                html.Tr([html.Td("Intent Resolution"), html.Td("Did the agent resolve the user's intent?"), html.Td(dbc.Badge("Quality", color="primary"))]),
                                html.Tr([html.Td("Tool Call Accuracy"), html.Td("Were the right tools called correctly?"), html.Td(dbc.Badge("Quality", color="primary"))]),
                                html.Tr([html.Td("Groundedness"), html.Td("Are responses grounded in retrieved data?"), html.Td(dbc.Badge("Safety", color="success"))]),
                                html.Tr([html.Td("Harmful Content"), html.Td("Hate, sexual, violent, self-harm content detection"), html.Td(dbc.Badge("Safety", color="danger"))]),
                                html.Tr([html.Td("Protected Material"), html.Td("Copyrighted content detection"), html.Td(dbc.Badge("Safety", color="warning"))]),
                                html.Tr([html.Td("Code Vulnerability"), html.Td("Security issues in generated code"), html.Td(dbc.Badge("Safety", color="danger"))]),
                            ])
                        ], striped=True, bordered=True, hover=True, responsive=True, size="sm")
                    ])
                ], className="shadow-sm h-100")
            ], md=7),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🚀 Setup Guide"),
                    dbc.CardBody([
                        html.P("Enable via Foundry Portal or SDK:", className="text-muted"),
                        html.Ol([
                            html.Li("Go to Foundry Portal > Operate > Assets"),
                            html.Li("Select your agent"),
                            html.Li("Click 'Evaluations' tab"),
                            html.Li("Enable Continuous Evaluation"),
                            html.Li("Select evaluators and sampling rate"),
                        ]),
                        html.Hr(),
                        html.P(html.Strong("SDK (Python):")),
                        html.Pre(
                            html.Code(
"""from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEvaluationRequest,
    EvaluatorConfiguration,
)

client = AIProjectClient(endpoint=endpoint, credential=cred)
client.evaluations.create_agent_evaluation(
    AgentEvaluationRequest(
        agent_id="your-agent-id",
        evaluators={
            "task_adherence": EvaluatorConfiguration(
                id="azureml://registries/..."
            ),
        },
        num_session=5,
    )
)""",
                                style={"fontSize": "0.75em"}
                            ),
                            style={"backgroundColor": "#f8f9fa", "padding": "10px", "borderRadius": "4px"}
                        ),
                    ])
                ], className="shadow-sm h-100"),
                
                dbc.Card([
                    dbc.CardHeader("🔗 Related Features"),
                    dbc.CardBody([
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Strong("AI Red Teaming Agent"),
                                html.P("Automated vulnerability probing and regression testing", 
                                      className="mb-0 text-muted small")
                            ]),
                            dbc.ListGroupItem([
                                html.Strong("Cluster Analysis"),
                                html.P("Error root-cause discovery across agent runs", 
                                      className="mb-0 text-muted small")
                            ]),
                            dbc.ListGroupItem([
                                html.Strong("Grafana Dashboards"),
                                html.P("Pre-built agent and workflow monitoring dashboards", 
                                      className="mb-0 text-muted small")
                            ]),
                        ], flush=True)
                    ])
                ], className="shadow-sm mt-3")
            ], md=5),
        ]),
        
        # Documentation links
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📚 Documentation"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.A("📖 Continuous Evaluation Docs", 
                                      href="https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/continuous-evaluation-agents?view=foundry",
                                      target="_blank", className="d-block mb-2"),
                                html.A("🛡️ AI Red Teaming Agent", 
                                      href="https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/ai-red-teaming-agent?view=foundry",
                                      target="_blank", className="d-block mb-2"),
                                html.A("📊 Agent Evaluators", 
                                      href="https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/agent-evaluators?view=foundry",
                                      target="_blank", className="d-block mb-2"),
                            ], md=4),
                            dbc.Col([
                                html.A("🔍 Cluster Analysis", 
                                      href="https://learn.microsoft.com/en-us/azure/ai-foundry/observability/how-to/cluster-analysis?view=foundry",
                                      target="_blank", className="d-block mb-2"),
                                html.A("📊 Grafana Agent Dashboard", 
                                      href="https://aka.ms/amg/dash/af-agent",
                                      target="_blank", className="d-block mb-2"),
                                html.A("📊 Grafana Workflow Dashboard", 
                                      href="https://aka.ms/amg/dash/af-workflow",
                                      target="_blank", className="d-block mb-2"),
                            ], md=4),
                            dbc.Col([
                                html.A("🎛️ Control Plane Overview", 
                                      href="https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/overview?view=foundry",
                                      target="_blank", className="d-block mb-2"),
                                html.A("📋 Register Custom Agents", 
                                      href="https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/register-custom-agent?view=foundry",
                                      target="_blank", className="d-block mb-2"),
                                html.A("🔧 Manage Agents", 
                                      href="https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/how-to-manage-agents?view=foundry",
                                      target="_blank", className="d-block mb-2"),
                            ], md=4),
                        ])
                    ])
                ], className="shadow-sm")
            ])
        ], className="mt-4"),
    ])


def register_callbacks(app: Dash):
    """Register all Dash callbacks."""
    
    @app.callback(
        Output("fleet-data-store", "data"),
        Output("last-refresh-time", "children"),
        Input("refresh-btn", "n_clicks"),
        Input("refresh-interval", "n_intervals"),
        prevent_initial_call=False
    )
    def refresh_data(n_clicks, n_intervals):
        """Fetch and store fleet data."""
        summary = get_data()
        data_source = get_data_source()
        
        # Convert to serializable dict
        data = {
            "total_agents": summary.total_agents,
            "active_agents": summary.active_agents,
            "healthy_agents": summary.healthy_agents,
            "warning_agents": summary.warning_agents,
            "critical_agents": summary.critical_agents,
            "fleet_health_score": summary.fleet_health_score,
            "avg_success_rate": summary.avg_success_rate,
            "total_runs_24h": summary.total_runs_24h,
            "total_errors_24h": summary.total_errors_24h,
            "total_cost_24h": summary.total_cost_24h,
            "total_cost_7d": summary.total_cost_7d,
            "total_tokens_24h": summary.total_tokens_24h,
            "cost_trend_pct": summary.cost_trend_pct,
            "compliant_agents": summary.compliant_agents,
            "non_compliant_agents": summary.non_compliant_agents,
            "total_policy_violations": summary.total_policy_violations,
            "critical_alerts": summary.critical_alerts,
            "high_alerts": summary.high_alerts,
            "medium_alerts": summary.medium_alerts,
            "low_alerts": summary.low_alerts,
            "agents": [
                {
                    "agent_id": a.agent_id,
                    "agent_name": a.agent_name,
                    "agent_version": a.agent_version,
                    "model": a.model,
                    "status": a.status.value,
                    "health_score": a.health_score,
                    "tools": a.tools,
                    "total_runs": a.total_runs,
                    "successful_runs": a.successful_runs,
                    "failed_runs": a.failed_runs,
                    "error_rate": a.error_rate,
                    "avg_latency_ms": a.avg_latency_ms,
                    "p95_latency_ms": a.p95_latency_ms,
                    "total_tokens": a.total_tokens,
                    "estimated_cost_usd": a.estimated_cost_usd,
                    "compliance_status": a.compliance_status,
                    "policy_violations": a.policy_violations,
                }
                for a in summary.agents
            ],
            "alerts": [
                {
                    "timestamp": str(a.get("timestamp", "")),
                    "message": a.get("message", ""),
                    "severity": a.get("severity", "low"),
                    "agent_name": a.get("agent_name", ""),
                    "source": a.get("source", ""),
                }
                for a in getattr(summary, 'alerts', [])
            ],
            "compliance_violations": getattr(summary, 'compliance_violations', []),
            "compliance_warnings": getattr(summary, 'compliance_warnings', []),
            "data_source": data_source,  # Track data source
        }
        
        # Show data source indicator
        source_badge = "🟢 Azure" if data_source == "azure" else "🟡 Demo"
        refresh_time = f"Last refresh: {datetime.now().strftime('%H:%M:%S')} | {source_badge}"
        return data, refresh_time
    
    @app.callback(
        Output("refresh-interval", "disabled"),
        Input("auto-refresh-switch", "value")
    )
    def toggle_auto_refresh(auto_refresh):
        """Enable/disable auto-refresh interval."""
        return not auto_refresh
    
    @app.callback(
        Output("tab-content", "children"),
        Input("main-tabs", "active_tab"),
        Input("fleet-data-store", "data")
    )
    def render_tab_content(active_tab, data):
        """Render content based on active tab."""
        if not data:
            return dbc.Alert("Loading data...", color="info")
        
        # Reconstruct summary from stored data
        summary = reconstruct_summary(data)
        
        if active_tab == "tab-overview":
            return create_overview_content(summary)
        elif active_tab == "tab-agents":
            return create_agents_content(summary)
        elif active_tab == "tab-alerts":
            return create_alerts_content(summary)
        elif active_tab == "tab-compliance":
            return create_compliance_content(summary)
        elif active_tab == "tab-cost":
            return create_cost_content(summary)
        elif active_tab == "tab-evaluation":
            return create_evaluation_content(summary)
        
        return dbc.Alert("Unknown tab", color="warning")
    
    @app.callback(
        Output("agents-table-container", "children"),
        Input("status-filter", "value"),
        Input("agent-search", "value"),
        Input("agent-sort", "value"),
        Input("fleet-data-store", "data")
    )
    def update_agents_table(status_filter, search, sort_by, data):
        """Update agents table based on filters."""
        if not data:
            return dbc.Alert("Loading...", color="info")
        
        summary = reconstruct_summary(data)
        agents = summary.agents
        
        # Filter by status
        if status_filter:
            agents = [a for a in agents if a.status.value in status_filter]
        
        # Filter by search
        if search:
            search_lower = search.lower()
            agents = [a for a in agents if search_lower in a.agent_name.lower()]
        
        # Sort
        sort_keys = {
            "health": lambda a: -a.health_score,
            "name": lambda a: a.agent_name.lower(),
            "runs": lambda a: -a.total_runs,
            "error": lambda a: -a.error_rate,
            "cost": lambda a: -a.estimated_cost_usd,
        }
        agents = sorted(agents, key=sort_keys.get(sort_by, lambda a: a.agent_name))
        
        if not agents:
            return dbc.Alert("No agents match the current filters", color="info")
        
        return create_agent_table(agents)


def reconstruct_summary(data: dict) -> FleetHealthSummary:
    """Reconstruct FleetHealthSummary from stored data dict."""
    agents = []
    for a in data.get("agents", []):
        status = HealthStatus(a["status"])
        agents.append(AgentHealthMetrics(
            agent_id=a["agent_id"],
            agent_name=a["agent_name"],
            agent_version=a["agent_version"],
            model=a["model"],
            status=status,
            health_score=a["health_score"],
            tools=a.get("tools", []),
            total_runs=a["total_runs"],
            successful_runs=a["successful_runs"],
            failed_runs=a["failed_runs"],
            error_rate=a["error_rate"],
            avg_latency_ms=a["avg_latency_ms"],
            p95_latency_ms=a.get("p95_latency_ms", 0),
            total_tokens=a["total_tokens"],
            estimated_cost_usd=a["estimated_cost_usd"],
            compliance_status=a.get("compliance_status", "unknown"),
            policy_violations=a.get("policy_violations", 0),
        ))
    
    summary = FleetHealthSummary(
        total_agents=data["total_agents"],
        active_agents=data["active_agents"],
        healthy_agents=data["healthy_agents"],
        warning_agents=data["warning_agents"],
        critical_agents=data["critical_agents"],
        fleet_health_score=data["fleet_health_score"],
        avg_success_rate=data["avg_success_rate"],
        total_runs_24h=data["total_runs_24h"],
        total_errors_24h=data["total_errors_24h"],
        total_cost_24h=data["total_cost_24h"],
        total_cost_7d=data["total_cost_7d"],
        total_tokens_24h=data["total_tokens_24h"],
        cost_trend_pct=data["cost_trend_pct"],
        compliant_agents=data["compliant_agents"],
        non_compliant_agents=data["non_compliant_agents"],
        total_policy_violations=data["total_policy_violations"],
        critical_alerts=data["critical_alerts"],
        high_alerts=data["high_alerts"],
        medium_alerts=data["medium_alerts"],
        low_alerts=data["low_alerts"],
        agents=agents,
    )
    
    # Add alerts
    summary.alerts = data.get("alerts", [])
    summary.compliance_violations = data.get("compliance_violations", [])
    summary.compliance_warnings = data.get("compliance_warnings", [])
    
    return summary


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def create_app() -> Dash:
    """Create and configure the Dash application."""
    # Use Bootstrap theme
    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP,  # Bootstrap icons
        ],
        suppress_callback_exceptions=True,
        title="Fleet Health Dashboard - Microsoft Foundry Control Plane"
    )
    
    app.layout = create_layout()
    register_callbacks(app)
    
    return app


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fleet Health Dashboard (Dash)")
    parser.add_argument("--port", type=int, default=8099, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--demo", action="store_true", help="Use demo data (skip Azure)")
    args = parser.parse_args()
    
    # If --demo flag passed, set global override
    if args.demo:
        os.environ.pop("AZURE_AI_PROJECT_ENDPOINT", None)  # Force demo mode
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║     🎛️  Microsoft Foundry Control Plane - Fleet Health       ║
║                      Dash Dashboard                            ║
╠═══════════════════════════════════════════════════════════════╣
║  Starting server at: http://{args.host}:{args.port}                    ║
║  Press Ctrl+C to stop                                          ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    app = create_app()
    app.run(debug=args.debug, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

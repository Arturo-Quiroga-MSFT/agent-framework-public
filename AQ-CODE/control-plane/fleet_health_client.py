#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Fleet Health Client - Control Plane Data Integration

This module provides a unified client for fetching fleet health data from:
- Azure AI Projects SDK (agent inventory, versions, metadata)
- Azure Monitor / Application Insights (metrics, traces, alerts)
- Azure Resource Graph (fleet-wide resource queries)
- Microsoft Defender for Cloud (security alerts)
- Azure Cost Management (cost data)

The client aggregates data from these sources to provide a comprehensive
view of your AI agent fleet's health, performance, and compliance status.

PREREQUISITES:
- Azure CLI authenticated: `az login`
- Environment variables configured (see .env.example)
- Required packages: azure-ai-projects, azure-monitor-query, azure-mgmt-resourcegraph

USAGE:
    from fleet_health_client import FleetHealthClient
    
    client = FleetHealthClient()
    health_data = await client.get_fleet_health_summary()
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

# Azure SDK imports
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Azure Monitor imports (for Application Insights metrics)
try:
    from azure.monitor.query import LogsQueryClient, MetricsQueryClient
    from azure.monitor.query import LogsQueryStatus
    AZURE_MONITOR_AVAILABLE = True
except ImportError:
    AZURE_MONITOR_AVAILABLE = False
    print("Warning: azure-monitor-query not installed. Install with: pip install azure-monitor-query")

# Azure Resource Graph (for fleet-wide queries)
try:
    from azure.mgmt.resourcegraph import ResourceGraphClient
    from azure.mgmt.resourcegraph.models import QueryRequest
    RESOURCE_GRAPH_AVAILABLE = True
except ImportError:
    RESOURCE_GRAPH_AVAILABLE = False
    print("Warning: azure-mgmt-resourcegraph not installed. Install with: pip install azure-mgmt-resourcegraph")


class HealthStatus(Enum):
    """Health status levels for agents and fleet."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class AgentHealthMetrics:
    """Health metrics for a single agent."""
    agent_id: str
    agent_name: str
    agent_version: str
    model: str
    status: HealthStatus
    health_score: float  # 0-100
    
    # Performance metrics
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    
    # Cost metrics
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    
    # Compliance
    compliance_status: str = "unknown"
    policy_violations: int = 0
    
    # Timestamps
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    
    # Alerts
    active_alerts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FleetHealthSummary:
    """Summary of fleet-wide health metrics."""
    # Counts
    total_agents: int = 0
    active_agents: int = 0
    healthy_agents: int = 0
    warning_agents: int = 0
    critical_agents: int = 0
    
    # Performance
    fleet_health_score: float = 0.0
    avg_success_rate: float = 0.0
    total_runs_24h: int = 0
    total_errors_24h: int = 0
    
    # Cost
    total_cost_24h: float = 0.0
    total_cost_7d: float = 0.0
    total_tokens_24h: int = 0
    cost_trend_pct: float = 0.0  # % change from previous period
    
    # Compliance
    compliant_agents: int = 0
    non_compliant_agents: int = 0
    total_policy_violations: int = 0
    
    # Alerts
    critical_alerts: int = 0
    high_alerts: int = 0
    medium_alerts: int = 0
    low_alerts: int = 0
    
    # Timestamp
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Individual agent data
    agents: List[AgentHealthMetrics] = field(default_factory=list)


class FleetHealthClient:
    """
    Unified client for fetching AI fleet health data from Control Plane sources.
    
    Aggregates data from:
    - Azure AI Projects SDK
    - Azure Monitor / Application Insights
    - Azure Resource Graph
    - Microsoft Defender for Cloud
    """
    
    def __init__(
        self,
        project_endpoint: Optional[str] = None,
        subscription_id: Optional[str] = None,
        app_insights_connection_string: Optional[str] = None,
        workspace_id: Optional[str] = None
    ):
        """
        Initialize the Fleet Health Client.
        
        Args:
            project_endpoint: Azure AI Project endpoint URL
            subscription_id: Azure subscription ID for resource graph queries
            app_insights_connection_string: Application Insights connection string
            workspace_id: Log Analytics workspace ID for Kusto queries
        """
        self.project_endpoint = project_endpoint or os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
        self.subscription_id = subscription_id or os.environ.get("AZURE_SUBSCRIPTION_ID")
        self.app_insights_conn_str = app_insights_connection_string or os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
        self.workspace_id = workspace_id or os.environ.get("LOG_ANALYTICS_WORKSPACE_ID")
        
        # Initialize credential
        self.credential = DefaultAzureCredential()
        
        # Initialize clients lazily
        self._project_client: Optional[AIProjectClient] = None
        self._logs_client: Optional[Any] = None
        self._metrics_client: Optional[Any] = None
        self._resource_graph_client: Optional[Any] = None
    
    @property
    def project_client(self) -> AIProjectClient:
        """Lazy initialization of AI Project client."""
        if self._project_client is None:
            if not self.project_endpoint:
                raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable not set")
            self._project_client = AIProjectClient(
                endpoint=self.project_endpoint,
                credential=self.credential
            )
        return self._project_client
    
    @property
    def logs_client(self):
        """Lazy initialization of Azure Monitor Logs client."""
        if self._logs_client is None and AZURE_MONITOR_AVAILABLE:
            self._logs_client = LogsQueryClient(self.credential)
        return self._logs_client
    
    @property
    def metrics_client(self):
        """Lazy initialization of Azure Monitor Metrics client."""
        if self._metrics_client is None and AZURE_MONITOR_AVAILABLE:
            self._metrics_client = MetricsQueryClient(self.credential)
        return self._metrics_client
    
    @property
    def resource_graph_client(self):
        """Lazy initialization of Resource Graph client."""
        if self._resource_graph_client is None and RESOURCE_GRAPH_AVAILABLE:
            self._resource_graph_client = ResourceGraphClient(self.credential)
        return self._resource_graph_client
    
    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Fetch all agents from Azure AI Project.
        
        Returns:
            List of agent dictionaries with metadata
        """
        agents = []
        try:
            # List all agents using the SDK
            for agent in self.project_client.agents.list():
                agents.append({
                    "id": getattr(agent, 'id', getattr(agent, 'name', 'unknown')),
                    "name": getattr(agent, 'name', getattr(agent, 'display_name', 'Unknown Agent')),
                    "version": getattr(agent, 'version', '1'),
                    "model": getattr(agent, 'model', getattr(agent, 'model_id', 'unknown')),
                    "instructions": (getattr(agent, 'instructions', '') or '')[:200],
                    "tools": [t.type if hasattr(t, 'type') else str(t) for t in getattr(agent, 'tools', []) or []],
                    "created_at": getattr(agent, 'created_at', None),
                    "metadata": getattr(agent, 'metadata', {}) or {},
                    "status": "active"  # Default status
                })
        except Exception as e:
            print(f"Error fetching agents: {e}")
        
        return agents
    
    async def get_agent_metrics(
        self,
        agent_id: str,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Fetch performance metrics for a specific agent from Application Insights.
        
        Args:
            agent_id: The agent ID to query metrics for
            time_range_hours: Hours of historical data to fetch
            
        Returns:
            Dictionary with performance metrics
        """
        metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "error_rate": 0.0,
            "avg_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        
        if not self.logs_client or not self.workspace_id:
            return metrics
        
        try:
            # Query AppDependencies table where OpenTelemetry GenAI spans are stored
            # Properties is a JSON string containing gen_ai.* attributes
            query = f"""
            AppDependencies
            | where TimeGenerated >= ago({time_range_hours}h)
            | where DependencyType == "GenAI | azure_ai_agents"
            | extend props = parse_json(Properties)
            | where props["gen_ai.agent.id"] == "{agent_id}" 
               or props["gen_ai.agent.name"] == "{agent_id}"
            | summarize 
                total_runs = count(),
                successful_runs = countif(Success == true),
                failed_runs = countif(Success == false),
                avg_latency = avg(DurationMs),
                p95_latency = percentile(DurationMs, 95),
                total_tokens = sum(toint(props["gen_ai.usage.total_tokens"]))
            """
            
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=query,
                timespan=timedelta(hours=time_range_hours)
            )
            
            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                table = response.tables[0]
                if table.rows:
                    row = table.rows[0]
                    metrics["total_runs"] = row[0] or 0
                    metrics["successful_runs"] = row[1] or 0
                    metrics["failed_runs"] = row[2] or 0
                    metrics["avg_latency_ms"] = row[3] or 0.0
                    metrics["p95_latency_ms"] = row[4] or 0.0
                    metrics["total_tokens"] = row[5] or 0
                    
                    if metrics["total_runs"] > 0:
                        metrics["error_rate"] = metrics["failed_runs"] / metrics["total_runs"]
                        
        except Exception as e:
            print(f"Error fetching agent metrics for {agent_id}: {e}")
        
        return metrics
    
    async def get_fleet_alerts(self) -> List[Dict[str, Any]]:
        """
        Fetch active alerts from Application Insights.
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if not self.logs_client or not self.workspace_id:
            return alerts
        
        try:
            # Query for errors and exceptions from agent runs
            query = """
            AppDependencies
            | where TimeGenerated >= ago(24h)
            | where DependencyType == "GenAI | azure_ai_agents"
            | where Success == false
            | extend props = parse_json(Properties)
            | project 
                TimeGenerated,
                Message = Name,
                agent_id = tostring(props["gen_ai.agent.id"]),
                agent_name = tostring(props["gen_ai.agent.name"]),
                model = tostring(props["gen_ai.request.model"]),
                DurationMs
            | order by TimeGenerated desc
            | take 100
            """
            
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=query,
                timespan=timedelta(hours=24)
            )
            
            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                table = response.tables[0]
                for row in table.rows:
                    alerts.append({
                        "timestamp": row[0],
                        "message": f"Agent run failed: {row[1]}",
                        "severity": "high",
                        "agent_id": row[2] or row[3],
                        "agent_name": row[3],
                        "model": row[4],
                        "duration_ms": row[5],
                        "source": "application_insights"
                    })
            
            # Also check AppExceptions
            exc_query = """
            AppExceptions
            | where TimeGenerated >= ago(24h)
            | project TimeGenerated, ExceptionType, OuterMessage, InnermostMessage
            | order by TimeGenerated desc
            | take 50
            """
            
            exc_response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=exc_query,
                timespan=timedelta(hours=24)
            )
            
            if exc_response.status == LogsQueryStatus.SUCCESS and exc_response.tables:
                table = exc_response.tables[0]
                for row in table.rows:
                    alerts.append({
                        "timestamp": row[0],
                        "message": f"{row[1]}: {row[2] or row[3]}",
                        "severity": "critical",
                        "agent_id": None,
                        "source": "exceptions"
                    })
                    
        except Exception as e:
            print(f"Error fetching alerts: {e}")
        
        return alerts
    
    async def get_cost_data(
        self,
        time_range_days: int = 7
    ) -> Dict[str, Any]:
        """
        Fetch cost data aggregated by agent.
        
        Note: This uses token counts and estimated pricing.
        For actual cost data, integrate with Azure Cost Management API.
        
        Args:
            time_range_days: Days of historical data
            
        Returns:
            Dictionary with cost metrics
        """
        cost_data = {
            "total_cost_usd": 0.0,
            "cost_by_agent": {},
            "cost_by_model": {},
            "cost_trend": []
        }
        
        if not self.logs_client or not self.workspace_id:
            return cost_data
        
        try:
            # Query token usage and estimate costs
            query = f"""
            traces
            | where timestamp >= ago({time_range_days}d)
            | where customDimensions has 'gen_ai.usage'
            | extend 
                agent_id = coalesce(
                    customDimensions['gen_ai.agent.id'],
                    customDimensions['gen_ai.agents.id']
                ),
                model = customDimensions['gen_ai.request.model'],
                prompt_tokens = toint(customDimensions['gen_ai.usage.input_tokens']),
                completion_tokens = toint(customDimensions['gen_ai.usage.output_tokens'])
            | summarize 
                total_prompt = sum(prompt_tokens),
                total_completion = sum(completion_tokens)
                by agent_id, model, bin(timestamp, 1d)
            | order by timestamp asc
            """
            
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=query,
                timespan=timedelta(days=time_range_days)
            )
            
            if response.status == LogsQueryStatus.SUCCESS and response.tables:
                # Estimated pricing per 1K tokens (adjust based on actual model pricing)
                pricing = {
                    "gpt-4o": {"input": 0.005, "output": 0.015},
                    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
                    "gpt-4": {"input": 0.03, "output": 0.06},
                    "default": {"input": 0.002, "output": 0.002}
                }
                
                table = response.tables[0]
                for row in table.rows:
                    agent_id = row[0] or "unknown"
                    model = row[1] or "default"
                    prompt_tokens = row[2] or 0
                    completion_tokens = row[3] or 0
                    
                    # Get pricing for model
                    model_pricing = pricing.get(model, pricing["default"])
                    
                    # Calculate cost
                    cost = (
                        (prompt_tokens / 1000) * model_pricing["input"] +
                        (completion_tokens / 1000) * model_pricing["output"]
                    )
                    
                    cost_data["total_cost_usd"] += cost
                    
                    if agent_id not in cost_data["cost_by_agent"]:
                        cost_data["cost_by_agent"][agent_id] = 0.0
                    cost_data["cost_by_agent"][agent_id] += cost
                    
                    if model not in cost_data["cost_by_model"]:
                        cost_data["cost_by_model"][model] = 0.0
                    cost_data["cost_by_model"][model] += cost
                    
        except Exception as e:
            print(f"Error fetching cost data: {e}")
        
        return cost_data
    
    async def get_compliance_status(self) -> Dict[str, Any]:
        """
        Fetch compliance status for agents.
        
        Note: Full compliance data requires Azure Policy integration.
        This provides a basic compliance check based on guardrail configurations.
        
        Returns:
            Dictionary with compliance metrics
        """
        compliance = {
            "total_agents": 0,
            "compliant": 0,
            "non_compliant": 0,
            "violations": [],
            "agents_status": {}
        }
        
        try:
            # Get all agents and check for basic compliance indicators
            agents = await self.get_all_agents()
            compliance["total_agents"] = len(agents)
            
            for agent in agents:
                agent_id = agent["id"]
                
                # Basic compliance checks
                is_compliant = True
                violations = []
                
                # Check 1: Has instructions defined
                if not agent.get("instructions"):
                    is_compliant = False
                    violations.append("Missing instructions/system prompt")
                
                # Check 2: Has metadata for tracking
                if not agent.get("metadata"):
                    violations.append("Missing metadata (recommended for governance)")
                
                # Check 3: Tools configured
                if not agent.get("tools"):
                    violations.append("No tools configured")
                
                compliance["agents_status"][agent_id] = {
                    "name": agent["name"],
                    "compliant": is_compliant,
                    "violations": violations
                }
                
                if is_compliant:
                    compliance["compliant"] += 1
                else:
                    compliance["non_compliant"] += 1
                    compliance["violations"].extend([
                        {"agent_id": agent_id, "agent_name": agent["name"], "violation": v}
                        for v in violations
                    ])
                    
        except Exception as e:
            print(f"Error checking compliance: {e}")
        
        return compliance
    
    def _calculate_health_score(
        self,
        error_rate: float,
        avg_latency_ms: float,
        has_violations: bool
    ) -> float:
        """
        Calculate a health score (0-100) based on multiple factors.
        
        Args:
            error_rate: Error rate as decimal (0-1)
            avg_latency_ms: Average latency in milliseconds
            has_violations: Whether agent has compliance violations
            
        Returns:
            Health score from 0-100
        """
        score = 100.0
        
        # Deduct for error rate (up to 40 points)
        score -= min(error_rate * 100, 40)
        
        # Deduct for high latency (up to 20 points)
        # >5s is considered high latency
        if avg_latency_ms > 5000:
            score -= 20
        elif avg_latency_ms > 2000:
            score -= 10
        elif avg_latency_ms > 1000:
            score -= 5
        
        # Deduct for violations (20 points)
        if has_violations:
            score -= 20
        
        return max(0, min(100, score))
    
    def _get_health_status(self, health_score: float) -> HealthStatus:
        """Convert health score to status."""
        if health_score >= 80:
            return HealthStatus.HEALTHY
        elif health_score >= 50:
            return HealthStatus.WARNING
        elif health_score > 0:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.UNKNOWN
    
    async def get_agent_health(self, agent: Dict[str, Any]) -> AgentHealthMetrics:
        """
        Get comprehensive health metrics for a single agent.
        
        Args:
            agent: Agent dictionary from get_all_agents()
            
        Returns:
            AgentHealthMetrics dataclass with all health data
        """
        agent_id = agent["id"]
        
        # Fetch metrics
        metrics = await self.get_agent_metrics(agent_id)
        
        # Check compliance
        has_violations = not agent.get("instructions")
        
        # Calculate health score
        health_score = self._calculate_health_score(
            error_rate=metrics["error_rate"],
            avg_latency_ms=metrics["avg_latency_ms"],
            has_violations=has_violations
        )
        
        # Estimate cost (rough calculation)
        # GPT-4o-mini pricing: $0.15/1M input, $0.60/1M output
        estimated_cost = metrics["total_tokens"] * 0.0000004  # Rough average
        
        return AgentHealthMetrics(
            agent_id=agent_id,
            agent_name=agent["name"],
            agent_version=agent.get("version", "1"),
            model=agent.get("model", "unknown"),
            status=self._get_health_status(health_score),
            health_score=health_score,
            total_runs=metrics["total_runs"],
            successful_runs=metrics["successful_runs"],
            failed_runs=metrics["failed_runs"],
            error_rate=metrics["error_rate"],
            avg_latency_ms=metrics["avg_latency_ms"],
            p95_latency_ms=metrics.get("p95_latency_ms", 0.0),
            total_tokens=metrics["total_tokens"],
            prompt_tokens=metrics.get("prompt_tokens", 0),
            completion_tokens=metrics.get("completion_tokens", 0),
            estimated_cost_usd=estimated_cost,
            compliance_status="compliant" if not has_violations else "non-compliant",
            policy_violations=1 if has_violations else 0,
            created_at=agent.get("created_at"),
            last_active=None,
            active_alerts=[]
        )
    
    async def get_fleet_health_summary(self) -> FleetHealthSummary:
        """
        Get comprehensive health summary for the entire fleet.
        
        Returns:
            FleetHealthSummary with aggregated metrics for all agents
        """
        summary = FleetHealthSummary()
        
        # Fetch all agents
        agents = await self.get_all_agents()
        summary.total_agents = len(agents)
        
        # Fetch alerts
        alerts = await self.get_fleet_alerts()
        for alert in alerts:
            severity = alert.get("severity", "low")
            if severity == "critical":
                summary.critical_alerts += 1
            elif severity == "high":
                summary.high_alerts += 1
            elif severity == "medium":
                summary.medium_alerts += 1
            else:
                summary.low_alerts += 1
        
        # Fetch cost data
        cost_data = await self.get_cost_data(time_range_days=7)
        summary.total_cost_7d = cost_data["total_cost_usd"]
        
        # Fetch compliance
        compliance = await self.get_compliance_status()
        summary.compliant_agents = compliance["compliant"]
        summary.non_compliant_agents = compliance["non_compliant"]
        summary.total_policy_violations = len(compliance["violations"])
        
        # Process each agent
        total_health_score = 0.0
        total_success_rate = 0.0
        
        for agent in agents:
            agent_health = await self.get_agent_health(agent)
            summary.agents.append(agent_health)
            
            # Aggregate metrics
            total_health_score += agent_health.health_score
            summary.total_runs_24h += agent_health.total_runs
            summary.total_errors_24h += agent_health.failed_runs
            summary.total_tokens_24h += agent_health.total_tokens
            
            if agent_health.total_runs > 0:
                total_success_rate += (1 - agent_health.error_rate)
            
            # Count by status
            if agent_health.status == HealthStatus.HEALTHY:
                summary.healthy_agents += 1
            elif agent_health.status == HealthStatus.WARNING:
                summary.warning_agents += 1
            elif agent_health.status == HealthStatus.CRITICAL:
                summary.critical_agents += 1
            
            # Count active agents (had runs in last 24h)
            if agent_health.total_runs > 0:
                summary.active_agents += 1
        
        # Calculate averages
        if summary.total_agents > 0:
            summary.fleet_health_score = total_health_score / summary.total_agents
            summary.avg_success_rate = total_success_rate / summary.total_agents
        
        # Estimate 24h cost (7d cost / 7)
        summary.total_cost_24h = summary.total_cost_7d / 7
        
        return summary
    
    def close(self):
        """Clean up client resources."""
        if self._project_client:
            # AIProjectClient doesn't have explicit close, but good practice
            pass


# Convenience function for running async code
def get_fleet_health_sync() -> FleetHealthSummary:
    """Synchronous wrapper for getting fleet health."""
    client = FleetHealthClient()
    try:
        return asyncio.run(client.get_fleet_health_summary())
    finally:
        client.close()


if __name__ == "__main__":
    # Test the client
    import asyncio
    
    async def main():
        client = FleetHealthClient()
        
        print("Fetching fleet health summary...")
        summary = await client.get_fleet_health_summary()
        
        print(f"\n=== Fleet Health Summary ===")
        print(f"Total Agents: {summary.total_agents}")
        print(f"Active Agents: {summary.active_agents}")
        print(f"Fleet Health Score: {summary.fleet_health_score:.1f}%")
        print(f"\nHealth Status:")
        print(f"  ✅ Healthy: {summary.healthy_agents}")
        print(f"  ⚠️  Warning: {summary.warning_agents}")
        print(f"  🔴 Critical: {summary.critical_agents}")
        print(f"\nAlerts (24h):")
        print(f"  🔴 Critical: {summary.critical_alerts}")
        print(f"  🟠 High: {summary.high_alerts}")
        print(f"  🟡 Medium: {summary.medium_alerts}")
        print(f"  🔵 Low: {summary.low_alerts}")
        print(f"\nCost:")
        print(f"  24h: ${summary.total_cost_24h:.2f}")
        print(f"  7d: ${summary.total_cost_7d:.2f}")
        print(f"\nCompliance:")
        print(f"  ✅ Compliant: {summary.compliant_agents}")
        print(f"  ❌ Non-compliant: {summary.non_compliant_agents}")
        print(f"  Policy Violations: {summary.total_policy_violations}")
        
        print(f"\n=== Agent Details ===")
        for agent in summary.agents:
            status_emoji = "✅" if agent.status == HealthStatus.HEALTHY else "⚠️" if agent.status == HealthStatus.WARNING else "🔴"
            print(f"\n{status_emoji} {agent.agent_name} (v{agent.agent_version})")
            print(f"   Health: {agent.health_score:.1f}% | Model: {agent.model}")
            print(f"   Runs: {agent.total_runs} | Errors: {agent.failed_runs} | Rate: {agent.error_rate*100:.1f}%")
            print(f"   Tokens: {agent.total_tokens:,} | Est. Cost: ${agent.estimated_cost_usd:.4f}")
        
        client.close()
    
    asyncio.run(main())

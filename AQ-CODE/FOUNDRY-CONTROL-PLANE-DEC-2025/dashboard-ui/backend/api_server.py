#!/usr/bin/env python3
"""
FastAPI backend for Fleet Health Dashboard (React UI).

Wraps the existing FleetHealthClient to serve REST endpoints.

Usage:
    uvicorn api_server:app --port 8098 --reload
"""

import math
import os
import sys
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

# Load env from the control-plane directory (two levels up from backend/)
_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_env_path = os.path.join(_parent_dir, ".env")
if os.path.exists(_env_path):
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv()

# Add control-plane directory so we can import fleet_health_client
sys.path.insert(0, _parent_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fleet_health_client import (
    FleetHealthClient,
    FleetHealthSummary,
    AgentHealthMetrics,
    HealthStatus,
)

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
_client: FleetHealthClient | None = None
_cached_summary: dict[str, Any] | None = None
_cache_time: datetime | None = None
_data_source: str = "unknown"
CACHE_TTL_SECONDS = 30


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _client
    _client = FleetHealthClient()
    yield
    if _client:
        _client.close()


app = FastAPI(
    title="Fleet Health API",
    description="REST API for Foundry Control Plane Fleet Health Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitize(obj):
    """Replace NaN/Inf floats with 0 so JSON serialization succeeds."""
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return 0.0
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj


def _serialize_agent(a: AgentHealthMetrics) -> dict:
    return {
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
        "prompt_tokens": a.prompt_tokens,
        "completion_tokens": a.completion_tokens,
        "estimated_cost_usd": a.estimated_cost_usd,
        "compliance_status": a.compliance_status,
        "policy_violations": a.policy_violations,
    }


def _serialize_summary(summary: FleetHealthSummary, source: str) -> dict:
    alerts_raw = getattr(summary, "alerts", [])
    alerts = []
    for a in alerts_raw:
        ts = a.get("timestamp", "")
        alerts.append({
            "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
            "message": a.get("message", ""),
            "severity": a.get("severity", "low"),
            "agent_name": a.get("agent_name", ""),
            "source": a.get("source", ""),
        })

    result = {
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
        "agents": [_serialize_agent(a) for a in summary.agents],
        "alerts": alerts,
        "compliance_violations": getattr(summary, "compliance_violations", []),
        "compliance_warnings": getattr(summary, "compliance_warnings", []),
        "generated_at": datetime.now().isoformat(),
        "data_source": source,
    }
    return _sanitize(result)


def _create_demo_data() -> FleetHealthSummary:
    """Demo data matching the Dash version."""
    demo_agents = [
        AgentHealthMetrics(agent_id="demo-1", agent_name="Market_Researcher", agent_version="2",
            model="gpt-4.1-mini", status=HealthStatus.HEALTHY, health_score=92.0,
            tools=["web_search", "file_search"], total_runs=156, successful_runs=152,
            failed_runs=4, error_rate=0.026, avg_latency_ms=1250, p95_latency_ms=2100,
            total_tokens=45000, prompt_tokens=30000, completion_tokens=15000,
            estimated_cost_usd=0.045, compliance_status="compliant", policy_violations=0),
        AgentHealthMetrics(agent_id="demo-2", agent_name="Marketing_Strategist", agent_version="1",
            model="gpt-4.1", status=HealthStatus.HEALTHY, health_score=88.0,
            tools=["code_interpreter"], total_runs=89, successful_runs=85,
            failed_runs=4, error_rate=0.045, avg_latency_ms=1800, p95_latency_ms=3200,
            total_tokens=62000, prompt_tokens=40000, completion_tokens=22000,
            estimated_cost_usd=0.85, compliance_status="compliant", policy_violations=0),
        AgentHealthMetrics(agent_id="demo-3", agent_name="Legal_Compliance_Advisor", agent_version="3",
            model="gpt-4.1", status=HealthStatus.WARNING, health_score=72.0,
            tools=["file_search"], total_runs=45, successful_runs=40,
            failed_runs=5, error_rate=0.111, avg_latency_ms=2500, p95_latency_ms=4500,
            total_tokens=38000, prompt_tokens=25000, completion_tokens=13000,
            estimated_cost_usd=0.52, compliance_status="non-compliant", policy_violations=1),
        AgentHealthMetrics(agent_id="demo-4", agent_name="Financial_Analyst", agent_version="1",
            model="gpt-4.1-mini", status=HealthStatus.HEALTHY, health_score=95.0,
            tools=["code_interpreter", "file_search"], total_runs=234, successful_runs=232,
            failed_runs=2, error_rate=0.009, avg_latency_ms=980, p95_latency_ms=1500,
            total_tokens=72000, prompt_tokens=48000, completion_tokens=24000,
            estimated_cost_usd=0.072, compliance_status="compliant", policy_violations=0),
        AgentHealthMetrics(agent_id="demo-5", agent_name="Technical_Architect", agent_version="2",
            model="gpt-4.1", status=HealthStatus.CRITICAL, health_score=45.0,
            tools=["code_interpreter", "web_search"], total_runs=67, successful_runs=52,
            failed_runs=15, error_rate=0.224, avg_latency_ms=3500, p95_latency_ms=6000,
            total_tokens=55000, prompt_tokens=35000, completion_tokens=20000,
            estimated_cost_usd=0.75, compliance_status="non-compliant", policy_violations=2),
        AgentHealthMetrics(agent_id="demo-6", agent_name="Customer_Support_Bot", agent_version="4",
            model="gpt-4.1-mini", status=HealthStatus.HEALTHY, health_score=91.0,
            tools=["file_search"], total_runs=512, successful_runs=498,
            failed_runs=14, error_rate=0.027, avg_latency_ms=850, p95_latency_ms=1200,
            total_tokens=125000, prompt_tokens=80000, completion_tokens=45000,
            estimated_cost_usd=0.125, compliance_status="compliant", policy_violations=0),
        AgentHealthMetrics(agent_id="demo-7", agent_name="SRE_Monitoring_Agent", agent_version="1",
            model="gpt-4.1", status=HealthStatus.HEALTHY, health_score=94.0,
            tools=["code_interpreter", "web_search"], total_runs=320, successful_runs=315,
            failed_runs=5, error_rate=0.016, avg_latency_ms=1100, p95_latency_ms=1800,
            total_tokens=89000, prompt_tokens=58000, completion_tokens=31000,
            estimated_cost_usd=0.89, compliance_status="compliant", policy_violations=0),
        AgentHealthMetrics(agent_id="demo-8", agent_name="Custom_RAG_Agent", agent_version="2",
            model="gpt-4o", status=HealthStatus.HEALTHY, health_score=87.0,
            tools=["file_search", "web_search"], total_runs=178, successful_runs=170,
            failed_runs=8, error_rate=0.045, avg_latency_ms=1450, p95_latency_ms=2400,
            total_tokens=96000, prompt_tokens=62000, completion_tokens=34000,
            estimated_cost_usd=0.96, compliance_status="compliant", policy_violations=0),
    ]

    summary = FleetHealthSummary(
        total_agents=8, active_agents=8, healthy_agents=6,
        warning_agents=1, critical_agents=1, fleet_health_score=83.0,
        avg_success_rate=0.940, total_runs_24h=1601, total_errors_24h=53,
        total_cost_24h=4.21, total_cost_7d=29.47, total_tokens_24h=582000,
        cost_trend_pct=-3.8, compliant_agents=6, non_compliant_agents=2,
        total_policy_violations=3, critical_alerts=1, high_alerts=1,
        medium_alerts=1, low_alerts=2, generated_at=datetime.now(),
        agents=demo_agents,
    )
    summary.alerts = [
        {"timestamp": datetime.now(), "message": "High latency detected",
         "severity": "high", "agent_name": "Technical_Architect", "source": "application_insights"},
        {"timestamp": datetime.now(), "message": "Rate limit reached",
         "severity": "critical", "agent_name": "Customer_Support_Bot", "source": "application_insights"},
        {"timestamp": datetime.now(), "message": "Token quota warning",
         "severity": "medium", "agent_name": "Marketing_Strategist", "source": "application_insights"},
    ]
    summary.compliance_violations = [
        {"agent_name": "Technical_Architect", "rule": "missing_instructions",
         "severity": "critical", "message": "Missing system prompt",
         "recommendation": "Add clear instructions to define agent behavior"},
        {"agent_name": "Legal_Compliance_Advisor", "rule": "deprecated_model",
         "severity": "high", "message": "Using deprecated model configuration",
         "recommendation": "Review and update model settings"},
    ]
    summary.compliance_warnings = [
        {"agent_name": "Market_Researcher", "rule": "high_risk_tools_no_safety",
         "severity": "medium", "message": "Web search tool without safety instructions",
         "recommendation": "Add content safety guidelines"},
    ]
    return summary


async def _fetch_summary() -> tuple[dict, str]:
    """Fetch (or cache) the fleet health summary."""
    global _cached_summary, _cache_time, _data_source

    now = datetime.now()
    if _cached_summary and _cache_time and (now - _cache_time).total_seconds() < CACHE_TTL_SECONDS:
        return _cached_summary, _data_source

    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if endpoint and _client:
        try:
            summary = await _client.get_fleet_health_summary()
            if summary and summary.total_agents > 0:
                _data_source = "azure"
                _cached_summary = _serialize_summary(summary, _data_source)
                _cache_time = now
                return _cached_summary, _data_source
        except Exception as e:
            print(f"Azure fetch failed: {e}")

    _data_source = "demo"
    demo = _create_demo_data()
    _cached_summary = _serialize_summary(demo, _data_source)
    _cache_time = now
    return _cached_summary, _data_source


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/fleet")
async def get_fleet_summary():
    """Full fleet health summary (overview + agents + alerts + compliance)."""
    data, _ = await _fetch_summary()
    return data


@app.get("/api/fleet/agents")
async def get_agents():
    data, _ = await _fetch_summary()
    return {"agents": data["agents"], "total": data["total_agents"]}


@app.get("/api/fleet/alerts")
async def get_alerts():
    data, _ = await _fetch_summary()
    return {
        "alerts": data["alerts"],
        "critical": data["critical_alerts"],
        "high": data["high_alerts"],
        "medium": data["medium_alerts"],
        "low": data["low_alerts"],
    }


@app.get("/api/fleet/compliance")
async def get_compliance():
    data, _ = await _fetch_summary()
    return {
        "compliant_agents": data["compliant_agents"],
        "non_compliant_agents": data["non_compliant_agents"],
        "total_policy_violations": data["total_policy_violations"],
        "violations": data["compliance_violations"],
        "warnings": data["compliance_warnings"],
    }


@app.get("/api/fleet/cost")
async def get_cost():
    data, _ = await _fetch_summary()
    return {
        "total_cost_24h": data["total_cost_24h"],
        "total_cost_7d": data["total_cost_7d"],
        "total_tokens_24h": data["total_tokens_24h"],
        "cost_trend_pct": data["cost_trend_pct"],
        "agents": [
            {"name": a["agent_name"], "cost": a["estimated_cost_usd"],
             "tokens": a["total_tokens"], "model": a["model"]}
            for a in sorted(data["agents"], key=lambda x: -x["estimated_cost_usd"])
        ],
    }


@app.post("/api/fleet/refresh")
async def force_refresh():
    """Clear cache and force a fresh fetch."""
    global _cached_summary, _cache_time
    _cached_summary = None
    _cache_time = None
    data, source = await _fetch_summary()
    return {"status": "refreshed", "data_source": source, "total_agents": data["total_agents"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="127.0.0.1", port=8098, reload=True)

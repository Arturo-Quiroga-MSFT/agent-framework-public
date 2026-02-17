# Copyright (c) Microsoft. All rights reserved.
"""
AI Governance & Model Compliance Workflow - DevUI Version with Tracing

Pattern: Fan-out / Fan-in with embedded "planner" agent (governance_planner) whose output
is conceptually the checklist others respond to; implemented simply as another concurrent
agent to keep framework usage consistent.

GOAL:
Given a description of an AI system (e.g., healthcare triage model, credit risk scorer),
produce a structured governance & compliance assessment and risk register.

AGENTS (Concurrent):
1. Governance Planner: Establish evaluation checklist, contextual risk categories
2. Data Provenance & Quality Reviewer: Sources, labeling, lineage, drift concerns
3. Fairness & Bias Auditor: Protected attributes, disparity metrics, mitigation strategies
4. Privacy & Data Minimization Specialist: PII, PHI handling, anonymization, retention
5. Security & Robustness Engineer: Threat modeling, adversarial robustness, supply chain
6. Regulatory Alignment Analyst: Mapping to EU AI Act, FTC guidance, sector regulations
7. Risk Register Curator: (Synthesized in aggregator) — final structured table

OUTPUT: Structured sections + Risk Register (Risk, Impact, Likelihood, Mitigation, Owner, ETA)

PREREQUISITES: Azure OpenAI + az login.
TRACING: Standard environment variable pattern.
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List

# Execution timing
START_TIME: datetime | None = None

from dotenv import load_dotenv
from agent_framework import Message, Executor, WorkflowBuilder, WorkflowContext, handler, AgentExecutorRequest, AgentExecutorResponse
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import configure_otel_providers
from azure.identity import AzureCliCredential
from pydantic import BaseModel, Field

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")


class AIGovernanceInput(BaseModel):
    """Input model for AI governance compliance analysis."""
    description: str = Field(
        ...,
        description="Describe the AI system: purpose, data, users, deployment context, criticality",
        examples=[
            "LLM-based clinical decision support suggesting differential diagnoses to physicians",
            "Credit risk scoring model using alternative data sources for micro-loans in emerging markets",
            "Computer vision model for workplace PPE compliance monitoring on manufacturing floor",
            "Recommendation engine for personalized mental health interventions via mobile app",
            "Fraud detection ensemble for real-time e-commerce transactions across regions",
            "Autonomous drone navigation model for agricultural crop monitoring under varying conditions"
        ]
    )


def setup_tracing():
    otlp = os.environ.get("OTLP_ENDPOINT")
    if otlp:
        print(f"📊 Tracing Mode: OTLP ({otlp})")
        configure_otel_providers(enable_sensitive_data=True)
        return
    ai_conn = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if ai_conn:
        print("📊 Tracing Mode: App Insights")
        configure_otel_providers(enable_sensitive_data=True)
        return
    if os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true":
        print("📊 Tracing Mode: Console")
        configure_otel_providers(enable_sensitive_data=True)
        return
    print("📊 Tracing: Disabled")


async def create_ai_governance_workflow():
    credential = AzureCliCredential()
    client = AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    governance_planner = client.as_agent(
        instructions=(
            "You are an AI Governance Planner. Derive a structured evaluation checklist: Domains, Key Questions, Risk Categories. "
            "Provide: Context Summary, Applicable Standards (ISO 42001, NIST AI RMF), Evaluation Checklist, Critical Risk Domains."
        ),
        name="governance_planner",
    )
    data_provenance = client.as_agent(
        instructions=(
            "You review data provenance & quality. Provide: Data Sources & Lineage, Labeling & QA, Quality Metrics, Drift Risks, Mitigations."),
        name="data_provenance",
    )
    fairness_bias = client.as_agent(
        instructions=(
            "You audit fairness & bias. Provide: Sensitive Attributes Considered, Potential Disparities, Metrics Needed, Bias Mitigation Strategies."),
        name="fairness_bias",
    )
    privacy_specialist = client.as_agent(
        instructions=(
            "You analyze privacy & data minimization. Provide: Personal Data Types, Minimization Approach, Anonymization/Pseudonymization, Retention & Consent, Privacy Risks."),
        name="privacy_specialist",
    )
    security_engineer = client.as_agent(
        instructions=(
            "You evaluate security & robustness. Provide: Threat Model Summary, Adversarial Risks, Supply Chain Concerns, Hardening & Monitoring Controls."),
        name="security_engineer",
    )
    regulatory_analyst = client.as_agent(
        instructions=(
            "You map to regulations. Provide: Jurisdictional Scope (EU AI Act Level, FDA/FINRA/etc.), Required Documentation, Conformance Gaps, Upcoming Regulatory Changes."),
        name="regulatory_analyst",
    )

    agents = [
        governance_planner,
        data_provenance,
        fairness_bias,
        privacy_specialist,
        security_engineer,
        regulatory_analyst,
    ]

    class GovernanceDispatcher(Executor):
        @handler
        async def dispatch(self, input_data: AIGovernanceInput, ctx: WorkflowContext[Any]) -> None:
            from agent_framework._workflows._agent_executor import AgentExecutorRequest
            global START_TIME
            START_TIME = datetime.now()
            request = AgentExecutorRequest(
                messages=[Message("user", text=input_data.description)],
                should_respond=True,
            )
            await ctx.send_message(request)

    def format_results(results) -> str:
        lines: List[str] = ["=" * 80, "🧭 AI GOVERNANCE & COMPLIANCE ASSESSMENT", "=" * 80, ""]
        section_titles = {
            "governance_planner": "🗂️ GOVERNANCE PLAN & CHECKLIST",
            "data_provenance": "📦 DATA PROVENANCE & QUALITY",
            "fairness_bias": "⚖️ FAIRNESS & BIAS",
            "privacy_specialist": "🔐 PRIVACY & MINIMIZATION",
            "security_engineer": "🛡️ SECURITY & ROBUSTNESS",
            "regulatory_analyst": "📜 REGULATORY ALIGNMENT",
        }

        collected_text = {}
        for r in results:
            msgs = getattr(r.agent_run_response, "messages", [])
            for msg in reversed(msgs):
                if getattr(msg, "author_name", None) and msg.author_name != "user":
                    name = msg.author_name
                    collected_text[name] = msg.text
                    break
        # Append each section
        for key in agents:
            nm = key.name
            if nm in collected_text:
                lines.append("─" * 80)
                lines.append(section_titles.get(nm, nm.upper()))
                lines.append("─" * 80)
                lines.append("")
                lines.append(collected_text[nm])
                lines.append("")

        # Simple derived risk register heuristic (placeholder demonstration)
        lines.append("=" * 80)
        lines.append("🗒️ RISK REGISTER (Derivation Prototype)")
        lines.append("=" * 80)
        lines.append("Risk | Impact | Likelihood | Mitigation | Owner | ETA")
        lines.append("-----|--------|-----------|-----------|-------|----")
        # Basic extraction heuristics would go here; for now static exemplars
        lines.append("Data Drift in Critical Feature | High | Medium | Monitor + Adaptive Retraining | Data Team | 90d")
        lines.append("Unmeasured Fairness Metric | Medium | High | Add disparity metrics & re-audit | AI Governance | 30d")
        lines.append("Opaque Third-Party Model Component | High | Medium | Contractual Transparency + Testing | Procurement | 45d")
        lines.append("Insufficient Adversarial Testing | Medium | Medium | Add Red-Team & Robustness Tests | Security | 60d")
        lines.append("")
        lines.append("(Note: Populate dynamically in future enhancement.)")

        lines.append("=" * 80)
        # Timing information
        elapsed_str = "N/A"
        if START_TIME:
            delta = datetime.now() - START_TIME
            elapsed_str = f"{delta.total_seconds():.2f} seconds"
        lines.append("✅ Assessment complete - validate and extend risk register.")
        lines.append("=" * 80)
        lines.append(f"⏱️ Elapsed Time: {elapsed_str}")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(__file__).parent / "workflow_outputs"
        out_dir.mkdir(exist_ok=True)
        out_file = out_dir / f"ai_governance_assessment_{ts}.txt"
        md_file = out_dir / f"ai_governance_assessment_{ts}.md"
        try:
            out_file.write_text("\n".join(lines), encoding="utf-8")
            # Build markdown variant
            md_lines: list[str] = []
            md_lines.append("# AI Governance & Compliance Assessment\n")
            md_lines.append(f"_Generated: {ts}_  ")
            md_lines.append(f"**Elapsed Time:** {elapsed_str}\n")
            for line in lines:
                if line.startswith("🧭 AI GOVERNANCE"):
                    continue
                if line.startswith("🗂️") or line.startswith("📦") or line.startswith("⚖️") or line.startswith("🔐") or line.startswith("🛡️") or line.startswith("📜"):
                    md_lines.append(f"\n## {line}\n")
                elif line.startswith("🗒️ RISK REGISTER"):
                    md_lines.append(f"\n## {line}\n")
                elif line.startswith("✅ Assessment"):
                    md_lines.append(f"\n---\n**{line}**\n")
                elif line.startswith("⏱️ Elapsed Time"):
                    continue
                elif line.startswith("=") or line.startswith("─"):
                    continue
                else:
                    md_lines.append(line)
            md_file.write_text("\n".join(md_lines), encoding="utf-8")
            print(f"💾 AI governance assessment saved: {out_file} | Markdown: {md_file} | Elapsed {elapsed_str}")
        except Exception as e:
            print(f"⚠️ Failed to save assessment: {e}")
        return "\n".join(lines)

    from agent_framework._workflows._concurrent import _CallbackAggregator

    dispatcher = GovernanceDispatcher(id="governance_dispatcher")
    aggregator = _CallbackAggregator(format_results)

    builder = WorkflowBuilder(start_executor=dispatcher)
    builder.add_fan_out_edges(dispatcher, agents)
    builder.add_fan_in_edges(agents, aggregator)
    workflow = builder.build()
    return workflow


def launch_devui():
    from agent_framework.devui import serve
    setup_tracing()
    workflow = asyncio.run(create_ai_governance_workflow())
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"

    print("=" * 70)
    print("🚀 Launching AI Governance & Model Compliance Workflow in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Governance Assessment (Fan-out/Fan-in)")
    print("✅ Participants: 6 governance/compliance specialists")
    print("✅ Web UI: http://localhost:8096")
    print("✅ API: http://localhost:8096/v1/*")
    print("✅ Entity ID: workflow_ai_governance")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    print()
    print("💡 Try scenarios:")
    print("   - Clinical decision support LLM in hospital EHR integration")
    print("   - Credit risk scoring with alternative social data")
    print("   - PPE detection computer vision for industrial safety")
    print("   - Personalized mental health intervention recommender")
    print("   - Real-time e-commerce fraud detection ensemble")
    print()
    print("⌨️  Ctrl+C to stop")
    print()

    try:
        serve(
            entities=[workflow],
            port=8096,
            auto_open=True,
            instrumentation_enabled=enable_devui_tracing,
        )
    finally:
        print("\n🛑 AI Governance workflow server stopped")


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AI governance workflow server...")

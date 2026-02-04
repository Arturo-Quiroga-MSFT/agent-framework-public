# Copyright (c) Microsoft. All rights reserved.
"""
ML Model Productionization Gate Review Workflow - DevUI Version with Tracing

Pattern: Explicit Sequential Chain (each agent visible as its own executor in DevUI).

SCENARIO:
A user describes an ML/AI product or model they want to take to production. Seven gate
review specialists evaluate in ordered sequence. Each gate consumes the full conversation
so far and appends structured findings. Final output: consolidated report + gate table.

GATES / AGENTS (Ordered):
1. Problem Framing Reviewer       -> Business objective clarity, KPIs, success criteria
2. Data Readiness Assessor        -> Data sources, quality, gaps, drift risk
3. Feature Engineering Auditor    -> Feature lineage, leakage checks, transformations
4. Model Performance Reviewer     -> Metrics vs KPIs, generalization, overfitting risks
5. Responsible AI & Fairness Gate -> Bias risks, mitigation strategies, governance flags
6. Security & Robustness Analyst  -> Threat model, adversarial / supply chain risks
7. Deployment & Monitoring Planner-> Rollout, canaries, SLOs, drift & alert strategy

OUTPUT SECTIONS:
- Executive Summary (auto heuristic)
- Per-Gate Sections (1..7)
- Consolidated Gate Table (Gate | Pass/Conditional | Key Risks | Mitigations | Owner)
- Overall Recommendation (Go / Conditional Go / No-Go)
- Elapsed Time

PREREQUISITES:
- Azure OpenAI configured (.env) + `az login`
- Environment vars for tracing (optional): OTLP_ENDPOINT / APPLICATIONINSIGHTS_CONNECTION_STRING / ENABLE_CONSOLE_TRACING / ENABLE_DEVUI_TRACING

"""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from agent_framework import ChatMessage, Executor, WorkflowBuilder, WorkflowContext, handler, Role
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import configure_otel_providers
from azure.identity import AzureCliCredential
from pydantic import BaseModel, Field

# Timing
START_TIME: datetime | None = None

# Load env
load_dotenv(Path(__file__).parent.parent / ".env")


class MLProductionInput(BaseModel):
    """User input for ML production gate review."""
    description: str = Field(
        ...,
        description="Describe the ML system: purpose, users, data sources, model type, context, constraints",
        examples=[
            "Gradient boosted model predicting customer churn for B2B SaaS platform with quarterly retention KPI",
            "Multi-modal transformer recommending personalized health coaching nudges in a mobile app",
            "Real-time fraud detection ensemble for payments using transaction + device fingerprint features",
            "Vision model for detecting defective components on assembly line under variable lighting",
            "LLM-based contextual code assistant for internal engineering teams with private repo ingestion",
            "Reinforcement learning policy optimizing warehouse picking routes on robotic fleet"
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


async def create_ml_production_workflow():
    credential = AzureCliCredential()
    client = AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Gate metadata for richer DevUI visualization & in-context hints
    GATE_METADATA = {
        "problem_framing": {
            "title": "Problem Framing / KPIs",
            "focus": "Clarify business objective, KPIs, scope, assumptions",
            "expects": "Objectives, KPIs, success criteria, scope boundaries"
        },
        "data_readiness": {
            "title": "Data Readiness",
            "focus": "Assess data sources, quality, coverage & drift risk",
            "expects": "Sources, ownership, quality gaps, drift & mitigation"
        },
        "feature_engineering": {
            "title": "Feature Engineering",
            "focus": "Review feature sets, transformations, leakage, importance",
            "expects": "Feature groups, leakage risks, missingness handling"
        },
        "model_performance": {
            "title": "Model Performance",
            "focus": "Evaluate metrics vs. KPIs, validation rigor, errors",
            "expects": "Metrics, validation scheme, error & improvement levers"
        },
        "responsible_ai": {
            "title": "Responsible AI / Fairness",
            "focus": "Identify bias risks, harm scenarios, mitigation pathways",
            "expects": "Sensitive attrs, mitigation plan, governance needs"
        },
        "security_robustness": {
            "title": "Security & Robustness",
            "focus": "Threat model, adversarial & supply chain risks",
            "expects": "Threats, integrity controls, hardening actions"
        },
        "deployment_monitoring": {
            "title": "Deployment & Monitoring",
            "focus": "Rollout strategy, observability, drift & retraining triggers",
            "expects": "Rollout, metrics, alert thresholds, ownership"
        },
    }

    # Create base agents
    problem_framing = client.as_agent(
        instructions=(
            "You are the Problem Framing Reviewer. Provide: Business Objectives, KPIs/Target Metrics, Success Criteria,\n"
            "Scope/Out-of-Scope, Assumptions, Open Clarifications. Return bullet lists where possible."
        ),
        name="problem_framing",
    )
    data_readiness = client.as_agent(
        instructions=(
            "You are the Data Readiness Assessor. Provide: Data Sources & Ownership, Volume/Freshness, Quality Issues,\n"
            "Labeling & Ground Truth, Bias / Coverage Gaps, Drift Risks, Mitigation Actions."
        ),
        name="data_readiness",
    )
    feature_engineering = client.as_agent(
        instructions=(
            "You are the Feature Engineering Auditor. Provide: Key Feature Groups, Transformations, Potential Leakage,\n"
            "Missingness Handling, Feature Importance Expectations, Risks & Mitigations."
        ),
        name="feature_engineering",
    )
    model_performance = client.as_agent(
        instructions=(
            "You are the Model Performance Reviewer. Provide: Candidate Algorithms/Architectures, Evaluation Metrics vs KPIs,\n"
            "Validation Strategy, Generalization / Overfitting Risks, Error Analysis Priorities, Improvement Levers."
        ),
        name="model_performance",
    )
    responsible_ai = client.as_agent(
        instructions=(
            "You are the Responsible AI & Fairness Gate. Provide: Sensitive Attributes (if any), Potential Harm Scenarios,\n"
            "Fairness Metrics Needed, Bias Detection Plan, Mitigation Strategies, Governance / Review Requirements."
        ),
        name="responsible_ai",
    )
    security_robustness = client.as_agent(
        instructions=(
            "You are the Security & Robustness Analyst. Provide: Threat Model (adversarial evasion/poisoning), Supply Chain Risks,\n"
            "Model/Artifact Integrity Controls, Credential/Secret Safeguards, Runtime Abuse Scenarios, Hardening Actions."
        ),
        name="security_robustness",
    )
    deployment_monitoring = client.as_agent(
        instructions=(
            "You are the Deployment & Monitoring Planner. Provide: Rollout Strategy (staging/canary/gradual), Monitoring Metrics (latency, drift, quality),\n"
            "Alert Thresholds, Retraining Triggers, On-call / Ownership, Post-launch Success Review Plan."
        ),
        name="deployment_monitoring",
    )

    ordered_agents = [
        problem_framing,
        data_readiness,
        feature_engineering,
        model_performance,
        responsible_ai,
        security_robustness,
        deployment_monitoring,
    ]

    # Generic sequential step executor
    class GateStepExecutor(Executor):
        def __init__(self, agent, label: str, **kw):
            super().__init__(**kw)
            self.agent = agent
            self.label = label

        @handler
        async def run_gate(self, conversation: list[ChatMessage], ctx: WorkflowContext[List[ChatMessage]]):
            # Insert a lightweight meta message so DevUI shows intent of this gate
            meta_key = self.agent.name
            meta = GATE_METADATA.get(meta_key, {})
            meta_msg_text = (
                f"[GATE INFO] {meta.get('title', self.label)} | Focus: {meta.get('focus','n/a')} | "
                f"Expected: {meta.get('expects','n/a')} | Prior messages: {len(conversation)}"
            )
            meta_msg = ChatMessage(Role.ASSISTANT, text=meta_msg_text, author_name=f"{meta_key}_meta")
            # Emit the meta message first so it's visible immediately in DevUI
            interim = list(conversation) + [meta_msg]
            await ctx.send_message(interim)

            # Provide meta context to the agent (so it can tailor output)
            response = await self.agent.run(interim)

            # Keep the meta message in the conversation history (so reporting sees it)
            new_messages = interim + list(response.messages)
            await ctx.send_message(new_messages)

    class MLDispatcher(Executor):
        @handler
        async def dispatch(self, input_data: MLProductionInput, ctx: WorkflowContext[List[ChatMessage]]):
            global START_TIME
            START_TIME = datetime.now()
            initial = [ChatMessage(Role.USER, text=input_data.description)]
            await ctx.send_message(initial)

    class FinalFormatter(Executor):
        @handler
        async def format_output(self, conversation: List[ChatMessage], ctx: WorkflowContext[str]):
            # Build formatted report + markdown + elapsed timing
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            elapsed_str = "N/A"
            if START_TIME:
                elapsed_str = f"{(datetime.now() - START_TIME).total_seconds():.2f} seconds"

            agent_name_map = {
                "problem_framing": "1. Problem Framing Review",
                "data_readiness": "2. Data Readiness",
                "feature_engineering": "3. Feature Engineering",
                "model_performance": "4. Model Performance",
                "responsible_ai": "5. Responsible AI & Fairness",
                "security_robustness": "6. Security & Robustness",
                "deployment_monitoring": "7. Deployment & Monitoring",
            }
            emoji_map = {
                "problem_framing": "🎯",
                "data_readiness": "📊",
                "feature_engineering": "🧱",
                "model_performance": "📈",
                "responsible_ai": "⚖️",
                "security_robustness": "🛡️",
                "deployment_monitoring": "🚀",
                "user": "👤",
            }

            lines: List[str] = ["="*90, "🤖 ML MODEL PRODUCTIONIZATION GATE REVIEW", "="*90, ""]
            # Auto executive summary heuristic: take first non-user assistant snippet
            first_agent_msg = None
            for m in conversation:
                if m.author_name and m.author_name != "user":
                    first_agent_msg = m.text[:500]
                    break
            lines.append("EXECUTIVE SUMMARY (Heuristic – refine manually):")
            lines.append(first_agent_msg or "(Not enough content to summarize yet.)")
            lines.append("")

            # Collect gate-specific sections
            for m in conversation:
                author = m.author_name if m.author_name else ("user" if m.role == Role.USER else "assistant")
                if author == "user":
                    lines.append("─"*90)
                    lines.append("👤 USER INPUT")
                    lines.append("─"*90)
                    lines.append("")
                    lines.append(m.text)
                    lines.append("")
                elif author in agent_name_map:
                    lines.append("─"*90)
                    lines.append(f"{emoji_map.get(author,'🔹')} {agent_name_map[author]}")
                    lines.append("─"*90)
                    lines.append("")
                    lines.append(m.text)
                    lines.append("")

            # Simple Gate Table heuristic (Pass assumed, upgrade manually) - extract first line of each agent's output
            lines.append("="*90)
            lines.append("📋 GATE TABLE (Heuristic)")
            lines.append("="*90)
            lines.append("Gate | Status | Key Risk (Heuristic) | Suggested Mitigation | Owner")
            lines.append("-----|--------|----------------------|----------------------|-------")
            extracted = {}
            for m in conversation:
                if m.author_name in agent_name_map:
                    first_line = m.text.strip().splitlines()[0][:60]
                    extracted[m.author_name] = first_line
            for aid in ["problem_framing","data_readiness","feature_engineering","model_performance","responsible_ai","security_robustness","deployment_monitoring"]:
                desc = extracted.get(aid, "(n/a)")
                owner = aid.replace('_','-')
                lines.append(f"{agent_name_map[aid]} | Pass | {desc} | (Refine) | {owner}")

            # Overall Recommendation (placeholder logic)
            lines.append("")
            lines.append("Overall Recommendation: Conditional Go (review fairness & drift monitoring depth).")
            lines.append("")
            lines.append(f"⏱️ Elapsed Time: {elapsed_str}")
            lines.append("")
            lines.append("="*90)
            lines.append("✅ Gate Review Complete")
            lines.append("="*90)

            out_dir = Path(__file__).parent / "workflow_outputs"
            out_dir.mkdir(exist_ok=True)
            txt_path = out_dir / f"ml_production_gate_review_{ts}.txt"
            md_path = out_dir / f"ml_production_gate_review_{ts}.md"
            try:
                txt_path.write_text("\n".join(lines), encoding="utf-8")
                # Markdown version
                md_lines: List[str] = ["# ML Model Productionization Gate Review\n", f"_Generated: {ts}_  ", f"**Elapsed Time:** {elapsed_str}\n"]
                for line in lines:
                    if line.startswith("🤖 ML MODEL"):
                        continue
                    if line.startswith("👤 USER INPUT") or line.startswith("🎯") or line.startswith("📊") or line.startswith("🧱") or line.startswith("📈") or line.startswith("⚖️") or line.startswith("🛡️") or line.startswith("🚀"):
                        md_lines.append(f"\n## {line}\n")
                    elif line.startswith("📋 GATE TABLE"):
                        md_lines.append(f"\n## {line}\n")
                    elif line.startswith("✅ Gate Review"):
                        md_lines.append(f"\n---\n**{line}**\n")
                    elif line.startswith("=") or line.startswith("─"):
                        continue
                    else:
                        md_lines.append(line)
                md_path.write_text("\n".join(md_lines), encoding="utf-8")
                print(f"💾 Gate review saved: {txt_path} | Markdown: {md_path} | Elapsed {elapsed_str}")
            except Exception as e:
                print(f"⚠️ Failed to save outputs: {e}")

            await ctx.yield_output("\n".join(lines))

    # Build workflow chain
    dispatcher = MLDispatcher(id="ml_dispatcher")
    step_execs = [
        GateStepExecutor(problem_framing, "Problem Framing", id="gate1_problem_framing"),
        GateStepExecutor(data_readiness, "Data Readiness", id="gate2_data_readiness"),
        GateStepExecutor(feature_engineering, "Feature Engineering", id="gate3_feature_engineering"),
        GateStepExecutor(model_performance, "Model Performance", id="gate4_model_performance"),
        GateStepExecutor(responsible_ai, "Responsible AI", id="gate5_responsible_ai"),
        GateStepExecutor(security_robustness, "Security & Robustness", id="gate6_security_robustness"),
        GateStepExecutor(deployment_monitoring, "Deployment & Monitoring", id="gate7_deployment_monitoring"),
    ]
    formatter = FinalFormatter(id="gate_final_formatter")

    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    # Chain steps
    prev = dispatcher
    for s in step_execs:
        builder.add_edge(prev, s)
        prev = s
    builder.add_edge(prev, formatter)

    workflow = builder.build()
    return workflow


def launch_devui():
    from agent_framework.devui import serve
    setup_tracing()
    workflow = asyncio.run(create_ml_production_workflow())
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"

    print("="*78)
    print("🚀 Launching ML Model Productionization Sequential Workflow in DevUI")
    print("="*78)
    print("✅ Workflow Type: Sequential Gate Review (7 stages)")
    print("✅ Participants: 7 gate reviewers (ordered)")
    print("✅ Web UI: http://localhost:8099")
    print("✅ API: http://localhost:8099/v1/*")
    print("✅ Entity ID: workflow_ml_prod_sequential")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    print()
    print("💡 Try scenarios:")
    print("   - Real-time fraud detection ensemble for fintech payments")
    print("   - Multi-modal health coaching recommendation system")
    print("   - Defect detection vision model on assembly line")
    print("   - LLM code assistant with private repository context")
    print("   - RL policy for robotic warehouse picking optimization")
    print()
    print("📋 Gate Order: Problem → Data → Features → Performance → Responsible AI → Security → Deployment")
    print()
    print("⌨️  Press Ctrl+C to stop the server")
    print()

    try:
        serve(
            entities=[workflow],
            port=8099,
            auto_open=True,
            instrumentation_enabled=enable_devui_tracing,
        )
    finally:
        print("\n🛑 ML gate review workflow server stopped")


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down ML gate review workflow server...")

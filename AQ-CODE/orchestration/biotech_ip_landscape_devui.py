# Copyright (c) Microsoft. All rights reserved.
"""
Biotech IP Landscape & Strategy Workflow - DevUI Version with Tracing

Pattern: Debate + Synthesis (Implemented as fan-out of analytical & adversarial agents
followed by a synthesis pass executed inside the aggregator callback).

SCENARIO:
User provides a biotech innovation (therapeutic modality, drug delivery platform,
biological tool). Multiple IP-focused analysts plus an adversarial red-team skeptic
produce a comprehensive intellectual property landscape and strategy; a synthesis
step generates recommended claim focus areas and risk mitigation.

AGENTS (Concurrent Base Layer):
1. Patent Landscape Researcher: Prior art clusters, key patents, expiration timelines
2. Freedom-to-Operate Analyst: Potential infringement zones, claim overlap risk
3. Competitive Pipeline Analyst: Active clinical/commercial competitors & differentiation
4. Regulatory Exclusivity Advisor: Data/market exclusivity, orphan designations potential
5. Differentiation Scientist (Pro): Unique technical novelty & defensibility arguments
6. Red-Team Skeptic (Con): Challenges novelty, obviousness, enablement vulnerabilities

SYNTHESIS (Performed after fan-in):
7. IP Strategy Synthesizer (virtual inside aggregator): Integrates perspectives, creates
   claim taxonomy, risk matrix, mitigation roadmap.

OUTPUT SECTIONS:
- Executive Snapshot
- Prior Art & Patent Landscape
- Freedom-to-Operate Analysis
- Competitive Pipeline & Positioning
- Regulatory Exclusivity Opportunities
- Differentiation (Pro) vs. Skeptic (Con) Summary
- Recommended Claim Taxonomy
- Risk Matrix (Risk | Impact | Likelihood | Mitigation | Priority)

PREREQUISITES & TRACING: Same approach as other workflows.
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Execution timing (set at dispatch; used in formatter)
START_TIME: datetime | None = None

from dotenv import load_dotenv
from agent_framework import ChatMessage, Executor, WorkflowBuilder, WorkflowContext, handler, Role
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import setup_observability
from azure.identity import AzureCliCredential
from pydantic import BaseModel, Field

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")


class BiotechIPInput(BaseModel):
    """Input model for biotech IP landscape analysis."""
    description: str = Field(
        ...,
        description="Describe the biotech innovation: modality, mechanism, target, formulation, delivery, differentiation",
        examples=[
            "Lipid nanoparticle delivering CRISPR base editor targeting PCSK9 for durable LDL reduction",
            "Engineered AAV capsid for CNS gene therapy with enhanced BBB penetration and reduced immunogenicity",
            "Dual-specific CAR-T targeting BCMA and GPRC5D with switchable activation domain",
            "Oral small molecule degrader for previously 'undruggable' transcription factor in oncology",
            "Self-amplifying mRNA vaccine platform with thermostable formulation for rapid pandemic response",
            "Microbiome-derived peptide therapeutic modulating gut-liver axis for NASH"
        ]
    )


def setup_tracing():
    otlp = os.environ.get("OTLP_ENDPOINT")
    if otlp:
        print(f"📊 Tracing Mode: OTLP ({otlp})")
        setup_observability(enable_sensitive_data=True, otlp_endpoint=otlp)
        return
    ai_conn = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if ai_conn:
        print("📊 Tracing Mode: App Insights")
        setup_observability(enable_sensitive_data=True, applicationinsights_connection_string=ai_conn)
        return
    if os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true":
        print("📊 Tracing Mode: Console")
        setup_observability(enable_sensitive_data=True)
        return
    print("📊 Tracing: Disabled")


async def create_biotech_ip_workflow():
    credential = AzureCliCredential()
    client = AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    patent_landscape = client.create_agent(
        instructions=(
            "You perform patent landscape research. Provide: Key Patents (numbers if plausible), Families & Expiration Windows, Prior Art Themes, White Space."
        ),
        name="patent_landscape",
    )
    fto = client.create_agent(
        instructions=(
            "You analyze freedom-to-operate. Provide: Potential Blocking Claims (describe), Overlap Risks, Need for Licensing, Design-Around Options."
        ),
        name="freedom_to_operate",
    )
    competitive = client.create_agent(
        instructions=(
            "You evaluate competitive pipeline. Provide: Active Competitors, Clinical Stages, Differentiation Gaps, Competitive Threat Assessment."
        ),
        name="competitive_pipeline",
    )
    regulatory_exclusivity = client.create_agent(
        instructions=(
            "You assess regulatory exclusivity. Provide: Data Exclusivity Paths (NCE/Biologic/Orphan), Potential Designations, Timeline Advantages, Strategic Considerations."
        ),
        name="reg_exclusivity",
    )
    differentiation = client.create_agent(
        instructions=(
            "You argue FOR novelty & defensibility. Provide: Novel Features, Technical Advantages, Unexpected Results, Claim Support Arguments."
        ),
        name="differentiation_pro",
    )
    skeptic = client.create_agent(
        instructions=(
            "You are a Red-Team Skeptic. Challenge novelty & defensibility. Provide: Obviousness Arguments, Prior Art Risk, Enablement Gaps, Potential Claim Rejections."
        ),
        name="skeptic_con",
    )

    agents = [
        patent_landscape,
        fto,
        competitive,
        regulatory_exclusivity,
        differentiation,
        skeptic,
    ]

    class IPDispatcher(Executor):
        @handler
        async def dispatch(self, input_data: BiotechIPInput, ctx: WorkflowContext[Any]) -> None:
            from agent_framework._workflows._executor import AgentExecutorRequest
            # Capture start time when first user description is dispatched
            global START_TIME
            START_TIME = datetime.now()
            request = AgentExecutorRequest(
                messages=[ChatMessage(Role.USER, text=input_data.description)],
                should_respond=True,
            )
            await ctx.send_message(request)

    def synthesize(clips: Dict[str, str]) -> str:
        # Simple heuristic synthesis for claim taxonomy & risk matrix
        claim_sections = []
        if clips.get("differentiation_pro"):
            claim_sections.append("Core Novelty Themes: " + clips["differentiation_pro"][:400])
        if clips.get("patent_landscape"):
            claim_sections.append("Landscape Highlights: " + clips["patent_landscape"][:400])
        if clips.get("freedom_to_operate"):
            claim_sections.append("FTO Constraints: " + clips["freedom_to_operate"][:400])
        claim_taxonomy = "\n".join(claim_sections) or "(Insufficient data for taxonomy)"

        risk_matrix = [
            "Risk | Impact | Likelihood | Mitigation | Priority",
            "-----|--------|-----------|-----------|---------",
            "Obviousness Challenge | High | Medium | Strengthen unexpected results evidence | High",
            "Blocking Prior Art Overlap | High | Medium | Licensing negotiation / design-around | High",
            "Enablement Question on Broad Claims | Medium | Medium | Narrow scope + add experimental examples | Medium",
            "Competitive Fast Follower | High | High | Accelerate filings + provisional strategy | High",
            "Reg Exclusivity Not Achieved | Medium | Low | Pursue orphan/fast-track designations early | Medium",
        ]
        return claim_taxonomy, "\n".join(risk_matrix)

    def format_results(results) -> str:
        lines = ["=" * 80, "🧬 BIOTECH IP LANDSCAPE & STRATEGY", "=" * 80, ""]
        section_titles = {
            "patent_landscape": "📜 PRIOR ART & PATENT LANDSCAPE",
            "freedom_to_operate": "🛑 FREEDOM-TO-OPERATE ANALYSIS",
            "competitive_pipeline": "⚔️ COMPETITIVE PIPELINE & POSITIONING",
            "reg_exclusivity": "🕒 REGULATORY EXCLUSIVITY OPPORTUNITIES",
            "differentiation_pro": "🟢 DIFFERENTIATION (PRO ARGUMENT)",
            "skeptic_con": "🔴 SKEPTIC (CON ARGUMENT)",
        }
        clips: Dict[str, str] = {}
        for r in results:
            msgs = getattr(r.agent_run_response, "messages", [])
            for msg in reversed(msgs):
                if getattr(msg, "author_name", None) and msg.author_name != "user":
                    clips[msg.author_name] = msg.text
                    break
        # Append sections
        for name, title in section_titles.items():
            if name in clips:
                lines.append("─" * 80)
                lines.append(title)
                lines.append("─" * 80)
                lines.append("")
                lines.append(clips[name])
                lines.append("")
        # Synthesis
        claim_taxonomy, risk_matrix = synthesize(clips)
        lines.append("=" * 80)
        lines.append("🧠 RECOMMENDED CLAIM TAXONOMY (SYNTHESIS)")
        lines.append("=" * 80)
        lines.append(claim_taxonomy)
        lines.append("")
        lines.append("=" * 80)
        lines.append("📊 RISK MATRIX")
        lines.append("=" * 80)
        lines.append(risk_matrix)
        lines.append("")
        # Elapsed timing
        elapsed_str = "N/A"
        if START_TIME:
            delta = datetime.now() - START_TIME
            elapsed_str = f"{delta.total_seconds():.2f} seconds"
        lines.append(f"⏱️ Elapsed Time: {elapsed_str}")
        lines.append("")
        lines.append("=" * 80)
        lines.append("✅ IP Strategy Draft Complete - Legal counsel review required.")
        lines.append("=" * 80)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(__file__).parent / "workflow_outputs"
        out_dir.mkdir(exist_ok=True)
        out_file = out_dir / f"biotech_ip_landscape_{ts}.txt"
        md_file = out_dir / f"biotech_ip_landscape_{ts}.md"
        try:
            out_file.write_text("\n".join(lines), encoding="utf-8")
            # Build markdown variant
            md_lines: list[str] = []
            md_lines.append(f"# Biotech IP Landscape & Strategy Report\n")
            md_lines.append(f"_Generated: {ts}_  ")
            md_lines.append(f"**Elapsed Time:** {elapsed_str}\n")
            # Convert sections heuristically
            for line in lines:
                if line.startswith("🧬 BIOTECH"):
                    continue
                if line.startswith("📜") or line.startswith("🛑") or line.startswith("⚔️") or line.startswith("🕒") or line.startswith("🟢") or line.startswith("🔴"):
                    md_lines.append(f"\n## {line}\n")
                elif line.startswith("🧠 RECOMMENDED"):
                    md_lines.append(f"\n## {line}\n")
                elif line.startswith("📊 RISK MATRIX"):
                    md_lines.append(f"\n## {line}\n")
                elif line.startswith("⏱️ Elapsed Time:"):
                    # already documented near top
                    continue
                elif line.startswith("✅ IP Strategy"):
                    md_lines.append(f"\n---\n**{line}**\n")
                elif line.startswith("=") or line.startswith("─"):
                    continue
                else:
                    md_lines.append(line)
            md_file.write_text("\n".join(md_lines), encoding="utf-8")
            print(f"💾 Biotech IP report saved: {out_file} | Markdown: {md_file} | Elapsed {elapsed_str}")
        except Exception as e:
            print(f"⚠️ Failed to save report: {e}")
        return "\n".join(lines)

    from agent_framework._workflows._concurrent import _CallbackAggregator

    dispatcher = IPDispatcher(id="ip_dispatcher")
    aggregator = _CallbackAggregator(format_results)

    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    builder.add_fan_out_edges(dispatcher, agents)
    builder.add_fan_in_edges(agents, aggregator)
    workflow = builder.build()
    return workflow


def launch_devui():
    from agent_framework.devui import serve
    setup_tracing()
    workflow = asyncio.run(create_biotech_ip_workflow())
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"

    print("=" * 70)
    print("🚀 Launching Biotech IP Landscape & Strategy Workflow in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Debate + Synthesis (Fan-out/Fan-in + Aggregated Synthesis)")
    print("✅ Participants: 6 analytical + synthesized strategy output")
    print("✅ Web UI: http://localhost:8098")
    print("✅ API: http://localhost:8098/v1/*")
    print("✅ Entity ID: workflow_biotech_ip")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    print()
    print("💡 Try scenarios:")
    print("   - LNP CRISPR base editor for PCSK9 LDL reduction")
    print("   - Engineered AAV capsid for CNS delivery")
    print("   - Dual-specific CAR-T with switchable activation")
    print("   - Oral small molecule degrader for transcription factor")
    print("   - Thermostable self-amplifying mRNA vaccine platform")
    print()
    print("⌨️  Ctrl+C to stop")
    print()

    try:
        serve(
            entities=[workflow],
            port=8098,
            auto_open=True,
            tracing_enabled=enable_devui_tracing,
        )
    finally:
        print("\n🛑 Biotech IP workflow server stopped")


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down biotech IP workflow server...")

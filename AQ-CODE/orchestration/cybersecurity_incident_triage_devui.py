# Copyright (c) Microsoft. All rights reserved.
"""
Cybersecurity Incident Triage Workflow - DevUI Version with Tracing

Pattern: Fan-out / Fan-in (Concurrent) with structured formatter.

SCENARIO:
User supplies a suspected cybersecurity incident description (e.g., ransomware on servers, suspicious outbound traffic, potential data exfiltration). Six specialized responders analyze concurrently and produce an actionable consolidated triage report.

AGENTS (Concurrent):
1. Threat Intelligence Analyst: Map indicators to known campaigns (MITRE ATT&CK), attribution hypotheses
2. Network Forensics Specialist: Traffic anomalies, lateral movement, C2 patterns
3. Endpoint Analyst: Host-based artifacts, persistence, malicious processes
4. Malware Analyst: Behavioral + static traits (speculative if sample not present)
5. Risk & Compliance Officer: Regulatory/reporting implications (HIPAA, PCI, GDPR)
6. Containment & Remediation Lead: Immediate actions, eradication, recovery priorities

OUTPUT STRUCTURE:
- Executive Summary
- Indicators & TTPs
- Affected Assets & Spread Hypothesis
- Regulatory / Reporting Considerations
- Prioritized Containment & Remediation Plan (0-6h, 6-24h, 1-7d)
- Confidence & Gaps

PREREQUISITES:
- Azure OpenAI setup (.env)
- Azure CLI auth (az login)

TRACING: Same environment variable behavior as other workflows.
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# Execution timing
START_TIME: datetime | None = None

from dotenv import load_dotenv
from agent_framework import Message, Executor, WorkflowBuilder, WorkflowContext, handler, AgentExecutorRequest, AgentExecutorResponse
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import configure_otel_providers
from azure.identity import AzureCliCredential
from pydantic import BaseModel, Field

# Load env
load_dotenv(Path(__file__).parent.parent / ".env")


class CyberIncidentInput(BaseModel):
    """User input model for cybersecurity incident triage."""
    description: str = Field(
        ...,
        description="Describe the suspected cybersecurity incident: systems, symptoms, timelines, observed indicators",
        examples=[
            "Ransomware detected on 3 Windows file servers; file extensions changed; note demanding Bitcoin; odd outbound traffic to 185.x.x.x",
            "Multiple phishing emails led to credential reuse; abnormal Azure AD sign-ins from foreign regions; possible mailbox rules added",
            "Egress spike from database subnet at 02:00 UTC; suspected data exfiltration via TLS to unknown domain; IDS flagged uncommon JA3 hash",
            "Unmanaged crypto-mining processes found on Kubernetes worker nodes; elevated CPU usage; suspicious container images pulled",
            "Industrial control network showing intermittent PLC command anomalies; potential unauthorized ladder logic changes",
            "SIEM alerts for PowerShell execution + LSASS access on two domain controllers; potential privilege escalation in progress"
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


async def create_cybersecurity_workflow():
    credential = AzureCliCredential()
    client = AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    threat_intel = client.as_agent(
        instructions=(
            "You are a Threat Intelligence Analyst. Map provided indicators to campaigns and MITRE ATT&CK techniques. "
            "Output sections: Indicators Observed, Likely TTPs (T#), Possible Attribution (confidence), Intelligence Gaps."
        ),
        name="threat_intel",
    )
    network_forensics = client.as_agent(
        instructions=(
            "You are a Network Forensics Specialist. Analyze potential lateral movement, beaconing, C2 channels, exfil paths. "
            "Output: Suspicious Flows, Protocol Anomalies, Lateral Movement Hypotheses, Recommended Network Containment."
        ),
        name="network_forensics",
    )
    endpoint_analyst = client.as_agent(
        instructions=(
            "You are an Endpoint / EDR Analyst. Focus on host artifacts: processes, persistence, registry/services, privilege escalation. "
            "Output: Key Host Artifacts, Persistence Mechanisms, Priv Esc Attempts, Host Triage Recommendations."
        ),
        name="endpoint_analyst",
    )
    malware_analyst = client.as_agent(
        instructions=(
            "You are a Malware Analyst. Even without a sample, infer possible behavior patterns. "
            "Output: Behavior Hypotheses, Encryption/Exfil Traits, Evasion Techniques, Needed Forensic Artifacts."
        ),
        name="malware_analyst",
    )
    compliance = client.as_agent(
        instructions=(
            "You are a Risk & Compliance Officer. Identify legal/regulatory impact: breach notification triggers, data classifications, jurisdictional concerns. "
            "Output: Regulatory Considerations, Reporting Deadlines, Data Categories Affected, Compliance Risks."
        ),
        name="compliance",
    )
    remediation = client.as_agent(
        instructions=(
            "You are the Containment & Remediation Lead. Prioritize actions by time horizon. "
            "Output: 0-6h Actions, 6-24h Actions, 1-7d Actions, Longer-Term Hardening, Risk Reduction Rationale."
        ),
        name="remediation",
    )

    agents = [
        threat_intel,
        network_forensics,
        endpoint_analyst,
        malware_analyst,
        compliance,
        remediation,
    ]

    class IncidentDispatcher(Executor):
        @handler
        async def dispatch(self, input_data: CyberIncidentInput, ctx: WorkflowContext) -> None:
            global START_TIME
            START_TIME = datetime.now()
            request = AgentExecutorRequest(
                messages=[Message("user", text=input_data.description)],
                should_respond=True,
            )
            await ctx.send_message(request)

    def format_results(results) -> str:
        lines = ["=" * 80, "🛡️ CYBERSECURITY INCIDENT TRIAGE REPORT", "=" * 80, ""]
        section_map = {
            "threat_intel": ("🔍 THREAT INTELLIGENCE",),
            "network_forensics": ("🌐 NETWORK FORENSICS",),
            "endpoint_analyst": ("💻 ENDPOINT ANALYSIS",),
            "malware_analyst": ("🧬 MALWARE BEHAVIOR",),
            "compliance": ("📋 RISK & COMPLIANCE",),
            "remediation": ("🚑 CONTAINMENT & REMEDIATION",),
        }
        # Collect last assistant message per result
        for r in results:
            msgs = getattr(r.agent_run_response, "messages", [])
            for msg in reversed(msgs):
                if getattr(msg, "author_name", None) and msg.author_name != "user":
                    tag = msg.author_name
                    title = section_map.get(tag, (tag.upper(),))[0]
                    lines.append("─" * 80)
                    lines.append(title)
                    lines.append("─" * 80)
                    lines.append("")
                    lines.append(msg.text)
                    lines.append("")
                    break
        # Basic executive summary heuristic (could be improved)
        lines.insert(3, "(Automated Summary: Review each section for validation.)")
        # Timing
        elapsed_str = "N/A"
        if START_TIME:
            delta = datetime.now() - START_TIME
            elapsed_str = f"{delta.total_seconds():.2f} seconds"
        lines.append("=" * 80)
        lines.append("✅ Triage complete - validate before execution.")
        lines.append("=" * 80)
        lines.append(f"⏱️ Elapsed Time: {elapsed_str}")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(__file__).parent / "workflow_outputs"
        out_dir.mkdir(exist_ok=True)
        out_file = out_dir / f"cyber_incident_triage_{ts}.txt"
        md_file = out_dir / f"cyber_incident_triage_{ts}.md"
        try:
            out_file.write_text("\n".join(lines), encoding="utf-8")
            # Build markdown variant
            md_lines: list[str] = []
            md_lines.append(f"# Cybersecurity Incident Triage Report\n")
            md_lines.append(f"_Generated: {ts}_  ")
            md_lines.append(f"**Elapsed Time:** {elapsed_str}\n")
            for line in lines:
                if line.startswith("🛡️ "):
                    continue
                if line.startswith("🔍") or line.startswith("🌐") or line.startswith("💻") or line.startswith("🧬") or line.startswith("📋") or line.startswith("🚑"):
                    md_lines.append(f"\n## {line}\n")
                elif line.startswith("✅ Triage"):
                    md_lines.append(f"\n---\n**{line}**\n")
                elif line.startswith("⏱️ Elapsed Time"):
                    continue
                elif line.startswith("=") or line.startswith("─"):
                    continue
                else:
                    md_lines.append(line)
            md_file.write_text("\n".join(md_lines), encoding="utf-8")
            print(f"💾 Report saved: {out_file} | Markdown: {md_file} | Elapsed {elapsed_str}")
        except Exception as e:
            print(f"⚠️ Failed to save report: {e}")
        return "\n".join(lines)

    class IncidentAggregator(Executor):
        """Aggregator that formats results from all cybersecurity agents."""
        
        @handler
        async def aggregate(self, results: list[AgentExecutorResponse], ctx: WorkflowContext) -> None:
            """Aggregate results from all agents and format output.
            
            Args:
                results: List of AgentExecutorResponse objects from agents
                ctx: WorkflowContext for yielding output
            """
            formatted_output = format_results(results)
            await ctx.yield_output(formatted_output)

    dispatcher = IncidentDispatcher(id="incident_dispatcher")
    aggregator = IncidentAggregator(id="incident_aggregator")

    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    builder.add_fan_out_edges(dispatcher, agents)
    builder.add_fan_in_edges(agents, aggregator)
    workflow = builder.build()
    return workflow


def launch_devui():
    from agent_framework.devui import serve
    setup_tracing()
    workflow = asyncio.run(create_cybersecurity_workflow())
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"

    print("=" * 70)
    print("🚀 Launching Cybersecurity Incident Triage Workflow in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Fan-out/Fan-in (Concurrent Incident Analysis)")
    print("✅ Participants: 6 cybersecurity specialists")
    print("✅ Web UI: http://localhost:8095")
    print("✅ API: http://localhost:8095/v1/*")
    print("✅ Entity ID: workflow_cyber_incident")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    print()
    print("💡 Try scenarios:")
    print("   - Ransomware lateral movement in mixed Windows environment")
    print("   - Suspicious exfiltration via unusual TLS JA3 fingerprint")
    print("   - Phishing-led credential abuse across cloud admin roles")
    print("   - Crypto-mining containers appearing in prod cluster")
    print("   - Possible PLC tampering in industrial control network")
    print()
    print("⌨️  Ctrl+C to stop")
    print()

    try:
        serve(
            entities=[workflow],
            port=8095,
            auto_open=True,
            instrumentation_enabled=enable_devui_tracing,
        )
    finally:
        print("\n🛑 Cybersecurity workflow server stopped")


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down cybersecurity workflow server...")

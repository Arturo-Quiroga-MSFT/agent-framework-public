# Copyright (c) Microsoft. All rights reserved.

"""
Clinical Trial Management Workflow - DevUI Version with Tracing

This workflow creates a specialized team of 7 clinical trial experts to analyze
pharmaceutical trials, medical device studies, and clinical research programs.

The workflow uses a fan-out/fan-in pattern where:
- User describes a clinical trial or study
- Input is dispatched to all 7 specialized agents concurrently
- Each agent provides domain-specific analysis
- Results are aggregated and formatted with clear sections

CLINICAL TRIAL AGENTS:
- Clinical Research: Protocol design, endpoints, statistical power
- Site Operations: Patient recruitment, site selection, monitoring
- Regulatory Affairs: FDA submissions, IRB, adverse event reporting
- Drug Development: Dosing, pharmacokinetics, formulation
- Clinical Finance: Budget, CRO contracts, patient compensation
- Biostatistics & Data: Data management, interim analysis, endpoints
- Patient Advocacy: Informed consent, diversity, patient experience

PREREQUISITES:
- Azure OpenAI access configured via .env file in workflows directory
- Azure CLI authentication: Run 'az login'

TRACING OPTIONS:
1. Console Tracing: Set ENABLE_CONSOLE_TRACING=true (simplest)
2. Azure AI Tracing: Set ENABLE_AZURE_AI_TRACING=true (requires Application Insights)
3. OTLP Tracing: Set OTLP_ENDPOINT (e.g., http://localhost:4317 for Jaeger/Zipkin)
4. DevUI Tracing: Set ENABLE_DEVUI_TRACING=true (view in DevUI interface)
"""

import asyncio
import os
from contextlib import AsyncExitStack
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from agent_framework import ChatMessage, Executor, WorkflowBuilder, WorkflowContext, handler, Role, AgentExecutorRequest, AgentExecutorResponse
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import get_tracer, configure_otel_providers
from azure.identity import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from pydantic import BaseModel, Field

# Load environment variables from workflows/.env file
load_dotenv(Path(__file__).parent.parent / ".env")


class ClinicalTrialInput(BaseModel):
    """Input model for clinical trial analysis."""
    
    description: str = Field(
        ...,
        description="Describe the clinical trial, drug candidate, medical device study, or therapeutic approach you want to evaluate",
        examples=[
            "Phase 3 trial for novel GLP-1 agonist for obesity management in adolescents aged 12-17",
            "Phase 2 oncology trial testing CAR-T cell therapy for relapsed/refractory multiple myeloma",
            "Medical device trial for AI-powered robotic surgery system for minimally invasive cardiac procedures",
            "Phase 1 dose-escalation study of oral small molecule KRAS inhibitor for solid tumors",
            "Multi-center trial for digital therapeutic app treating moderate-to-severe depression",
            "Rare disease trial for enzyme replacement therapy in pediatric Gaucher disease patients",
            "Adaptive platform trial for combination immunotherapy in advanced melanoma",
            "Decentralized trial using wearables to monitor Parkinson's disease progression and treatment response"
        ]
    )


def format_clinical_trial_results(results, start_time: datetime | None = None) -> str:
    """Format clinical trial agent outputs for DevUI display and save to files.

    Adds elapsed time information (if ``start_time`` provided) and writes both a
    ``.txt`` and ``.md`` artifact to ``workflow_outputs``.

    Args:
        results: List of AgentExecutorResponse objects from concurrent agents.
        start_time: Optional datetime captured when the workflow execution for this
            user request started. If provided, elapsed time will be computed and
            appended to the artifacts.

    Returns:
        Formatted string with all agent responses (plain text flavor) used as the
        aggregator output.
    """
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("🔬 COMPREHENSIVE CLINICAL TRIAL ANALYSIS")
    output_lines.append("=" * 80)
    output_lines.append("")
    if start_time is not None:
        elapsed: timedelta = datetime.now() - start_time
        human_elapsed = str(elapsed).split(".")[0]  # trim microseconds for readability
        output_lines.append(f"⏱️ Elapsed Time: {human_elapsed}")
        output_lines.append("")
    
    # Process each agent's response
    for result in results:
        # Get the agent's messages
        messages = getattr(result.agent_run_response, "messages", [])
        
        # Find the final assistant message
        for msg in reversed(messages):
            if hasattr(msg, "author_name") and msg.author_name and msg.author_name != "user":
                agent_name = msg.author_name.upper()
                
                # Add emoji based on agent type
                emoji = {
                    "CLINICAL_RESEARCH": "🔬",
                    "SITE_OPERATIONS": "🏥",
                    "REGULATORY_AFFAIRS": "📋",
                    "DRUG_DEVELOPMENT": "💊",
                    "CLINICAL_FINANCE": "💰",
                    "BIOSTATISTICS": "📊",
                    "PATIENT_ADVOCACY": "🤝"
                }.get(agent_name, "🧪")
                
                # Readable names
                display_name = {
                    "CLINICAL_RESEARCH": "CLINICAL RESEARCH & PROTOCOL DESIGN",
                    "SITE_OPERATIONS": "SITE OPERATIONS & PATIENT RECRUITMENT",
                    "REGULATORY_AFFAIRS": "REGULATORY AFFAIRS & COMPLIANCE",
                    "DRUG_DEVELOPMENT": "DRUG DEVELOPMENT & PHARMACOLOGY",
                    "CLINICAL_FINANCE": "CLINICAL TRIAL FINANCE & BUDGETING",
                    "BIOSTATISTICS": "BIOSTATISTICS & DATA MANAGEMENT",
                    "PATIENT_ADVOCACY": "PATIENT ADVOCACY & ENGAGEMENT"
                }.get(agent_name, agent_name)
                
                output_lines.append("─" * 80)
                output_lines.append(f"{emoji} {display_name}")
                output_lines.append("─" * 80)
                output_lines.append("")
                output_lines.append(msg.text)
                output_lines.append("")
                break  # Only use the final message
    
    output_lines.append("=" * 80)
    output_lines.append("✅ Clinical Trial Analysis Complete - All perspectives reviewed")
    if start_time is not None:
        elapsed_final: timedelta = datetime.now() - start_time
        human_elapsed_final = str(elapsed_final).split(".")[0]
        output_lines.append(f"⏱️ Total Elapsed Time: {human_elapsed_final}")
    output_lines.append("=" * 80)
    
    formatted_output = "\n".join(output_lines)
    
    # Save to files with timestamp (text + markdown)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file_txt = output_dir / f"clinical_trial_analysis_{timestamp}.txt"
    output_file_md = output_dir / f"clinical_trial_analysis_{timestamp}.md"
    
    try:
        with open(output_file_txt, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        # Basic markdown variant (re-use but add markdown headings)
        md_lines = [
            "# Comprehensive Clinical Trial Analysis",
            "",
            f"_Generated_: {datetime.now().isoformat(timespec='seconds')}",
        ]
        if start_time is not None:
            md_lines.append(f"_Elapsed Time_: {human_elapsed_final}")
        md_lines.append("")
        # The plain formatted output already has separators; we preserve below under details section
        md_lines.append("## Detailed Multi-Agent Output")
        md_lines.append("\n" + formatted_output)
        with open(output_file_md, "w", encoding="utf-8") as fmd:
            fmd.write("\n".join(md_lines))
        print(f"\n💾 Clinical trial analysis saved to: {output_file_txt}")
        print(f"💾 Markdown version saved to: {output_file_md}")
    except Exception as e:
        print(f"\n⚠️ Failed to save output to file: {e}")
    
    return formatted_output


def setup_tracing():
    """Set up tracing based on environment variables.
    
    Priority order:
    1. OTLP endpoint (OTLP_ENDPOINT)
    2. Application Insights (APPLICATIONINSIGHTS_CONNECTION_STRING)
    3. Console tracing (ENABLE_CONSOLE_TRACING=true)
    """
    # Check for OTLP endpoint
    otlp_endpoint = os.environ.get("OTLP_ENDPOINT")
    if otlp_endpoint:
        print(f"📊 Tracing Mode: OTLP Endpoint ({otlp_endpoint})")
        print("   Make sure you have an OTLP receiver running (e.g., Jaeger, Zipkin)")
        configure_otel_providers(enable_sensitive_data=True)
        return
    
    # Check for Application Insights connection string
    app_insights_conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn_str:
        print("📊 Tracing Mode: Application Insights (Direct)")
        configure_otel_providers(enable_sensitive_data=True)
        return
    
    # Check for console tracing
    if os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true":
        print("📊 Tracing Mode: Console Output")
        print("   Traces will be printed to the console")
        configure_otel_providers(enable_sensitive_data=True)
        return
    
    print("📊 Tracing: Disabled")
    print("   To enable tracing, set one of:")
    print("   - OTLP_ENDPOINT=http://localhost:4317 (requires OTLP receiver)")
    print("   - APPLICATIONINSIGHTS_CONNECTION_STRING=<your-connection-string>")
    print("   - ENABLE_CONSOLE_TRACING=true (console output)")


async def create_clinical_trial_workflow():
    """Create and return a clinical trial management workflow for DevUI."""
    # Create async context stack for managing resources
    stack = AsyncExitStack()
    
    # Initialize async credential (no context manager needed)
    credential = AzureCliCredential()
    
    # Initialize Azure OpenAI client
    chat_client = AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )
    
    # Create seven specialized clinical trial agents
    clinical_research = chat_client.as_agent(
        instructions=(
            "You're a clinical research scientist and protocol designer with expertise in clinical trial methodology. "
            "Analyze trial design, endpoints, inclusion/exclusion criteria, and scientific validity. "
            "Consider: primary and secondary endpoints, study population, randomization, blinding, "
            "sample size and statistical power, comparator selection, visit schedule, "
            "outcome measures (efficacy and safety), trial phases (I/II/III/IV), "
            "adaptive designs, biomarkers, and scientific rationale. "
            "Provide rigorous but practical protocol recommendations."
        ),
        name="clinical_research",
    )

    site_operations = chat_client.as_agent(
        instructions=(
            "You're a clinical trial site operations and patient recruitment expert. "
            "Analyze site selection, patient enrollment strategies, and operational logistics. "
            "Consider: site selection criteria, investigator qualifications, patient recruitment strategies, "
            "retention plans, site initiation and monitoring, protocol deviations, "
            "source data verification, patient screening and enrollment timelines, "
            "geographic distribution, centralized vs local labs, home health visits, "
            "and operational feasibility. Focus on enrollment success and site performance."
        ),
        name="site_operations",
    )

    regulatory_affairs = chat_client.as_agent(
        instructions=(
            "You're a regulatory affairs specialist with expertise in FDA, EMA, and global clinical trial regulations. "
            "Analyze regulatory pathways, submission requirements, and compliance obligations. "
            "Consider: IND/CTA applications, IDE for devices, IRB/EC submissions and approvals, "
            "informed consent forms, investigator brochure, protocol amendments, "
            "adverse event reporting (SAEs, SUSARs), DSMB requirements, "
            "21 CFR Part 11 compliance, ICH-GCP guidelines, pediatric plans (PREA), "
            "orphan drug designations, and post-market commitments. Provide clear regulatory roadmaps."
        ),
        name="regulatory_affairs",
    )
    
    drug_development = chat_client.as_agent(
        instructions=(
            "You're a drug development and pharmacology expert specializing in PK/PD and formulation. "
            "Analyze dosing strategy, pharmacokinetics, safety profile, and drug-specific considerations. "
            "Consider: dose selection and escalation, PK/PD modeling, ADME properties, "
            "drug-drug interactions, formulation and stability, route of administration, "
            "therapeutic index, mechanism of action, preclinical data translation, "
            "bioavailability, half-life, metabolism, combination therapy considerations, "
            "and CMC (chemistry, manufacturing, controls). Focus on safety and efficacy optimization."
        ),
        name="drug_development",
    )
    
    clinical_finance = chat_client.as_agent(
        instructions=(
            "You're a clinical trial finance and budget expert. "
            "Analyze trial costs, CRO contracts, patient compensation, and financial feasibility. "
            "Consider: per-patient costs, site budgets, startup costs, CRO vs in-house, "
            "patient stipends and travel reimbursement, investigator fees, "
            "lab and imaging costs, insurance and indemnification, "
            "budget contingencies, milestone payments, risk-sharing arrangements, "
            "cost per completed patient, burn rate, and fundraising needs. "
            "Provide realistic budget estimates and cost optimization strategies."
        ),
        name="clinical_finance",
    )
    
    biostatistics = chat_client.as_agent(
        instructions=(
            "You're a biostatistician and clinical data management expert. "
            "Analyze statistical design, sample size, data management, and analysis plans. "
            "Consider: statistical analysis plan (SAP), sample size justification, "
            "power calculations, interim analysis, futility and efficacy stopping rules, "
            "multiple comparisons adjustments, missing data handling, ITT vs PP populations, "
            "subgroup analyses, sensitivity analyses, Bayesian vs frequentist approaches, "
            "EDC system requirements, data quality and monitoring, "
            "and publication-ready analysis. Focus on statistical rigor and data integrity."
        ),
        name="biostatistics",
    )
    
    patient_advocacy = chat_client.as_agent(
        instructions=(
            "You're a patient advocacy and engagement expert focused on patient-centered trial design. "
            "Analyze informed consent, patient burden, diversity, and patient experience. "
            "Consider: informed consent clarity and comprehension, patient burden (visits, procedures), "
            "trial diversity and inclusion (racial, ethnic, age, gender), health equity, "
            "patient-reported outcomes (PROs), quality of life assessments, "
            "patient advisory boards, community engagement, patient compensation adequacy, "
            "accessibility accommodations, language translation, health literacy, "
            "and retention strategies. Prioritize patient welfare and meaningful engagement."
        ),
        name="patient_advocacy",
    )
    
        # Build the clinical trial workflow with structured input handling
    # Create custom dispatcher that handles ClinicalTrialInput
    class ClinicalTrialDispatcher(Executor):
        """Dispatcher that extracts description from ClinicalTrialInput and forwards to agents."""
        
        @handler
        async def dispatch(self, input_data: ClinicalTrialInput, ctx: WorkflowContext) -> None:
            """Extract description and send to all clinical trial agents.
            
            Args:
                input_data: ClinicalTrialInput with description field
                ctx: WorkflowContext for dispatching to agents
            """
            request = AgentExecutorRequest(
                messages=[ChatMessage(Role.USER, text=input_data.description)],
                should_respond=True
            )
            await ctx.send_message(request)
    
    # Build workflow with custom components
    dispatcher = ClinicalTrialDispatcher(id="clinical_trial_dispatcher")
    # Capture start time to compute elapsed duration for this workflow execution
    workflow_start_time = datetime.now()

    # Create custom aggregator executor
    class ClinicalTrialAggregator(Executor):
        """Aggregator that formats results from all clinical trial agents."""
        
        @handler
        async def aggregate(self, results: list[AgentExecutorResponse], ctx: WorkflowContext) -> None:
            """Aggregate results from all agents and format output.
            
            Args:
                results: List of AgentExecutorResponse objects from agents
                ctx: WorkflowContext for yielding output
            """
            formatted_output = format_clinical_trial_results(results, workflow_start_time)
            await ctx.yield_output(formatted_output)
    
    aggregator = ClinicalTrialAggregator(id="clinical_trial_aggregator")
    
    # Build workflow with custom components
    dispatcher = ClinicalTrialDispatcher(id="clinical_trial_dispatcher")
    # Capture start time to compute elapsed duration for this workflow execution
    workflow_start_time = datetime.now()

    def aggregator_func(results):  # closure to include timing
        return format_clinical_trial_results(results, start_time=workflow_start_time)
    
    # Use WorkflowBuilder to create the complete workflow
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    
    # Add all clinical trial agent participants
    agents = [
        clinical_research,
        site_operations,
        regulatory_affairs,
        drug_development,
        clinical_finance,
        biostatistics,
        patient_advocacy
    ]
    builder.add_fan_out_edges(dispatcher, agents)
    
    # Add aggregator
    builder.add_fan_in_edges(agents, aggregator)
    
    workflow = builder.build()
    
    # Store the stack for cleanup
    workflow._devui_stack = stack
    
    return workflow


def launch_devui():
    """Launch the DevUI interface with the clinical trial workflow."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Create the workflow asynchronously
    workflow = asyncio.run(create_clinical_trial_workflow())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Clinical Trial Management Workflow in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Clinical Trial Analysis (Fan-out/Fan-in)")
    print("✅ Participants: 7 specialized clinical trial experts")
    print("✅ Web UI: http://localhost:8095")
    print("✅ API: http://localhost:8095/v1/*")
    print("✅ Entity ID: workflow_clinical_trial")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    print("=" * 70)
    print()
    print("💡 Try these clinical trial scenarios in the DevUI:")
    print()
    print("💊 Pharmaceutical Trials:")
    print("   - Phase 3 GLP-1 agonist for adolescent obesity")
    print("   - Phase 2 CAR-T therapy for multiple myeloma")
    print("   - Phase 1 KRAS inhibitor dose-escalation study")
    print()
    print("🏥 Medical Device Studies:")
    print("   - AI-powered robotic surgery system trial")
    print("   - Wearable continuous glucose monitoring device")
    print("   - Implantable cardiac defibrillator safety study")
    print()
    print("🧬 Specialized Trials:")
    print("   - Rare disease enzyme replacement therapy (pediatric)")
    print("   - Digital therapeutic app for depression")
    print("   - Adaptive platform trial for combination immunotherapy")
    print("   - Decentralized trial with wearables for Parkinson's")
    print()
    print("⚡ Each query will be analyzed by 7 clinical trial experts:")
    print("   • Clinical Research: Protocol design, endpoints, statistical power")
    print("   • Site Operations: Patient recruitment, site selection, monitoring")
    print("   • Regulatory Affairs: FDA/EMA submissions, IRB, adverse events")
    print("   • Drug Development: Dosing, PK/PD, formulation, safety profile")
    print("   • Clinical Finance: Budget, CRO contracts, cost optimization")
    print("   • Biostatistics: Sample size, data management, analysis plan")
    print("   • Patient Advocacy: Informed consent, diversity, patient burden")
    print()
    print("⌨️  Press Ctrl+C to stop the server")
    print()
    
    # Launch the DevUI server
    try:
        serve(
            entities=[workflow],
            port=8095,
            auto_open=True,
            instrumentation_enabled=enable_devui_tracing,
        )
    finally:
        # Clean up resources
        if hasattr(workflow, "_devui_stack"):
            asyncio.run(workflow._devui_stack.aclose())


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down clinical trial workflow server...")

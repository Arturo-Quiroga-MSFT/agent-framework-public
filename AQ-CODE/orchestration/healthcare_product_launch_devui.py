# Copyright (c) Microsoft. All rights reserved.

"""
Healthcare Product Launch Workflow - DevUI Version with Tracing

This workflow creates a specialized team of 5 healthcare domain experts to analyze
medical devices, health apps, telehealth services, or other healthcare products.

The workflow uses a fan-out/fan-in pattern where:
- User describes a healthcare product or service
- Input is dispatched to all 5 specialized agents concurrently
- Each agent provides domain-specific analysis
- Results are aggregated and formatted with clear sections

HEALTHCARE AGENTS:
- Clinical Researcher: Evidence-based medicine, clinical trials, efficacy
- Healthcare Compliance: HIPAA, FDA, medical regulations, patient privacy
- Healthcare Economics: Reimbursement, insurance coverage, healthcare ROI
- Patient Experience: User journey, accessibility, patient safety, usability
- Medical Data Security: PHI protection, cybersecurity, data governance

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
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from agent_framework import ChatMessage, Executor, WorkflowBuilder, WorkflowContext, handler, Role
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import get_tracer, setup_observability
from azure.identity import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from pydantic import BaseModel, Field

# Load environment variables from workflows/.env file
load_dotenv(Path(__file__).parent.parent / ".env")


class HealthcareProductInput(BaseModel):
    """Input model for healthcare product launch analysis."""
    
    description: str = Field(
        ...,
        description="Describe the healthcare product, medical device, health app, or healthcare service you want to launch",
        examples=[
            "AI-powered diagnostic tool for early detection of diabetic retinopathy using smartphone cameras",
            "Wearable cardiac monitoring device with real-time alerts for atrial fibrillation",
            "Telehealth platform connecting rural patients with specialist physicians",
            "Mental health app with AI-powered CBT therapy and crisis intervention",
            "Remote patient monitoring system for chronic disease management (diabetes, hypertension)",
            "Medical imaging AI assistant for radiologists to detect lung nodules",
            "Medication adherence app with smart pill dispenser integration",
            "Virtual physical therapy platform with motion tracking technology"
        ]
    )


def format_healthcare_results(results) -> str:
    """Format healthcare agent outputs for DevUI display and save to file.
    
    Args:
        results: List of AgentExecutorResponse objects from concurrent agents
        
    Returns:
        Formatted string with all agent responses
    """
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("🏥 COMPREHENSIVE HEALTHCARE PRODUCT ANALYSIS")
    output_lines.append("=" * 80)
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
                    "CLINICAL_RESEARCHER": "🔬",
                    "COMPLIANCE_OFFICER": "📋",
                    "ECONOMICS_ANALYST": "💰",
                    "PATIENT_EXPERIENCE": "👥",
                    "DATA_SECURITY": "🔐"
                }.get(agent_name, "🏥")
                
                # Readable names
                display_name = {
                    "CLINICAL_RESEARCHER": "CLINICAL RESEARCH & EVIDENCE",
                    "COMPLIANCE_OFFICER": "HEALTHCARE COMPLIANCE & REGULATORY",
                    "ECONOMICS_ANALYST": "HEALTHCARE ECONOMICS & REIMBURSEMENT",
                    "PATIENT_EXPERIENCE": "PATIENT EXPERIENCE & SAFETY",
                    "DATA_SECURITY": "MEDICAL DATA SECURITY & PRIVACY"
                }.get(agent_name, agent_name)
                
                output_lines.append("─" * 80)
                output_lines.append(f"{emoji} {display_name}")
                output_lines.append("─" * 80)
                output_lines.append("")
                output_lines.append(msg.text)
                output_lines.append("")
                break  # Only use the final message
    
    output_lines.append("=" * 80)
    output_lines.append("✅ Healthcare Analysis Complete - All perspectives reviewed")
    output_lines.append("=" * 80)
    
    formatted_output = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"healthcare_analysis_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"\n💾 Healthcare analysis saved to: {output_file}")
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
        setup_observability(
            enable_sensitive_data=True,
            otlp_endpoint=otlp_endpoint,
        )
        return
    
    # Check for Application Insights connection string
    app_insights_conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn_str:
        print("📊 Tracing Mode: Application Insights (Direct)")
        setup_observability(
            enable_sensitive_data=True,
            applicationinsights_connection_string=app_insights_conn_str,
        )
        return
    
    # Check for console tracing
    if os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true":
        print("📊 Tracing Mode: Console Output")
        print("   Traces will be printed to the console")
        setup_observability(enable_sensitive_data=True)
        return
    
    print("📊 Tracing: Disabled")
    print("   To enable tracing, set one of:")
    print("   - OTLP_ENDPOINT=http://localhost:4317 (requires OTLP receiver)")
    print("   - APPLICATIONINSIGHTS_CONNECTION_STRING=<your-connection-string>")
    print("   - ENABLE_CONSOLE_TRACING=true (console output)")


async def create_healthcare_workflow():
    """Create and return a healthcare product launch workflow for DevUI."""
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
    
    # Create five specialized healthcare agents
    clinical_researcher = chat_client.create_agent(
        instructions=(
            "You're a clinical researcher and medical scientist specializing in evidence-based medicine. "
            "Analyze the clinical validity, scientific evidence, and medical efficacy of healthcare products. "
            "Consider: clinical trial requirements, evidence standards, efficacy metrics, patient outcomes, "
            "safety profiles, adverse events, contraindications, and peer-reviewed research needs. "
            "Evaluate the strength of clinical evidence and identify gaps. Be rigorous but practical."
        ),
        name="clinical_researcher",
    )

    compliance_officer = chat_client.create_agent(
        instructions=(
            "You're a healthcare compliance and regulatory affairs expert specializing in FDA, HIPAA, and medical regulations. "
            "Analyze regulatory pathways, compliance requirements, and legal constraints for healthcare products. "
            "Consider: FDA classification (510k, PMA, De Novo), HIPAA privacy rules, medical device regulations, "
            "clinical trial requirements (IRB approval), state licensing, international standards (CE mark, ISO 13485), "
            "advertising restrictions, and post-market surveillance. Provide clear compliance roadmaps."
        ),
        name="compliance_officer",
    )

    economics_analyst = chat_client.create_agent(
        instructions=(
            "You're a healthcare economics and reimbursement specialist. Analyze financial viability, "
            "reimbursement strategies, and healthcare business models. Consider: insurance coverage (Medicare, Medicaid, private), "
            "CPT/HCPCS codes, value-based care models, cost-effectiveness analysis (QALY), "
            "provider adoption barriers, patient out-of-pocket costs, pricing strategies, "
            "payer negotiations, and revenue cycle management. Focus on sustainable healthcare economics."
        ),
        name="economics_analyst",
    )
    
    patient_experience = chat_client.create_agent(
        instructions=(
            "You're a patient experience designer and healthcare usability expert. Analyze the patient journey, "
            "accessibility, and safety considerations. Consider: health literacy requirements, "
            "accessibility standards (ADA, WCAG), cultural competency, patient engagement, "
            "user interface for diverse populations (elderly, disabled, non-English speakers), "
            "informed consent processes, patient education materials, usability testing needs, "
            "and patient safety protocols. Prioritize patient-centered design and health equity."
        ),
        name="patient_experience",
    )
    
    data_security = chat_client.create_agent(
        instructions=(
            "You're a medical data security and privacy expert specializing in protecting health information. "
            "Analyze data security, privacy controls, and Protected Health Information (PHI) safeguards. "
            "Consider: HIPAA Security Rule requirements, encryption standards (at rest and in transit), "
            "access controls, audit logging, breach notification procedures, Business Associate Agreements (BAA), "
            "cloud security (HITRUST, SOC 2), mobile device security, authentication mechanisms, "
            "and cybersecurity threats to medical devices. Provide comprehensive security architecture guidance."
        ),
        name="data_security",
    )
    
    # Build the healthcare workflow with structured input handling
    # Create custom dispatcher that handles HealthcareProductInput
    class HealthcareDispatcher(Executor):
        """Dispatcher that extracts description from HealthcareProductInput and forwards to agents."""
        
        @handler
        async def dispatch(self, input_data: HealthcareProductInput, ctx: WorkflowContext) -> None:
            """Extract description and send to all healthcare agents.
            
            Args:
                input_data: HealthcareProductInput with description field
                ctx: WorkflowContext for dispatching to agents
            """
            from agent_framework._workflows._executor import AgentExecutorRequest
            request = AgentExecutorRequest(
                messages=[ChatMessage(Role.USER, text=input_data.description)],
                should_respond=True
            )
            await ctx.send_message(request)
    
    # Build workflow with custom components
    dispatcher = HealthcareDispatcher(id="healthcare_dispatcher")
    aggregator_func = format_healthcare_results
    
    # Use WorkflowBuilder to create the complete workflow
    from agent_framework._workflows._concurrent import _CallbackAggregator
    
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    
    # Add all healthcare agent participants
    agents = [clinical_researcher, compliance_officer, economics_analyst, patient_experience, data_security]
    builder.add_fan_out_edges(dispatcher, agents)
    
    # Add aggregator
    aggregator_executor = _CallbackAggregator(aggregator_func)
    builder.add_fan_in_edges(agents, aggregator_executor)
    
    workflow = builder.build()
    
    # Store the stack for cleanup
    workflow._devui_stack = stack
    
    return workflow


def launch_devui():
    """Launch the DevUI interface with the healthcare workflow."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Create the workflow asynchronously
    workflow = asyncio.run(create_healthcare_workflow())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Healthcare Product Launch Workflow in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Healthcare Product Analysis (Fan-out/Fan-in)")
    print("✅ Participants: 5 specialized healthcare agents")
    print("✅ Web UI: http://localhost:8094")
    print("✅ API: http://localhost:8094/v1/*")
    print("✅ Entity ID: workflow_healthcare")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    print("=" * 70)
    print()
    print("💡 Try these healthcare scenarios in the DevUI:")
    print()
    print("🏥 Medical Devices:")
    print("   - AI-powered diagnostic tool for diabetic retinopathy")
    print("   - Wearable cardiac monitoring device with AFib detection")
    print("   - Smart insulin pump with automated glucose management")
    print()
    print("📱 Digital Health:")
    print("   - Telehealth platform for rural healthcare access")
    print("   - Mental health app with AI-powered CBT therapy")
    print("   - Medication adherence app with smart reminders")
    print()
    print("🔬 Clinical Solutions:")
    print("   - Remote patient monitoring for chronic disease management")
    print("   - Medical imaging AI for lung nodule detection")
    print("   - Virtual physical therapy with motion tracking")
    print()
    print("⚡ Each query will be analyzed by 5 healthcare experts:")
    print("   • Clinical Researcher: Evidence, efficacy, clinical trials")
    print("   • Compliance Officer: FDA, HIPAA, regulatory pathways")
    print("   • Economics Analyst: Reimbursement, insurance, ROI")
    print("   • Patient Experience: Usability, accessibility, safety")
    print("   • Data Security: PHI protection, HIPAA Security Rule")
    print()
    print("⌨️  Press Ctrl+C to stop the server")
    print()
    
    # Launch the DevUI server
    try:
        serve(
            entities=[workflow],
            port=8094,
            auto_open=True,
            tracing_enabled=enable_devui_tracing,
        )
    finally:
        # Clean up resources
        if hasattr(workflow, "_devui_stack"):
            asyncio.run(workflow._devui_stack.aclose())


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down healthcare workflow server...")

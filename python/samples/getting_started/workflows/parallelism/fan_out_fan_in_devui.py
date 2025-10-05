# Copyright (c) Microsoft. All rights reserved.

"""
Concurrent Fan-Out/Fan-In Workflow - DevUI Version with Tracing

This DevUI version demonstrates a parallel workflow pattern where:
- A dispatcher fans out the same prompt to three domain experts (researcher, marketer, legal)
- All experts process the input concurrently
- An aggregator fans in their responses into a consolidated report
- Results are saved to a timestamped text file

The workflow uses a fan-out/fan-in pattern for parallel processing with
clear visualization in DevUI showing all 5 executors.

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
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    ChatMessage,
    Executor,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import get_tracer, setup_observability
from azure.identity import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from pydantic import BaseModel, Field
from typing_extensions import Never

# Load environment variables from workflows/.env file
load_dotenv(Path(__file__).parent.parent / ".env")


class ProductAnalysisInput(BaseModel):
    """Input model for product/business analysis across multiple expert domains."""
    
    description: str = Field(
        description="Product, service, or business idea to analyze",
        examples=[
            "Budget-friendly electric bike for urban commuters",
            "AI-powered personal finance management app for millennials",
            "Sustainable packaging solution for e-commerce using biodegradable materials",
            "Virtual reality fitness platform with live instructor-led classes",
            "Smart home energy monitoring system with predictive cost optimization"
        ]
    )


class DispatchToExperts(Executor):
    """Dispatches the incoming prompt to all expert agent executors for parallel processing (fan-out)."""

    def __init__(self, expert_ids: list[str], id: str | None = None):
        super().__init__(id=id or "dispatch_to_experts")
        self._expert_ids = expert_ids

    @handler
    async def dispatch(self, input_data: ProductAnalysisInput, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
        """Convert ProductAnalysisInput to AgentExecutorRequest and dispatch to all experts.
        
        Args:
            input_data: ProductAnalysisInput with description field
            ctx: WorkflowContext for sending messages to experts
        """
        # Wrap the incoming prompt as a user message for each expert
        initial_message = ChatMessage(Role.USER, text=input_data.description)
        for expert_id in self._expert_ids:
            await ctx.send_message(
                AgentExecutorRequest(messages=[initial_message], should_respond=True),
                target_id=expert_id,
            )


@dataclass
class AggregatedInsights:
    """Typed container for the aggregator to hold per-domain expert insights."""

    research: str
    marketing: str
    legal: str


def format_expert_insights(aggregated: AggregatedInsights, input_prompt: str) -> str:
    """Format the aggregated expert insights into a readable report with file save.
    
    Args:
        aggregated: AggregatedInsights with research, marketing, and legal text
        input_prompt: Original user input for context
        
    Returns:
        Formatted string with all expert insights
    """
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("🔍 PARALLEL EXPERT ANALYSIS REPORT")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("📋 ANALYSIS TYPE: Fan-Out/Fan-In Concurrent Processing")
    output_lines.append("👥 EXPERTS: Research • Marketing • Legal/Compliance")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # User input section
    output_lines.append("─" * 80)
    output_lines.append("💡 INPUT: PRODUCT/BUSINESS CONCEPT")
    output_lines.append("─" * 80)
    output_lines.append("")
    output_lines.append(input_prompt)
    output_lines.append("")
    
    # Research findings
    output_lines.append("─" * 80)
    output_lines.append("🔬 RESEARCH FINDINGS")
    output_lines.append("─" * 80)
    output_lines.append("")
    output_lines.append(aggregated.research)
    output_lines.append("")
    
    # Marketing angle
    output_lines.append("─" * 80)
    output_lines.append("📢 MARKETING STRATEGY")
    output_lines.append("─" * 80)
    output_lines.append("")
    output_lines.append(aggregated.marketing)
    output_lines.append("")
    
    # Legal/compliance notes
    output_lines.append("─" * 80)
    output_lines.append("⚖️ LEGAL & COMPLIANCE")
    output_lines.append("─" * 80)
    output_lines.append("")
    output_lines.append(aggregated.legal)
    output_lines.append("")
    
    output_lines.append("=" * 80)
    output_lines.append("✅ Expert Analysis Complete - All 3 Domains Reviewed")
    output_lines.append("=" * 80)
    
    formatted_output = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"expert_analysis_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"\n💾 Expert analysis saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️ Failed to save output to file: {e}")
    
    return formatted_output


class AggregateInsights(Executor):
    """Aggregates expert agent responses into a single consolidated result (fan-in)."""

    def __init__(self, expert_ids: list[str], input_prompt: str = "", id: str | None = None):
        super().__init__(id=id or "aggregate_insights")
        self._expert_ids = expert_ids
        self._input_prompt = input_prompt

    @handler
    async def aggregate(self, results: list[AgentExecutorResponse], ctx: WorkflowContext[Never, str]) -> None:
        """Aggregate all expert responses and format output.
        
        Args:
            results: List of AgentExecutorResponse from all expert agents
            ctx: WorkflowContext for yielding formatted output
        """
        # Map responses to text by executor id
        by_id: dict[str, str] = {}
        for r in results:
            by_id[r.executor_id] = r.agent_run_response.text

        research_text = by_id.get("researcher", "No research insights available")
        marketing_text = by_id.get("marketer", "No marketing insights available")
        legal_text = by_id.get("legal", "No legal/compliance insights available")

        aggregated = AggregatedInsights(
            research=research_text,
            marketing=marketing_text,
            legal=legal_text,
        )

        # Format and save the consolidated report
        formatted_output = format_expert_insights(aggregated, self._input_prompt)
        
        await ctx.yield_output(formatted_output)


async def create_expert_agents():
    """Create the three domain expert agents with specialized instructions."""
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())

    researcher = AgentExecutor(
        chat_client.create_agent(
            instructions=(
                "You're an expert market and product researcher. Given a product or business concept, provide "
                "concise, factual insights covering: market size/demand, target customer segments, competitive "
                "landscape, key opportunities, and potential risks. Use bullet points for clarity."
            ),
            name="researcher",
        ),
        id="researcher",
    )
    
    marketer = AgentExecutor(
        chat_client.create_agent(
            instructions=(
                "You're a creative marketing strategist. For the given product or business concept, craft "
                "compelling value propositions, positioning strategies, target messaging, channel recommendations, "
                "and campaign ideas. Focus on unique selling points and customer appeal. Use bullet points for clarity."
            ),
            name="marketer",
        ),
        id="marketer",
    )
    
    legal = AgentExecutor(
        chat_client.create_agent(
            instructions=(
                "You're a cautious legal and compliance reviewer. For the given product or business concept, "
                "highlight regulatory constraints, required disclaimers, potential liability concerns, intellectual "
                "property considerations, and compliance requirements. Be thorough but concise. Use bullet points for clarity."
            ),
            name="legal",
        ),
        id="legal",
    )
    
    return researcher, marketer, legal


async def create_expert_analysis_workflow(input_prompt: str = ""):
    """Create and return the DevUI-compatible expert analysis workflow.
    
    Args:
        input_prompt: The user's input prompt (for file output context)
        
    Returns:
        Configured workflow ready for DevUI
    """
    # Create the three expert agents
    researcher, marketer, legal = await create_expert_agents()
    
    expert_ids = [researcher.id, marketer.id, legal.id]
    
    # Create dispatcher and aggregator
    dispatcher = DispatchToExperts(expert_ids=expert_ids, id="dispatcher")
    aggregator = AggregateInsights(expert_ids=expert_ids, input_prompt=input_prompt, id="aggregator")
    
    # Build the fan-out/fan-in workflow
    workflow = (
        WorkflowBuilder()
        .set_start_executor(dispatcher)
        .add_fan_out_edges(dispatcher, [researcher, marketer, legal])  # Parallel branches
        .add_fan_in_edges([researcher, marketer, legal], aggregator)  # Join at aggregator
        .build()
    )
    
    return workflow


def setup_tracing():
    """Set up observability tracing based on environment variables."""
    enable_console = os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true"
    enable_azure_ai = os.environ.get("ENABLE_AZURE_AI_TRACING", "").lower() == "true"
    otlp_endpoint = os.environ.get("OTLP_ENDPOINT")
    
    if enable_console:
        print("📊 Tracing: Console tracing enabled")
        setup_observability(console=True)
    elif enable_azure_ai:
        print("📊 Tracing: Azure AI tracing enabled")
        setup_observability(azure_ai=True)
    elif otlp_endpoint:
        print(f"📊 Tracing: OTLP endpoint configured: {otlp_endpoint}")
        setup_observability(otlp_endpoint=otlp_endpoint)
    else:
        print("📊 Tracing: Disabled")


def launch_devui():
    """Launch the DevUI interface with the expert analysis workflow."""
    from agent_framework.devui import serve
    
    # Set up tracing
    setup_tracing()
    
    # Create the workflow (with empty input_prompt initially)
    workflow = asyncio.run(create_expert_analysis_workflow())
    
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Expert Analysis Fan-Out/Fan-In Workflow in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Concurrent (Fan-Out/Fan-In)")
    print("✅ Participants: 3 Expert Agents (parallel processing)")
    print("    • 🔬 Researcher - Market & product analysis")
    print("    • 📢 Marketer - Strategy & positioning")
    print("    • ⚖️ Legal - Compliance & risk assessment")
    print("✅ Web UI: http://localhost:8098")
    print("✅ API: http://localhost:8098/v1/*")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    print("=" * 70)
    print()
    print("💡 Try these product/business concepts:")
    print()
    print("🚴 Transportation:")
    print("   - Budget-friendly electric bike for urban commuters")
    print("   - Autonomous shuttle service for suburban office parks")
    print()
    print("📱 Technology:")
    print("   - AI-powered personal finance app for millennials")
    print("   - Smart home energy monitoring with predictive optimization")
    print()
    print("🌱 Sustainability:")
    print("   - Biodegradable packaging solution for e-commerce")
    print("   - Carbon offset marketplace connecting businesses to verified projects")
    print()
    print("🏋️ Health & Wellness:")
    print("   - Virtual reality fitness platform with live classes")
    print("   - Mental health chatbot providing CBT-based support")
    print()
    print("=" * 70)
    
    # Serve the workflow through DevUI
    serve(
        entities=[workflow],
        port=8098,
        auto_open=True,
        tracing_enabled=enable_devui_tracing
    )


if __name__ == "__main__":
    launch_devui()

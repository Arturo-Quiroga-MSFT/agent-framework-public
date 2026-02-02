# Copyright (c) Microsoft. All rights reserved.

"""
Concurrent Agents Workflow - DevUI Version with Tracing

This version of concurrent_agents.py is instrumented to work with DevUI
for visualization and debugging. It creates a persistent concurrent workflow
with five specialized agents (researcher, marketer, legal, finance, technical) that can be
interacted with through the DevUI web interface.

The workflow uses a fan-out/fan-in pattern where:
- User input is dispatched to all five agents concurrently
- Each agent processes the input independently
- Results are aggregated and returned together

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
from agent_framework import ChatMessage, Executor, WorkflowBuilder, WorkflowContext, handler, Role, AgentExecutorRequest, AgentExecutorResponse
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import get_tracer, configure_otel_providers
from azure.identity import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from pydantic import BaseModel, Field

# Load environment variables from workflows/.env file
load_dotenv(Path(__file__).parent.parent / ".env")


class ProductLaunchInput(BaseModel):
    """Input model for product launch analysis."""
    
    description: str = Field(
        ...,
        description="Describe your product, service, or business idea. Include details about target market, key features, and unique value proposition.",
        examples=[
            "We are launching a new budget-friendly electric bike for urban commuters",
            "Introducing an AI-powered personal finance app for Gen Z users",
            "Developing a telemedicine platform for rural healthcare access"
        ]
    )


def format_concurrent_results(results) -> str:
    """Format concurrent agent outputs for DevUI display and save to file.
    
    Args:
        results: List of AgentExecutorResponse objects from concurrent agents
        
    Returns:
        Formatted string with all agent responses
    """
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("📊 COMPREHENSIVE PRODUCT ANALYSIS")
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
                    "RESEARCHER": "🔬",
                    "MARKETER": "📢",
                    "LEGAL": "⚖️",
                    "FINANCE": "💰",
                    "TECHNICAL": "🏗️"
                }.get(agent_name, "👤")
                
                output_lines.append("─" * 80)
                output_lines.append(f"{emoji} {agent_name} ANALYSIS")
                output_lines.append("─" * 80)
                output_lines.append("")
                output_lines.append(msg.text)
                output_lines.append("")
                break  # Only use the final message
    
    output_lines.append("=" * 80)
    output_lines.append("✅ Analysis Complete - All perspectives reviewed")
    output_lines.append("=" * 80)
    
    formatted_output = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"concurrent_analysis_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"\n💾 Output saved to: {output_file}")
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


async def create_concurrent_workflow():
    """Create and return a concurrent workflow for DevUI (async version)."""
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
    
    # Create five specialized agents for comprehensive product analysis
    researcher = chat_client.as_agent(
        instructions=(
            "You're an expert market and product researcher. Given a prompt, provide concise, factual insights,"
            " opportunities, and risks. Keep your response focused and actionable."
        ),
        name="researcher",
    )

    marketer = chat_client.as_agent(
        instructions=(
            "You're a creative marketing strategist. Craft compelling value propositions and target messaging"
            " aligned to the prompt. Be creative but practical."
        ),
        name="marketer",
    )

    legal = chat_client.as_agent(
        instructions=(
            "You're a cautious legal/compliance reviewer. Highlight constraints, disclaimers, and policy concerns"
            " based on the prompt. Be thorough but concise."
        ),
        name="legal",
    )
    
    finance = chat_client.as_agent(
        instructions=(
            "You're a financial analyst and business strategist. Analyze financial viability, revenue models,"
            " cost structures, pricing strategies, and ROI projections. Provide actionable financial insights"
            " and identify key financial risks and opportunities."
        ),
        name="finance",
    )
    
    technical = chat_client.as_agent(
        instructions=(
            "You're a technical architect and engineering lead. Evaluate technical feasibility, architecture requirements,"
            " technology stack recommendations, scalability considerations, and implementation challenges."
            " Focus on practical, actionable technical guidance."
        ),
        name="technical",
    )
    
    # Build the concurrent workflow with structured input handling
    # Create custom dispatcher that handles ProductLaunchInput
    class ProductLaunchDispatcher(Executor):
        """Dispatcher that extracts description from ProductLaunchInput and forwards to agents."""
        
        @handler
        async def dispatch(self, input_data: ProductLaunchInput, ctx: WorkflowContext) -> None:
            """Extract description and send to all agents.
            
            Args:
                input_data: ProductLaunchInput with description field
                ctx: WorkflowContext for dispatching to agents
            """
            request = AgentExecutorRequest(
                messages=[ChatMessage(Role.USER, text=input_data.description)],
                should_respond=True
            )
            await ctx.send_message(request)
    
    # Build workflow with custom components
    dispatcher = ProductLaunchDispatcher(id="dispatcher")
    
    # Create custom aggregator executor
    class ProductAggregator(Executor):
        """Aggregator that formats results from all product analysis agents."""
        
        @handler
        async def aggregate(self, results: list[AgentExecutorResponse], ctx: WorkflowContext) -> None:
            """Aggregate results from all agents and format output.
            
            Args:
                results: List of AgentExecutorResponse objects from agents
                ctx: WorkflowContext for yielding output
            """
            formatted_output = format_concurrent_results(results)
            await ctx.yield_output(formatted_output)
    
    aggregator = ProductAggregator(id="product_aggregator")
    
    # Use WorkflowBuilder to create the complete workflow
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    
    # Add all agent participants
    agents = [researcher, marketer, legal, finance, technical]
    builder.add_fan_out_edges(dispatcher, agents)
    
    # Add aggregator
    builder.add_fan_in_edges(agents, aggregator)
    
    workflow = builder.build()
    
    # Store the stack for cleanup
    workflow._devui_stack = stack
    
    return workflow


def launch_devui():
    """Launch the DevUI interface with the concurrent workflow."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Create the workflow asynchronously
    workflow = asyncio.run(create_concurrent_workflow())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Concurrent Agents Workflow in DevUI")
    print("=" * 70)
    print(f"✅ Workflow Type: Concurrent (Fan-out/Fan-in)")
    print(f"✅ Participants: 5 agents (researcher, marketer, legal, finance, technical)")
    print(f"✅ Web UI: http://localhost:8093")
    print(f"✅ API: http://localhost:8093/v1/*")
    print(f"✅ Entity ID: workflow_concurrent")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    else:
        print("   → Set ENABLE_DEVUI_TRACING=true to enable")
    print("=" * 70)
    print("\n💡 Try these product launch scenarios in the DevUI:")
    print("\n🚴 E-Commerce:")
    print("   - We are launching a new budget-friendly electric bike for urban commuters")
    print("   - Launching a subscription box service for organic pet food")
    print("\n🎮 Technology:")
    print("   - Introducing an AI-powered personal finance app for Gen Z users")
    print("   - Launching a VR fitness platform for home workouts")
    print("\n🏥 Healthcare:")
    print("   - Developing a telemedicine platform for rural healthcare access")
    print("   - Launching a mental health app with AI-powered therapy sessions")
    print("\n📱 Consumer:")
    print("   - Introducing a sustainable fashion rental marketplace")
    print("   - Launching a smart home security system with AI detection")
    print("\n⚡ Each query will be analyzed concurrently by 5 expert agents:")
    print("   • Researcher: Market insights, opportunities, risks")
    print("   • Marketer: Value propositions, target messaging")
    print("   • Legal: Compliance, disclaimers, policy concerns")
    print("   • Finance: Revenue models, cost structure, ROI projections")
    print("   • Technical: Architecture, tech stack, scalability, implementation")
    print("\n⌨️  Press Ctrl+C to stop the server\n")
    
    try:
        # Launch the DevUI server with tracing enabled if configured
        serve(
            entities=[workflow], 
            port=8093, 
            auto_open=True,
            instrumentation_enabled=enable_devui_tracing
        )
    finally:
        # Clean up resources
        if hasattr(workflow, '_devui_stack'):
            asyncio.run(workflow._devui_stack.aclose())


async def test_workflow():
    """Test the workflow programmatically before launching DevUI."""
    print("\n🧪 Testing concurrent workflow functionality with tracing...")
    
    # Set up tracing
    setup_tracing()
    
    workflow = await create_concurrent_workflow()
    
    try:
        # Test with a sample product launch scenario
        test_input = ProductLaunchInput(
            description="We are launching a new budget-friendly electric bike for urban commuters."
        )
        
        # Create a span for the entire test session
        with get_tracer().start_as_current_span("Workflow Test Session", kind=SpanKind.CLIENT) as span:
            trace_id = format_trace_id(span.get_span_context().trace_id)
            print(f"🔍 Trace ID: {trace_id}")
            print("   Use this ID to find traces in your observability backend\n")
            
            print(f"👤 User: {test_input.description}")
            print("\n🤖 Workflow is running concurrent agents...\n")
            
            # Run the workflow
            events = await workflow.run(test_input)
            outputs = events.get_outputs()
            
            if outputs:
                print("=" * 70)
                print("📊 Aggregated Results from All Agents:")
                print("=" * 70)
                # The output should be our formatted string
                for output in outputs:
                    print(output)
        
        print("\n" + "=" * 70)
        print("✅ Workflow test completed successfully!")
        print(f"🔍 All operations traced under ID: {trace_id}")
        print("=" * 70 + "\n")
    finally:
        # Clean up resources
        if hasattr(workflow, '_devui_stack'):
            await workflow._devui_stack.aclose()


def main():
    """Main entry point."""
    import sys
    
    # Check if we should test or launch DevUI
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run async test
        asyncio.run(test_workflow())
    else:
        # Launch DevUI (synchronous)
        launch_devui()


if __name__ == "__main__":
    main()

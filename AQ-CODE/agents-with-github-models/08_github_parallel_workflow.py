#!/usr/bin/env python3
"""
Example 08: Parallel Workflow with DevUI Visualization (Workflow Builder)

This example demonstrates a PROPER concurrent/parallel workflow using MAF's WorkflowBuilder
with fan-out/fan-in pattern. This enables visual workflow representation in DevUI showing
how agents execute simultaneously and aggregate results.

Key Differences from Example 06:
- Uses WorkflowBuilder for proper concurrent workflow construction
- Visual flow diagram showing fan-out and fan-in
- Proper parallel execution via workflow edges
- Structured input/output handling with aggregation
- Enhanced observability and tracing

Concurrent Flow Visualization:
                    ┌→ Technical Analyst →┐
                    ├→ Business Analyst  →┤
User Input → Dispatcher ├→ Risk Analyst     →├→ Aggregator → Final Report
                    ├→ Creative Consultant→┤
                    └────────────────────┘

All 4 agents run simultaneously! (~15-20s total)

Prerequisites:
1. Set up your .env file with GITHUB_TOKEN
2. Install dependencies: pip install -r requirements.txt
3. Install DevUI: pip install agent-framework-devui --pre

Usage:
    python 08_github_parallel_workflow.py
    
    Opens DevUI at http://localhost:8083 with visual workflow diagram!

Example Topics:
- "AI-powered mental health therapy mobile app"
- "Blockchain carbon credit trading marketplace"
- "Autonomous delivery robot for urban areas"
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

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
from agent_framework.openai import OpenAIChatClient

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
GITHUB_BASE_URL = "https://models.inference.ai.azure.com"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file. Please set it first.")


class ProductAnalysisInput(BaseModel):
    """Input model for parallel product analysis workflow."""
    
    description: str = Field(
        ...,
        description="Describe the product, service, or business idea you want analyzed from multiple expert perspectives",
        examples=[
            "AI-powered personal fitness coach with computer vision form correction",
            "Blockchain-based digital identity verification for remote work",
            "Sustainable fashion rental marketplace with AI styling",
            "Mental health app with AI therapy and peer community",
            "Smart home energy optimizer using predictive analytics"
        ]
    )


def create_github_client(model_id: str = GITHUB_MODEL) -> OpenAIChatClient:
    """Create an OpenAI-compatible client configured for GitHub Models."""
    return OpenAIChatClient(
        model_id=model_id,
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_BASE_URL,
    )


def format_concurrent_results(results: list[AgentExecutorResponse]) -> str:
    """Format concurrent agent outputs for DevUI display and save to file.
    
    Args:
        results: List of AgentExecutorResponse objects from concurrent agents
        
    Returns:
        Formatted string with all agent responses
    """
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("⚡ PARALLEL MULTI-PERSPECTIVE ANALYSIS")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("📋 All agents analyzed simultaneously for comprehensive insights")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Emoji mapping
    agent_emoji = {
        "technical": "🔧",
        "business": "💼",
        "risk": "⚖️",
        "creative": "🎨"
    }
    
    # Process each agent's response
    for result in results:
        messages = getattr(result.agent_run_response, "messages", [])
        
        # Find the final assistant message
        for msg in reversed(messages):
            if hasattr(msg, "author_name") and msg.author_name and msg.author_name != "user":
                agent_name = msg.author_name
                emoji = agent_emoji.get(agent_name, "👤")
                display_name = agent_name.replace("_", " ").upper()
                
                output_lines.append("─" * 80)
                output_lines.append(f"{emoji} {display_name} ANALYSIS")
                output_lines.append("─" * 80)
                output_lines.append("")
                output_lines.append(msg.text)
                output_lines.append("")
                break
    
    output_lines.append("=" * 80)
    output_lines.append("✅ Parallel Analysis Complete - All 4 perspectives reviewed")
    output_lines.append("=" * 80)
    
    formatted_output = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"parallel_github_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"\n💾 Output saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️ Failed to save output to file: {e}")
    
    return formatted_output


async def create_parallel_workflow():
    """
    Creates a parallel/concurrent workflow with proper WorkflowBuilder integration.
    
    This creates a fan-out/fan-in workflow with:
    - Input dispatcher that handles ProductAnalysisInput
    - Four parallel agents (Technical, Business, Risk, Creative)
    - Aggregator that combines all results
    - Visual flow representation in DevUI showing parallelism
    
    Returns:
        Workflow object with proper concurrent structure
    """
    # Create shared GitHub Models client
    client = create_github_client()
    
    # Agent 1: Technical Analyst
    technical_agent = client.create_agent(
        instructions="""You are a Technical Analyst with expertise in software architecture, scalability, and implementation.

Your role is to analyze topics from a technical perspective:
- Technical feasibility and architecture requirements
- Technology stack recommendations
- Scalability and performance considerations
- Technical risks and mitigation strategies
- Implementation timeline and complexity

Provide 200-300 words of actionable technical insights with bullet points.""",
        name="technical",
    )
    
    # Agent 2: Business Analyst
    business_agent = client.create_agent(
        instructions="""You are a Business Analyst with expertise in market analysis, business models, and strategy.

Your role is to analyze topics from a business perspective:
- Market opportunity and target audience
- Business model and revenue potential
- Competitive landscape and differentiation
- Go-to-market strategy
- Financial projections and ROI

Provide 200-300 words of actionable business insights with bullet points.""",
        name="business",
    )
    
    # Agent 3: Risk Analyst
    risk_agent = client.create_agent(
        instructions="""You are a Risk Analyst with expertise in risk assessment, compliance, and security.

Your role is to analyze topics from a risk perspective:
- Operational risks and challenges
- Regulatory and compliance requirements
- Security and privacy concerns
- Risk mitigation strategies
- Long-term sustainability considerations

Provide 200-300 words of actionable risk insights with bullet points.""",
        name="risk",
    )
    
    # Agent 4: Creative Consultant
    creative_agent = client.create_agent(
        instructions="""You are a Creative Consultant with expertise in innovation, UX, and creative problem-solving.

Your role is to analyze topics from a creative perspective:
- Innovative approaches and unique angles
- User experience and engagement strategies
- Creative differentiation opportunities
- Emerging trends and future possibilities
- Unconventional solutions

Provide 200-300 words of actionable creative insights with bullet points.""",
        name="creative",
    )
    
    # Create input dispatcher
    class ProductInputDispatcher(Executor):
        """Dispatcher that extracts description from ProductAnalysisInput and broadcasts to all agents."""
        
        @handler
        async def dispatch(self, input_data: ProductAnalysisInput, ctx: WorkflowContext) -> None:
            """Extract description and send to all parallel agents.
            
            Args:
                input_data: ProductAnalysisInput with description field
                ctx: WorkflowContext for broadcasting
            """
            request = AgentExecutorRequest(
                messages=[ChatMessage(Role.USER, text=f"Analyze the following from your expert perspective:\n\n{input_data.description}")],
                should_respond=True
            )
            await ctx.send_message(request)
    
    dispatcher = ProductInputDispatcher(id="input_dispatcher")
    
    # Wrap agents in AgentExecutor
    technical_executor = AgentExecutor(agent=technical_agent, id="technical")
    business_executor = AgentExecutor(agent=business_agent, id="business")
    risk_executor = AgentExecutor(agent=risk_agent, id="risk")
    creative_executor = AgentExecutor(agent=creative_agent, id="creative")
    
    # Create aggregator
    class ParallelAggregator(Executor):
        """Aggregator that combines results from all parallel agents."""
        
        @handler
        async def aggregate(
            self,
            results: list[AgentExecutorResponse],
            ctx: WorkflowContext[list[AgentExecutorResponse], str]
        ) -> None:
            """Aggregate parallel results and format output.
            
            Args:
                results: List of AgentExecutorResponse from all agents
                ctx: WorkflowContext for yielding output
            """
            formatted_output = format_concurrent_results(results)
            await ctx.yield_output(formatted_output)
    
    aggregator = ParallelAggregator(id="result_aggregator")
    
    # Build the parallel workflow with fan-out/fan-in pattern
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    
    # Add fan-out edges (dispatcher → all agents in parallel)
    agents = [technical_executor, business_executor, risk_executor, creative_executor]
    builder.add_fan_out_edges(dispatcher, agents)
    
    # Add fan-in edges (all agents → aggregator)
    builder.add_fan_in_edges(agents, aggregator)
    
    workflow = builder.build()
    
    return workflow


def main():
    """Launch the parallel workflow in DevUI with visual representation."""
    from agent_framework.devui import serve
    
    print("\n" + "="*80)
    print("⚡ Parallel Workflow with Visual Representation - DevUI")
    print("="*80)
    print("\n📋 Workflow Architecture (Fan-Out/Fan-In):")
    print("                  ┌→ Technical Analyst →┐")
    print("                  ├→ Business Analyst  →┤")
    print("   Input → Dispatcher ├→ Risk Analyst     →├→ Aggregator → Output")
    print("                  ├→ Creative Consultant→┤")
    print("                  └───────────────────────┘")
    print("\n🔧 Using: GitHub Models with Microsoft Agent Framework")
    print("🎨 Feature: WorkflowBuilder with parallel execution visualization")
    print("\n🌐 Starting DevUI server...")
    
    # Create the workflow
    workflow = asyncio.run(create_parallel_workflow())
    
    print("\n✅ Parallel workflow created")
    print("\n" + "="*80)
    print("🎯 DevUI Interface")
    print("="*80)
    print("\n🌐 Web UI:  http://localhost:8083")
    print("📡 API:     http://localhost:8083/v1/*")
    print("🔍 Entity:  workflow_parallel")
    print("📊 Feature: Visual workflow diagram showing parallel execution")
    
    print("\n" + "="*80)
    print("💡 How to Use")
    print("="*80)
    print("\n1. Open http://localhost:8083 in your browser")
    print("2. Select 'workflow_parallel' from dropdown")
    print("3. You'll see the fan-out/fan-in workflow visualization")
    print("4. Enter your product/idea description")
    print("5. Watch all 4 agents execute simultaneously:")
    print("   • Technical Analyst - Architecture & feasibility (~15-20s)")
    print("   • Business Analyst - Market & revenue (~15-20s)")
    print("   • Risk Analyst - Compliance & risks (~15-20s)")
    print("   • Creative Consultant - Innovation & UX (~15-20s)")
    print("6. Total time: ~15-20s (all run in parallel!)")
    
    print("\n" + "="*80)
    print("📝 Example Topics")
    print("="*80)
    print("\n🤖 AI Applications:")
    print("   • AI-powered customer service chatbot with sentiment analysis")
    print("   • Computer vision quality control for manufacturing")
    print("   • Personalized learning platform with adaptive assessments")
    
    print("\n🏥 Healthcare:")
    print("   • Telemedicine app with AI symptom checker")
    print("   • Mental health support chatbot with crisis detection")
    print("   • Wearable device for continuous glucose monitoring")
    
    print("\n🌱 Sustainability:")
    print("   • Carbon offsetting marketplace for individuals")
    print("   • Smart building energy management system")
    print("   • Circular economy platform for electronics recycling")
    
    print("\n" + "="*80)
    print("✨ New in Example 08: Parallel Workflow Visualization")
    print("="*80)
    print("\n🎨 WorkflowBuilder Benefits:")
    print("   • Visual fan-out/fan-in diagram (vs individual agents in 06)")
    print("   • Proper parallel execution via workflow edges")
    print("   • Automatic result aggregation")
    print("   • Structured input handling (ProductAnalysisInput)")
    print("   • Enhanced observability - see all agents working simultaneously")
    print("   • Output saved to workflow_outputs/ directory")
    
    print("\n" + "="*80)
    print("⚡ Performance Comparison")
    print("="*80)
    print("\nExample 06 (Individual Agents):")
    print("   • 4 separate agent entities")
    print("   • Manual chat with each agent")
    print("   • No built-in aggregation")
    print("   • ~15-20s per agent if done sequentially")
    
    print("\nExample 08 (Parallel Workflow):")
    print("   • Single unified workflow entity")
    print("   • One input → 4 agents simultaneously")
    print("   • Automatic result aggregation")
    print("   • ~15-20s total (all run in parallel)")
    print("   • 4x speedup potential vs sequential!")
    
    print("\n" + "="*80)
    print("📊 Architecture Comparison")
    print("="*80)
    print("\nExample 07 (Sequential):")
    print("   Dispatcher → Agent1 → Agent2 → Agent3 → Aggregator")
    print("   Time: ~55-70s (agents wait for each other)")
    
    print("\nExample 08 (Parallel):")
    print("   Dispatcher → [Agent1, Agent2, Agent3, Agent4] → Aggregator")
    print("   Time: ~15-20s (all agents work simultaneously)")
    
    print("\n" + "="*80)
    print("🎯 When to Use Each Pattern")
    print("="*80)
    print("\n📝 Sequential (Example 07):")
    print("   ✅ Agents need previous agent's output")
    print("   ✅ Building on prior analysis")
    print("   ✅ Step-by-step refinement")
    print("   ❌ Slower total execution time")
    
    print("\n⚡ Parallel (Example 08):")
    print("   ✅ Independent expert perspectives")
    print("   ✅ Faster total execution time")
    print("   ✅ Comprehensive multi-angle analysis")
    print("   ❌ Agents can't build on each other")
    
    print("\n" + "="*80)
    print("⌨️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    # Launch DevUI server with tracing enabled
    serve(
        entities=[workflow],
        port=8083,
        auto_open=True,
        tracing_enabled=True,  # Enable OpenTelemetry tracing
    )


if __name__ == "__main__":
    main()

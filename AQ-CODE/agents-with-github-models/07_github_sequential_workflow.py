#!/usr/bin/env python3
"""
Example 07: Sequential Workflow with DevUI Visualization (Workflow Builder)

This example demonstrates a PROPER sequential workflow using MAF's WorkflowBuilder,
which enables visual workflow representation in DevUI. Unlike example 05 which wraps
agents, this creates a true workflow with proper edges and flow visualization.

Key Differences from Example 05:
- Uses WorkflowBuilder for proper workflow construction
- Visual flow diagram in DevUI showing agent progression
- Proper message passing between agents via workflow edges
- Structured input/output handling
- Enhanced observability and tracing

Sequential Flow Visualization:
User Input → Research Agent → Analysis Agent → Writer Agent → Final Report
    ↓            ↓                 ↓                 ↓              ↓
[Dispatcher] → [Research] ────→ [Analysis] ────→ [Writer] → [Formatter]

Prerequisites:
1. Set up your .env file with GITHUB_TOKEN
2. Install dependencies: pip install -r requirements.txt
3. Install DevUI: pip install agent-framework-devui --pre

Usage:
    python 07_github_sequential_workflow.py
    
    Opens DevUI at http://localhost:8082 with visual workflow diagram!

Example Topics:
- "AI-powered education platform for remote learning"
- "Blockchain supply chain transparency system"
- "Sustainable urban farming marketplace"
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


class TopicAnalysisInput(BaseModel):
    """Input model for topic analysis workflow."""
    
    topic: str = Field(
        ...,
        description="Describe the topic, product, or concept you want analyzed comprehensively",
        examples=[
            "AI-powered personal learning assistant for working professionals",
            "Blockchain-based supply chain tracking for ethical sourcing",
            "Sustainable urban vertical farming system for restaurants",
            "Mental health app with AI therapy and peer support",
            "Carbon footprint tracking platform for small businesses"
        ]
    )


def create_github_client(model_id: str = GITHUB_MODEL) -> OpenAIChatClient:
    """Create an OpenAI-compatible client configured for GitHub Models."""
    return OpenAIChatClient(
        model_id=model_id,
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_BASE_URL,
    )


def format_sequential_results(conversation: list[ChatMessage]) -> str:
    """Format sequential conversation into readable output with file save.
    
    Args:
        conversation: Complete list of ChatMessage objects from sequential workflow
        
    Returns:
        Formatted string with all sequential agent responses
    """
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("🔄 SEQUENTIAL ANALYSIS WORKFLOW")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("📋 FLOW: User Input → Research → Analysis → Writing → Final Report")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Emoji mapping for agents
    agent_emoji = {
        "user": "👤",
        "research_agent": "🔬",
        "analysis_agent": "📊",
        "writer_agent": "✍️"
    }
    
    # Display names
    agent_names = {
        "user": "USER INPUT",
        "research_agent": "RESEARCH AGENT",
        "analysis_agent": "ANALYSIS AGENT",
        "writer_agent": "WRITER AGENT"
    }
    
    step = 1
    for msg in conversation:
        name = msg.author_name or ("user" if msg.role == Role.USER else "assistant")
        emoji = agent_emoji.get(name, "🔹")
        display_name = agent_names.get(name, name.upper())
        
        output_lines.append("─" * 80)
        output_lines.append(f"{emoji} STEP {step}: {display_name}")
        output_lines.append("─" * 80)
        output_lines.append("")
        output_lines.append(msg.text)
        output_lines.append("")
        step += 1
    
    output_lines.append("=" * 80)
    output_lines.append("✅ Sequential Analysis Complete - All 3 agents reviewed")
    output_lines.append("=" * 80)
    
    formatted_output = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"sequential_github_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"\n💾 Output saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️ Failed to save output to file: {e}")
    
    return formatted_output


async def create_sequential_workflow():
    """
    Creates a sequential workflow with proper WorkflowBuilder integration.
    
    This creates a true MAF workflow with:
    - Input dispatcher that handles TopicAnalysisInput
    - Three sequential agents (Research → Analysis → Writer)
    - Output formatter for final presentation
    - Visual flow representation in DevUI
    
    Returns:
        Workflow object with proper sequential structure
    """
    # Create shared GitHub Models client
    client = create_github_client()
    
    # Agent 1: Research Agent
    research_agent = client.create_agent(
        instructions="""You are a Research Agent specialized in gathering comprehensive information.

Your role is to:
1. Identify key aspects of the topic
2. Research relevant facts, data, and examples
3. Highlight important trends and developments
4. Note potential challenges and opportunities
5. Provide detailed findings (300-400 words)

Be thorough and objective in your research. Your findings will be used by downstream analysts.""",
        name="research_agent",
    )
    
    # Agent 2: Analysis Agent
    analysis_agent = client.create_agent(
        instructions="""You are an Analysis Agent specialized in pattern recognition and insight generation.

Your role is to:
1. Review the complete conversation history including research findings
2. Identify key patterns and connections
3. Generate actionable insights
4. Highlight critical success factors and risks
5. Provide strategic recommendations (250-350 words)

Focus on synthesis and strategic thinking. Build upon the research provided.""",
        name="analysis_agent",
    )
    
    # Agent 3: Writer Agent
    writer_agent = client.create_agent(
        instructions="""You are a Writer Agent specialized in creating comprehensive reports.

Your role is to:
1. Review the complete conversation including research and analysis
2. Synthesize all information into a cohesive report
3. Structure information clearly with sections
4. Highlight key findings and recommendations
5. Create an executive summary
6. Provide a final report (400-500 words)

Structure: Executive Summary, Key Findings, Analysis, Recommendations, Conclusion.
Build upon all previous agent insights.""",
        name="writer_agent",
    )
    
    # Create input dispatcher that extracts topic from TopicAnalysisInput
    class TopicInputDispatcher(Executor):
        """Dispatcher that extracts topic from TopicAnalysisInput and forwards to first agent."""
        
        @handler
        async def dispatch(self, input_data: TopicAnalysisInput, ctx: WorkflowContext) -> None:
            """Extract topic and send to research agent.
            
            Args:
                input_data: TopicAnalysisInput with topic field
                ctx: WorkflowContext for message passing
            """
            request = AgentExecutorRequest(
                messages=[ChatMessage(Role.USER, text=f"Research the following topic comprehensively:\n\n{input_data.topic}")],
                should_respond=True
            )
            await ctx.send_message(request)
    
    dispatcher = TopicInputDispatcher(id="input_dispatcher")
    
    # Wrap agents in AgentExecutor
    research_executor = AgentExecutor(agent=research_agent, id="research")
    analysis_executor = AgentExecutor(agent=analysis_agent, id="analysis")
    writer_executor = AgentExecutor(agent=writer_agent, id="writer")
    
    # Create output formatter
    class SequentialOutputFormatter(Executor):
        """Formatter that creates final readable output from workflow."""
        
        @handler
        async def format_output(
            self,
            response: AgentExecutorResponse,
            ctx: WorkflowContext[AgentExecutorResponse, str]
        ) -> None:
            """Format the complete sequential conversation.
            
            Args:
                response: Final AgentExecutorResponse from writer agent
                ctx: WorkflowContext for yielding output
            """
            conversation = response.full_conversation or []
            formatted_output = format_sequential_results(conversation)
            await ctx.yield_output(formatted_output)
    
    output_formatter = SequentialOutputFormatter(id="output_formatter")
    
    # Build the sequential workflow
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    
    # Create sequential chain: dispatcher → research → analysis → writer → formatter
    builder.add_edge(dispatcher, research_executor)
    builder.add_edge(research_executor, analysis_executor)
    builder.add_edge(analysis_executor, writer_executor)
    builder.add_edge(writer_executor, output_formatter)
    
    workflow = builder.build()
    
    return workflow


def main():
    """Launch the sequential workflow in DevUI with visual representation."""
    from agent_framework.devui import serve
    
    print("\n" + "="*80)
    print("🔄 Sequential Workflow with Visual Representation - DevUI")
    print("="*80)
    print("\n📋 Workflow Architecture:")
    print("   Input → Research Agent → Analysis Agent → Writer Agent → Output")
    print("           (Gather Info)    (Find Patterns)   (Create Report)")
    print("\n🔧 Using: GitHub Models with Microsoft Agent Framework")
    print("🎨 Feature: WorkflowBuilder with visual flow diagram")
    print("\n🌐 Starting DevUI server...")
    
    # Create the workflow
    workflow = asyncio.run(create_sequential_workflow())
    
    print("\n✅ Sequential workflow created")
    print("\n" + "="*80)
    print("🎯 DevUI Interface")
    print("="*80)
    print("\n🌐 Web UI:  http://localhost:8082")
    print("📡 API:     http://localhost:8082/v1/*")
    print("🔍 Entity:  workflow_sequential")
    print("📊 Feature: Visual workflow diagram showing flow")
    
    print("\n" + "="*80)
    print("💡 How to Use")
    print("="*80)
    print("\n1. Open http://localhost:8082 in your browser")
    print("2. Select 'workflow_sequential' from dropdown")
    print("3. You'll see the workflow visualization (if supported)")
    print("4. Enter your topic in the input field")
    print("5. Watch the sequential flow:")
    print("   • Research Agent gathers comprehensive information (~20s)")
    print("   • Analysis Agent identifies patterns and insights (~15s)")
    print("   • Writer Agent creates structured final report (~20s)")
    print("6. Total time: ~55-70 seconds for complete analysis")
    
    print("\n" + "="*80)
    print("📝 Example Topics")
    print("="*80)
    print("\n🤖 AI & Technology:")
    print("   • AI-powered code review automation tool")
    print("   • Blockchain supply chain transparency platform")
    print("   • Edge computing for IoT smart cities")
    
    print("\n🏥 Healthcare:")
    print("   • Telemedicine platform for mental health")
    print("   • AI diagnostic assistant for radiologists")
    print("   • Wearable health monitoring ecosystem")
    
    print("\n🌱 Sustainability:")
    print("   • Carbon tracking SaaS for enterprises")
    print("   • Renewable energy micro-grid management")
    print("   • Circular economy marketplace platform")
    
    print("\n" + "="*80)
    print("✨ New in Example 07: Workflow Visualization")
    print("="*80)
    print("\n🎨 WorkflowBuilder Benefits:")
    print("   • Visual flow diagram (vs simple chat in 05)")
    print("   • Proper sequential edges between agents")
    print("   • Message passing via workflow context")
    print("   • Structured input handling (TopicAnalysisInput)")
    print("   • Enhanced observability and tracing")
    print("   • Output saved to workflow_outputs/ directory")
    
    print("\n" + "="*80)
    print("📊 Architecture Comparison")
    print("="*80)
    print("\nExample 05 (Simple Wrapper):")
    print("   User → [Wrapped Agent] → Response")
    print("   • No visual workflow")
    print("   • Manual agent chaining in code")
    print("   • Basic DevUI chat interface")
    
    print("\nExample 07 (WorkflowBuilder):")
    print("   User → [Dispatcher] → [Research] → [Analysis] → [Writer] → [Formatter]")
    print("   • Visual workflow diagram")
    print("   • Proper workflow edges")
    print("   • Structured message passing")
    print("   • Enhanced DevUI visualization")
    
    print("\n" + "="*80)
    print("⌨️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    # Launch DevUI server with tracing enabled
    serve(
        entities=[workflow],
        port=8082,
        auto_open=True,
        tracing_enabled=True,  # Enable OpenTelemetry tracing
    )


if __name__ == "__main__":
    main()

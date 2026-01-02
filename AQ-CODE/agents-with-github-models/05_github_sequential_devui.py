#!/usr/bin/env python3
"""
Example 05: Sequential Multi-Agent Workflow with DevUI Visualization

This example demonstrates the same sequential workflow as 03_github_multi_agent.py
but with DevUI integration for interactive testing and visual debugging.

Key Differences from Example 03:
- DevUI web interface for testing the workflow
- No hardcoded topic - you provide input via the UI
- Visual conversation history and agent outputs
- API endpoint for programmatic access
- Real-time execution monitoring

Workflow: User Query → Research Agent → Analysis Agent → Writer Agent → Final Report

DevUI Benefits:
✅ Interactive web interface for testing
✅ Visual conversation history
✅ Real-time agent execution monitoring
✅ API access for integration testing
✅ No code changes needed to test different inputs

Prerequisites:
1. Set up your .env file with GITHUB_TOKEN
2. Install dependencies: pip install -r requirements.txt
3. Install DevUI: pip install agent-framework-devui --pre

Usage:
    python 05_github_sequential_devui.py
    
    Then open http://localhost:8080 in your browser and chat with the workflow!

Example Prompts to Try:
- "Analyze the potential of AI-powered education platforms"
- "Research blockchain applications in supply chain management"
- "Investigate the market for sustainable food packaging solutions"
"""

import asyncio
import os
from dotenv import load_dotenv

from agent_framework import ChatAgent, Workflow
from agent_framework.openai import OpenAIChatClient

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
GITHUB_BASE_URL = "https://models.inference.ai.azure.com"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file. Please set it first.")


def create_github_client(model_id: str = GITHUB_MODEL) -> OpenAIChatClient:
    """Create an OpenAI-compatible client configured for GitHub Models."""
    return OpenAIChatClient(
        model_id=model_id,
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_BASE_URL,
    )


async def create_sequential_workflow() -> Workflow:
    """
    Creates a sequential multi-agent workflow for comprehensive topic analysis.
    
    The workflow consists of three specialized agents that work in sequence:
    1. Research Agent: Gathers information and key facts
    2. Analysis Agent: Identifies patterns and insights  
    3. Writer Agent: Creates a comprehensive report
    
    Returns:
        Workflow object configured with three sequential agents
    """
    # Create shared client
    client = create_github_client()
    
    # Agent 1: Research Agent
    research_agent = ChatAgent(
        chat_client=client,
        instructions="""You are a Research Agent specialized in gathering comprehensive information.

Your role is to:
1. Identify key aspects of the topic
2. Research relevant facts, data, and examples
3. Highlight important trends and developments
4. Note potential challenges and opportunities
5. Provide detailed findings (300-400 words)

Be thorough and objective in your research.""",
        name="research_agent",
    )
    
    # Agent 2: Analysis Agent
    analysis_agent = ChatAgent(
        chat_client=client,
        instructions="""You are an Analysis Agent specialized in pattern recognition and insight generation.

Your role is to:
1. Review the research findings provided
2. Identify key patterns and connections
3. Generate actionable insights
4. Highlight critical success factors and risks
5. Provide strategic recommendations (250-350 words)

Focus on synthesis and strategic thinking.""",
        name="analysis_agent",
    )
    
    # Agent 3: Writer Agent
    writer_agent = ChatAgent(
        chat_client=client,
        instructions="""You are a Writer Agent specialized in creating comprehensive reports.

Your role is to:
1. Synthesize research and analysis into a cohesive report
2. Structure information clearly with sections
3. Highlight key findings and recommendations
4. Use professional, accessible language
5. Create an executive summary
6. Provide a final report (400-500 words)

Structure: Executive Summary, Key Findings, Analysis, Recommendations, Conclusion.""",
        name="writer_agent",
    )
    
    # Create a sequential workflow
    # Note: In a real workflow implementation, you would use the Workflow class
    # to define the sequence. For DevUI, we'll create a wrapper that executes
    # the agents in sequence when called.
    
    async def sequential_handler(user_message: str) -> str:
        """Execute the three agents in sequence."""
        
        # Step 1: Research
        research_prompt = f"Research the following topic comprehensively:\n\n{user_message}"
        research_response = await research_agent.run(research_prompt)
        research_result = str(research_response)
        
        # Step 2: Analysis (use research findings)
        analysis_prompt = f"""Analyze the following research findings and generate insights:

RESEARCH FINDINGS:
{research_result}

Provide strategic analysis and recommendations."""
        analysis_response = await analysis_agent.run(analysis_prompt)
        analysis_result = str(analysis_response)
        
        # Step 3: Writing (synthesize research + analysis)
        writing_prompt = f"""Create a comprehensive report based on the following:

RESEARCH FINDINGS:
{research_result}

ANALYSIS & INSIGHTS:
{analysis_result}

Synthesize this into a well-structured final report."""
        report_response = await writer_agent.run(writing_prompt)
        final_report = str(report_response)
        
        return final_report
    
    # Create a wrapper agent that executes the sequential workflow
    workflow_agent = ChatAgent(
        chat_client=client,
        instructions="""You are a Sequential Analysis Workflow that coordinates three specialized agents:
1. Research Agent: Gathers comprehensive information
2. Analysis Agent: Generates insights and recommendations  
3. Writer Agent: Creates final structured report

When given a topic, you execute all three agents in sequence and return the final report.""",
        name="sequential_workflow",
    )
    
    # Override the run method to use our sequential handler
    original_run = workflow_agent.run
    async def workflow_run(message: str, **kwargs):
        return await sequential_handler(message)
    workflow_agent.run = workflow_run
    
    return workflow_agent


def main():
    """Launch the sequential workflow in DevUI."""
    from agent_framework.devui import serve
    
    print("\n" + "="*80)
    print("🚀 Sequential Multi-Agent Workflow - DevUI")
    print("="*80)
    print("\n📋 Workflow: Research → Analysis → Writing (Sequential)")
    print("🔧 Using: GitHub Models with Microsoft Agent Framework")
    print("\n🌐 Starting DevUI server...")
    
    # Create the workflow
    workflow = asyncio.run(create_sequential_workflow())
    
    print("\n✅ Sequential workflow created")
    print("\n" + "="*80)
    print("🎯 DevUI Interface")
    print("="*80)
    print("\n🌐 Web UI:  http://localhost:8080")
    print("📡 API:     http://localhost:8080/v1/*")
    print("🔍 Entity:  sequential_workflow")
    
    print("\n" + "="*80)
    print("💡 How to Use")
    print("="*80)
    print("\n1. Open http://localhost:8080 in your browser")
    print("2. Select 'sequential_workflow' from the agent dropdown")
    print("3. Enter a topic to analyze (examples below)")
    print("4. Watch the sequential workflow execute:")
    print("   • Research Agent gathers information")
    print("   • Analysis Agent generates insights")
    print("   • Writer Agent creates final report")
    
    print("\n" + "="*80)
    print("📝 Example Topics to Try")
    print("="*80)
    print("\n🤖 AI/Tech:")
    print("   • AI-powered personal learning assistants")
    print("   • Blockchain in supply chain management")
    print("   • Edge computing for IoT applications")
    
    print("\n🏥 Healthcare:")
    print("   • Telemedicine platforms for rural areas")
    print("   • AI-assisted diagnostic tools")
    print("   • Mental health apps with AI therapy")
    
    print("\n🌱 Sustainability:")
    print("   • Sustainable food packaging solutions")
    print("   • Carbon tracking apps for consumers")
    print("   • Renewable energy micro-grids")
    
    print("\n💼 Business:")
    print("   • B2B SaaS for small businesses")
    print("   • Marketplace platforms for freelancers")
    print("   • Remote team collaboration tools")
    
    print("\n" + "="*80)
    print("⚡ Comparison: Example 03 vs 05")
    print("="*80)
    print("\n📄 Example 03 (Script-based):")
    print("   • Hardcoded topic in Python code")
    print("   • Console output only")
    print("   • Requires code edit + re-run to test new topics")
    print("   • Good for: Automation, CI/CD, scripting")
    
    print("\n🌐 Example 05 (DevUI):")
    print("   • Interactive web interface")
    print("   • Test any topic via browser")
    print("   • Visual conversation history")
    print("   • Real-time execution monitoring")
    print("   • API endpoint for integration")
    print("   • Good for: Development, testing, demos")
    
    print("\n" + "="*80)
    print("🔍 Behind the Scenes")
    print("="*80)
    print("\n⏱️  Execution Flow (Sequential):")
    print("   1. User submits query → Research Agent")
    print("   2. Research completes → Analysis Agent (uses research)")
    print("   3. Analysis completes → Writer Agent (uses both)")
    print("   4. Final report returned to user")
    print("\n⏱️  Total time: ~45-60 seconds (agents wait for each other)")
    print("📊 Compare with Example 06 (parallel) for speed comparison!")
    
    print("\n" + "="*80)
    print("⌨️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    # Launch DevUI server
    serve(
        entities=[workflow],
        port=8080,
        auto_open=True,  # Automatically open browser
    )


if __name__ == "__main__":
    main()

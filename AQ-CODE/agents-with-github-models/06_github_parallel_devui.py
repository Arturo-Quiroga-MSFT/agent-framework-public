#!/usr/bin/env python3
"""
Example 06: Parallel Multi-Agent Execution with DevUI Visualization

This example demonstrates parallel agent execution (like 04_github_parallel_agents.py)
but with DevUI integration for interactive testing and visual debugging.

Key Differences from Example 04:
- DevUI web interface for testing multiple agents
- Choose to interact with individual agents OR trigger parallel execution
- Visual conversation history for each agent
- API endpoint for programmatic access
- Real-time execution monitoring

Parallel Execution: All 4 agents analyze the same topic simultaneously
- Technical Analyst: Architecture and feasibility
- Business Analyst: Market opportunity and ROI
- Risk Analyst: Challenges and mitigation
- Creative Consultant: Innovation and differentiation

DevUI Benefits:
✅ Interactive web interface
✅ Individual agent conversations OR parallel execution
✅ Visual comparison of agent perspectives
✅ Real-time execution monitoring
✅ API access for integration testing
✅ No code changes to test different inputs

Prerequisites:
1. Set up your .env file with GITHUB_TOKEN
2. Install dependencies: pip install -r requirements.txt
3. Install DevUI: pip install agent-framework-devui --pre

Usage:
    python 06_github_parallel_devui.py
    
    Then open http://localhost:8081 in your browser!

Example Prompts to Try:
- "AI-powered personal learning assistant for professionals"
- "Blockchain-based supply chain tracking system"
- "Sustainable urban farming marketplace platform"
"""

import asyncio
import os
from dotenv import load_dotenv

from agent_framework import ChatAgent
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


async def create_specialized_agents() -> list[ChatAgent]:
    """
    Creates four specialized agents for parallel analysis.
    
    Returns:
        List of ChatAgent objects, one for each specialty:
        - Technical Analyst
        - Business Analyst
        - Risk Analyst
        - Creative Consultant
    """
    # Create shared client
    client = create_github_client()
    
    # Agent 1: Technical Analyst
    technical_agent = ChatAgent(
        chat_client=client,
        instructions="""You are a Technical Analyst with deep expertise in software architecture, scalability, and technical implementation.

Your role is to analyze topics from a technical perspective and provide insights on:
- Technical feasibility and architecture requirements
- Technology stack recommendations and rationale
- Scalability and performance considerations
- Technical risks and mitigation strategies
- Implementation timeline and complexity assessment

Guidelines:
1. Be concise but thorough (200-300 words)
2. Use bullet points for clarity
3. Focus on actionable technical insights
4. Highlight critical technical considerations
5. Provide specific technology recommendations

Format your response with clear sections.""",
        name="technical_analyst",
    )
    
    # Agent 2: Business Analyst
    business_agent = ChatAgent(
        chat_client=client,
        instructions="""You are a Business Analyst with expertise in market analysis, business models, and competitive strategy.

Your role is to analyze topics from a business perspective and provide insights on:
- Market opportunity and target audience analysis
- Business model options and revenue potential
- Competitive landscape and differentiation strategies
- Go-to-market strategy recommendations
- Financial projections and ROI estimates

Guidelines:
1. Be concise but thorough (200-300 words)
2. Use bullet points for clarity
3. Focus on actionable business insights
4. Highlight critical market considerations
5. Provide specific business recommendations

Format your response with clear sections.""",
        name="business_analyst",
    )
    
    # Agent 3: Risk Analyst
    risk_agent = ChatAgent(
        chat_client=client,
        instructions="""You are a Risk Analyst with expertise in risk assessment, compliance, and operational security.

Your role is to analyze topics from a risk perspective and provide insights on:
- Operational risks and potential challenges
- Regulatory and compliance requirements
- Security and privacy concerns
- Risk mitigation strategies and contingency plans
- Long-term sustainability considerations

Guidelines:
1. Be concise but thorough (200-300 words)
2. Use bullet points for clarity
3. Focus on actionable risk insights
4. Highlight critical risk factors
5. Provide specific mitigation recommendations

Format your response with clear sections.""",
        name="risk_analyst",
    )
    
    # Agent 4: Creative Consultant
    creative_agent = ChatAgent(
        chat_client=client,
        instructions="""You are a Creative Consultant with expertise in innovation, user experience, and creative problem-solving.

Your role is to analyze topics from a creative perspective and provide insights on:
- Innovative approaches and unique angles
- User experience and engagement strategies
- Creative differentiation opportunities
- Emerging trends and future possibilities
- Unconventional solutions and blue-sky thinking

Guidelines:
1. Be concise but thorough (200-300 words)
2. Use bullet points for clarity
3. Focus on innovative and creative insights
4. Highlight unique differentiation opportunities
5. Provide specific creative recommendations

Format your response with clear sections.""",
        name="creative_consultant",
    )
    
    return [technical_agent, business_agent, risk_agent, creative_agent]


def main():
    """Launch the parallel agents in DevUI."""
    from agent_framework.devui import serve
    
    print("\n" + "="*80)
    print("⚡ Parallel Multi-Agent Analysis - DevUI")
    print("="*80)
    print("\n📋 Agents: 4 specialists (Technical, Business, Risk, Creative)")
    print("🔧 Using: GitHub Models with Microsoft Agent Framework")
    print("\n🌐 Starting DevUI server...")
    
    # Create all agents
    agents = asyncio.run(create_specialized_agents())
    
    print("\n✅ All agents created:")
    print("   • Technical Analyst")
    print("   • Business Analyst")
    print("   • Risk Analyst")
    print("   • Creative Consultant")
    
    print("\n" + "="*80)
    print("🎯 DevUI Interface")
    print("="*80)
    print("\n🌐 Web UI:  http://localhost:8081")
    print("📡 API:     http://localhost:8081/v1/*")
    print("🔍 Agents:  4 individual specialists available")
    
    print("\n" + "="*80)
    print("💡 How to Use - Two Modes")
    print("="*80)
    
    print("\n🎨 MODE 1: Individual Agent Conversations")
    print("─" * 60)
    print("1. Open http://localhost:8081 in your browser")
    print("2. Select ONE agent from the dropdown:")
    print("   • technical_analyst")
    print("   • business_analyst")
    print("   • risk_analyst")
    print("   • creative_consultant")
    print("3. Chat with that specialist about your topic")
    print("4. Get focused insights from their expertise area")
    
    print("\n🚀 MODE 2: Compare Multiple Perspectives")
    print("─" * 60)
    print("1. Open 4 browser tabs/windows")
    print("2. Select different agent in each tab")
    print("3. Ask THE SAME question to all agents")
    print("4. See how each specialist approaches the topic")
    print("5. Compare insights side-by-side")
    
    print("\n" + "="*80)
    print("📝 Example Topics to Try")
    print("="*80)
    
    print("\n🤖 AI Applications:")
    print("   • AI-powered personal learning assistant")
    print("   • Intelligent code review automation tool")
    print("   • AI-driven customer support chatbot")
    
    print("\n🏥 Healthcare:")
    print("   • Telemedicine platform with AI diagnostics")
    print("   • Mental health app with AI therapy")
    print("   • Wearable health monitor with predictive alerts")
    
    print("\n🌱 Sustainability:")
    print("   • Carbon footprint tracking app for businesses")
    print("   • Sustainable fashion marketplace")
    print("   • Smart home energy optimization system")
    
    print("\n💼 Business:")
    print("   • B2B SaaS for project management")
    print("   • Freelancer marketplace with AI matching")
    print("   • Remote team productivity dashboard")
    
    print("\n" + "="*80)
    print("⚡ Parallel vs Sequential Comparison")
    print("="*80)
    
    print("\n📊 Example 05 (Sequential Workflow):")
    print("   • Single workflow entity")
    print("   • Research → Analysis → Writing")
    print("   • Each agent waits for previous")
    print("   • ~45-60 seconds total")
    print("   • Good for: Dependent analysis steps")
    
    print("\n⚡ Example 06 (Parallel Agents):")
    print("   • 4 independent agent entities")
    print("   • All agents work simultaneously")
    print("   • No waiting between agents")
    print("   • ~15-20 seconds per agent")
    print("   • Good for: Multiple perspectives, speed")
    
    print("\n" + "="*80)
    print("🎯 What Each Agent Provides")
    print("="*80)
    
    print("\n🔧 Technical Analyst:")
    print("   • Architecture & tech stack")
    print("   • Scalability & performance")
    print("   • Implementation complexity")
    print("   • Technical risks & mitigation")
    
    print("\n💼 Business Analyst:")
    print("   • Market opportunity sizing")
    print("   • Revenue models & pricing")
    print("   • Competitive positioning")
    print("   • Go-to-market strategy")
    
    print("\n⚖️ Risk Analyst:")
    print("   • Regulatory compliance")
    print("   • Security & privacy risks")
    print("   • Operational challenges")
    print("   • Mitigation strategies")
    
    print("\n🎨 Creative Consultant:")
    print("   • Innovative approaches")
    print("   • User experience ideas")
    print("   • Differentiation opportunities")
    print("   • Emerging trends")
    
    print("\n" + "="*80)
    print("🔍 DevUI Features")
    print("="*80)
    print("\n✅ Interactive chat interface")
    print("✅ Conversation history per agent")
    print("✅ Real-time response streaming")
    print("✅ Multi-turn conversations")
    print("✅ OpenAI-compatible API endpoint")
    print("✅ No code changes to test new prompts")
    
    print("\n" + "="*80)
    print("💡 Pro Tips")
    print("="*80)
    print("\n• Ask follow-up questions to dig deeper")
    print("• Try the same topic with different agents")
    print("• Compare technical vs business perspectives")
    print("• Use creative agent for brainstorming")
    print("• Use risk agent before finalizing plans")
    
    print("\n" + "="*80)
    print("⌨️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    # Launch DevUI server with all agents
    serve(
        entities=agents,
        port=8081,
        auto_open=True,  # Automatically open browser
    )


if __name__ == "__main__":
    main()

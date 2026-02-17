# Copyright (c) Microsoft. All rights reserved.

"""
Interactive Concurrent Agents - DevUI Version

This version provides 5 specialized agents that can be interacted with individually
through the DevUI web interface. Each agent maintains its own conversation history
and can engage in multi-turn dialogues with follow-up questions and clarifications.

Unlike the workflow version (concurrent_agents_devui.py) which processes a single
query through all agents concurrently, this version allows you to:
- Chat with each agent separately in their own conversation thread
- Ask follow-up questions and get contextual responses
- See agent questions and answer them interactively
- Maintain conversation history across multiple exchanges

THE 5 EXPERT AGENTS:
1. 🔬 Market Researcher: Market analysis, opportunities, risks, competitive landscape
2. 📢 Marketing Strategist: Value propositions, messaging, target audiences, campaigns
3. ⚖️ Legal/Compliance Advisor: Regulatory concerns, disclaimers, policy compliance
4. 💰 Financial Analyst: Revenue models, cost structure, ROI, pricing strategies
5. 🏗️ Technical Architect: Architecture, tech stack, scalability, implementation

USAGE PATTERNS:
- Start with one agent (e.g., Researcher) to explore market insights
- Ask follow-up questions: "Can you elaborate on the European market?"
- Get specific clarifications: "What about regulatory requirements in California?"
- Switch to another agent to explore their domain expertise
- Reference previous conversations: "Based on the researcher's analysis..."

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
from pathlib import Path

from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import configure_otel_providers
from azure.identity import AzureCliCredential

# Load environment variables from workflows/.env file
load_dotenv(Path(__file__).parent.parent / ".env")


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


async def create_interactive_agents():
    """Create and return 5 specialized agents for interactive conversations."""
    
    # Initialize Azure OpenAI client
    credential = AzureCliCredential()
    chat_client = AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )
    
    # Create five specialized agents with enhanced instructions for interactive dialogue
    agent_options = {"max_tokens": 600}

    researcher = chat_client.as_agent(
        instructions=(
            "You're an expert market and product researcher with deep knowledge of consumer behavior, "
            "competitive landscapes, and market trends. Your role is to provide data-driven insights, "
            "identify opportunities and risks, and help users understand market dynamics.\n\n"
            "COMMUNICATION STYLE:\n"
            "- Be conversational and engaging while maintaining professionalism\n"
            "- Ask clarifying questions when the user's query is broad or ambiguous\n"
            "- Provide specific examples and actionable recommendations\n"
            "- Reference previous conversation points to build on the discussion\n"
            "- If you need more information, explicitly ask the user for it\n\n"
            "EXPERTISE AREAS:\n"
            "- Market sizing and segmentation\n"
            "- Competitive analysis and positioning\n"
            "- Consumer behavior and trends\n"
            "- Market entry strategies\n"
            "- Risk assessment and opportunity identification\n\n"
            "Remember: You're having a conversation, not writing a one-shot report. Engage with the user, "
            "ask follow-up questions, and help them explore their ideas deeply. "
            "Keep your analysis focused and concise."
        ),
        name="Market_Researcher",
        default_options=agent_options,
    )

    marketer = chat_client.as_agent(
        instructions=(
            "You're a creative marketing strategist with expertise in brand positioning, messaging, "
            "and go-to-market strategies. You help users craft compelling narratives and effective "
            "marketing approaches for their products and services.\n\n"
            "COMMUNICATION STYLE:\n"
            "- Be creative and inspiring while staying grounded in practicality\n"
            "- Ask about target audiences when they're not specified\n"
            "- Provide multiple options and perspectives when appropriate\n"
            "- Build on previous ideas in the conversation\n"
            "- Request more details about positioning, differentiation, or channels as needed\n\n"
            "EXPERTISE AREAS:\n"
            "- Value proposition development\n"
            "- Target audience definition and messaging\n"
            "- Brand positioning and differentiation\n"
            "- Marketing channel strategies (digital, content, social, etc.)\n"
            "- Campaign concepts and creative direction\n"
            "- Messaging frameworks and communication strategies\n\n"
            "Remember: Great marketing comes from understanding the audience and the product deeply. "
            "Don't hesitate to ask questions that will help you provide better recommendations. "
            "Keep your analysis focused and concise."
        ),
        name="Marketing_Strategist",
        default_options=agent_options,
    )

    legal = chat_client.as_agent(
        instructions=(
            "You're a careful legal and compliance advisor specializing in business law, regulations, "
            "and risk management. You help users identify legal considerations, compliance requirements, "
            "and potential liabilities for their business initiatives.\n\n"
            "COMMUNICATION STYLE:\n"
            "- Be thorough but accessible - avoid unnecessary legal jargon\n"
            "- Ask about jurisdiction, industry, and specific use cases for accurate guidance\n"
            "- Clearly distinguish between critical legal requirements and best practices\n"
            "- Reference previous compliance concerns discussed in the conversation\n"
            "- When regulations are complex, break them down into actionable steps\n\n"
            "EXPERTISE AREAS:\n"
            "- Regulatory compliance (FDA, FTC, GDPR, CCPA, etc.)\n"
            "- Intellectual property considerations\n"
            "- Terms of service and privacy policies\n"
            "- Consumer protection laws\n"
            "- Liability and risk mitigation\n"
            "- Industry-specific regulations (healthcare, finance, etc.)\n\n"
            "IMPORTANT DISCLAIMERS:\n"
            "- Always remind users that your guidance is general information, not legal advice\n"
            "- Recommend consulting with licensed attorneys for specific legal matters\n"
            "- Be clear about areas where regulations are complex or jurisdiction-dependent\n\n"
            "Remember: Your goal is to raise awareness of legal considerations and help users "
            "ask the right questions when they consult with their legal team. "
            "Keep your analysis focused and concise."
        ),
        name="Legal_Compliance_Advisor",
        default_options=agent_options,
    )
    
    finance = chat_client.as_agent(
        instructions=(
            "You're a financial analyst and business strategist with expertise in financial modeling, "
            "business economics, and investment analysis. You help users understand the financial "
            "implications of their business decisions and develop sustainable revenue models.\n\n"
            "COMMUNICATION STYLE:\n"
            "- Be analytical but practical - focus on actionable financial insights\n"
            "- Ask about cost assumptions, revenue expectations, and timeline when not provided\n"
            "- Use specific numbers and ranges when possible\n"
            "- Build financial scenarios based on the conversation history\n"
            "- Request clarification on business model details as needed\n\n"
            "EXPERTISE AREAS:\n"
            "- Revenue models and pricing strategies\n"
            "- Cost structure analysis (COGS, fixed costs, variable costs)\n"
            "- Break-even analysis and unit economics\n"
            "- ROI and payback period calculations\n"
            "- Financial projections and scenario planning\n"
            "- Funding requirements and capital structure\n"
            "- Key financial metrics and KPIs\n\n"
            "Remember: Good financial analysis requires understanding the business context. "
            "Ask questions to gather the information you need for meaningful insights. "
            "Keep your analysis focused and concise."
        ),
        name="Financial_Analyst",
        default_options=agent_options,
    )
    
    technical = chat_client.as_agent(
        instructions=(
            "You're a technical architect and engineering lead with expertise in system design, "
            "technology selection, and software development. You help users make informed technical "
            "decisions and understand implementation considerations for their products.\n\n"
            "COMMUNICATION STYLE:\n"
            "- Be technical but accessible - explain concepts clearly\n"
            "- Ask about scale, performance requirements, and constraints when not specified\n"
            "- Provide multiple technology options with trade-offs\n"
            "- Reference technical decisions discussed earlier in the conversation\n"
            "- Request details about existing infrastructure, team skills, or integration needs\n\n"
            "EXPERTISE AREAS:\n"
            "- System architecture and design patterns\n"
            "- Technology stack recommendations (frontend, backend, databases, cloud)\n"
            "- Scalability and performance optimization\n"
            "- Security architecture and best practices\n"
            "- API design and integration strategies\n"
            "- DevOps, CI/CD, and deployment strategies\n"
            "- Technical debt and maintenance considerations\n\n"
            "Remember: The best technical solution depends on context - team capabilities, "
            "timeline, budget, and specific requirements. Ask questions to understand these factors. "
            "Keep your analysis focused and concise."
        ),
        name="Technical_Architect",
        default_options=agent_options,
    )
    
    # Return all agents as a list
    return [researcher, marketer, legal, finance, technical]


def launch_devui():
    """Launch the DevUI interface with the 5 interactive agents."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Create the agents asynchronously
    agents = asyncio.run(create_interactive_agents())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Interactive Multi-Agent Team in DevUI")
    print("=" * 70)
    print("✅ Mode: Interactive Individual Agents")
    print("✅ Agents: 5 specialized experts (each with their own conversation)")
    print("✅ Web UI: http://localhost:8092")
    print("✅ API: http://localhost:8092/v1/*")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    print("=" * 70)
    print()
    print("👥 YOUR EXPERT TEAM:")
    print()
    print("🔬 Market_Researcher")
    print("   • Market analysis, competitive landscape, opportunities & risks")
    print("   • Example: 'What's the market size for electric bikes in Europe?'")
    print()
    print("📢 Marketing_Strategist")
    print("   • Value propositions, messaging, target audiences, campaigns")
    print("   • Example: 'Help me craft a value proposition for Gen Z users'")
    print()
    print("⚖️ Legal_Compliance_Advisor")
    print("   • Regulatory compliance, disclaimers, policy concerns, risk management")
    print("   • Example: 'What are the GDPR implications for my app?'")
    print()
    print("💰 Financial_Analyst")
    print("   • Revenue models, cost structure, ROI, pricing strategies")
    print("   • Example: 'What pricing model would work for a SaaS product?'")
    print()
    print("🏗️ Technical_Architect")
    print("   • System design, tech stack, scalability, implementation")
    print("   • Example: 'What tech stack would you recommend for a mobile app?'")
    print()
    print("=" * 70)
    print("💡 USAGE TIPS:")
    print()
    print("1️⃣ Select an agent to start a conversation")
    print("2️⃣ Ask your initial question or describe your idea")
    print("3️⃣ The agent will respond and may ask clarifying questions")
    print("4️⃣ Continue the conversation - ask follow-ups, provide details")
    print("5️⃣ Switch agents anytime to explore different perspectives")
    print()
    print("🎯 EXAMPLE CONVERSATIONS:")
    print()
    print("→ With Researcher:")
    print("  You: 'I'm launching a budget e-bike for urban commuters'")
    print("  Agent: [Provides market analysis and asks about target market]")
    print("  You: 'Focused on US cities, priced under $1500'")
    print("  Agent: [Gives specific insights and competitive analysis]")
    print()
    print("→ With Marketer:")
    print("  You: 'How should I position this e-bike?'")
    print("  Agent: [Asks about differentiation and target audience]")
    print("  You: 'Targeting young professionals who want to skip traffic'")
    print("  Agent: [Develops messaging and value props]")
    print()
    print("=" * 70)
    print("⌨️  Press Ctrl+C to stop the server")
    print()
    
    # Launch the DevUI server with all agents
    serve(
        entities=agents,
        port=8092,
        auto_open=True,
        instrumentation_enabled=enable_devui_tracing,
    )


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down interactive agents server...")

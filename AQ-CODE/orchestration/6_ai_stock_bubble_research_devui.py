# Copyright (c) Microsoft. All rights reserved.

"""
AI Stock Bubble Research Workflow - DevUI Version with Web Search

This workflow creates a specialized team of 5 financial research experts to analyze
whether AI companies are overvalued and if a stock market bubble is forming.

The workflow uses a fan-out/fan-in pattern where:
- User provides a research question about AI stock valuations
- Input is dispatched to all 5 specialized agents concurrently
- Each agent uses Bing web search to gather real-time market data
- Results are aggregated into a comprehensive research report

RESEARCH AGENTS:
- Market Analyst: Stock valuations, P/E ratios, market cap analysis
- Technical Analyst: Chart patterns, momentum indicators, market sentiment
- Fundamental Analyst: Revenue, earnings, business models, competitive analysis
- Economic Historian: Historical bubble patterns, market cycles, warning signs
- Risk Analyst: Systemic risks, correlation analysis, portfolio exposure

PREREQUISITES:
- Azure OpenAI access configured via .env file
- Azure CLI authentication: Run 'az login'
- Bing Grounding connection configured in Azure AI Foundry
- BING_CONNECTION_ID in environment variables

TRACING OPTIONS:
1. Console Tracing: Set ENABLE_CONSOLE_TRACING=true (simplest)
2. Azure AI Tracing: Set ENABLE_AZURE_AI_TRACING=true (requires Application Insights)
3. OTLP Tracing: Set OTLP_ENDPOINT (e.g., http://localhost:4317 for Jaeger/Zipkin)
4. DevUI Tracing: Set ENABLE_DEVUI_TRACING=true (view in DevUI interface)
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import Message, Executor, WorkflowContext, handler, AgentExecutorRequest, AgentExecutorResponse
from agent_framework.azure import AzureAIAgentClient
from agent_framework.observability import configure_otel_providers
from agent_framework._workflows import WorkflowBuilder
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel, Field

# Load environment variables from orchestration/.env file (same directory)
load_dotenv(Path(__file__).parent / ".env")


class AIStockResearchInput(BaseModel):
    """Input model for AI stock bubble research."""
    
    query: str = Field(
        default="Is there an AI stock bubble forming in 2025? Analyze major AI companies for overvaluation.",
        description="Research question about AI stock valuations, bubble indicators, or market risks",
        examples=[
            "Is there an AI stock bubble forming in 2025? Analyze major AI companies for overvaluation.",
            "Compare current AI stock valuations to historical tech bubbles (dot-com, 2000)",
            "What are the P/E ratios and market caps of leading AI companies? Are they sustainable?",
            "Analyze NVIDIA, Microsoft, Google, and OpenAI-related stocks for bubble indicators",
            "What percentage of S&P 500 is AI-related? Is this concentration a systemic risk?",
            "Are AI company revenues justifying their stock prices?",
            "What warning signs suggest an AI market correction is coming?",
            "How do current AI stock valuations compare to historical norms?"
        ]
    )


def format_research_report(results) -> str:
    """Format research agent outputs into a comprehensive report and save to file.
    
    Args:
        results: List of AgentExecutorResponse objects from concurrent agents
        
    Returns:
        Formatted research report string
    """
    output_lines = []
    output_lines.append("=" * 100)
    output_lines.append("📊 AI STOCK BUBBLE RESEARCH REPORT")
    output_lines.append(f"🗓️  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 100)
    output_lines.append("")
    output_lines.append("⚠️  DISCLAIMER: This report is for research purposes only and does not constitute financial advice.")
    output_lines.append("   Consult a qualified financial advisor before making investment decisions.")
    output_lines.append("")
    
    # Process each agent's response
    for result in results:
        # Get the agent's messages
        messages = getattr(result.agent_response, "messages", [])
        
        # Find the final assistant message
        for msg in reversed(messages):
            if hasattr(msg, "author_name") and msg.author_name and msg.author_name != "user":
                agent_name = msg.author_name.upper()
                
                # Add emoji based on agent type
                emoji = {
                    "MARKET_ANALYST": "📈",
                    "TECHNICAL_ANALYST": "📉",
                    "FUNDAMENTAL_ANALYST": "💼",
                    "ECONOMIC_HISTORIAN": "📚",
                    "RISK_ANALYST": "⚠️"
                }.get(agent_name, "📊")
                
                # Readable names
                display_name = {
                    "MARKET_ANALYST": "MARKET VALUATION ANALYSIS",
                    "TECHNICAL_ANALYST": "TECHNICAL & SENTIMENT ANALYSIS",
                    "FUNDAMENTAL_ANALYST": "FUNDAMENTAL BUSINESS ANALYSIS",
                    "ECONOMIC_HISTORIAN": "HISTORICAL BUBBLE COMPARISON",
                    "RISK_ANALYST": "RISK & PORTFOLIO ANALYSIS"
                }.get(agent_name, agent_name)
                
                output_lines.append("─" * 100)
                output_lines.append(f"{emoji} {display_name}")
                output_lines.append("─" * 100)
                output_lines.append("")
                output_lines.append(msg.text)
                output_lines.append("")
                break  # Only use the final message
    
    output_lines.append("=" * 100)
    output_lines.append("✅ Research Complete - All perspectives analyzed with real-time web data")
    output_lines.append("=" * 100)
    output_lines.append("")
    output_lines.append("📌 SUMMARY CONSIDERATIONS:")
    output_lines.append("   • Review all five analyses for a comprehensive view")
    output_lines.append("   • Compare current metrics to historical bubble indicators")
    output_lines.append("   • Consider both fundamental value and market sentiment")
    output_lines.append("   • Evaluate systemic risks and portfolio exposure")
    output_lines.append("   • Monitor for warning signs: extreme P/E ratios, revenue-valuation gaps, market concentration")
    output_lines.append("")
    
    formatted_output = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent.parent.parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"ai_stock_bubble_research_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"\n💾 Research report saved to: {output_file}")
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


async def create_ai_stock_research_workflow():
    """Create and return an AI stock bubble research workflow for DevUI."""
    
    # Initialize Azure AI Agent client (for Bing Grounding support)
    # Note: Bing Grounding requires a compatible model like gpt-4.1, gpt-4o, gpt-4o-mini, or gpt-4-turbo
    credential = DefaultAzureCredential()
    agent_client = AzureAIAgentClient(
        credential=credential,
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        model_deployment_name=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1"),
    )
    
    # Create Bing web search tool for real-time market data
    bing_connection_id = os.environ.get("BING_CONNECTION_ID", "")
    bing_search_tool = {
        "type": "bing_grounding",
        "bing_grounding": {
            "search_configurations": [
                {"connection_id": bing_connection_id}
            ]
        },
    }
    
    # Create five specialized financial research agents with web search capability
    agent_options = {"max_tokens": 600}

    market_analyst = agent_client.as_agent(
        instructions=(
            "You're a senior market analyst specializing in technology stock valuations and bubble detection. "
            "Use web search to find current stock prices, P/E ratios, market caps, and valuation metrics for major AI companies "
            "(NVIDIA, Microsoft, Google, Meta, Amazon, Tesla, OpenAI-related stocks). "
            "Compare current valuations to historical averages and industry norms. "
            "Calculate metrics like: Price-to-Earnings ratios, Price-to-Sales ratios, market cap as % of GDP, "
            "revenue multiples, and growth rates. Identify overvaluation warning signs. "
            "Provide specific numbers, company names, and current market data from your web searches. "
            "Be analytical and cite your sources with recent dates. "
            "Keep your analysis focused and concise."
        ),
        name="market_analyst",
        tools=bing_search_tool,
        default_options=agent_options,
    )

    technical_analyst = agent_client.as_agent(
        instructions=(
            "You're a technical analyst and market sentiment expert focusing on AI stock momentum and crowd behavior. "
            "Use web search to find: recent price movements, trading volumes, RSI indicators, moving averages, "
            "analyst sentiment, social media trends, and retail investor behavior around AI stocks. "
            "Look for technical bubble indicators: parabolic price moves, extreme RSI, "
            "retail euphoria, insider selling, excessive IPO activity, and FOMO buying patterns. "
            "Search for recent news about AI stock market sentiment, Reddit/Twitter discussions, "
            "and institutional investor positioning. Provide current market psychology insights. "
            "Be data-driven and reference recent technical signals with dates. "
            "Keep your analysis focused and concise."
        ),
        name="technical_analyst",
        tools=bing_search_tool,
        default_options=agent_options,
    )

    fundamental_analyst = agent_client.as_agent(
        instructions=(
            "You're a fundamental analyst specializing in AI company business models and profitability. "
            "Use web search to find: quarterly earnings, revenue growth, profit margins, cash flow, "
            "R&D spending, customer acquisition costs, and business fundamentals for major AI companies. "
            "Evaluate: Are revenues growing fast enough to justify valuations? Are companies profitable? "
            "What are unit economics? Is growth sustainable or hype-driven? "
            "Search for recent earnings reports, revenue projections, competitive threats, "
            "and business model sustainability. Compare AI company fundamentals to their stock prices. "
            "Look for red flags: unprofitable growth, unsustainable burn rates, or revenue-valuation gaps. "
            "Provide specific financial metrics from recent quarters with sources. "
            "Keep your analysis focused and concise."
        ),
        name="fundamental_analyst",
        tools=bing_search_tool,
        default_options=agent_options,
    )
    
    economic_historian = agent_client.as_agent(
        instructions=(
            "You're an economic historian and bubble expert specializing in tech market cycles. "
            "Use web search to compare current AI stock situation to historical bubbles: "
            "1) Dot-com bubble (1999-2000), 2) Housing bubble (2008), 3) Crypto bubble (2021), 4) Previous tech manias. "
            "Search for: historical P/E ratios during bubbles, market cap concentrations, "
            "IPO activity patterns, retail participation rates, and warning signs that preceded crashes. "
            "Identify common bubble characteristics: irrational exuberance, 'new paradigm' narratives, "
            "extreme valuations, leverage buildup, and contagion risks. "
            "Draw parallels between past bubbles and current AI stock market. "
            "Provide historical comparisons with specific years, events, and data points from your research. "
            "Keep your analysis focused and concise."
        ),
        name="economic_historian",
        tools=bing_search_tool,
        default_options=agent_options,
    )
    
    risk_analyst = agent_client.as_agent(
        instructions=(
            "You're a risk management specialist focusing on systemic market risks and portfolio exposure. "
            "Use web search to analyze: AI stock concentration in major indices (S&P 500, NASDAQ), "
            "cross-sector correlations, leverage in the system, derivative exposure, "
            "and potential cascade effects if AI stocks correct. "
            "Search for: percentage of market cap in AI stocks, institutional ownership concentration, "
            "margin debt levels, options activity, and ETF flows into AI sectors. "
            "Evaluate systemic risks: What happens if NVIDIA drops 50%? What's the domino effect? "
            "Are pension funds, mutual funds, and retail investors over-exposed? "
            "Look for liquidity risks, crowding, and contagion pathways. "
            "Provide risk metrics, concentration data, and potential scenario impacts from your research. "
            "Quantify portfolio exposure and diversification risks. "
            "Keep your analysis focused and concise."
        ),
        name="risk_analyst",
        tools=bing_search_tool,
        default_options=agent_options,
    )
    
    # Build the research workflow with structured input handling
    # Create custom dispatcher that handles AIStockResearchInput
    class ResearchDispatcher(Executor):
        """Dispatcher that extracts query from AIStockResearchInput and forwards to agents."""
        
        @handler
        async def dispatch(self, input_data: AIStockResearchInput, ctx: WorkflowContext) -> None:
            """Extract query and send to all research agents.
            
            Args:
                input_data: AIStockResearchInput with query field
                ctx: WorkflowContext for dispatching to agents
            """
            request = AgentExecutorRequest(
                messages=[Message("user", text=input_data.query)],
                should_respond=True
            )
            await ctx.send_message(request)
    
    # Build workflow with custom components
    dispatcher = ResearchDispatcher(id="research_dispatcher")
    
    # Create custom aggregator executor
    class ResearchAggregator(Executor):
        """Aggregator that formats results from all research agents."""
        
        @handler
        async def aggregate(self, results: list[AgentExecutorResponse], ctx: WorkflowContext) -> None:
            """Aggregate results from all agents and format report.
            
            Args:
                results: List of AgentExecutorResponse objects from agents
                ctx: WorkflowContext for yielding output
            """
            formatted_output = format_research_report(results)
            await ctx.yield_output(formatted_output)
    
    aggregator = ResearchAggregator(id="research_aggregator")
    
    # Use WorkflowBuilder to create the complete workflow
    builder = WorkflowBuilder(start_executor=dispatcher)
    
    # Add all research agent participants
    agents = [
        market_analyst,
        technical_analyst,
        fundamental_analyst,
        economic_historian,
        risk_analyst
    ]
    builder.add_fan_out_edges(dispatcher, agents)
    
    # Add aggregator
    builder.add_fan_in_edges(agents, aggregator)
    
    workflow = builder.build()
    
    return workflow


def launch_devui():
    """Launch the DevUI interface with the AI stock research workflow."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Verify Bing connection is configured
    if not os.environ.get("BING_CONNECTION_ID"):
        print("\n⚠️  WARNING: BING_CONNECTION_ID not found in environment variables!")
        print("   Web search functionality requires Bing Grounding connection.")
        print("   Please configure in Azure AI Foundry and set BING_CONNECTION_ID.\n")
    
    # Display model configuration
    model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "unknown")
    print("\n" + "=" * 90)
    print("🔧 MODEL CONFIGURATION")
    print("=" * 90)
    print(f"📌 Model: {model}")
    if model in ["gpt-4.1", "gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]:
        print("✅ Model supports Bing Grounding web search")
    else:
        print("⚠️  WARNING: This model may not support Bing Grounding tools")
    print("=" * 90)
    print()
    
    # Create the workflow asynchronously
    workflow = asyncio.run(create_ai_stock_research_workflow())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 90)
    print("🚀 Launching AI Stock Bubble Research Workflow in DevUI")
    print("=" * 90)
    print("✅ Workflow Type: AI Stock Market Analysis with Web Search (Concurrent)")
    print("✅ Participants: 5 specialized financial research agents")
    print("✅ Data Source: Real-time web search via Bing Grounding")
    print("✅ Web UI: http://localhost:8095")
    print("✅ API: http://localhost:8095/v1/*")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    print("=" * 90)
    print()
    print("💡 Example Research Questions:")
    print()
    print("📊 Valuation Analysis:")
    print("   - Is there an AI stock bubble forming in 2025?")
    print("   - What are the P/E ratios of NVIDIA, Microsoft, and Google?")
    print("   - Compare AI stock valuations to historical tech bubbles")
    print()
    print("📈 Market Concentration:")
    print("   - What percentage of S&P 500 is AI-related stocks?")
    print("   - Analyze market cap concentration risk in AI sector")
    print("   - Are institutional investors over-exposed to AI stocks?")
    print()
    print("⚠️  Warning Signs:")
    print("   - What bubble indicators are present in AI stocks?")
    print("   - Compare current AI hype to dot-com bubble of 2000")
    print("   - Are AI company revenues justifying their stock prices?")
    print()
    print("🔍 Company Analysis:")
    print("   - Analyze NVIDIA for overvaluation signs")
    print("   - Compare Microsoft's AI revenue to its AI stock premium")
    print("   - What are the fundamentals of major AI chip makers?")
    print()
    print("⚡ Each query will be analyzed by 5 financial experts:")
    print("   • Market Analyst: Valuations, P/E ratios, current stock prices")
    print("   • Technical Analyst: Chart patterns, sentiment, momentum signals")
    print("   • Fundamental Analyst: Revenue, earnings, business models")
    print("   • Economic Historian: Historical bubble comparisons, warning signs")
    print("   • Risk Analyst: Systemic risks, portfolio exposure, contagion")
    print()
    print("🌐 All agents use real-time web search to gather current market data")
    print()
    print("⌨️  Press Ctrl+C to stop the server")
    print()
    
    # Launch the DevUI server (different port than healthcare workflow)
    serve(
        entities=[workflow],
        port=8095,
        auto_open=True,
        instrumentation_enabled=enable_devui_tracing,
    )


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AI stock research workflow server...")

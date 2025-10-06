# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Agent with Bing Grounding - DevUI Version with Tracing

This version of azure_ai_with_bing_grounding.py is instrumented to work with DevUI
for visualization and debugging. It creates a persistent agent that can search the web
using Bing Grounding and be interacted with through the DevUI web interface.

PREREQUISITES:
1. Bing Grounding connection in your Azure AI project
2. BING_CONNECTION_ID environment variable set in .env
3. Azure credentials configured (az login)

TRACING OPTIONS:
1. Console Tracing: Set ENABLE_CONSOLE_TRACING=true (simplest)
2. Azure AI Tracing: Set ENABLE_AZURE_AI_TRACING=true (requires Application Insights)
3. OTLP Tracing: Set OTLP_ENDPOINT (e.g., http://localhost:4317 for Jaeger/Zipkin)
4. DevUI Tracing: Set ENABLE_DEVUI_TRACING=true (view in DevUI interface)

Note: This uses a synchronous wrapper around the async Azure AI client.
"""

import asyncio
import os
from contextlib import AsyncExitStack
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import ChatAgent, HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient
from agent_framework.observability import get_tracer, setup_observability
from azure.identity.aio import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id

# Load environment variables from .env file in the current directory
load_dotenv(Path(__file__).parent / ".env")


def setup_tracing():
    """Set up tracing based on environment variables.
    
    Priority order:
    1. Azure AI tracing (ENABLE_AZURE_AI_TRACING=true) - handled in create_bing_agent
    2. OTLP endpoint (OTLP_ENDPOINT)
    3. Application Insights (APPLICATIONINSIGHTS_CONNECTION_STRING)
    4. Console tracing (ENABLE_CONSOLE_TRACING=true)
    """
    # Check if Azure AI tracing is enabled (handled separately in agent creation)
    if os.environ.get("ENABLE_AZURE_AI_TRACING", "").lower() == "true":
        print("📊 Tracing Mode: Azure AI (Application Insights)")
        print("   Traces will be sent to Azure Application Insights in your AI project")
        return
    
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
    print("   - ENABLE_AZURE_AI_TRACING=true (requires App Insights in Azure AI project)")
    print("   - OTLP_ENDPOINT=http://localhost:4317 (requires OTLP receiver)")
    print("   - APPLICATIONINSIGHTS_CONNECTION_STRING=<your-connection-string>")
    print("   - ENABLE_CONSOLE_TRACING=true (console output)")


async def create_bing_agent() -> ChatAgent:
    """Create and return a Bing search agent for DevUI (async version)."""
    # Create async context stack for managing resources
    stack = AsyncExitStack()
    
    # Initialize async credential
    credential = await stack.enter_async_context(AzureCliCredential())
    
    # Initialize Azure AI client with async credential
    client = await stack.enter_async_context(
        AzureAIAgentClient(
            async_credential=credential,
            project_endpoint=os.environ.get("AZURE_AI_PROJECT_ENDPOINT"),
            model_deployment_name=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        )
    )
    
    # Set up Azure AI tracing if enabled
    if os.environ.get("ENABLE_AZURE_AI_TRACING", "").lower() == "true":
        try:
            await client.setup_azure_ai_observability()
            print("✅ Azure AI tracing configured successfully")
        except Exception as e:
            print(f"⚠️  Failed to setup Azure AI tracing: {e}")
            print("   Make sure Application Insights is attached to your Azure AI project")
    
    # Check if Bing connection is configured
    bing_connection_id = os.environ.get("BING_CONNECTION_ID")
    if not bing_connection_id:
        print("⚠️  Warning: BING_CONNECTION_ID not set in .env")
        print("   The agent will be created but web search may not work")
        print("   To enable Bing search:")
        print("   1. Go to Azure AI Studio → Your Project → Connected resources")
        print("   2. Add 'Grounding with Bing Search' connection")
        print("   3. Copy connection ID to .env as BING_CONNECTION_ID")
    else:
        print("🔍 Bing Search: Enabled")
        print(f"   Connection ID: ...{bing_connection_id[-40:]}")
    
    # Create Bing Grounding search tool
    bing_search_tool = HostedWebSearchTool(
        name="BingGroundingSearch",
        description="Search the web for current, up-to-date information using Bing. Use this when you need real-time data, recent news, current events, or information that may have changed recently.",
    )
    
    # Create agent with the client and search tool
    agent = await stack.enter_async_context(
        client.create_agent(
            name="BingSearchAgent",
            instructions="""
            You are a helpful research assistant with access to real-time web search through Bing.
            
            Your capabilities:
            - Search the web for current, up-to-date information
            - Find recent news and current events
            - Look up facts that may have changed recently
            - Research topics that require fresh information
            
            Guidelines:
            - Always use the search tool when asked about current events, news, or recent information
            - Cite your sources and mention where the information comes from
            - Be clear when information comes from web search vs. your training data
            - If search results are unclear or contradictory, mention that
            - Provide well-organized, informative responses
            - When appropriate, include relevant links or sources
            """,
            tools=bing_search_tool,
        )
    )
    
    # Store the stack so we can close it later
    agent._devui_stack = stack
    
    return agent


def launch_devui():
    """Launch the DevUI interface with the Bing search agent."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Create the agent asynchronously
    agent = asyncio.run(create_bing_agent())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Azure AI Bing Search Agent in DevUI")
    print("=" * 70)
    print(f"✅ Agent Name: BingSearchAgent")
    print(f"✅ Tools: Bing Grounding Web Search")
    print(f"✅ Web UI: http://localhost:8091")
    print(f"✅ API: http://localhost:8091/v1/*")
    print(f"✅ Entity ID: agent_BingSearchAgent")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    else:
        print("   → Set ENABLE_DEVUI_TRACING=true to enable")
    print("=" * 70)
    print("\n💡 Try these queries in the DevUI:")
    print("   - What's the latest news about AI?")
    print("   - Who won the Nobel Prize in Physics this year?")
    print("   - What's the current weather in Tokyo?")
    print("   - What are the top trending topics on social media today?")
    print("\n⌨️  Press Ctrl+C to stop the server\n")
    
    try:
        # Launch the DevUI server with tracing enabled if configured
        serve(
            entities=[agent], 
            port=8091, 
            auto_open=True,
            tracing_enabled=enable_devui_tracing
        )
    finally:
        # Clean up resources
        if hasattr(agent, '_devui_stack'):
            asyncio.run(agent._devui_stack.aclose())


async def test_agent():
    """Test the agent programmatically before launching DevUI."""
    print("\n🧪 Testing Bing search agent functionality with tracing...")
    
    # Set up tracing
    setup_tracing()
    
    agent = await create_bing_agent()
    
    try:
        test_queries = [
            "What's the latest news about artificial intelligence?",
            "What's the current weather in Seattle?",
        ]
        
        # Create a span for the entire test session
        with get_tracer().start_as_current_span("Bing Agent Test Session", kind=SpanKind.CLIENT) as span:
            trace_id = format_trace_id(span.get_span_context().trace_id)
            print(f"🔍 Trace ID: {trace_id}")
            print("   Use this ID to find traces in your observability backend\n")
            
            for query in test_queries:
                print(f"\n👤 User: {query}")
                print("🤖 Agent: ", end="", flush=True)
                
                response = await agent.run(query)
                # Truncate long responses for readability
                response_text = response.text
                if len(response_text) > 500:
                    print(f"{response_text[:500]}...")
                else:
                    print(response_text)
        
        print("\n✅ Agent test completed successfully!")
        print(f"🔍 All operations traced under ID: {trace_id}\n")
    finally:
        # Clean up resources
        if hasattr(agent, '_devui_stack'):
            await agent._devui_stack.aclose()


def main():
    """Main entry point."""
    import sys
    
    # Check if we should test or launch DevUI
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run async test
        asyncio.run(test_agent())
    else:
        # Launch DevUI (synchronous)
        launch_devui()


if __name__ == "__main__":
    main()

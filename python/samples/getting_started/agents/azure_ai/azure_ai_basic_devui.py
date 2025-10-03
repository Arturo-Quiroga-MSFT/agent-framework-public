# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Agent Basic Example - DevUI Version with Tracing

This version of azure_ai_basic.py is instrumented to work with DevUI
for visualization and debugging. It creates a persistent agent that can
be interacted with through the DevUI web interface.

WEATHER DATA:
- Uses real weather data from OpenWeatherMap API (if OPENWEATHER_API_KEY is set)
- Falls back to mock data if API key is not configured
- Get free API key at: https://openweathermap.org/api

TRACING OPTIONS:
1. Console Tracing: Set ENABLE_CONSOLE_TRACING=true (simplest)
2. Azure AI Tracing: Set ENABLE_AZURE_AI_TRACING=true (requires Application Insights in Azure AI project)
3. OTLP Tracing: Set OTLP_ENDPOINT (e.g., http://localhost:4317 for Jaeger/Zipkin)
4. Application Insights: Set APPLICATIONINSIGHTS_CONNECTION_STRING

Note: This uses a synchronous wrapper around the async Azure AI client.
"""

import asyncio
import os
from contextlib import AsyncExitStack
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from agent_framework.observability import get_tracer, setup_observability
from azure.identity.aio import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id

# Load environment variables from .env file in the current directory
load_dotenv(Path(__file__).parent / ".env")

# Import weather functions from shared utilities
from shared_utils import get_real_weather, get_mock_weather


def setup_tracing():
    """Set up tracing based on environment variables.
    
    Priority order:
    1. Azure AI tracing (ENABLE_AZURE_AI_TRACING=true) - handled in create_weather_agent
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


async def create_weather_agent() -> ChatAgent:
    """Create and return a weather agent for DevUI (async version)."""
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
    
    # Determine which weather function to use
    has_api_key = bool(os.environ.get("OPENWEATHER_API_KEY"))
    weather_function = get_real_weather if has_api_key else get_mock_weather
    weather_type = "real-time" if has_api_key else "mock"
    
    print(f"🌤️  Weather data: Using {weather_type} weather data")
    if not has_api_key:
        print("   💡 Tip: Set OPENWEATHER_API_KEY in .env for real weather data")
        print("   Get free API key at: https://openweathermap.org/api")
    
    # Create agent with the client
    agent = await stack.enter_async_context(
        client.create_agent(
            name="WeatherAgent",
            instructions=f"""
            You are a helpful weather assistant. You can provide weather information
            for any location using the get_weather tool.
            
            Note: You are currently using {weather_type} weather data.
            
            Guidelines:
            - Always be friendly and informative
            - When users ask about weather, use the tool to get the information
            - Provide helpful context about the weather conditions
            - If asked about multiple locations, check each one
            - Present the weather information in a clear, easy-to-read format
            """,
            tools=weather_function,
        )
    )
    
    # Store the stack so we can close it later
    agent._devui_stack = stack
    
    return agent


def launch_devui():
    """Launch the DevUI interface with the weather agent."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Create the agent asynchronously
    agent = asyncio.run(create_weather_agent())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Azure AI Weather Agent in DevUI")
    print("=" * 70)
    print(f"✅ Agent Name: WeatherAgent")
    print(f"✅ Tools: get_weather")
    print(f"✅ Web UI: http://localhost:8090")
    print(f"✅ API: http://localhost:8090/v1/*")
    print(f"✅ Entity ID: agent_WeatherAgent")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    else:
        print("   → Set ENABLE_DEVUI_TRACING=true to enable")
    print("=" * 70)
    print("\n💡 Try these queries in the DevUI:")
    print("   - What's the weather like in Seattle?")
    print("   - Tell me the weather in New York and Los Angeles")
    print("   - Is it sunny in Miami?")
    print("\n⌨️  Press Ctrl+C to stop the server\n")
    
    try:
        # Launch the DevUI server with tracing enabled if configured
        serve(
            entities=[agent], 
            port=8090, 
            auto_open=True,
            tracing_enabled=enable_devui_tracing
        )
    finally:
        # Clean up resources
        if hasattr(agent, '_devui_stack'):
            asyncio.run(agent._devui_stack.aclose())


async def test_agent():
    """Test the agent programmatically before launching DevUI."""
    print("\n🧪 Testing agent functionality with tracing...")
    
    # Set up tracing
    setup_tracing()
    
    agent = await create_weather_agent()
    
    try:
        test_queries = [
            "What's the weather like in Seattle?",
            "How's the weather in Tokyo?",
        ]
        
        # Create a span for the entire test session
        with get_tracer().start_as_current_span("Agent Test Session", kind=SpanKind.CLIENT) as span:
            trace_id = format_trace_id(span.get_span_context().trace_id)
            print(f"🔍 Trace ID: {trace_id}")
            print("   Use this ID to find traces in your observability backend\n")
            
            for query in test_queries:
                print(f"\n👤 User: {query}")
                print("🤖 Agent: ", end="", flush=True)
                
                response = await agent.run(query)
                print(response.text)
        
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

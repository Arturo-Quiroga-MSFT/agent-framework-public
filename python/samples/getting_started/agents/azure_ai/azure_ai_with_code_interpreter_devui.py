# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Agent with Code Interpreter - DevUI Version with Tracing

This version of azure_ai_with_code_interpreter.py is instrumented to work with DevUI
for visualization and debugging. It creates a persistent agent with code execution
capabilities that can be interacted with through the DevUI web interface.

PREREQUISITES:
1. Azure AI project configured with code interpreter enabled
2. Azure credentials configured (az login)

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
from agent_framework import ChatAgent, HostedCodeInterpreterTool
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
    1. Azure AI tracing (ENABLE_AZURE_AI_TRACING=true) - handled in create_code_agent
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


async def create_code_agent() -> ChatAgent:
    """Create and return a code interpreter agent for DevUI (async version)."""
    # Create async context stack for managing resources
    stack = AsyncExitStack()
    
    # Initialize async credential
    credential = await stack.enter_async_context(AzureCliCredential())
    
    # Check if Azure AI tracing is enabled
    enable_azure_tracing = os.environ.get("ENABLE_AZURE_AI_TRACING", "").lower() == "true"
    
    # Initialize Azure AI client with async credential
    client = await stack.enter_async_context(
        AzureAIAgentClient(
            async_credential=credential,
            project_endpoint=os.environ.get("AZURE_AI_PROJECT_ENDPOINT"),
            model_deployment_name=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
            enable_tracing=enable_azure_tracing,
        )
    )
    
    # Create Code Interpreter tool
    code_tool = HostedCodeInterpreterTool()
    
    # Create agent with the client and code interpreter tool (not awaitable)
    agent = client.create_agent(
        name="CodeInterpreterAgent",
        instructions="""
        You are an expert programming assistant with access to a Python code interpreter.
        
        Your capabilities:
        - Write and execute Python code to solve complex problems
        - Perform data analysis and create visualizations
        - Implement algorithms and mathematical computations
        - Debug and optimize code
        - Explain your code and approach clearly
        
        Guidelines:
        - Always show your code before executing it
        - Explain your approach and reasoning
        - Break down complex problems into steps
        - Provide well-commented, clean code
        - Use appropriate data structures and algorithms
        - Create visualizations when helpful
        - Handle edge cases and errors gracefully
        """,
        tools=code_tool,
    )
    
    # Store the stack so we can close it later
    agent._devui_stack = stack
    
    return agent


def launch_devui():
    """Launch the DevUI interface with the code interpreter agent."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Create the agent asynchronously
    agent = asyncio.run(create_code_agent())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Azure AI Code Interpreter Agent in DevUI")
    print("=" * 70)
    print(f"✅ Agent Name: CodeInterpreterAgent")
    print(f"✅ Tools: HostedCodeInterpreterTool")
    print(f"✅ Web UI: http://localhost:8092")
    print(f"✅ API: http://localhost:8092/v1/*")
    print(f"✅ Entity ID: agent_CodeInterpreterAgent")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    else:
        print("   → Set ENABLE_DEVUI_TRACING=true to enable")
    print("=" * 70)
    print("\n💡 Try these challenging queries in the DevUI:")
    print("\n📊 Data Analysis:")
    print("   - Analyze the Collatz conjecture for numbers 1-100 with visualization")
    print("   - Generate and cluster synthetic data using k-means from scratch")
    print("\n🧩 Algorithms:")
    print("   - Solve the N-Queens problem for N=8 and visualize a solution")
    print("   - Implement the Sieve of Eratosthenes and find patterns in primes")
    print("\n🎨 Visualizations:")
    print("   - Create a visualization of the Mandelbrot set with zoom")
    print("   - Generate an Ulam spiral for prime numbers up to 400")
    print("\n🔢 Mathematics:")
    print("   - Calculate Fibonacci numbers up to F(1000) and analyze growth rate")
    print("   - Verify Goldbach's conjecture for even numbers up to 1000")
    print("\n⌨️  Press Ctrl+C to stop the server\n")
    
    try:
        # Launch the DevUI server with tracing enabled if configured
        serve(
            entities=[agent], 
            port=8092, 
            auto_open=True,
            tracing_enabled=enable_devui_tracing
        )
    finally:
        # Clean up resources
        if hasattr(agent, '_devui_stack'):
            asyncio.run(agent._devui_stack.aclose())


async def test_agent():
    """Test the agent programmatically before launching DevUI."""
    print("\n🧪 Testing code interpreter agent functionality with tracing...")
    
    # Set up tracing
    setup_tracing()
    
    agent = await create_code_agent()
    
    try:
        # Test with a challenging problem
        test_query = """Analyze the Collatz conjecture for numbers 1-20:
        1. For each starting number, count how many steps it takes to reach 1
        2. Find which number takes the longest sequence
        3. Calculate basic statistics (mean, max steps)
        Show your code and results."""
        
        # Create a span for the entire test session
        with get_tracer().start_as_current_span("Agent Test Session", kind=SpanKind.CLIENT) as span:
            trace_id = format_trace_id(span.get_span_context().trace_id)
            print(f"🔍 Trace ID: {trace_id}")
            print("   Use this ID to find traces in your observability backend\n")
            
            print(f"👤 User: {test_query}")
            print("\n🤖 Agent is writing and executing code...\n")
            
            response = await agent.run(test_query)
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

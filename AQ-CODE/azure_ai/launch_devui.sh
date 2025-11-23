#!/bin/bash
# Quick launcher for DevUI with Azure AI Weather Agent

echo "🚀 Azure AI Weather Agent - DevUI Launcher"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "azure_agents" ]; then
    echo "❌ Error: Please run this script from the azure_ai directory"
    exit 1
fi

# Check if devui is installed
if ! command -v devui &> /dev/null; then
    echo "📦 Installing agent-framework-devui..."
    pip install agent-framework-devui --pre
fi

# Parse command line argument
MODE=${1:-"standalone"}

case $MODE in
    "gallery"|"1"|"standalone")
        echo "📍 Mode: DevUI Gallery (default)"
        echo "🔧 Running: devui azure_agents --port 8100"
        echo ""
        echo "💡 All agents will be available in the dropdown menu"
        echo "   Open http://localhost:8100 in your browser"
        echo ""
        devui azure_agents --port 8100
        ;;
    
    "tracing"|"2")
        echo "📍 Mode: DevUI Gallery with Tracing"
        echo "🔧 Running: devui azure_agents --port 8100 --tracing framework"
        echo ""
        echo "💡 OpenTelemetry tracing enabled"
        echo "   Open http://localhost:8100 in your browser"
        echo ""
        devui azure_agents --port 8100 --tracing framework
        ;;
    
    "test")
        echo "📍 Mode: Test Weather Agent"
        echo "🔧 Running: python test_weather.py"
        echo ""
        python test_weather.py
        ;;
    
    *)
        echo "Usage: $0 [mode]"
        echo ""
        echo "Modes:"
        echo "  gallery (1)    - Run DevUI Gallery (default)"
        echo "  tracing (2)    - Enable OpenTelemetry tracing"
        echo "  test           - Test weather agent without DevUI"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run DevUI Gallery (default)"
        echo "  $0 gallery            # Run DevUI Gallery"
        echo "  $0 tracing            # Enable tracing"
        echo "  $0 test               # Test without DevUI"
        echo ""
        echo "Available Agents in Gallery:"
        echo "  • weather_agent_basic               - Weather queries"
        echo "  • weather_agent_functions           - Multi-tool weather & time"
        echo "  • bing_grounding_agent             - Web search"
        echo "  • code_interpreter_agent           - Python code execution"
        echo "  • code_interpreter_agent_with_images - Code with plot extraction"
        echo "  • file_search_agent                - Document search/RAG"
        echo "  • azure_search_agent               - Azure AI Search"
        echo "  • openapi_tools_agent              - REST API integration"
        exit 1
        ;;
esac

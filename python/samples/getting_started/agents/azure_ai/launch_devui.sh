#!/bin/bash
# Quick launcher for DevUI with Azure AI Weather Agent

echo "🚀 Azure AI Weather Agent - DevUI Launcher"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "azure_ai_basic.py" ]; then
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
    "standalone"|"1")
        echo "📍 Mode: Standalone Script"
        echo "🔧 Running: python azure_ai_basic_devui.py"
        echo ""
        python azure_ai_basic_devui.py
        ;;
    
    "discovery"|"2")
        echo "📍 Mode: Directory Discovery"
        echo "🔧 Running: devui devui_agents --port 8090"
        echo ""
        devui devui_agents --port 8090
        ;;
    
    "tracing"|"3")
        echo "📍 Mode: Directory Discovery with Tracing"
        echo "🔧 Running: devui devui_agents --port 8090 --tracing framework"
        echo ""
        devui devui_agents --port 8090 --tracing framework
        ;;
    
    "test")
        echo "📍 Mode: Test Agent"
        echo "🔧 Running: python azure_ai_basic_devui.py --test"
        echo ""
        python azure_ai_basic_devui.py --test
        ;;
    
    *)
        echo "Usage: $0 [mode]"
        echo ""
        echo "Modes:"
        echo "  standalone (1)  - Run standalone script (default)"
        echo "  discovery (2)   - Use directory discovery"
        echo "  tracing (3)     - Enable OpenTelemetry tracing"
        echo "  test           - Test agent without DevUI"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run standalone (default)"
        echo "  $0 standalone         # Run standalone"
        echo "  $0 discovery          # Use directory discovery"
        echo "  $0 tracing            # Enable tracing"
        echo "  $0 test               # Test without DevUI"
        exit 1
        ;;
esac

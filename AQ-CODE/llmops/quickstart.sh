#!/bin/bash
# Quick Start Script for LLMOps Production Agent UI

set -e

echo "🚀 LLMOps Production Agent - Quick Start"
echo "========================================"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source .venv/bin/activate"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check if in correct directory
if [[ ! -f "streamlit_production_ui.py" ]]; then
    echo "❌ Error: Must be run from AQ-CODE/llmops directory"
    exit 1
fi

echo ""
echo "📦 Installing UI dependencies..."
pip install -q -r requirements-ui.txt

echo ""
echo "🔍 Checking environment variables..."

if [[ -f "../../orchestration/.env" ]]; then
    echo "✓ Found .env file"
else
    echo "⚠️  Warning: .env file not found"
    echo "   Expected location: orchestration/.env"
fi

# Check Azure CLI login
if az account show &>/dev/null; then
    ACCOUNT=$(az account show --query name -o tsv)
    echo "✓ Azure CLI logged in: $ACCOUNT"
else
    echo "⚠️  Azure CLI not logged in"
    echo "   Run: az login"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Choose what to run:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Enhanced Agent (CLI Demo)"
echo "2. Streamlit UI"
echo "3. Both (CLI then UI)"
echo ""

read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "▶️  Running Enhanced Agent (CLI)..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python production_agent_enhanced.py
        ;;
    2)
        echo ""
        echo "▶️  Launching Streamlit UI..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📌 UI will open at: http://localhost:8501"
        echo "   Press Ctrl+C to stop"
        echo ""
        streamlit run streamlit_production_ui.py
        ;;
    3)
        echo ""
        echo "▶️  Running Enhanced Agent (CLI) first..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python production_agent_enhanced.py
        
        echo ""
        echo "✅ CLI demo complete!"
        echo ""
        read -p "Press Enter to launch Streamlit UI..."
        
        echo ""
        echo "▶️  Launching Streamlit UI..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📌 UI will open at: http://localhost:8501"
        echo "   Press Ctrl+C to stop"
        echo ""
        streamlit run streamlit_production_ui.py
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

#!/bin/bash
# Startup script for RDBMS DBA Assistant UI
# NOTE: Gradio UI has been removed. This script is deprecated.
# Use: python dba_assistant.py for CLI interface

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    RDBMS DBA Assistant - CLI                                 ║"
echo "║                 Powered by Microsoft Agent Framework                         ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with the following variables:"
    echo ""
    echo "  SERVER_NAME=your-server.database.windows.net"
    echo "  DATABASE_NAME=your-database"
    echo "  SQL_USERNAME=your-username"
    echo "  SQL_PASSWORD=your-password"
    echo "  TRUST_SERVER_CERTIFICATE=true"
    echo "  READONLY=false"
    echo ""
    exit 1
fi

# Check if MCP server is built
if [ ! -f "MssqlMcp/Node/dist/index.js" ]; then
    echo "⚠️  MCP server not built. Building now..."
    cd MssqlMcp/Node
    npm install
    npm run build
    cd ../..
    echo "✅ MCP server built successfully"
    echo ""
fi

# Activate virtual environment if it exists
if [ -d "../../.venv" ]; then
    echo "🔧 Activating virtual environment..."
    source ../../.venv/bin/activate
fi

# Check dependencies
if ! python -c "import agent_framework" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Installing..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
    echo ""
fi

# Start the CLI assistant
echo "🚀 Starting DBA Assistant CLI..."
echo "💬 Ask questions about your database in natural language"
echo ""
echo "Press Ctrl+C to exit"
echo ""

python dba_assistant.py

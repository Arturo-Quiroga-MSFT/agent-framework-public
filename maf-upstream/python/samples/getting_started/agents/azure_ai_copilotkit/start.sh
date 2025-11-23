#!/bin/bash

# Azure AI Weather Agent - CopilotKit Demo Startup Script
# This script starts both backend and frontend servers for testing

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Azure AI Weather Agent - CopilotKit Demo"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "${YELLOW}🛑 Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Check if backend dependencies are installed
echo "${BLUE}📦 Checking backend dependencies...${NC}"
if [ ! -d "agent/.venv" ] && [ ! -f "agent/pyproject.toml" ]; then
    echo "${YELLOW}Installing backend dependencies...${NC}"
    cd agent
    pip install -e . || {
        echo "❌ Failed to install backend dependencies"
        exit 1
    }
    cd ..
fi

# Check if frontend dependencies are installed
echo "${BLUE}📦 Checking frontend dependencies...${NC}"
if [ ! -d "ui/node_modules" ]; then
    echo "${YELLOW}Installing frontend dependencies...${NC}"
    cd ui
    npm install || {
        echo "❌ Failed to install frontend dependencies"
        exit 1
    }
    cd ..
fi

echo ""
echo "${GREEN}✅ Dependencies ready${NC}"
echo ""

# Start backend
echo "${BLUE}🔧 Starting Backend (FastAPI on port 8200)...${NC}"
cd agent
python src/main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "${YELLOW}⏳ Waiting for backend to start...${NC}"
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8200/docs > /dev/null; then
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "${GREEN}✅ Backend running at http://localhost:8200${NC}"
echo ""

# Start frontend
echo "${BLUE}🎨 Starting Frontend (Next.js on port 3200)...${NC}"
cd ui
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "${YELLOW}⏳ Waiting for frontend to start...${NC}"
sleep 5

echo ""
echo "${GREEN}✅ Frontend running at http://localhost:3200${NC}"
echo ""
echo "=================================================="
echo "${GREEN}🎉 All services are running!${NC}"
echo ""
echo "📡 Backend API: http://localhost:8200"
echo "📖 API Docs: http://localhost:8200/docs"
echo "🌐 Frontend UI: http://localhost:3200"
echo ""
echo "💡 Try these queries in the sidebar:"
echo "   - What's the weather in Toronto?"
echo "   - How's the weather in Mexico City?"
echo "   - Compare weather in Guadalajara and Monterrey"
echo ""
echo "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Wait for both processes
wait

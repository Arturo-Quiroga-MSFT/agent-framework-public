#!/bin/bash
# Quick start script for AG-UI Client-Server

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}${CYAN}"
echo "================================================================================"
echo "🚀 AG-UI Client-Server Quick Start"
echo "================================================================================"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "agui_server.py" ]; then
    echo -e "${RED}❌ Error: agui_server.py not found${NC}"
    echo -e "${YELLOW}Please run this script from the AQ-CODE/agui-clientserver directory${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../../.venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo -e "${CYAN}Creating virtual environment...${NC}"
    python3 -m venv ../../.venv
fi

# Activate virtual environment
echo -e "${CYAN}📦 Activating virtual environment...${NC}"
source ../../.venv/bin/activate

# Install requirements
echo -e "${CYAN}📦 Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Check environment variables
echo ""
echo -e "${BOLD}Environment Check:${NC}"

if [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo -e "${YELLOW}⚠️  AZURE_OPENAI_ENDPOINT not set${NC}"
    echo -e "   Set it with: export AZURE_OPENAI_ENDPOINT='https://your-endpoint.openai.azure.com/'"
else
    echo -e "${GREEN}✅ AZURE_OPENAI_ENDPOINT: $AZURE_OPENAI_ENDPOINT${NC}"
fi

if [ -z "$AZURE_OPENAI_DEPLOYMENT_NAME" ]; then
    echo -e "${YELLOW}⚠️  AZURE_OPENAI_DEPLOYMENT_NAME not set (using default: gpt-4o)${NC}"
else
    echo -e "${GREEN}✅ AZURE_OPENAI_DEPLOYMENT_NAME: $AZURE_OPENAI_DEPLOYMENT_NAME${NC}"
fi

if [ -z "$PROJECT_CONNECTION_STRING" ]; then
    echo -e "${YELLOW}⚠️  PROJECT_CONNECTION_STRING not set${NC}"
    echo -e "   This is required for Azure AI Foundry integration"
else
    echo -e "${GREEN}✅ PROJECT_CONNECTION_STRING configured${NC}"
fi

# Menu
echo ""
echo -e "${BOLD}What would you like to do?${NC}"
echo ""
echo "  1) Start AG-UI Server"
echo "  2) Start AG-UI Client (interactive)"
echo "  3) Run automated tests"
echo "  4) Test single query"
echo "  5) Exit"
echo ""

read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo -e "${CYAN}🚀 Starting AG-UI Server...${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        echo ""
        python3 agui_server.py
        ;;
    2)
        echo ""
        echo -e "${CYAN}🚀 Starting AG-UI Client...${NC}"
        echo -e "${YELLOW}Make sure the server is running in another terminal!${NC}"
        echo ""
        sleep 2
        python3 agui_client.py
        ;;
    3)
        echo ""
        echo -e "${CYAN}🧪 Running automated tests...${NC}"
        echo -e "${YELLOW}Make sure the server is running in another terminal!${NC}"
        echo ""
        sleep 2
        python3 test_agui.py
        ;;
    4)
        echo ""
        read -p "Enter your query: " query
        echo ""
        echo -e "${CYAN}🚀 Sending query...${NC}"
        echo -e "${YELLOW}Make sure the server is running in another terminal!${NC}"
        echo ""
        sleep 2
        python3 agui_client.py "$query"
        ;;
    5)
        echo ""
        echo -e "${CYAN}Goodbye! 👋${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

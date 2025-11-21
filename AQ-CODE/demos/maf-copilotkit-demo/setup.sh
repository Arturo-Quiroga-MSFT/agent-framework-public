#!/bin/bash

# MAF + CopilotKit Demo Setup Script

set -e

echo "🚀 MAF + CopilotKit Demo Setup"
echo "================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.12+ is required"
    exit 1
fi
echo "✓ Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 20+ is required"
    exit 1
fi
echo "✓ Node.js found: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required"
    exit 1
fi
echo "✓ npm found: $(npm --version)"

echo ""
echo "📦 Installing dependencies..."
echo ""

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your API credentials!"
    echo ""
fi

echo "Installing Python packages..."
pip install -e . || {
    echo "❌ Failed to install Python packages"
    echo "💡 Try: pip install --upgrade pip"
    exit 1
}

cd ..

# Frontend setup
echo ""
echo "⚛️  Setting up Next.js frontend..."
cd frontend

echo "Installing npm packages..."
npm install || {
    echo "❌ Failed to install npm packages"
    exit 1
}

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Edit backend/.env with your Azure OpenAI or OpenAI credentials"
echo "  2. Add OPENWEATHER_API_KEY (get free key at https://openweathermap.org/api)"
echo "  3. (Optional) Add FIRECRAWL_API_KEY for web scraping"
echo ""
echo "🚀 To start the demo:"
echo "  Terminal 1: cd backend/src && python main.py"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "  Then open: http://localhost:3000"
echo ""
echo "📚 For more help, see README.md"
echo ""

#!/bin/bash

# Azure AI Weather Agent - Stop Script
# Stops all running backend and frontend servers

echo "🛑 Stopping Azure AI Weather Agent servers..."

# Kill processes on port 8200 (backend)
lsof -ti:8200 | xargs kill -9 2>/dev/null && echo "✅ Stopped backend (port 8200)" || echo "ℹ️  No backend running on port 8200"

# Kill processes on port 3200 (frontend)
lsof -ti:3200 | xargs kill -9 2>/dev/null && echo "✅ Stopped frontend (port 3200)" || echo "ℹ️  No frontend running on port 3200"

# Kill any remaining node/python processes from this project
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "python src/main.py" 2>/dev/null

echo ""
echo "✅ All servers stopped"

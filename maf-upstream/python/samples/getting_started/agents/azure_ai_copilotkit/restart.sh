#!/bin/bash

# Azure AI Weather Agent - Restart Script
# Stops and restarts both servers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Restarting Azure AI Weather Agent..."
echo ""

# Stop existing servers
./stop.sh

echo ""
echo "⏳ Waiting 2 seconds before restart..."
sleep 2
echo ""

# Start servers
./start.sh

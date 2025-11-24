#!/bin/bash
set -euo pipefail

# Azure AI Weather Agent - Restart Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Restarting Azure AI Weather Agent..."

"$SCRIPT_DIR/stop.sh" || true
sleep 2
"$SCRIPT_DIR/start.sh"

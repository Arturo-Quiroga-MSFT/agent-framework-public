#!/bin/bash
#
# Bash wrapper for Python agent creation script.
# Equivalent to Create.ps1 (PowerShell version).
#
# Usage:
#   ./create_agents.sh
#
# Prerequisites:
#   - Python 3.11+
#   - pip packages: azure-ai-projects, azure-identity, pyyaml
#   - Azure CLI logged in: az login
#   - Environment variables set:
#     - FOUNDRY_PROJECT_ENDPOINT
#     - FOUNDRY_MODEL_DEPLOYMENT_NAME
#     - FOUNDRY_CONNECTION_GROUNDING_TOOL (optional)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🐍 Running Python agent creation script..."
echo ""

cd "$SCRIPT_DIR"
python create_agents.py "$@"

echo ""
echo "✅ Done!"

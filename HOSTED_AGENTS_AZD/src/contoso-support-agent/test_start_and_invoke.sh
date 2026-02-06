#!/bin/bash
# Simple: start the agent (it's already stopped), wait, test
set -e

echo "=== Starting the agent ==="
az cognitiveservices agent start \
  --account-name r2d2-foundry-001 \
  --project-name Main-Project \
  --name contoso-support-agent \
  --agent-version 2 2>&1

echo ""
echo "=== Waiting 60 seconds for container startup ==="
sleep 60

echo ""
echo "=== Checking status ==="
az cognitiveservices agent list-versions \
  --account-name r2d2-foundry-001 \
  --project-name Main-Project \
  --name contoso-support-agent 2>&1

echo ""
echo "=== Testing invocation ==="
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
BASE="https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"
API="api-version=2025-11-15-preview"

CONV=$(curl -sS -X POST "$BASE/openai/conversations?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Conversation: $CONV"

curl -sS -X POST "$BASE/openai/responses?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"agent\": {\"type\": \"agent_reference\", \"name\": \"contoso-support-agent\"},
    \"conversation\": \"$CONV\",
    \"input\": \"Hello! What products do you support?\"
  }" | python3 -m json.tool 2>&1 | head -30

echo ""
echo "Done."

#!/bin/bash
# Fix: stop, restart, and re-test the hosted agent
set -e

TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
BASE="https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"
API="api-version=2025-11-15-preview"

echo "=== Step 1: Stop the hosted agent ==="
az cognitiveservices agent stop \
  --account-name r2d2-foundry-001 \
  --project-name Main-Project \
  --name contoso-support-agent \
  --agent-version 2 2>&1 || echo "(stop may fail if already stopped)"

echo ""
echo "=== Step 2: Poll until stopped (up to 3 minutes) ==="
for i in $(seq 1 18); do
  STATUS=$(az cognitiveservices agent list-versions \
    --account-name r2d2-foundry-001 \
    --project-name Main-Project \
    --name contoso-support-agent 2>/dev/null | python3 -c "
import sys,json
data = json.load(sys.stdin)
for v in data:
  if v.get('Agent_version_id') == '2':
    print(v.get('Status','unknown'))
    break
" 2>/dev/null || echo "unknown")
  echo "  Attempt $i: Status = $STATUS"
  if [[ "$STATUS" == "Stopped" || "$STATUS" == "stopped" ]]; then
    echo "  Agent stopped!"
    break
  fi
  sleep 10
done

echo ""
echo "=== Step 3: Start the hosted agent ==="
az cognitiveservices agent start \
  --account-name r2d2-foundry-001 \
  --project-name Main-Project \
  --name contoso-support-agent \
  --agent-version 2 2>&1

echo ""
echo "=== Step 4: Poll until running (up to 3 minutes) ==="
for i in $(seq 1 18); do
  STATUS=$(az cognitiveservices agent list-versions \
    --account-name r2d2-foundry-001 \
    --project-name Main-Project \
    --name contoso-support-agent 2>/dev/null | python3 -c "
import sys,json
data = json.load(sys.stdin)
for v in data:
  if v.get('Agent_version_id') == '2':
    print(v.get('Status','unknown'))
    break
" 2>/dev/null || echo "unknown")
  echo "  Attempt $i: Status = $STATUS"
  if [[ "$STATUS" == "Running" || "$STATUS" == "running" ]]; then
    echo "  Agent running!"
    break
  fi
  sleep 10
done

echo ""
echo "=== Step 5: Check deployment status ==="
az cognitiveservices agent show \
  --account-name r2d2-foundry-001 \
  --project-name Main-Project \
  --name contoso-support-agent 2>&1

echo ""
echo "=== Step 6: Test invocation ==="
# Refresh token after the wait
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)

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
echo "=== Step 7: Check container logs for incoming request ==="
curl -sS -N "$BASE/agents/contoso-support-agent/versions/2/containers/default:logstream?kind=console&tail=20&$API" \
  -H "Authorization: Bearer $TOKEN" --max-time 5 2>&1 | grep -v readiness | grep -v liveness | tail -10

echo ""
echo "Done."

#!/bin/bash
# Nuclear option: delete everything, recreate from scratch, test properly
set -euo pipefail

ACCOUNT="r2d2-foundry-001"
PROJECT="Main-Project"
AGENT="contoso-support-agent-v2"
IMAGE="aqr2d2acr001.azurecr.io/contoso-support-agent:v3"
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
BASE="https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"
API="api-version=2025-11-15-preview"

echo "=========================================="
echo "Step 1: Create a FRESH hosted agent"
echo "=========================================="
# Use REST API directly - cleaner than SDK
RESPONSE=$(curl -sS -X POST "$BASE/agents/$AGENT/versions?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"definition\": {
      \"kind\": \"hosted\",
      \"image\": \"$IMAGE\",
      \"cpu\": \"1\",
      \"memory\": \"2Gi\",
      \"container_protocol_versions\": [{\"protocol\": \"RESPONSES\", \"version\": \"v1\"}],
      \"environment_variables\": {
        \"AZURE_AI_PROJECT_ENDPOINT\": \"$BASE\",
        \"AZURE_AI_MODEL_DEPLOYMENT_NAME\": \"gpt-4.1\"
      }
    }
  }")
echo "$RESPONSE" | python3 -m json.tool 2>&1
VERSION=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))")
echo "Created version: $VERSION"

echo ""
echo "=========================================="
echo "Step 2: Start the agent"  
echo "=========================================="
az cognitiveservices agent start \
  --account-name "$ACCOUNT" \
  --project-name "$PROJECT" \
  --name "$AGENT" \
  --agent-version "$VERSION" 2>&1

echo ""
echo "=========================================="
echo "Step 3: Poll for Running status (up to 5 min)"
echo "=========================================="
for i in $(seq 1 30); do
  # Use show command which should include deployment status
  RAW=$(az cognitiveservices agent show \
    --account-name "$ACCOUNT" \
    --project-name "$PROJECT" \
    --name "$AGENT" 2>/dev/null || echo "{}")
  echo "  Poll $i ($(( i * 10 ))s): $(echo "$RAW" | head -5)"
  
  # Also check via REST for deployment status
  REST=$(curl -sS "$BASE/agents/$AGENT/versions/$VERSION?$API" \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null)
  DEPLOY_STATUS=$(echo "$REST" | python3 -c "
import sys,json
d=json.load(sys.stdin)
dep=d.get('deployment',{})
print(f\"deploy={dep.get('status','none')}\")
" 2>/dev/null || echo "deploy=unknown")
  echo "  $DEPLOY_STATUS"
  
  if echo "$DEPLOY_STATUS" | grep -qi "running"; then
    echo "  >>> Agent is RUNNING!"
    break
  fi
  sleep 10
done

echo ""
echo "=========================================="
echo "Step 4: Check container logs"
echo "=========================================="
curl -sS -N "$BASE/agents/$AGENT/versions/$VERSION/containers/default:logstream?kind=console&tail=5&$API" \
  -H "Authorization: Bearer $(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)" \
  --max-time 5 2>&1 | tail -10
echo ""

echo ""
echo "=========================================="
echo "Step 5: Test invocation"
echo "=========================================="
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)

CONV=$(curl -sS -X POST "$BASE/openai/conversations?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Conversation: $CONV"

echo "Invoking agent..."
curl -sS -X POST "$BASE/openai/responses?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"agent\": {\"type\": \"agent_reference\", \"name\": \"$AGENT\"},
    \"conversation\": \"$CONV\",
    \"input\": \"Hello! What products do you support?\"
  }" | python3 -m json.tool 2>&1

echo ""
echo "=========================================="
echo "Also testing OLD agent (contoso-support-agent)"
echo "=========================================="
curl -sS -X POST "$BASE/openai/responses?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"agent\": {\"type\": \"agent_reference\", \"name\": \"contoso-support-agent\"},
    \"conversation\": \"$CONV\",
    \"input\": \"Hello!\"
  }" | python3 -m json.tool 2>&1 | head -15

echo ""
echo "Done."

#!/bin/bash
# Direct REST tests against the hosted agent - bypasses all SDK issues

TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
BASE="https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project/openai"
API="api-version=2025-11-15-preview"

echo "=== Test 1: Minimal - no conversation ==="
curl -sS -X POST "$BASE/responses?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent": {"type": "agent_reference", "name": "contoso-support-agent"},
    "input": "Hello!"
  }' | python3 -m json.tool 2>&1 | head -20

echo ""
echo "=== Test 2: With version field ==="
curl -sS -X POST "$BASE/responses?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent": {"type": "agent_reference", "name": "contoso-support-agent", "version": "2"},
    "input": "Hello!"
  }' | python3 -m json.tool 2>&1 | head -20

echo ""
echo "=== Test 3: With model field ==="
curl -sS -X POST "$BASE/responses?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent": {"type": "agent_reference", "name": "contoso-support-agent"},
    "model": "gpt-4.1",
    "input": "Hello!"
  }' | python3 -m json.tool 2>&1 | head -20

echo ""
echo "=== Test 4: With conversation ==="
CONV=$(curl -sS -X POST "$BASE/conversations?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Conversation ID: $CONV"

curl -sS -X POST "$BASE/responses?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"agent\": {\"type\": \"agent_reference\", \"name\": \"contoso-support-agent\"},
    \"conversation\": \"$CONV\",
    \"input\": \"Hello! What products do you support?\"
  }" | python3 -m json.tool 2>&1 | head -30

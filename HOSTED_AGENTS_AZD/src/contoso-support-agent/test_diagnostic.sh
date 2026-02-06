#!/bin/bash
# Diagnostic script: check agent status + test prompt agent vs hosted agent

TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
BASE="https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"
API="api-version=2025-11-15-preview"

echo "=== 1. Check hosted agent status ==="
curl -sS "$BASE/agents/contoso-support-agent?$API" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"Name: {d.get('name')}\")
print(f\"ID: {d.get('id')}\")
v = d.get('versions', {})
latest = v.get('latest', {})
print(f\"Latest version: {latest.get('version')}\")
print(f\"Status: {latest.get('deployment', {}).get('status')}\")
print(f\"Protocol: {latest.get('definition', {}).get('container_protocol_versions')}\")
"

echo ""
echo "=== 2. Create a quick prompt agent and test it ==="
curl -sS -X POST "$BASE/agents/test-prompt-agent/versions?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "definition": {
      "kind": "prompt",
      "model": "gpt-4.1-mini",
      "instructions": "You are a helpful assistant. Be brief."
    }
  }' | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"Prompt agent created: {d.get('name')} v{d.get('version')}\")
" 2>&1

echo ""
echo "=== 3. Test prompt agent via responses API ==="
curl -sS -X POST "$BASE/openai/responses?$API" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "agent": {"type": "agent_reference", "name": "test-prompt-agent"},
    "input": "Say hello in one sentence"
  }' | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'error' in d:
    print(f\"ERROR: {d['error']['message']}\")
else:
    print(f\"Response ID: {d.get('id')}\")
    for item in d.get('output', []):
        if item.get('type') == 'message':
            for c in item.get('content', []):
                print(f\"Output: {c.get('text', '')[:200]}\")
" 2>&1

echo ""
echo "=== 4. Check container logs (last 10 lines) ==="
curl -sS -N "https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project/agents/contoso-support-agent/versions/2/containers/default:logstream?kind=console&tail=10&api-version=2025-11-15-preview" \
  -H "Authorization: Bearer $TOKEN" --max-time 5 2>&1 | tail -15

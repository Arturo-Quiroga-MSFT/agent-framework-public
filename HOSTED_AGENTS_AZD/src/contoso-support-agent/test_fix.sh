#!/bin/bash
# Fix: check actual deployment status and start agent if needed

TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
BASE="https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project"
API="api-version=2025-11-15-preview"

echo "=== 1. Get full agent details via REST ==="
curl -sS "$BASE/agents/contoso-support-agent?$API" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== 2. Get agent version 2 details ==="
curl -sS "$BASE/agents/contoso-support-agent/versions/2?$API" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== 3. Test prompt agent invocation ==="
# Create a simple prompt agent and immediately test
python3 -c "
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

client = AIProjectClient(
    endpoint='https://r2d2-foundry-001.services.ai.azure.com/api/projects/Main-Project',
    credential=DefaultAzureCredential(),
)
openai_client = client.get_openai_client()

# Create a prompt agent
agent = client.agents.create_version(
    agent_name='test-prompt-agent-v2',
    definition=PromptAgentDefinition(
        model='gpt-4.1',
        instructions='You are a helpful assistant. Always respond briefly.',
    ),
)
print(f'Created prompt agent: {agent.name} v{agent.version}')

# Create conversation
conversation = openai_client.conversations.create()
print(f'Conversation: {conversation.id}')

# Invoke
response = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={'agent': {'name': agent.name, 'type': 'agent_reference'}},
    input='Say hello in one sentence.',
)
print(f'Prompt agent response: {response.output_text}')

# Clean up
client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print('Cleaned up prompt agent')
"

echo ""
echo "=== 4. Try starting hosted agent via CLI ==="
az cognitiveservices agent start \
  --account-name r2d2-foundry-001 \
  --project-name Main-Project \
  --name contoso-support-agent \
  --agent-version 2 2>&1 || echo "(CLI command may not be available yet)"

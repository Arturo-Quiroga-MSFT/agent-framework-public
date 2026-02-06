# Quick Start: MAF V2 → Hosted Agents

**Updated**: February 5, 2026  
**Based on**: Official Microsoft documentation

## 🚀 5-Minute Setup

### 1. Install Packages

```bash
pip install --pre "azure-ai-projects>=2.0.0b3"
pip install azure-ai-agentserver-core azure-ai-agentserver-agentframework
pip install agent-framework agent-framework-azure
pip install azure-identity python-dotenv
```

### 2. Set Environment Variables

```bash
# .env file
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

### 3. Create Agent (app.py)

```python
#!/usr/bin/env python3
from azure.ai.agentserver.agentframework import from_azure_ai_agent
from agent_framework.azure import AzureAIClient
from azure.identity import DefaultAzureCredential
import os

def create_app():
    # Initialize V2 client
    client = AzureAIClient(
        endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )
    
    # Create agent
    agent = client.create_agent(
        model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        instructions="You are a helpful assistant.",
        name="MyAgent",
        use_latest_version=True
    )
    
    # Transform to hosted service
    return from_azure_ai_agent(agent, client=client)

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8088)
```

### 4. Test Locally

```bash
# Terminal 1: Start server
python app.py

# Terminal 2: Test REST API
curl -X POST http://localhost:8088/responses \
  -H 'Content-Type: application/json' \
  -d '{"input": {"messages": [{"role": "user", "content": "Hello!"}]}}'
```

### 5. Deploy to Foundry

```bash
# Option A: Using azd (recommended)
azd init -t https://github.com/Azure-Samples/azd-ai-starter-basic
azd ai agent init -m agent.yaml
azd up

# Option B: Using Azure CLI
# 1) Build image in ACR (no local Docker)
az acr build --registry yourregistry --image my-agent:v1 .

# 2) Create capability host (one-time per account)
az rest --method put \
  --url "https://management.azure.com/subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.CognitiveServices/accounts/<ACCOUNT>/capabilityHosts/accountcaphost?api-version=2025-10-01-preview" \
  --headers "content-type=application/json" \
  --body '{
    "properties": {
      "capabilityHostKind": "Agents",
      "enablePublicHostingEnvironment": true
    }
  }'

# 3) Create hosted agent from image
az cognitiveservices agent create \
  --account-name your-account \
  --project-name your-project \
  --name my-agent \
  --image yourregistry.azurecr.io/my-agent:v1 \
  --env "AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>" \
  --env "AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1" \
  --cpu 1 --memory 2Gi \
  --min-replicas 1 --max-replicas 2
```

## 📦 Complete Project Structure

```
my-agent/
├── app.py                 # Agent server with hosting adapter
├── agent.yaml            # azd configuration
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (local only)
├── .env.template         # Template for .env
└── .dockerignore         # Docker ignore patterns
```

## 🔑 Key Concepts

### AzureAIClient (V2)
- Wraps azure-ai-projects SDK
- Manages agent lifecycle
- Handles authentication
- Creates agents on Azure AI service

### Hosting Adapter
- Transforms MAF agent → HTTP service
- Provides Foundry-compatible REST API
- Built-in OpenTelemetry tracing
- Automatic conversation management

### Azure Developer CLI (azd)
- Simplifies infrastructure provisioning
- Handles containerization
- Manages deployments
- Configures RBAC automatically

## 🎯 Common Patterns

### Pattern 1: Reuse Existing Agent

```python
agent = client.create_agent(
    model="gpt-4o-mini",
    instructions="...",
    name="MyAgent",
    use_latest_version=True  # Don't create new version
)
```

### Pattern 2: Thread-Based Conversations

```python
# First message - creates thread
run = await client.agents.run(
    agent=agent,
    messages=[{"role": "user", "content": "Hello"}]
)

# Continue conversation with thread_id
run = await client.agents.run(
    agent=agent,
    thread_id=run.thread_id,
    messages=[{"role": "user", "content": "Follow-up"}]
)
```

### Pattern 3: Streaming Responses

```python
# Hosting adapter automatically supports SSE streaming
# Client receives events in real-time
```

### Pattern 4: Add Tools

```python
agent = client.create_agent(
    model="gpt-4o-mini",
    instructions="...",
    tools=[
        {"type": "code_interpreter"},
        {"type": "web_search"},
        {"type": "mcp", "project_connection_id": "mcp-connection-id"}
    ]
)
```

## 🛠️ Dockerfile Template

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8088

ENV PYTHONUNBUFFERED=1
ENV PORT=8088

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8088/health')"

CMD ["python", "app.py"]
```

## 📋 agent.yaml Template

```yaml
name: my-agent
version: 1.0
description: My hosted agent

image:
  registry: yourregistry.azurecr.io
  repository: my-agent
  tag: v1

resources:
  cpu: "1"
  memory: "2Gi"

scaling:
  minReplicas: 1
  maxReplicas: 3

protocols:
  - name: responses
    version: v1

environment:
  - name: AZURE_AI_PROJECT_ENDPOINT
    value: "${AZURE_AI_PROJECT_ENDPOINT}"
  - name: AZURE_AI_MODEL_DEPLOYMENT_NAME
    value: "${AZURE_AI_MODEL_DEPLOYMENT_NAME}"
```

## 🔍 Debugging Tips

### Check Agent Status

```bash
az cognitiveservices agent show \
  --account-name your-account \
  --project-name your-project \
  --name my-agent
```

### View Deployment Logs

```bash
# From Foundry portal
# Navigate to: Agents > Your Agent > View deployment logs
```

### Test Health Endpoint

```bash
curl http://localhost:8088/health
```

### Check OpenTelemetry Traces

```python
# Set environment variable for local tracing
export OTEL_EXPORTER_ENDPOINT=http://localhost:4318
```

## 📚 References

- [MAF V2 Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/getting_started/agents/azure_ai)
- [Hosted Agents Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents)
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [Foundry Samples](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents)

## ⚠️ Important Notes

- **Region Availability**: 25 regions supported (East US 2 or Sweden Central recommended)
- **Preview Limitations**: Max 2 min replicas, 5 max replicas
- **Authentication**: Use `az login` before running locally
- **Package Versions**: Some packages in preview, check PyPI availability

## 🎉 Next Steps

1. ✅ Run the Jupyter notebook: [hosted_agents_e2e_demo.ipynb](./hosted_agents_e2e_demo.ipynb)
2. ✅ Review official samples in GitHub
3. ✅ Deploy to staging environment
4. ✅ Add observability with Application Insights
5. ✅ Publish to Teams or M365 Copilot

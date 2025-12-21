# Hosted Agents Demo Guide

**Created**: December 20, 2025  
**Status**: Planning Phase  
**Reference**: [Microsoft Learn - Hosted Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry&tabs=cli)

---

## 🤝 How MAF and Hosted Agents Work Together

### The Relationship

Think of it as a **two-layer stack**:

```
┌─────────────────────────────────────────┐
│   MICROSOFT AGENT FRAMEWORK (MAF)       │  ← Layer 1: BUILD
│   • Write agent code (Python/C#)        │    (Development Framework)
│   • Define workflows & orchestration    │
│   • Add tools & plugins                 │
│   • Local testing & debugging           │
└──────────────────┬──────────────────────┘
                   │
                   │ Hosting Adapter (bridge)
                   │
┌──────────────────▼──────────────────────┐
│        HOSTED AGENTS SERVICE            │  ← Layer 2: RUN
│   • Container orchestration             │    (Deployment Platform)
│   • Autoscaling & load balancing        │
│   • State & conversation management     │
│   • Identity, security, observability   │
└─────────────────────────────────────────┘
```

### Simple Explanation

- **MAF is your toolkit** for building agents (like Django/Flask for web apps)
- **Hosted Agents is your cloud platform** for running those agents (like Azure App Service)
- **The hosting adapter** connects them seamlessly

### How They Complement Each Other

| Aspect | MAF Provides | Hosted Agents Provides |
|--------|--------------|------------------------|
| **Development** | Agent code, workflows, tools | N/A (local only) |
| **Testing** | Local execution, debugging | N/A (local only) |
| **Deployment** | Containerization support | Managed hosting infrastructure |
| **Scaling** | Agent logic | Autoscaling, load balancing |
| **State** | Agent memory, context | Durable conversation objects |
| **Identity** | Agent behavior | Managed identity, RBAC |
| **Observability** | Telemetry collection | Application Insights integration |
| **Publishing** | N/A | Teams, M365, stable endpoints |

### The Magic: Hosting Adapter

The **hosting adapter** is what bridges MAF and Hosted Agents:

```python
# Your MAF agent code
from agent_framework import ChatAgent
agent = ChatAgent(...)

# The bridge: hosting adapter
from azure.ai.agentserver.agentframework import from_agentframework
from_agentframework(agent).run()  # ✨ Now it's a hosted service
```

**What the adapter does**:
1. Takes your MAF agent instance
2. Wraps it in HTTP endpoints (REST API)
3. Adds Foundry protocol compatibility
4. Enables streaming (SSE)
5. Integrates observability (OpenTelemetry)
6. Handles conversation management

### You Can Use MAF Without Hosted Agents

**MAF standalone** (without hosting):
- ✅ Build and test agents locally
- ✅ Deploy to your own infrastructure (VMs, Kubernetes, etc.)
- ✅ Run in Azure Functions, Container Apps, etc.
- ✅ Custom deployment and scaling logic

**Example**: NL2SQL pipeline in this repo runs MAF agents locally without hosted agents service.

### You Need MAF (or LangGraph) for Hosted Agents

**Hosted Agents requires** a supported framework:
- ✅ Microsoft Agent Framework (Python/C#)
- ✅ LangGraph (Python only)
- ✅ Custom code implementing the Foundry protocol

You **cannot** use Hosted Agents with:
- ❌ Raw OpenAI SDK code
- ❌ Arbitrary Python scripts
- ❌ Prompt-based agents (those are different)

### Complete Flow: MAF → Hosted Agents

```
1️⃣ DEVELOP with MAF
   └─ Write agent in Python/C# using MAF SDK
   └─ Add tools, workflows, custom logic
   └─ Test locally: agent.run("Hello")

2️⃣ ADAPT for Hosting
   └─ Add hosting adapter: from_agentframework(agent).run()
   └─ Test locally at localhost:8088
   └─ Validate REST API compatibility

3️⃣ CONTAINERIZE
   └─ Create Dockerfile
   └─ Build container image
   └─ Push to Azure Container Registry

4️⃣ DEPLOY to Hosted Agents
   └─ Use azd up or Azure CLI
   └─ Foundry Agent Service provisions infrastructure
   └─ Your MAF agent runs as managed service

5️⃣ PUBLISH (Optional)
   └─ Publish to Teams, M365 Copilot
   └─ Get stable API endpoint
   └─ Share with organization
```

### Real-World Analogy

**Building a Web Application**:
- **Framework Layer**: Django/Flask (like MAF) - you write your app logic
- **Hosting Layer**: Azure App Service (like Hosted Agents) - runs your app at scale
- **Bridge**: WSGI/ASGI server (like hosting adapter) - connects framework to hosting

**Building an AI Agent**:
- **Framework Layer**: MAF - you write your agent logic
- **Hosting Layer**: Hosted Agents Service - runs your agent at scale
- **Bridge**: Hosting adapter - connects MAF to Foundry

### Key Takeaway

> **MAF is how you build agents. Hosted Agents is where you run them at scale.**
>
> You need MAF (or similar framework) to create the agent code. You use Hosted Agents to deploy that code as a production-ready, auto-scaling, managed service.

---

## 🎯 What are Hosted Agents?

**Hosted agents** are containerized agentic AI applications that run on **Azure AI Foundry Agent Service** - Microsoft's fully managed platform for deploying and operationalizing AI agents at scale.

### Key Differentiators

| Feature | Prompt-Based Agents | Hosted Agents |
|---------|-------------------|---------------|
| **Build Method** | UI/Portal configuration | Code-based (MAF, LangGraph, custom) |
| **Deployment** | Direct from portal | Containerized on managed infrastructure |
| **Scalability** | Limited | Auto-scaling, enterprise-grade |
| **Lifecycle** | Edit in portal | Create → Start → Update → Stop → Delete |
| **Infrastructure** | Not applicable | Pay-as-you-go Azure infrastructure |
| **Customization** | Limited by portal | Full programmatic control |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Developer Workflow                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Write Agent Code (MAF/LangGraph/Custom)            │
│                    ↓                                     │
│  2. Use Hosting Adapter (from_* method)                │
│     • from_agentframework(agent).run()                  │
│     • from_langgraph(agent).run()                       │
│                    ↓                                     │
│  3. Test Locally (localhost:8088)                       │
│     • REST API auto-exposed                             │
│     • OpenTelemetry tracing                             │
│     • Foundry protocol compliance                       │
│                    ↓                                     │
│  4. Containerize (Docker)                               │
│                    ↓                                     │
│  5. Deploy via Azure Developer CLI (azd)               │
│     • azd up → provision + deploy                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│               Azure AI Foundry Agent Service             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  • Container orchestration & autoscaling                │
│  • Conversation state management                        │
│  • Identity & security (RBAC, Managed Identity)        │
│  • Built-in observability (Application Insights)       │
│  • Integration with Foundry tools & models             │
│  • OpenAI Responses-compatible API                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Publishing Channels                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  • Web app preview (instant shareable interface)       │
│  • Microsoft 365 Copilot                                │
│  • Microsoft Teams                                      │
│  • Stable REST API endpoint                             │
│  • Custom applications                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Components

### 1. Hosting Adapter

The **hosting adapter** is the magic abstraction layer that transforms your agent framework code into a Foundry-compatible HTTP service.

**One-Line Deployment**:
```python
# Python example
from azure.ai.agentserver.agentframework import from_agentframework
from agent_framework import ChatAgent

agent = ChatAgent(...)
from_agentframework(agent).run()  # ✨ Instant HTTP server on localhost:8088
```

```csharp
// C# example
using Azure.AI.AgentServer.AgentFramework;

var agent = new ChatAgent(...);
await AgentServerExtensions.RunAsync(agent);  // ✨ HTTP server ready
```

**What the Adapter Provides**:
- ✅ Automatic REST API endpoints
- ✅ SSE (Server-Sent Events) streaming
- ✅ Foundry protocol translation
- ✅ OpenTelemetry tracing
- ✅ CORS support
- ✅ Conversation management
- ✅ Message serialization

### 2. Managed Service Capabilities

What Azure AI Foundry Agent Service handles for you:

- **Provisioning & Autoscaling**: No Kubernetes configs, no scaling logic
- **Conversation Orchestration**: Durable conversation objects with state
- **Identity Management**: Managed identities, RBAC integration
- **Observability**: Built-in Application Insights integration
- **Security & Compliance**: Enterprise-grade by default
- **Integration**: Seamless connection to Azure AI models and tools

### 3. Framework Support

| Framework | Python | .NET |
|-----------|--------|------|
| **Microsoft Agent Framework** | ✅ | ✅ |
| **LangGraph** | ✅ | ❌ |
| **Custom Code** | ✅ | ✅ |

**Package Names**:
- Python:
  - `azure-ai-agentserver-core`
  - `azure-ai-agentserver-agentframework`
  - `azure-ai-agentserver-langgraph`
- .NET:
  - `Azure.AI.AgentServer.Core`
  - `Azure.AI.AgentServer.AgentFramework`

---

## 🚀 Demo Scenarios

### Scenario 1: Basic Hosted Agent with MAF

**Use Case**: Deploy a simple customer support agent that answers product questions

**Demo Flow**:
1. Show local agent code (MAF ChatAgent with instructions)
2. Add hosting adapter → instant HTTP server
3. Test locally with REST calls (localhost:8088)
4. Containerize with Dockerfile
5. Deploy with `azd up`
6. Show running agent in Foundry portal
7. Test with Foundry Responses API
8. Show conversation persistence across sessions

**Key Message**: "From code to production-ready hosted agent in minutes"

**Sample Code** (Python):
```python
#!/usr/bin/env python3
"""Basic customer support agent"""
from azure.ai.agentserver.agentframework import from_agentframework
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

# Create agent
agent = ChatAgent(
    chat_client=AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
    ),
    instructions="""
    You are a helpful customer support agent for Contoso Electronics.
    Answer product questions, help with orders, and provide troubleshooting.
    Be friendly and professional.
    """
)

# Host it!
if __name__ == "__main__":
    from_agentframework(agent).run()
    # Now accessible at http://localhost:8088
```

**Test Locally**:
```bash
# Terminal 1: Run the agent
python app.py

# Terminal 2: Test with curl
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [
        {"role": "user", "content": "What warranty comes with your laptops?"}
      ]
    }
  }'
```

---

### Scenario 2: Hosted Agent with MCP Tools

**Use Case**: Deploy an agent that can search Microsoft Learn documentation

**Demo Flow**:
1. Show agent with HostedMcpServerTool configuration
2. Test locally - agent automatically calls MCP server
3. Deploy as hosted agent
4. Show how agent uses remote MCP server in production
5. Demonstrate tool filtering and approval modes

**Key Message**: "Enterprise tools integration without managing infrastructure"

**Reference Sample**: `/maf-upstream/dotnet/samples/HostedAgents/AgentWithHostedMCP/`

**Sample Configuration**:
```python
from agent_framework import ChatAgent, HostedMCPTool
from agent_framework.azure import AzureOpenAIResponsesClient

agent = AzureOpenAIResponsesClient().create_agent(
    instructions="You are a helpful assistant that searches Microsoft documentation.",
    tools=[
        HostedMCPTool(
            server_url="https://learn.microsoft.com/api/mcp",
            tools_to_enable=["microsoft_docs_search"],
            approval_mode="never_require"  # Auto-approve tool calls
        )
    ]
)
```

---

### Scenario 3: Agents in Workflows (Hosted)

**Use Case**: Deploy a multi-step translation workflow as a hosted agent

**Demo Flow**:
1. Show workflow with 3 translation agents (EN→FR→ES→EN)
2. Each agent is a separate AI model call
3. Workflow orchestrates the sequence
4. Deploy entire workflow as a single hosted agent
5. Show how Foundry manages conversation state across steps

**Key Message**: "Complex multi-agent workflows as managed services"

**Reference Sample**: `/maf-upstream/dotnet/samples/HostedAgents/AgentsInWorkflows/`

**Architecture**:
```
User Input → [French Agent] → [Spanish Agent] → [English Agent] → Final Output
              Sequential Workflow (deployed as container)
              Managed by Azure AI Foundry Agent Service
```

---

### Scenario 4: Hosted Agent with RAG (Text Search)

**Use Case**: Document Q&A agent with uploaded files

**Demo Flow**:
1. Show agent with file upload capability
2. Upload company documents (PDFs, docs)
3. Agent uses Azure AI Search for retrieval
4. Deploy as hosted agent
5. Show how conversations maintain context
6. Demonstrate evaluation with built-in metrics

**Key Message**: "Enterprise RAG without managing infrastructure"

**Reference Sample**: `/maf-upstream/dotnet/samples/HostedAgents/AgentWithTextSearchRag/`

**Features**:
- Upload documents to vector store
- Automatic indexing with Azure AI Search
- Semantic search during conversations
- Built-in evaluation for response quality

---

## 📋 Prerequisites for Demo

### Azure Resources
- ✅ Azure AI Foundry project
- ✅ Azure OpenAI endpoint with model deployment (e.g., gpt-4o-mini)
- ✅ Azure Container Registry (created by `azd` or manual)
- ✅ Application Insights (created by `azd` or manual)

### Developer Tools
- ✅ Azure CLI (`az` command)
- ✅ Azure Developer CLI (`azd` command) with `ai agent` extension
- ✅ Docker Desktop (for containerization)
- ✅ Python 3.10+ or .NET 10+ SDK

### Permissions
- **For new project**: Account Owner + Azure AI User roles
- **For existing project**: Reader + Azure AI User roles
- **For full setup**: Contributor on subscription + Account Owner + Azure AI User on Foundry

---

## 🎬 Demo Script (15 minutes)

### Part 1: Local Development (5 min)

**Show**:
1. Simple MAF agent code (5 lines)
2. Add hosting adapter → `from_agentframework(agent).run()`
3. Test at `localhost:8088` with REST client
4. Show OpenTelemetry traces in AI Toolkit

**Talk Track**:
> "With just one line - `from_agentframework(agent).run()` - we transform our MAF agent into a production-ready HTTP service. The hosting adapter handles everything: REST endpoints, streaming, protocol translation, and observability."

### Part 2: Containerization (3 min)

**Show**:
1. Dockerfile (simple, pre-made)
2. `docker build` command
3. Optional: Show container running locally

**Talk Track**:
> "The agent becomes a standard container that can run anywhere - locally, in Azure, or any Kubernetes environment. The Foundry agent packages handle all the Azure-specific integration."

### Part 3: Deployment (4 min)

**Show**:
1. `azd ai agent init` → configure parameters
2. `azd up` → provision + deploy (show progress)
3. Agent appears in Foundry portal
4. Show agent status, logs, metrics

**Talk Track**:
> "Azure Developer CLI abstracts everything: provisioning, RBAC, container registry, Application Insights, managed identity. One command - `azd up` - and we're production-ready."

### Part 4: Production Features (3 min)

**Show**:
1. Test via Foundry Responses API
2. Show conversation persistence
3. Demonstrate autoscaling (simulate load)
4. Show Application Insights traces
5. Publish to Microsoft Teams (if time permits)

**Talk Track**:
> "Now our agent is enterprise-grade: autoscaling, managed state, built-in observability, and ready to publish to Teams or M365 Copilot. No Kubernetes, no DevOps complexity - just code to cloud."

---

## 🔧 Technical Deep Dive

### Conversation Management

**Automatic State Persistence**:
```python
# First request - creates conversation
response1 = client.responses.create(
    input=[{"role": "user", "content": "My order number is 12345"}]
)
conversation_id = response1.conversation_id

# Follow-up - context maintained
response2 = client.responses.create(
    input=[{"role": "user", "content": "What's the status?"}],
    conversation_id=conversation_id  # Agent knows about order 12345
)
```

### Lifecycle Management

```bash
# Create agent version
az cognitiveservices agent create-version \
  --account-name myAccount \
  --project-name myProject \
  --name myAgent \
  --image myregistry.azurecr.io/myagent:v2

# Start with scaling configuration
az cognitiveservices agent start \
  --account-name myAccount \
  --project-name myProject \
  --name myAgent \
  --agent-version 2 \
  --min-replicas 2 \
  --max-replicas 10

# Stop for maintenance
az cognitiveservices agent stop \
  --account-name myAccount \
  --project-name myProject \
  --name myAgent \
  --agent-version 2

# Delete specific version
az cognitiveservices agent delete \
  --account-name myAccount \
  --project-name myProject \
  --name myAgent \
  --agent-version 2
```

### Versioned vs Non-Versioned Updates

**Versioned Update** (creates new version):
- Container image changes
- CPU/memory allocation changes
- Environment variables
- Protocol versions

**Non-Versioned Update** (modifies existing):
- Min/max replicas (horizontal scaling)
- Description and tags

---

## 💡 Demo Tips & Best Practices

### Do's ✅

1. **Start Simple**: Begin with basic agent, add complexity progressively
2. **Show Local First**: Demonstrate localhost:8088 testing - it's impressive
3. **Highlight One-Liner**: `from_agentframework(agent).run()` is the hero
4. **Show Traces**: OpenTelemetry integration is a killer feature
5. **Emphasize "No DevOps"**: No Kubernetes, no scaling logic, no infra management
6. **Demo Conversation State**: Show follow-up questions work automatically
7. **Use Real Scenarios**: Customer support, doc search, data analysis

### Don'ts ❌

1. **Don't Skip Local Testing**: Jumping straight to deployment misses the point
2. **Avoid Complex Dockerfile**: Use simple pre-made examples
3. **Don't Over-Explain Azure**: Focus on developer experience
4. **Skip Kubernetes Mentions**: This is "beyond Kubernetes"
5. **Don't Debug Live**: Pre-test everything, have backup videos
6. **Avoid "In Preview" Disclaimers**: Focus on capabilities, mention limitations only if asked

### Common Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| Deployment takes 15-20 min | Pre-deploy, show portal; or have backup video |
| Port 8088 already in use | Kill existing processes or use different port |
| Azure auth fails | Pre-authenticate with `az login` |
| Container build slow | Use pre-built images or speed up with layer caching |
| Traces not showing | Verify OTEL_EXPORTER_ENDPOINT is set |

---

## 📊 Demo Variants by Audience

### For Developers

**Focus**: Developer experience, code simplicity, testing workflow

**Show**:
- VS Code with AI Toolkit for local tracing
- REST API testing with Postman/Thunder Client
- Dockerfile and build process
- Environment variable configuration

**Key Message**: "From agent code to production in 5 commands"

### For Architects

**Focus**: Enterprise architecture, scalability, security

**Show**:
- Autoscaling demonstration
- Managed identity and RBAC
- Application Insights integration
- Multi-region deployment options

**Key Message**: "Enterprise-grade agent hosting without infrastructure complexity"

### For Business/Product

**Focus**: Time to market, business value, channel integration

**Show**:
- Rapid deployment from code to Teams
- Conversation management UI
- Agent store publishing
- End-user experience in M365 Copilot

**Key Message**: "Deploy AI agents to millions of M365 users in hours, not months"

---

## 📚 Reference Resources

### Official Documentation
- [Hosted Agents Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry&tabs=cli)
- [Agent Development Lifecycle](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/development-lifecycle?view=foundry)
- [Publish and Share Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-agent?view=foundry)

### Code Samples
- **Python**: [GitHub - Hosted Agents Samples](https://github.com/azure-ai-foundry/foundry-samples/tree/hosted-agents/pyaf-samples/samples/microsoft/python/getting-started-agents/hosted-agents)
- **C#**: [GitHub - C# Hosted Agents](https://github.com/azure-ai-foundry/foundry-samples/tree/main/samples/csharp/hosted-agents)
- **Local Samples**:
  - `/maf-upstream/dotnet/samples/HostedAgents/AgentWithHostedMCP/`
  - `/maf-upstream/dotnet/samples/HostedAgents/AgentsInWorkflows/`
  - `/maf-upstream/dotnet/samples/HostedAgents/AgentWithTextSearchRag/`

### Tools & Extensions
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/overview)
- [AI Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)

---

## 🎯 Success Metrics for Demo

After the demo, audience should be able to:

- [ ] Explain what hosted agents are vs prompt-based agents
- [ ] Understand the role of the hosting adapter
- [ ] Identify when to use hosted agents (code-based, complex, production)
- [ ] Know the deployment workflow (local → container → azd → production)
- [ ] Recognize the managed service value proposition
- [ ] Be excited to try it themselves

---

## 🚀 Next Steps After Demo

### For Immediate Try-Out
1. Follow [Foundry starter template](https://github.com/Azure-Samples/azd-ai-starter-basic)
2. Start with simplest sample (basic agent)
3. Deploy locally, then to Foundry

### For Production Planning
1. Identify first agent candidate (customer support, doc search, etc.)
2. Assess Azure resources needed
3. Plan RBAC and security model
4. Design evaluation strategy

### For Learning More
1. Review all hosted agents samples in `/maf-upstream/dotnet/samples/HostedAgents/`
2. Read agent development lifecycle docs
3. Join Azure AI community Discord
4. Attend office hours (if available)

---

## ⚠️ Current Limitations (Preview)

| Limitation | Value |
|------------|-------|
| **Foundry resources per Azure subscription** | 100 |
| **Hosted agents per Foundry resource** | 200 |
| **Max min_replica count** | 2 |
| **Max max_replica count** | 5 |
| **Region availability** | North Central US only |
| **Private networking** | Not supported in preview |
| **Billing start date** | No earlier than February 1, 2026 |

**Note**: These are preview limitations and will likely expand at GA.

---

## 🎬 Conclusion

Hosted agents represent a significant shift in how we deploy agentic AI:

**From**:
- Manual infrastructure setup
- Complex Kubernetes configurations
- Custom API implementations
- DIY observability and scaling
- Weeks to deploy

**To**:
- One-line hosting adapter
- Managed infrastructure
- Built-in enterprise features
- Minutes to deploy
- Focus on agent logic, not DevOps

**The Demo Sweet Spot**: Show how MAF agent code becomes a production-ready, enterprise-grade service with minimal ceremony.

---

**Created**: December 20, 2025  
**Status**: Ready for demo preparation  
**Next**: Select demo variant, prepare Azure resources, practice timing

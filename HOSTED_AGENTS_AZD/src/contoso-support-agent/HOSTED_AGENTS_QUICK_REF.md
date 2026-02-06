# Hosted Agents - Quick Reference Card

**Last Updated**: February 5, 2026

---

## 🤝 MAF + Hosted Agents: The Relationship

**MAF (Microsoft Agent Framework)** = Build your agent (the framework/SDK)  
**Hosted Agents** = Run your agent (the managed hosting platform)  
**Hosting Adapter** = Bridge between them (one function call)

```
MAF Agent Code → Hosting Adapter → Hosted Agents Service
  (you write)      (from_*)         (Azure manages)
```

**In Plain English**:
- Use **MAF** to write agent logic (like using Flask for web apps)
- Use **Hosted Agents** to run it at scale (like Azure App Service for web apps)
- The **hosting adapter** connects them with one line of code

---

## 🎯 30-Second Pitch

> "Hosted Agents let you deploy your MAF code-based agents as fully managed, auto-scaling microservices on Azure - with one line of code for local testing and one command for production deployment. No Kubernetes, no infrastructure management."

---

## ⚡ Quick Commands

### Local Development
```bash
# Install packages (Python)
pip install azure-ai-agentserver-agentframework agent-framework

# Run agent locally (one line!)
python -c "from azure.ai.agentserver.agentframework import from_agentframework; \
           from agent_framework import ChatAgent; \
           from_agentframework(ChatAgent(...)).run()"

# Test locally
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"input": {"messages": [{"role": "user", "content": "Hello"}]}}'
```

### Deployment
```bash
# Install Azure Developer CLI (requires 1.23.0+)
curl -fsSL https://aka.ms/install-azd.sh | bash
azd version  # Verify 1.23.0 or later

# Initialize from starter template
azd init -t https://github.com/Azure-Samples/azd-ai-starter-basic

# Initialize agent from sample (NEW!)
azd ai agent init -m https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/hosted-agents/agent-framework/agent-with-foundry-tools/agent.yaml

# Deploy (one command!)
azd up  # Provisions + Deploys + Configures everything
```

### Management
```bash
# Start agent
az cognitiveservices agent start \
  --account-name myAccount --project-name myProject \
  --name myAgent --agent-version 1

# Stop agent
az cognitiveservices agent stop \
  --account-name myAccount --project-name myProject \
  --name myAgent --agent-version 1

# Update scaling (non-versioned - no new version created)
az cognitiveservices agent update \
  --account-name myAccount --project-name myProject \
  --name myAgent --agent-version 1 \
  --min-replicas 1 --max-replicas 3

# Create with remote build (no local Docker needed!)
az cognitiveservices agent create \
  --account-name myAccount --project-name myProject \
  --name myAgent --source ./src/my-agent \
  --registry myregistry --build-remote

# Stream logs during deployment
az cognitiveservices agent create --show-logs ...

# List all versions
az cognitiveservices agent list-versions \
  --account-name myAccount --project-name myProject \
  --name myAgent
```

---

## 🧩 Framework Support

| Framework | Python | C# |
|-----------|--------|-----|
| **Microsoft Agent Framework** | ✅ | ✅ |
| **LangGraph** | ✅ | ❌ |
| **Custom code** | ✅ | ✅ |

**Public Adapter Packages:**
- Python: `azure-ai-agentserver-core`, `azure-ai-agentserver-agentframework`, `azure-ai-agentserver-langgraph`
- .NET: `Azure.AI.AgentServer.Core`, `Azure.AI.AgentServer.AgentFramework`

---

## 🔑 Key Concepts

| Concept | Explanation |
|---------|-------------|
| **Hosting Adapter** | Transforms MAF agent code → HTTP service (one function call) |
| **Managed Service** | Azure handles: provisioning, scaling, state, identity, observability |
| **Conversation Objects** | Durable, cross-session state management (automatic) |
| **Versioned Updates** | Create new version for image/config/env changes |
| **Non-Versioned Updates** | Scale changes (min/max replicas) don't create new version |
| **Protocol Options** | `responses` (default) or `streaming` |
| **Activity Protocol** | A2A (agent-to-agent) patterns for M365 integration |
| **Publishing** | Deploy to Teams, M365 Copilot, Agent 365, or stable REST API |

---

## 📦 What You Get (Automatically)

✅ REST API endpoints (OpenAI Responses compatible)  
✅ SSE streaming support (configurable protocol)  
✅ OpenTelemetry tracing → Application Insights  
✅ Conversation state management  
✅ Autoscaling (horizontal, min 2/max 5 replicas in preview)  
✅ Managed identity & RBAC  
✅ Integration with Azure AI tools (Code Interpreter, Web Search, Image Gen, MCP)  
✅ OAuth identity passthrough for MCP servers (preserves user context)  
✅ Remote builds via ACR Task (no local Docker needed)  
✅ Activity Protocol & A2A patterns  
✅ Deployment to M365 channels + Agent 365  

---

## 🎬 5-Minute Demo Flow

1. **Show agent code** (simple MAF ChatAgent - 10 lines)
2. **Add hosting adapter** → `from_agentframework(agent).run()`
3. **Test locally** → curl to localhost:8088
4. **Deploy** → `azd up` (show progress)
5. **Test in Foundry** → Portal UI + Responses API
6. **Show conversation state** → Follow-up questions work
7. **Bonus**: Show non-versioned scaling or publish to Teams

**Key Talking Point**: *"From code to production-ready agent in 5 commands, no infrastructure management needed."*

**New Talking Points (Feb 2026)**:
- *"Remote builds with `--build-remote` - no Docker Desktop needed on my machine"*
- *"Scale changes don't create new versions - instant horizontal scaling"*
- *"OAuth passthrough for MCP servers preserves individual user context"*

---

## 🏗️ Architecture (One Image)

```
┌──────────────────┐
│   Your MAF Agent │  ← Write code
│   (Python/.NET)  │
└────────┬─────────┘
         │ from_agentframework(agent).run()
         ↓
┌──────────────────┐
│  Hosting Adapter │  ← Auto HTTP service
│  (localhost:8088)│
└────────┬─────────┘
         │ Docker build + azd up
         ↓
┌──────────────────┐
│  Azure AI Foundry│  ← Managed hosting
│   Agent Service  │     • Autoscaling
└────────┬─────────┘     • State mgmt
         │               • Observability
         ↓
┌──────────────────┐
│  Teams/M365/API  │  ← Publish channels
└──────────────────┘
```

---

## 🎯 Use Cases

| Use Case | Why Hosted Agents? |
|----------|-------------------|
| **Customer Support Bot** | State persistence, Teams integration, autoscaling |
| **Document Q&A** | RAG + managed infrastructure + conversation memory |
| **Multi-Agent Workflows** | Complex orchestration deployed as single service |
| **Enterprise Tools Integration** | MCP servers + managed identity + RBAC |
| **Internal Productivity** | Publish to M365 Copilot for org-wide access |

---

## 🆚 When to Use vs Alternatives

### Use Hosted Agents When:
✅ You have complex, code-based agent logic  
✅ You need production-grade hosting without DevOps  
✅ You want autoscaling and managed state  
✅ You're deploying to Microsoft 365 channels  
✅ You use MAF or LangGraph frameworks  

### Use Prompt-Based Agents When:
✅ Simple Q&A or chat scenarios  
✅ No complex code or workflows  
✅ Quick prototyping in the portal  
✅ No need for custom deployment  

### Use Custom Deployment When:
✅ Existing container orchestration (Kubernetes)  
✅ Multi-cloud requirements  
✅ Custom scaling logic needed  
✅ On-premises hosting required  

---

## 🚀 Samples (Local)

**Available Now**:
- `/maf-upstream/dotnet/samples/HostedAgents/AgentWithHostedMCP/`
  - MCP integration with Microsoft Learn search
- `/maf-upstream/dotnet/samples/HostedAgents/AgentsInWorkflows/`
  - Multi-agent translation workflow
- `/maf-upstream/dotnet/samples/HostedAgents/AgentWithTextSearchRag/`
  - RAG with document upload

**GitHub Samples (microsoft-foundry)**:
- [Python Hosted Agents](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents)
- [C# Hosted Agents](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/csharp/hosted-agents)
- [agent-with-foundry-tools](https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/hosted-agents/agent-framework/agent-with-foundry-tools/agent.yaml) - Web search + MCP sample

---

## 📋 Prerequisites Checklist

### Azure Resources
- [ ] Azure AI Foundry project created
- [ ] Azure OpenAI endpoint + deployment (gpt-4o-mini)
- [ ] Azure CLI installed and authenticated (`az login`)

### Developer Tools  
- [ ] Azure Developer CLI **1.23.0+** installed (`azd version`)
- [ ] `azd ai agent` extension (included in 1.23.0+)
- [ ] Docker Desktop running (or use `--build-remote` flag)
- [ ] Python 3.10+ or .NET 10+
- [ ] Azure AI Projects SDK 2.0.0b3+ (`pip install --pre "azure-ai-projects>=2.0.0b3"`)

### Permissions
- [ ] Azure AI User role on Foundry resource
- [ ] **Azure AI Owner** role (if creating new project)
- [ ] Contributor on subscription (for full setup)
- [ ] **Container Registry Repository Reader** role for project managed identity on ACR
- [ ] Reader role (minimum for existing project)

---

## ⚠️ Preview Limitations

- 🌐 **Regions**: Now **25 regions** supported (see list below)
- 🔢 **Replicas**: Max 5 (min 2) per deployment
- 🚫 **Private Network**: Not supported yet (can't use network-isolated Foundry resources)
- 💰 **Billing**: Starts no earlier than Feb 1, 2026
- 📊 **Scale**: 100 Foundry resources/subscription, 200 agents/resource
- ⚙️ **Capability Host**: Can't update existing - must delete and recreate with `enablePublicHostingEnvironment: true`

### Supported Regions (25 total)

| Americas | Europe | Asia Pacific | Middle East & Africa |
|----------|--------|--------------|---------------------|
| Brazil South | France Central | Australia East | South Africa North |
| Canada Central | Germany West Central | Japan East | UAE North |
| Canada East | Italy North | Korea Central | |
| East US | Norway East | South India | |
| East US 2 | Poland Central | Southeast Asia | |
| North Central US | Spain Central | | |
| South Central US | Sweden Central | | |
| West US | Switzerland North | | |
| West US 3 | UK South | | |

**Tip**: For best availability, use **East US 2** or **Sweden Central** as primary regions.

---

## � Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| `azd init` fails | Run `azd version` - requires 1.23.0+. Update: `brew upgrade azd` (macOS) |
| Docker build errors | Ensure Docker Desktop running, or use `--build-remote` flag |
| `SubscriptionNotRegistered` | `az provider register --namespace Microsoft.CognitiveServices` |
| `AuthorizationFailed` | Request **Contributor** role on subscription |
| Agent doesn't start locally | Check env vars, run `az login` to refresh credentials |
| `AcrPullUnauthorized` | Grant **Container Registry Repository Reader** role to project managed identity |
| Model not found | Fork sample agent.yaml, change model to one in your subscription |

---

## �🔗 Essential Links

| Resource | URL |
|----------|-----|
| **Hosted Agents Docs** | [aka.ms/foundry-hosted-agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry) |
| **Deploy Hosted Agent** | [How-to Guide](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent?view=foundry) |
| **Quickstart** | [Deploy First Hosted Agent](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstarts/quickstart-hosted-agent?view=foundry) |
| **Azure Developer CLI** | [aka.ms/azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/) |
| **Starter Template** | [GitHub](https://github.com/Azure-Samples/azd-ai-starter-basic) |
| **Foundry Samples** | [GitHub](https://github.com/azure-ai-foundry/foundry-samples) |
| **AI Toolkit (VS Code)** | [Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio) |

---

## 💬 Elevator Pitches by Audience

### For Developers
> "Turn your MAF agent into a production HTTP service with one line of code. Test locally, deploy with `azd up`, get autoscaling, observability, and state management for free."

### For Architects
> "Enterprise-grade agent hosting without Kubernetes. Microsoft manages infrastructure, scaling, identity, and observability. You write agent code, we handle DevOps."

### For Business
> "Deploy AI agents to Microsoft Teams and Copilot in hours instead of months. No infrastructure team required."

---

## 🎤 Demo Sound Bites

Use these during demos for impact:

1. **On the Hosting Adapter**:
   > "This one line - `from_agentframework(agent).run()` - transforms my agent into a production-ready HTTP service with streaming, tracing, and protocol compliance. No Flask, no FastAPI, no configuration."

2. **On Managed Service**:
   > "I don't provision infrastructure, I don't configure Kubernetes, I don't set up monitoring. Azure handles provisioning, autoscaling, state management, and observability. I just write agent logic."

3. **On Deployment**:
   > "One command - `azd up` - provisions everything: container registry, Application Insights, managed identity, RBAC, the agent deployment. From code to production in 5 minutes."

4. **On Conversation State**:
   > "Notice how the agent remembers context across messages. That's automatic. Foundry manages conversation objects, state persistence, and thread continuity. I didn't write any state management code."

5. **On Publishing**:
   > "Now this agent is published to Microsoft Teams. Anyone in my org can chat with it. Same agent, same code, now available to thousands of users. No app packaging, no deployment complexity."

---

## ⏱️ Time Estimates

| Activity | Time |
|----------|------|
| **Code → Local test** | 2 minutes |
| **Containerize** | 1 minute (pre-made Dockerfile) |
| **First deployment** | 15-20 minutes (provision + deploy) |
| **Subsequent deploys** | 5-10 minutes |
| **Test in portal** | 2 minutes |
| **Publish to Teams** | 5 minutes |

💡 **Demo Tip**: Pre-deploy and show portal for live demos. Have backup recording for cold deploys.

---

## 🎯 Success Indicators

After your demo, attendees should:
- [ ] Understand "code-based agents + managed hosting"
- [ ] Know the magic one-liner: `from_agentframework(agent).run()`
- [ ] Appreciate the "no DevOps" value proposition
- [ ] Want to try it themselves
- [ ] See clear use cases for their scenarios

---

**For full details, see**: [`HOSTED_AGENTS_DEMO_GUIDE.md`](./HOSTED_AGENTS_DEMO_GUIDE.md)

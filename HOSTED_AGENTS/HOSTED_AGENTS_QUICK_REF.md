# Hosted Agents - Quick Reference Card

**Last Updated**: December 20, 2025

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
# Install Azure Developer CLI
curl -fsSL https://aka.ms/install-azd.sh | bash

# Initialize from template
azd init -t https://github.com/Azure-Samples/azd-ai-starter-basic

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

# List all versions
az cognitiveservices agent list-versions \
  --account-name myAccount --project-name myProject \
  --name myAgent
```

---

## 🔑 Key Concepts

| Concept | Explanation |
|---------|-------------|
| **Hosting Adapter** | Transforms MAF agent code → HTTP service (one function call) |
| **Managed Service** | Azure handles: provisioning, scaling, state, identity, observability |
| **Conversation Objects** | Durable, cross-session state management (automatic) |
| **Versioning** | Create versions for image/config changes; update in place for scaling |
| **Publishing** | Deploy to Teams, M365 Copilot, or stable REST API |

---

## 📦 What You Get (Automatically)

✅ REST API endpoints (OpenAI Responses compatible)  
✅ SSE streaming support  
✅ OpenTelemetry tracing → Application Insights  
✅ Conversation state management  
✅ Autoscaling (horizontal, 1-5 replicas in preview)  
✅ Managed identity & RBAC  
✅ Integration with Azure AI tools (Code Interpreter, Web Search, MCP)  
✅ Deployment to M365 channels  

---

## 🎬 5-Minute Demo Flow

1. **Show agent code** (simple MAF ChatAgent - 10 lines)
2. **Add hosting adapter** → `from_agentframework(agent).run()`
3. **Test locally** → curl to localhost:8088
4. **Deploy** → `azd up` (show progress)
5. **Test in Foundry** → Portal UI + Responses API
6. **Show conversation state** → Follow-up questions work
7. **Bonus**: Show autoscaling or publish to Teams

**Key Talking Point**: *"From code to production-ready agent in 5 commands, no infrastructure management needed."*

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

**GitHub Samples**:
- [Python Samples](https://github.com/azure-ai-foundry/foundry-samples/tree/hosted-agents/pyaf-samples/samples/microsoft/python/getting-started-agents/hosted-agents)
- [C# Samples](https://github.com/azure-ai-foundry/foundry-samples/tree/main/samples/csharp/hosted-agents)

---

## 📋 Prerequisites Checklist

### Azure Resources
- [ ] Azure AI Foundry project created
- [ ] Azure OpenAI endpoint + deployment (gpt-4o-mini)
- [ ] Azure CLI installed and authenticated (`az login`)

### Developer Tools  
- [ ] Azure Developer CLI installed (`azd`)
- [ ] `azd ai agent` extension installed
- [ ] Docker Desktop running
- [ ] Python 3.10+ or .NET 10+

### Permissions
- [ ] Azure AI User role on Foundry resource
- [ ] Contributor on subscription (for full setup)
- [ ] Reader role (minimum for existing project)

---

## ⚠️ Preview Limitations

- 🌐 **Region**: North Central US only
- 🔢 **Replicas**: Max 5 (min 2) per deployment
- 🚫 **Private Network**: Not supported yet
- 💰 **Billing**: Starts no earlier than Feb 1, 2026
- 📊 **Scale**: 100 Foundry resources/subscription, 200 agents/resource

---

## 🔗 Essential Links

| Resource | URL |
|----------|-----|
| **Hosted Agents Docs** | [aka.ms/foundry-hosted-agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry) |
| **Azure Developer CLI** | [aka.ms/azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/) |
| **Starter Template** | [GitHub](https://github.com/Azure-Samples/azd-ai-starter-basic) |
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

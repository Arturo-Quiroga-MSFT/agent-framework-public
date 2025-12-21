# Microsoft Agent Framework vs Hosted Agents: Comprehensive Comparison

**Last Updated:** December 20, 2025

## Table of Contents
1. [Overview](#overview)
2. [Microsoft Agent Framework (MAF)](#microsoft-agent-framework-maf)
3. [Hosted Agents](#hosted-agents)
4. [How MAF and Hosted Agents Work Together](#how-maf-and-hosted-agents-work-together)
5. [Key Differences](#key-differences)
6. [Decision Guide](#decision-guide)
7. [References](#references)

---

## Overview

This document provides a comprehensive comparison between Microsoft's two complementary offerings for the AI agent lifecycle:
- **Microsoft Agent Framework (MAF)**: An open-source SDK for building custom AI agents
- **Hosted Agents**: A managed Azure service for deploying and running agents built with MAF or other frameworks

These are **not alternatives** but work together: MAF is the development layer, Hosted Agents is the deployment layer.

---

## Microsoft Agent Framework (MAF)

### What is MAF?

Microsoft Agent Framework is an open-source development kit for building AI agents and multi-agent workflows for .NET and Python. It is the direct successor to Semantic Kernel and AutoGen, built by the same teams to combine their strengths while adding new capabilities.

**Status:** Public Preview  
**Repository:** https://github.com/microsoft/agent-framework  
**Documentation:** https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview

### Architecture & Components

#### 1. Individual AI Agents (V1 & V2)

An AI agent in MAF consists of:
- **Model (LLM)**: The reasoning core (Azure OpenAI, OpenAI, Azure AI)
- **Instructions**: Define goals, behavior, and constraints
- **Tools**: Enable retrieval and actions via MCP servers
- **Thread**: State management for multi-turn conversations
- **Context Providers**: Agent memory capabilities
- **Middleware**: Intercept and modify agent actions

**Agent Lifecycle:**
```
User Input → Agent Processing → Tool Calls → Response Generation
```

#### 2. Workflows

Graph-based orchestration system for complex multi-agent coordination:

**Key Features:**
- **Modularity**: Reusable components
- **Type Safety**: Strong typing with validation
- **Flexible Flow**: Conditional routing, parallel processing
- **Checkpointing**: Save/resume long-running processes
- **External Integration**: Request/response patterns for human-in-the-loop
- **Multi-Agent Orchestration**: Sequential, concurrent, hand-off, Magentic patterns
- **Composability**: Nested and combined workflows

**Workflow Structure:**
```
Agent A → Function → Agent B → Conditional Router → Agent C/D
```

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Language Support** | Python & .NET with consistent APIs |
| **Model Providers** | Azure OpenAI, OpenAI, Azure AI |
| **Tool Integration** | Model Context Protocol (MCP) support |
| **State Management** | Thread-based conversations |
| **Observability** | OpenTelemetry integration |
| **Type Safety** | Comprehensive validation |
| **Middleware** | Request/response processing, exception handling |
| **DevUI** | Interactive developer UI for testing/debugging |

### Installation

**Python:**
```bash
pip install agent-framework --pre
```

**C#/.NET:**
```bash
dotnet add package Microsoft.Agents.AI
```

### When to Use MAF

✅ **Best Use Cases:**
- **Autonomous Decision-Making**: Tasks requiring dynamic planning
- **Customer Support**: Multi-modal queries (text, voice, images)
- **Education & Tutoring**: Personalized learning with knowledge bases
- **Code Generation**: Development assistance, code reviews, debugging
- **Research Assistance**: Web search, document summarization, multi-source analysis
- **Complex Workflows**: Multi-step processes with explicit control requirements
- **Unstructured Inputs**: Tasks where exact sequence is not predefined

❌ **When NOT to Use:**
- **Highly Structured Tasks**: Predefined rules and sequences
- **Simple Functions**: If you can write a function, do that instead
- **Single Agent Limitations**: Tasks requiring 20+ tools (use workflows instead)

### Migration Path

MAF provides migration guides for:
- **From Semantic Kernel**: Enterprise features + multi-agent capabilities
- **From AutoGen**: Enhanced abstractions + type safety + state management

---

## Hosted Agents

### What is Hosted Agents?

Hosted Agents is an Azure AI Foundry managed service that containerizes and deploys agents built with frameworks like MAF or LangGraph. It provides production-grade infrastructure, scaling, and enterprise features for running agents in production.

**Key Concept**: Hosted Agents is **not a framework**—it's a deployment platform. You build agents using MAF (or LangGraph), then deploy them to Hosted Agents for production hosting.

**Platform:** Azure AI Foundry  
**Documentation:** https://learn.microsoft.com/azure/ai-studio/agents/agents-overview  
**Hosting Adapter Package (Python):** `azure-ai-agentserver-agentframework`  
**Hosting Adapter Package (.NET):** `Azure.AI.AgentServer.AgentFramework`

### The Deployment Platform Model

Hosted Agents provides managed infrastructure for agents built with frameworks:

#### 1. Models
Select from LLM catalog:
- GPT-4o, GPT-4, GPT-3.5 (Azure OpenAI)
- Llama and other models
- Growing catalog of AI models

#### 2. Customizability
- Fine-tuning for domain-specific tasks
- Distillation for performance optimization
- Custom prompts encoding behavior patterns

#### 3. Knowledge & Tools
Integration with enterprise systems:
- **Knowledge**: Bing, SharePoint, Azure AI Search
- **Actions**: Azure Logic Apps, Azure Functions, OpenAPI endpoints

#### 4. Orchestration
Server-side management:
- Tool call handling
- Conversation state updates
- Retry logic
- Structured logging

#### 5. Observability
Full traceability:
- Logs, traces, and evaluations
- Application Insights integration
- Conversation-level visibility
- Performance monitoring

#### 6. Trust & Safety
Enterprise-grade security:
- Microsoft Entra identity
- Role-Based Access Control (RBAC)
- Content filters (XPIA mitigation)
- Encryption at rest and in transit
- Network isolation (VNet support)

### Agent Types in Hosted Agents

#### 1. Declarative Agents

**Prompt-Based:**
- Single agent configuration
- Model + instructions + tools + prompts
- Declaratively defined behavior

**Workflow:**
- Agentic workflows in YAML or code
- Multi-agent orchestration
- Event-triggered actions

#### 2. Code-Based Agents (MAF/LangGraph)
- Built using MAF or LangGraph frameworks
- Containerized using hosting adapter
- Deployed and scaled by Azure
- Full programmatic control with managed hosting

### Enterprise Features

| Feature | Description |
|---------|-------------|
| **Conversation Visibility** | Full access to user-to-agent and agent-to-agent messages |
| **Multi-Agent Coordination** | Built-in agent-to-agent messaging |
| **Tool Orchestration** | Server-side execution with retry logic |
| **Trust & Safety** | Integrated content filters, policy governance |
| **Enterprise Integration** | BYOS (Bring Your Own Storage), Azure AI Search, VNet |
| **Identity & Policy** | Microsoft Entra, RBAC, audit logs, conditional access |
| **Observability** | Full traceability, Application Insights |
| **BCDR** | Business continuity via Azure Cosmos DB |

### Business Continuity & Disaster Recovery (BCDR)

Hosted Agents uses Azure Cosmos DB for agent state persistence and resilience:
- **Single-tenant account**: Customer-managed
- **Agent state preservation**: All history stored in Cosmos DB
- **Automatic failover**: Agent available in secondary region
- **Seamless continuity**: Minimal disruption during outages

### When to Use Hosted Agents

✅ **Best Use Cases:**
- **Production Enterprise Deployments**: Governance and compliance requirements
- **Multi-Region Availability**: High availability across Azure regions
- **Agent-to-Agent Coordination**: Scale across multiple agents
- **Trust & Safety Critical**: Content filtering, XPIA protection
- **Azure Ecosystem**: Integration with Azure services
- **Managed Infrastructure**: Platform-handled operations
- **Full Observability**: Enterprise monitoring and debugging
- **Process Automation**: Invoice processing, ticket management, document summarization

❌ **When NOT to Use:**
- **Prototyping phase**: Use MAF for development
- **Non-Azure environments**: On-premises or other clouds
- **Full code control required**: Custom infrastructure needs
- **Cost-sensitive experiments**: Open-source alternatives better

---

## How MAF and Hosted Agents Work Together

### The Two-Layer Stack

```
┌─────────────────────────────────────────────┐
│  LAYER 2: Hosted Agents (Azure Platform)   │
│  • Containerization & deployment            │
│  • Autoscaling & load balancing             │
│  • Monitoring & logging                     │
│  • Enterprise security & compliance         │
└─────────────────────────────────────────────┘
                     ↑
              Hosting Adapter
      from_agentframework(agent).run()
                     ↓
┌─────────────────────────────────────────────┐
│  LAYER 1: MAF (Development Framework)       │
│  • Agent creation & logic                   │
│  • Workflow orchestration                   │
│  • Tool integration (MCP)                   │
│  • Local development & testing              │
└─────────────────────────────────────────────┘
```

### Development → Production Flow

1. **Build with MAF** (Layer 1)
   - Write agent code in Python or .NET
   - Test locally with DevUI
   - Integrate tools via MCP

2. **Add Hosting Adapter** (Bridge)
   ```python
   # Python
   from azure.ai.agentserver.agentframework import from_agentframework
   from_agentframework(agent).run()  # One line!
   ```
   ```csharp
   // C#/.NET
   AgentServerAdapter.FromAgentFramework(agent).Run();
   ```

3. **Deploy to Hosted Agents** (Layer 2)
   ```bash
   azd up  # Azure Developer CLI
   ```

4. **Azure Manages**
   - Containers, scaling, monitoring, security

### Why This Matters

- **MAF alone**: You build agents, you manage infrastructure
- **Hosted Agents alone**: Doesn't work—needs a framework (MAF or LangGraph)
- **MAF + Hosted Agents**: You build agents, Azure manages infrastructure

**Analogy**: MAF is like Django (web framework), Hosted Agents is like Azure App Service (hosting platform), and the hosting adapter is like WSGI (the bridge).

---

## Key Differences

### Side-by-Side Comparison

| Aspect | Microsoft Agent Framework (MAF) | Hosted Agents |
|--------|--------------------------------|----------------------|
| **Nature** | Open-source SDK/Framework | Managed Cloud Service |
| **Deployment** | Self-managed, anywhere | Azure-hosted |
| **Target Audience** | Developers building custom solutions | Enterprise production deployments |
| **Control Level** | Full code-level control | Platform-managed with policies |
| **Languages** | Python & .NET | Language-agnostic (API-based) |
| **Infrastructure** | Bring your own | Platform-managed or BYOI |
| **State Management** | Thread-based, developer-managed | Cosmos DB-backed with BCDR |
| **Observability** | OpenTelemetry integration | Native Application Insights + full tracing |
| **Security** | Developer-implemented | Built-in enterprise-grade |
| **Identity** | Custom implementation | Microsoft Entra built-in |
| **Content Safety** | Manual implementation | Integrated content filters |
| **Multi-Agent** | Workflow orchestration | Built-in coordination |
| **Cost Model** | Open-source (compute only) | Service + infrastructure pricing |
| **Migration** | From SK/AutoGen supported | N/A |
| **Development** | Local + cloud | Cloud-first |
| **Compliance** | Developer responsibility | Platform-enforced |
| **Support** | Community + Microsoft docs | Enterprise SLA available |

### Development Lifecycle Comparison

**MAF Standalone Workflow:**
```
Local Development → Testing → Custom Deployment → Self-Managed Operations
```

**MAF + Hosted Agents Workflow:**
```
Build with MAF → Add Hosting Adapter → azd up → Azure-Managed Operations
```

**Declarative Agent Workflow (Hosted Agents):**
```
Portal Configuration → Testing → Managed Deployment → Platform Operations
```

---

## Decision Guide

### Choose Microsoft Agent Framework (MAF) When:

1. **Development & Experimentation**
   - Building custom agent solutions
   - Prototyping new agent patterns
   - Research and innovation projects

2. **Infrastructure Requirements**
   - Need to run agents on-premises
   - Multi-cloud deployments
   - Custom hosting requirements

3. **Control & Customization**
   - Full code-level control required
   - Custom state management needed
   - Specific framework requirements

4. **Cost Considerations**
   - Budget-conscious projects
   - Pay only for compute resources
   - No platform fees

5. **Migration Projects**
   - Moving from Semantic Kernel
   - Migrating from AutoGen
   - Consolidating agent frameworks

6. **Platform Flexibility**
   - Cross-platform deployment (Python/.NET)
   - Integration with non-Azure services
   - Vendor independence

### Choose Hosted Agents When:

1. **Enterprise Production**
   - Deploying agents to production
   - Enterprise compliance requirements
   - Multi-region high availability needed

2. **Governance & Security**
   - Microsoft Entra integration required
   - RBAC and audit logs mandatory
   - Content safety filters essential

3. **Azure Ecosystem**
   - Already using Azure services
   - Integration with Azure AI Search, Logic Apps
   - VNet and private endpoints needed

4. **Managed Operations**
   - Prefer managed infrastructure
   - Want built-in observability
   - Need automated BCDR

5. **Scale Requirements**
   - Agent-to-agent coordination at scale
   - High-throughput scenarios
   - Global distribution

6. **Time to Market**
   - Rapid production deployment
   - Pre-built security features
   - Reduced operational overhead

### Recommended Approach: Use Both Together

The recommended pattern for most production scenarios:

**Development Phase (MAF):**
- Build agents locally with full control
- Test with DevUI and local debugging
- Iterate quickly with Python/.NET
- Integrate tools via MCP

**Production Phase (Hosted Agents):**
- Add one line: `from_agentframework(agent).run()`
- Deploy with `azd up`
- Azure manages containers, scaling, monitoring
- Enterprise security and compliance built-in

**This is the intended workflow**: MAF for development, Hosted Agents for production. They're designed to work together, not as alternatives.

---

## Migration & Interoperability

### From Semantic Kernel to MAF
MAF inherits and extends Semantic Kernel's enterprise features:
- Thread-based state management
- Type safety and validation
- Extensive model support
- **Plus**: Multi-agent workflows, checkpointing, graph orchestration

### From AutoGen to MAF
MAF builds on AutoGen's agent abstractions:
- Simple multi-agent patterns
- Tool integration
- Conversation management
- **Plus**: Type safety, middleware, enterprise observability

### MAF to Hosted Agents
Agents built with MAF deploy to Hosted Agents with minimal changes:
- Install hosting adapter package: `pip install azure-ai-agentserver-agentframework`
- Add one line: `from_agentframework(agent).run()`
- Deploy with Azure Developer CLI: `azd up`
- No rewrite needed—MAF code runs as-is

---

## Use Case Matrix

### Customer Support

| Requirement | MAF Standalone | MAF + Hosted Agents | Recommendation |
|-------------|----------------|---------------------|----------------|
| Basic chatbot | ✅ | ✅ | MAF standalone for cost |
| Multi-modal (text/voice/image) | ✅ | ✅ | Either |
| Enterprise compliance | ⚠️ | ✅ | MAF + Hosted Agents |
| Custom CRM integration | ✅ | ✅ | Either (MAF for both) |
| 24/7 high availability | ⚠️ | ✅ | MAF + Hosted Agents |

### Code Generation

| Requirement | MAF Standalone | MAF + Hosted Agents | Recommendation |
|-------------|----------------|---------------------|----------------|
| IDE integration | ✅ | ⚠️ | MAF standalone |
| Code review automation | ✅ | ✅ | Either |
| Enterprise code policies | ⚠️ | ✅ | MAF + Hosted Agents |
| Custom language support | ✅ | ✅ | MAF (either deployment) |
| Multi-developer teams | ✅ | ✅ | Either |

### Document Processing

| Requirement | MAF Standalone | MAF + Hosted Agents | Recommendation |
|-------------|----------------|---------------------|----------------|
| Invoice processing | ✅ | ✅ | MAF + Hosted Agents for scale |
| Custom document types | ✅ | ✅ | Either (MAF for both) |
| Compliance requirements | ⚠️ | ✅ | MAF + Hosted Agents |
| On-premises processing | ✅ | ❌ | MAF standalone |
| Azure AI Search integration | ✅ | ✅ | MAF + Hosted Agents |

### Research & Analysis

| Requirement | MAF Standalone | MAF + Hosted Agents | Recommendation |
|-------------|----------------|---------------------|----------------|
| Web scraping | ✅ | ✅ | MAF (either deployment) |
| Multi-source synthesis | ✅ | ✅ | Either |
| Academic institutions | ✅ | ⚠️ | MAF standalone (cost) |
| Enterprise research | ✅ | ✅ | MAF + Hosted Agents |
| Custom data sources | ✅ | ✅ | MAF (either deployment) |

Legend:
- ✅ Well-supported
- ⚠️ Possible but requires extra work
- ❌ Not supported

---

## Technical Deep Dive

### MAF Architecture

```
┌─────────────────────────────────────────────┐
│          User Application Layer             │
├─────────────────────────────────────────────┤
│   Agent Framework SDK (Python/.NET)         │
│   ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│   │  Agents  │  │ Workflows │  │  Tools  │ │
│   └──────────┘  └──────────┘  └─────────┘ │
├─────────────────────────────────────────────┤
│   Core Components                           │
│   ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│   │  Models  │  │  Threads │  │  MCP    │ │
│   └──────────┘  └──────────┘  └─────────┘ │
├─────────────────────────────────────────────┤
│   Infrastructure (Developer-Managed)        │
│   ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│   │ Compute  │  │ Storage  │  │ Network │ │
│   └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────┘
```

### Hosted Agents Architecture

```
┌─────────────────────────────────────────────┐
│         User Applications / APIs            │
├─────────────────────────────────────────────┤
│       Hosted Agents Service (Managed)       │
│   ┌────────────────────────────────────┐   │
│   │     Agent Runtime & Orchestration  │   │
│   ├────────────────────────────────────┤   │
│   │  Identity  │  Safety  │ Observability│ │
│   ├────────────────────────────────────┤   │
│   │     Cosmos DB (State/BCDR)         │   │
│   └────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│      Azure Platform Services                │
│   ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│   │   Entra  │  │ AI Search│  │  Logic  │ │
│   │    ID    │  │          │  │  Apps   │ │
│   └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────┘
```

---

## Cost Considerations

### MAF Standalone Cost Model

**Costs:**
- Compute resources (VMs, containers, serverless)
- Model API calls (Azure OpenAI, OpenAI)
- Storage for state management
- Network egress
- Observability tools (optional)

**Benefits:**
- No platform fees
- Pay only for what you use
- Flexible cost optimization
- Can use free/open models

**Typical Monthly Cost (Small Project):**
- Compute: $50-200
- Model APIs: $100-500
- Storage: $10-50
- **Total: $160-750/month**

### Hosted Agents Cost Model

**Costs:**
- Hosted Agents service fees
- Model API calls
- Azure Cosmos DB (customer-provisioned)
- Azure AI Search (if used)
- Application Insights
- Network egress

**Benefits:**
- Managed infrastructure
- Built-in features (no dev cost)
- Predictable pricing
- Enterprise SLA

**Typical Monthly Cost (Small Project):**
- Hosted Agents Service: $200-500
- Model APIs: $100-500
- Cosmos DB: $100-300
- Observability: $50-100
- **Total: $450-1400/month**

**Note:** Enterprise features and reduced operational overhead often justify higher costs for production deployments. Using MAF + Hosted Agents eliminates infrastructure management costs.

---

## Best Practices

### For MAF Development

1. **Start Simple**: Begin with single agents before building workflows
2. **Use Type Safety**: Leverage type validation to catch errors early
3. **Implement Observability**: Set up OpenTelemetry from the start
4. **Test Locally**: Use DevUI for interactive debugging
5. **Checkpoint Workflows**: Save state for long-running processes
6. **Manage Context**: Use context providers for agent memory
7. **Tool Design**: Keep tools focused and well-documented
8. **Error Handling**: Implement middleware for consistent error management

### For Hosted Agents Deployment

1. **Plan BCDR**: Configure Cosmos DB with appropriate backup policies
2. **Identity First**: Set up Microsoft Entra integration early
3. **Content Filters**: Configure and test safety filters
4. **Monitor Everything**: Enable Application Insights from day one
5. **Network Security**: Use VNet integration for sensitive data
6. **Agent Coordination**: Design clear communication patterns
7. **Cost Management**: Set up budgets and alerts
8. **Governance**: Establish RBAC policies before production

---

## Future Roadmap

### MAF (Open Source)
- Expanded model provider support
- Enhanced workflow patterns
- Performance optimizations
- Community contributions
- Integration with more MCP servers

### Hosted Agents Service
- Additional Azure service integrations
- Advanced agent coordination patterns
- Enhanced observability features
- Improved MAF/LangGraph integration
- Expanded regional availability
- Streamlined deployment experience

---

## References

### Official Documentation

**Microsoft Agent Framework:**
- GitHub Repository: https://github.com/microsoft/agent-framework
- Documentation: https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview
- Quick Start: https://learn.microsoft.com/agent-framework/tutorials/quick-start
- User Guide: https://learn.microsoft.com/en-us/agent-framework/user-guide/overview
- Migration from Semantic Kernel: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel
- Migration from AutoGen: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen

**Hosted Agents:**
- Overview: https://learn.microsoft.com/azure/ai-studio/agents/agents-overview
- Quickstart: https://learn.microsoft.com/azure/ai-studio/agents/deploy-agent
- Hosting Adapter (Python): https://pypi.org/project/azure-ai-agentserver-agentframework/
- Hosting Adapter (.NET): https://www.nuget.org/packages/Azure.AI.AgentServer.AgentFramework/
- Azure Developer CLI: https://learn.microsoft.com/azure/developer/azure-developer-cli/overview

**Community Resources:**
- Discord: https://discord.gg/b5zjErwbQM (Azure AI Foundry)
- Weekly Office Hours: https://github.com/microsoft/agent-framework/blob/main/COMMUNITY.md

### Related Technologies
- Semantic Kernel: https://github.com/microsoft/semantic-kernel
- AutoGen: https://github.com/microsoft/autogen
- Model Context Protocol: https://modelcontextprotocol.io/

---

## Conclusion

Microsoft Agent Framework and Hosted Agents are **complementary technologies** designed to work together:

- **MAF** is the development framework—where you write agent code
- **Hosted Agents** is the deployment platform—where Azure runs your agents
- **Hosting Adapter** is the bridge—one line of code connects them

**Key Insight**: These are not competing solutions. For production deployments, the recommended path is:
1. Build with MAF (development framework)
2. Add hosting adapter (one line)
3. Deploy to Hosted Agents (Azure manages infrastructure)

This gives you the flexibility of code-based development with the benefits of managed cloud infrastructure.

**For Teams**:
- **Developers**: Write agents in MAF with full programmatic control
- **DevOps**: Deploy with `azd up`, Azure handles containers/scaling/monitoring
- **Security**: Built-in enterprise compliance, no infrastructure management

---

**Document Version:** 2.0  
**Last Updated:** December 20, 2025  
**Author:** Research compiled from official Microsoft documentation  
**Next Review:** Q1 2026

# Microsoft Agent Framework vs Foundry Agent Service: Comprehensive Comparison

**Last Updated:** December 9, 2025

## Table of Contents
1. [Overview](#overview)
2. [Microsoft Agent Framework (MAF)](#microsoft-agent-framework-maf)
3. [Microsoft Foundry Agent Service](#microsoft-foundry-agent-service)
4. [Key Differences](#key-differences)
5. [Decision Guide](#decision-guide)
6. [References](#references)

---

## Overview

This document provides a comprehensive comparison between Microsoft's two primary offerings for building AI agents:
- **Microsoft Agent Framework (MAF)**: An open-source SDK for building custom AI agents
- **Microsoft Foundry Agent Service**: A managed enterprise platform for deploying production agents

Both are Microsoft products but serve different purposes in the AI agent development lifecycle.

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

## Microsoft Foundry Agent Service

### What is Foundry Agent Service?

A production-ready, managed platform for deploying intelligent agents in enterprise environments. It serves as the runtime and orchestration layer that connects models, tools, frameworks, and governance into a unified system.

**Platform:** Azure AI Foundry  
**Documentation:** https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview

### The "Agent Factory" Model

Foundry operates as an assembly line for building production agents:

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

### Agent Types in Foundry

#### 1. Declarative Agents

**Prompt-Based:**
- Single agent configuration
- Model + instructions + tools + prompts
- Declaratively defined behavior

**Workflow:**
- Agentic workflows in YAML or code
- Multi-agent orchestration
- Event-triggered actions

#### 2. Hosted Agents
- Containerized agents
- Code-based creation and deployment
- Foundry-managed hosting

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

Foundry relies on customer-provisioned Azure Cosmos DB for resilience:
- **Single-tenant account**: Customer-managed
- **Agent state preservation**: All history stored in Cosmos DB
- **Automatic failover**: Agent available in secondary region
- **Seamless continuity**: Minimal disruption during outages

### When to Use Foundry Agent Service

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

## Key Differences

### Side-by-Side Comparison

| Aspect | Microsoft Agent Framework (MAF) | Foundry Agent Service |
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

**MAF Workflow:**
```
Local Development → Testing → Custom Deployment → Self-Managed Operations
```

**Foundry Workflow:**
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

### Choose Foundry Agent Service When:

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

### Hybrid Approach: Use Both

Many organizations use a hybrid strategy:

**Development Phase:**
- Use MAF for building and testing agents locally
- Iterate quickly with full control
- Experiment with different patterns

**Production Phase:**
- Deploy to Foundry Agent Service for enterprise features
- Leverage managed infrastructure
- Benefit from built-in governance

**Integration:**
MAF agents can be adapted to run on Foundry's runtime, enabling a smooth transition from development to production.

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

### MAF to Foundry
While not a direct migration, agents built with MAF can be adapted for Foundry:
- Extract agent logic and tools
- Configure in Foundry portal
- Deploy with enterprise features

---

## Use Case Matrix

### Customer Support

| Requirement | MAF | Foundry | Recommendation |
|-------------|-----|---------|----------------|
| Basic chatbot | ✅ | ✅ | MAF for cost |
| Multi-modal (text/voice/image) | ✅ | ✅ | Either |
| Enterprise compliance | ⚠️ | ✅ | Foundry |
| Custom CRM integration | ✅ | ⚠️ | MAF |
| 24/7 high availability | ⚠️ | ✅ | Foundry |

### Code Generation

| Requirement | MAF | Foundry | Recommendation |
|-------------|-----|---------|----------------|
| IDE integration | ✅ | ⚠️ | MAF |
| Code review automation | ✅ | ✅ | Either |
| Enterprise code policies | ⚠️ | ✅ | Foundry |
| Custom language support | ✅ | ⚠️ | MAF |
| Multi-developer teams | ✅ | ✅ | Either |

### Document Processing

| Requirement | MAF | Foundry | Recommendation |
|-------------|-----|---------|----------------|
| Invoice processing | ✅ | ✅ | Foundry for scale |
| Custom document types | ✅ | ⚠️ | MAF |
| Compliance requirements | ⚠️ | ✅ | Foundry |
| On-premises processing | ✅ | ❌ | MAF |
| Azure AI Search integration | ✅ | ✅ | Foundry |

### Research & Analysis

| Requirement | MAF | Foundry | Recommendation |
|-------------|-----|---------|----------------|
| Web scraping | ✅ | ⚠️ | MAF |
| Multi-source synthesis | ✅ | ✅ | Either |
| Academic institutions | ✅ | ⚠️ | MAF (cost) |
| Enterprise research | ⚠️ | ✅ | Foundry |
| Custom data sources | ✅ | ⚠️ | MAF |

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

### Foundry Architecture

```
┌─────────────────────────────────────────────┐
│         User Applications / APIs            │
├─────────────────────────────────────────────┤
│       Foundry Agent Service (Managed)       │
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

### MAF Cost Model

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

### Foundry Cost Model

**Costs:**
- Foundry Agent Service fees
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
- Agent Service: $200-500
- Model APIs: $100-500
- Cosmos DB: $100-300
- Observability: $50-100
- **Total: $450-1400/month**

**Note:** Enterprise features and reduced operational overhead often justify higher costs for production deployments.

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

### For Foundry Deployment

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

### Foundry Agent Service
- Additional Azure service integrations
- Advanced agent coordination patterns
- Enhanced observability features
- More deployment options
- Expanded regional availability

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

**Microsoft Foundry Agent Service:**
- Overview: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry
- Environment Setup: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/environment-setup?view=foundry
- Quickstart: https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code?view=foundry
- Python SDK Samples: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects

**Community Resources:**
- Discord: https://discord.gg/b5zjErwbQM (Azure AI Foundry)
- Weekly Office Hours: https://github.com/microsoft/agent-framework/blob/main/COMMUNITY.md

### Related Technologies
- Semantic Kernel: https://github.com/microsoft/semantic-kernel
- AutoGen: https://github.com/microsoft/autogen
- Model Context Protocol: https://modelcontextprotocol.io/

---

## Conclusion

Both Microsoft Agent Framework and Foundry Agent Service are powerful solutions for building AI agents, each optimized for different stages of the development lifecycle and organizational needs:

- **MAF** excels in flexibility, control, and development-phase work
- **Foundry** excels in production readiness, enterprise features, and managed operations

The choice between them depends on your specific requirements for control, compliance, scale, and operational overhead. Many organizations find value in using both: MAF for development and Foundry for production deployment.

---

**Document Version:** 1.0  
**Last Updated:** December 9, 2025  
**Author:** Research compiled from official Microsoft documentation  
**Next Review:** Q1 2026

# Microsoft Entra Agent ID Documentation

> **Status**: PREVIEW (as of January 2026)  
> **Last Updated**: January 19, 2026

## Overview

This directory contains comprehensive documentation and implementation guides for **Microsoft Entra Agent ID**, the identity and security platform designed specifically for AI agents in enterprise environments.

Microsoft Entra Agent ID extends Microsoft Entra ID's capabilities to provide specialized identity constructs, authentication patterns, and governance frameworks for autonomous and assistive AI agents.

> **Note**: Microsoft Entra Agent ID is part of **Microsoft Agent 365**, available now in **Frontier**, the Microsoft early access program for the latest AI innovations.

## 📚 Documentation Structure

### Core Documentation
- **[01-OVERVIEW.md](01-OVERVIEW.md)** - Introduction to Microsoft Entra Agent ID platform
- **[02-CORE-CONCEPTS.md](02-CORE-CONCEPTS.md)** - Agent identities, blueprints, and registry
- **[03-AUTHENTICATION.md](03-AUTHENTICATION.md)** - OAuth 2.0, OIDC, and token flows
- **[04-AGENT-REGISTRY.md](04-AGENT-REGISTRY.md)** - Agent discovery and metadata management
- **[05-SECURITY-GOVERNANCE.md](05-SECURITY-GOVERNANCE.md)** - Conditional access, identity protection, governance
- **[06-IMPLEMENTATION-GUIDE.md](06-IMPLEMENTATION-GUIDE.md)** - Practical implementation steps
- **[07-MCP-INTEGRATION.md](07-MCP-INTEGRATION.md)** - Model Context Protocol with agent identities
- **[08-A2A-PROTOCOL.md](08-A2A-PROTOCOL.md)** - Agent-to-Agent communication patterns
- **[09-BEST-PRACTICES.md](09-BEST-PRACTICES.md)** - Security, scalability, and operational best practices
- **[10-USE-CASES.md](10-USE-CASES.md)** - Real-world scenarios and patterns

### Quick References
- **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** - Quick start guide and essential commands
- **[UPDATES_JAN_2026.md](UPDATES_JAN_2026.md)** - Latest updates and new features (January 2026)

## 🎯 Quick Start

### For Developers

1. **Understand the Basics**: Start with [01-OVERVIEW.md](01-OVERVIEW.md) and [02-CORE-CONCEPTS.md](02-CORE-CONCEPTS.md)
2. **Authentication Patterns**: Review [03-AUTHENTICATION.md](03-AUTHENTICATION.md)
3. **Implementation**: Follow [06-IMPLEMENTATION-GUIDE.md](06-IMPLEMENTATION-GUIDE.md)
4. **MCP/A2A Integration**: See [07-MCP-INTEGRATION.md](07-MCP-INTEGRATION.md) and [08-A2A-PROTOCOL.md](08-A2A-PROTOCOL.md)

### For Identity Professionals

1. **Platform Overview**: [01-OVERVIEW.md](01-OVERVIEW.md)
2. **Security & Governance**: [05-SECURITY-GOVERNANCE.md](05-SECURITY-GOVERNANCE.md)
3. **Best Practices**: [09-BEST-PRACTICES.md](09-BEST-PRACTICES.md)

## 🔑 Key Capabilities

| Capability | Description |
|------------|-------------|
| **Agent Identities** | Specialized identity accounts for AI agents with unique authentication patterns |
| **Agent Registry** | Centralized metadata repository for all organizational agents |
| **Conditional Access** | Adaptive policies based on agent risk and context |
| **Identity Protection** | Anomaly detection and automated threat response for agents |
| **Identity Governance** | Lifecycle management, entitlements, and access packages |
| **Network Controls** | Web filtering, threat intelligence, prompt injection detection |
| **MCP Support** | Native integration with Model Context Protocol |
| **A2A Protocol** | Standard agent-to-agent discovery and communication |

## 🏗️ Architecture Components

![Microsoft Entra Agent ID Architecture](./media/microsoft-entra-agent-identity-capabilities.png)

**Three Foundational Pillars**:
1. **Register and manage AI agents** - Agent identity platform and SDK
2. **Govern agent identities and lifecycle** - A2A protocol and authentication
3. **Protect agent access to resources** - Identity governance, conditional access, and network controls

```
┌─────────────────────────────────────────────────────────────┐
│                  Microsoft Entra Agent ID                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Agent      │  │    Agent     │  │    Agent     │      │
│  │  Identity    │  │   Registry   │  │    SDKs      │      │
│  │  Platform    │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   Authentication (OAuth/OIDC) + A2A + MCP Protocols  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Microsoft Entra Security Services               │
├─────────────────────────────────────────────────────────────┤
│  Conditional Access | Identity Protection | ID Governance    │
│  Network Controls | Threat Intelligence | Compliance         │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 Integration Points

### Supported Platforms
- **Azure AI Foundry** (automatic agent identity provisioning)
- **Microsoft Copilot Studio**
- **Custom Agent Frameworks** (via SDK)
- **Third-party Agent Platforms**

### Supported Protocols
- **OAuth 2.0** - Authorization framework
- **OpenID Connect (OIDC)** - Authentication layer
- **Model Context Protocol (MCP)** - Tool and resource access
- **Agent-to-Agent (A2A)** - Inter-agent communication

## 📦 Code Examples

Examples and sample implementations are located in:
- **[examples/](examples/)** - Complete working examples
  - `basic-agent-auth/` - Basic authentication patterns
  - `mcp-integration/` - MCP with agent identities
  - `a2a-communication/` - Agent-to-agent patterns
  - `azure-foundry/` - Azure AI Foundry integration
  - `dbms-assistant/` - Database agent with identity

- **[scripts/](scripts/)** - Utility scripts for agent identity management
  - `auto_mapper.py` - **Automatic agent-to-identity mapping** ⭐
  - `agent_identity_mapping_complete.json` - Verified mapping for 9 agents
  - See [scripts/README.md](scripts/README.md) for full documentation

## 🔧 Agent Identity Mapping Tool

The `auto_mapper.py` script automatically maps Azure AI Foundry agents to their Entra ID identities:

```bash
cd MICROSOFT-ENTRA-AGENT-ID/scripts
python auto_mapper.py
```

**Key Discovery**: When you publish an agent in Azure AI Foundry, it creates **2 service principals** in Entra ID. The script extracts every 2nd identity (the actual agent identity) and correlates them with your published agents.

### Current Verified Mapping (December 4, 2025)

| Agent | Object ID |
|-------|-----------|
| WebSearchAgent | `38c14420-a914-4370-a0f8-1b014598c1d0` |
| BasicWeatherAgent | `966ccc07-512a-4698-bafb-4d5686973d27` |
| ResearchAgent | `9350dda6-b732-4b1c-a111-c5d8c4ffc64a` |
| DataAnalysisAgent | `a3be091d-da7b-4696-b0f6-b7f41f5cca84` |
| CodeInterpreterAgent | `d73547cc-9f5f-4de5-8f3b-97e14f882016` |
| FileSearchAgent | `0e1584e6-f309-4e4b-9909-3200e3bca7a5` |
| BasicAgent | `bde46d80-de73-4bd9-9416-4515799ae72d` |
| WeatherAgent | `ff55957a-bbf1-4be8-9e41-0046b2b2494c` |
| BingGroundingAgent | `420c8552-5d64-4c44-869c-037ad07ef351` |

## � Technical Discovery: Identity Creation Pattern

When you **publish** an agent in Azure AI Foundry, the platform creates **2 service principals** in Entra ID:

1. **Infrastructure identity** (odd index when sorted by creation time) - Used internally by the platform
2. **Agent identity** (even index) - The actual identity for your agent ⭐

This is why `auto_mapper.py` extracts every 2nd identity when correlating agents to their Entra ID Object IDs.

### Identity Naming Convention

All Foundry agent identities follow this pattern:
```
{foundry-resource-name}/agents/{agent-name}
```
Example: `aq-ai-foundry-Sweden-Central/agents/WebSearchAgent`

### Practical RBAC Workflow

1. **Publish agents** in Azure AI Foundry (note the order you publish them)
2. **Run auto_mapper.py** to extract identities
3. **Apply RBAC** using generated commands
4. **Use Object IDs** for fine-grained access control

```bash
# Example: Grant agent access to Cosmos DB
az role assignment create \
    --role "Cosmos DB Built-in Data Contributor" \
    --assignee-object-id 38c14420-a914-4370-a0f8-1b014598c1d0 \
    --assignee-principal-type ServicePrincipal \
    --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.DocumentDB/databaseAccounts/{account}
```

## �🔒 Security Considerations

Microsoft Entra Agent ID implements **Zero Trust** principles:
- ✅ Identity verification required before any access
- ✅ Least privilege access enforcement
- ✅ Risk-based conditional access
- ✅ Continuous monitoring and threat detection
- ✅ Automated remediation for compromised agents
- ✅ Audit logging for compliance

## 🎓 Learning Path

```
Week 1: Fundamentals
├── Understand agent identity concepts (01-OVERVIEW.md)
├── Learn authentication patterns (03-AUTHENTICATION.md)
└── Explore the agent registry (04-AGENT-REGISTRY.md)

Week 2: Implementation
├── Review core concepts (02-CORE-CONCEPTS.md)
├── Configure RBAC permissions (scripts/auto_mapper.py)
└── Study real-world examples (examples/)

Week 3: Advanced Topics
├── Multi-agent orchestration with A2A
├── MCP server integration
└── Security and governance patterns

Week 4: Production
├── Security hardening best practices
├── Monitoring and observability setup
└── Operational procedures
```

## 📖 Official Resources

- [Microsoft Entra Agent ID](https://aka.ms/EntraAgentID)
- [Developer Platform Docs](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-id-platform)
- [Identity Professional Docs](https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents)
- [Agent Registry Docs](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-registry)

## 🚀 Relevance to This Repository

### Current Projects

| Project | Agent Identity Application |
|---------|----------------------------|
| **DBMS-ASSISTANT** | SQL Server authentication, MCP tool access with agent identities |
| **MCP Integration** | Secure MCP servers using agent identity tokens |
| **Agent Framework** | Multi-agent orchestration with A2A protocol |
| **Azure Cosmos DB** | Agent RBAC authentication to Cosmos DB resources |
| **LLMOps** | Identity governance for deployed agents |
| **Observability** | Audit logging and monitoring of agent activities |

### Next Steps for Integration

1. **Enable agent identities** for existing agent implementations
2. **Register agents** in the Agent Registry for organization-wide visibility
3. **Implement MCP authentication** using agent identity tokens
4. **Configure RBAC** permissions for agent access to Azure resources
5. **Set up conditional access** policies for risk-based agent control
6. **Establish governance** workflows for agent lifecycle management

## ⚠️ Important Notes

- **Preview Status**: Features may change; review release notes regularly
- **Compliance**: Ensure agent identities comply with organizational policies
- **RBAC**: Always use least privilege when assigning permissions
- **Monitoring**: Enable comprehensive logging for all agent activities
- **Testing**: Test thoroughly in non-production environments first

## 🤝 Contributing

When adding new documentation or examples:
1. Follow the existing structure and numbering
2. Include practical code examples
3. Reference official Microsoft documentation
4. Update this README with new content
5. Add examples to the `examples/` directory

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2 | January 19, 2026 | Updated with Microsoft Agent 365/Frontier program, enhanced security features, network controls, architectural clarity. See [UPDATES_JAN_2026.md](UPDATES_JAN_2026.md) |
| 1.1 | December 4, 2025 | Added auto_mapper.py tool, identity creation pattern discovery, verified mapping for 9 agents |
| 1.0 | December 4, 2025 | Initial documentation structure |

---

**Questions?** Review the detailed documentation files or consult the official Microsoft Entra Agent ID resources.

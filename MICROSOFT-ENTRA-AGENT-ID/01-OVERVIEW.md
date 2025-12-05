# Microsoft Entra Agent ID - Overview

> **Status**: PREVIEW  
> **Last Updated**: December 4, 2025

## What is Microsoft Entra Agent ID?

Microsoft Entra Agent ID is a comprehensive **identity and security platform** specifically designed for AI agents operating in enterprise environments. It extends the proven capabilities of Microsoft Entra ID (formerly Azure Active Directory) to address the unique authentication, authorization, and governance challenges posed by autonomous and assistive AI agents.

### Why Agent-Specific Identity?

Traditional identity models designed for humans and applications are insufficient for AI agents because:

1. **Autonomous Decision-Making**: Agents make decisions without direct human oversight
2. **Dynamic Behavior**: Agents learn and adapt, potentially exhibiting unpredictable behaviors
3. **Sensitive Data Access**: Agents often require access to confidential organizational data
4. **Scale Operations**: Agents can execute tasks rapidly across multiple systems
5. **Compliance Requirements**: Organizations need audit trails and governance for agent actions

## Platform Architecture

Microsoft Entra Agent ID is built on three foundational pillars:

```
┌─────────────────────────────────────────────────────────────────┐
│                 Microsoft Entra Agent ID Platform                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────┐ │
│  │  Agent Identity    │  │   Agent Registry   │  │   Security │ │
│  │    Platform        │  │                    │  │  & Govern. │ │
│  │                    │  │                    │  │            │ │
│  │ • Agent Identities │  │ • Metadata Store   │  │ • Cond.    │ │
│  │ • Blueprints       │  │ • Collections      │  │   Access   │ │
│  │ • Agent Users      │  │ • Discovery APIs   │  │ • Identity │ │
│  │ • Auth Service     │  │ • A2A Protocol     │  │   Protect. │ │
│  │ • SDKs             │  │ • Policy Enforce.  │  │ • ID Gov.  │ │
│  └────────────────────┘  └────────────────────┘  └────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Agent Identity Platform (For Developers)

The identity platform provides the core authentication and authorization infrastructure:

- **Agent Identities**: Specialized identity accounts for AI agents
- **Agent Identity Blueprints**: Reusable identity templates (1:N mapping)
- **Agent Users**: Identity construct for agents acting on behalf of users
- **Authentication Service**: OAuth 2.0 and OpenID Connect (OIDC) compliant
- **SDKs**: Developer tools for identity integration
  - Microsoft Identity Web (.NET)
  - Microsoft Entra SDK for Agent ID

### 2. Agent Registry (For Discovery & Metadata)

A centralized repository for agent metadata and discovery:

- **Comprehensive Inventory**: Maintains records of all deployed agents
- **Agent Card Manifests**: Rich metadata using open standards
- **Collections**: Secure categorization and discovery boundaries
- **Discovery Service**: Multi-dimensional search and filtering
- **Integration Layer**: Connects Microsoft and non-Microsoft ecosystems

### 3. Security & Governance (For Identity Professionals)

Enterprise-grade security and compliance features:

- **Conditional Access**: Adaptive, risk-based access policies
- **Identity Protection**: Anomaly detection and threat response
- **Identity Governance**: Lifecycle management and entitlements
- **Network Controls**: Web filtering, threat intelligence, prompt injection detection
- **Audit & Compliance**: Comprehensive logging and monitoring

## Core Capabilities

### For Developers

| Capability | Description | Benefit |
|------------|-------------|---------|
| **Secure Authentication** | OAuth 2.0/OIDC standard protocols | Industry-standard security |
| **Token Management** | Multiple token flow patterns | Flexible access scenarios |
| **Agent Discovery** | Standard protocols (MCP, A2A) | Interoperability |
| **SDK Support** | .NET, Python integration | Easy implementation |
| **Auto-provisioning** | Automatic identity assignment (Foundry) | Reduced setup time |

### For Identity Professionals

| Capability | Description | Benefit |
|------------|-------------|---------|
| **Centralized Visibility** | Organization-wide agent inventory | Complete oversight |
| **Policy Enforcement** | Conditional access at scale | Consistent security |
| **Risk Detection** | Real-time threat identification | Proactive protection |
| **Lifecycle Management** | Automated governance workflows | Reduced manual effort |
| **Compliance Logging** | Comprehensive audit trails | Regulatory compliance |

## Key Concepts

### Agent Identity

An identity account within Microsoft Entra ID that provides unique identification and authentication for AI agents. Similar to user or application identities but purpose-built for agent-specific scenarios.

**Key Features**:
- Unique identifier (GUID)
- Authentication credentials (certificates, secrets)
- RBAC role assignments
- 1:1 mapping with agent instances

### Agent Identity Blueprint

A reusable identity template that can map to multiple agent instances (1:N relationship). Enables centralized management while providing flexibility for diverse deployment scenarios.

**Use Cases**:
- Deploy multiple instances of the same agent type
- Centralized policy management
- Consistent security posture across instances

### Agent User

An identity construct that represents an agent acting on behalf of a specific user. Enables delegated access scenarios where user context must be preserved.

**Use Cases**:
- Personal assistants accessing user-specific data
- Agents performing actions with user authorization
- OAuth Identity Passthrough scenarios

### Agent Registry

A metadata repository that provides visibility, discovery, and governance across all agents in an organization.

**Components**:
- Agent card manifests (metadata)
- Collections (categorization)
- Discovery service (search/filter)
- Policy enforcement

## Authentication Patterns

Microsoft Entra Agent ID supports multiple authentication scenarios:

### 1. Autonomous Agent
```
Agent operates in its own application context
└── Uses: Agent Identity
    └── Pattern: Application-only OAuth flow
```

### 2. Interactive Agent (User Context)
```
Agent acts on behalf of a specific user
└── Uses: Agent Identity + Agent User
    └── Pattern: Delegated OAuth flow
```

### 3. Shared Authentication
```
All users share the same agent identity
└── Uses: Agent Identity or Managed Identity
    └── Pattern: Service-to-service authentication
```

### 4. Individual Authentication
```
Each user authenticates with their own credentials
└── Uses: OAuth Identity Passthrough
    └── Pattern: User-delegated access
```

## Integration with Microsoft Ecosystem

### Automatic Integration
- **Azure AI Foundry**: Automatic agent identity provisioning
- **Microsoft Copilot Studio**: Built-in identity management
- **Microsoft 365 Agents**: Native integration

### SDK Integration
- **Custom Agents**: Integrate via Microsoft Identity SDKs
- **Third-party Platforms**: Use standard OAuth/OIDC flows

### Security Services Integration
- **Conditional Access**: Leverage existing policies
- **Identity Protection**: Extend risk detection to agents
- **Identity Governance**: Apply lifecycle management
- **Global Secure Access**: Network-level controls

## Standard Protocol Support

### OAuth 2.0
- **Client Credentials Flow**: Agent-to-service authentication
- **Authorization Code Flow**: User-delegated access
- **On-Behalf-Of Flow**: Service-to-service delegation

### OpenID Connect (OIDC)
- Identity verification
- Trust relationship establishment
- Token-based authentication

### Model Context Protocol (MCP)
- Tool and resource access
- Agent identity token authentication
- Secure MCP server connections

### Agent-to-Agent (A2A)
- Inter-agent discovery
- Agent-to-agent communication
- Authorization between agents

## Zero Trust Principles

Microsoft Entra Agent ID implements Zero Trust security:

1. **Verify Explicitly**: Always authenticate and authorize
2. **Least Privilege Access**: Minimal permissions required
3. **Assume Breach**: Continuous monitoring and validation

### Security Implementation

```
┌─────────────────────────────────────────────────────┐
│            Every Agent Access Request               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  1. Identity Verification (Authentication)          │
│     └── OAuth/OIDC token validation                 │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  2. Risk Assessment (Identity Protection)           │
│     └── Anomaly detection, threat intelligence      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  3. Policy Evaluation (Conditional Access)          │
│     └── Risk-based, context-aware decisions         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  4. Authorization Check (RBAC)                      │
│     └── Verify permissions for requested resource   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  5. Network Controls (Secure Access)                │
│     └── Web filtering, threat prevention            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  6. Audit Logging (Compliance)                      │
│     └── Record all agent activities                 │
└─────────────────────────────────────────────────────┘
```

## Use Cases

### Enterprise Scenarios

1. **IT Automation Agents**
   - Manage infrastructure with agent identities
   - Enforce least privilege access
   - Audit all administrative actions

2. **Data Analysis Agents**
   - Secure access to sensitive data sources
   - User context preservation for personal data
   - Compliance with data governance policies

3. **Customer Service Agents**
   - Multi-tenant isolation via collections
   - Individual user authentication
   - Access control per customer context

4. **Development & DevOps Agents**
   - Code repository access with agent identities
   - CI/CD pipeline integration
   - Secure credential management

5. **Research Agents**
   - Access to proprietary knowledge bases
   - Collaboration via A2A protocol
   - Intellectual property protection

## Benefits Summary

### Security
- ✅ Purpose-built for autonomous AI systems
- ✅ Industry-standard authentication protocols
- ✅ Real-time threat detection and response
- ✅ Network-level security controls

### Governance
- ✅ Centralized visibility across all agents
- ✅ Lifecycle management automation
- ✅ Policy enforcement at scale
- ✅ Comprehensive audit trails

### Developer Experience
- ✅ Easy SDK integration
- ✅ Automatic provisioning (Foundry)
- ✅ Standard protocols (OAuth/OIDC)
- ✅ Flexible authentication patterns

### Operations
- ✅ Reduced manual administration
- ✅ Scalable identity management
- ✅ Integration with existing Entra services
- ✅ Multi-platform support

## Preview Status & Considerations

⚠️ **Important**: Microsoft Entra Agent ID is currently in PREVIEW

### What This Means
- Features may change before general availability
- Breaking changes possible in preview period
- Microsoft makes no warranties (express or implied)
- Not recommended for production-critical scenarios yet

### Best Practices During Preview
1. Test thoroughly in non-production environments
2. Monitor Microsoft documentation for updates
3. Provide feedback to the product team
4. Plan for potential migration when GA is released
5. Maintain fallback authentication mechanisms

## Getting Started

### Next Steps

1. **Learn Core Concepts**: Read [02-CORE-CONCEPTS.md](02-CORE-CONCEPTS.md)
2. **Understand Authentication**: Review [03-AUTHENTICATION.md](03-AUTHENTICATION.md)
3. **Explore the Registry**: See [04-AGENT-REGISTRY.md](04-AGENT-REGISTRY.md)
4. **Implement Security**: Study [05-SECURITY-GOVERNANCE.md](05-SECURITY-GOVERNANCE.md)
5. **Build Your Agent**: Follow [06-IMPLEMENTATION-GUIDE.md](06-IMPLEMENTATION-GUIDE.md)

### Resources

- [Official Microsoft Entra Agent ID](https://aka.ms/EntraAgentID)
- [Developer Platform Documentation](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-id-platform)
- [Identity Professional Documentation](https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents)

---

**Next**: [Core Concepts →](02-CORE-CONCEPTS.md)

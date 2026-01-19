# Microsoft Entra Agent ID - Quick Reference

> **Last Updated**: January 19, 2026  
> **Status**: PREVIEW

## What Is It?

Microsoft Entra Agent ID is an **identity and security platform specifically designed for AI agents**. It extends Microsoft Entra ID to provide agent-specific authentication, authorization, discovery, and governance capabilities.

## Core Components

| Component | Purpose | For |
|-----------|---------|-----|
| **Agent Identity Platform** | Authentication & authorization | Developers |
| **Agent Registry** | Discovery & metadata management | Developers & Admins |
| **Security & Governance** | Policies, risk detection, compliance | Identity Professionals |

## Quick Start

### For Developers

**1. Create an Agent with Identity (Azure AI Foundry)**

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential()
)

# Agent automatically gets identity + registry entry
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="My Agent",
    instructions="Agent instructions here"
)
```

**2. Authenticate as an Autonomous Agent**

```python
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="agent-app-id",
    client_secret="agent-secret"
)

# Use credential to access Azure resources
```

**3. Discover Other Agents**

```python
import requests

# Search for agents with specific capabilities
response = requests.post(
    "https://agent-registry.azure.com/discovery/v1/search",
    headers={"Authorization": f"Bearer {token}"},
    json={"capability": "data_analysis"}
)

agents = response.json()["agents"]
```

### For Identity Professionals

**1. View All Agents**

Navigate to **Microsoft Entra admin center** → **Agent ID** → **Agent Registry**

**2. Create a Collection**

```json
{
  "name": "Production Agents",
  "membership_criteria": {
    "environment": "production"
  },
  "discovery_policy": "restricted"
}
```

**3. Apply Conditional Access Policy**

Create policy targeting agent identities:
- Target: Agent identity collection
- Condition: Risk level
- Control: Block/Allow based on risk

## Key Concepts

### Agent Identity
A specialized identity account for AI agents (like user identity but for agents)

### Agent Identity Blueprint  
Reusable template → Deploy multiple agent instances

### Agent User
Agent acting on behalf of a specific user (preserves user context)

### Agent Registry
Central repository of all agents + metadata + capabilities

### Collections
Logical groups for policy enforcement and discovery control

## Authentication Patterns

| Pattern | Use Case | OAuth Flow |
|---------|----------|------------|
| **Autonomous** | Agent operates independently | Client Credentials |
| **Interactive** | Agent acts on behalf of user | Authorization Code |
| **Multi-Agent** | Agent chains with user context | On-Behalf-Of (OBO) |
| **Azure-Hosted** | Agent in Azure service | Managed Identity |

## Common Scenarios

### Scenario 1: Background Data Processing

```python
# Autonomous agent with application permissions
credential = ClientSecretCredential(tenant_id, client_id, secret)
storage_client = BlobServiceClient(account_url, credential=credential)
# Process data autonomously
```

### Scenario 2: Personal Assistant

```python
# Interactive agent with delegated permissions
app = PublicClientApplication(client_id, authority=authority)
result = app.acquire_token_interactive(scopes=["User.Read"])
# Access user's data on their behalf
```

### Scenario 3: Agent-to-Agent Communication

```python
# Discover agent → Get authorization → Call agent
agents = discover_by_capability("sentiment_analysis")
token = get_agent_authorization(target_agent_id)
result = requests.post(agent_endpoint, headers={"Authorization": token})
```

## Security Features

### Conditional Access
- Risk-based policies for agents
- Context-aware access control
- Adaptive authentication

### Identity Protection
- Anomaly detection
- Threat intelligence
- Automated remediation

### Identity Governance
- Lifecycle management
- Access reviews
- Entitlement management

### Network Controls
- Web filtering
- Prompt injection detection
- Threat prevention

## MCP Integration

**Model Context Protocol** with agent identity authentication:

```python
from azure.ai.agents.models import McpTool

mcp_tool = McpTool(
    server_url="https://mcp-server.contoso.com",
    server_label="knowledge_base"
)

# Agent identity used automatically for authentication
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="Agent",
    tools=[mcp_tool]
)
```

## A2A Protocol

**Agent-to-Agent** standard communication:

1. **Discover**: Find agents via registry
2. **Authorize**: Get token for target agent
3. **Communicate**: Call agent using A2A protocol
4. **Audit**: All interactions logged

## RBAC for Agents

Common role assignments:

```bash
# Assign Storage Blob Data Reader to agent
az role assignment create \
  --assignee <agent-identity-id> \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>
```

## Best Practices

### ✅ Do

- Use agent identities for all production agents
- Register agents in the Agent Registry
- Apply least privilege RBAC
- Implement conditional access policies
- Use managed identities when possible
- Monitor agent activity continuously
- Rotate credentials regularly
- Document agent capabilities

### ❌ Don't

- Grant high-privilege roles to agents
- Skip agent registration
- Hardcode credentials
- Bypass discovery service
- Ignore risk signals
- Deploy agents without governance
- Reuse credentials across agents
- Leave agents unmonitored

## Limitations (Preview)

⚠️ Agent identities are **blocked** from:
- High-privilege roles (Global Admin, etc.)
- User/identity management operations
- Security setting modifications
- Sensitive permission consents

## Architecture at a Glance

```
┌─────────────────────────────────────────────┐
│         Your AI Agent Application           │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│      Microsoft Entra Agent ID Platform      │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Agent   │  │  Agent   │  │ Security │ │
│  │ Identity │  │ Registry │  │   &      │ │
│  │          │  │          │  │ Govern.  │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│        Azure Resources & APIs               │
│  Storage | Cosmos DB | APIs | MCP Servers  │
└─────────────────────────────────────────────┘
```

## Token Lifecycle

```
1. Agent requests token → 2. Entra ID validates
3. Token issued (1 hour) → 4. Agent calls API
5. Token expires → 6. Refresh or re-authenticate
```

## Documentation Structure

| Document | Content | Audience |
|----------|---------|----------|
| [01-OVERVIEW](01-OVERVIEW.md) | Platform introduction | All |
| [02-CORE-CONCEPTS](02-CORE-CONCEPTS.md) | Identity constructs | All |
| [03-AUTHENTICATION](03-AUTHENTICATION.md) | Auth patterns & flows | Developers |
| [04-AGENT-REGISTRY](04-AGENT-REGISTRY.md) | Discovery & metadata | Developers |
| [05-SECURITY-GOVERNANCE](05-SECURITY-GOVERNANCE.md) | Policies & compliance | IT/Security |
| [06-IMPLEMENTATION-GUIDE](06-IMPLEMENTATION-GUIDE.md) | Step-by-step setup | Developers |
| [07-MCP-INTEGRATION](07-MCP-INTEGRATION.md) | MCP with identities | Developers |
| [08-A2A-PROTOCOL](08-A2A-PROTOCOL.md) | Agent-to-agent comms | Developers |
| [09-BEST-PRACTICES](09-BEST-PRACTICES.md) | Recommendations | All |
| [10-USE-CASES](10-USE-CASES.md) | Real-world examples | All |

## Resources

- **Official Docs**: [Microsoft Entra Agent ID](https://aka.ms/EntraAgentID)
- **Developer Platform**: [Agent Identity Platform](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-id-platform)
- **Registry Guide**: [Agent Registry](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/what-is-agent-registry)

## Getting Help

1. **Read the docs**: Start with [01-OVERVIEW.md](01-OVERVIEW.md)
2. **Check examples**: See `examples/` directory
3. **Review use cases**: Read [10-USE-CASES.md](10-USE-CASES.md)
4. **Microsoft Learn**: Official documentation
5. **Preview feedback**: Report issues to Microsoft

## Roadmap to GA

Current: **PREVIEW**
- Features may change
- Breaking changes possible
- Not for production-critical scenarios

Expected: **General Availability (TBD)**
- Stable APIs
- Production-ready
- Full support

---

**Start Here**: [Overview →](01-OVERVIEW.md)

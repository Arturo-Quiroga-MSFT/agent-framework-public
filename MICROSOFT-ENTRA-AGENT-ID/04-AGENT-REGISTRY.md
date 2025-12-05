# Agent Registry - Discovery & Metadata

> **Last Updated**: December 4, 2025

## Overview

The **Agent Registry** is a centralized metadata repository that provides comprehensive visibility, discovery, and governance capabilities for all AI agents across an organization. It serves as the single source of truth for agent-related data, enabling secure discovery, policy enforcement, and compliance.

## Core Purpose

The Agent Registry solves critical enterprise challenges:

1. **Visibility Gap**: Organizations lack awareness of deployed agents
2. **Security Risk**: Ungoverned agents can access sensitive resources
3. **Discovery Challenge**: Agents cannot find other agents for collaboration
4. **Compliance Need**: Auditors require complete agent inventory
5. **Policy Enforcement**: Security controls must apply uniformly

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Agent Registry                           │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │   Metadata     │  │  Collections   │  │   Discovery    │  │
│  │     Store      │  │                │  │    Service     │  │
│  │                │  │                │  │                │  │
│  │ • Agent cards  │  │ • Baseline     │  │ • Search API   │  │
│  │ • Manifests    │  │ • Custom       │  │ • Filter API   │  │
│  │ • NoSQL DB     │  │ • Policies     │  │ • A2A protocol │  │
│  └────────────────┘  └────────────────┘  └────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Integration Layer                        │    │
│  │  • Microsoft Entra ID  • Copilot Studio              │    │
│  │  • Azure AI Foundry    • Third-party platforms       │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
└──────────────────────────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────┐
│              Microsoft Entra Core Directory                   │
│  • Identity enforcement  • Entitlement policies              │
└──────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Metadata Store

A NoSQL-based repository that stores rich agent metadata.

**Stored Information**:
- Agent card manifests
- Agent identity mappings
- Capability descriptions
- Endpoint information
- Protocol support
- Version history
- Ownership details

**Characteristics**:
- Real-time updates
- Scalable storage
- Flexible schema
- Query optimization
- Event triggers

### 2. Collections

Logical groupings of agents for security, discovery control, and governance.

**Types**:
- **Baseline Collections**: Automatically created (e.g., "All Agents", "Microsoft Platform Agents")
- **Custom Collections**: Organization-defined groups (e.g., "Customer-Facing", "Internal-Only", "Production")

**Purpose**:
- Control discoverability
- Apply policies at scale
- Organize agents by function/environment
- Enforce Zero Trust boundaries

### 3. Discovery Service

APIs and protocols for finding and connecting to agents.

**Capabilities**:
- Multi-dimensional search
- Collection-aware filtering
- Skill-based discovery
- Protocol negotiation
- Authorization checks

### 4. Integration Layer

Connectors to agent creation platforms and ecosystems.

**Supported Platforms**:
- Azure AI Foundry (automatic registration)
- Microsoft Copilot Studio (automatic registration)
- Custom agent frameworks (SDK-based registration)
- Third-party platforms (API-based registration)

## Agent Card Manifest

An agent card is a standardized metadata document that describes an agent's capabilities, endpoints, and characteristics.

### Manifest Structure

```json
{
  "schema_version": "1.0",
  "agent_card_id": "card-customer-service-v2",
  "created": "2025-12-01T10:00:00Z",
  "updated": "2025-12-03T14:30:00Z",
  
  "identity": {
    "agent_identity_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "agent_blueprint_id": "blueprint-customer-service",
    "display_name": "Customer Service Agent",
    "description": "Handles tier-1 customer support inquiries",
    "version": "2.1.0"
  },
  
  "capabilities": [
    {
      "name": "order_lookup",
      "description": "Retrieve customer order information",
      "input_schema": {
        "type": "object",
        "properties": {
          "order_id": {"type": "string"},
          "customer_email": {"type": "string"}
        }
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "order_details": {"type": "object"},
          "status": {"type": "string"}
        }
      }
    },
    {
      "name": "return_processing",
      "description": "Initiate product return workflow",
      "requires_approval": true
    },
    {
      "name": "faq_response",
      "description": "Answer frequently asked questions",
      "knowledge_base": "customer-support-kb-v3"
    }
  ],
  
  "protocols": {
    "mcp": {
      "version": "1.0",
      "endpoint": "https://api.contoso.com/agents/cs-agent/mcp",
      "authentication": "AgenticIdentityToken",
      "tools": ["order_lookup", "return_processing", "faq_response"]
    },
    "a2a": {
      "version": "1.0",
      "endpoint": "https://api.contoso.com/agents/cs-agent/a2a",
      "authentication": "OAuth2",
      "authorization_endpoint": "https://api.contoso.com/agents/cs-agent/authorize"
    },
    "rest_api": {
      "openapi_spec": "https://api.contoso.com/agents/cs-agent/openapi.json",
      "base_url": "https://api.contoso.com/agents/cs-agent/v2"
    }
  },
  
  "metadata": {
    "owner": "support-team@contoso.com",
    "cost_center": "CC-1234",
    "environment": "production",
    "region": "us-east",
    "tags": ["customer-facing", "tier-1", "support"],
    "compliance": {
      "data_classification": "confidential",
      "retention_policy": "7-years",
      "gdpr_compliant": true
    }
  },
  
  "performance": {
    "average_response_time_ms": 250,
    "availability_sla": "99.9%",
    "max_concurrent_requests": 1000
  },
  
  "dependencies": {
    "required_services": [
      "order-management-api",
      "customer-database"
    ],
    "optional_services": [
      "inventory-system",
      "shipping-tracker"
    ]
  }
}
```

### Manifest Schema Standards

The registry supports multiple manifest formats:
- **Microsoft Agent Card Schema** (recommended)
- **OpenAPI/Swagger** for REST APIs
- **AsyncAPI** for event-driven agents
- **Custom JSON Schema** with validation

## Collections

### Baseline Collections

Automatically created by the system:

| Collection | Description | Members |
|------------|-------------|---------|
| **All Agents** | Every registered agent | All agents in tenant |
| **Microsoft Platform Agents** | Agents from Microsoft services | Copilot Studio, Foundry agents |
| **External Agents** | Third-party registered agents | Non-Microsoft platform agents |
| **Active Agents** | Currently operational | Agents with active status |

### Custom Collections

Organization-defined groups for governance:

```json
{
  "collection_id": "customer-facing-agents",
  "name": "Customer-Facing Agents",
  "description": "Agents that directly interact with customers",
  "created_by": "security-team@contoso.com",
  "created_date": "2025-11-01T10:00:00Z",
  
  "membership_criteria": {
    "tags": ["customer-facing"],
    "environment": ["production", "staging"],
    "compliance.gdpr_compliant": true
  },
  
  "discovery_policy": {
    "visible_to": "authenticated-agents",
    "discoverable_by_collections": [
      "internal-agents",
      "support-agents"
    ],
    "require_authorization": true
  },
  
  "conditional_access_policy": "CAPolicy-CustomerFacing-001",
  
  "members": [
    "agent-id-001",
    "agent-id-002",
    "agent-id-003"
  ]
}
```

### Collection-Based Policies

Collections enable policy enforcement at scale:

**Discovery Control**:
```python
# Example: Restrict discovery based on collection membership
discovery_policy = {
    "collection": "internal-tools",
    "visible_to": ["employees-collection"],
    "hidden_from": ["external-partners-collection"]
}
```

**Conditional Access**:
```python
# Example: Require MFA for high-risk agent collections
conditional_access = {
    "collection": "admin-agents",
    "policy": "require-mfa",
    "risk_threshold": "low",
    "block_if": "high-risk"
}
```

**Network Controls**:
```python
# Example: Apply network restrictions per collection
network_policy = {
    "collection": "sensitive-data-agents",
    "allowed_networks": ["corporate-vnet"],
    "block_public_internet": True
}
```

## Discovery Service

### Discovery API

Agents use the discovery service to find other agents:

```python
from azure.identity import DefaultAzureCredential
import requests

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default")

# Search for agents with specific capabilities
discovery_request = {
    "capabilities": ["order_lookup"],
    "collections": ["customer-facing-agents"],
    "protocols": ["mcp"],
    "environment": "production"
}

response = requests.post(
    "https://agent-registry.azure.com/discovery/v1/search",
    headers={"Authorization": f"Bearer {token.token}"},
    json=discovery_request
)

agents = response.json()["agents"]
for agent in agents:
    print(f"Found: {agent['display_name']} at {agent['endpoints']['mcp']}")
```

### Discovery Patterns

#### 1. Capability-Based Discovery

Find agents that can perform specific tasks:

```python
def discover_by_capability(capability_name):
    query = {
        "capability": capability_name,
        "status": "active"
    }
    return registry_client.search_agents(query)

# Find all agents that can process payments
payment_agents = discover_by_capability("payment_processing")
```

#### 2. Protocol-Based Discovery

Find agents supporting specific protocols:

```python
def discover_by_protocol(protocol):
    query = {
        "protocols": [protocol],
        "collection": "verified-agents"
    }
    return registry_client.search_agents(query)

# Find all MCP-enabled agents
mcp_agents = discover_by_protocol("mcp")
```

#### 3. Collection-Based Discovery

Find agents within a specific collection:

```python
def discover_by_collection(collection_name):
    query = {
        "collection": collection_name,
        "discoverable": True
    }
    return registry_client.search_agents(query)

# Find all agents in the data-analysis collection
data_agents = discover_by_collection("data-analysis-agents")
```

### Authorization for Discovery

Discovery requests are subject to authorization checks:

```
┌─────────────┐
│ Agent A     │  Requests discovery
│ (Requester) │
└──────┬──────┘
       │ 1. Discovery Query
       ↓
┌──────────────────┐
│ Agent Registry   │  2. Verify Agent A identity
│ Discovery Service│  3. Check Agent A collections
└──────┬───────────┘  4. Apply discovery policies
       │ 5. Filter results
       ↓
┌──────────────────┐
│ Authorized       │  Only agents Agent A can see
│ Results          │
└──────────────────┘
```

## Registration Process

### Automatic Registration (Azure AI Foundry)

Agents created in Foundry are automatically registered:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Create agent in Foundry
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential()
)

agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="Data Analysis Agent",
    instructions="Analyze sales data and generate reports"
)

# Agent is automatically:
# 1. Assigned an agent identity
# 2. Registered in the Agent Registry
# 3. Added to "Microsoft Platform Agents" collection
# 4. Given an agent card with default metadata

print(f"Agent registered: {agent.id}")
print(f"Agent identity: {agent.agent_identity_id}")
```

### Manual Registration (Custom Agents)

Custom agents can register via API:

```python
import requests
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default")

# Create agent card manifest
agent_card = {
    "identity": {
        "agent_identity_id": "your-agent-identity-id",
        "display_name": "Custom Data Agent",
        "description": "Processes customer data for insights",
        "version": "1.0.0"
    },
    "capabilities": [
        {
            "name": "data_analysis",
            "description": "Analyze customer behavior data"
        }
    ],
    "protocols": {
        "rest_api": {
            "base_url": "https://api.yourcompany.com/agent"
        }
    },
    "metadata": {
        "owner": "data-team@yourcompany.com",
        "environment": "production"
    }
}

# Register with Agent Registry
response = requests.post(
    "https://agent-registry.azure.com/registry/v1/agents",
    headers={"Authorization": f"Bearer {token.token}"},
    json=agent_card
)

registry_id = response.json()["registry_id"]
print(f"Agent registered: {registry_id}")
```

### SDK-Based Registration

Using Microsoft Agent Framework:

```python
from agent_framework.registry import AgentRegistry
from agent_framework import Agent

# Create your agent
agent = Agent(
    name="Customer Service Bot",
    instructions="Handle customer inquiries",
    tools=[order_lookup_tool, faq_tool]
)

# Register with Agent Registry
registry = AgentRegistry(
    credential=DefaultAzureCredential()
)

registry_entry = registry.register_agent(
    agent=agent,
    collections=["customer-facing-agents", "production-agents"],
    capabilities=["order_lookup", "faq_response"],
    metadata={
        "owner": "support@contoso.com",
        "cost_center": "CC-5678"
    }
)

print(f"Agent registered with ID: {registry_entry.registry_id}")
```

## Agent-to-Agent (A2A) Protocol

The A2A protocol enables secure, standardized agent-to-agent communication.

### A2A Discovery Flow

```
┌─────────────┐                           ┌──────────────────┐
│  Agent A    │                           │ Agent Registry   │
└──────┬──────┘                           └────────┬─────────┘
       │                                           │
       │ 1. Discover agents with capability       │
       │    "data_processing"                     │
       │ ─────────────────────────────────────> │
       │                                           │
       │ 2. List of authorized agents             │
       │ <───────────────────────────────────── │
       │                                           │
       ↓                                           │
┌─────────────┐                                   │
│  Agent B    │  3. Establish connection          │
│  (Selected) │     using A2A protocol            │
└──────┬──────┘                                   │
       │                                           │
       │ 4. Request authorization                 │
       │ ─────────────────────────────────────> │
       │                                           │
       │ 5. Authorization token                   │
       │ <───────────────────────────────────── │
       │                                           │
       │ 6. Authenticated A2A call                │
       │ ──> Agent B executes task                │
```

### A2A Authentication

```python
from azure.identity import DefaultAzureCredential
import requests

# Agent A discovers Agent B
credential = DefaultAzureCredential()
registry_token = credential.get_token("https://agent-registry.azure.com/.default")

# Discover agents
discovery_response = requests.post(
    "https://agent-registry.azure.com/discovery/v1/search",
    headers={"Authorization": f"Bearer {registry_token.token}"},
    json={"capability": "sentiment_analysis"}
)

agent_b = discovery_response.json()["agents"][0]

# Get authorization to call Agent B
auth_response = requests.post(
    "https://agent-registry.azure.com/authorization/v1/token",
    headers={"Authorization": f"Bearer {registry_token.token}"},
    json={
        "target_agent_id": agent_b["agent_identity_id"],
        "requested_capabilities": ["sentiment_analysis"]
    }
)

agent_b_token = auth_response.json()["access_token"]

# Call Agent B using A2A protocol
result = requests.post(
    agent_b["endpoints"]["a2a"],
    headers={"Authorization": f"Bearer {agent_b_token}"},
    json={
        "action": "analyze_sentiment",
        "data": {"text": "Customer feedback text here"}
    }
)

print(result.json())
```

## Security & Policy Enforcement

### Discovery Policies

Control who can discover which agents:

```json
{
  "policy_name": "restricted-discovery",
  "applies_to_collection": "sensitive-agents",
  "rules": [
    {
      "allow_discovery_by": ["internal-agents"],
      "deny_discovery_by": ["external-agents"],
      "require_conditions": [
        "requesting_agent.risk_level == 'low'",
        "requesting_agent.environment == 'production'"
      ]
    }
  ]
}
```

### Runtime Enforcement

```
Every Discovery Request:
  1. Authenticate requesting agent
  2. Verify agent identity validity
  3. Check agent collection membership
  4. Apply discovery policies
  5. Filter results based on authorization
  6. Log discovery attempt
  7. Return authorized agents only
```

### Audit Logging

All registry operations are logged:

```json
{
  "event_type": "agent_discovery",
  "timestamp": "2025-12-04T10:30:00Z",
  "requester": {
    "agent_identity_id": "a1b2c3d4-...",
    "display_name": "Agent A"
  },
  "query": {
    "capability": "data_processing",
    "collection": "production-agents"
  },
  "results": {
    "count": 5,
    "agent_ids": ["agent-1", "agent-2", "..."]
  },
  "authorization": "granted",
  "policy_applied": "discovery-policy-001"
}
```

## Best Practices

### Registration

✅ **Do**:
- Register all agents (internal and external)
- Keep agent cards up-to-date
- Use descriptive names and descriptions
- Document all capabilities
- Specify protocol support
- Assign appropriate collections

❌ **Don't**:
- Deploy unregistered agents
- Use generic agent names
- Skip capability documentation
- Hardcode endpoint URLs
- Ignore metadata fields

### Discovery

✅ **Do**:
- Use capability-based discovery
- Respect discovery policies
- Cache discovery results appropriately
- Handle authorization errors gracefully
- Log discovery operations

❌ **Don't**:
- Bypass discovery service
- Hardcode agent endpoints
- Ignore collection boundaries
- Over-query the registry
- Skip error handling

### Collections

✅ **Do**:
- Create meaningful collections
- Apply consistent naming
- Document collection purpose
- Review membership regularly
- Use collections for policies

❌ **Don't**:
- Create overlapping collections
- Leave collections unmanaged
- Skip policy assignment
- Ignore collection hygiene

## Key Takeaways

1. **Central Registry**: Single source of truth for all agents
2. **Rich Metadata**: Agent cards provide comprehensive information
3. **Collections**: Enable policy enforcement at scale
4. **Secure Discovery**: Authorization required for agent discovery
5. **A2A Protocol**: Standardized agent-to-agent communication
6. **Integration**: Automatic registration from Microsoft platforms

---

**Previous**: [← Authentication](03-AUTHENTICATION.md) | **Next**: [Security & Governance →](05-SECURITY-GOVERNANCE.md)

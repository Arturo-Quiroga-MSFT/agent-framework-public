# Core Concepts - Agent Identity Architecture

> **Last Updated**: December 4, 2025

## Overview

This document explains the core identity constructs that form the foundation of Microsoft Entra Agent ID. Understanding these concepts is essential for implementing secure, scalable authentication patterns for AI agents.

## Identity Construct Hierarchy

```
┌────────────────────────────────────────────────────────┐
│          Agent Identity Blueprint (Template)           │
│  • Reusable identity configuration                     │
│  • Centralized policy management                       │
│  • One blueprint → Many instances (1:N)                │
└────────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
┌───────────────────┐         ┌───────────────────┐
│  Agent Identity   │         │  Agent Identity   │
│   (Instance 1)    │         │   (Instance 2)    │
│  • Unique ID      │         │  • Unique ID      │
│  • Credentials    │         │  • Credentials    │
│  • RBAC roles     │         │  • RBAC roles     │
└───────────────────┘         └───────────────────┘
        ↓                               ↓
┌───────────────────┐         ┌───────────────────┐
│   Agent User      │         │   Agent User      │
│   (Optional)      │         │   (Optional)      │
│  • User context   │         │  • User context   │
│  • Delegated auth │         │  • Delegated auth │
└───────────────────┘         └───────────────────┘
```

## 1. Agent Identity

### Definition

An **Agent Identity** is a specialized identity account within Microsoft Entra ID that provides unique identification and authentication capabilities for AI agents. It serves the same fundamental purpose as user or application identities but is purpose-built for autonomous AI systems.

### Key Characteristics

| Attribute | Description |
|-----------|-------------|
| **Unique Identifier** | GUID (Globally Unique Identifier) |
| **Identity Type** | Agent (distinct from User or Application) |
| **Authentication** | OAuth 2.0 / OpenID Connect |
| **Credentials** | Certificates, secrets, or federated credentials |
| **Scope** | Application-only or delegated access |
| **Lifecycle** | Created, active, suspended, deleted |

### Agent Identity Structure

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "type": "AgentIdentity",
  "displayName": "Customer Service Agent - Production",
  "createdDateTime": "2025-12-01T10:00:00Z",
  "status": "Active",
  "blueprintId": "blueprint-abc-123",
  "credentials": {
    "type": "Certificate",
    "thumbprint": "A1B2C3D4E5F6...",
    "expiryDate": "2026-12-01T10:00:00Z"
  },
  "rbacAssignments": [
    {
      "role": "Storage Blob Data Reader",
      "scope": "/subscriptions/.../resourceGroups/..."
    }
  ],
  "metadata": {
    "environment": "production",
    "version": "2.1.0"
  }
}
```

### Agent Identity vs. Other Identity Types

| Feature | Agent Identity | User Identity | Application Identity |
|---------|----------------|---------------|---------------------|
| **Purpose** | AI agents | Human users | Web apps/services |
| **Autonomy** | High autonomy | Human-directed | Programmatic |
| **Risk Profile** | Unpredictable behavior | Predictable | Deterministic |
| **Privileges** | Restricted set | Full range | Full range |
| **Governance** | Agent-specific policies | User policies | App policies |
| **Discovery** | Agent Registry | People directory | App registrations |

### Important Restrictions

Agent identities have **intentional limitations** to minimize risk:

❌ **Blocked Capabilities**:
- Cannot be granted high-privilege roles (e.g., Global Administrator)
- Cannot manage users or other identities
- Cannot modify security settings
- Cannot consent to sensitive permissions

✅ **Allowed Capabilities**:
- Read access to authorized resources
- Write access with appropriate RBAC
- Tool execution (e.g., function calling)
- API access with proper scoping

## 2. Agent Identity Blueprint

### Definition

An **Agent Identity Blueprint** is a reusable identity template that defines the configuration, policies, and capabilities shared across multiple agent instances. It enables the 1:N relationship pattern where one blueprint maps to many agent identities.

### Purpose

Blueprints provide:
1. **Consistency**: Standardized configuration across agent instances
2. **Scalability**: Deploy many agents from a single template
3. **Centralized Management**: Update all instances through blueprint changes
4. **Governance**: Apply policies at the blueprint level

### Blueprint Structure

```json
{
  "blueprintId": "blueprint-customer-service-agent",
  "name": "Customer Service Agent Blueprint",
  "version": "1.0",
  "description": "Template for customer service agents",
  "configuration": {
    "authenticationMethod": "Certificate",
    "tokenLifetime": "1 hour",
    "allowedScopes": [
      "https://graph.microsoft.com/.default",
      "https://storage.azure.com/.default"
    ]
  },
  "defaultRbacRoles": [
    {
      "role": "Reader",
      "scope": "subscription"
    }
  ],
  "policies": {
    "conditionalAccess": "CAPolicy-Agents-001",
    "riskThreshold": "medium",
    "requireMFA": false
  },
  "capabilities": [
    "DataRetrieval",
    "DocumentGeneration",
    "APIIntegration"
  ],
  "instances": [
    "agent-instance-001",
    "agent-instance-002",
    "agent-instance-003"
  ]
}
```

### Blueprint Lifecycle

```
┌─────────────┐
│   Create    │  Define blueprint with configuration
│  Blueprint  │  and policies
└──────┬──────┘
       ↓
┌─────────────┐
│   Deploy    │  Create agent instances from blueprint
│  Instances  │  Each gets unique identity
└──────┬──────┘
       ↓
┌─────────────┐
│   Manage    │  Update blueprint → affects all instances
│  Blueprint  │  Add/remove instances as needed
└──────┬──────┘
       ↓
┌─────────────┐
│  Deprecate  │  Mark blueprint as deprecated
│  Blueprint  │  Migrate instances to new blueprint
└─────────────┘
```

### Use Cases

#### Scenario 1: Multi-Environment Deployment
```
Blueprint: "Data Analysis Agent"
├── Instance: data-agent-dev (Development)
├── Instance: data-agent-staging (Staging)
└── Instance: data-agent-prod (Production)
```

#### Scenario 2: Geographic Distribution
```
Blueprint: "Customer Support Agent"
├── Instance: support-agent-us-east
├── Instance: support-agent-eu-west
└── Instance: support-agent-asia-pacific
```

#### Scenario 3: Team-Based Deployment
```
Blueprint: "Research Assistant"
├── Instance: research-agent-team-alpha
├── Instance: research-agent-team-beta
└── Instance: research-agent-team-gamma
```

## 3. Agent User

### Definition

An **Agent User** is an identity construct that represents an agent acting on behalf of a specific user. It enables delegated access scenarios where the user's context, permissions, and data access rights must be preserved during agent operations.

### When to Use Agent Users

Use agent users when:
- ✅ Agent needs to access user-specific data
- ✅ User context must be preserved (e.g., OneDrive files)
- ✅ Auditing requires user-level attribution
- ✅ Permissions are user-scoped (not app-scoped)

Don't use agent users when:
- ❌ All users share the same data access
- ❌ Agent operates autonomously without user context
- ❌ Application-level permissions are sufficient

### Authentication Flow with Agent User

```
┌──────────┐
│   User   │  Authenticates and authorizes agent
└────┬─────┘
     │ OAuth consent
     ↓
┌────────────────┐
│ Agent Identity │  Agent identity + Agent user context
│  + Agent User  │  Combined for delegated access
└────┬───────────┘
     │ Access token (delegated)
     ↓
┌──────────────┐
│   Resource   │  Verifies both agent identity and user context
│  (e.g., API) │  Applies user-level permissions
└──────────────┘
```

### Agent User Structure

```json
{
  "agentUserId": "au-12345-67890",
  "agentIdentityId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "userObjectId": "u9i8o7p6-5t4r-3e2w-1q0a-9z8x7y6v5u4t",
  "userPrincipalName": "john.doe@contoso.com",
  "delegatedScopes": [
    "User.Read",
    "Files.Read",
    "Mail.Send"
  ],
  "consentGranted": "2025-12-01T10:00:00Z",
  "consentExpiry": "2026-12-01T10:00:00Z"
}
```

### SDK Query Parameters

The Microsoft Entra SDK supports three query parameters for agent user scenarios:

| Parameter | Type | Description |
|-----------|------|-------------|
| `AgentIdentity` | GUID | Agent identity identifier |
| `AgentUsername` | UPN | User principal name |
| `AgentUserId` | GUID | User object ID (alternative to UPN) |

**Precedence**: `AgentUsername` > `AgentUserId`

⚠️ **Do not provide both** `AgentUsername` and `AgentUserId` simultaneously.

### Code Example: Agent User Pattern

```python
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentClient

# Interactive agent acting on behalf of a user
agent_client = AgentClient(
    endpoint="https://your-endpoint.azure.com",
    credential=DefaultAzureCredential()
)

# Specify agent identity and user context
response = agent_client.execute_task(
    agent_identity="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    agent_username="john.doe@contoso.com",  # User context
    task="Retrieve my recent emails and summarize"
)
```

## 4. Relationship Patterns

### Pattern 1: Autonomous Agent (No User Context)

```
Agent Identity (1:1)
└── Accesses resources in application context
    └── Uses: Client Credentials Flow
```

**Example**: Background data processing agent
- No user interaction
- Application-level permissions
- Operates independently

### Pattern 2: Interactive Agent (With User Context)

```
Agent Identity (1:1) + Agent User (1:1)
└── Accesses resources on behalf of user
    └── Uses: Authorization Code Flow / OBO Flow
```

**Example**: Personal assistant agent
- User initiates interaction
- User-delegated permissions
- User context preserved

### Pattern 3: Blueprint-Based Deployment

```
Agent Identity Blueprint (1:N)
├── Agent Identity Instance 1 (1:1)
│   └── Optional: Agent User (1:1)
├── Agent Identity Instance 2 (1:1)
│   └── Optional: Agent User (1:1)
└── Agent Identity Instance 3 (1:1)
    └── Optional: Agent User (1:1)
```

**Example**: Multi-region customer service deployment
- Centralized blueprint management
- Multiple instances across regions
- Each can support user-specific interactions

## 5. Agent Identity Lifecycle

### States

```
┌─────────┐      ┌────────┐      ┌───────────┐      ┌─────────┐
│ Created │ ───> │ Active │ ───> │ Suspended │ ───> │ Deleted │
└─────────┘      └────────┘      └───────────┘      └─────────┘
                      ↓                ↑
                      └────────────────┘
                        Reactivation
```

### Lifecycle Management Operations

| Operation | Description | Impact |
|-----------|-------------|--------|
| **Create** | Provision new agent identity | Identity becomes active |
| **Activate** | Enable authentication | Agent can obtain tokens |
| **Suspend** | Temporarily disable | Existing tokens remain valid until expiry |
| **Rotate Credentials** | Update certificates/secrets | Old credentials invalidated |
| **Update RBAC** | Modify role assignments | Permissions change immediately |
| **Delete** | Remove identity | All tokens immediately invalidated |

### Governance Triggers

```
┌──────────────────┐
│  Scheduled        │  Quarterly access reviews
│  Review           │  Automated compliance checks
└────────┬──────────┘
         ↓
┌──────────────────┐
│  Risk Event       │  Anomalous behavior detected
│  Detected         │  Suspicious authentication attempts
└────────┬──────────┘
         ↓
┌──────────────────┐
│  Policy           │  Conditional access policy changes
│  Update           │  Organization-wide security updates
└────────┬──────────┘
         ↓
┌──────────────────┐
│  Automated        │  Suspend, notify owner
│  Response         │  Require re-certification
└──────────────────┘
```

## 6. Agent Identity in the Registry

Agent identities are registered in the **Agent Registry** with rich metadata:

### Registry Entry

```json
{
  "registryId": "reg-agent-12345",
  "agentIdentityId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "agentCard": {
    "name": "Customer Service Agent",
    "description": "Handles tier-1 customer inquiries",
    "version": "2.1.0",
    "capabilities": [
      "order_lookup",
      "return_processing",
      "faq_response"
    ],
    "protocols": ["MCP", "A2A"],
    "endpoints": {
      "mcp": "https://api.contoso.com/agents/cs-agent/mcp",
      "a2a": "https://api.contoso.com/agents/cs-agent/a2a"
    }
  },
  "collections": [
    "customer-facing-agents",
    "production-agents"
  ],
  "discoveryPolicy": "restricted",
  "owner": "support-team@contoso.com",
  "createdDate": "2025-12-01T10:00:00Z",
  "lastUpdated": "2025-12-03T14:30:00Z"
}
```

### Registry Benefits

1. **Discoverability**: Other agents can find this agent via search
2. **Metadata**: Rich information about capabilities and endpoints
3. **Governance**: Collections and policies control access
4. **Audit**: Complete history of registry changes

## Key Takeaways

1. **Agent Identity**: The fundamental identity construct (1:1 with agent instances)
2. **Blueprint**: Reusable template for deploying multiple agents (1:N)
3. **Agent User**: Enables user context preservation in delegated scenarios
4. **Lifecycle**: Managed through standard Entra governance workflows
5. **Registry**: Provides discoverability and metadata management

## Best Practices

✅ **Do**:
- Use blueprints for standardized agent deployments
- Apply least privilege RBAC to agent identities
- Implement agent users for user-specific data access
- Register all agents in the Agent Registry
- Monitor agent identity lifecycle events

❌ **Don't**:
- Grant high-privilege roles to agent identities
- Reuse credentials across multiple agents
- Skip blueprint governance for one-off agents
- Ignore agent identity expiration/rotation
- Deploy agents without registry metadata

---

**Previous**: [← Overview](01-OVERVIEW.md) | **Next**: [Authentication →](03-AUTHENTICATION.md)

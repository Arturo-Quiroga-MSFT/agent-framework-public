# Security & Governance for Microsoft Entra Agent ID

> **Last Updated**: January 19, 2026  
> **Status**: PREVIEW

## Overview

Microsoft Entra Agent ID provides enterprise-grade security and governance capabilities specifically designed for AI agents. This document covers the four primary security pillars: Conditional Access, Identity Protection, Identity Governance, and Network Controls.

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│         Every Agent Access Request                  │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  1. Identity Verification (Authentication)          │
│     └── OAuth/OIDC token validation                 │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  2. Risk Assessment (Identity Protection)           │
│     └── Anomaly detection, threat intelligence      │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  3. Policy Evaluation (Conditional Access)          │
│     └── Risk-based, context-aware decisions         │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  4. Authorization Check (RBAC)                      │
│     └── Verify permissions for requested resource   │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  5. Network Controls (Secure Access)                │
│     └── Web filtering, prompt injection detection   │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  6. Audit Logging (Compliance)                      │
│     └── Record all agent activities                 │
└─────────────────────────────────────────────────────┘
```

## 1. Conditional Access for Agents

### Overview

Conditional Access enables organizations to define and enforce adaptive policies that evaluate agent context and risk before granting access to resources.

### Key Capabilities

- **Adaptive access control policies** for all agent patterns (assistive, autonomous, agent user types)
- **Real-time signals** such as agent identity risk controlling agent access to resources
- **Microsoft Managed Policies** providing a secure baseline by blocking high-risk agents
- **Scale deployment** using custom security attributes
- **Fine-grained controls** for individual agents

### Policy Components

#### Assignments
- Target specific agent identities or collections
- Include/exclude specific agents
- Apply to specific cloud apps or actions

#### Conditions
- Agent risk level (low, medium, high)
- Location (IP ranges, named locations)
- Platform (Azure, AWS, GCP)
- Client app type

#### Access Controls
- **Grant**: Allow access, require MFA equivalent
- **Block**: Deny access entirely
- **Session**: Monitor only, limited access

### Example Policies

#### Block High-Risk Agents

```json
{
  "displayName": "Block High-Risk Agents",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeAgents": ["all-agents-collection"]
    },
    "signInRiskLevels": ["high"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

#### Require Specific Locations for Production Agents

```json
{
  "displayName": "Production Agents - Trusted Locations Only",
  "state": "enabled",
  "conditions": {
    "users": {
      "includeAgents": ["production-agents-collection"]
    },
    "locations": {
      "includeLocations": ["AllTrusted"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["compliantDevice"]
  }
}
```

### Best Practices

1. **Start with Report-Only Mode**: Test policies before enforcement
2. **Use Collections**: Apply policies to groups, not individual agents
3. **Leverage Microsoft Managed Policies**: Let Microsoft handle baseline security
4. **Monitor Policy Impact**: Review sign-in logs regularly
5. **Exception Handling**: Document exceptions clearly

### Documentation
[Conditional Access for Agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id)

---

## 2. Identity Protection for Agents

### Overview

Identity Protection detects and blocks threats by flagging anomalous activities involving agents. Risk signals are used to enforce risk-based access policies and inform agent discoverability.

### Risk Detection Capabilities

#### User-Derived Risk
- Agent identity risk can be derived from associated user risk
- Inherits risk from user who created or manages the agent
- Useful for interactive agents acting on behalf of users

#### Agent-Specific Risk
- Based on the agent's own actions
- Unusual or unauthorized activities
- Behavioral pattern deviations
- Suspicious API access patterns

### Risk Integration

```
┌─────────────────────────────────────────┐
│     Risk Detection Engine               │
│  • Anomaly detection                    │
│  • Threat intelligence                  │
│  • Machine learning models              │
└────────────────┬────────────────────────┘
                 ↓
         ┌───────┴───────┐
         ↓               ↓
┌─────────────────┐  ┌──────────────────┐
│ Conditional     │  │ Agent Registry   │
│ Access          │  │                  │
│ • Block/Allow   │  │ • Visibility     │
│ • Require Auth  │  │ • Discoverability│
└─────────────────┘  └──────────────────┘
```

### Risk Signals

| Signal Type | Description | Risk Level |
|-------------|-------------|------------|
| **Anomalous Activity** | Unusual API call patterns | Medium-High |
| **Unfamiliar Location** | Access from new geography | Low-Medium |
| **Credential Leak** | Token found in public repos | High |
| **Brute Force** | Multiple failed auth attempts | High |
| **Impossible Travel** | Multiple locations, short time | Medium |
| **Malicious IP** | Known threat actor address | High |

### Automated Remediation

#### Preconfigured Policies

```python
# Example: Auto-disable high-risk agents
{
    "name": "Auto-Disable High-Risk Agents",
    "riskLevel": "high",
    "actions": [
        {
            "type": "disableAgent",
            "notifyOwner": true,
            "requireReview": true
        }
    ]
}
```

### Monitoring & Response

#### View Risky Agents

**Azure Portal**:
1. Navigate to **Microsoft Entra ID** → **Security** → **Identity Protection**
2. Select **Risky Agents**
3. Review risk detections and remediation recommendations

#### API Access

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.security import SecurityCenter

credential = DefaultAzureCredential()
security_client = SecurityCenter(credential, subscription_id)

# Get risky agents
risky_agents = security_client.risky_agents.list()
for agent in risky_agents:
    print(f"Agent: {agent.name}, Risk: {agent.risk_level}")
```

### Documentation
[Identity Protection for Agents](https://learn.microsoft.com/en-us/entra/id-protection/concept-risky-agents)

---

## 3. Identity Governance for Agents

### Overview

Microsoft Entra Agent ID brings agent IDs into similar identity governance processes as users, enabling management at scale.

### Lifecycle Management

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Creation   │ → │  Assignment  │ → │   Renewal    │
│              │    │              │    │              │
│ • Blueprint  │    │ • Owner      │    │ • Review     │
│ • Identity   │    │ • Sponsor    │    │ • Extend     │
└──────────────┘    └──────────────┘    └──────────────┘
                                              ↓
                         ┌──────────────────────────────┐
                         │      Expiration/Removal      │
                         │ • Auto-disable               │
                         │ • Cleanup resources          │
                         └──────────────────────────────┘
```

### Key Capabilities

#### Govern at Scale
- Deployment to expiration lifecycle
- Automated provisioning and deprovisioning
- Bulk management operations

#### Sponsor & Owner Assignment
- **Enforce sponsor assignment**: Every agent must have an assigned sponsor
- **Owner maintenance**: Regular review of ownership
- **Prevent orphaned agents**: Automated detection and alerts

#### Access Packages

Access packages ensure agent access is:
- **Intentional**: Explicitly requested and approved
- **Auditable**: Full trail of access decisions
- **Time-bound**: Automatic expiration dates

### Creating an Access Package

```json
{
  "displayName": "Agent Access to Production Cosmos DB",
  "description": "Grants agents read access to production Cosmos DB",
  "catalog": {
    "id": "production-catalog-id"
  },
  "resourceRoleScopes": [
    {
      "role": {
        "displayName": "Cosmos DB Data Reader"
      },
      "scope": {
        "resourceType": "Microsoft.DocumentDB/databaseAccounts",
        "resourceId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.DocumentDB/databaseAccounts/{account}"
      }
    }
  ],
  "requestApprovalSettings": {
    "isApprovalRequired": true,
    "approvers": [
      {
        "type": "manager"
      }
    ]
  },
  "expirationSettings": {
    "duration": "P90D"
  }
}
```

### Access Reviews

#### Periodic Reviews

```python
# Create access review for agent access
from azure.mgmt.authorization import AccessReviewScheduleDefinition

review = {
    "displayName": "Quarterly Agent Access Review",
    "scope": "/subscriptions/{sub}/resourceGroups/{rg}",
    "reviewers": [
        {"principalType": "User", "principalId": "{manager-id}"}
    ],
    "settings": {
        "recurrence": {
            "pattern": {
                "type": "absoluteMonthly",
                "interval": 3
            }
        },
        "autoApplyDecisions": True,
        "defaultDecision": "Deny"
    }
}
```

### Orphaned Agent Detection

```bash
# List agents without owners
az ad sp list --filter "servicePrincipalType eq 'Agent' and owners/$count eq 0"

# Assign owner to agent
az ad sp owner add \
  --id {agent-object-id} \
  --owner-object-id {owner-object-id}
```

### Documentation
[Identity Governance for Agents](https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview)

---

## 4. Network Controls for Agents

### Overview

Network controls enforce consistent network security policies across users and agents on any platform or application. Provides full network visibility, filters malicious content, and prevents data exfiltration.

### Key Capabilities

#### Full Network Visibility
- **Log agent network activity** to remote tools for audit and threat detection
- **Web categorization** to control access to APIs and MCP servers
- **Traffic analysis** for compliance and security monitoring

#### Security Controls
- **File-type policies**: Restrict file uploads and downloads to minimize risk
- **Threat intelligence filtering**: Automatically block and alert on malicious destinations
- **Data exfiltration prevention**: Network-based controls to prevent data leakage
- **Rate limiting**: Prevent abuse and resource exhaustion

#### Prompt Injection Protection 🆕

Network controls can **detect and block prompt injection attacks** that attempt to manipulate agent behavior through malicious instructions.

```
User Input → Network Gateway → Prompt Analysis → Agent
                    ↓
            Threat Detection
                    ↓
        ┌─── Safe? ──── Block ───┐
        ↓                         ↓
    Allow                    Log & Alert
```

### Configuration Examples

#### Enable Network Controls

**Azure Portal**:
1. Navigate to **Global Secure Access** → **Traffic Forwarding**
2. Enable **Agent Traffic**
3. Configure **Web Content Filtering** policies

#### Web Content Filtering

```json
{
  "policyName": "Agent Web Access Policy",
  "categories": {
    "allowedCategories": [
      "Business",
      "CloudStorage",
      "WebServices"
    ],
    "blockedCategories": [
      "Gambling",
      "Adult",
      "Malware",
      "PhishingSuspected"
    ]
  },
  "customUrls": {
    "allowed": [
      "https://api.openai.com/*",
      "https://*.azure.com/*"
    ],
    "blocked": [
      "https://untrusted-domain.com/*"
    ]
  }
}
```

#### File Type Restrictions

```json
{
  "policyName": "Agent File Upload Policy",
  "fileTypes": {
    "allowedUploads": [".txt", ".json", ".csv"],
    "allowedDownloads": [".pdf", ".docx", ".json"],
    "blocked": [".exe", ".dll", ".bat", ".ps1"]
  },
  "maxFileSize": "10MB"
}
```

#### Prompt Injection Detection

```python
# Example pattern detection rules
prompt_injection_patterns = {
    "ignore_previous": {
        "pattern": r"ignore (all )?previous (instructions|rules|prompts)",
        "action": "block",
        "severity": "high"
    },
    "system_override": {
        "pattern": r"you are now|new instructions|forget (everything|all)",
        "action": "block",
        "severity": "high"
    },
    "credential_extraction": {
        "pattern": r"(api.?key|password|token|secret).*is",
        "action": "alert",
        "severity": "critical"
    }
}
```

### Monitoring & Alerts

#### Network Activity Dashboard

```python
from azure.monitor import LogsQueryClient

query = """
AgentNetworkLogs
| where TimeGenerated > ago(24h)
| where Action == "Blocked"
| summarize BlockCount=count() by AgentId, DestinationUrl, Category
| order by BlockCount desc
"""

results = logs_client.query_workspace(workspace_id, query)
```

### Documentation
[Network Controls for Agents](https://learn.microsoft.com/en-us/entra/global-secure-access/concept-secure-web-ai-gateway-agents)

---

## Zero Trust Principles

All security features implement Zero Trust principles:

### 1. Verify Explicitly
- Always authenticate and authorize based on all available data points
- Multi-factor verification when appropriate
- Continuous validation

### 2. Least Privilege Access
- Just-in-time and just-enough-access (JIT/JEA)
- Risk-based adaptive policies
- Time-bound access grants

### 3. Assume Breach
- Minimize blast radius with segmentation
- Verify end-to-end encryption
- Use analytics for threat detection and response

## Compliance & Auditing

### Audit Logs

All agent activities are logged for compliance:

```python
# Query agent activity logs
from azure.monitor import LogsQueryClient

query = """
AuditLogs
| where ActivityDisplayName contains "Agent"
| where TimeGenerated > ago(30d)
| project TimeGenerated, Identity, ActivityDisplayName, Result, TargetResources
| order by TimeGenerated desc
"""
```

### Compliance Reports

Generate compliance reports for:
- Agent creation and deletion
- Permission changes
- Risk events
- Policy violations
- Access reviews

### Data Retention

Configure retention policies:
- **Audit logs**: 90 days (default), up to 2 years
- **Sign-in logs**: 30 days (default)
- **Risk detections**: Continuous
- **Access reviews**: Historical records maintained

## Best Practices Summary

### Security

1. ✅ Enable all four security pillars (Conditional Access, Identity Protection, Governance, Network Controls)
2. ✅ Start with Microsoft Managed Policies
3. ✅ Implement prompt injection detection
4. ✅ Monitor risk signals continuously
5. ✅ Regular access reviews (quarterly minimum)

### Governance

1. ✅ Enforce sponsor assignment for all agents
2. ✅ Use access packages with expiration dates
3. ✅ Automate orphaned agent detection
4. ✅ Document exception policies
5. ✅ Regular compliance reporting

### Operations

1. ✅ Comprehensive logging and monitoring
2. ✅ Automated remediation workflows
3. ✅ Incident response procedures
4. ✅ Regular security assessments
5. ✅ Team training and awareness

---

**Next**: [Implementation Guide →](06-IMPLEMENTATION-GUIDE.md)

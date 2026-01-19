# Best Practices - Microsoft Entra Agent ID

> **Last Updated**: January 19, 2026  
> **Status**: PREVIEW

## Overview

This document provides comprehensive best practices for implementing, securing, and operating AI agents with Microsoft Entra Agent ID in production environments.

## Security Best Practices

### Identity & Authentication

#### ✅ Use Managed Identity for Azure-Hosted Agents

```python
# GOOD: Managed Identity (no secrets)
from azure.identity import ManagedIdentityCredential

credential = ManagedIdentityCredential()
storage_client = BlobServiceClient(account_url, credential=credential)
```

```python
# AVOID: Hardcoded secrets
storage_client = BlobServiceClient(
    account_url="https://storage.blob.core.windows.net",
    credential=ClientSecretCredential(
        tenant_id="xxx",
        client_id="xxx",
        client_secret="hardcoded-secret-bad!"  # ❌ Never do this
    )
)
```

#### ✅ Rotate Credentials Regularly

```bash
# Automate secret rotation every 90 days
az ad sp credential reset \
  --id {agent-app-id} \
  --years 0.25  # 90 days

# Update Key Vault with new secret
az keyvault secret set \
  --vault-name {vault-name} \
  --name "agent-secret" \
  --value "{new-secret}"
```

#### ✅ Use Certificate Authentication (More Secure)

```python
from azure.identity import CertificateCredential

credential = CertificateCredential(
    tenant_id="tenant-id",
    client_id="agent-id",
    certificate_path="/path/to/cert.pem"
)
```

#### ✅ Never Log Secrets

```python
# GOOD
logging.info(f"Agent {agent_id} authenticated successfully")

# BAD
logging.info(f"Agent authenticated with secret {secret}")  # ❌ Never log secrets!
```

### Authorization & Permissions

#### ✅ Principle of Least Privilege

```bash
# GOOD: Specific role for specific resource
az role assignment create \
  --role "Storage Blob Data Reader" \
  --assignee-object-id {agent-id} \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account}/blobServices/default/containers/data

# AVOID: Overly broad permissions
az role assignment create \
  --role "Contributor" \  # ❌ Too broad!
  --assignee-object-id {agent-id} \
  --scope /subscriptions/{sub}  # ❌ Too wide scope!
```

#### ✅ Use Custom Roles for Specific Needs

```json
{
  "Name": "Agent Data Reader",
  "Description": "Allows agents to read data but not modify",
  "Actions": [
    "Microsoft.Storage/storageAccounts/blobServices/containers/read",
    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read",
    "Microsoft.DocumentDB/databaseAccounts/readonlyKeys/action"
  ],
  "NotActions": [
    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/write",
    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/delete"
  ],
  "AssignableScopes": [
    "/subscriptions/{subscription-id}/resourceGroups/production"
  ]
}
```

#### ✅ Time-Bound Access with Access Packages

```python
# Grant temporary access that expires
{
    "displayName": "Agent Q1 2026 Production Access",
    "expirationSettings": {
        "duration": "P90D",  # 90 days
        "expirationDate": "2026-03-31T23:59:59Z"
    },
    "automaticRequestSettings": {
        "requestAccessForAllowedTargets": True
    }
}
```

### Conditional Access & Identity Protection

#### ✅ Start with Report-Only Mode

```bash
# Create policy in report-only mode first
az ad ca policy create \
  --display-name "Production Agents - Location Restriction" \
  --state "enabledForReportingButNotEnforced" \
  --conditions '{...}' \
  --grant-controls '{...}'

# Monitor for 1-2 weeks, then enable
az ad ca policy update \
  --id {policy-id} \
  --state "enabled"
```

#### ✅ Implement Layered Security

```
Layer 1: Microsoft Managed Policies (baseline)
Layer 2: Organization-wide agent policies
Layer 3: Environment-specific policies (dev/test/prod)
Layer 4: Agent-specific exceptions (documented)
```

#### ✅ Monitor and Respond to Risk Signals

```python
# Automated risk response
def handle_high_risk_agent(agent_id, risk_details):
    """Respond to high-risk agent detection"""
    
    # 1. Block agent immediately
    disable_agent(agent_id)
    
    # 2. Notify security team
    send_alert(
        severity="high",
        subject=f"High-risk agent detected: {agent_id}",
        details=risk_details
    )
    
    # 3. Revoke active tokens
    revoke_agent_tokens(agent_id)
    
    # 4. Create incident ticket
    create_security_incident(agent_id, risk_details)
    
    # 5. Require manual review before re-enabling
    set_review_required(agent_id)
```

### Network Security

#### ✅ Enable Network Controls

```python
# Configure web filtering for agents
web_filtering_policy = {
    "blockedCategories": [
        "Gambling",
        "Adult",
        "Malware",
        "PhishingSuspected"
    ],
    "allowedDomains": [
        "*.azure.com",
        "*.microsoft.com",
        "api.openai.com"
    ],
    "logAllTraffic": True
}
```

#### ✅ Implement Prompt Injection Detection

```python
# Pattern-based prompt injection detection
INJECTION_PATTERNS = [
    r"ignore (all )?previous (instructions|rules)",
    r"you are now",
    r"forget (everything|all)",
    r"(api.?key|password|token|secret).*is",
    r"disregard (all )?above",
    r"new instructions:",
]

def check_prompt_injection(user_input):
    """Check for prompt injection attempts"""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            log_security_event("prompt_injection_detected", user_input)
            return True
    return False
```

#### ✅ Rate Limiting

```python
from functools import wraps
from collections import defaultdict
import time

rate_limits = defaultdict(list)

def rate_limit(max_calls=100, period=60):
    """Rate limit decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(agent_id, *args, **kwargs):
            now = time.time()
            cutoff = now - period
            
            # Clean old calls
            rate_limits[agent_id] = [
                t for t in rate_limits[agent_id] if t > cutoff
            ]
            
            # Check limit
            if len(rate_limits[agent_id]) >= max_calls:
                raise RateLimitExceeded(
                    f"Agent {agent_id} exceeded {max_calls} calls per {period}s"
                )
            
            # Record call
            rate_limits[agent_id].append(now)
            
            return func(agent_id, *args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=100, period=60)
def process_agent_request(agent_id, request):
    # Process request
    pass
```

## Governance Best Practices

### Lifecycle Management

#### ✅ Enforce Sponsor Assignment

```python
def create_agent_with_governance(name, owner_id, sponsor_id):
    """Create agent with required governance metadata"""
    
    if not sponsor_id:
        raise ValueError("Sponsor is required for all production agents")
    
    agent = create_agent_identity(name)
    
    # Assign owner
    assign_owner(agent.id, owner_id)
    
    # Assign sponsor (for accountability)
    assign_sponsor(agent.id, sponsor_id)
    
    # Set expiration (default 1 year)
    set_expiration(agent.id, days=365)
    
    # Add to appropriate collection
    add_to_collection(agent.id, determine_collection(agent))
    
    return agent
```

#### ✅ Automated Orphaned Agent Detection

```python
def detect_orphaned_agents():
    """Find and remediate orphaned agents"""
    
    orphaned = []
    
    # Query all agent identities
    agents = list_all_agents()
    
    for agent in agents:
        # Check if has owner
        owners = get_agent_owners(agent.id)
        
        if not owners:
            orphaned.append(agent)
            
            # Automated remediation
            # 1. Notify last known contact
            notify_last_contact(agent)
            
            # 2. Set grace period
            set_deletion_grace_period(agent.id, days=30)
            
            # 3. Log for compliance
            log_orphaned_agent(agent)
    
    return orphaned
```

#### ✅ Access Reviews

```python
# Configure quarterly access reviews
def setup_access_review():
    return {
        "displayName": "Q1 2026 Agent Access Review",
        "scope": {
            "principalScopes": [{
                "query": "tags/any(t:t eq 'AgentIdentity')"
            }]
        },
        "reviewers": [
            {"principalType": "Manager"},
            {"principalType": "ResourceOwner"}
        ],
        "settings": {
            "mailNotificationsEnabled": True,
            "reminderNotificationsEnabled": True,
            "defaultDecision": "Deny",  # Remove access if not reviewed
            "autoApplyDecisionsEnabled": True,
            "recommendationsEnabled": True,
            "recurrence": {
                "pattern": {"type": "absoluteMonthly", "interval": 3}
            }
        }
    }
```

### Documentation & Compliance

#### ✅ Maintain Agent Inventory

```markdown
# Agent Inventory Template

## Agent: DataAnalysisAgent-Prod-001

### Identity Information
- **Object ID**: `bde46d80-de73-4bd9-9416-4515799ae72d`
- **App ID**: `8f7d3c9e-2a4b-4f1c-9e8d-7a6b5c4d3e2f`
- **Created**: 2026-01-15
- **Expires**: 2027-01-15

### Ownership
- **Owner**: Alice Johnson (alice@contoso.com)
- **Sponsor**: Bob Smith (bob@contoso.com)
- **Team**: Data Analytics Team
- **Cost Center**: CC-12345

### Technical Details
- **Purpose**: Analyzes customer data and generates reports
- **Environment**: Production
- **Deployment**: Azure Container Apps (West US 2)
- **Resources Accessed**:
  - Cosmos DB: customer-data-prod
  - Storage Account: analytics-results-prod

### Security
- **Risk Level**: Medium
- **Conditional Access Policies**: 
  - Production Agents - Location Restriction
  - Production Agents - Device Compliance
- **Network Controls**: Enabled
- **Prompt Injection Detection**: Enabled

### Compliance
- **Data Classification**: High (contains PII)
- **Regulations**: GDPR, SOC2
- **Last Access Review**: 2026-01-01
- **Next Review**: 2026-04-01
```

#### ✅ Document Exception Policies

```markdown
# Exception Policy Template

## Exception Request: GlobalAdmin-Agent-Exception

### Justification
Agent requires temporary elevated permissions for database migration.

### Risk Assessment
- **Risk Level**: High
- **Mitigation**: Time-bound (7 days), monitored 24/7, manual approval for each operation

### Approval
- **Requested By**: DBA Team Lead
- **Approved By**: CISO
- **Approval Date**: 2026-01-15
- **Expiration Date**: 2026-01-22

### Monitoring
- All activities logged to SIEM
- Real-time alerting on suspicious activities
- Daily review by security team
```

## Operational Best Practices

### Monitoring & Alerting

#### ✅ Comprehensive Logging

```python
import logging
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Configure Azure Monitor
configure_azure_monitor()

tracer = trace.get_tracer(__name__)

def process_with_telemetry(agent_id, request):
    """Process request with full telemetry"""
    
    with tracer.start_as_current_span("process_request") as span:
        # Add attributes
        span.set_attribute("agent.id", agent_id)
        span.set_attribute("request.type", request.type)
        
        try:
            # Process request
            result = process_request(request)
            
            # Log success
            span.set_attribute("result.status", "success")
            span.set_attribute("result.items", len(result))
            
            return result
            
        except Exception as e:
            # Log error
            span.set_attribute("result.status", "error")
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise
```

#### ✅ Key Metrics to Monitor

```python
# Define SLIs (Service Level Indicators)
SLIs = {
    "authentication_success_rate": {
        "target": 99.9,
        "query": "SignInLogs | where ResultType == 'Success' | summarize SuccessRate=count()*100.0/count()"
    },
    "average_response_time": {
        "target": 500,  # ms
        "query": "AgentMetrics | summarize avg(ResponseTime)"
    },
    "error_rate": {
        "target": 0.1,  # %
        "query": "AgentLogs | where Level == 'Error' | summarize ErrorRate=count()*100.0/count()"
    },
    "policy_violation_rate": {
        "target": 0.0,
        "query": "ConditionalAccessLogs | where Result == 'failure' | summarize count()"
    }
}
```

#### ✅ Alert Configuration

```python
# Production-ready alert rules
ALERT_RULES = [
    {
        "name": "High Error Rate",
        "condition": "error_rate > 1.0",
        "severity": "high",
        "action": ["email", "pagerduty"],
        "throttle": 300  # seconds
    },
    {
        "name": "Authentication Failures",
        "condition": "failed_auth_count > 10 in 5m",
        "severity": "medium",
        "action": ["email", "slack"]
    },
    {
        "name": "High-Risk Agent Detected",
        "condition": "risk_level == 'high'",
        "severity": "critical",
        "action": ["email", "pagerduty", "disable_agent"]
    },
    {
        "name": "Orphaned Agents",
        "condition": "orphaned_count > 0",
        "severity": "low",
        "action": ["email"],
        "schedule": "daily"
    }
]
```

### Performance Optimization

#### ✅ Token Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class TokenCache:
    """Cache tokens to reduce authentication overhead"""
    
    def __init__(self):
        self.cache = {}
    
    def get_token(self, credential, scope):
        """Get token from cache or acquire new one"""
        
        cache_key = f"{credential.client_id}:{scope}"
        
        # Check cache
        if cache_key in self.cache:
            cached_token, expiry = self.cache[cache_key]
            
            # Return if still valid (with 5 min buffer)
            if datetime.now() < expiry - timedelta(minutes=5):
                return cached_token
        
        # Acquire new token
        token = credential.get_token(scope)
        
        # Cache it
        expiry = datetime.fromtimestamp(token.expires_on)
        self.cache[cache_key] = (token, expiry)
        
        return token

# Usage
token_cache = TokenCache()
token = token_cache.get_token(credential, "https://management.azure.com/.default")
```

#### ✅ Connection Pooling

```python
from azure.storage.blob import BlobServiceClient
from azure.core.pipeline.transport import RequestsTransport
from requests.adapters import HTTPAdapter

# Configure connection pooling
adapter = HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3
)

transport = RequestsTransport(session=session)
transport.session.mount('https://', adapter)

# Use with clients
blob_client = BlobServiceClient(
    account_url="https://storage.blob.core.windows.net",
    credential=credential,
    transport=transport
)
```

### Disaster Recovery

#### ✅ Backup Agent Configurations

```python
def backup_agent_config(agent_id):
    """Backup agent configuration"""
    
    config = {
        "agent_id": agent_id,
        "backup_date": datetime.utcnow().isoformat(),
        "identity": get_agent_identity(agent_id),
        "permissions": get_agent_permissions(agent_id),
        "policies": get_applied_policies(agent_id),
        "metadata": get_agent_metadata(agent_id)
    }
    
    # Store in versioned blob storage
    store_backup(f"agent-configs/{agent_id}/{datetime.utcnow().isoformat()}.json", config)
    
    return config
```

#### ✅ Implement Circuit Breaker

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Service unavailable")
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
            
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise

# Usage
breaker = CircuitBreaker()
result = breaker.call(call_external_service, arg1, arg2)
```

## Development Best Practices

### Testing

#### ✅ Test Authentication Flows

```python
import pytest
from azure.identity import ClientSecretCredential

def test_agent_can_authenticate():
    """Test agent identity authentication"""
    credential = ClientSecretCredential(
        tenant_id=TEST_TENANT_ID,
        client_id=TEST_AGENT_ID,
        client_secret=TEST_AGENT_SECRET
    )
    
    token = credential.get_token("https://management.azure.com/.default")
    assert token is not None
    assert token.expires_on > time.time()

def test_agent_rbac_permissions():
    """Test agent has correct RBAC permissions"""
    # Should succeed
    assert can_read_storage(agent_credential)
    
    # Should fail
    with pytest.raises(PermissionError):
        can_write_storage(agent_credential)

def test_conditional_access_policies():
    """Test conditional access blocking"""
    # From allowed IP
    assert can_authenticate_from_ip("10.0.0.1")
    
    # From blocked IP
    with pytest.raises(AuthenticationError):
        can_authenticate_from_ip("1.2.3.4")
```

#### ✅ Mock External Dependencies

```python
from unittest.mock import Mock, patch

@patch('azure.identity.ClientSecretCredential')
def test_agent_with_mock(mock_credential):
    """Test with mocked credential"""
    
    # Configure mock
    mock_token = Mock()
    mock_token.token = "mock-token"
    mock_token.expires_on = time.time() + 3600
    
    mock_credential.return_value.get_token.return_value = mock_token
    
    # Test your code
    agent = MyAgent(mock_credential.return_value)
    result = agent.process()
    
    assert result is not None
```

### Code Quality

#### ✅ Use Type Hints

```python
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class AgentConfig:
    agent_id: str
    name: str
    capabilities: List[str]
    environment: str
    risk_level: str

def create_agent(config: AgentConfig) -> str:
    """Create agent and return Object ID"""
    # Implementation
    pass

def get_agent_permissions(agent_id: str) -> Dict[str, List[str]]:
    """Get agent's permissions"""
    # Implementation
    pass
```

#### ✅ Error Handling

```python
# GOOD: Specific exceptions
class AgentAuthenticationError(Exception):
    """Raised when agent authentication fails"""
    pass

class AgentPermissionError(Exception):
    """Raised when agent lacks required permissions"""
    pass

def process_request(agent_id: str, request: dict):
    try:
        # Authenticate
        token = authenticate_agent(agent_id)
    except InvalidCredentialsError:
        raise AgentAuthenticationError(f"Agent {agent_id} authentication failed")
    
    try:
        # Process
        result = perform_operation(token, request)
    except PermissionDeniedError:
        raise AgentPermissionError(f"Agent {agent_id} lacks required permissions")
    
    return result

# BAD: Generic exceptions
def bad_process_request(agent_id, request):
    try:
        return perform_operation(agent_id, request)
    except:  # ❌ Too broad!
        return None  # ❌ Swallowing errors!
```

## Summary Checklist

### Security ✅
- [ ] Use Managed Identity where possible
- [ ] Implement certificate authentication for production
- [ ] Rotate secrets every 90 days
- [ ] Apply least privilege RBAC
- [ ] Enable all security features (CA, IP, IG, NC)
- [ ] Never log secrets or tokens
- [ ] Implement prompt injection detection
- [ ] Use rate limiting

### Governance ✅
- [ ] Enforce sponsor assignment
- [ ] Use time-bound access packages
- [ ] Configure quarterly access reviews
- [ ] Automate orphaned agent detection
- [ ] Maintain agent inventory
- [ ] Document exception policies
- [ ] Regular compliance audits

### Operations ✅
- [ ] Comprehensive logging and monitoring
- [ ] Configure appropriate alerts
- [ ] Track key SLIs
- [ ] Implement circuit breakers
- [ ] Backup agent configurations
- [ ] Document runbooks
- [ ] Regular disaster recovery drills

### Development ✅
- [ ] Write unit and integration tests
- [ ] Use type hints
- [ ] Proper error handling
- [ ] Code reviews required
- [ ] Mock external dependencies in tests
- [ ] Performance testing
- [ ] Security testing (SAST/DAST)

---

**Next**: [Use Cases →](10-USE-CASES.md)

# Authentication & Authorization

> **Last Updated**: December 4, 2025

## Overview

Microsoft Entra Agent ID uses industry-standard authentication protocols (OAuth 2.0 and OpenID Connect) to secure agent access to resources. This document explains the authentication mechanisms, token flows, and authorization patterns for AI agents.

## Authentication Protocols

### OAuth 2.0

**Purpose**: Authorization framework that enables agents to obtain access tokens for resource access.

**Key Components**:
- **Authorization Server**: Microsoft Entra ID
- **Resource Owner**: User or organization
- **Client**: Agent application
- **Resource Server**: Protected API or service

### OpenID Connect (OIDC)

**Purpose**: Authentication layer on top of OAuth 2.0 that enables identity verification.

**Key Components**:
- **ID Token**: Contains identity claims about the authenticated entity
- **UserInfo Endpoint**: Provides additional identity information
- **Discovery**: Metadata about the authentication service

## Token Types

### 1. Access Token

**Purpose**: Grants access to protected resources.

```json
{
  "typ": "JWT",
  "alg": "RS256",
  "kid": "key-identifier"
}
{
  "aud": "https://storage.azure.com",
  "iss": "https://login.microsoftonline.com/{tenant-id}/v2.0",
  "iat": 1701700800,
  "nbf": 1701700800,
  "exp": 1701704400,
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "oid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "azp": "agent-app-id",
  "roles": [
    "Storage.Blob.Reader"
  ],
  "agent_identity": true,
  "agent_blueprint_id": "blueprint-abc-123"
}
```

**Characteristics**:
- Short-lived (typically 1 hour)
- Scoped to specific resources
- Contains authorization claims (roles, scopes)
- Must be presented with every API request

### 2. Refresh Token

**Purpose**: Obtain new access tokens without re-authentication.

**Characteristics**:
- Long-lived (days to months)
- Single-use (rotated on each use)
- Bound to specific client
- Stored securely by agent application

### 3. ID Token

**Purpose**: Provides identity information about the authenticated agent.

```json
{
  "iss": "https://login.microsoftonline.com/{tenant-id}/v2.0",
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "aud": "agent-app-id",
  "exp": 1701704400,
  "iat": 1701700800,
  "agent_identity": true,
  "agent_name": "Customer Service Agent",
  "agent_blueprint_id": "blueprint-abc-123",
  "agent_version": "2.1.0"
}
```

**Characteristics**:
- Contains identity claims
- Used for authentication verification
- Not used for API access
- Can be validated locally

## OAuth Flow Patterns

### 1. Client Credentials Flow (Autonomous Agents)

**Use Case**: Agent operates independently without user context.

```
┌─────────────┐                                  ┌──────────────┐
│    Agent    │                                  │ Microsoft    │
│ Application │                                  │ Entra ID     │
└──────┬──────┘                                  └──────┬───────┘
       │                                                │
       │  1. POST /token                               │
       │     client_id={agent-app-id}                  │
       │     client_secret={secret}                    │
       │     grant_type=client_credentials             │
       │     scope={resource}/.default                 │
       │ ──────────────────────────────────────────> │
       │                                                │
       │  2. Access Token                              │
       │     {access_token, expires_in}                │
       │ <────────────────────────────────────────── │
       │                                                │
       ↓
┌──────────────┐
│   Protected  │  3. API Request
│   Resource   │     Authorization: Bearer {token}
└──────────────┘
```

**Python Example**:

```python
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

# Agent credentials
tenant_id = "your-tenant-id"
client_id = "agent-app-id"
client_secret = "agent-secret"

# Acquire token
credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

# Access resource
blob_service = BlobServiceClient(
    account_url="https://youraccount.blob.core.windows.net",
    credential=credential
)

# Agent operates autonomously
containers = blob_service.list_containers()
```

**When to Use**:
- ✅ Background processing agents
- ✅ Scheduled task execution
- ✅ Service-to-service communication
- ✅ No user interaction required

### 2. Authorization Code Flow (Interactive Agents)

**Use Case**: Agent acts on behalf of a user with user consent.

```
┌──────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ User │     │    Agent    │     │ Microsoft    │     │ Resource │
│      │     │ Application │     │ Entra ID     │     │          │
└───┬──┘     └──────┬──────┘     └──────┬───────┘     └────┬─────┘
    │               │                    │                   │
    │ 1. Initiate   │                    │                   │
    │ ────────────> │                    │                   │
    │               │                    │                   │
    │               │ 2. Authorization   │                   │
    │               │    Request         │                   │
    │               │ ─────────────────> │                   │
    │               │                    │                   │
    │               │ 3. Login & Consent │                   │
    │ <──────────────────────────────────┤                   │
    │               │                    │                   │
    │ 4. Authorize  │                    │                   │
    │ ─────────────────────────────────> │                   │
    │               │                    │                   │
    │               │ 5. Auth Code       │                   │
    │               │ <───────────────── │                   │
    │               │                    │                   │
    │               │ 6. Exchange for    │                   │
    │               │    Tokens          │                   │
    │               │ ─────────────────> │                   │
    │               │                    │                   │
    │               │ 7. Tokens          │                   │
    │               │ <───────────────── │                   │
    │               │                    │                   │
    │               │ 8. API Request     │                   │
    │               │ ───────────────────────────────────> │
    │               │                    │                   │
    │               │ 9. Response        │                   │
    │               │ <─────────────────────────────────── │
```

**Python Example**:

```python
from msal import PublicClientApplication

# Agent application configuration
agent_config = {
    "client_id": "agent-app-id",
    "authority": "https://login.microsoftonline.com/your-tenant-id",
    "scope": ["User.Read", "Files.Read"]
}

# Create MSAL application
app = PublicClientApplication(
    agent_config["client_id"],
    authority=agent_config["authority"]
)

# Interactive authentication with user consent
result = app.acquire_token_interactive(
    scopes=agent_config["scope"],
    prompt="consent"
)

if "access_token" in result:
    access_token = result["access_token"]
    # Agent can now act on behalf of user
    print(f"Agent authenticated as: {result['id_token_claims']['preferred_username']}")
else:
    print(f"Authentication failed: {result.get('error_description')}")
```

**When to Use**:
- ✅ Personal assistant agents
- ✅ User-specific data access
- ✅ Delegated permissions required
- ✅ User consent needed

### 3. On-Behalf-Of (OBO) Flow

**Use Case**: Agent receives token from user, exchanges it for token to access downstream service.

```
┌──────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ User │     │   Agent 1   │     │ Microsoft    │     │  Agent 2 │
│      │     │             │     │ Entra ID     │     │          │
└───┬──┘     └──────┬──────┘     └──────┬───────┘     └────┬─────┘
    │               │                    │                   │
    │ 1. User Token │                    │                   │
    │ ────────────> │                    │                   │
    │               │                    │                   │
    │               │ 2. OBO Exchange    │                   │
    │               │    grant_type=     │                   │
    │               │    urn:ietf:params │                   │
    │               │    :oauth:grant-   │                   │
    │               │    type:jwt-bearer │                   │
    │               │ ─────────────────> │                   │
    │               │                    │                   │
    │               │ 3. New Token       │                   │
    │               │    (Agent 1 →      │                   │
    │               │     Agent 2)       │                   │
    │               │ <───────────────── │                   │
    │               │                    │                   │
    │               │ 4. Call Agent 2    │                   │
    │               │ ───────────────────────────────────> │
    │               │                    │                   │
    │               │ 5. Response        │                   │
    │               │ <─────────────────────────────────── │
```

**Python Example**:

```python
import requests
from msal import ConfidentialClientApplication

# Agent 1 receives user token
user_token = request.headers.get("Authorization").split(" ")[1]

# Agent 1 configuration
agent_1_config = {
    "client_id": "agent-1-id",
    "client_secret": "agent-1-secret",
    "authority": "https://login.microsoftonline.com/tenant-id"
}

# Create confidential client
app = ConfidentialClientApplication(
    agent_1_config["client_id"],
    authority=agent_1_config["authority"],
    client_credential=agent_1_config["client_secret"]
)

# Exchange user token for downstream agent token
result = app.acquire_token_on_behalf_of(
    user_assertion=user_token,
    scopes=["api://agent-2-id/.default"]
)

if "access_token" in result:
    # Call Agent 2 with new token
    agent_2_response = requests.post(
        "https://agent2.contoso.com/api/process",
        headers={"Authorization": f"Bearer {result['access_token']}"},
        json={"task": "analyze_data"}
    )
```

**When to Use**:
- ✅ Multi-agent workflows
- ✅ Agent-to-agent calls with user context
- ✅ Microservices architecture
- ✅ Service chaining scenarios

### 4. Managed Identity (Azure-Hosted Agents)

**Use Case**: Agent running in Azure acquires token automatically.

```
┌─────────────────┐                    ┌──────────────────┐
│ Azure Service   │                    │ Azure Managed    │
│ (VM, Function,  │                    │ Identity Service │
│  Container)     │                    │                  │
└────────┬────────┘                    └────────┬─────────┘
         │                                      │
         │ 1. Request Token                    │
         │    (automatic via Azure SDK)        │
         │ ──────────────────────────────────> │
         │                                      │
         │ 2. Access Token                     │
         │    (no credentials needed)          │
         │ <────────────────────────────────── │
         │                                      │
         ↓
┌──────────────────┐
│ Azure Resource   │  3. API Call with token
│ (Storage, DB)    │
└──────────────────┘
```

**Python Example**:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# No credentials needed - uses managed identity
credential = DefaultAzureCredential()

# Access Azure Key Vault
vault_url = "https://your-keyvault.vault.azure.net"
secret_client = SecretClient(vault_url=vault_url, credential=credential)

# Agent retrieves secrets automatically
db_password = secret_client.get_secret("database-password")
```

**When to Use**:
- ✅ Agents hosted in Azure
- ✅ Eliminate credential management
- ✅ Automatic token rotation
- ✅ Best security posture

## Authorization Patterns

### Role-Based Access Control (RBAC)

Agent identities are assigned Azure RBAC roles to access resources.

**Common Roles for Agents**:

| Role | Scope | Use Case |
|------|-------|----------|
| **Storage Blob Data Reader** | Storage Account | Read-only blob access |
| **Storage Blob Data Contributor** | Storage Account | Read/write blob access |
| **Cognitive Services User** | Cognitive Services | API access |
| **Cosmos DB Account Reader** | Cosmos DB | Read database metadata |
| **Key Vault Secrets User** | Key Vault | Read secrets |
| **Reader** | Resource Group | View resources |

**Assignment Example**:

```bash
# Assign role to agent identity
az role assignment create \
  --assignee <agent-identity-object-id> \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>
```

**Python SDK**:

```python
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
auth_client = AuthorizationManagementClient(credential, subscription_id)

# Assign role to agent
role_assignment = auth_client.role_assignments.create(
    scope=f"/subscriptions/{subscription_id}/resourceGroups/{rg_name}",
    role_assignment_name=str(uuid.uuid4()),
    parameters={
        "properties": {
            "role_definition_id": f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{role_def_id}",
            "principal_id": agent_identity_object_id,
            "principal_type": "ServicePrincipal"
        }
    }
)
```

### Scoped Permissions

**Application Permissions** (app-only, no user):
```
scope = "https://graph.microsoft.com/.default"
# Agent gets all permissions assigned to its app registration
```

**Delegated Permissions** (on behalf of user):
```
scopes = [
    "User.Read",
    "Files.Read",
    "Mail.Send"
]
# Agent gets permissions user has + permissions agent is granted
```

### Least Privilege Principle

✅ **Do**:
- Grant minimum permissions required
- Use resource-specific scopes
- Time-bound access when possible
- Regular permission reviews

❌ **Don't**:
- Grant `/.default` without review
- Use `*` wildcards in scopes
- Assign owner-level permissions
- Skip permission documentation

## Token Validation

### Validating Access Tokens

```python
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import requests

def validate_token(token, expected_audience):
    # 1. Get signing keys from Microsoft
    jwks_uri = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
    jwks = requests.get(jwks_uri).json()
    
    # 2. Decode token header
    header = jwt.get_unverified_header(token)
    
    # 3. Find matching key
    key = next(k for k in jwks["keys"] if k["kid"] == header["kid"])
    
    # 4. Construct public key
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
    
    # 5. Validate token
    try:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=expected_audience,
            options={"verify_exp": True}
        )
        return decoded
    except jwt.InvalidTokenError as e:
        print(f"Token validation failed: {e}")
        return None

# Usage
token = request.headers.get("Authorization").split(" ")[1]
claims = validate_token(token, "api://your-agent-id")

if claims and claims.get("agent_identity"):
    print(f"Valid agent identity: {claims['oid']}")
```

### Token Validation Checklist

- ✅ Signature validation (RS256)
- ✅ Issuer verification (`iss` claim)
- ✅ Audience validation (`aud` claim)
- ✅ Expiration check (`exp` claim)
- ✅ Not before check (`nbf` claim)
- ✅ Agent identity flag verification
- ✅ Required claims present

## Security Best Practices

### 1. Credential Management

```python
# ✅ Good: Use Azure Key Vault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url, credential)
client_secret = secret_client.get_secret("agent-client-secret").value

# ❌ Bad: Hardcoded credentials
client_secret = "hardcoded-secret-12345"
```

### 2. Token Storage

```python
# ✅ Good: In-memory or encrypted cache
from msal import SerializableTokenCache
import keyring

cache = SerializableTokenCache()
cache_data = keyring.get_password("agent_cache", "tokens")
if cache_data:
    cache.deserialize(cache_data)

# ❌ Bad: Plain text file
with open("tokens.txt", "w") as f:
    f.write(access_token)
```

### 3. Token Lifetime

```python
# ✅ Good: Check expiration before use
import time

def get_valid_token(cache):
    if cache["expires_at"] > time.time() + 300:  # 5 min buffer
        return cache["access_token"]
    else:
        return acquire_new_token()

# ❌ Bad: Never refresh
access_token = cache["access_token"]  # May be expired
```

### 4. Error Handling

```python
# ✅ Good: Specific error handling
from azure.core.exceptions import ClientAuthenticationError

try:
    token = credential.get_token("https://storage.azure.com/.default")
except ClientAuthenticationError as e:
    logger.error(f"Authentication failed: {e.message}")
    if "invalid_client" in str(e):
        # Credential rotation needed
        notify_admin("Agent credentials expired")
    raise

# ❌ Bad: Generic catch-all
try:
    token = credential.get_token(scope)
except Exception:
    pass  # Silent failure
```

## Common Scenarios

### Scenario 1: Autonomous Data Processing Agent

```python
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient

# Agent identity credentials
credential = ClientSecretCredential(
    tenant_id=os.getenv("TENANT_ID"),
    client_id=os.getenv("AGENT_CLIENT_ID"),
    client_secret=os.getenv("AGENT_CLIENT_SECRET")
)

# Access multiple resources
blob_client = BlobServiceClient(
    account_url="https://storage.blob.core.windows.net",
    credential=credential
)

cosmos_client = CosmosClient(
    url="https://cosmosdb.documents.azure.com",
    credential=credential
)

# Process data autonomously
def process_data():
    # Read from blob
    container = blob_client.get_container_client("input-data")
    blobs = container.list_blobs()
    
    # Process and write to Cosmos DB
    database = cosmos_client.get_database_client("analytics")
    container = database.get_container_client("results")
    
    for blob in blobs:
        data = process_blob(blob)
        container.create_item(data)
```

### Scenario 2: Personal Assistant with User Context

```python
from msal import PublicClientApplication
import requests

# Interactive authentication
app = PublicClientApplication(
    client_id="agent-app-id",
    authority="https://login.microsoftonline.com/tenant-id"
)

# User signs in and grants consent
result = app.acquire_token_interactive(
    scopes=["User.Read", "Files.Read", "Mail.Send"]
)

# Agent acts on behalf of user
def send_summary_email(user_token):
    # Get user's recent files
    files_response = requests.get(
        "https://graph.microsoft.com/v1.0/me/drive/recent",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    # Generate summary
    summary = generate_summary(files_response.json())
    
    # Send email as user
    mail_response = requests.post(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "message": {
                "subject": "Your Daily File Summary",
                "body": {"content": summary},
                "toRecipients": [{"emailAddress": {"address": "user@contoso.com"}}]
            }
        }
    )
```

### Scenario 3: Multi-Agent Workflow with OBO

```python
from msal import ConfidentialClientApplication
from flask import Flask, request
import requests

app = Flask(__name__)

# Agent 1: Orchestrator
@app.route("/orchestrate", methods=["POST"])
def orchestrate():
    # Receive user token
    user_token = request.headers.get("Authorization").split(" ")[1]
    
    # Exchange for token to call Agent 2
    msal_app = ConfidentialClientApplication(
        client_id=os.getenv("AGENT1_CLIENT_ID"),
        client_credential=os.getenv("AGENT1_CLIENT_SECRET"),
        authority="https://login.microsoftonline.com/tenant-id"
    )
    
    result = msal_app.acquire_token_on_behalf_of(
        user_assertion=user_token,
        scopes=["api://agent2-id/.default"]
    )
    
    # Call Agent 2 with new token
    agent2_response = requests.post(
        "https://agent2.contoso.com/api/analyze",
        headers={"Authorization": f"Bearer {result['access_token']}"},
        json={"data": request.json}
    )
    
    return agent2_response.json()

# Agent 2: Analyzer
@app.route("/analyze", methods=["POST"])
def analyze():
    # Validate token
    token = request.headers.get("Authorization").split(" ")[1]
    claims = validate_token(token, "api://agent2-id")
    
    if not claims:
        return {"error": "Invalid token"}, 401
    
    # Verify this is an OBO flow preserving user context
    if "agent_identity" in claims and "scp" in claims:
        # Process with user context preserved
        return {"result": "analysis_complete", "user": claims.get("upn")}
    
    return {"error": "Unauthorized"}, 403
```

## Key Takeaways

1. **Use standard protocols**: OAuth 2.0 and OIDC provide proven security
2. **Choose the right flow**: Match authentication pattern to agent scenario
3. **Apply least privilege**: Grant minimum required permissions
4. **Validate tokens**: Always verify token integrity and claims
5. **Secure credentials**: Use Key Vault, managed identities
6. **Handle errors gracefully**: Implement retry logic and monitoring

---

**Previous**: [← Core Concepts](02-CORE-CONCEPTS.md) | **Next**: [Agent Registry →](04-AGENT-REGISTRY.md)

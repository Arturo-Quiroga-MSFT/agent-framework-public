# Basic Agent Authentication Example

This example demonstrates the fundamental authentication patterns for AI agents using Microsoft Entra Agent ID.

## What You'll Learn

- How to authenticate an autonomous agent (client credentials)
- How to implement interactive agent authentication
- How to use managed identities for Azure-hosted agents
- How to validate and refresh tokens
- How to handle authentication errors

## Prerequisites

- Azure subscription
- Microsoft Entra ID tenant
- Python 3.9+
- Azure CLI installed

## Setup

### 1. Create Agent Identity

```bash
# Login to Azure
az login

# Create an app registration for your agent
az ad app create \
  --display-name "Example Agent" \
  --sign-in-audience AzureADMyOrg

# Get the app ID
APP_ID=$(az ad app list --display-name "Example Agent" --query "[0].appId" -o tsv)

# Create a service principal (agent identity)
az ad sp create --id $APP_ID

# Create a client secret
az ad app credential reset --id $APP_ID --append
```

### 2. Assign RBAC Permissions

```bash
# Example: Grant Storage Blob Data Reader role
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SP_OBJECT_ID=$(az ad sp list --display-name "Example Agent" --query "[0].id" -o tsv)

az role assignment create \
  --assignee $SP_OBJECT_ID \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/$SUBSCRIPTION_ID"
```

### 3. Configure Environment

Create `.env` file:

```env
TENANT_ID=your-tenant-id
AGENT_CLIENT_ID=your-agent-client-id
AGENT_CLIENT_SECRET=your-agent-client-secret
STORAGE_ACCOUNT_NAME=your-storage-account
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Examples

### Example 1: Autonomous Agent (Client Credentials)

```python
python autonomous_agent.py
```

Demonstrates:
- Acquiring token with client credentials
- Accessing Azure Storage autonomously
- Token caching and reuse
- Error handling

### Example 2: Interactive Agent (User Context)

```python
python interactive_agent.py
```

Demonstrates:
- User authentication with consent
- Delegated permissions
- User context preservation
- Token refresh

### Example 3: Managed Identity (Azure-Hosted)

```python
python managed_identity_agent.py
```

Demonstrates:
- Automatic credential management
- Zero credential configuration
- Azure service integration

### Example 4: Token Management

```python
python token_management.py
```

Demonstrates:
- Token validation
- Token expiration handling
- Refresh token usage
- Secure token storage

## File Structure

```
basic-agent-auth/
├── README.md (this file)
├── requirements.txt
├── .env.example
├── autonomous_agent.py
├── interactive_agent.py
├── managed_identity_agent.py
├── token_management.py
└── utils/
    ├── __init__.py
    ├── token_validator.py
    └── error_handler.py
```

## Key Concepts Demonstrated

### Client Credentials Flow
```python
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id=os.getenv("TENANT_ID"),
    client_id=os.getenv("AGENT_CLIENT_ID"),
    client_secret=os.getenv("AGENT_CLIENT_SECRET")
)

# Token acquired automatically when needed
token = credential.get_token("https://storage.azure.com/.default")
```

### Token Validation
```python
import jwt

def validate_token(token):
    # Decode header
    header = jwt.get_unverified_header(token)
    
    # Verify signature, audience, expiration
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience="expected-audience"
    )
    
    return decoded
```

### Error Handling
```python
from azure.core.exceptions import ClientAuthenticationError

try:
    token = credential.get_token(scope)
except ClientAuthenticationError as e:
    if "invalid_client" in str(e):
        # Handle credential issues
        logger.error("Agent credentials invalid or expired")
    elif "unauthorized_client" in str(e):
        # Handle permission issues
        logger.error("Agent not authorized for requested scope")
    raise
```

## Testing

Run all examples:
```bash
python -m pytest tests/
```

## Troubleshooting

### Issue: "AADSTS700016: Application not found"
**Solution**: Ensure the app registration exists and service principal is created.

### Issue: "AADSTS7000215: Invalid client secret"
**Solution**: Generate a new client secret and update `.env` file.

### Issue: "Insufficient privileges"
**Solution**: Verify RBAC role assignments for the agent identity.

## Security Best Practices

✅ **Do**:
- Store credentials in Azure Key Vault
- Use managed identities when possible
- Implement token caching
- Validate tokens before use
- Handle errors gracefully
- Log authentication events

❌ **Don't**:
- Hardcode credentials in code
- Commit `.env` files to git
- Store tokens in plain text files
- Ignore token expiration
- Grant excessive permissions

## Next Steps

After completing this example, explore:
- [MCP Integration](../mcp-integration/) - Use agent identities with MCP
- [A2A Communication](../a2a-communication/) - Agent-to-agent calls
- [Azure Foundry](../azure-foundry/) - Foundry agent integration

## Resources

- [Authentication Documentation](../../03-AUTHENTICATION.md)
- [Microsoft Entra Agent ID Docs](https://aka.ms/EntraAgentID)
- [Azure Identity SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme)

---

**Back to**: [Examples](../README.md)

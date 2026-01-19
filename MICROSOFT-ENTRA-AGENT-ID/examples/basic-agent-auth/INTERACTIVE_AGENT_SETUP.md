# Interactive Agent Setup Requirements

## Issue: App Registration Needs Public Client Configuration

The interactive agent examples failed because the current app registration (`2c9ecb92-2756-4983-a4c6-2884d8ba3fa1`) is configured as a **confidential client** (service principal with secret) but interactive authentication requires a **public client** configuration.

### Error Received:
```
AADSTS7000218: The request body must contain the following parameter: 'client_assertion' or 'client_secret'
```

---

## Solution: Two Options

### Option 1: Create Separate Public Client App Registration (Recommended)

Interactive agents should use a **different** app registration than autonomous agents for security reasons:

```bash
# Create new app registration for interactive/user-context scenarios
az ad app create \
  --display-name "Interactive-Agent-Example" \
  --sign-in-audience AzureADMyOrg \
  --enable-id-token-issuance true \
  --public-client-redirect-uris "http://localhost:8400"

# Get the new app ID
NEW_APP_ID=$(az ad app list --display-name "Interactive-Agent-Example" --query "[0].appId" -o tsv)
echo "New Interactive App ID: $NEW_APP_ID"

# Enable public client flows
az ad app update \
  --id $NEW_APP_ID \
  --set isFallbackPublicClient=true

# Add delegated permissions for Microsoft Graph
az ad app permission add \
  --id $NEW_APP_ID \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope

# Add delegated permissions for Cognitive Services (Azure OpenAI)
COGNITIVE_API_ID=$(az ad sp list --display-name "Cognitive Services" --query "[0].appId" -o tsv)
az ad app permission add \
  --id $NEW_APP_ID \
  --api $COGNITIVE_API_ID \
  --api-permissions <cognitive-services-user-impersonation-scope>=Scope

# Grant admin consent (if you have admin rights)
az ad app permission admin-consent --id $NEW_APP_ID

# Update .env file
echo "INTERACTIVE_AGENT_CLIENT_ID=$NEW_APP_ID" >> .env
```

---

### Option 2: Modify Existing App (Not Recommended for Production)

You can modify the existing app to support both flows, but this is not recommended for production:

```bash
# Enable public client flows on existing app
az ad app update \
  --id 2c9ecb92-2756-4983-a4c6-2884d8ba3fa1 \
  --set isFallbackPublicClient=true

# Add redirect URI for interactive browser
az ad app update \
  --id 2c9ecb92-2756-4983-a4c6-2884d8ba3fa1 \
  --add publicClient.redirectUris "http://localhost:8400"

# Add delegated permissions
az ad app permission add \
  --id 2c9ecb92-2756-4983-a4c6-2884d8ba3fa1 \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope

# Grant admin consent
az ad app permission admin-consent --id 2c9ecb92-2756-4983-a4c6-2884d8ba3fa1
```

---

## Why Separate App Registrations?

**Security Best Practice:**
- **Autonomous agents** (service principals) = Application permissions, run unattended
- **Interactive agents** (user context) = Delegated permissions, require user login

**Separation Benefits:**
1. **Least Privilege**: Each app has only the permissions it needs
2. **Auditability**: Clear separation of automated vs user-driven actions
3. **Security**: Compromise of one doesn't affect the other
4. **Compliance**: Easier to track who did what

---

## Required Azure AD Permissions

### For Interactive Agent (Delegated):
- `User.Read` - Read user profile
- `Cognitive Services User Impersonation` - Access Azure OpenAI on behalf of user

### For Interactive Agent + LLM (Delegated):
- `User.Read` - Read user profile
- `Cognitive Services User Impersonation` - Access Azure OpenAI as user

---

## Testing Interactive Agents

After setting up the public client app registration:

### 1. Update .env file:
```bash
# Add new variable (keep existing AGENT_CLIENT_ID for autonomous agents)
INTERACTIVE_AGENT_CLIENT_ID=<new-public-client-app-id>
```

### 2. Update code to use correct client ID:
In `interactive_agent.py` and `interactive_agent_llm.py`, change:
```python
client_id = os.getenv("INTERACTIVE_AGENT_CLIENT_ID") or os.getenv("AGENT_CLIENT_ID")
```

### 3. Run the tests:
```bash
# Browser flow (default)
python interactive_agent.py

# Device code flow (for headless/SSH sessions)
python interactive_agent.py --device-code

# LLM version
python interactive_agent_llm.py
```

---

## Alternative: Test with Different Tools

If you don't want to configure the app registration, you can test interactive authentication patterns with:

### 1. Azure CLI (already working):
```bash
az login
az account get-access-token --resource https://graph.microsoft.com
```

### 2. PowerShell:
```powershell
Connect-AzAccount
Get-AzAccessToken -ResourceUrl https://graph.microsoft.com
```

### 3. VS Code Azure Account Extension:
- Already provides interactive authentication
- DefaultAzureCredential picks it up automatically

---

## Summary

**Current State:**
- ✅ Autonomous agents working (client credentials flow)
- ✅ Managed identity agents working (with DefaultAzureCredential fallback)
- ❌ Interactive agents blocked (need public client configuration)

**To Fix:**
1. Create new public client app registration (recommended)
2. Or modify existing app to allow public client flows (not recommended for production)
3. Add delegated permissions
4. Grant admin consent
5. Update .env with new client ID
6. Test with browser or device code flow

**Testing Status:**
- 4 out of 6 examples fully tested and working
- 2 interactive examples require Azure AD app registration changes

# MCP Integration with Microsoft Entra Agent ID

> **Last Updated**: January 19, 2026  
> **Status**: PREVIEW

## Overview

The **Model Context Protocol (MCP)** is an open standard that enables secure and efficient communication between AI agents and external tools/resources. Microsoft Entra Agent ID provides native authentication and authorization for MCP servers, enabling secure agent access to organizational resources.

## What is MCP?

MCP defines a standard way for agents to:
- **Discover** available tools and resources
- **Request** access to specific capabilities
- **Invoke** tools with proper authentication
- **Receive** structured responses

### MCP Architecture

```
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│              │           │              │           │              │
│   AI Agent   │ ←─MCP───→ │  MCP Server  │ ←────────→│   Resource   │
│              │           │              │           │  (Database)  │
└──────────────┘           └──────────────┘           └──────────────┘
      ↓                           ↓
      │                           │
      └──── Microsoft Entra Agent Identity ────┘
                  (Authentication)
```

## Agent Identity Authentication for MCP

### Authentication Flow

```
1. Agent requests MCP server access
         ↓
2. Agent Identity token obtained (OAuth 2.0)
         ↓
3. Token sent to MCP server
         ↓
4. MCP server validates token with Microsoft Entra
         ↓
5. MCP server checks agent permissions
         ↓
6. MCP server grants/denies access
```

### Token Acquisition

```python
from azure.identity import ClientSecretCredential

# Agent Identity credentials
credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="agent-app-id",
    client_secret="agent-secret"
)

# Get token for MCP server
# Scope format: api://{mcp-server-app-id}/.default
token = credential.get_token("api://mcp-knowledge-base-server/.default")

# Use token in MCP request
headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}
```

## MCP in Azure AI Foundry

### Automatic Agent Identity Integration

When creating agents in Azure AI Foundry, MCP tools automatically use the agent's identity for authentication:

```python
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import McpTool
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint="https://your-project.azure.com",
    credential=DefaultAzureCredential()
)

# Create MCP tool - authentication is automatic
mcp_tool = McpTool(
    server_url="https://mcp-knowledge-base.contoso.com",
    server_label="knowledge_base"
)

# Agent identity is used automatically for MCP authentication
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="ResearchAgent",
    instructions="You are a research assistant with access to the knowledge base.",
    tools=[mcp_tool]
)
```

### How It Works

1. **Agent publishes** → Agent Identity created in Entra ID
2. **MCP tool added** → Agent Identity app registration includes MCP server scope
3. **Agent invokes tool** → Token automatically acquired using Agent Identity
4. **MCP server validates** → Token validated against Entra ID
5. **Access granted** → Agent can use MCP tool

## Building an MCP Server with Agent Identity Auth

### Server Setup

#### 1. Register MCP Server in Azure AD

```bash
# Create app registration for MCP server
az ad app create \
  --display-name "MCP Knowledge Base Server" \
  --identifier-uris "api://mcp-knowledge-base-server"

# Note the Application (client) ID from output
APP_ID="<app-id-from-output>"

# Expose an API scope
az ad app update --id $APP_ID \
  --set api='{"oauth2PermissionScopes":[{
    "id":"'$(uuidgen)'",
    "adminConsentDescription":"Allow agents to access knowledge base",
    "adminConsentDisplayName":"Access knowledge base",
    "type":"Admin",
    "value":"KnowledgeBase.Read"
  }]}'
```

#### 2. Grant Agent Identity Permission

```bash
# Grant agent permission to call MCP server
az ad app permission add \
  --id {agent-app-id} \
  --api {mcp-server-app-id} \
  --api-permissions {permission-id}=Scope

# Grant admin consent
az ad app permission admin-consent \
  --id {agent-app-id}
```

### MCP Server Implementation (Python)

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AccessToken
import jwt

app = FastAPI()
security = HTTPBearer()

# MCP Server configuration
MCP_SERVER_APP_ID = "api://mcp-knowledge-base-server"
TENANT_ID = "your-tenant-id"

# Token validation
def validate_agent_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate agent identity token"""
    token = credentials.credentials
    
    try:
        # Decode token (verify signature against Microsoft public keys)
        decoded = jwt.decode(
            token,
            options={"verify_signature": False},  # Simplified for example
            audience=MCP_SERVER_APP_ID
        )
        
        # Verify claims
        if decoded.get("tid") != TENANT_ID:
            raise HTTPException(status_code=401, detail="Invalid tenant")
        
        if decoded.get("aud") != MCP_SERVER_APP_ID:
            raise HTTPException(status_code=401, detail="Invalid audience")
        
        # Extract agent identity
        agent_id = decoded.get("oid")  # Object ID of agent
        agent_app_id = decoded.get("appid")  # Application ID
        
        return {
            "agent_id": agent_id,
            "agent_app_id": agent_app_id,
            "roles": decoded.get("roles", [])
        }
        
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# MCP Endpoints

@app.get("/mcp/v1/tools")
async def list_tools(agent = Depends(validate_agent_token)):
    """List available tools"""
    return {
        "tools": [
            {
                "name": "search_knowledge_base",
                "description": "Search the organizational knowledge base",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"}
                }
            },
            {
                "name": "get_document",
                "description": "Retrieve a specific document",
                "parameters": {
                    "document_id": {"type": "string", "description": "Document ID"}
                }
            }
        ]
    }

@app.post("/mcp/v1/invoke")
async def invoke_tool(request: dict, agent = Depends(validate_agent_token)):
    """Invoke a tool"""
    tool_name = request.get("tool")
    parameters = request.get("parameters", {})
    
    # Log agent activity
    print(f"Agent {agent['agent_id']} invoking tool: {tool_name}")
    
    if tool_name == "search_knowledge_base":
        query = parameters.get("query")
        results = search_knowledge_base(query, agent)
        return {"result": results}
    
    elif tool_name == "get_document":
        doc_id = parameters.get("document_id")
        document = get_document(doc_id, agent)
        return {"result": document}
    
    else:
        raise HTTPException(status_code=400, detail="Unknown tool")

def search_knowledge_base(query: str, agent: dict):
    """Search implementation with agent context"""
    # Check agent permissions for specific content
    # Implement RBAC based on agent identity
    # Log access for audit
    
    # Example implementation
    results = [
        {"title": "Document 1", "snippet": "..."},
        {"title": "Document 2", "snippet": "..."}
    ]
    return results

def get_document(doc_id: str, agent: dict):
    """Document retrieval with agent permissions"""
    # Verify agent has permission to access this document
    # Log document access
    
    return {
        "id": doc_id,
        "title": "Sample Document",
        "content": "Document content...",
        "accessed_by": agent["agent_id"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### MCP Server Implementation (.NET)

```csharp
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// Add authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddAuthorization();
builder.Services.AddControllers();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();

// MCP Controller
[ApiController]
[Route("mcp/v1")]
[Authorize]
public class McpController : ControllerBase
{
    [HttpGet("tools")]
    public IActionResult ListTools()
    {
        // Extract agent identity from claims
        var agentId = User.FindFirst("oid")?.Value;
        var agentAppId = User.FindFirst("appid")?.Value;
        
        return Ok(new
        {
            tools = new[]
            {
                new
                {
                    name = "search_knowledge_base",
                    description = "Search the organizational knowledge base",
                    parameters = new
                    {
                        query = new { type = "string", description = "Search query" }
                    }
                }
            }
        });
    }
    
    [HttpPost("invoke")]
    public IActionResult InvokeTool([FromBody] ToolRequest request)
    {
        var agentId = User.FindFirst("oid")?.Value;
        
        // Log agent activity
        Console.WriteLine($"Agent {agentId} invoking tool: {request.Tool}");
        
        // Implement tool logic with agent permissions
        return Ok(new { result = "Tool result" });
    }
}

public class ToolRequest
{
    public string Tool { get; set; }
    public Dictionary<string, object> Parameters { get; set; }
}
```

## Agent Client Implementation

### Using MCP Tool in Agent Code

```python
from azure.identity import ClientSecretCredential
import requests

class AgentMcpClient:
    def __init__(self, agent_credential, mcp_server_url, mcp_server_scope):
        self.credential = agent_credential
        self.server_url = mcp_server_url
        self.scope = mcp_server_scope
        
    def get_token(self):
        """Get access token for MCP server"""
        token = self.credential.get_token(self.scope)
        return token.token
    
    def list_tools(self):
        """List available tools from MCP server"""
        token = self.get_token()
        
        response = requests.get(
            f"{self.server_url}/mcp/v1/tools",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    
    def invoke_tool(self, tool_name, parameters):
        """Invoke a specific tool"""
        token = self.get_token()
        
        response = requests.post(
            f"{self.server_url}/mcp/v1/invoke",
            headers={"Authorization": f"Bearer {token}"},
            json={"tool": tool_name, "parameters": parameters}
        )
        response.raise_for_status()
        return response.json()

# Usage
agent_credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="agent-app-id",
    client_secret="agent-secret"
)

mcp_client = AgentMcpClient(
    agent_credential=agent_credential,
    mcp_server_url="https://mcp-knowledge-base.contoso.com",
    mcp_server_scope="api://mcp-knowledge-base-server/.default"
)

# List available tools
tools = mcp_client.list_tools()
print(f"Available tools: {tools}")

# Invoke a tool
result = mcp_client.invoke_tool(
    tool_name="search_knowledge_base",
    parameters={"query": "Microsoft Entra Agent ID"}
)
print(f"Search results: {result}")
```

## Security Best Practices

### 1. Token Validation

Always validate:
- ✅ Token signature (against Microsoft public keys)
- ✅ Issuer (`iss` claim matches Microsoft Entra)
- ✅ Audience (`aud` claim matches your MCP server)
- ✅ Expiration (`exp` claim is in the future)
- ✅ Tenant ID (`tid` claim matches your tenant)

### 2. Permission Scoping

```python
# Define granular scopes for different tool categories
scopes = {
    "read": "KnowledgeBase.Read",
    "write": "KnowledgeBase.Write",
    "admin": "KnowledgeBase.Admin"
}

# Check agent has required scope
def require_scope(required_scope):
    def decorator(func):
        def wrapper(agent, *args, **kwargs):
            agent_scopes = agent.get("scp", "").split()
            if required_scope not in agent_scopes:
                raise PermissionError(f"Agent lacks required scope: {required_scope}")
            return func(agent, *args, **kwargs)
        return wrapper
    return decorator

@require_scope("KnowledgeBase.Write")
def update_document(doc_id, content, agent):
    # Only agents with Write scope can call this
    pass
```

### 3. Audit Logging

```python
import logging
from datetime import datetime

def log_mcp_access(agent_id, tool_name, parameters, result):
    """Log all MCP tool invocations"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent_id": agent_id,
        "tool": tool_name,
        "parameters": parameters,
        "result_status": "success" if result else "failure"
    }
    
    # Send to Azure Monitor / Log Analytics
    logging.info(f"MCP Access: {log_entry}")
```

### 4. Rate Limiting

```python
from fastapi import HTTPException
from collections import defaultdict
from datetime import datetime, timedelta

# Simple rate limiter
rate_limit_store = defaultdict(list)
RATE_LIMIT = 100  # requests per minute

def check_rate_limit(agent_id):
    now = datetime.utcnow()
    minute_ago = now - timedelta(minutes=1)
    
    # Clean old requests
    rate_limit_store[agent_id] = [
        req_time for req_time in rate_limit_store[agent_id]
        if req_time > minute_ago
    ]
    
    # Check limit
    if len(rate_limit_store[agent_id]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Record this request
    rate_limit_store[agent_id].append(now)
```

## Advanced Scenarios

### Multi-MCP Server Agent

```python
# Agent accessing multiple MCP servers
mcp_servers = {
    "knowledge_base": AgentMcpClient(
        credential,
        "https://mcp-kb.contoso.com",
        "api://mcp-kb-server/.default"
    ),
    "data_warehouse": AgentMcpClient(
        credential,
        "https://mcp-dw.contoso.com",
        "api://mcp-dw-server/.default"
    )
}

# Use different servers as needed
kb_results = mcp_servers["knowledge_base"].invoke_tool("search", {...})
dw_results = mcp_servers["data_warehouse"].invoke_tool("query", {...})
```

### Federated MCP (Cross-Organization)

```python
# Agent from Organization A accessing Organization B's MCP server
# Requires B2B collaboration setup

external_credential = ClientSecretCredential(
    tenant_id="org-a-tenant-id",
    client_id="org-a-agent-id",
    client_secret="org-a-agent-secret"
)

# Token request includes resource tenant
token = external_credential.get_token(
    "api://org-b-mcp-server/.default",
    tenant_id="org-b-tenant-id"  # Target tenant
)
```

## Monitoring & Troubleshooting

### Common Issues

#### Issue: 401 Unauthorized from MCP Server

**Solutions**:
1. Verify token scope matches MCP server audience
2. Check app permissions granted and consented
3. Validate token hasn't expired
4. Ensure MCP server is validating tokens correctly

#### Issue: 403 Forbidden - Agent Lacks Permission

**Solutions**:
1. Check agent has required API permissions
2. Verify admin consent has been granted
3. Review MCP server's permission checking logic
4. Check for conditional access policy blocking access

### Monitoring Dashboard

```kusto
// KQL query for MCP access monitoring
McpAccessLogs
| where TimeGenerated > ago(24h)
| summarize 
    TotalRequests=count(),
    UniqueAgents=dcount(AgentId),
    AvgResponseTime=avg(ResponseTime)
    by Tool, bin(TimeGenerated, 1h)
| render timechart
```

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Azure AI Foundry MCP Documentation](https://learn.microsoft.com/en-us/azure/ai-services/agents/model-context-protocol)
- [Microsoft Identity Platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/)

---

**Next**: [A2A Protocol →](08-A2A-PROTOCOL.md)

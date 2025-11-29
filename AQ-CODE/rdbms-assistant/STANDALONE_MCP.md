# RDBMS Assistant - Standalone MCP Server Configuration

## Overview

The RDBMS Assistant uses the MSSQL MCP Server in **standalone mode** - no VS Code dependency required! The MCP server runs as a separate Node.js process that your Python agent communicates with via the Model Context Protocol.

## Architecture

```
┌─────────────────────────────────┐
│  Python Agent                   │
│  (db_health_agent.py)           │
│  - AzureAIAgentClient           │
└────────────┬────────────────────┘
             │ MCP Protocol
┌────────────▼────────────────────┐
│  MSSQL MCP Server               │
│  (Node.js Standalone Process)   │
│  - Reads .env variables         │
│  - Manages SQL connections      │
│  - Exposes 13 tools             │
└────────────┬────────────────────┘
             │ SQL Protocol
┌────────────▼────────────────────┐
│  SQL Server / Azure SQL         │
│  - Local or Cloud               │
│  - Entra ID or SQL Auth         │
└─────────────────────────────────┘
```

## Environment Variable Configuration

The MCP server is configured via environment variables in your `.env` file:

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SERVER_NAME` | SQL Server hostname | `localhost` or `myserver.database.windows.net` |
| `DATABASE_NAME` | Initial database | `master` |
| `READONLY` | Restrict to read-only | `false` |
| `TRUST_SERVER_CERTIFICATE` | Trust self-signed certs | `true` (dev), `false` (prod) |

### Authentication Options

#### Option 1: Entra ID (Azure Active Directory)
**Best for:** Azure SQL Database

```bash
# .env configuration
SERVER_NAME=myserver.database.windows.net
DATABASE_NAME=mydb
# No SQL_USERNAME or SQL_PASSWORD needed
```

**Prerequisites:**
```bash
az login
az account show  # Verify authentication
```

The MCP server will use your Azure CLI credentials automatically.

#### Option 2: SQL Server Authentication
**Best for:** Local SQL Server, development environments

```bash
# .env configuration
SERVER_NAME=localhost
DATABASE_NAME=master
SQL_USERNAME=sa
SQL_PASSWORD=YourStrongPassword123!
```

**Note:** Requires modifying the MCP server code to use SQL authentication instead of default Entra ID. See "Customizing Authentication" section below.

#### Option 3: Windows Authentication
**Best for:** Windows environments, .NET MCP server

Use the .NET implementation of the MCP server which supports Windows Authentication natively.

## Customizing Authentication

The Node.js MCP server defaults to Entra ID authentication. To use SQL Server Authentication:

1. Navigate to your cloned MCP server repository:
```bash
cd SQL-AI-samples/MssqlMcp/Node/src
```

2. Edit the connection configuration (likely in `index.ts` or `db.ts`):

```typescript
// Change from:
authentication: {
  type: 'azure-active-directory-access-token'
}

// To:
authentication: {
  type: 'default',
  options: {
    userName: process.env.SQL_USERNAME,
    password: process.env.SQL_PASSWORD,
  },
}
```

3. Rebuild:
```bash
npm run build
```

## Starting the MCP Server

### Manual Start (for testing)

```bash
cd SQL-AI-samples/MssqlMcp/Node

# Set environment variables
export SERVER_NAME=localhost
export DATABASE_NAME=master
export READONLY=false
export TRUST_SERVER_CERTIFICATE=true
export SQL_USERNAME=sa
export SQL_PASSWORD=YourPassword

# Run the server
node dist/index.js
```

### Integrated with Python Agent

The Python agent will start the MCP server automatically when configured properly. The agent uses the MCP Python SDK to spawn the Node.js process.

**Configuration in Python:**

```python
from mcp import StdioClientTransport
import os

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Configure MCP transport
transport = StdioClientTransport(
    command="node",
    args=["/path/to/SQL-AI-samples/MssqlMcp/Node/dist/index.js"],
    env={
        "SERVER_NAME": os.getenv("SERVER_NAME"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
        "READONLY": os.getenv("READONLY", "false"),
        "TRUST_SERVER_CERTIFICATE": os.getenv("TRUST_SERVER_CERTIFICATE", "true"),
        "SQL_USERNAME": os.getenv("SQL_USERNAME", ""),
        "SQL_PASSWORD": os.getenv("SQL_PASSWORD", ""),
    }
)
```

## Connection String Format

While environment variables are used, the underlying connection format follows standard SQL Server patterns:

### Azure SQL Database
```
Server=myserver.database.windows.net;Database=mydb;Authentication=Active Directory Default;
```

### SQL Server with SQL Authentication
```
Server=localhost;Database=master;User Id=sa;Password=YourPassword;TrustServerCertificate=True;
```

### SQL Server with Port
```
Server=localhost,1433;Database=master;...
```

## Security Best Practices

1. **Never commit `.env` files** with credentials
2. **Use Azure Key Vault** for production credentials
3. **Enable SSL/TLS** for all connections (set `TRUST_SERVER_CERTIFICATE=false` in prod)
4. **Use Managed Identity** when running in Azure (App Service, Container Apps, VMs)
5. **Rotate passwords** regularly if using SQL authentication
6. **Use read-only connections** when possible (`READONLY=true`)

## Troubleshooting

### Connection Refused
```
Error: connect ECONNREFUSED
```
**Solution:**
- Verify SQL Server is running
- Check firewall rules
- Confirm SERVER_NAME and port

### Authentication Failed
```
Error: Login failed for user
```
**Solution:**
- For Entra ID: Run `az login` and verify with `az account show`
- For SQL Auth: Verify username/password are correct
- Check SQL Server authentication mode (mixed mode required for SQL auth)

### Certificate Trust Issues
```
Error: Self-signed certificate
```
**Solution:**
- Set `TRUST_SERVER_CERTIFICATE=true` in .env
- Or install proper SSL certificate on SQL Server

### Module Not Found
```
Error: Cannot find module
```
**Solution:**
- Run `npm install` in the MCP server directory
- Verify the path to `dist/index.js` is correct

## Comparison: Standalone vs VS Code Mode

| Feature | Standalone Mode | VS Code Mode |
|---------|----------------|--------------|
| **Dependencies** | Node.js, Python | VS Code + Extension |
| **Configuration** | Environment variables | VS Code settings UI |
| **Portability** | High - runs anywhere | Low - requires VS Code |
| **Deployment** | Easy - containerize | Difficult - desktop only |
| **CI/CD Integration** | ✅ Yes | ❌ No |
| **Multi-Connection** | One per server instance | Multiple via VS Code UI |
| **Best For** | Production, automation | Interactive development |

## Next Steps

1. **Configure your `.env`** with SQL Server connection details
2. **Build the MCP server** from the GitHub repository
3. **Test the connection** manually with Node.js
4. **Run the Python agent** which will communicate with the MCP server
5. **Deploy to production** using containers or serverless functions

## References

- [MSSQL MCP Server GitHub](https://github.com/Azure-Samples/SQL-AI-samples/tree/main/MssqlMcp)
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- [Node.js SQL Authentication](https://learn.microsoft.com/en-us/sql/connect/node-js/node-js-driver-for-sql-server)
- [Azure SQL Entra ID](https://learn.microsoft.com/en-us/azure/azure-sql/database/authentication-aad-overview)

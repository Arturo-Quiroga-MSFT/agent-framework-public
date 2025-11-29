# Quick Setup for SQL Server Authentication Testing

## Your Current Configuration ✅

Your `.env` is already set up for SQL Auth:
```bash
SERVER_NAME=localhost
DATABASE_NAME=master
SQL_USERNAME=sa
SQL_PASSWORD=YourStrongPassword123!
TRUST_SERVER_CERTIFICATE=true
```

## Required: Modify MCP Server for SQL Auth

The Node.js MCP server defaults to Entra ID. You need to change it to use SQL authentication.

### Step 1: Clone and Build MCP Server

```bash
# Clone the repository
git clone https://github.com/Azure-Samples/SQL-AI-samples.git
cd SQL-AI-samples/MssqlMcp/Node
```

### Step 2: Modify Authentication Code

Edit the file: `src/index.ts` (or similar authentication config file)

**Find this code block:**
```typescript
const config = {
  server: process.env.SERVER_NAME,
  database: process.env.DATABASE_NAME,
  authentication: {
    type: 'azure-active-directory-access-token',
    options: {
      token: async () => {
        // Token retrieval logic
      }
    }
  },
  options: {
    encrypt: true,
    trustServerCertificate: process.env.TRUST_SERVER_CERTIFICATE === 'true'
  }
};
```

**Replace with:**
```typescript
const config = {
  server: process.env.SERVER_NAME,
  database: process.env.DATABASE_NAME,
  authentication: {
    type: 'default',
    options: {
      userName: process.env.SQL_USERNAME,
      password: process.env.SQL_PASSWORD,
    }
  },
  options: {
    encrypt: true,
    trustServerCertificate: process.env.TRUST_SERVER_CERTIFICATE === 'true'
  }
};
```

### Step 3: Build

```bash
npm install
npm run build
```

### Step 4: Note the Path

Save the path to the built file:
```
/path/to/SQL-AI-samples/MssqlMcp/Node/dist/index.js
```

## Test the MCP Server Manually

```bash
cd SQL-AI-samples/MssqlMcp/Node

# Export environment variables
export SERVER_NAME=localhost
export DATABASE_NAME=master
export SQL_USERNAME=sa
export SQL_PASSWORD=YourStrongPassword123!
export TRUST_SERVER_CERTIFICATE=true
export READONLY=false

# Run the server
node dist/index.js
```

If it connects successfully, you'll see the MCP server waiting for input.

## Alternative: Use .NET MCP Server

The .NET version has better support for SQL Authentication out of the box:

```bash
cd SQL-AI-samples/MssqlMcp/dotnet
dotnet build
dotnet run
```

Configure via environment variables (same as Node.js version).

## Update Python Agent Configuration

Once your MCP server is built and tested, update `db_health_agent.py`:

```python
# Add at the top of the file
MCP_SERVER_PATH = "/Users/arturoquiroga/path/to/SQL-AI-samples/MssqlMcp/Node/dist/index.js"
```

## SQL Server Setup Checklist

Make sure your SQL Server is ready:

1. **SQL Server is running**
   ```bash
   # On macOS/Linux with Docker:
   docker ps | grep sql
   
   # Or start SQL Server:
   docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrongPassword123!" \
     -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest
   ```

2. **Mixed Mode Authentication enabled**
   - SQL Server must allow SQL authentication (not just Windows auth)

3. **SA account enabled**
   ```sql
   ALTER LOGIN sa ENABLE;
   ALTER LOGIN sa WITH PASSWORD = 'YourStrongPassword123!';
   ```

4. **Firewall allows connections**
   ```bash
   # Test connection
   sqlcmd -S localhost -U sa -P YourStrongPassword123!
   ```

## Quick Test Query

Once everything is set up, test with a simple query:

```bash
# In the MCP server directory
export SERVER_NAME=localhost
export DATABASE_NAME=master  
export SQL_USERNAME=sa
export SQL_PASSWORD=YourStrongPassword123!
export TRUST_SERVER_CERTIFICATE=true

node dist/index.js
```

Then in another terminal, test the Python agent:
```bash
cd AQ-CODE/rdbms-assistant
source ../../.venv/bin/activate
python db_health_agent.py
```

Choose option 3 (Interactive) and ask:
```
DBA> What databases are available?
```

## Troubleshooting

### "Login failed for user 'sa'"
- Verify password is correct
- Ensure SA account is enabled
- Check SQL Server authentication mode (mixed mode required)

### "Connection refused"
- SQL Server not running
- Wrong port (default is 1433)
- Firewall blocking connection

### "Certificate error"
- Set `TRUST_SERVER_CERTIFICATE=true` in .env
- Or install proper certificate on SQL Server

## Ready to Go!

Your `.env` is already configured for SQL Auth. Just:
1. Clone and modify the MCP server code for SQL authentication
2. Build the MCP server
3. Test the connection manually
4. Run the Python agent

Let me know if you need help with any of these steps!

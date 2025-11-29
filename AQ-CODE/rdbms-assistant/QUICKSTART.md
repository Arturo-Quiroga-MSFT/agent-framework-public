# RDBMS Assistant - Quick Start Guide

## Installation

### 1. Build the MSSQL MCP Server (Standalone Mode)

The MCP server runs as a standalone Node.js process - **no VS Code required!**

```bash
# Install Node.js (if not already installed)
# Download from: https://nodejs.org/

# Clone the MSSQL MCP Server repository
git clone https://github.com/Azure-Samples/SQL-AI-samples.git

# Navigate to the Node.js MCP server
cd SQL-AI-samples/MssqlMcp/Node

# Install dependencies and build
npm install

# Note the path to the built index.js file
# Location: SQL-AI-samples/MssqlMcp/Node/dist/index.js
```

### 2. Set up Python Environment
```bash
cd AQ-CODE/rdbms-assistant

# Use the workspace virtual environment
source ../../.venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Azure Authentication
```bash
# Login to Azure
az login

# Verify authentication
az account show
```

### 4. Set Up Environment Variables
```bash
# Copy template
cp .env.template .env

# Edit .env with your settings
nano .env
```

**Required Settings in .env:**

1. **Azure AI Project Connection String**
   - Get from: Azure Portal → Your AI Project → Settings

2. **SQL Server Connection**
   ```bash
   SERVER_NAME=localhost           # Or: your-server.database.windows.net
   DATABASE_NAME=master            # Your database name
   TRUST_SERVER_CERTIFICATE=true   # For local dev
   ```

3. **Authentication** (choose one):

   **Option A: Entra ID (Azure AD) - For Azure SQL**
   ```bash
   # No username/password needed
   # Just run: az login
   ```

   **Option B: SQL Server Authentication - For Local SQL**
   ```bash
   SQL_USERNAME=sa
   SQL_PASSWORD=YourStrongPassword123!
   ```

### 5. Configure MCP Server Path

The assistant needs to know where your built MCP server is located.

Edit `db_health_agent.py` and update the MCP server path:
```python
MCP_SERVER_PATH = "/path/to/SQL-AI-samples/MssqlMcp/Node/dist/index.js"
```

## Usage

### Run the Health Monitor Agent

```bash
python db_health_agent.py
```

This provides three modes:

#### Mode 1: Comprehensive Health Check
Runs a full suite of diagnostic queries:
- Index fragmentation analysis
- Blocking session detection
- Database size monitoring
- Performance bottleneck identification

#### Mode 2: Quick Health Assessment (Streaming)
Real-time streaming analysis for rapid diagnostics.

#### Mode 3: Interactive DBA Session (Recommended)
Chat-style interface where you can ask questions like:
- "Check index fragmentation on all tables"
- "Show me the top 5 slowest queries"
- "Are there any blocking sessions?"
- "What's the database size and growth trend?"

### Example Session

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                   SQL Database Health Monitor Agent                          ║
║                   Powered by Microsoft Agent Framework                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Choose a demo mode:
  1. Comprehensive Health Check (non-streaming)
  2. Quick Health Assessment (streaming)
  3. Interactive DBA Session (recommended)

Enter choice (1-3) [3]: 3

Available servers (example - actual list from mssql_list_servers):
  - localhost
  - myserver.database.windows.net

Enter server name: localhost

✅ Connected to localhost
💬 You can now ask questions...

DBA> Check for high index fragmentation

🤖 Agent: I'll check the index fragmentation across your databases...

[Agent performs analysis and provides recommendations]

DBA> exit
👋 Goodbye!
```

## Architecture

```
Your Question
     ↓
db_health_agent.py (AzureAIAgentClient)
     ↓
Azure AI Agent Service + LLM
     ↓
mcp_client.py (MCP Tool Wrappers)
     ↓
MSSQL MCP Server (Standalone Node.js Process)
     ↓
Direct SQL Connection (Entra ID or SQL Auth)
     ↓
Azure SQL / SQL Server / On-Premises
```

**No VS Code Required!** The MCP server runs as a standalone process using environment variables for configuration.

## Available Tools

The agent has access to these MSSQL MCP tools:

### Connection Management
- `mssql_list_servers` - List configured servers
- `mssql_connect` - Connect to a server/database
- `mssql_disconnect` - Disconnect from server
- `mssql_change_database` - Switch database
- `mssql_get_connection_details` - View connection info

### Discovery
- `mssql_list_databases` - List all databases
- `mssql_list_tables` - List tables
- `mssql_list_views` - List views
- `mssql_list_schemas` - List schemas
- `mssql_list_functions` - List functions

### Execution
- `mssql_run_query` - Execute SQL queries
- `mssql_show_schema` - Open schema visualizer

### Built-in DBA Queries
The agent has access to pre-built queries for:
- Index fragmentation analysis
- Blocking session detection
- Database size monitoring
- Top CPU-consuming queries
- Missing index recommendations

## Safety Features

### Read-Only by Default
Most operations use SELECT queries only. Write operations require explicit approval.

### Query Validation
All queries are analyzed before execution to identify:
- Destructive operations (DROP, TRUNCATE, DELETE without WHERE)
- Schema changes (ALTER, CREATE)
- Data modifications (INSERT, UPDATE)

### Approval Workflow
Set `REQUIRE_APPROVAL_FOR_WRITES=true` in `.env` to enable approval prompts for any write operation.

## Troubleshooting

### "AZURE_AI_PROJECT_CONNECTION_STRING not set"
- Create `.env` file from `.env.template`
- Add your Azure AI project connection string

### "Authentication failed"
- Run `az login` to authenticate
- Verify with `az account show`

### "MCP server not found"
- Install: `npm install -g @azure/mssql-mcp-server`
- Verify: `npm list -g @azure/mssql-mcp-server`

### "No servers available"
- Configure connections in VS Code SQL extension
- Verify connections work in VS Code SQL Explorer

### "Connection refused"
- Check SQL Server is running
- Verify firewall rules allow connections
- Test connection in VS Code SQL extension first

## Next Steps

### Create More Specialized Agents

1. **Performance Tuner Agent** - Focus on query optimization
2. **Backup Manager Agent** - Handle backup/restore operations
3. **Security Auditor Agent** - Review permissions and vulnerabilities
4. **Capacity Planner Agent** - Analyze growth trends

### Add Custom Tools

Extend `mcp_client.py` with domain-specific functions:
```python
def check_backup_status(connection_id: str) -> str:
    """Check last backup date for all databases."""
    # Implementation
    pass
```

### Build a Web UI

Use Gradio to create a web interface:
```python
import gradio as gr

def health_check(server_name: str, question: str) -> str:
    # Run agent and return results
    pass

demo = gr.Interface(
    fn=health_check,
    inputs=["text", "text"],
    outputs="text"
)
demo.launch()
```

## Resources

- [MSSQL MCP Server Blog](https://devblogs.microsoft.com/azure-sql/introducing-mssql-mcp-server/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure AI Agent Service Docs](https://learn.microsoft.com/azure/ai-services/agents/)
- [VS Code SQL Extension](https://marketplace.visualstudio.com/items?itemName=ms-mssql.mssql)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review project documentation in README.md and ARCHITECTURE.md
3. Consult Azure AI Agent Service documentation

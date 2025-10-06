# NL2SQL with MSSQL MCP Server

This implementation uses the **Node.js MSSQL MCP Server** for robust, secure SQL operations.

## Architecture

```
User Question
    ↓
Intent Analyzer (no tools)
    ↓
Schema Agent (with MCP tools: list_table, describe_table)
    ↓
SQL Agent (with MCP tool: read_data - generates & executes SQL)
    ↓
Results Formatter
    ↓
Formatted Output
```

## Setup Instructions

### 1. Build the MSSQL MCP Server

```bash
cd MssqlMcp/Node
npm install
npm run build
```

### 2. Configure MCP Server Environment

Create `MssqlMcp/Node/.env` with your Azure SQL credentials:

```env
# Azure SQL Database Configuration
SERVER_NAME=your-server.database.windows.net
DATABASE_NAME=your-database-name

# Optional settings
TRUST_SERVER_CERTIFICATE=false
CONNECTION_TIMEOUT=30
READONLY=false
```

### 3. Configure Python Environment

Ensure your `python/nl2sql_workflow/.env` has Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
ENABLE_CONSOLE_TRACING=true
```

### 4. Run the Workflow

```bash
cd python/nl2sql_workflow
source ../../.venv/bin/activate  # or ../../.venv/Scripts/activate on Windows
python nl2sql_with_mcp_server.py
```

## How It Works

### MCP Tools Used

1. **list_table** - Lists all tables in the database
   - Parameters: `parameters` (optional array of schema names to filter)
   - Returns: Array of table names (schema.table format)

2. **describe_table** - Gets schema for a specific table
   - Parameters: `tableName` (string)
   - Returns: Array of columns with name and data type

3. **read_data** - Executes SELECT queries with security validation
   - Parameters: `query` (SQL SELECT statement)
   - Returns: Query results
   - Security: Validates queries to prevent SQL injection and destructive operations

### Agent Flow

1. **Intent Analyzer**: Understands what the user wants (no MCP tools needed)

2. **Schema Agent**: 
   - Calls `list_table` to see available tables
   - Calls `describe_table` on relevant tables to understand structure
   - Provides schema mapping for SQL generation

3. **SQL Agent**:
   - Generates SQL Server query based on intent and schema
   - Calls `read_data` tool with the query
   - MCP server validates and executes the query
   - Returns real results to the agent

4. **Results Formatter**: Creates business-friendly summary of actual data

## Advantages of MCP Approach

✅ **Security**: MCP server validates all queries to prevent SQL injection
✅ **Authentication**: Handles Azure AD authentication automatically
✅ **Error Handling**: Proper error messages from MCP server
✅ **SQL Server Syntax**: MCP server ensures correct syntax
✅ **Tool Integration**: Agents can call tools naturally in their workflow
✅ **Separation of Concerns**: SQL logic in MCP server, AI logic in agents

## Troubleshooting

### MCP Server Not Starting

```bash
# Check if MCP server is built
cd MssqlMcp/Node
ls -la dist/

# Rebuild if needed
npm run build

# Test MCP server manually
node dist/index.js
```

### Authentication Issues

The MCP server uses `InteractiveBrowserCredential` which will open a browser for Azure AD authentication. Ensure you have:
- Azure CLI installed and logged in (`az login`)
- Proper permissions to the Azure SQL Database
- Network connectivity to Azure

### Port Already in Use

If port 8099 is in use:
```bash
# Find and kill the process
lsof -ti:8099 | xargs kill -9

# Or change the port in nl2sql_with_mcp_server.py (line with serve_async)
```

## Example Questions

- "Show me all tables in the database"
- "What is the schema of the Company table?"
- "Show me the top 10 companies by employee count"
- "How many active loans do we have?"
- "List customers with credit rating above BBB"

## Comparison with Previous Approach

| Aspect | Previous (Custom) | New (MCP Server) |
|--------|------------------|------------------|
| SQL Execution | pyodbc directly | MCP tool `read_data` |
| Schema Discovery | Manual INFORMATION_SCHEMA queries | MCP tools `list_table`, `describe_table` |
| Security | Basic validation | Comprehensive SQL injection prevention |
| Authentication | Manual token management | Automatic via MCP server |
| Error Handling | Custom try/catch | Structured MCP responses |
| Agent Integration | Custom executors | Native tool calling |
| Syntax Correction | Post-hoc regex fixes | Validation at execution |

The MCP approach is more robust, secure, and maintainable!

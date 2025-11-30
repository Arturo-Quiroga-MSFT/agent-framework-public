# RDBMS Assistant - Quick Start Guide

## ✅ Prerequisites

1. **Python 3.10+** 
2. **Node.js 18+** and npm
3. **Azure CLI** authenticated (`az login`)
4. **Azure AI Project** (Foundry) endpoint
5. **Azure SQL Database** or SQL Server credentials

## 🚀 Installation (5 Minutes)

### Step 1: Install Python Dependencies
```bash
cd /path/to/rdbms-assistant

# Activate virtual environment (or create one)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Build MCP Server
The MSSQL MCP Server is already included in `MssqlMcp/Node`. Build it:

```bash
cd MssqlMcp/Node
npm install
npm run build
cd ../..
```

✅ This creates `MssqlMcp/Node/dist/index.js` which the agent automatically spawns.

### Step 3: Configure Environment
Create a `.env` file in the project root with your settings:

```bash
# Azure AI Project (Required)
AZURE_AI_PROJECT_ENDPOINT=https://your-project.api.azureml.ms

# SQL Server Connection (Required)
SERVER_NAME=your-server.database.windows.net
DATABASE_NAME=your-database
SQL_USERNAME=your-username
SQL_PASSWORD=your-password
TRUST_SERVER_CERTIFICATE=true

# Optional
READONLY=false
```

**Get your Azure AI Project Endpoint:**
1. Open Azure Portal
2. Go to your Azure AI Project (AI Foundry)
3. Copy the endpoint URL from Overview

### Step 4: Authenticate with Azure
```bash
az login
```

### Step 5: Run!
```bash
python dba_assistant.py
```

## 💬 Example Session

```
$ python dba_assistant.py
✓ Loaded environment from: /Users/.../rdbms-assistant/.env

╔══════════════════════════════════════════════════════════════╗
║            Interactive DBA Assistant                         ║
║        Powered by Microsoft Agent Framework                  ║
║              & MSSQL MCP Server                             ║
╚══════════════════════════════════════════════════════════════╝

================================================================================
INTERACTIVE DBA ASSISTANT
Ask questions about your databases in natural language
Type 'exit' to quit
================================================================================

📡 Using server: aqsqlserver001.database.windows.net
📊 Database: TERADATA-FI
⏳ Starting MCP server...

✅ MCP server started
✅ Agent ready
💬 You can now ask questions...

DBA> how many tables are in the database?

🤖 Agent: There are 22 tables in the database. The tables are organized 
under two schemas: "dim" and "fact". Here are the tables:

Under the "dim" schema (dimension tables):
1. DimApplicationStatus
2. DimCollateralType
3. DimCovenantType
4. DimCustomer
5. DimDate
...

Under the "fact" schema (fact tables):
1. FACT_COVENANT_TEST
2. FACT_CUSTOMER_FINANCIALS
3. FACT_CUSTOMER_INTERACTION
...

DBA> show me the top 5 largest tables

🤖 Agent: [Agent queries the database and returns results]

DBA> check for blocking sessions

🤖 Agent: [Agent checks sys.dm_exec_requests for blocking]

DBA> exit
👋 Goodbye!
```

## 🛠️ Try These Questions

```
DBA> how many tables are in the database?
DBA> show me all the dimension tables
DBA> what's the schema of the customers table?
DBA> list all the fact tables
DBA> show me the top 10 largest tables
DBA> check for blocking sessions
DBA> what's the total database size?
DBA> show me index fragmentation
DBA> are there any long-running queries?
```

## 🔧 How It Works

The assistant uses **Microsoft Agent Framework** with **MCPStdioTool** to connect your natural language questions to SQL operations:

```
┌─────────────────────────┐
│   Your NL Question      │
│  "how many tables?"     │
└───────────┬─────────────┘
            │
      ┌─────▼──────┐
      │   Agent    │  Azure AI Agent (GPT-4o)
      │  Reasoning │  Decides which tools to call
      └─────┬──────┘
            │
    ┌───────▼────────┐
    │  MCPStdioTool  │  Spawns Node.js MCP server
    │                │  as subprocess
    └───────┬────────┘
            │
      ┌─────▼─────┐
      │ MCP Server│  Node.js process
      │ (Node.js) │  Handles SQL operations
      └─────┬─────┘
            │
   ┌────────▼──────────┐
   │   Azure SQL DB    │  Your database
   └───────────────────┘
```

**Key Components:**

1. **MCPStdioTool**: Framework's built-in tool that spawns and communicates with MCP servers via stdio
2. **MCP Server**: Node.js process (`MssqlMcp/Node/dist/index.js`) that provides 13 SQL database tools
3. **Agent**: Azure AI Agent that orchestrates tool calls based on your questions

## 📚 Available MCP Tools

The MCP server automatically provides these tools to the agent:

| Tool | Description |
|------|-------------|
| `mssql_connect` | Connect to SQL Server |
| `mssql_disconnect` | Close connection |
| `mssql_list_databases` | List all databases |
| `mssql_list_tables` | List tables in database |
| `mssql_list_views` | List views |
| `mssql_list_functions` | List functions |
| `mssql_list_schemas` | List schemas |
| `mssql_run_query` | Execute SQL queries |
| `mssql_show_schema` | Visualize database schema |
| `mssql_get_connection_details` | Get connection info |
| `mssql_change_database` | Switch databases |

The agent automatically selects the right tools based on your question!

## 🐛 Troubleshooting

### "MCP server not found"
```bash
cd MssqlMcp/Node
npm run build
```

### "Failed to connect to SQL Server"
1. Verify `SERVER_NAME` in `.env`
2. Check SQL Server firewall rules allow your IP
3. Confirm SQL authentication is enabled
4. Test credentials with SSMS or Azure Data Studio

### "AZURE_AI_PROJECT_ENDPOINT not set"
1. Create Azure AI Project in Azure Portal (AI Foundry)
2. Copy the endpoint URL from project Overview
3. Add to `.env` file

### "Azure authentication failed"
```bash
az login
az account show  # Verify you're logged in
```

### MCP Server Logs
The MCP server writes to stderr. To see logs:
```bash
# The agent will show MCP server output in the console
```

## 📖 Documentation

- **[README.md](README.md)** - Full project documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture
- **[SQL_AUTH_SETUP.md](SQL_AUTH_SETUP.md)** - SQL authentication setup
- **[STANDALONE_MCP.md](STANDALONE_MCP.md)** - MCP server internals

## 🎯 What's Next?

1. **Test with real queries**: Ask about your actual database schema
2. **Explore diagnostics**: Try health check queries
3. **Monitor performance**: Ask about slow queries or blocking
4. **Customize**: Add your own system instructions in `dba_assistant.py`

## 💡 Pro Tips

- The agent **maintains conversation context** - follow-up questions work!
- Ask for **explanations**: "Why is this table so large?"
- Request **recommendations**: "How can I improve query performance?"
- Be specific: "Check index fragmentation for tables over 1GB"

---

**Need Help?** Check the full [README.md](README.md) or [ARCHITECTURE.md](ARCHITECTURE.md) for more details.

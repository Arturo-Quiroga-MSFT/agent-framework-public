# NL2SQL Sequential Pipeline Workflow

A complete Natural Language to SQL pipeline built with Azure Agent Framework, featuring 6 specialized agents working sequentially to convert natural language questions into SQL queries and execute them against Azure SQL Database.

## 🎯 What It Does

This workflow takes a natural language question about your database and processes it through 6 sequential stages:

```
User Question
     ↓
1. 🎯 Intent Analyzer ──────→ Understands what user wants
     ↓
2. 📊 Schema Expert ─────────→ Maps intent to database schema
     ↓
3. 💻 SQL Generator ─────────→ Writes optimized SQL query
     ↓
4. ✅ SQL Validator ─────────→ Validates and optimizes SQL
     ↓
5. 🔧 Query Executor ────────→ Executes against Azure SQL DB
     ↓
6. 📝 Results Formatter ─────→ Formats results with insights
     ↓
Formatted Output + Saved Report
```

## 📋 Prerequisites

### 1. Python Dependencies

```bash
pip install pyodbc
```

### 2. Microsoft ODBC Driver for SQL Server

**macOS:**
```bash
brew install unixodbc
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18
```

**Linux (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

**Windows:**
Download and install from [Microsoft's website](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 3. Azure Resources

- **Azure OpenAI**: Deployed GPT-4 model
- **Azure SQL Database**: With SQL authentication enabled
- **Azure CLI**: Logged in (`az login`)

## ⚙️ Configuration

### 1. Create `.env` File

Copy the example and configure:

```bash
cp .env.example .env
```

### 2. Configure Azure OpenAI

```env
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
```

### 3. Configure Azure SQL Database

```env
AZURE_SQL_SERVER="your-server.database.windows.net"
AZURE_SQL_DATABASE="your-database-name"
AZURE_SQL_USERNAME="your-username"
AZURE_SQL_PASSWORD="your-password"
AZURE_SQL_DRIVER="{ODBC Driver 18 for SQL Server}"
```

**Important:** 
- Server name should NOT include `tcp:` prefix
- Use SQL authentication (not Windows/AAD authentication for this version)
- Ensure firewall rules allow your IP address

### 4. Optional: Enable Tracing

```env
# Console tracing (simplest)
ENABLE_CONSOLE_TRACING=true

# Or Azure AI tracing
ENABLE_AZURE_AI_TRACING=true

# Or DevUI tracing
ENABLE_DEVUI_TRACING=true
```

## 🚀 Running the Workflow

```bash
cd /path/to/python/nl2sql_workflow
python nl2sql_sequential_devui.py
```

This will:
1. Test database connection
2. Launch DevUI on `http://localhost:8099`
3. Open browser automatically

## 💡 Example Questions

### Analytics
- "Show me the top 10 customers by total purchase amount"
- "What are the sales trends by month for the last year?"

### Inventory
- "Which products have inventory below 50 units?"
- "List all products that need reordering"

### HR
- "List all employees hired in 2024 with their departments"
- "What is the average salary by department?"

### Finance
- "What is the average order value per customer segment?"
- "Show revenue by product category for Q4 2024"

## 📊 Pipeline Stages Explained

### Stage 1: 🎯 Intent Analyzer
Analyzes the natural language question to identify:
- Primary intent (SELECT, aggregate, filter, etc.)
- Entities mentioned
- Conditions/filters requested
- Required aggregations
- Expected output format

### Stage 2: 📊 Schema Expert
Maps the intent to database schema:
- Identifies relevant tables
- Selects specific columns
- Determines JOIN relationships
- Considers indexes for performance
- Notes schema limitations

### Stage 3: 💻 SQL Generator
Writes optimized SQL query:
- Complete executable SQL
- Proper JOINs and WHERE clauses
- Aggregations and calculations
- Best practices (aliases, formatting)
- Performance considerations

### Stage 4: ✅ SQL Validator
Validates and optimizes:
- Checks syntax correctness
- Verifies intent alignment
- Identifies potential issues
- Suggests optimizations
- Provides final validated SQL

### Stage 5: 🔧 Query Executor
Executes the query:
- Extracts validated SQL
- Executes against Azure SQL DB
- Handles errors and timeouts
- Returns result set
- Notes execution metadata

### Stage 6: 📝 Results Formatter
Formats final output:
- Natural language summary
- Plain English explanation of SQL
- Expected results format
- Business insights
- Limitations and caveats

## 📁 Output Files

Results are automatically saved to:
```
workflow_outputs/nl2sql_pipeline_YYYYMMDD_HHMMSS.txt
```

Each file contains:
- Original question
- All 6 pipeline stages
- Complete conversation history
- Formatted insights

## 🔍 DevUI Visualization

The DevUI interface shows 3 executors:
1. **input_dispatcher** - Handles input conversion
2. **nl2sql_pipeline** - Runs all 6 agents sequentially (internally)
3. **output_formatter** - Formats final output

The 6 agents run inside the `nl2sql_pipeline` executor, maintaining full conversation history.

## 🛠️ Troubleshooting

### Database Connection Issues

**Error:** "Unable to connect to database"

**Solutions:**
1. Verify server name format (no `tcp:` prefix)
2. Check SQL authentication is enabled
3. Confirm firewall allows your IP
4. Test connection string with Azure Data Studio
5. Verify ODBC driver is installed

```bash
# Test ODBC drivers on macOS/Linux
odbcinst -q -d
```

### Missing pyodbc Module

**Error:** "ImportError: No module named 'pyodbc'"

**Solution:**
```bash
pip install pyodbc
```

### ODBC Driver Not Found

**Error:** "Data source name not found and no default driver specified"

**Solution:**
- Install Microsoft ODBC Driver 18 (see Prerequisites)
- Update `AZURE_SQL_DRIVER` in `.env` if using different version

### Schema Retrieval Fails

The workflow will continue with a simulated schema if retrieval fails. To fix:
1. Check database user has read permissions on `INFORMATION_SCHEMA`
2. Verify database name is correct
3. Check network connectivity

## 🔐 Security Notes

- Never commit `.env` file to source control
- Use strong passwords for SQL authentication
- Consider using Azure AD authentication in production
- Restrict firewall rules to specific IP addresses
- Rotate credentials regularly

## 📚 Additional Resources

- [Azure SQL Database Documentation](https://learn.microsoft.com/en-us/azure/azure-sql/)
- [Azure Agent Framework](https://github.com/microsoft/azure-ai-agent-service)
- [Microsoft ODBC Driver Documentation](https://learn.microsoft.com/en-us/sql/connect/odbc/)
- [DevUI Guide](../samples/getting_started/workflows/README.md)

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Support for Azure AD authentication
- Query result caching
- Multiple database connections
- Query history and favorites
- Result visualization (charts/graphs)
- Advanced error handling and retry logic

## 📄 License

Copyright (c) Microsoft. All rights reserved.

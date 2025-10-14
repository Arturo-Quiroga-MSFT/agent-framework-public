# NL2SQL Pipeline - Quick Start Guide

Get up and running with the NL2SQL workflow in 5 minutes.

## Step 1: Prerequisites Check

Ensure you have:
- ✅ Azure OpenAI endpoint and deployment
- ✅ Azure SQL Database with accessible data
- ✅ Azure CLI installed and authenticated (`az login`)
- ✅ Python 3.10+ virtual environment activated

## Step 2: Configure Environment

Edit the `.env` file in this directory:

```env
# Required: Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Required: MSSQL Connection (Option A or B)

# Option A: Use existing connection ID
MSSQL_CONNECTION_ID=your-connection-id

# Option B: Auto-connect with server details
MSSQL_SERVER_NAME=your-server.database.windows.net
MSSQL_DATABASE_NAME=your-database

# Optional: Tracing
ENABLE_CONSOLE_TRACING=true
```

## Step 3: Test MSSQL Connection

```bash
# Activate virtual environment
cd /Users/arturoquiroga/GITHUB/agent-framework-public
source .venv/bin/activate

# Test connection
python -c "
from mssql_list_servers import mssql_list_servers
print('Available servers:', mssql_list_servers())
"
```

## Step 4: Launch Workflow

```bash
python nl2sql-pipeline/nl2sql_workflow.py
```

The DevUI will open automatically at `http://localhost:8097`

## Step 5: Try Example Questions

In the DevUI interface, try these questions:

### Basic Queries
```
What are the top 10 rows from the Customers table?
```

### Aggregations
```
How many orders were placed last month?
```

### Joins
```
Show me customers who placed orders over $1000
```

### Analytics
```
What's the average order value by product category?
```

## Troubleshooting

### "Cannot connect to database"

1. Check firewall rules allow your IP
2. Verify credentials: `az account show`
3. Test connection: `az sql db show --name DB_NAME --server SERVER_NAME`

### "No SQL generated"

1. Check Azure OpenAI endpoint is correct
2. Verify deployment name matches
3. Check token limits in Azure OpenAI

### "Query execution failed"

1. Review SQL in validator output
2. Check database permissions
3. Verify table/column names exist

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🔧 Customize executors in [executors.py](executors.py)
- 📊 Review [examples/](examples/) for advanced patterns
- 🎯 Add custom validators for your use case

## Tips

💡 **Schema Discovery**: The workflow automatically discovers your database schema - no manual configuration needed!

💡 **Safety First**: By default, only SELECT queries are allowed. Edit `SQLValidatorExecutor(allow_write=True)` to enable writes.

💡 **Row Limits**: Queries are automatically limited to 1000 rows. Adjust in `SQLValidatorExecutor(max_rows=5000)`.

💡 **Tracing**: Enable console tracing to see each pipeline step: `ENABLE_CONSOLE_TRACING=true`

## Support

For issues, check:
- Pipeline logs in console output
- DevUI trace viewer
- MSSQL connection status
- Azure OpenAI quota and limits

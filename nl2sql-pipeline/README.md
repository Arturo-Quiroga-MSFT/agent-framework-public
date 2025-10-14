# NL2SQL Pipeline - Natural Language to SQL Workflow

A production-ready sequential workflow that converts natural language questions into SQL queries, executes them against Azure SQL Database, and returns intelligent insights.

## Architecture

**Pattern**: Sequential Pipeline with Agents + Business Logic Executors

```
User Question
    ↓
[1] Input Normalizer (Executor)
    ↓
[2] Schema Retriever (Executor) ──→ MSSQL MCP Tools
    ↓
[3] SQL Generator Agent (LLM)
    ↓
[4] SQL Validator (Executor)
    ↓
[5] Query Executor (Executor) ──→ MSSQL Database
    ↓
[6] Results Interpreter Agent (LLM)
    ↓
Natural Language Answer + Insights
```

## Features

✅ **Natural Language Interface** - Ask questions in plain English  
✅ **Automatic Schema Discovery** - Retrieves relevant tables and columns  
✅ **SQL Safety Validation** - Prevents destructive operations  
✅ **Error Recovery** - Automatically retries with corrected queries  
✅ **Azure SQL Integration** - Real database connectivity with pyodbc  
✅ **DevUI Interface** - Visual testing and debugging  
✅ **Full Observability** - Traces every pipeline step  
✅ **Export Results** - Automatic CSV and Excel export with formatting  
✅ **Table Formatting** - Beautiful ASCII tables for readability  
✅ **Schema Caching** - 100-500x faster with intelligent caching (< 1ms vs 500ms)  
✅ **Data Visualization** - Automatic chart generation (bar, line, pie charts)  

## Prerequisites

1. **Azure OpenAI** - Configured endpoint and deployment
2. **Azure SQL Database** - Accessible database with connection configured
3. **MSSQL MCP Server** - Available in framework (built-in)
4. **Python 3.10+** - With agent framework installed
5. **Authentication** - `az login` completed

## Setup

### 1. Environment Configuration

The `.env` file in this directory should contain:

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# MSSQL Connection
MSSQL_SERVER_NAME=your-server.database.windows.net
MSSQL_DATABASE_NAME=your-database
MSSQL_CONNECTION_ID=<obtained-from-mssql-connect>

# Optional: Tracing
ENABLE_CONSOLE_TRACING=true
# OR
OTLP_ENDPOINT=http://localhost:4317
# OR
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

### 2. Database Setup

Ensure your Azure SQL Database has:
- Tables with proper schemas
- Read permissions for the authenticated user
- Firewall rules allowing your IP

### 3. Install Dependencies

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public
source .venv/bin/activate
pip install -r python/packages/core/requirements.txt

# Install additional dependencies for this pipeline
pip install pyodbc openpyxl matplotlib seaborn
```

## Usage

### Launch DevUI Interface

```bash
python nl2sql-pipeline/nl2sql_workflow.py
```

Access at: `http://localhost:8097`

### Example Questions

- "What are the top 10 customers by revenue?"
- "Show me all orders from last month"
- "How many products are out of stock?"
- "What's the average order value by region?"
- "List employees hired in 2024"

## Pipeline Components

### 1. Input Normalizer
- Parses user input
- Validates question format
- Extracts intent

### 2. Schema Retriever
- Connects to MSSQL database
- Identifies relevant tables/columns
- Provides schema context to LLM

### 3. SQL Generator Agent
- LLM-powered SQL generation
- Schema-aware query construction
- Handles complex joins and aggregations

### 4. SQL Validator
- Syntax validation
- Safety checks (prevents DROP, DELETE, ALTER)
- Permission verification
- Query cost estimation

### 5. Query Executor
- Executes SQL against database
- Handles errors and retries
- Returns structured results
- Pagination for large datasets

### 6. Results Interpreter Agent
- Converts tabular data to natural language
- Generates insights and patterns
- Suggests follow-up questions
- Handles empty results gracefully

## Safety Features

🛡️ **Query Whitelisting** - Only SELECT statements by default  
🛡️ **Write Confirmation** - INSERT/UPDATE/DELETE require explicit approval  
🛡️ **Row Limits** - Automatic LIMIT/TOP clause for large queries  
🛡️ **Schema Isolation** - Only accesses configured schemas  
🛡️ **Error Handling** - Graceful failures with retry logic  

## Configuration Options

### Query Limits

```python
MAX_ROWS = 1000  # Maximum rows returned
QUERY_TIMEOUT = 30  # Seconds
```

### Allowed Operations

```python
ALLOWED_OPERATIONS = ["SELECT"]  # Add "INSERT", "UPDATE" for write access
```

### Schema Scope

```python
ALLOWED_SCHEMAS = ["dbo", "sales"]  # Restrict to specific schemas
```

## Observability

### Tracing

Each pipeline step emits structured traces:
- Schema retrieval time
- SQL generation prompt/response
- Query execution time
- Result size and structure

### Metrics

- Query success/failure rate
- Average execution time
- Token usage per query
- Error types and frequencies

## Troubleshooting

### Connection Issues

```bash
# Test MSSQL connection
python -c "from mssql_list_servers import *; print(mssql_list_servers())"
```

### SQL Generation Failures

- Check schema context in traces
- Verify LLM has access to correct tables
- Review prompt engineering in SQL Generator

### Query Execution Errors

- Verify database permissions
- Check firewall rules
- Review SQL syntax in validator output

## Extending the Pipeline

### Add Custom Validators

```python
class CustomValidator(Executor):
    @handler
    async def validate(self, sql: str, ctx: WorkflowContext[str]) -> None:
        # Your validation logic
        await ctx.send_message(sql)
```

### Add Query Optimization

```python
class QueryOptimizer(Executor):
    @handler
    async def optimize(self, sql: str, ctx: WorkflowContext[str]) -> None:
        # Add indexes, rewrite joins, etc.
        await ctx.send_message(optimized_sql)
```

### Add Result Visualization

```python
class ChartGenerator(Executor):
    @handler
    async def generate_chart(self, results: dict, ctx: WorkflowContext[str]) -> None:
        # Generate charts, graphs, etc.
        await ctx.send_message(chart_config)
```

## Examples

See `examples/` directory for:
- Basic queries
- Complex aggregations
- Multi-table joins
- Error recovery scenarios
- Custom validator implementations

## Additional Documentation

- **[SCHEMA_CACHE_GUIDE.md](SCHEMA_CACHE_GUIDE.md)** - Schema caching for 100-500x performance improvement
- **[VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md)** - Automatic chart generation and customization
- **[WEATHER_API_GUIDE.md](../AQ-CODE/azure_ai/WEATHER_API_GUIDE.md)** - Weather API integration (if needed)

## License

See repository LICENSE file.

## Support

For issues or questions, refer to the main agent-framework documentation.

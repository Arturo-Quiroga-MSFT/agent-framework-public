# NL2SQL Configuration Reference

Complete guide to configuring and customizing the NL2SQL pipeline.

## Environment Variables

### Required Variables

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### MSSQL Connection (Choose One Method)

#### Method A: Existing Connection ID
```env
MSSQL_CONNECTION_ID=uuid-string-from-previous-connection
```

#### Method B: Auto-Connect
```env
MSSQL_SERVER_NAME=your-server.database.windows.net
MSSQL_DATABASE_NAME=your-database-name
```

### Optional: Tracing & Observability

#### Console Tracing (Simplest)
```env
ENABLE_CONSOLE_TRACING=true
```

#### OTLP Endpoint (Jaeger, Zipkin)
```env
OTLP_ENDPOINT=http://localhost:4317
```

#### Application Insights
```env
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

#### DevUI Tracing
```env
ENABLE_DEVUI_TRACING=true
```

## Workflow Configuration

### Pipeline Components

Edit `nl2sql_workflow.py` to customize:

#### 1. SQL Generator Agent Instructions

```python
sql_generator = client.create_agent(
    instructions="""Your custom instructions here...""",
    name="sql_generator",
)
```

**Customization Tips:**
- Add domain-specific SQL patterns
- Include company-specific naming conventions
- Add examples of complex queries
- Specify preferred SQL style (ANSI vs T-SQL)

#### 2. Results Interpreter Agent Instructions

```python
results_interpreter = client.create_agent(
    instructions="""Your custom instructions here...""",
    name="results_interpreter",
)
```

**Customization Tips:**
- Add business context for data interpretation
- Specify KPI definitions
- Include threshold values for alerts
- Define what constitutes "interesting" insights

### Executor Configuration

#### Input Normalizer

```python
input_normalizer = InputNormalizerExecutor(
    id="input_normalizer"  # Custom ID for tracing
)
```

#### Schema Retriever

```python
schema_retriever = SchemaRetrieverExecutor(
    connection_id=connection_id,
    id="schema_retriever"
)
```

**Future Enhancements:**
- Add schema caching
- Filter tables by prefix/pattern
- Include column descriptions from metadata

#### SQL Validator

```python
sql_validator = SQLValidatorExecutor(
    max_rows=1000,        # Maximum rows per query
    allow_write=False,    # Enable INSERT/UPDATE/DELETE
    id="sql_validator"
)
```

**Security Options:**
- `max_rows`: Prevent large result sets (default: 1000)
- `allow_write`: Enable write operations (default: False)
- Add custom validation rules in `executors.py`

#### Query Executor

```python
query_executor = QueryExecutorExecutor(
    connection_id=connection_id,
    id="query_executor"
)
```

**Performance Options:**
- Add query timeout
- Implement result caching
- Add query plan analysis

## Custom Validators

### Add Domain-Specific Rules

Edit `executors.py` → `SQLValidatorExecutor`:

```python
def _check_safety(self, sql: str) -> tuple[bool, list[str]]:
    warnings = []
    sql_upper = sql.upper()
    
    # Your custom rules
    if "SENSITIVE_TABLE" in sql_upper:
        warnings.append("❌ Access to sensitive table denied")
        return False, warnings
    
    # Require specific columns
    if "SELECT *" in sql_upper:
        warnings.append("⚠️  SELECT * discouraged, specify columns")
    
    # Check join complexity
    join_count = sql_upper.count("JOIN")
    if join_count > 5:
        warnings.append(f"⚠️  Complex query with {join_count} joins")
    
    return True, warnings
```

### Add Cost Estimation

```python
def _estimate_cost(self, sql: str) -> dict:
    """Estimate query cost before execution."""
    # Check for expensive operations
    has_full_scan = "SELECT *" in sql.upper()
    has_sort = "ORDER BY" in sql.upper()
    has_aggregate = any(kw in sql.upper() for kw in ["SUM", "AVG", "COUNT"])
    
    cost_score = 0
    if has_full_scan: cost_score += 3
    if has_sort: cost_score += 2
    if has_aggregate: cost_score += 1
    
    return {
        "score": cost_score,
        "category": "high" if cost_score > 4 else "medium" if cost_score > 2 else "low"
    }
```

## Schema Filtering

### Restrict to Specific Schemas

Edit `SchemaRetrieverExecutor._format_schema_context()`:

```python
def _format_schema_context(self, conn_details: dict, schemas: list, tables: list) -> str:
    # Filter schemas
    allowed_schemas = ["dbo", "sales", "marketing"]
    schemas = [s for s in schemas if s in allowed_schemas]
    
    # Filter tables
    tables = [t for t in tables if t.get("schema") in allowed_schemas]
    
    # ... rest of formatting
```

### Add Table Descriptions

```python
TABLE_DESCRIPTIONS = {
    "Customers": "Customer master data including demographics",
    "Orders": "Transaction records with order details",
    "Products": "Product catalog with pricing and inventory",
}

def _format_schema_context(self, ...):
    lines.append("Table Descriptions:")
    for table_name, description in TABLE_DESCRIPTIONS.items():
        lines.append(f"  {table_name}: {description}")
```

## Result Formatting

### Custom Result Presentation

Edit `QueryExecutorExecutor._format_results()`:

```python
def _format_results(self, result: dict, execution_time: float) -> str:
    lines = ["QUERY RESULTS:", ""]
    
    # Add custom metadata
    lines.append(f"⏱️  Execution Time: {execution_time:.2f}ms")
    lines.append(f"📊 Rows Returned: {result.get('rowCount', 0)}")
    
    # Add performance indicators
    if execution_time > 1000:
        lines.append("⚠️  Slow query - consider optimization")
    
    # Format data with custom styling
    rows = result.get("rows", [])
    if rows:
        # Create markdown table
        columns = list(rows[0].keys())
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        
        for row in rows[:20]:  # Show more rows
            values = [str(row.get(col, "")) for col in columns]
            lines.append("| " + " | ".join(values) + " |")
    
    return "\n".join(lines)
```

## Error Recovery

### Add Retry Logic

```python
class QueryExecutorExecutor(Executor):
    def __init__(self, connection_id: str, max_retries: int = 3, id: str = "query_executor"):
        super().__init__(id=id)
        self.connection_id = connection_id
        self.max_retries = max_retries
    
    @handler
    async def execute(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]) -> None:
        for attempt in range(self.max_retries):
            try:
                # Execute query
                result = self._execute_query(sql)
                break
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Query failed, retry {attempt + 1}/{self.max_retries}")
                    await asyncio.sleep(1)
                else:
                    raise
```

## Performance Tuning

### Enable Query Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def _get_cached_schema(connection_id: str) -> dict:
    """Cache schema information to reduce database calls."""
    schemas = mssql_list_schemas(connection_id=connection_id)
    tables = mssql_list_tables(connection_id=connection_id)
    return {"schemas": schemas, "tables": tables}
```

### Parallel Schema Retrieval

```python
async def retrieve_schema_async(self, ...):
    # Fetch schemas and tables in parallel
    schemas_task = asyncio.to_thread(mssql_list_schemas, connection_id=self.connection_id)
    tables_task = asyncio.to_thread(mssql_list_tables, connection_id=self.connection_id)
    
    schemas, tables = await asyncio.gather(schemas_task, tables_task)
```

## Deployment Options

### Production Settings

```env
# Production configuration
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4        # More reliable
MAX_ROWS=500                               # Conservative limit
ALLOW_WRITE=false                          # Read-only by default
QUERY_TIMEOUT=30                           # 30 second timeout
ENABLE_CONSOLE_TRACING=false              # Disable console noise
APPLICATIONINSIGHTS_CONNECTION_STRING=... # Production monitoring
```

### Development Settings

```env
# Development configuration
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o       # Faster for testing
MAX_ROWS=100                               # Smaller results
ALLOW_WRITE=true                           # Enable testing writes
ENABLE_CONSOLE_TRACING=true               # Debug output
ENABLE_DEVUI_TRACING=true                 # Visual debugging
```

## Advanced Customizations

### Add Query Optimization Step

Create a new executor between validator and executor:

```python
class QueryOptimizerExecutor(Executor):
    @handler
    async def optimize(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]) -> None:
        sql = self._extract_sql(message.text)
        
        # Add indexes hint
        if "JOIN" in sql.upper():
            sql = f"-- Consider indexes on join columns\n{sql}"
        
        # Rewrite inefficient patterns
        sql = sql.replace("SELECT *", "SELECT <columns>")
        
        await ctx.send_message(ChatMessage(Role.SYSTEM, text=sql))
```

Then add to pipeline:

```python
builder.participants([
    input_normalizer,
    schema_retriever,
    sql_generator,
    sql_validator,
    query_optimizer,  # ← New step
    query_executor,
    results_interpreter,
])
```

### Add Visualization Suggestions

Extend results interpreter agent instructions:

```python
instructions="""...

Also suggest appropriate visualizations:
- Bar chart for categorical comparisons
- Line chart for time series
- Pie chart for proportions
- Scatter plot for correlations

Format: **Visualization:** [chart type] showing [x-axis] vs [y-axis]
"""
```

## Monitoring & Alerting

### Log Important Metrics

```python
import logging
logger = logging.getLogger(__name__)

# In QueryExecutor
logger.info(f"Query executed: {sql[:100]}...")
logger.info(f"Execution time: {execution_time:.2f}ms")
logger.info(f"Rows returned: {row_count}")

if execution_time > 5000:
    logger.warning(f"Slow query detected: {execution_time:.2f}ms")
```

### Track Query Patterns

```python
# Add to QueryExecutorExecutor
self.query_stats = {
    "total_queries": 0,
    "avg_execution_time": 0,
    "failed_queries": 0,
}

# Update after each query
self.query_stats["total_queries"] += 1
# ... calculate running average
```

## Security Considerations

### Row-Level Security

```python
# Add user context to queries
def _inject_user_filter(self, sql: str, user_id: str) -> str:
    # Append WHERE clause for user data isolation
    if "WHERE" in sql.upper():
        sql = sql.replace("WHERE", f"WHERE UserID = '{user_id}' AND")
    else:
        sql += f" WHERE UserID = '{user_id}'"
    return sql
```

### Audit Logging

```python
# Log all queries for compliance
def _audit_log(self, sql: str, user: str, result: dict):
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "query": sql,
        "rows_returned": result.get("rowCount", 0),
    }
    logger.info(f"AUDIT: {audit_entry}")
```

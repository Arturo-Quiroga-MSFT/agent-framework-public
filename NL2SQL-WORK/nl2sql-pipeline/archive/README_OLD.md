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
[7] Data Exporter (Executor) ──→ CSV & Excel Files
    ↓
[8] Visualization Generator (Executor) ──→ Charts & Graphs
    ↓
Natural Language Answer + Insights + Files + Visualizations
```

## Features

✅ **Natural Language Interface** - Ask questions in plain English  
✅ **Automatic Schema Discovery** - Retrieves relevant tables and columns  
✅ **SQL Safety Validation** - Prevents destructive operations  
✅ **Error Recovery** - Automatically retries with corrected queries  
✅ **Azure SQL Integration** - Real database connectivity with pyodbc  
✅ **DevUI Interface** - Visual testing and debugging  
✅ **Full Observability** - Traces every pipeline step  
✅ **Schema Caching** - 100-500x faster with intelligent caching (< 1ms vs 500ms)  
✅ **Data Export** - Automatic CSV and Excel (XLSX) export with timestamps  
✅ **Smart Visualizations** - Auto-generates appropriate charts based on data type  
  - Horizontal bar charts for top-N analyses  
  - Line charts for time series and trends  
  - Pie charts for category distributions  
  - Heatmaps for correlation matrices  
✅ **Table Formatting** - Beautiful ASCII tables for readability  
✅ **File Management** - Organized exports/ and visualizations/ directories  

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
pip install pyodbc openpyxl matplotlib seaborn pandas
```

## Usage

### Launch DevUI Interface

```bash
python nl2sql-pipeline/nl2sql_workflow.py
```

Access at: `http://localhost:8097`

### Demo Questions

#### 📊 Analytics & Aggregations (Great for Visualizations)
- "What are the top 10 customers by revenue?"
- "Show me sales by product category"
- "What's the revenue trend by month this year?"
- "Which regions have the highest order volume?"
- "What are the top 5 best-selling products?"
- "Show me employee count by department"

#### 🔍 Data Exploration
- "Show me all orders from last month"
- "List all active customers"
- "What products are currently in stock?"
- "Show me recent transactions"
- "List employees hired in 2024"

#### 📈 Time Series & Trends
- "Show me daily sales for the past 30 days"
- "What's the monthly revenue trend this year?"
- "How has customer growth changed over time?"
- "Show me order volume by week"

#### 💰 Financial Analysis
- "What's the average order value by region?"
- "Show me total revenue by quarter"
- "Which products have the highest profit margins?"
- "What's the customer lifetime value distribution?"

#### 🏆 Rankings & Comparisons
- "Who are the top 10 sales representatives?"
- "Which stores have the lowest performance?"
- "Compare sales across different categories"
- "Rank products by customer satisfaction"

#### ❓ Counts & Summaries
- "How many products are out of stock?"
- "How many orders were placed today?"
- "What's the total number of customers?"
- "Count orders by status"

**💡 Tip**: Questions about rankings, trends, and distributions automatically generate visualizations!

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

### 7. Data Exporter
- Exports results to CSV format
- Exports results to Excel (XLSX) with formatting
- Timestamp-based filenames (e.g., `query_results_20251124_143022.csv`)
- Saves to `exports/` directory
- Preserves data types and null values
- Handles large datasets efficiently

### 8. Visualization Generator
- Analyzes data characteristics automatically
- Selects appropriate chart types:
  - **Horizontal Bar Charts**: Rankings, top-N lists, category comparisons
  - **Line Charts**: Time series, trends over time
  - **Pie Charts**: Proportions and distributions (when ≤8 categories)
  - **Heatmaps**: Correlation matrices, multi-dimensional data
- Generates publication-quality charts
- Saves to `visualizations/` directory as PNG
- Smart labeling and formatting
- Handles edge cases (empty data, single values)

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

## Output Files

The pipeline automatically generates three types of outputs:

### 1. CSV Exports
- Location: `exports/query_results_YYYYMMDD_HHMMSS.csv`
- Format: Standard CSV with headers
- Use case: Data analysis in Excel, Python, R
- Features: Preserves all data types

### 2. Excel Exports
- Location: `exports/query_results_YYYYMMDD_HHMMSS.xlsx`
- Format: Excel workbook with formatting
- Use case: Business reporting, presentations
- Features: Styled headers, auto-sized columns

### 3. Visualizations
- Location: `visualizations/viz_YYYYMMDD_HHMMSS.png`
- Format: High-resolution PNG images
- Use case: Reports, dashboards, presentations
- Features: Professional styling, clear labels

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

### Customize Visualizations

The `VisualizationGeneratorExecutor` can be extended to add new chart types:

```python
class CustomChartGenerator(VisualizationGeneratorExecutor):
    def _create_custom_chart(self, df, ax):
        # Add your custom matplotlib/seaborn code
        sns.violinplot(data=df, ax=ax)
        return "violin"
```

## Examples

See `examples/` directory for:
- Basic queries
- Complex aggregations
- Multi-table joins
- Error recovery scenarios
- Custom validator implementations

## Additional Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture and data flow
- **[SCHEMA_CACHE_GUIDE.md](SCHEMA_CACHE_GUIDE.md)** - Schema caching for 100-500x performance improvement
- **[VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md)** - Automatic chart generation and customization

## Demo Tips

### Best Questions for Visualizations
1. **Rankings**: "Show me top 10..." → Horizontal bar chart
2. **Trends**: "Show monthly sales..." → Line chart
3. **Distributions**: "Sales by category" → Pie chart (if ≤8 categories) or bar chart
4. **Comparisons**: "Compare revenue across regions" → Bar chart

### File Access
- CSV/Excel files: Check `exports/` directory
- Visualizations: Check `visualizations/` directory
- Files are timestamped for easy tracking

### Performance Tips
- Schema caching makes repeat queries 100-500x faster
- First query: ~500ms for schema retrieval
- Subsequent queries: <1ms (cached)
- Cache auto-refreshes every 5 minutes

## License

See repository LICENSE file.

## Support

For issues or questions, refer to the main agent-framework documentation.

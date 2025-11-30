# 🎯 NL2SQL-WORK Directory

> **Three deployment variants** of the production-ready NL2SQL (Natural Language to SQL) workflow pipeline built with Microsoft Agent Framework.

**Created**: October 2025  
**Last Updated**: November 30, 2025  
**Framework**: Microsoft Agent Framework  
**Status**: ✅ Production Ready  

---

## 📁 Directory Overview

This directory contains three implementations of the same NL2SQL pipeline, each optimized for different deployment scenarios:

```
NL2SQL-WORK/
├── nl2sql-pipeline/        # Core implementation with DevUI web interface
├── nl2sql-cli/             # CLI-only version (no web UI)
└── nl2sql-gradio/          # Gradio chat interface variant
```

---

## 🚀 What is the NL2SQL Pipeline?

A **production-ready sequential workflow** that:
1. Takes natural language questions from users
2. Automatically discovers your database schema
3. Generates safe SQL queries using Azure OpenAI GPT-4
4. Executes queries against Azure SQL Database
5. Interprets results with natural language insights
6. Exports data to CSV/Excel automatically
7. Generates smart visualizations (charts) automatically

### Key Features Across All Variants

✅ **Natural Language Interface** - Ask questions in plain English  
✅ **Automatic Schema Discovery** - No manual configuration needed  
✅ **Schema Caching** - 100-500x performance improvement  
✅ **SQL Safety** - Prevents destructive operations (DROP, DELETE, ALTER)  
✅ **Error Recovery** - Automatic retry with LLM-corrected queries  
✅ **Data Export** - Automatic CSV & Excel with timestamps  
✅ **Smart Visualizations** - Auto-selects appropriate chart types  
✅ **Full Observability** - Traces, OTLP, Application Insights support  
✅ **Production Ready** - Error handling, validation, security built-in  

---

## 📦 Three Variants Explained

### 1. 🌐 nl2sql-pipeline/ (DevUI Web Interface)

**Best for**: Development, testing, full observability

**Features**:
- Web-based DevUI interface on `http://localhost:8097`
- Real-time trace viewing of all pipeline steps
- Visual inspection of LLM prompts and responses
- Session management and conversation history
- Full workflow visualization

**Quick Start**:
```bash
cd nl2sql-pipeline
python nl2sql_workflow.py
# Opens DevUI at http://localhost:8097
```

**Use Cases**:
- Development and testing
- Debugging SQL generation issues
- Training and demonstrations
- Understanding pipeline flow
- Monitoring LLM behavior

**Documentation**: [nl2sql-pipeline/README.md](nl2sql-pipeline/README.md)

---

### 2. ⚡ nl2sql-cli/ (Command Line Interface)

**Best for**: Production deployments, automation, scripting

**Features**:
- Pure CLI interface - no web server
- Faster startup (no DevUI overhead)
- Direct command-line arguments
- Scriptable and automatable
- Same pipeline logic as DevUI version
- Session support for follow-up questions

**Quick Start**:
```bash
cd nl2sql-cli
python nl2sql_workflow.py "What are the top 10 customers by revenue?"

# With session for follow-ups
python nl2sql_workflow.py "Show me customers" session1
python nl2sql_workflow.py "What about their revenue?" session1
```

**Use Cases**:
- Production deployments
- Scheduled queries / cron jobs
- Azure Functions
- Container deployments (ACI, AKS)
- CI/CD pipelines
- Shell scripts and automation

**Documentation**: [nl2sql-cli/README.md](nl2sql-cli/README.md)

---

### 3. 💬 nl2sql-gradio/ (Chat Interface)

**Best for**: Interactive demos, user-facing applications

**Features**:
- Modern chat UI with conversation flow
- Inline visualization display
- Click-to-download exports (CSV/Excel)
- Query suggestions after each response
- Session-based conversations
- Beautiful, user-friendly interface

**Quick Start**:
```bash
cd nl2sql-gradio
pip install gradio
python app.py
# Opens browser at http://localhost:7860
```

**Use Cases**:
- End-user applications
- Interactive demos and presentations
- Non-technical user access
- Data exploration tools
- Business intelligence dashboards

**Documentation**: [nl2sql-gradio/README.md](nl2sql-gradio/README.md)

---

## 🏗️ Pipeline Architecture

All three variants share the same core architecture:

**Pattern**: Sequential Pipeline combining LLM Agents + Custom Executors

```
User Question (Natural Language)
    ↓
[1] Input Normalizer (Executor)
    ↓ Parse & structure input
    ↓
[2] Schema Retriever (Executor) ──→ Azure SQL Database
    ↓ [Schema cached for 100-500x speedup]
    ↓
[3] SQL Generator Agent (LLM) ──→ Azure OpenAI GPT-4
    ↓ Generate SQL from question + schema
    ↓
[4] SQL Validator (Executor)
    ↓ Safety checks & optimization
    ↓
[5] Query Executor (Executor) ──→ Azure SQL Database
    ↓ Execute validated query
    ↓
[6] Results Interpreter Agent (LLM) ──→ Azure OpenAI GPT-4
    ↓ Natural language insights
    ↓
[7] Data Exporter (Executor) ──→ CSV & Excel Files
    ↓ Timestamped exports
    ↓
[8] Visualization Generator (Executor) ──→ PNG Charts
    ↓ Smart chart selection & rendering
    ↓
Natural Language Answer + Insights + Data Files + Charts
```

### Shared Components

All variants include the same core files:
- `nl2sql_workflow.py` - Main workflow orchestration
- `executors.py` - Custom business logic executors
- `schema_cache.py` - Performance caching implementation
- `visualizer.py` - Chart generation logic
- `db_utils.py` - Database utility functions
- `requirements.txt` - Python dependencies
- `.env` / `.env.example` - Configuration

---

## ⚙️ Configuration

All three variants share configuration through `.env` files:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure SQL Database Configuration
MSSQL_SERVER_NAME=your-server.database.windows.net
MSSQL_DATABASE_NAME=your-database
MSSQL_CONNECTION_ID=<obtained-from-mssql-connect>

# Optional: Schema Caching (default: enabled)
ENABLE_SCHEMA_CACHE=true
SCHEMA_CACHE_TTL=300  # 5 minutes

# Optional: Query Safety (default: read-only)
ALLOW_WRITE_OPERATIONS=false
MAX_RESULT_ROWS=1000

# Optional: Tracing/Observability
ENABLE_CONSOLE_TRACING=true
# OR
OTLP_ENDPOINT=http://localhost:4317
# OR
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

**Configuration is shared** - you can copy `.env` between variants.

---

## 🚦 Quick Start Guide

### Prerequisites

1. **Azure Services**:
   - Azure OpenAI with GPT-4 deployment
   - Azure SQL Database with sample data
   - Azure CLI authenticated (`az login`)

2. **Python Environment**:
   ```bash
   # From repository root
   cd /Users/arturoquiroga/GITHUB/agent-framework-public
   source .venv/bin/activate
   ```

3. **Configuration**:
   ```bash
   cd NL2SQL-WORK/nl2sql-pipeline  # or nl2sql-cli or nl2sql-gradio
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Choose Your Variant

**For Development & Testing**:
```bash
cd nl2sql-pipeline
python nl2sql_workflow.py
# Opens DevUI at http://localhost:8097
```

**For Production & Automation**:
```bash
cd nl2sql-cli
python nl2sql_workflow.py "Your question here"
```

**For User-Facing Applications**:
```bash
cd nl2sql-gradio
python app.py
# Opens chat UI at http://localhost:7860
```

---

## 💡 Example Questions

Try these across any variant:

### Basic Queries
```
"Show me all customers from California"
"List all products with price greater than $100"
"What orders were placed in the last 7 days?"
```

### Analytics & Aggregations
```
"What are the top 10 customers by revenue?" → Bar chart
"Show me monthly sales trends for 2024" → Line chart
"Sales breakdown by category" → Pie chart
"Which regions have the highest order volume?" → Bar chart
```

### Trends & Time Series
```
"Show me daily sales for the past 30 days" → Line chart
"What's the revenue trend by quarter?" → Line chart
"How has customer growth changed over time?" → Line chart
```

### Complex Queries
```
"Compare year-over-year sales growth by product category"
"Show me customer lifetime value distribution by segment"
"Which sales representatives have the best conversion rates?"
```

---

## 📊 Output Files

All variants generate the same output files:

### 1. CSV Exports
**Location**: `exports/query_results_YYYYMMDD_HHMMSS.csv`  
Standard CSV format, ready for Excel, Python, or R analysis

### 2. Excel Exports
**Location**: `exports/query_results_YYYYMMDD_HHMMSS.xlsx`  
Formatted workbook with styled headers and auto-sized columns

### 3. Visualizations
**Location**: `visualizations/chart_YYYYMMDD_HHMMSS.png`  
High-resolution PNG charts (300 DPI) with professional styling

---

## 📈 Performance

All variants share the same performance characteristics:

| Component | Latency | Notes |
|-----------|---------|-------|
| Schema Retrieval | 1-5ms | **Cached** (500ms first time) |
| SQL Generation (LLM) | 1-3s | Azure OpenAI |
| Query Execution | 100ms-5s | Database speed |
| Results Interpretation (LLM) | 1-2s | Azure OpenAI |
| Export + Visualization | 50-300ms | Pandas + Matplotlib |
| **Total End-to-End** | **3-10s** | With caching |

**Key Optimization**: Schema caching provides **100-500x speedup** on schema retrieval.

---

## 🔒 Security Features

All variants implement enterprise-grade security:

### Query Safety
- ✅ **Whitelist approach** - Only SELECT by default
- ✅ **Dangerous operation blocking** - Prevents DROP, DELETE, ALTER, TRUNCATE, EXEC
- ✅ **Row limit enforcement** - Automatic TOP/LIMIT clause
- ✅ **SQL injection prevention** - Parameterized queries
- ✅ **Schema isolation** - Optional restrictions to specific schemas

### Database Access
- ✅ **Read-only mode** - Default configuration
- ✅ **Azure AD authentication** - Secure credential-free access
- ✅ **Connection pooling** - Efficient resource usage
- ✅ **Timeout enforcement** - Prevents long-running queries

### Audit & Compliance
- ✅ **Full query logging** - All SQL queries traced
- ✅ **User attribution** - Track who asked what
- ✅ **Result tracking** - Log all data access
- ✅ **Observability integration** - Send to SIEM/monitoring

---

## 🚀 Deployment Scenarios

### Development & Testing
**Use**: `nl2sql-pipeline` (DevUI)  
**Deploy**: Local machine  
```bash
python nl2sql_workflow.py
```

### Azure Functions
**Use**: `nl2sql-cli` (CLI)  
**Deploy**: HTTP-triggered function  
```bash
func azure functionapp publish your-function-app
```

### Azure Container Instance
**Use**: `nl2sql-cli` (CLI) or `nl2sql-gradio` (Chat)  
**Deploy**: Docker container  
```bash
docker build -t nl2sql-app .
az container create \
    --resource-group your-rg \
    --name nl2sql-app \
    --image nl2sql-app \
    --ports 7860 \
    --environment-variables \
        AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT
```

### Kubernetes
**Use**: `nl2sql-gradio` (Chat)  
**Deploy**: Multiple replicas with load balancing  
```bash
kubectl apply -f nl2sql-deployment.yaml
```

### User-Facing Web App
**Use**: `nl2sql-gradio` (Chat)  
**Deploy**: Azure App Service or Azure Container Apps  
```bash
az containerapp create \
    --name nl2sql-chat \
    --resource-group your-rg \
    --image nl2sql-gradio:latest \
    --target-port 7860
```

---

## 🛠️ Customization

All variants share the same customization points:

### Modify Agent Instructions
Edit in `nl2sql_workflow.py` of any variant:
```python
sql_generator = client.create_agent(
    instructions="""You are an expert SQL generator for retail analytics.
    
    Domain-specific rules:
    - Always use CustomerID instead of CustomerName for joins
    - Sales data is in UTC timezone
    - Revenue should be calculated as Quantity * UnitPrice
    """,
    name="sql_generator",
)
```

### Add Custom Validators
Edit in `executors.py`:
```python
class SQLValidatorExecutor(Executor):
    def _check_safety(self, sql: str):
        # Add your domain-specific rules
        if "SENSITIVE_TABLE" in sql.upper():
            return False, ["Access to sensitive table denied"]
        
        return True, []
```

### Add Pipeline Steps
Insert custom executors in `nl2sql_workflow.py`:
```python
builder.participants([
    input_normalizer,
    schema_retriever,
    sql_generator,
    your_custom_optimizer,  # ← Add here
    sql_validator,
    query_executor,
    results_interpreter,
    data_exporter,
    visualization_generator,
])
```

---

## 🧪 Testing

Each variant includes test files:

```bash
# Test database connection
python test_db_connection.py

# Test complete workflow
python test_workflow.py

# Test visualizations
python test_visualizations.py
```

---

## 📖 Documentation Structure

### Per-Variant Documentation

Each variant has its own comprehensive README:
- [nl2sql-pipeline/README.md](nl2sql-pipeline/README.md) - DevUI variant (most detailed)
- [nl2sql-cli/README.md](nl2sql-cli/README.md) - CLI variant
- [nl2sql-gradio/README.md](nl2sql-gradio/README.md) - Gradio chat variant

### Shared Documentation

All variants reference common documentation in `nl2sql-pipeline/docs/`:

**Getting Started**:
- [QUICKSTART.md](nl2sql-pipeline/docs/guides/QUICKSTART.md) - 5-minute setup
- [DATABASE_SETUP.md](nl2sql-pipeline/docs/guides/DATABASE_SETUP.md) - Database configuration
- [TESTING_GUIDE.md](nl2sql-pipeline/docs/guides/TESTING_GUIDE.md) - Testing and validation

**Feature Guides**:
- [SCHEMA_CACHE_GUIDE.md](nl2sql-pipeline/docs/guides/SCHEMA_CACHE_GUIDE.md) - 100-500x speedup
- [VISUALIZATION_GUIDE.md](nl2sql-pipeline/docs/guides/VISUALIZATION_GUIDE.md) - Chart generation
- [EXPORT_GUIDE.md](nl2sql-pipeline/docs/guides/EXPORT_GUIDE.md) - Data export features

**Technical Reference**:
- [ARCHITECTURE.md](nl2sql-pipeline/docs/reference/ARCHITECTURE.md) - System design
- [CONFIGURATION.md](nl2sql-pipeline/docs/reference/CONFIGURATION.md) - All settings
- [INDEX.md](nl2sql-pipeline/INDEX.md) - Complete file index

---

## 🔄 Variant Comparison

| Feature | nl2sql-pipeline | nl2sql-cli | nl2sql-gradio |
|---------|----------------|------------|---------------|
| **Interface** | DevUI Web | Command Line | Gradio Chat |
| **Port** | 8097 | None | 7860 |
| **Startup** | 2-3s | <1s | 2-3s |
| **Observability** | Full traces | Logs only | Logs only |
| **Best For** | Development | Production | End Users |
| **User Type** | Developers | Automation | All Users |
| **Session Support** | ✅ Visual | ✅ CLI args | ✅ Automatic |
| **Visualization** | Files only | Files only | Inline + Files |
| **Export Access** | Files only | Files only | Download buttons |
| **Deployment** | Local | Any | Web hosting |
| **Scriptable** | ❌ | ✅ | ❌ |
| **Interactive** | ✅ | ❌ | ✅ |
| **Trace Viewing** | ✅ Real-time | ❌ | ❌ |

---

## 🐛 Troubleshooting

### Common Issues Across Variants

**Problem**: Connection to Azure SQL fails  
**Solution**: 
- Verify firewall rules allow your IP
- Check MSSQL_CONNECTION_ID in `.env`
- Run `python test_db_connection.py`

**Problem**: Schema caching not working  
**Solution**:
- Check `.cache/` directory exists
- Verify `ENABLE_SCHEMA_CACHE=true` in `.env`
- Delete cache files to force refresh

**Problem**: SQL generation is incorrect  
**Solution**:
- Review agent instructions in `nl2sql_workflow.py`
- Check schema context being provided
- Adjust prompts for your domain

**Problem**: Charts not generating  
**Solution**:
- Verify matplotlib/seaborn installed
- Check `visualizations/` directory writable
- Run `python test_visualizations.py`

### Variant-Specific Issues

**nl2sql-pipeline**:
- Port 8097 already in use → Change in `nl2sql_workflow.py`
- DevUI not opening → Check browser console, verify port forwarding

**nl2sql-cli**:
- No output → Check stderr for errors
- Session not working → Verify session ID consistency

**nl2sql-gradio**:
- Port 7860 busy → Change in `app.py`
- Charts not displaying → Check file permissions on visualizations/

---

## 📦 Dependencies

All variants share the same core dependencies:

```txt
agent_framework>=1.0.0      # Core workflow framework
azure-identity>=1.15.0      # Azure authentication
azure-openai>=1.0.0         # OpenAI client
pyodbc>=5.0.0               # SQL Server driver
pandas>=2.0.0               # Data manipulation
openpyxl>=3.1.0            # Excel export
matplotlib>=3.8.0           # Visualization
seaborn>=0.13.0            # Chart styling
python-dotenv>=1.0.0       # Environment management
pydantic>=2.0.0            # Data validation
```

**Additional for nl2sql-gradio**:
```txt
gradio>=4.0.0              # Chat UI framework
```

---

## 🎯 Choosing the Right Variant

### Use nl2sql-pipeline (DevUI) if you need:
- Development and debugging
- Visual inspection of LLM behavior
- Training and demonstrations
- Understanding pipeline flow
- Real-time trace viewing

### Use nl2sql-cli if you need:
- Production deployments
- Automation and scripting
- Azure Functions or containers
- Scheduled queries
- CI/CD integration
- Fastest startup time

### Use nl2sql-gradio if you need:
- User-facing applications
- Interactive demos
- Non-technical user access
- Modern chat interface
- Inline visualizations
- Beautiful UI

---

## 📄 License

See repository [LICENSE](../LICENSE) file.

---

## 🤝 Contributing

### Extend All Variants
1. Make changes to shared files:
   - `executors.py` - Add/modify executors
   - `nl2sql_workflow.py` - Modify pipeline
   - `visualizer.py` - Add chart types
   - `schema_cache.py` - Enhance caching
   - `db_utils.py` - Database utilities

2. Copy changes to all three variants
3. Test each variant independently
4. Update documentation

### Add New Variant
1. Copy `nl2sql-pipeline/` to new directory
2. Modify interface layer only
3. Keep core pipeline logic unchanged
4. Add to this README
5. Create variant-specific README

---

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ All three variants can connect to Azure SQL
2. ✅ Schema caching works (check `.cache/` directory)
3. ✅ SQL generation produces valid queries
4. ✅ Queries execute successfully
5. ✅ Natural language answers are coherent
6. ✅ CSV/Excel files appear in `exports/`
7. ✅ Charts appear in `visualizations/`
8. ✅ Traces visible (in DevUI variant)

---

## 📞 Support Resources

### Framework Documentation
- **Agent Framework** - [../python/README.md](../python/README.md)
- **Workflow Samples** - [../python/samples/](../python/samples/)
- **MCP Tools** - [../MssqlMcp/](../MssqlMcp/)

### Azure Resources
- **Azure OpenAI** - [Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- **Azure SQL** - [Documentation](https://learn.microsoft.com/azure/azure-sql/)

---

## 🎉 Summary

This directory provides **three production-ready variants** of the same powerful NL2SQL pipeline:

- **nl2sql-pipeline** for **development** with full observability
- **nl2sql-cli** for **production** automation and scripting
- **nl2sql-gradio** for **end users** with beautiful chat interface

All variants share:
- ✅ Same core pipeline architecture
- ✅ Same safety and security features
- ✅ Same performance optimizations
- ✅ Same output formats
- ✅ Same configuration

Choose the variant that best fits your deployment scenario, and enjoy natural language access to your SQL databases! 🚀

---

**Created**: October 2025  
**Last Updated**: November 30, 2025  
**Framework**: Microsoft Agent Framework  
**Pattern**: Sequential Pipeline (Agents + Executors)  
**Status**: ✅ Production Ready  
**Performance**: 3-10s end-to-end with 100-500x schema caching speedup

---

_For detailed documentation, see the README in each variant's directory._

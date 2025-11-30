# NL2SQL Pipeline - Complete Artifact Index

> **Quick Reference**: All files and documentation for the Natural Language to SQL workflow

**Last Updated**: November 28, 2025  
**Status**: Production Ready ✅

---

## 📁 Complete Directory Structure

```
nl2sql-pipeline/
│
├── 📄 Core Python Files (Root)
│   ├── nl2sql_workflow.py          # Main pipeline orchestration
│   ├── executors.py                # Custom business logic executors
│   ├── schema_cache.py             # Performance caching (100-500x speedup)
│   ├── visualizer.py               # Automatic chart generation
│   ├── db_utils.py                 # Database connection utilities
│   └── demo_followup.py            # Demo/testing helper
│
├── 📚 Documentation (Root)
│   ├── README.md                   # Main documentation (START HERE)
│   ├── INDEX.md                    # This file - complete index
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Your configuration (not in git)
│   ├── .env.example                # Configuration template
│   └── .gitignore                  # Git ignore rules
│
├── 📖 docs/                        # Organized documentation
│   ├── guides/                     # How-to guides
│   │   ├── QUICKSTART.md          # 5-minute setup guide
│   │   ├── SCHEMA_CACHE_GUIDE.md  # Performance optimization
│   │   ├── VISUALIZATION_GUIDE.md # Chart generation
│   │   ├── EXPORT_GUIDE.md        # Data export features
│   │   ├── TESTING_GUIDE.md       # Testing & validation
│   │   └── DATABASE_SETUP.md      # Database configuration
│   └── reference/                  # Technical reference
│       ├── ARCHITECTURE.md        # System design & diagrams
│       └── CONFIGURATION.md       # Configuration reference
│
├── 💾 sql/                         # Database scripts
│   ├── discover_schema.sql        # Schema discovery queries
│   ├── get_fact_tables.sql        # Fact table identification
│   ├── add_foreign_keys.sql       # Foreign key setup
│   └── add_foreign_keys_final.sql # Final FK configuration
│
├── 🧪 tests/                       # Test suite
│   ├── test_workflow.py           # End-to-end workflow tests
│   ├── test_visualizations.py     # Chart generation tests
│   └── test_db_connection.py      # Database connection tests
│
├── 💡 examples/                    # Example queries
│   └── sample_questions.md        # Sample NL questions to try
│
├── 📊 exports/                     # Auto-generated data files
│   ├── query_results_*.csv        # CSV exports (timestamped)
│   └── query_results_*.xlsx       # Excel exports (timestamped)
│
├── 📈 visualizations/              # Auto-generated charts
│   └── chart_*.png                # PNG charts (timestamped)
│
├── ⚡ .cache/                      # Schema cache (auto-managed)
│   └── schema_cache_*.json        # Cached schema files
│
├── 📋 workflow_outputs/            # Run logs
│   └── sessions/                  # DevUI session data
│
└── 🗃️ archive/                     # Historical files
    ├── README_OLD.md              # Previous README version
    ├── OVERVIEW.md                # Old overview doc
    ├── BUGFIX_NOTES.md            # Bug fix history
    ├── TEST_SUCCESS_SUMMARY.md    # Test results
    ├── EXPORT_TEST.md             # Export testing notes
    ├── TERADATA-FI_nl2sql_test_cases.md
    ├── nl2sql_workflow copy.py    # Old workflow version
    ├── test.csv                   # Old test data
    ├── fact_tables.csv            # Fact table data
    └── OUPUT.json                 # Old output file
```

---

## 📚 Documentation Quick Reference

### 🚀 Getting Started (Read in Order)
1. **[README.md](README.md)** - **START HERE** - Complete overview & features
2. **[docs/guides/QUICKSTART.md](docs/guides/QUICKSTART.md)** - 5-minute setup
3. **[examples/sample_questions.md](examples/sample_questions.md)** - Try example queries

### 📖 Feature Guides
4. **[docs/guides/SCHEMA_CACHE_GUIDE.md](docs/guides/SCHEMA_CACHE_GUIDE.md)** - 100-500x performance boost
5. **[docs/guides/VISUALIZATION_GUIDE.md](docs/guides/VISUALIZATION_GUIDE.md)** - Automatic charts
6. **[docs/guides/EXPORT_GUIDE.md](docs/guides/EXPORT_GUIDE.md)** - CSV & Excel export
7. **[docs/guides/TESTING_GUIDE.md](docs/guides/TESTING_GUIDE.md)** - Run tests
8. **[docs/guides/DATABASE_SETUP.md](docs/guides/DATABASE_SETUP.md)** - Database config

### 🔧 Technical Reference
9. **[docs/reference/ARCHITECTURE.md](docs/reference/ARCHITECTURE.md)** - System design & flow
10. **[docs/reference/CONFIGURATION.md](docs/reference/CONFIGURATION.md)** - All settings explained

---

## 🔧 Core Python Modules

### nl2sql_workflow.py
**Main workflow orchestration** - Entry point for the pipeline.

**Key Functions:**
- `setup_tracing()` - Configure observability (OTLP, AppInsights, Console)
- `get_mssql_connection()` - Database connection management
- `create_nl2sql_workflow()` - Build sequential pipeline
- `launch_devui()` - Start DevUI server on port 8097

**Usage:**
```bash
python nl2sql_workflow.py
```

### executors.py (380 lines)
**Custom business logic executors** - All non-LLM pipeline steps.

**Executors:**
- `InputNormalizerExecutor` - Parse and validate user questions
- `SchemaRetrieverExecutor` - Fetch database schema (with caching)
- `SQLValidatorExecutor` - Safety checks & query validation
- `QueryExecutorExecutor` - Execute SQL queries safely
- `DataExporterExecutor` - Export to CSV & Excel
- `VisualizationGeneratorExecutor` - Auto-generate charts

**Data Models:**
- `UserQuestion` - Input model
- `SchemaContext` - Database schema info
- `GeneratedSQL` - LLM-generated SQL
- `ValidatedSQL` - Validated query
- `QueryResults` - Execution results with data
- `ExportedFiles` - File paths for exports
- `VisualizationResult` - Chart metadata

### schema_cache.py
**Performance optimization** - In-memory and file-based schema caching.

**Features:**
- 100-500x faster schema retrieval
- Two-tier caching (memory + file)
- Auto-refresh every 5 minutes
- Survives workflow restarts

### visualizer.py
**Chart generation** - Automatic visualization based on data characteristics.

**Supported Charts:**
- Horizontal bar charts (rankings, top-N)
- Line charts (time series, trends)
- Pie charts (distributions, ≤8 categories)
- Heatmaps (correlation matrices)

### db_utils.py
**Database utilities** - Connection management and query execution.

**Functions:**
- `get_connection()` - Azure SQL connection with retry
- `execute_query()` - Safe query execution
- `test_connection()` - Connection validation

### demo_followup.py
**Demo helper** - Testing and demonstration utilities.

---

## 🎯 Key Features Summary

✅ **Natural Language Interface** - Ask questions in plain English  
✅ **Automatic Schema Discovery** - No manual configuration needed  
✅ **Schema Caching** - 100-500x performance improvement  
✅ **SQL Safety** - Prevents destructive operations (DROP, DELETE, ALTER)  
✅ **Error Recovery** - Automatic retry with LLM-corrected queries  
✅ **Data Export** - Automatic CSV & Excel with timestamps  
✅ **Smart Visualizations** - Auto-selects appropriate chart types  
✅ **Full Observability** - DevUI traces, OTLP, Application Insights  
✅ **Production Ready** - Error handling, validation, security built-in  

---

## 🚀 Quick Start Guide

```bash
# 1. Configure environment
cd nl2sql-pipeline
cp .env.example .env
# Edit .env with your Azure OpenAI and Azure SQL credentials

# 2. Activate virtual environment
cd /Users/arturoquiroga/GITHUB/agent-framework-public
source .venv/bin/activate

# 3. Launch pipeline
cd nl2sql-pipeline
python nl2sql_workflow.py

# 4. Open DevUI in browser
open http://localhost:8097
```

**Try asking:**
```
"What are the top 10 customers by revenue?"
"Show me monthly sales trends for 2024"
"Which products are out of stock?"
```

---

## 📊 Pipeline Architecture

**Pattern**: Sequential Pipeline with LLM Agents + Custom Executors

```
User Question (Natural Language)
    ↓
[1] Input Normalizer (Executor)
    ↓ Parse & validate
    ↓
[2] Schema Retriever (Executor) ──→ Azure SQL Database
    ↓ [Cached for 100-500x speedup]
    ↓
[3] SQL Generator (Agent) ──→ Azure OpenAI GPT-4
    ↓ Natural language → SQL
    ↓
[4] SQL Validator (Executor)
    ↓ Safety checks & optimization
    ↓
[5] Query Executor (Executor) ──→ Azure SQL Database
    ↓ Execute validated query
    ↓
[6] Results Interpreter (Agent) ──→ Azure OpenAI GPT-4
    ↓ SQL results → Natural language
    ↓
[7] Data Exporter (Executor) ──→ CSV & Excel files
    ↓ Timestamped exports
    ↓
[8] Visualization Generator (Executor) ──→ PNG charts
    ↓ Smart chart selection
    ↓
Natural Language Answer + Insights + Data Files + Visualizations
```

**Total Latency**: 3-10 seconds end-to-end

---

## 📁 File Organization

### Production Files (Root - 11 files)
| File | Purpose | Lines |
|------|---------|-------|
| `nl2sql_workflow.py` | Main orchestration | 570 |
| `executors.py` | Business logic | 380 |
| `schema_cache.py` | Performance caching | ~150 |
| `visualizer.py` | Chart generation | ~200 |
| `db_utils.py` | Database utilities | ~250 |
| `demo_followup.py` | Testing helper | ~100 |
| `README.md` | Main documentation | 600+ |
| `INDEX.md` | This file | 400+ |
| `requirements.txt` | Dependencies | ~20 |
| `.env` / `.env.example` | Configuration | ~30 |

### Documentation (docs/ - 8 files)
| Location | File | Purpose |
|----------|------|---------|
| `guides/` | `QUICKSTART.md` | 5-minute setup |
| `guides/` | `SCHEMA_CACHE_GUIDE.md` | Caching optimization |
| `guides/` | `VISUALIZATION_GUIDE.md` | Chart features |
| `guides/` | `EXPORT_GUIDE.md` | Data export |
| `guides/` | `TESTING_GUIDE.md` | Test & validate |
| `guides/` | `DATABASE_SETUP.md` | DB configuration |
| `reference/` | `ARCHITECTURE.md` | System design |
| `reference/` | `CONFIGURATION.md` | Settings reference |

### SQL Scripts (sql/ - 4 files)
- Setup and schema discovery scripts
- Foreign key configuration
- Fact table identification

### Tests (tests/ - 3 files)
- End-to-end workflow tests
- Visualization tests
- Database connection tests

### Archives (archive/ - 10+ files)
- Historical documentation
- Old test files
- Bug fix notes

---

## 🔐 Security & Safety Features

### Query Safety
- **Whitelist Approach** - Only SELECT statements by default
- **Dangerous Operation Blocking** - Prevents DROP, DELETE, ALTER, TRUNCATE, EXEC
- **Row Limit Enforcement** - Automatic TOP 1000 clause
- **SQL Injection Prevention** - Parameterized queries
- **Schema Isolation** - Optional restrictions to specific schemas

### Database Access
- **Read-Only Mode** - Default configuration
- **Azure AD Authentication** - Secure, credential-free access
- **Connection Pooling** - Efficient resource usage
- **Timeout Enforcement** - Prevents runaway queries

### Audit & Compliance
- **Full Query Logging** - All SQL queries traced
- **Result Tracking** - Log all data access
- **Observability Integration** - Send to SIEM/monitoring

---

## 📈 Performance Metrics

| Component | Latency | Optimization |
|-----------|---------|--------------|
| Input Normalizer | <10ms | Pure Python |
| Schema Retriever | 1-5ms | **Cached** (500ms without) |
| SQL Generator (LLM) | 1-3s | Azure OpenAI |
| SQL Validator | <50ms | Pure Python |
| Query Executor | 100ms-5s | Database speed |
| Results Interpreter (LLM) | 1-2s | Azure OpenAI |
| Data Exporter | 10-100ms | Pandas |
| Visualization | 50-200ms | Matplotlib/Seaborn |
| **Total End-to-End** | **3-10s** | **With caching** |

**Key Optimization**: Schema caching provides **100-500x speedup** on schema retrieval.

---

## 🛠️ Customization Examples

### Modify Agent Instructions
Edit in [nl2sql_workflow.py](nl2sql_workflow.py):
```python
sql_generator = client.create_agent(
    instructions="""You are an expert SQL generator for retail analytics.
    
    Domain rules:
    - Always join customers on CustomerID (not Name)
    - Sales dates are in UTC timezone
    - Revenue = Quantity * UnitPrice (don't use TotalSales column)
    """,
    name="sql_generator",
)
```

### Add Custom Validators
Edit in [executors.py](executors.py):
```python
class SQLValidatorExecutor(Executor):
    def _check_safety(self, sql: str):
        # Block access to sensitive tables
        if "EMPLOYEE_SALARY" in sql.upper():
            return False, ["Access denied to salary data"]
        
        # Require WHERE for large tables
        if "FROM orders" in sql.lower() and "WHERE" not in sql.upper():
            return False, ["WHERE clause required for orders table"]
            
        return True, []
```

### Add Pipeline Steps
Edit in [nl2sql_workflow.py](nl2sql_workflow.py):
```python
builder.participants([
    input_normalizer,
    schema_retriever,
    sql_generator,
    your_query_optimizer,      # ← Add custom step
    sql_validator,
    query_executor,
    your_result_enricher,      # ← Add custom step
    results_interpreter,
    data_exporter,
    visualization_generator,
])
```

---

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test Azure SQL connection
python tests/test_db_connection.py

# Check Azure CLI authentication
az account show
```

### SQL Generation Issues
**Problem**: Generated SQL is incorrect  
**Solution**: 
- Check schema context in DevUI traces
- Adjust agent instructions for your domain
- Review question phrasing

### Query Execution Failures
**Problem**: Query fails to execute  
**Solution**:
- Check database permissions
- Verify firewall rules allow your IP
- Review SQL in validator output
- Check table/column names exist

### Performance Issues
**Problem**: Queries are slow  
**Solution**:
- Verify schema caching is enabled (`ENABLE_SCHEMA_CACHE=true`)
- Check query execution time in database
- Add database indexes on frequently queried columns
- Monitor in DevUI traces

---

## 📖 Example Questions by Category

### Basic Queries
```
"Show me all customers from California"
"List products with price over $100"
"What orders were placed in the last 7 days?"
```

### Analytics & Aggregations (→ Bar Charts)
```
"What are the top 10 customers by revenue?"
"Show me sales by product category"
"Which regions have the highest order volume?"
"Top 5 best-selling products this quarter"
```

### Time Series & Trends (→ Line Charts)
```
"Show me daily sales for the past 30 days"
"What's the monthly revenue trend for 2024?"
"How has customer count changed over time?"
"Order volume by week this year"
```

### Distributions (→ Pie Charts)
```
"Sales breakdown by category"
"Customer distribution by region"
"Order status distribution"
```

### Complex Analytics
```
"Compare year-over-year sales growth by category"
"Customer lifetime value by segment"
"Sales rep performance with conversion rates"
"Product inventory turnover analysis"
```

See [examples/sample_questions.md](examples/sample_questions.md) for 50+ examples.

---

## 🔄 Workflow Pattern Details

**Type**: Sequential Pipeline  
**Framework**: Microsoft Agent Framework  
**Pattern**: LLM Agents + Custom Executors (Hybrid)  
**Orchestration**: SequentialBuilder  
**Observability**: OpenTelemetry compatible  

### Components Breakdown
| # | Component | Type | Technology | Purpose |
|---|-----------|------|------------|---------|
| 1 | Input Normalizer | Executor | Python | Parse user input |
| 2 | Schema Retriever | Executor | Python + Azure SQL | Fetch schema (cached) |
| 3 | SQL Generator | **Agent** | **Azure OpenAI GPT-4** | NL → SQL |
| 4 | SQL Validator | Executor | Python | Safety checks |
| 5 | Query Executor | Executor | Python + Azure SQL | Run SQL |
| 6 | Results Interpreter | **Agent** | **Azure OpenAI GPT-4** | SQL results → NL |
| 7 | Data Exporter | Executor | Python + Pandas | CSV/Excel export |
| 8 | Visualization | Executor | Python + Matplotlib | Auto charts |

---

## 🌐 Integration Points

### Azure Services
- **Azure OpenAI** - GPT-4 for SQL generation and interpretation
- **Azure SQL Database** - Data storage and querying
- **Application Insights** (optional) - Observability and monitoring
- **Azure CLI** - Authentication (`az login`)

### Python Packages
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

---

## 📦 Output Files Generated

### 1. CSV Exports
**Location**: `exports/query_results_YYYYMMDD_HHMMSS.csv`  
**Format**: Standard CSV with headers  
**Features**: All data types preserved, ready for Excel/Python/R  

### 2. Excel Exports
**Location**: `exports/query_results_YYYYMMDD_HHMMSS.xlsx`  
**Format**: Excel workbook with formatting  
**Features**: Styled headers, auto-sized columns, professional formatting  

### 3. Visualizations
**Location**: `visualizations/chart_YYYYMMDD_HHMMSS.png`  
**Format**: High-resolution PNG (300 DPI)  
**Features**: Auto-selected chart type, professional styling  

### 4. Workflow Logs
**Location**: `workflow_outputs/sessions/`  
**Format**: JSON logs per session  
**Features**: Complete trace of pipeline execution  

---

## 🎓 Learning Resources

### Agent Framework
1. **Main Docs** - `../python/README.md`
2. **Sequential Workflows** - `../python/samples/getting_started/workflows/agents/`
3. **Custom Executors** - `../python/samples/getting_started/workflows/orchestration/`
4. **Observability** - `../python/samples/observability/`

### MSSQL Integration
5. **MCP Tools** - `../MssqlMcp/` directory
6. **Connection Guide** - [docs/guides/DATABASE_SETUP.md](docs/guides/DATABASE_SETUP.md)

### Azure Resources
7. **Azure OpenAI** - [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
8. **Azure SQL** - [Azure SQL Database Documentation](https://learn.microsoft.com/azure/azure-sql/)

---

## 💡 Enhancement Ideas

### ✅ Already Implemented
- [x] Schema caching for performance
- [x] Automatic data export (CSV/Excel)
- [x] Smart visualization generation
- [x] Error recovery with retry
- [x] SQL safety validation
- [x] DevUI integration
- [x] Full observability

### 🔄 Potential Enhancements
- [ ] Query result caching (cache frequently asked questions)
- [ ] Multi-turn conversation support (follow-up questions)
- [ ] Query history and favorites
- [ ] Query cost estimation (show expected execution time)
- [ ] Query optimization suggestions
- [ ] Natural language error messages
- [ ] Voice input support
- [ ] Scheduled reports
- [ ] Email notifications for query completion
- [ ] Data quality checks
- [ ] Anomaly detection in results
- [ ] Query templates library

### 🚀 Production Features
- [ ] Rate limiting per user
- [ ] Query result pagination
- [ ] Horizontal scaling support
- [ ] Database connection pooling optimization
- [ ] Advanced caching strategies
- [ ] A/B testing for prompts
- [ ] User feedback collection
- [ ] Query performance analytics
- [ ] Cost tracking and alerts
- [ ] Multi-database support (PostgreSQL, MySQL)

---

## 🤝 Contributing & Extending

### Add New Validators
1. Open [executors.py](executors.py)
2. Modify `SQLValidatorExecutor._check_safety()`
3. Add your domain-specific rules
4. Test with [tests/test_workflow.py](tests/test_workflow.py)

### Add Pipeline Steps
1. Create new executor class in [executors.py](executors.py)
2. Add to pipeline in [nl2sql_workflow.py](nl2sql_workflow.py)
3. Update data models if needed
4. Add tests in [tests/](tests/)

### Customize Agents
1. Edit agent instructions in [nl2sql_workflow.py](nl2sql_workflow.py)
2. Adjust prompts for your domain
3. Test with example questions
4. Document in [examples/sample_questions.md](examples/sample_questions.md)

### Add Chart Types
1. Edit [visualizer.py](visualizer.py)
2. Add chart generation function
3. Update chart type detection logic
4. Test with [tests/test_visualizations.py](tests/test_visualizations.py)

---

## ✅ Pre-Flight Checklist

Before first run, ensure:

- [ ] **Azure OpenAI** endpoint configured in `.env`
- [ ] **Azure SQL Database** accessible and has sample data
- [ ] **Azure CLI** authenticated (`az login` completed)
- [ ] **Python virtual environment** activated
- [ ] **Dependencies** installed (`pip install -r requirements.txt`)
- [ ] **Port 8097** available for DevUI
- [ ] **Firewall rules** allow connection to Azure SQL
- [ ] **.env file** created from `.env.example`

---

## 🎉 Success Indicators

You'll know the pipeline is working when:

1. ✅ DevUI opens at http://localhost:8097
2. ✅ Schema retrieval displays your database tables in traces
3. ✅ SQL generation produces valid queries for your schema
4. ✅ Queries execute successfully and return results
5. ✅ Natural language answers are coherent and accurate
6. ✅ CSV/Excel files appear in `exports/` directory
7. ✅ Charts appear in `visualizations/` directory
8. ✅ Complete traces visible in DevUI showing all 8 steps

### Expected First Query Timeline
- Schema retrieval: ~500ms (first time, then <1ms cached)
- SQL generation: 1-3s
- Query execution: 100ms-5s (depending on query complexity)
- Results interpretation: 1-2s
- Export + visualization: <500ms
- **Total: 3-12s for first query, 2-10s for subsequent queries**

---

## 📄 License

See repository [LICENSE](../LICENSE) file.

---

## 📞 Support & Contact

### Documentation
- **This Index** - Complete file reference
- **[README.md](README.md)** - Main documentation
- **[docs/guides/](docs/guides/)** - How-to guides
- **[docs/reference/](docs/reference/)** - Technical reference

### Framework Resources
- **Agent Framework** - [../python/README.md](../python/README.md)
- **Samples** - [../python/samples/](../python/samples/)
- **MCP Tools** - [../MssqlMcp/](../MssqlMcp/)

### Common Questions

**Q: Can I use other databases?**  
A: Yes, modify [db_utils.py](db_utils.py) for PostgreSQL, MySQL, Snowflake, etc.

**Q: Can I use other LLMs?**  
A: Yes, agent framework supports OpenAI, Anthropic, and other providers.

**Q: Is this production-ready?**  
A: Yes, includes error handling, validation, security, and observability.

**Q: How do I deploy this?**  
A: Deploy to Azure Container Instance, Azure Functions, or any Python hosting.

**Q: Can I customize the SQL generation?**  
A: Yes, edit agent instructions in [nl2sql_workflow.py](nl2sql_workflow.py).

**Q: How do I add write operations (INSERT/UPDATE/DELETE)?**  
A: Set `ALLOW_WRITE_OPERATIONS=true` in `.env` and modify validator in [executors.py](executors.py).

---

**Created**: October 2025  
**Last Updated**: November 28, 2025  
**Framework**: Microsoft Agent Framework  
**Pattern**: Sequential Pipeline (Agents + Executors)  
**Status**: ✅ Production Ready  
**Performance**: 3-10s end-to-end, 100-500x schema caching speedup

---

_End of Index - [Back to README](README.md)_

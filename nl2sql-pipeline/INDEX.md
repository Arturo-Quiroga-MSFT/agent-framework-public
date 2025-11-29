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

## 🔐 Security

- **Read-Only by Default** - Only SELECT queries allowed
- **Row Limits** - Automatic TOP 1000 clause
- **Query Validation** - Blocks DROP, DELETE, ALTER, etc.
- **Schema Isolation** - Optional schema restrictions
- **Audit Logging** - Track all queries

## 🛠️ Customization

### Modify Agent Instructions
Edit in `nl2sql_workflow.py`:
```python
sql_generator = client.create_agent(
    instructions="Your custom instructions...",
    name="sql_generator",
)
```

### Add Custom Validators
Edit in `executors.py`:
```python
class SQLValidatorExecutor(Executor):
    def _check_safety(self, sql: str):
        # Add your rules here
        pass
```

### Change Pipeline Structure
Edit in `nl2sql_workflow.py`:
```python
builder.participants([
    input_normalizer,
    schema_retriever,
    sql_generator,
    # Add your custom executor here
    sql_validator,
    query_executor,
    results_interpreter,
])
```

## 📈 Performance

| Component | Typical Latency |
|-----------|----------------|
| Input Normalizer | <10ms |
| Schema Retriever | 50-200ms |
| SQL Generator | 1-3s |
| SQL Validator | <50ms |
| Query Executor | 100ms-5s |
| Results Interpreter | 1-2s |
| **Total** | **3-10s** |

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test MSSQL connection
python -c "from mssql_list_servers import mssql_list_servers; print(mssql_list_servers())"
```

### LLM Issues
- Check Azure OpenAI endpoint in `.env`
- Verify deployment name matches
- Check quota and rate limits

### Query Failures
- Review SQL in validator output
- Check database permissions
- Verify table/column names

## 📖 Example Questions

Try these with your database:

**Basic:**
- "Show me all customers"
- "What are the top 10 products?"

**Aggregations:**
- "How many orders were placed last month?"
- "What's the total revenue by region?"

**Analytics:**
- "Who are the top 5 customers by revenue?"
- "What's the monthly sales trend this year?"

See [examples/sample_questions.md](examples/sample_questions.md) for more.

## 🔄 Workflow Pattern

**Type:** Sequential Pipeline  
**Framework:** Microsoft Agent Framework  
**Pattern:** Agents + Business Logic Executors  
**Orchestration:** SequentialBuilder  

## 🌐 Integration Points

### Azure Services
- **Azure OpenAI** - LLM inference
- **Azure SQL Database** - Data storage
- **Application Insights** - Observability (optional)

### MCP Tools
- `mssql_connect` - Database connection
- `mssql_list_servers` - Server discovery
- `mssql_list_schemas` - Schema retrieval
- `mssql_list_tables` - Table listing
- `mssql_run_query` - Query execution

## 📦 Dependencies

Required packages (already in agent framework):
- `agent_framework` - Core workflow framework
- `azure-identity` - Azure authentication
- `python-dotenv` - Environment management
- `pydantic` - Data validation

## 🎓 Learning Resources

1. **Sequential Workflows** - See `python/samples/getting_started/workflows/agents/`
2. **Custom Executors** - See `python/samples/getting_started/workflows/orchestration/`
3. **Agent Framework Docs** - See `python/README.md`
4. **MSSQL MCP Tools** - See `MssqlMcp/` directory

## 💡 Next Steps

### Enhancements
- [ ] Add query result caching
- [ ] Implement schema caching
- [ ] Add query optimization step
- [ ] Create visualization suggestions
- [ ] Add multi-turn conversation support
- [ ] Implement query history
- [ ] Add cost estimation

### Production Readiness
- [ ] Add comprehensive error handling
- [ ] Implement retry logic
- [ ] Add monitoring and alerts
- [ ] Create deployment scripts
- [ ] Add load testing
- [ ] Document security best practices
- [ ] Create CI/CD pipeline

## 🤝 Contributing

To extend this workflow:

1. **Add Validators**: Edit `executors.py` → `SQLValidatorExecutor`
2. **Add Steps**: Create new executor → Add to pipeline in `nl2sql_workflow.py`
3. **Modify Agents**: Edit agent instructions in `nl2sql_workflow.py`
4. **Add Examples**: Create new files in `examples/`

## 📄 License

See repository LICENSE file.

## ✅ Checklist for First Run

- [ ] Azure OpenAI endpoint configured in `.env`
- [ ] MSSQL server accessible
- [ ] `az login` completed
- [ ] Virtual environment activated
- [ ] Database has sample data
- [ ] Port 8097 available
- [ ] Firewall allows Azure SQL connection

## 🎉 Success Indicators

You'll know it's working when:
1. DevUI opens at http://localhost:8097
2. Schema retrieval shows your tables
3. SQL generation produces valid queries
4. Query execution returns results
5. Interpreter provides natural language answers

---

**Created:** October 14, 2025  
**Framework:** Microsoft Agent Framework  
**Pattern:** Sequential Pipeline with Agents + Custom Executors  
**Purpose:** Natural Language to SQL with Azure SQL Database

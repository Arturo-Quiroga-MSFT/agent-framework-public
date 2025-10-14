# NL2SQL Pipeline - Complete Artifact Index

All files and documentation for the Natural Language to SQL workflow.

## 📁 Directory Structure

```
nl2sql-pipeline/
├── README.md                    # Main documentation
├── QUICKSTART.md               # 5-minute setup guide
├── ARCHITECTURE.md             # System architecture & diagrams
├── CONFIGURATION.md            # Configuration reference
├── .env                        # Environment variables (user-provided)
├── nl2sql_workflow.py          # Main workflow implementation
├── executors.py                # Custom business logic executors
└── examples/
    └── sample_questions.md     # Example queries for testing
```

## 📚 Documentation

### Getting Started
1. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
2. **[README.md](README.md)** - Full feature documentation
3. **[examples/sample_questions.md](examples/sample_questions.md)** - Test queries

### Deep Dive
4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & flow diagrams
5. **[CONFIGURATION.md](CONFIGURATION.md)** - Customization guide

## 🔧 Core Files

### nl2sql_workflow.py
Main workflow file that orchestrates the sequential pipeline.

**Key Components:**
- `setup_tracing()` - Configure observability
- `get_mssql_connection()` - Database connection management
- `create_nl2sql_workflow()` - Workflow builder
- `launch_devui()` - DevUI server startup

**Usage:**
```bash
python nl2sql-pipeline/nl2sql_workflow.py
```

### executors.py
Custom executors for business logic.

**Classes:**
- `InputNormalizerExecutor` - Parse user input
- `SchemaRetrieverExecutor` - Fetch database schema
- `SQLValidatorExecutor` - Safety & validation
- `QueryExecutorExecutor` - Execute SQL queries

**Data Models:**
- `UserQuestion` - Input model
- `SchemaContext` - Database schema info
- `GeneratedSQL` - LLM output
- `ValidatedSQL` - Validated query
- `QueryResults` - Execution results

## 🎯 Key Features

✅ **Natural Language Interface** - Ask questions in plain English  
✅ **Automatic Schema Discovery** - No manual configuration  
✅ **SQL Safety** - Prevents destructive operations  
✅ **Error Recovery** - Automatic retry with corrections  
✅ **Full Observability** - Trace every step  
✅ **DevUI Integration** - Visual testing interface  

## 🚀 Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI and MSSQL settings

# 2. Activate virtual environment
cd /Users/arturoquiroga/GITHUB/agent-framework-public
source .venv/bin/activate

# 3. Launch workflow
python nl2sql-pipeline/nl2sql_workflow.py

# 4. Open browser at http://localhost:8097
```

## 📊 Pipeline Flow

```
User Question
    ↓
Input Normalizer (Executor)
    ↓
Schema Retriever (Executor) → [MSSQL Database]
    ↓
SQL Generator (Agent) → [Azure OpenAI]
    ↓
SQL Validator (Executor)
    ↓
Query Executor (Executor) → [MSSQL Database]
    ↓
Results Interpreter (Agent) → [Azure OpenAI]
    ↓
Natural Language Answer + Insights
```

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

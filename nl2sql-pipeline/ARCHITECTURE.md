# NL2SQL Pipeline Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (DevUI on port 8097)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Natural Language Question
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SEQUENTIAL WORKFLOW                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ 1. INPUT NORMALIZER (Executor)                        │    │
│  │    • Parse user input                                 │    │
│  │    • Validate format                                  │    │
│  │    • Create ChatMessage                               │    │
│  └─────────────────────┬─────────────────────────────────┘    │
│                        │                                        │
│                        ▼                                        │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ 2. SCHEMA RETRIEVER (Executor)                        │    │
│  │    • Connect to MSSQL ──────────────┐                │    │
│  │    • List tables & schemas          │                │    │
│  │    • Format schema context          │                │    │
│  └─────────────────────┬───────────────┼────────────────┘    │
│                        │               │                       │
│                        │               │ MSSQL MCP Tools       │
│                        │               │ • mssql_list_tables   │
│                        │               │ • mssql_list_schemas  │
│                        │               │ • mssql_get_details   │
│                        │               │                       │
│                        ▼               │                       │
│  ┌───────────────────────────────────┼────────────────────┐  │
│  │ 3. SQL GENERATOR (LLM Agent)      │                    │  │
│  │    • Receive question + schema ◄──┘                    │  │
│  │    • Generate SQL query                                │  │
│  │    • Add explanation                                   │  │
│  └─────────────────────┬──────────────────────────────────┘  │
│                        │                                       │
│                        │ Generated SQL                         │
│                        │                                       │
│                        ▼                                       │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 4. SQL VALIDATOR (Executor)                           │   │
│  │    • Parse SQL                                        │   │
│  │    • Safety checks (no DROP/DELETE)                   │   │
│  │    • Add row limits                                   │   │
│  │    • Syntax validation                                │   │
│  └─────────────────────┬─────────────────────────────────┘   │
│                        │                                       │
│                        │ Validated SQL                         │
│                        │                                       │
│                        ▼                                       │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ 5. QUERY EXECUTOR (Executor)                          │   │
│  │    • Execute SQL ────────────────┐                    │   │
│  │    • Handle errors               │                    │   │
│  │    • Format results              │                    │   │
│  └─────────────────────┬────────────┼────────────────────┘   │
│                        │            │                         │
│                        │            │ MSSQL MCP Tools         │
│                        │            │ • mssql_run_query       │
│                        │            │                         │
│                        ▼            │                         │
│  ┌───────────────────────────────┼──────────────────────┐   │
│  │ 6. RESULTS INTERPRETER (Agent)│                       │   │
│  │    • Receive query results ◄──┘                       │   │
│  │    • Generate insights                                │   │
│  │    • Natural language answer                          │   │
│  └─────────────────────┬───────────────────────────────┘    │
│                        │                                      │
└────────────────────────┼──────────────────────────────────────┘
                         │
                         │ Natural Language Answer + Insights
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         USER RESPONSE                           │
│         (Displayed in DevUI with suggestions)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Input Phase
```
User Question (str)
    ↓
UserQuestion (Pydantic Model)
    ↓
ChatMessage(Role.USER, text=question)
```

### 2. Context Enrichment Phase
```
ChatMessage
    ↓
[MSSQL Connection]
    ↓
SchemaContext {
    tables: [...],
    schemas: [...],
    connection_id: "..."
}
    ↓
ChatMessage(Role.SYSTEM, text=schema_context + question)
```

### 3. SQL Generation Phase
```
ChatMessage (with schema)
    ↓
[Azure OpenAI LLM]
    ↓
ChatMessage(Role.ASSISTANT, text="```sql\nSELECT...\n```")
```

### 4. Validation Phase
```
ChatMessage (with SQL)
    ↓
SQL Extraction + Safety Checks
    ↓
ValidatedSQL {
    query: "SELECT...",
    is_safe: true,
    warnings: [...]
}
    ↓
ChatMessage(Role.SYSTEM, text=validated_sql)
```

### 5. Execution Phase
```
ChatMessage (with validated SQL)
    ↓
[MSSQL Database Execution]
    ↓
QueryResults {
    success: true,
    rows: [...],
    row_count: 42,
    columns: [...]
}
    ↓
ChatMessage(Role.SYSTEM, text=formatted_results)
```

### 6. Interpretation Phase
```
ChatMessage (with results)
    ↓
[Azure OpenAI LLM]
    ↓
ChatMessage(Role.ASSISTANT, text=natural_language_answer)
    ↓
[Workflow Output]
```

## Component Details

### Executors (Business Logic)

#### 1. InputNormalizerExecutor
- **Input**: `str` or `UserQuestion`
- **Output**: `ChatMessage`
- **Purpose**: Standardize input format
- **Key Logic**: Format question for LLM processing

#### 2. SchemaRetrieverExecutor
- **Input**: `ChatMessage`
- **Output**: `ChatMessage` (enriched with schema)
- **Purpose**: Provide database context
- **Key Logic**: 
  - Connect to MSSQL via MCP tools
  - Format schema for LLM understanding
  - Cache schema for performance

#### 3. SQLValidatorExecutor
- **Input**: `ChatMessage` (with SQL)
- **Output**: `ChatMessage` (validated SQL)
- **Purpose**: Security and safety
- **Key Logic**:
  - Regex-based SQL extraction
  - Keyword blacklist (DROP, DELETE, etc.)
  - Row limit enforcement
  - Syntax pre-check

#### 4. QueryExecutorExecutor
- **Input**: `ChatMessage` (validated SQL)
- **Output**: `ChatMessage` (query results)
- **Purpose**: Database interaction
- **Key Logic**:
  - Execute via mssql_run_query MCP tool
  - Error handling with context
  - Result formatting for LLM
  - Performance metrics

### Agents (LLM-Powered)

#### 1. SQL Generator Agent
- **Model**: Azure OpenAI (GPT-4)
- **Input**: User question + Database schema
- **Output**: SQL query + explanation
- **Instructions**: 
  - Generate SELECT statements
  - Use proper JOIN syntax
  - Add TOP clauses
  - Include comments
  - Provide explanations

#### 2. Results Interpreter Agent
- **Model**: Azure OpenAI (GPT-4)
- **Input**: Query results + original question
- **Output**: Natural language answer + insights
- **Instructions**:
  - Answer user's question directly
  - Extract key insights
  - Identify patterns
  - Suggest follow-ups

## Technology Stack

```
┌─────────────────────────────────────┐
│   Presentation Layer                │
│   • DevUI (port 8097)              │
│   • REST API endpoints              │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Workflow Layer                    │
│   • Agent Framework                 │
│   • SequentialBuilder              │
│   • WorkflowContext                │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Agent Layer                       │
│   • Azure OpenAI Chat Client       │
│   • ChatAgent (SQL Gen)            │
│   • ChatAgent (Interpreter)        │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Business Logic Layer              │
│   • Custom Executors               │
│   • Validators                     │
│   • Formatters                     │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Integration Layer                 │
│   • MSSQL MCP Server               │
│   • Azure CLI Authentication       │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Data Layer                        │
│   • Azure SQL Database             │
│   • Connection Pool                │
└─────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────┐
│   Authentication Layer              │
│   • Azure CLI (az login)           │
│   • Managed Identity (optional)    │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Authorization Layer               │
│   • SQL Validator (query safety)   │
│   • Row-level filters (optional)   │
│   • Schema restrictions            │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   Audit Layer                       │
│   • Query logging                  │
│   • Performance metrics            │
│   • Error tracking                 │
└─────────────────────────────────────┘
```

## Observability Architecture

```
┌──────────────────────────────────────┐
│   Tracing Layer                      │
│   • OpenTelemetry SDK               │
│   • OTLP Exporter                   │
│   • Console Exporter (dev)          │
└────────────┬─────────────────────────┘
             │
             ├─────────────────────────┐
             │                         │
┌────────────▼──────────┐  ┌──────────▼──────────┐
│  Application Insights │  │  OTLP Receiver      │
│  • Distributed traces │  │  • Jaeger           │
│  • Metrics           │  │  • Zipkin           │
│  • Logs              │  │  • Custom backend   │
└──────────────────────┘  └─────────────────────┘
```

## Deployment Architecture

### Development
```
┌─────────────────────┐
│  Local Machine      │
│  • Python 3.10+    │
│  • .venv           │
│  • DevUI (8097)    │
└──────────┬──────────┘
           │
           ├──────────────────┐
           │                  │
┌──────────▼──────┐  ┌────────▼──────────┐
│  Azure OpenAI   │  │  Azure SQL DB     │
│  • GPT-4        │  │  • Dev Database   │
└─────────────────┘  └───────────────────┘
```

### Production
```
┌────────────────────────────────┐
│  Azure Container Instance      │
│  • Workflow Container         │
│  • Auto-scaling              │
│  • Health checks             │
└───────────┬────────────────────┘
            │
            ├─────────────────────────┐
            │                         │
┌───────────▼──────┐    ┌────────────▼─────────┐
│  Azure OpenAI    │    │  Azure SQL DB        │
│  • Private EP   │    │  • Production        │
│  • VNet         │    │  • Geo-replicated    │
└─────────────────┘    └──────────────────────┘
            │
┌───────────▼──────────────────┐
│  Application Insights        │
│  • Monitoring               │
│  • Alerts                   │
└─────────────────────────────┘
```

## Error Handling Flow

```
User Question
    ↓
┌───────────────────┐
│ Input Validation  │ ───► Error: Invalid format
└────────┬──────────┘
         │ ✓
┌────────▼──────────┐
│ Schema Retrieval  │ ───► Error: Connection failed
└────────┬──────────┘      │
         │ ✓               └─► Retry 3x → User notification
┌────────▼──────────┐
│ SQL Generation    │ ───► Error: LLM timeout
└────────┬──────────┘      │
         │ ✓               └─► Fallback to simpler query
┌────────▼──────────┐
│ SQL Validation    │ ───► Error: Unsafe query
└────────┬──────────┘      │
         │ ✓               └─► Regenerate with constraints
┌────────▼──────────┐
│ Query Execution   │ ───► Error: Syntax/Permission
└────────┬──────────┘      │
         │ ✓               └─► Send error to LLM for fix
┌────────▼──────────┐
│ Interpretation    │ ───► Error: Empty results
└────────┬──────────┘      │
         │ ✓               └─► Explain no matches found
         ▼
    Success
```

## Performance Characteristics

| Component | Avg Latency | Notes |
|-----------|-------------|-------|
| Input Normalizer | <10ms | Pure Python |
| Schema Retriever | 50-200ms | DB round-trip |
| SQL Generator | 1-3s | LLM inference |
| SQL Validator | <50ms | Regex + rules |
| Query Executor | 100ms-5s | Depends on query |
| Results Interpreter | 1-2s | LLM inference |
| **Total Pipeline** | **3-10s** | Typical question |

## Scaling Considerations

### Bottlenecks
1. **LLM Latency** (2-5s per call)
   - Solution: Use streaming responses
   - Cache common queries

2. **Database Connections** (limited pool)
   - Solution: Connection pooling
   - Async query execution

3. **Schema Retrieval** (repeated fetches)
   - Solution: Cache schema for 5-10 minutes
   - Background refresh

### Optimization Strategies
1. Parallel schema + table fetch
2. LLM response streaming
3. Result pagination
4. Query result caching
5. Schema information caching

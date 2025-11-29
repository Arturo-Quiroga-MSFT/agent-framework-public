# NL2SQL Pipeline Architecture

## System Overview

```mermaid
flowchart TD
    UI["USER INTERFACE<br/>(DevUI on port 8097)"] --> |Natural Language Question| WORKFLOW
    
    subgraph WORKFLOW["SEQUENTIAL WORKFLOW"]
        direction TB
        
        Step1["1. INPUT NORMALIZER<br/>(Executor)<br/>• Parse user input<br/>• Validate format<br/>• Create ChatMessage"]
        
        Step2["2. SCHEMA RETRIEVER<br/>(Executor)<br/>• Connect to MSSQL<br/>• List tables & schemas<br/>• Format schema context"]
        
        Step3["3. SQL GENERATOR<br/>(LLM Agent)<br/>• Receive question + schema<br/>• Generate SQL query<br/>• Add explanation"]
        
        Step4["4. SQL VALIDATOR<br/>(Executor)<br/>• Parse SQL<br/>• Safety checks<br/>• Add row limits<br/>• Syntax validation"]
        
        Step5["5. QUERY EXECUTOR<br/>(Executor)<br/>• Execute SQL<br/>• Handle errors<br/>• Format results"]
        
        Step6["6. RESULTS INTERPRETER<br/>(Agent)<br/>• Receive query results<br/>• Generate insights<br/>• Natural language answer"]
        
        Step7["7. DATA EXPORTER<br/>(Executor)<br/>• Export to CSV<br/>• Export to Excel<br/>• Save to exports/<br/>• Timestamp filenames"]
        
        Step8["8. VISUALIZATION GENERATOR<br/>(Executor)<br/>• Analyze data patterns<br/>• Generate charts<br/>• Create bar/line/pie<br/>• Save to visualizations/"]
        
        Step1 --> Step2
        Step2 --> Step3
        Step3 --> Step4
        Step4 --> Step5
        Step5 --> Step6
        Step6 --> Step7
        Step7 --> Step8
    end
    
    MCP[("MSSQL MCP Tools<br/>• mssql_list_tables<br/>• mssql_list_schemas<br/>• mssql_get_details<br/>• mssql_run_query")]
    
    Step2 -.-> MCP
    Step5 -.-> MCP
    
    Step8 --> |Natural Language Answer<br/>+ Insights + CSV/XLS<br/>+ Visualizations| RESPONSE
    
    RESPONSE["USER RESPONSE<br/>(Displayed in DevUI)<br/>• Natural language answer<br/>• Download links for CSV/Excel<br/>• Embedded visualization images"]
    
    style UI fill:#e1f5ff
    style RESPONSE fill:#e1f5ff
    style Step3 fill:#fff4e1
    style Step6 fill:#fff4e1
    style MCP fill:#f0f0f0
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
[Continue to Export Phase]
```

### 7. Data Export Phase
```
QueryResults
    ↓
Data Export (CSV + Excel)
    ↓
ExportedFiles {
    csv_path: "exports/query_results_YYYYMMDD_HHMMSS.csv",
    excel_path: "exports/query_results_YYYYMMDD_HHMMSS.xlsx",
    row_count: 42
}
    ↓
[Continue to Visualization Phase]
```

### 8. Visualization Generation Phase
```
QueryResults + Column Metadata
    ↓
Chart Type Selection (based on data)
    ↓
Visualization Generation (matplotlib/seaborn)
    ↓
VisualizationOutput {
    chart_path: "visualizations/viz_YYYYMMDD_HHMMSS.png",
    chart_type: "bar",
    title: "..."
}
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

#### 5. DataExporterExecutor
- **Input**: `QueryResults`
- **Output**: `ExportedFiles` (CSV + Excel paths)
- **Purpose**: Persist query results for download/analysis
- **Key Logic**:
  - Export to CSV using pandas `to_csv()`
  - Export to Excel using pandas `to_excel()`
  - Timestamp-based filenames
  - Save to `exports/` directory
  - Handle large datasets (chunking if needed)
  - Preserve data types and formatting

#### 6. VisualizationGeneratorExecutor
- **Input**: `QueryResults` + Column metadata
- **Output**: `VisualizationOutput` (chart image path)
- **Purpose**: Automatic chart generation from query results
- **Key Logic**:
  - Analyze data characteristics (numeric, categorical, temporal)
  - Select appropriate chart type:
    - Bar charts for categorical comparisons
    - Line charts for time series
    - Pie charts for proportions
    - Scatter plots for correlations
  - Generate using matplotlib/seaborn
  - Save to `visualizations/` directory
  - Create descriptive titles and labels
  - Handle edge cases (empty data, single value, etc.)

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

```mermaid
flowchart TD
    PL["Presentation Layer<br/>• DevUI (port 8097)<br/>• REST API endpoints<br/>• File download endpoints<br/>• Image display for charts"]
    
    WL["Workflow Layer<br/>• Agent Framework<br/>• SequentialBuilder<br/>• WorkflowContext"]
    
    AL["Agent Layer<br/>• Azure OpenAI Chat Client<br/>• ChatAgent (SQL Gen)<br/>• ChatAgent (Interpreter)"]
    
    BL["Business Logic Layer<br/>• Custom Executors<br/>• Validators<br/>• Formatters<br/>• Data Exporters<br/>• Visualization Generators"]
    
    DP["Data Processing Layer<br/>• pandas (DataFrames)<br/>• matplotlib (Charts)<br/>• seaborn (Advanced viz)<br/>• openpyxl (Excel export)"]
    
    IL["Integration Layer<br/>• MSSQL MCP Server<br/>• Azure CLI Authentication"]
    
    DL["Data Layer<br/>• Azure SQL Database<br/>• Connection Pool"]
    
    SL["Storage Layer<br/>• exports/ (CSV/Excel files)<br/>• visualizations/ (PNG charts)<br/>• Timestamped file management"]
    
    PL --> WL --> AL --> BL --> DP --> IL --> DL --> SL
    
    style PL fill:#e1f5ff
    style WL fill:#fff4e1
    style AL fill:#ffe1f5
    style BL fill:#e1ffe1
    style DP fill:#f5e1ff
    style IL fill:#ffe1e1
    style DL fill:#e1ffe1
    style SL fill:#fff4e1
```

## Security Architecture

```mermaid
flowchart TD
    Auth["Authentication Layer<br/>• Azure CLI (az login)<br/>• Managed Identity (optional)"]
    
    Authz["Authorization Layer<br/>• SQL Validator (query safety)<br/>• Row-level filters (optional)<br/>• Schema restrictions"]
    
    Audit["Audit Layer<br/>• Query logging<br/>• Performance metrics<br/>• Error tracking"]
    
    Auth --> Authz --> Audit
    
    style Auth fill:#ffe1e1
    style Authz fill:#fff4e1
    style Audit fill:#e1f5ff
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

```mermaid
flowchart TD
    Start([User Question]) --> Input[Input Validation]
    
    Input -->|✓| Schema[Schema Retrieval]
    Input -->|Error| E1[Invalid format]
    
    Schema -->|✓| SQLGen[SQL Generation]
    Schema -->|Error| E2[Connection failed] --> R2[Retry 3x] --> N2[User notification]
    
    SQLGen -->|✓| SQLVal[SQL Validation]
    SQLGen -->|Error| E3[LLM timeout] --> F3[Fallback to simpler query]
    
    SQLVal -->|✓| Exec[Query Execution]
    SQLVal -->|Error| E4[Unsafe query] --> R4[Regenerate with constraints]
    
    Exec -->|✓| Interp[Interpretation]
    Exec -->|Error| E5[Syntax/Permission] --> F5[Send error to LLM for fix]
    
    Interp -->|✓| Export[Data Export]
    Interp -->|Error| E6[Empty results] --> F6[Explain no matches found]
    
    Export -->|✓| Viz[Visualization]
    Export -->|Error| E7[File write permission] --> L7[Log error, continue workflow] --> Viz
    
    Viz -->|✓| Success([Success])
    Viz -->|Error| E8[Invalid data for chart] --> L8[Skip viz, log reason] --> Success
    
    style Start fill:#e1f5ff
    style Success fill:#e1ffe1
    style E1 fill:#ffe1e1
    style E2 fill:#ffe1e1
    style E3 fill:#ffe1e1
    style E4 fill:#ffe1e1
    style E5 fill:#ffe1e1
    style E6 fill:#ffe1e1
    style E7 fill:#ffe1e1
    style E8 fill:#ffe1e1
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
| Data Exporter | 50-500ms | File I/O + pandas |
| Visualization Generator | 200ms-2s | Chart rendering |
| **Total Pipeline** | **4-14s** | Typical question |

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
6. Async file exports (CSV/Excel in parallel)
7. Lazy visualization generation (on-demand)
8. Reuse visualizations for identical queries
9. Compress/archive old exports periodically
10. Thumbnail generation for quick preview

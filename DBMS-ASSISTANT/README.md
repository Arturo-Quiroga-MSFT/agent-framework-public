# RDBMS Assistant for Azure SQL Database Administrators

## Overview
An AI-powered assistant for SQL Database administrators to perform daily administrative tasks on Azure SQL databases using natural language. Built on Microsoft's Agent Framework and integrated with the official Microsoft MSSQL MCP Server.

## Project Goals
- Enable DB admins to manage Azure SQL databases using natural language
- Automate routine DBA tasks (health monitoring, performance tuning, troubleshooting)
- Provide intelligent insights and recommendations based on database state
- Ensure safe execution with approval workflows for destructive operations

## Technology Stack

### Core Framework
- **Agent Framework**: Microsoft Agent Framework (MAF) using `AzureAIAgentClient`
- **MCP Server**: `@azure/mssql-mcp-server` (official Microsoft implementation)
- **Authentication**: Azure CLI Credential / Azure Identity
- **Orchestration**: Azure AI Agent Service
- **UI Framework**: Tauri 2.0 (Rust + React) with Pyo3 FFI bridge
- **LLM Models**: GPT-4.1 (primary), GPT-4.1-mini (development/testing)

### Why AzureAIAgentClient?
After comparing `AzureAIClient` vs `AzureAIAgentClient`, we selected `AzureAIAgentClient` because:

| Feature | Benefit for RDBMS Assistant |
|---------|----------------------------|
| **Automatic Lifecycle Management** | Agents are created/deleted per task - perfect for on-demand admin operations |
| **Tool-First Design** | Optimized for function-heavy workflows (MSSQL MCP tools) |
| **Resource Cleanup** | Prevents orphaned agents in Azure AI Foundry |
| **Task-Based Operations** | Each DBA task gets a specialized agent instance |

**Reference Sample**: `/maf-upstream/python/samples/getting_started/agents/azure_ai_agent/azure_ai_basic.py`

### Model Selection: GPT-4.1 vs GPT-4.1-mini

After testing both models extensively, **GPT-4.1 (full)** is recommended for production use:

| Aspect | GPT-4.1-mini | GPT-4.1 |
|--------|--------------|---------|
| **Response Quality** | Good | Excellent |
| **Output Structure** | Clean tables | Professional document-style with sections |
| **Technical Depth** | Provides what | Explains why + what |
| **Decisiveness** | Follows instructions | Zero hesitation, immediate execution |
| **Error Handling** | Reports errors | Explains + fixes automatically |
| **Business Context** | Basic technical | Strong business implications |
| **Formatting** | Markdown tables | Rich formatting with headers, summaries |
| **Cost** | Lower | Higher (~10x) |
| **Speed** | Faster | Slightly slower |

**Key Differences Observed:**
- **GPT-4.1** provides consultant-grade output with better context understanding
- **GPT-4.1** handles SQL errors more gracefully (auto-corrects syntax issues)
- **GPT-4.1** gives more comprehensive recommendations with rationale
- **GPT-4.1-mini** is suitable for development/testing to reduce costs

**Configuration**: Edit `.env` file:
```env
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"  # or "gpt-4.1-mini"
```

## Architecture

```
┌──────────────────────────────────────┐
│   Tauri Desktop UI (React)           │
│   - Natural Language Chat            │
│   - Connection Status                │
│   - Export Chat History              │
│   - Quick Question Templates         │
└────────────┬─────────────────────────┘
             │ IPC Commands
┌────────────▼─────────────────────────┐
│   Rust Backend (src-tauri)           │
│   - Tauri Commands                   │
│   - Python FFI Bridge (Pyo3)         │
│   - Conversation History Tracking    │
└────────────┬─────────────────────────┘
             │ Pyo3 FFI
┌────────────▼─────────────────────────┐
│  Python Agent (dba_assistant.py)     │
│  - AzureAIAgentClient                │
│  - Streaming Response                │
│  - Context Management                │
│  - Embedded Instructions             │
└────────────┬─────────────────────────┘
             │ MCP Stdio
┌────────────▼─────────────────────────┐
│  MSSQL MCP Server (Node.js)          │
│  - Connection Management             │
│  - Query Execution                   │
│  - Schema Discovery                  │
│  - 11 Specialized Tools              │
└────────────┬─────────────────────────┘
             │ SQL Client
┌────────────▼─────────────────────────┐
│  Azure SQL Database                  │
│  - TERADATA-FI (Demo)                │
│  - Star Schema (dim/fact)            │
└──────────────────────────────────────┘
```

## Key Components

### Desktop Application Features

**Tauri 2.0 Architecture:**
- **Frontend**: React 18 with TypeScript
- **Backend**: Rust with Tauri framework
- **FFI Bridge**: Pyo3 for Python integration
- **Agent Execution**: Embedded Python runtime with venv support

**UI Capabilities:**
- Real-time connection status with 5-second polling
- Chat history export to downloadable text files
- Quick question templates for common DBA tasks
- Markdown table rendering with horizontal scroll
- Mermaid ERD diagram support
- Clean, professional dark theme

**Agent Behavioral Features:**
- **Decisive Execution**: No repeated "do you want me to proceed?" questions
- **Context Awareness**: Remembers conversation history across queries
- **Action-Oriented**: Executes plans immediately without asking permission
- **Schema-First Approach**: Validates table/column names before generating SQL
- **Mermaid ERD Output**: Generates text-based diagrams (no image file execution)
- **Comprehensive Responses**: Always shows actual data, not just summaries

### 1. MSSQL MCP Server Tools
The official Microsoft MCP server provides these capabilities:
- **Connection Management**: `mssql_connect`, `mssql_disconnect`, `mssql_change_database`
- **Discovery**: `mssql_list_databases`, `mssql_list_tables`, `mssql_list_views`, `mssql_list_schemas`, `mssql_list_functions`
- **Query Execution**: `mssql_run_query` (with safety validation)
- **Schema Visualization**: `mssql_show_schema`
- **Connection Info**: `mssql_get_connection_details`

**Reference**: [Microsoft DevBlogs - MSSQL MCP Server](https://devblogs.microsoft.com/azure-sql/introducing-mssql-mcp-server/)

### 2. Agent Capabilities

The DBA assistant agent can perform:

**Schema Analysis & Discovery:**
- Database structure review (tables, schemas, relationships)
- Foreign key relationship mapping
- Primary key and index identification
- Column metadata and data type analysis

**Performance Optimization:**
- Index recommendation and creation
- Fragmentation analysis
- Query performance review
- Missing index identification

**Data Operations:**
- Schema modification (ALTER TABLE)
- Synthetic data generation for testing
- Data quality assessment
- Row count and statistics

**Visualization:**
- Mermaid ERD diagram generation
- Foreign key relationship visualization
- Schema documentation in markdown

**Recommendations:**
- Database improvement suggestions
- Index optimization strategies
- Data model enhancements
- Capacity planning insights

### 3. Safety Mechanisms
- **Read-only by default**: Exploration and monitoring use read-only connections
- **Approval workflows**: Destructive operations (DROP, TRUNCATE, DELETE without WHERE) require explicit confirmation
- **Query validation**: Pre-execution validation of SQL queries
- **Audit logging**: All operations logged for compliance

## Development Phases

### Phase 1: Foundation ✅ COMPLETE
- [x] Architecture design
- [x] Technology selection (AzureAIAgentClient)
- [x] Basic agent setup with MCP server integration
- [x] Simple health check operations
- [x] CLI interface working

### Phase 2: Desktop UI ✅ COMPLETE
- [x] Tauri 2.0 application framework
- [x] React frontend with chat interface
- [x] Rust-Python FFI bridge (Pyo3)
- [x] Real-time connection status monitoring
- [x] Chat history export functionality
- [x] Quick question templates for DBAs
- [x] Markdown table formatting for results
- [x] Mermaid ERD diagram generation

### Phase 3: Intelligence & Capabilities ✅ COMPLETE
- [x] Natural language to SQL query generation
- [x] Schema analysis and recommendations
- [x] Index optimization suggestions
- [x] Synthetic data generation
- [x] Database enhancement recommendations
- [x] Proactive schema improvement analysis

### Phase 4: Production Features (In Progress)
- [x] Safety validation framework
- [x] Query execution with tool integration
- [x] Comprehensive agent instructions
- [ ] Multi-database connection management
- [ ] Role-based access control
- [ ] Advanced observability and tracing

## Integration with Existing Workspace

This project leverages existing capabilities:
- **NL2SQL Pipeline** (`/nl2sql-pipeline/`): Natural language query generation
- **Orchestration** (`/AQ-CODE/orchestration/`): Agent coordination patterns
- **Observability** (`/AQ-CODE/observability/`): Performance monitoring and tracing
- **Azure AI** (`/AQ-CODE/azure_ai/`): LLM service integration

## Installation

### Prerequisites
```bash
# Node.js and npm (for MCP server and Tauri)
node --version  # v18+ required
npm --version

# Rust toolchain (for Tauri)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Azure CLI authentication
az login

# Python 3.13+ (for agent framework)
python3 --version
```

### Build MCP Server
```bash
cd DBMS-ASSISTANT/MssqlMcp/Node
npm install
npm run build
```

### Setup Python Environment
```bash
# From repository root
python3 -m venv .venv
source .venv/bin/activate
pip install -r DBMS-ASSISTANT/requirements.txt
```

### Configure Environment
Create `DBMS-ASSISTANT/.env` with:
```env
# Azure AI Project
AZURE_AI_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com/api/projects/yourProject"
AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/"
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"

# Database Connection
SERVER_NAME=your-server.database.windows.net
DATABASE_NAME=your-database
SQL_USERNAME=your-username
SQL_PASSWORD=your-password
TRUST_SERVER_CERTIFICATE=true
READONLY=false
```

### Run Application
```bash
cd DBMS-ASSISTANT/UI
npm install
npm run tauri dev
```

## Configuration

### Environment Variables (.env)

The application uses a comprehensive `.env` file in the `DBMS-ASSISTANT` directory:

**Required Settings:**
```env
# Azure AI Service
AZURE_AI_PROJECT_ENDPOINT="https://your-ai-foundry.services.ai.azure.com/api/projects/yourProject"
AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com/"
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"

# Database Connection
SERVER_NAME=your-server.database.windows.net
DATABASE_NAME=your-database
SQL_USERNAME=your-username
SQL_PASSWORD=your-password
TRUST_SERVER_CERTIFICATE=true
READONLY=false
```

**Optional Settings:**
```env
# Observability
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
ENABLE_OTEL=true
ENABLE_DEVUI_TRACING=true

# Safety
REQUIRE_APPROVAL_FOR_WRITES=true
DRY_RUN_MODE=false
```

See the complete `.env.example` file for all available options.

## Usage

### Desktop Application

**Start the Tauri UI:**
```bash
cd UI
npm install
npm run tauri dev
```

**Build for production:**
```bash
npm run tauri build
```

The application provides:
- Natural language chat interface
- Connection status indicator (server/database info)
- Quick question templates
- Chat history export to text files
- Real-time query execution
- Mermaid ERD diagram generation

### CLI (Legacy)

**Run the Python CLI:**
```bash
cd DBMS-ASSISTANT
source ../.venv/bin/activate
python dba_assistant.py
```

### Example Queries

The agent can handle diverse DBA tasks:

- **Schema Analysis**: "Tell me what kind of DB we have and what can we improve on it"
- **Index Optimization**: "Check for unused indexes or redundant keys"
- **Data Enhancement**: "Generate synthetic data to populate new columns"
- **ERD Generation**: "Generate an ERD diagram" (outputs Mermaid syntax)
- **Performance Tuning**: "Review if dimension tables have appropriate hierarchies"
- **Schema Changes**: "Add geographic location columns to DimCustomer"

## Security Considerations

1. **Authentication**: Uses Azure CLI Credential (can be replaced with Managed Identity in production)
2. **Least Privilege**: Agents use database accounts with minimal required permissions
3. **Query Validation**: All queries validated before execution
4. **Audit Trail**: All operations logged with user, timestamp, and result
5. **Approval Gates**: Destructive operations require explicit approval

## Roadmap

### Completed (Q4 2024)
- ✅ Foundation architecture with AzureAIAgentClient
- ✅ MSSQL MCP Server integration
- ✅ Tauri desktop application with React UI
- ✅ Rust-Python FFI bridge (Pyo3)
- ✅ Natural language to SQL capabilities
- ✅ Mermaid ERD diagram generation
- ✅ Schema analysis and recommendations
- ✅ Index optimization features
- ✅ Synthetic data generation

### Planned Enhancements
- **Multi-Database Management**: Support multiple concurrent connections
- **Advanced Observability**: Integration with Azure Monitor and Application Insights
- **Query History**: Save and replay previous queries
- **Export Formats**: PDF and Excel export for reports
- **Saved Templates**: Custom query templates per user
- **Role-Based Access**: Fine-grained permission control
- **Backup Management**: Backup status monitoring and recommendations
- **Performance Dashboards**: Real-time performance metrics visualization

## References

- [Microsoft MSSQL MCP Server Blog](https://devblogs.microsoft.com/azure-sql/introducing-mssql-mcp-server/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Azure AI Agent Service](https://learn.microsoft.com/azure/ai-services/agents/)

## License
MIT (following workspace conventions)

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

### Why AzureAIAgentClient?
After comparing `AzureAIClient` vs `AzureAIAgentClient`, we selected `AzureAIAgentClient` because:

| Feature | Benefit for RDBMS Assistant |
|---------|----------------------------|
| **Automatic Lifecycle Management** | Agents are created/deleted per task - perfect for on-demand admin operations |
| **Tool-First Design** | Optimized for function-heavy workflows (MSSQL MCP tools) |
| **Resource Cleanup** | Prevents orphaned agents in Azure AI Foundry |
| **Task-Based Operations** | Each DBA task gets a specialized agent instance |

**Reference Sample**: `/maf-upstream/python/samples/getting_started/agents/azure_ai_agent/azure_ai_basic.py`

## Architecture

```
┌──────────────────────────┐
│   Admin Interface        │  (CLI)
│   - Natural Language     │
│   - Task Selection       │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│  Agent Orchestrator      │  (AzureAIAgentClient)
│  - Task Routing          │
│  - Safety Validation     │
│  - Context Management    │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│  Specialized Agents      │
│  ├─ Health Monitor       │
│  ├─ Performance Tuner    │
│  ├─ Backup Manager       │
│  └─ Security Auditor     │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│  MSSQL MCP Server        │  (@azure/mssql-mcp-server)
│  - mssql_connect         │
│  - mssql_run_query       │
│  - mssql_list_*          │
│  - mssql_show_schema     │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│  Azure SQL Databases     │
└──────────────────────────┘
```

## Key Components

### 1. MSSQL MCP Server Tools
The official Microsoft MCP server provides these capabilities:
- **Connection Management**: `mssql_connect`, `mssql_disconnect`, `mssql_change_database`
- **Discovery**: `mssql_list_databases`, `mssql_list_tables`, `mssql_list_views`, `mssql_list_schemas`, `mssql_list_functions`
- **Query Execution**: `mssql_run_query` (with safety validation)
- **Schema Visualization**: `mssql_show_schema`
- **Connection Info**: `mssql_get_connection_details`

**Reference**: [Microsoft DevBlogs - MSSQL MCP Server](https://devblogs.microsoft.com/azure-sql/introducing-mssql-mcp-server/)

### 2. Specialized Agent Types

#### Health Monitor Agent
- Check database health metrics
- Monitor index fragmentation
- Analyze wait statistics
- Detect blocking sessions

#### Performance Tuner Agent
- Query execution plan analysis
- Missing index recommendations
- Statistics update suggestions
- Resource utilization monitoring

#### Backup Manager Agent
- Backup status verification
- Recovery model checks
- Backup scheduling recommendations
- Point-in-time recovery scenarios

#### Security Auditor Agent
- Permission audits
- Login reviews
- Security vulnerability checks
- Compliance reporting

### 3. Safety Mechanisms
- **Read-only by default**: Exploration and monitoring use read-only connections
- **Approval workflows**: Destructive operations (DROP, TRUNCATE, DELETE without WHERE) require explicit confirmation
- **Query validation**: Pre-execution validation of SQL queries
- **Audit logging**: All operations logged for compliance

## Development Phases

### Phase 1: Foundation (Current)
- [x] Architecture design
- [x] Technology selection (AzureAIAgentClient)
- [ ] Basic agent setup with MCP server integration
- [ ] Simple health check operations

### Phase 2: Core Features
- [ ] Implement all specialized agents
- [ ] Safety validation framework
- [ ] Query template library (DMVs, system views)
- [ ] Basic CLI interface

### Phase 3: Intelligence Layer
- [ ] Natural language to admin task mapping
- [ ] Proactive recommendations
- [ ] Anomaly detection
- [ ] Integration with Azure Monitor

### Phase 4: Production Ready
- [ ] Web UI (framework TBD)
- [ ] Multi-database management
- [ ] Role-based access control
- [ ] Comprehensive audit logging

## Integration with Existing Workspace

This project leverages existing capabilities:
- **NL2SQL Pipeline** (`/nl2sql-pipeline/`): Natural language query generation
- **Orchestration** (`/AQ-CODE/orchestration/`): Agent coordination patterns
- **Observability** (`/AQ-CODE/observability/`): Performance monitoring and tracing
- **Azure AI** (`/AQ-CODE/azure_ai/`): LLM service integration

## Installation

### Prerequisites
```bash
# Install MSSQL MCP Server
npm install -g @azure/mssql-mcp-server

# Azure CLI authentication
az login

# Python environment
python -m venv .venv
source .venv/bin/activate
```

### Dependencies (to be added)
```bash
pip install agent-framework azure-identity mcp httpx pydantic
```

## Configuration

### Environment Variables (.env)
```env
# Azure AI Service
AZURE_AI_PROJECT_CONNECTION_STRING=<your-connection-string>

# Optional: OpenAI for alternative LLM
OPENAI_API_KEY=<your-key>

# Database Connections (managed via MCP server)
# Configured in VS Code SQL extension
```

## Usage Examples

### Basic Health Check
```python
async with AzureAIAgentClient(credential).create_agent(
    name="HealthMonitor",
    instructions="You check SQL database health and report issues.",
    tools=[mssql_connect, mssql_run_query],
) as agent:
    result = await agent.run("Check index fragmentation on production database")
    print(result)
```

### Performance Analysis
```python
async with AzureAIAgentClient(credential).create_agent(
    name="PerformanceTuner",
    instructions="You analyze query performance and suggest optimizations.",
    tools=[mssql_connect, mssql_run_query, get_execution_plan],
) as agent:
    result = await agent.run("Find the top 5 slowest queries in the last hour")
    print(result)
```

## Security Considerations

1. **Authentication**: Uses Azure CLI Credential (can be replaced with Managed Identity in production)
2. **Least Privilege**: Agents use database accounts with minimal required permissions
3. **Query Validation**: All queries validated before execution
4. **Audit Trail**: All operations logged with user, timestamp, and result
5. **Approval Gates**: Destructive operations require explicit approval

## Roadmap

- **Q4 2024**: Foundation and core features
- **Q1 2025**: Intelligence layer and recommendations
- **Q2 2025**: Production deployment and web UI
- **Q3 2025**: Advanced features (multi-cloud support, ML-based anomaly detection)

## References

- [Microsoft MSSQL MCP Server Blog](https://devblogs.microsoft.com/azure-sql/introducing-mssql-mcp-server/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Azure AI Agent Service](https://learn.microsoft.com/azure/ai-services/agents/)

## License
MIT (following workspace conventions)

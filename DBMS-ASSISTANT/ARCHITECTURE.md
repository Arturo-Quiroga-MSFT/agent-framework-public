# RDBMS Assistant - Architecture Decision Record

## Date
November 29, 2025

## Status
Approved

## Context

We need to build an AI-powered assistant for SQL Database administrators working with Azure SQL databases. The assistant should:
- Handle daily DBA tasks through natural language
- Integrate with existing Azure SQL infrastructure
- Provide safe, auditable database operations
- Scale to multiple databases and concurrent operations

## Decision Drivers

1. **Official Microsoft Support**: Need production-ready, maintained tooling
2. **Safety First**: Database operations must be validated and auditable
3. **Existing Infrastructure**: Leverage Microsoft Agent Framework already in use
4. **VS Code Integration**: Seamless workflow with existing SQL tools

## Considered Options

### Option 1: AzureAIClient (Chat-focused)
**Location**: `/maf-upstream/python/samples/getting_started/agents/azure_ai/azure_ai_basic.py`

**Pros**:
- Simpler API
- Good for chat scenarios
- Less boilerplate

**Cons**:
- Manual agent lifecycle management
- Not optimized for tool-heavy workflows
- Requires explicit cleanup

### Option 2: AzureAIAgentClient (Agent-focused) ✅ SELECTED
**Location**: `/maf-upstream/python/samples/getting_started/agents/azure_ai_agent/azure_ai_basic.py`

**Pros**:
- Automatic agent creation/deletion within context managers
- Tool-first design pattern
- Better resource management
- Purpose-built for task-based agent operations
- Scales well with multiple specialized agents

**Cons**:
- Slightly more boilerplate
- Requires understanding of context managers

### Option 3: Custom LangGraph Implementation
**Pros**:
- Maximum flexibility
- Direct control over agent behavior

**Cons**:
- More development time
- Need to maintain custom orchestration
- Reinventing what MAF already provides

## Decision

**Selected: Option 2 - AzureAIAgentClient**

### Rationale

1. **Perfect Fit for DBA Tasks**: Each database admin task (health check, backup verification, performance tuning) maps naturally to a specialized agent with automatic lifecycle
   
2. **Tool Integration**: The MSSQL MCP Server provides 13+ tools. `AzureAIAgentClient` is designed for tool-heavy workflows

3. **Resource Efficiency**: Automatic cleanup prevents orphaned agents in Azure AI Foundry

4. **Production Ready**: Official Microsoft implementation with enterprise support

5. **Scalability**: Can easily spawn multiple agents for concurrent database operations

## Implementation Strategy

### Agent Specialization
Each DBA domain gets a specialized agent:

```python
# Health Monitoring
async with AzureAIAgentClient(credential).create_agent(
    name="HealthMonitor",
    instructions="You monitor database health metrics.",
    tools=[mssql_connect, mssql_run_query, check_fragmentation]
) as agent:
    await agent.run(user_query)

# Performance Tuning  
async with AzureAIAgentClient(credential).create_agent(
    name="PerformanceTuner",
    instructions="You analyze and optimize query performance.",
    tools=[mssql_connect, mssql_run_query, analyze_plan]
) as agent:
    await agent.run(user_query)
```

### MSSQL MCP Server Integration

**Package**: `@azure/mssql-mcp-server`

**Key Tools** (13 available):
1. Connection: `mssql_connect`, `mssql_disconnect`, `mssql_change_database`, `mssql_get_connection_details`
2. Discovery: `mssql_list_databases`, `mssql_list_tables`, `mssql_list_views`, `mssql_list_schemas`, `mssql_list_functions`
3. Execution: `mssql_run_query`
4. Visualization: `mssql_show_schema`

**Integration Method**: MCP protocol via VS Code extension

### Safety Architecture

```
User Request
    ↓
┌───────────────────┐
│ Intent Classifier │ → Determine if read-only or write operation
└────────┬──────────┘
         ↓
    ┌────────┐
    │ Router │
    └───┬────┘
        ↓
   ╔════════════╗
   ║ Read-only? ║
   ╚════╤═══════╝
        │
    Yes │ No
        │  ↓
        │ ┌──────────────────┐
        │ │ Query Validator  │ → Check for destructive patterns
        │ └────────┬─────────┘
        │          ↓
        │     ┌─────────┐
        │     │ Approve?│ → User confirmation required
        │     └────┬────┘
        ↓          ↓
┌────────────────────┐
│ Execute via MCP    │
└────────┬───────────┘
         ↓
┌────────────────────┐
│ Audit Log          │
└────────────────────┘
```

## Consequences

### Positive
- Fast development using proven patterns
- Enterprise-grade reliability
- Seamless VS Code integration
- Automatic resource management
- Scales naturally with workload

### Negative
- Dependency on Azure AI Agent Service
- Requires Azure subscription
- Learning curve for MCP protocol

### Mitigation
- Document MCP integration patterns
- Provide fallback to direct SQL execution for development
- Create comprehensive examples

## Technical Specifications

### Language & Runtime
- Python 3.11+
- AsyncIO for concurrent operations
- Type hints throughout

### Key Dependencies
```python
agent-framework          # Microsoft Agent Framework
azure-identity           # Azure authentication
mcp                      # Model Context Protocol client
pydantic                 # Data validation
httpx                    # HTTP client for APIs
```

### Authentication Flow
```
Developer Machine
    ↓
az login (Azure CLI)
    ↓
AzureCliCredential
    ↓
AzureAIAgentClient
    ↓
Azure AI Agent Service
    ↓
LLM (GPT-4, etc.)
```

### Data Flow
```
User Query (Natural Language)
    ↓
AzureAIAgentClient.run()
    ↓
LLM (determine tools to call)
    ↓
MCP Server Tools (MSSQL operations)
    ↓
Azure SQL Database
    ↓
Results back through stack
    ↓
Natural Language Response
```

## Future Considerations

1. **Multi-Cloud Support**: Extend to AWS RDS, Google Cloud SQL
2. **Advanced Analytics**: ML-based anomaly detection on database metrics
3. **Proactive Monitoring**: Scheduled health checks and alerts
4. **Web Interface**: Gradio UI for non-CLI users
5. **Multi-Tenancy**: Support for managing hundreds of databases

## References

- [AzureAIAgentClient Sample](../maf-upstream/python/samples/getting_started/agents/azure_ai_agent/azure_ai_basic.py)
- [MSSQL MCP Server Blog](https://devblogs.microsoft.com/azure-sql/introducing-mssql-mcp-server/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Azure AI Agent Service Documentation](https://learn.microsoft.com/azure/ai-services/agents/)

## Team
- Architecture: Arturo Quiroga
- Framework: Microsoft Agent Framework Team
- MCP Integration: Microsoft Azure SQL Team

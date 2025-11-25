# LangGraph to MCP Server Integration Guide

This guide explains how to expose LangGraph agents as Model Context Protocol (MCP) servers, enabling them to be called by MAF orchestrators in a cloud-agnostic manner.

## Overview

**Goal**: Convert a LangGraph agent into an MCP server that can be deployed anywhere and called by MAF workflows.

**Benefits**:
- ✅ Standard interface (MCP protocol)
- ✅ Language-agnostic communication
- ✅ Reusable across workflows
- ✅ Independent deployment and scaling
- ✅ Cloud-agnostic (works on Azure, AWS, GCP, on-prem)

## Architecture

```
┌────────────────────────────────────────┐
│     LangGraph Agent (Python)           │
│  • StateGraph definition               │
│  • Node functions                      │
│  • Edge conditions                     │
│  • Tool integrations                   │
└──────────────┬─────────────────────────┘
               │ Wrapped by
┌──────────────▼─────────────────────────┐
│     MCP Server Layer                   │
│  • HTTP/gRPC endpoints                 │
│  • Tool definitions (JSON schema)      │
│  • Request validation                  │
│  • Response formatting                 │
└──────────────┬─────────────────────────┘
               │ Network (HTTP/gRPC)
┌──────────────▼─────────────────────────┐
│     MAF Orchestrator                   │
│  • MCPExecutor calls server            │
│  • Workflow coordination               │
└────────────────────────────────────────┘
```

## Step-by-Step Implementation

### Step 1: Create LangGraph Agent

```python
# sql_optimizer_agent.py
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI

# Define agent state
class SQLAgentState(TypedDict):
    query: str
    database_schema: str
    optimized_sql: str
    explanation: str
    confidence: float

class SQLOptimizerAgent:
    """LangGraph agent for SQL optimization"""
    
    def __init__(self, llm):
        self.llm = llm
        self.graph = self._build_graph()
        self.agent = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(SQLAgentState)
        
        # Add nodes
        graph.add_node("analyze", self.analyze_query)
        graph.add_node("optimize", self.optimize_query)
        graph.add_node("validate", self.validate_sql)
        
        # Define flow
        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "optimize")
        graph.add_edge("optimize", "validate")
        
        # Conditional end
        graph.add_conditional_edges(
            "validate",
            self.should_retry,
            {
                "retry": "optimize",
                "done": END
            }
        )
        
        return graph
    
    def analyze_query(self, state: SQLAgentState) -> SQLAgentState:
        """Analyze the input query"""
        analysis_prompt = f"""
        Analyze this SQL query for optimization opportunities:
        Query: {state['query']}
        Schema: {state['database_schema']}
        """
        
        response = self.llm.invoke(analysis_prompt)
        state['explanation'] = response.content
        return state
    
    def optimize_query(self, state: SQLAgentState) -> SQLAgentState:
        """Generate optimized SQL"""
        optimize_prompt = f"""
        Based on this analysis: {state['explanation']}
        
        Original query: {state['query']}
        Schema: {state['database_schema']}
        
        Generate an optimized SQL query.
        """
        
        response = self.llm.invoke(optimize_prompt)
        state['optimized_sql'] = response.content
        return state
    
    def validate_sql(self, state: SQLAgentState) -> SQLAgentState:
        """Validate the optimized SQL"""
        # Add validation logic
        state['confidence'] = 0.95
        return state
    
    def should_retry(self, state: SQLAgentState) -> Literal["retry", "done"]:
        """Decide whether to retry optimization"""
        return "done" if state['confidence'] > 0.8 else "retry"
    
    async def ainvoke(self, input_data: dict) -> dict:
        """Async invoke method for MCP server"""
        result = await self.agent.ainvoke(input_data)
        return result
```

### Step 2: Create MCP Server Wrapper

```python
# mcp_server.py
import asyncio
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from sql_optimizer_agent import SQLOptimizerAgent
from langchain_openai import AzureChatOpenAI
import os

# Initialize LangGraph agent
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-02-15-preview"
)

sql_agent = SQLOptimizerAgent(llm)

# Create MCP server
server = Server("teradata-sql-optimizer")

# Register tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="optimize_sql",
            description="Optimize a SQL query for better performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to optimize"
                    },
                    "database_schema": {
                        "type": "string",
                        "description": "Database schema information"
                    }
                },
                "required": ["query", "database_schema"]
            }
        ),
        Tool(
            name="analyze_query",
            description="Analyze a SQL query without optimization",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to analyze"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tool calls"""
    
    if name == "optimize_sql":
        # Run LangGraph agent
        result = await sql_agent.ainvoke({
            "query": arguments["query"],
            "database_schema": arguments.get("database_schema", ""),
            "optimized_sql": "",
            "explanation": "",
            "confidence": 0.0
        })
        
        return [
            TextContent(
                type="text",
                text=f"""
Optimized SQL:
{result['optimized_sql']}

Explanation:
{result['explanation']}

Confidence: {result['confidence']}
"""
            )
        ]
    
    elif name == "analyze_query":
        # Simpler analysis without full optimization
        analysis_prompt = f"Analyze this SQL query: {arguments['query']}"
        response = llm.invoke(analysis_prompt)
        
        return [
            TextContent(
                type="text",
                text=response.content
            )
        ]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# Health check endpoint
@server.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "sql-optimizer"}

if __name__ == "__main__":
    # Run MCP server
    server.run(
        host="0.0.0.0",
        port=int(os.getenv("MCP_PORT", "8080"))
    )
```

### Step 3: Containerize the MCP Server

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY sql_optimizer_agent.py .
COPY mcp_server.py .

# Expose MCP port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run server
CMD ["python", "mcp_server.py"]
```

```txt
# requirements.txt
langgraph>=0.2.0
langchain-openai>=0.2.0
mcp>=1.0.0
uvicorn>=0.30.0
fastapi>=0.110.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### Step 4: Deploy to Any Cloud

**Local Development:**
```bash
# Build
docker build -t teradata/sql-optimizer:latest .

# Run
docker run -d \
  -p 8080:8080 \
  -e AZURE_OPENAI_ENDPOINT="https://..." \
  -e AZURE_OPENAI_KEY="..." \
  -e AZURE_OPENAI_DEPLOYMENT="gpt-4" \
  teradata/sql-optimizer:latest
```

**Kubernetes (Any Cloud):**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sql-optimizer-agent
  labels:
    app: sql-optimizer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sql-optimizer
  template:
    metadata:
      labels:
        app: sql-optimizer
    spec:
      containers:
      - name: agent
        image: teradata/sql-optimizer:latest
        ports:
        - containerPort: 8080
          name: mcp
        env:
        - name: MCP_PORT
          value: "8080"
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: openai-secrets
              key: endpoint
        - name: AZURE_OPENAI_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secrets
              key: api-key
        - name: AZURE_OPENAI_DEPLOYMENT
          value: "gpt-4"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: sql-optimizer-service
spec:
  selector:
    app: sql-optimizer
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: ClusterIP
```

### Step 5: Call from MAF Orchestrator

```python
# maf_orchestrator.py
from agent_framework import SequentialBuilder
from agent_framework.executors import Executor, handler
from agent_framework.workflow import WorkflowContext
import httpx
import os

class MCPClientExecutor(Executor):
    """Call MCP server from MAF workflow"""
    
    def __init__(self, server_url: str, tool_name: str):
        self.server_url = server_url
        self.tool_name = tool_name
    
    @handler
    async def execute(self, input_data: dict, ctx: WorkflowContext) -> None:
        """Execute MCP tool call"""
        
        async with httpx.AsyncClient() as client:
            # Call MCP server
            response = await client.post(
                f"{self.server_url}/tools/call",
                json={
                    "name": self.tool_name,
                    "arguments": input_data
                },
                timeout=60.0
            )
            
            result = response.json()
            
            # Send result to next step
            await ctx.send_message(result)

# Build workflow
def create_sql_optimization_workflow():
    # Get MCP server URL (works in any environment)
    # In Kubernetes: sql-optimizer-service:8080
    # In Azure: https://sql-optimizer.azurewebsites.net
    # In AWS: https://sql-optimizer.execute-api.us-east-1.amazonaws.com
    mcp_url = os.getenv(
        "SQL_OPTIMIZER_URL",
        "http://sql-optimizer-service:8080"
    )
    
    return (
        SequentialBuilder()
        .add_executor(InputValidator())
        .add_executor(SchemaRetriever())
        .add_executor(MCPClientExecutor(
            server_url=mcp_url,
            tool_name="optimize_sql"
        ))
        .add_executor(QueryExecutor())
        .add_executor(ResultsFormatter())
        .build()
    )

# Run workflow
async def main():
    workflow = create_sql_optimization_workflow()
    
    result = await workflow.run({
        "user_query": "SELECT * FROM customers WHERE city = 'New York'"
    })
    
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Advanced Patterns

### Pattern 1: Multiple Tools in One Server

```python
# Multi-tool MCP server
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="optimize_sql", ...),
        Tool(name="analyze_query", ...),
        Tool(name="generate_indexes", ...),
        Tool(name="explain_plan", ...),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Route to different LangGraph agents
    if name == "optimize_sql":
        return await sql_optimizer_agent.ainvoke(arguments)
    elif name == "analyze_query":
        return await query_analyzer_agent.ainvoke(arguments)
    elif name == "generate_indexes":
        return await index_generator_agent.ainvoke(arguments)
    # ... etc
```

### Pattern 2: Streaming Responses

```python
from mcp.types import StreamContent

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Stream agent responses"""
    
    if name == "optimize_sql":
        # Stream LangGraph execution
        async for chunk in sql_agent.astream(arguments):
            yield StreamContent(
                type="stream",
                text=chunk.get("optimized_sql", "")
            )
```

### Pattern 3: State Management with MCP

```python
from langgraph.checkpoint.postgres import PostgresCheckpointer

# Add checkpointing to LangGraph agent
checkpointer = PostgresCheckpointer(
    connection_string=os.getenv("POSTGRES_URL")
)

sql_agent = sql_optimizer_graph.compile(
    checkpointer=checkpointer
)

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Use thread_id for conversation continuity
    thread_id = arguments.get("thread_id", "default")
    
    result = await sql_agent.ainvoke(
        arguments,
        config={"configurable": {"thread_id": thread_id}}
    )
    
    return result
```

### Pattern 4: Error Handling and Retries

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@server.call_tool()
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_tool(name: str, arguments: dict):
    try:
        result = await sql_agent.ainvoke(arguments)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        # Log error
        logger.error(f"Agent error: {e}")
        
        # Return error response
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
```

## Testing

### Unit Test LangGraph Agent

```python
# test_sql_agent.py
import pytest
from sql_optimizer_agent import SQLOptimizerAgent

@pytest.mark.asyncio
async def test_sql_optimization():
    agent = SQLOptimizerAgent(mock_llm)
    
    result = await agent.ainvoke({
        "query": "SELECT * FROM users",
        "database_schema": "users (id, name, email)",
        "optimized_sql": "",
        "explanation": "",
        "confidence": 0.0
    })
    
    assert result["optimized_sql"]
    assert result["confidence"] > 0.0
```

### Integration Test MCP Server

```python
# test_mcp_server.py
import pytest
import httpx

@pytest.mark.asyncio
async def test_mcp_optimize_tool():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/tools/call",
            json={
                "name": "optimize_sql",
                "arguments": {
                    "query": "SELECT * FROM users WHERE active = 1",
                    "database_schema": "users (id, name, email, active)"
                }
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "optimized_sql" in str(result)
```

### End-to-End Test with MAF

```python
# test_e2e.py
import pytest
from maf_orchestrator import create_sql_optimization_workflow

@pytest.mark.asyncio
async def test_full_workflow():
    workflow = create_sql_optimization_workflow()
    
    result = await workflow.run({
        "user_query": "Show me all customers"
    })
    
    assert result["optimized_sql"]
    assert result["execution_results"]
```

## Monitoring and Observability

### Add OpenTelemetry to MCP Server

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Setup tracing
tracer = trace.get_tracer(__name__)

# Instrument FastAPI (if using FastAPI for MCP)
FastAPIInstrumentor.instrument_app(server.app)

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    with tracer.start_as_current_span("mcp_tool_call") as span:
        span.set_attribute("tool.name", name)
        span.set_attribute("query.length", len(arguments.get("query", "")))
        
        start_time = time.time()
        result = await sql_agent.ainvoke(arguments)
        latency = time.time() - start_time
        
        span.set_attribute("latency.seconds", latency)
        span.set_attribute("confidence", result.get("confidence", 0))
        
        return result
```

## Production Checklist

- [ ] Health check endpoint implemented
- [ ] Error handling and retries configured
- [ ] Logging structured and centralized
- [ ] OpenTelemetry tracing enabled
- [ ] Resource limits set (memory, CPU)
- [ ] Environment variables externalized
- [ ] Secrets managed securely
- [ ] Container image scanned for vulnerabilities
- [ ] Horizontal scaling configured
- [ ] Monitoring and alerting setup
- [ ] Documentation complete

## Next Steps

- [Architecture Patterns](ARCHITECTURE_PATTERNS.md) - Deployment patterns
- [MAF Cloud Adapters](MAF_CLOUD_ADAPTERS.md) - Cloud abstractions
- [Deployment Strategies](DEPLOYMENT_STRATEGIES.md) - Infrastructure setup

---

**Author**: Arturo Quiroga  
**Date**: November 24, 2025

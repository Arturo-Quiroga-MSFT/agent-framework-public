# Architecture Patterns for LangGraph + MAF Integration

This document provides detailed architecture patterns for integrating LangGraph agents with MAF orchestration in cloud-agnostic deployments.

## Pattern Categories

1. [Integration Patterns](#integration-patterns) - How LangGraph and MAF connect
2. [Deployment Patterns](#deployment-patterns) - How to deploy across clouds
3. [Communication Patterns](#communication-patterns) - How components interact
4. [State Management Patterns](#state-management-patterns) - How to handle persistence
5. [Observability Patterns](#observability-patterns) - How to monitor and trace

---

## Integration Patterns

### Pattern 1.1: MCP Server Sidecar

**Structure:**
```
┌─────────────────────────────────────────┐
│  Kubernetes Pod / Container Group       │
├─────────────────────────────────────────┤
│  Container 1: LangGraph Agent           │
│    • Runs agent logic                   │
│    • Exposes MCP on localhost:8080      │
│                                         │
│  Container 2: MAF Orchestrator          │
│    • Runs workflow                      │
│    • Calls localhost:8080 (MCP)         │
└─────────────────────────────────────────┘
```

**Benefits:**
- Fast localhost communication
- Co-located deployment
- Simplified service discovery
- Works on any Kubernetes (AKS, EKS, GKE)

**Example Kubernetes Manifest:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: teradata-agent-pod
spec:
  containers:
  - name: langgraph-agent
    image: teradata/langgraph-sql-agent:latest
    ports:
    - containerPort: 8080
      name: mcp
    env:
    - name: MCP_PORT
      value: "8080"
    
  - name: maf-orchestrator
    image: teradata/maf-orchestrator:latest
    env:
    - name: LANGGRAPH_AGENT_URL
      value: "http://localhost:8080"
    - name: CLOUD_PROVIDER
      value: "kubernetes"
```

**When to Use:**
- Low-latency requirements
- Simplified deployment
- Single workflow using specific agent
- Cost optimization (shared resources)

---

### Pattern 1.2: Microservices with Service Mesh

**Structure:**
```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  SQL Optimizer   │     │  Query Analyzer  │     │  Data Profiler   │
│  (LangGraph)     │     │  (LangGraph)     │     │  (LangGraph)     │
│  MCP Server      │     │  MCP Server      │     │  MCP Server      │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                        │                        │
         │         Service Mesh / Load Balancer            │
         └───────────────────┬────────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │  MAF Orchestrator       │
                │  (Service Discovery)    │
                └─────────────────────────┘
```

**Benefits:**
- Independent scaling per agent
- Language/framework flexibility per service
- Rolling updates per component
- Service mesh features (retries, circuit breakers, observability)

**Example with Service Discovery:**
```python
from agent_framework import SequentialBuilder
from agent_framework.executors import MCPExecutor

class TeradataOrchestrator:
    def __init__(self, service_registry: ServiceRegistry):
        self.registry = service_registry
        
    def build_workflow(self):
        # Discover services dynamically
        sql_optimizer_url = self.registry.get_service("sql-optimizer")
        query_analyzer_url = self.registry.get_service("query-analyzer")
        
        return (
            SequentialBuilder()
            .add_executor(MCPExecutor(
                server_url=sql_optimizer_url,
                tool_name="optimize_sql"
            ))
            .add_executor(MCPExecutor(
                server_url=query_analyzer_url,
                tool_name="analyze_query"
            ))
            .build()
        )
```

**Service Discovery Options:**
- **Kubernetes**: Built-in DNS (service-name.namespace.svc.cluster.local)
- **Consul**: HashiCorp Consul (cloud-agnostic)
- **Cloud-Native**: Azure Service Fabric, AWS Cloud Map, GCP Service Directory

**When to Use:**
- Multiple specialized agents
- Need independent scaling
- Complex agent ecosystem
- Production workloads with high availability

---

### Pattern 1.3: Embedded Executor (Monolithic)

**Structure:**
```python
from agent_framework import SequentialBuilder
from agent_framework.executors import Executor
from langgraph.graph import StateGraph

class LangGraphExecutor(Executor):
    """Embed LangGraph directly in MAF workflow"""
    
    def __init__(self, agent: StateGraph):
        self.agent = agent.compile()
    
    @handler
    async def execute(self, input_data: dict, ctx: WorkflowContext) -> None:
        result = await self.agent.ainvoke(input_data)
        await ctx.send_message(result)

# Build workflow
sql_agent = create_sql_optimization_agent()

workflow = (
    SequentialBuilder()
    .add_executor(InputValidator())
    .add_executor(LangGraphExecutor(sql_agent))  # Embedded
    .add_executor(ResultsProcessor())
    .build()
)
```

**Benefits:**
- Simplest deployment (single process)
- No network overhead
- Shared memory and state
- Easier local debugging

**Drawbacks:**
- Tight coupling
- No independent scaling
- Language lock-in (Python only)
- Harder to reuse agents

**When to Use:**
- Simple workflows with one agent
- Development and testing
- Low-latency critical paths
- Resource-constrained environments

---

## Deployment Patterns

### Pattern 2.1: Container-Based Multi-Cloud

**Single Docker Image Strategy:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt \
    && pip install azure-storage-blob boto3 google-cloud-storage

# Copy application code
COPY agents/ /app/agents/
COPY orchestrator/ /app/orchestrator/
COPY adapters/ /app/adapters/

WORKDIR /app

# Runtime configuration via environment
ENV CLOUD_PROVIDER=auto-detect
ENV AGENT_TYPE=sql-optimizer

CMD ["python", "orchestrator/main.py"]
```

**Cloud-Specific Deployment:**

**Azure Container Instances:**
```bash
az container create \
  --resource-group teradata-rg \
  --name sql-agent \
  --image teradata/agent:1.0 \
  --environment-variables \
    CLOUD_PROVIDER=azure \
    AZURE_STORAGE_CONNECTION="${STORAGE_CONN}"
```

**AWS ECS Fargate:**
```json
{
  "family": "teradata-agent",
  "containerDefinitions": [{
    "name": "agent",
    "image": "teradata/agent:1.0",
    "environment": [
      {"name": "CLOUD_PROVIDER", "value": "aws"},
      {"name": "AWS_REGION", "value": "us-east-1"}
    ]
  }]
}
```

**GCP Cloud Run:**
```bash
gcloud run deploy teradata-agent \
  --image teradata/agent:1.0 \
  --set-env-vars CLOUD_PROVIDER=gcp \
  --region us-central1
```

**Kubernetes (Universal):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: teradata-agent
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: agent
        image: teradata/agent:1.0
        env:
        - name: CLOUD_PROVIDER
          value: kubernetes  # Auto-detects underlying cloud
```

---

### Pattern 2.2: Serverless Functions

**Function-per-Agent Pattern:**

**Azure Functions:**
```python
# function_app.py
import azure.functions as func
from langgraph_agents import SQLOptimizerAgent

app = func.FunctionApp()
agent = SQLOptimizerAgent()

@app.route(route="optimize")
async def optimize_sql(req: func.HttpRequest) -> func.HttpResponse:
    query = req.get_json()["query"]
    result = await agent.invoke({"query": query})
    return func.HttpResponse(json.dumps(result), mimetype="application/json")
```

**AWS Lambda:**
```python
# lambda_function.py
import json
from langgraph_agents import SQLOptimizerAgent

agent = SQLOptimizerAgent()  # Initialize once (warm start)

def lambda_handler(event, context):
    query = json.loads(event['body'])['query']
    result = agent.invoke({"query": query})
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

**GCP Cloud Functions:**
```python
# main.py
import functions_framework
from langgraph_agents import SQLOptimizerAgent

agent = SQLOptimizerAgent()

@functions_framework.http
def optimize_sql(request):
    query = request.get_json()['query']
    result = agent.invoke({"query": query})
    return result
```

**MAF Orchestrator Calls Functions:**
```python
class ServerlessMCPExecutor(Executor):
    """Call serverless functions as MCP tools"""
    
    def __init__(self, function_url: str, cloud: str):
        self.url = function_url
        self.cloud = cloud
        self.client = self._get_client()
    
    def _get_client(self):
        if self.cloud == "azure":
            return DefaultAzureCredential()
        elif self.cloud == "aws":
            return boto3.client('lambda')
        elif self.cloud == "gcp":
            return functions_v2.FunctionServiceClient()
    
    @handler
    async def execute(self, input_data: dict, ctx: WorkflowContext):
        # Call function with auth
        result = await self._invoke_function(input_data)
        await ctx.send_message(result)
```

**When to Use:**
- Intermittent workloads
- Pay-per-use cost model
- Auto-scaling requirements
- Stateless agents

---

### Pattern 2.3: Hybrid Multi-Region

**Architecture:**
```
         Primary Region (Azure)              Secondary Region (AWS)
┌────────────────────────────────┐    ┌──────────────────────────────┐
│  MAF Orchestrator (Active)     │    │  MAF Orchestrator (Standby)  │
│  LangGraph Agents              │◄───┤  LangGraph Agents            │
│  Azure Storage                 │    │  S3 Storage                  │
│  Cosmos DB (State)             │◄───┤  DynamoDB (State Replica)    │
└────────────────────────────────┘    └──────────────────────────────┘
                │                                    │
                └──────────── Traffic Manager ──────┘
```

**Benefits:**
- High availability across clouds
- Disaster recovery
- Geo-distributed users
- No single cloud dependency

**State Replication:**
```python
class MultiCloudStateManager:
    """Replicate state across clouds"""
    
    def __init__(self):
        self.primary = CosmosDBCheckpointer(...)  # Azure
        self.secondary = DynamoDBCheckpointer(...) # AWS
    
    async def save_state(self, state: dict):
        # Write to primary
        await self.primary.save(state)
        
        # Async replicate to secondary
        asyncio.create_task(self.secondary.save(state))
    
    async def load_state(self, key: str):
        try:
            return await self.primary.load(key)
        except Exception:
            # Failover to secondary
            return await self.secondary.load(key)
```

---

## Communication Patterns

### Pattern 3.1: Synchronous MCP Call

**Flow:**
```
MAF Orchestrator
    │
    │ 1. HTTP POST /tools/optimize
    ▼
MCP Server (LangGraph Agent)
    │
    │ 2. Execute agent graph
    │ 3. Return result
    ▼
MAF Orchestrator
    │
    │ 4. Continue workflow
```

**Implementation:**
```python
# MAF side
async def call_agent(query: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://sql-agent:8080/tools/optimize",
            json={"query": query},
            timeout=30.0
        )
        return response.json()["result"]

# LangGraph MCP server side
from mcp.server import Server

server = Server("sql-optimizer")

@server.call_tool()
async def optimize(query: str) -> str:
    result = await sql_agent.ainvoke({"query": query})
    return result["optimized_sql"]
```

---

### Pattern 3.2: Asynchronous with Callbacks

**Flow:**
```
MAF Orchestrator
    │ 1. POST /tools/analyze (callback_url=...)
    ▼
MCP Server
    │ 2. Return 202 Accepted
    │ 3. Process async
    │ 4. POST callback_url (result)
    ▼
MAF Orchestrator
    │ 5. Continue workflow
```

**Implementation:**
```python
# MAF orchestrator
class AsyncMCPExecutor(Executor):
    @handler
    async def execute(self, input_data: dict, ctx: WorkflowContext):
        # Start async job
        job_id = await self.start_job(input_data)
        
        # Wait for callback or poll
        result = await self.wait_for_result(job_id)
        
        await ctx.send_message(result)

# LangGraph MCP server
@server.call_tool()
async def analyze_async(query: str, callback_url: str) -> dict:
    job_id = str(uuid.uuid4())
    
    # Start background task
    asyncio.create_task(
        process_and_callback(query, callback_url, job_id)
    )
    
    return {"job_id": job_id, "status": "processing"}

async def process_and_callback(query, callback_url, job_id):
    result = await agent.ainvoke({"query": query})
    
    # POST result to callback
    async with httpx.AsyncClient() as client:
        await client.post(callback_url, json={
            "job_id": job_id,
            "result": result
        })
```

---

### Pattern 3.3: Event-Driven (Message Queue)

**Architecture:**
```
MAF Orchestrator
    │ 1. Publish to "sql-optimize-requests"
    ▼
Message Queue (Azure Service Bus / AWS SQS / GCP Pub/Sub)
    │
    ▼
LangGraph Agent Consumer
    │ 2. Process message
    │ 3. Publish to "sql-optimize-results"
    ▼
MAF Orchestrator
    │ 4. Consume result, continue
```

**Benefits:**
- Decoupling
- Buffering during load spikes
- Retry and dead-letter handling
- Works across clouds

**Implementation:**
```python
# Cloud-agnostic queue abstraction
class MessageQueue(ABC):
    @abstractmethod
    async def publish(self, topic: str, message: dict): pass
    
    @abstractmethod
    async def subscribe(self, topic: str) -> AsyncIterator[dict]: pass

# MAF orchestrator
class QueueBasedMCPExecutor(Executor):
    def __init__(self, queue: MessageQueue):
        self.queue = queue
    
    @handler
    async def execute(self, input_data: dict, ctx: WorkflowContext):
        request_id = str(uuid.uuid4())
        
        # Publish request
        await self.queue.publish("agent-requests", {
            "request_id": request_id,
            "data": input_data
        })
        
        # Wait for response
        async for message in self.queue.subscribe("agent-responses"):
            if message["request_id"] == request_id:
                await ctx.send_message(message["result"])
                break
```

---

## State Management Patterns

### Pattern 4.1: Shared State Store

**Architecture:**
```
LangGraph Agent 1 ──┐
                    ├──► Shared State Store (PostgreSQL/Redis)
LangGraph Agent 2 ──┤       • Thread states
                    │       • Checkpoints
MAF Orchestrator ───┘       • Conversation history
```

**Universal PostgreSQL Checkpointer:**
```python
from langgraph.checkpoint.postgres import PostgresCheckpointer

# Works on any cloud with PostgreSQL
checkpointer = PostgresCheckpointer(
    connection_string=os.getenv("POSTGRES_URL")
)

# Azure: Azure Database for PostgreSQL
# AWS: RDS PostgreSQL
# GCP: Cloud SQL PostgreSQL
# On-prem: Self-hosted PostgreSQL

agent = graph.compile(checkpointer=checkpointer)
```

---

### Pattern 4.2: Cloud-Native State Backends

**Multi-Backend Abstraction:**
```python
from abc import ABC, abstractmethod

class StateBackend(ABC):
    @abstractmethod
    async def save_checkpoint(self, thread_id: str, state: dict): pass
    
    @abstractmethod
    async def load_checkpoint(self, thread_id: str) -> dict: pass

class CosmosDBBackend(StateBackend):
    async def save_checkpoint(self, thread_id: str, state: dict):
        await self.container.upsert_item({
            "id": thread_id,
            "state": state,
            "timestamp": datetime.utcnow().isoformat()
        })

class DynamoDBBackend(StateBackend):
    async def save_checkpoint(self, thread_id: str, state: dict):
        self.table.put_item(Item={
            "thread_id": thread_id,
            "state": state,
            "timestamp": int(time.time())
        })

class FirestoreBackend(StateBackend):
    async def save_checkpoint(self, thread_id: str, state: dict):
        doc_ref = self.db.collection("checkpoints").document(thread_id)
        await doc_ref.set({
            "state": state,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

# Factory
def get_state_backend() -> StateBackend:
    if CLOUD == "azure":
        return CosmosDBBackend()
    elif CLOUD == "aws":
        return DynamoDBBackend()
    elif CLOUD == "gcp":
        return FirestoreBackend()
```

---

## Observability Patterns

### Pattern 5.1: OpenTelemetry Everywhere

**Universal Tracing:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing():
    provider = TracerProvider()
    
    # Cloud-specific exporter
    exporter = get_exporter_for_cloud()
    
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

# In LangGraph agent
tracer = trace.get_tracer("langgraph.sql_optimizer")

async def optimize_query(state):
    with tracer.start_as_current_span("optimize_query") as span:
        span.set_attribute("query_length", len(state["query"]))
        
        result = await llm.ainvoke(state["query"])
        
        span.set_attribute("tokens_used", result.token_count)
        return result

# In MAF orchestrator (automatic tracing built-in)
```

---

### Pattern 5.2: Unified Logging

**Structured Logging:**
```python
import structlog

# Configure once
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Use everywhere
logger.info("agent_invoked",
    agent_type="sql_optimizer",
    cloud=CLOUD,
    thread_id=thread_id,
    latency_ms=latency
)
```

**Send to Cloud Logging:**
```python
# Azure: Application Insights
# AWS: CloudWatch Logs
# GCP: Cloud Logging
# On-prem: ELK Stack / Loki

def get_log_handler():
    if CLOUD == "azure":
        return AzureLogHandler(connection_string=APPINSIGHTS_CONN)
    elif CLOUD == "aws":
        return CloudWatchLogHandler(log_group=LOG_GROUP)
    elif CLOUD == "gcp":
        return CloudLoggingHandler(project=PROJECT_ID)
    else:
        return logging.StreamHandler()
```

---

## Pattern Summary

| Pattern | Use Case | Complexity | Cloud Portability |
|---------|----------|------------|-------------------|
| MCP Sidecar | Low latency, simple deployment | Low | ⭐⭐⭐⭐⭐ |
| Microservices | Multiple agents, independent scaling | Medium | ⭐⭐⭐⭐⭐ |
| Embedded Executor | Development, simple workflows | Low | ⭐⭐⭐⭐⭐ |
| Container Multi-Cloud | Production workloads | Medium | ⭐⭐⭐⭐⭐ |
| Serverless | Intermittent workloads | Medium | ⭐⭐⭐⭐ |
| Hybrid Multi-Region | HA/DR requirements | High | ⭐⭐⭐⭐⭐ |
| Sync MCP | Simple request/response | Low | ⭐⭐⭐⭐⭐ |
| Async Callbacks | Long-running tasks | Medium | ⭐⭐⭐⭐⭐ |
| Event-Driven Queue | Decoupled, buffered | Medium | ⭐⭐⭐⭐ |
| Shared State Store | Universal persistence | Low | ⭐⭐⭐⭐⭐ |
| Cloud-Native State | Optimized per cloud | Medium | ⭐⭐⭐ |

---

**Next**: [Deployment Strategies](DEPLOYMENT_STRATEGIES.md) for detailed infrastructure guides.

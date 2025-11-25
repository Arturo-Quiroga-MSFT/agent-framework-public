# LangGraph + MAF Integration Overview

## Executive Summary

This document outlines the strategic integration of **LangGraph** (agent logic) with **Microsoft Agent Framework (MAF)** (orchestration) to create a cloud-agnostic AI agent platform for Teradata that can deploy seamlessly across Azure, AWS, GCP, and on-premises infrastructure.

## Why This Integration?

### The Challenge
Teradata customers require:
- Advanced AI agent capabilities
- Multi-cloud deployment flexibility
- No vendor lock-in
- Enterprise-grade orchestration
- Production-ready infrastructure

### The Solution: LangGraph + MAF

**LangGraph** provides:
- ✅ Graph-based agent reasoning
- ✅ Stateful conversations with memory
- ✅ Complex multi-step workflows
- ✅ Tool calling and function execution
- ✅ Pure Python (no cloud dependencies)

**MAF** provides:
- ✅ Enterprise workflow orchestration
- ✅ Multi-agent coordination
- ✅ OpenTelemetry observability
- ✅ Error handling and retries
- ✅ Cloud integration patterns

**MCP Protocol** provides:
- ✅ Universal agent communication standard
- ✅ Interoperability across frameworks
- ✅ No vendor lock-in
- ✅ Future-proof architecture

## Integration Patterns

### Pattern 1: LangGraph as MCP Server (Recommended)

**Architecture:**
```
┌─────────────────────────────────────┐
│     LangGraph Agent                 │
│  (SQL Optimization Logic)           │
│  • Graph-based reasoning            │
│  • State management                 │
│  • Tool calling                     │
└──────────────┬──────────────────────┘
               │ Exposed via MCP
┌──────────────▼──────────────────────┐
│     MCP Server Interface            │
│  • HTTP/gRPC endpoints              │
│  • Standard tool definitions        │
└──────────────┬──────────────────────┘
               │ Network call
┌──────────────▼──────────────────────┐
│     MAF Orchestrator                │
│  • Workflow coordination            │
│  • Calls agent via MCP              │
│  • Handles errors/retries           │
└─────────────────────────────────────┘
```

**Benefits:**
- Clear separation of concerns
- LangGraph focuses on reasoning
- MAF focuses on orchestration
- Agents are reusable across workflows
- Easy to test independently

**Use Cases:**
- Complex SQL generation with multi-step reasoning
- Query optimization requiring state/memory
- Data analysis with tool calling
- Any workflow needing advanced agent capabilities

### Pattern 2: LangGraph as MAF Executor

**Architecture:**
```
┌─────────────────────────────────────┐
│     MAF Workflow                    │
├─────────────────────────────────────┤
│  [1] Input Validator (Executor)    │
│  [2] Schema Retriever (Executor)   │
│  [3] LangGraph Agent (Executor) ◄──┐
│  [4] Query Executor (Executor)     │ Embedded
│  [5] Results Processor (Executor)  │ directly
└─────────────────────────────────────┘
```

**Benefits:**
- Tighter integration
- Shared context/state
- Lower latency (no network)
- Simpler deployment

**Use Cases:**
- Single workflow with embedded agent
- Low-latency requirements
- Simple agent logic
- Monolithic deployment acceptable

### Pattern 3: Hybrid (Recommended for Production)

**Architecture:**
```
┌─────────────────────────────────────┐
│     MAF Orchestration Workflow      │
├─────────────────────────────────────┤
│  [1] Simple Executors (Direct)     │
│  [2] Complex Agent (MCP) ──────────┼───► LangGraph Agent 1
│  [3] Simple Executors (Direct)     │
│  [4] Complex Agent (MCP) ──────────┼───► LangGraph Agent 2
│  [5] Simple Executors (Direct)     │
└─────────────────────────────────────┘
```

**Benefits:**
- Use right tool for the job
- Simple logic stays in MAF executors
- Complex reasoning delegated to LangGraph
- Flexible scaling
- Optimal performance

## Component Responsibilities

### LangGraph Agents (Business Logic)

**Responsible For:**
- ✅ AI reasoning and decision making
- ✅ Multi-step problem solving
- ✅ State management across turns
- ✅ Tool selection and calling
- ✅ Context window management
- ✅ Prompt engineering

**NOT Responsible For:**
- ❌ Workflow orchestration
- ❌ Error recovery strategies
- ❌ Cloud service integration
- ❌ Observability infrastructure
- ❌ Deployment concerns

**Example:**
```python
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

# LangGraph agent focuses on reasoning
class SQLOptimizationAgent:
    def __init__(self):
        self.graph = StateGraph(AgentState)
        
        # Define reasoning steps
        self.graph.add_node("analyze", self.analyze_query)
        self.graph.add_node("optimize", self.optimize_query)
        self.graph.add_node("validate", self.validate_query)
        self.graph.add_node("tools", ToolNode(self.tools))
        
        # Define flow logic
        self.graph.add_conditional_edges(
            "analyze",
            self.should_optimize,
            {
                "optimize": "optimize",
                "done": END
            }
        )
        
    def analyze_query(self, state):
        # Complex reasoning here
        return state
```

### MAF Orchestration (Infrastructure)

**Responsible For:**
- ✅ Overall workflow coordination
- ✅ Calling agents at right time
- ✅ Error handling and retries
- ✅ Parallel execution
- ✅ Cloud service integration
- ✅ Observability and tracing
- ✅ Resource management

**NOT Responsible For:**
- ❌ AI reasoning logic
- ❌ Prompt construction
- ❌ Model selection
- ❌ Agent-specific state

**Example:**
```python
from agent_framework import SequentialBuilder
from agent_framework.executors import MCPExecutor, Executor

# MAF orchestrator focuses on coordination
class TeradataWorkflow:
    def __init__(self):
        self.workflow = (
            SequentialBuilder()
            # Simple logic: direct executor
            .add_executor(InputValidator())
            .add_executor(SchemaRetriever())
            
            # Complex reasoning: delegate to LangGraph
            .add_executor(MCPExecutor(
                server_url="http://sql-optimizer:8080",
                tool_name="optimize"
            ))
            
            # Simple logic: direct executor
            .add_executor(QueryExecutor())
            .add_executor(ResultsFormatter())
            
            .build()
        )
```

## Cloud Agnostic Architecture

### Abstraction Layers

```
┌─────────────────────────────────────────────────────┐
│         Application Layer (Cloud Agnostic)          │
│  • LangGraph agents (pure Python)                  │
│  • MAF workflows (core framework)                  │
│  • Business logic                                  │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│         Abstraction Layer (Adapters)                │
│  • Storage Interface → Azure/AWS/GCP/PostgreSQL    │
│  • Database Interface → Various DB drivers         │
│  • Secrets Interface → KeyVault/Secrets Manager    │
│  • Observability → OTLP exporter                   │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│         Cloud Provider Layer                        │
│  • Azure: Blob, Cosmos DB, Key Vault, App Insights│
│  • AWS: S3, DynamoDB, Secrets Manager, X-Ray       │
│  • GCP: GCS, Firestore, Secret Manager, Trace     │
│  • On-Prem: MinIO, PostgreSQL, Vault, Jaeger      │
└─────────────────────────────────────────────────────┘
```

### Storage Abstraction Example

```python
from abc import ABC, abstractmethod

class StorageProvider(ABC):
    """Cloud-agnostic storage interface"""
    
    @abstractmethod
    async def save(self, key: str, data: bytes) -> str:
        """Save data, return URL"""
        pass
    
    @abstractmethod
    async def load(self, key: str) -> bytes:
        """Load data by key"""
        pass
    
    @abstractmethod
    async def list(self, prefix: str) -> list[str]:
        """List keys with prefix"""
        pass

class AzureBlobStorage(StorageProvider):
    def __init__(self, connection_string: str):
        self.client = BlobServiceClient(connection_string)
    
    async def save(self, key: str, data: bytes) -> str:
        blob = self.client.get_blob_client("container", key)
        await blob.upload_blob(data)
        return blob.url

class S3Storage(StorageProvider):
    def __init__(self, bucket: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket
    
    async def save(self, key: str, data: bytes) -> str:
        await self.s3.put_object(Bucket=self.bucket, Key=key, Body=data)
        return f"s3://{self.bucket}/{key}"

class GCSStorage(StorageProvider):
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
    
    async def save(self, key: str, data: bytes) -> str:
        blob = self.bucket.blob(key)
        await blob.upload_from_string(data)
        return blob.public_url

# Factory pattern for runtime selection
def get_storage() -> StorageProvider:
    provider = os.getenv("CLOUD_PROVIDER", "azure")
    
    if provider == "azure":
        return AzureBlobStorage(os.getenv("AZURE_STORAGE_CONNECTION"))
    elif provider == "aws":
        return S3Storage(os.getenv("AWS_S3_BUCKET"))
    elif provider == "gcp":
        return GCSStorage(os.getenv("GCP_BUCKET_NAME"))
    else:
        raise ValueError(f"Unknown provider: {provider}")
```

## State Management Strategy

### LangGraph Checkpointing (Multi-Backend)

```python
from langgraph.checkpoint import CheckpointSaver

# Azure: Cosmos DB
if CLOUD == "azure":
    checkpointer = CosmosDBCheckpointer(
        connection_string=os.getenv("COSMOS_CONNECTION"),
        database_name="teradata",
        container_name="agent_state"
    )

# AWS: DynamoDB
elif CLOUD == "aws":
    checkpointer = DynamoDBCheckpointer(
        table_name="teradata-agent-state",
        region="us-east-1"
    )

# GCP: Firestore
elif CLOUD == "gcp":
    checkpointer = FirestoreCheckpointer(
        project_id="teradata-agents",
        collection="agent_state"
    )

# Universal: PostgreSQL (works everywhere)
else:
    checkpointer = PostgresCheckpointer(
        connection_string=os.getenv("POSTGRES_URL")
    )

# Use with LangGraph
agent = graph.compile(checkpointer=checkpointer)
```

## Observability Across Clouds

### OpenTelemetry (Universal Standard)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Single configuration works everywhere
def setup_tracing():
    provider = TracerProvider()
    
    # Send to cloud-specific backend
    if CLOUD == "azure":
        # Azure Application Insights
        exporter = OTLPSpanExporter(
            endpoint=os.getenv("APPLICATIONINSIGHTS_ENDPOINT")
        )
    elif CLOUD == "aws":
        # AWS X-Ray
        exporter = OTLPSpanExporter(
            endpoint="localhost:4317"  # X-Ray collector
        )
    elif CLOUD == "gcp":
        # GCP Cloud Trace
        exporter = OTLPSpanExporter(
            endpoint="localhost:4317"  # Cloud Trace agent
        )
    else:
        # Jaeger (works anywhere)
        exporter = OTLPSpanExporter(
            endpoint="jaeger:4317"
        )
    
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
```

## Deployment Flexibility

### Container-Based (Recommended)

**Single Image, Multiple Targets:**
```dockerfile
# Dockerfile (builds once, runs anywhere)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy agent code
COPY langgraph_agents/ ./agents/
COPY maf_orchestrator/ ./orchestrator/
COPY cloud_adapters/ ./adapters/

# Environment-based configuration
ENV CLOUD_PROVIDER=azure
ENV MCP_PORT=8080

CMD ["python", "orchestrator/main.py"]
```

**Deploy to Azure:**
```bash
az container create \
  --resource-group teradata-rg \
  --name agent-container \
  --image teradata/agent:latest \
  --environment-variables CLOUD_PROVIDER=azure
```

**Deploy to AWS:**
```bash
aws ecs run-task \
  --cluster teradata-cluster \
  --task-definition agent-task \
  --overrides '{"containerOverrides": [{"name": "agent", "environment": [{"name": "CLOUD_PROVIDER", "value": "aws"}]}]}'
```

**Deploy to GCP:**
```bash
gcloud run deploy agent \
  --image teradata/agent:latest \
  --set-env-vars CLOUD_PROVIDER=gcp
```

**Deploy to Kubernetes (Any Cloud):**
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
        image: teradata/agent:latest
        env:
        - name: CLOUD_PROVIDER
          value: kubernetes  # Auto-detect cloud
```

## Security Considerations

### Secrets Management (Cloud-Agnostic)

```python
from abc import ABC, abstractmethod

class SecretsProvider(ABC):
    @abstractmethod
    async def get_secret(self, name: str) -> str:
        pass

class AzureKeyVaultSecrets(SecretsProvider):
    async def get_secret(self, name: str) -> str:
        client = SecretClient(vault_url=VAULT_URL, credential=DefaultAzureCredential())
        return (await client.get_secret(name)).value

class AWSSecretsManager(SecretsProvider):
    async def get_secret(self, name: str) -> str:
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId=name)
        return response['SecretString']

class GCPSecretManager(SecretsProvider):
    async def get_secret(self, name: str) -> str:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT}/secrets/{name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode('UTF-8')

# Factory
def get_secrets_provider() -> SecretsProvider:
    if CLOUD == "azure":
        return AzureKeyVaultSecrets()
    elif CLOUD == "aws":
        return AWSSecretsManager()
    elif CLOUD == "gcp":
        return GCPSecretManager()
```

## Migration Path

### Phase 1: Single Cloud (Weeks 1-2)
1. Build LangGraph agent
2. Create MCP server wrapper
3. Implement MAF orchestrator
4. Deploy to primary cloud (e.g., Azure)
5. Validate functionality

### Phase 2: Add Abstractions (Weeks 3-4)
1. Identify cloud-specific dependencies
2. Create abstraction interfaces
3. Implement adapters for primary cloud
4. Test with abstraction layer

### Phase 3: Multi-Cloud (Weeks 5-6)
1. Implement adapters for secondary clouds
2. Test deployment to AWS
3. Test deployment to GCP
4. Validate feature parity

### Phase 4: Production Hardening (Weeks 7-8)
1. Security review
2. Performance optimization
3. CI/CD automation
4. Documentation
5. Training

## Success Metrics

- ✅ **Code Reuse**: >95% of code shared across clouds
- ✅ **Deployment Time**: <30 minutes to new cloud
- ✅ **Performance**: <5% overhead from abstraction
- ✅ **Observability**: Full traces across all deployments
- ✅ **Developer Experience**: Local testing without cloud
- ✅ **Production Readiness**: HA, DR, monitoring

## Next Steps

1. **Review Architecture**: Validate with Teradata stakeholders
2. **Choose Pilot Use Case**: Select first agent to build
3. **Set Up Development Environment**: Local tools and cloud access
4. **Build Reference Implementation**: End-to-end example
5. **Document Patterns**: Reusable templates and best practices

## Resources

- [Architecture Patterns](ARCHITECTURE_PATTERNS.md)
- [Deployment Strategies](DEPLOYMENT_STRATEGIES.md)
- [LangGraph MCP Integration](LANGGRAPH_MCP_INTEGRATION.md)
- [Cloud Adapters Guide](MAF_CLOUD_ADAPTERS.md)

---

**Author**: Arturo Quiroga  
**Date**: November 24, 2025  
**Status**: Design Review

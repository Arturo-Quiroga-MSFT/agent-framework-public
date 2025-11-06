# Production Deployment Strategy for Microsoft Agent Framework

## Response to: "What's the recommended approach for production deployment with enterprise-grade capabilities?"

**Date:** November 6, 2025  
**Context:** Customer with existing AKS APIs wanting to integrate enterprise-grade agents

---

## Executive Summary

Your understanding is **correct**, but let me provide additional context and clarify the deployment paths:

### Current State (November 2025)

1. **Agent Framework** - Open-source framework for building AI agents
   - ✅ Production-ready for custom deployments
   - ✅ Full control over infrastructure and deployment
   - ✅ Works with Azure AI Foundry backend services
   - ✅ Perfect for containerized deployments (AKS, ACA)

2. **AI Agents in Azure AI Foundry** (Agent Hosted Service)
   - ✅ Managed hosting environment for agents
   - ✅ Built on Agent Framework under the hood
   - ✅ Serverless execution model
   - ✅ Integrated with Foundry governance & monitoring

---

## Recommended Approach for Your Customer

### Scenario: Customer with existing AKS infrastructure + custom APIs

**✅ Recommended: Containerize Agent Framework + Deploy to AKS/ACA**

**Why this approach:**

1. **Seamless Integration with Existing Infrastructure**
   - Agents run in same environment as APIs
   - Private networking / VNet integration
   - Existing security policies apply
   - Unified logging, monitoring, and alerting

2. **Full Control & Customization**
   - Custom middleware and authentication
   - Direct API access without extra hops
   - Custom scaling policies
   - Bring your own observability tools

3. **Enterprise-Grade Security**
   - Keep traffic within private network
   - Use existing identity & access management
   - Comply with data residency requirements
   - Fine-grained network policies

4. **Cost Optimization**
   - Leverage existing AKS capacity
   - No per-invocation charges (like hosted service)
   - Predictable costs for high-volume scenarios

5. **Migration Path to Foundry Hosted Service**
   - Agent Framework code **is compatible** with Foundry Hosted Service
   - Can migrate later when/if it makes sense
   - No code rewrite needed - just deployment target changes

---

## Deployment Architecture Options

### Option 1: Agent Framework on AKS (Recommended for this customer)

```
┌─────────────────────────────────────────────────────────┐
│                     Azure AKS Cluster                   │
│                                                         │
│  ┌──────────────┐         ┌─────────────────────┐     │
│  │  Agent API   │◄────────┤  Customer APIs      │     │
│  │  (Container) │         │  (Existing Workload)│     │
│  └──────┬───────┘         └─────────────────────┘     │
│         │                                              │
│         │ Private Network                              │
│         ▼                                              │
│  ┌──────────────────────────────────────┐             │
│  │  Agent Framework Implementation      │             │
│  │  - Custom Tools (API integrations)   │             │
│  │  - Authentication middleware         │             │
│  │  - Business logic                    │             │
│  └──────┬───────────────────────────────┘             │
└─────────┼───────────────────────────────────────────────┘
          │
          ▼
   ┌─────────────────────┐
   │ Azure AI Foundry    │
   │ (Model Backend)     │
   │ - GPT-4, etc.       │
   │ - Search, etc.      │
   └─────────────────────┘
```

**Deployment Steps:**
1. Containerize Agent Framework app (using Dockerfile we just created)
2. Push to Azure Container Registry (ACR)
3. Deploy to AKS with Helm or kubectl
4. Configure private endpoints to Azure AI Foundry
5. Integrate with existing API services via service mesh

**Benefits:**
- ✅ All traffic stays within customer's VNet
- ✅ Direct API access (no external calls)
- ✅ Existing security/compliance policies apply
- ✅ Can use AKS features (auto-scaling, pod identity, service mesh)

### Option 2: Agent Framework on Azure Container Apps

```
┌─────────────────────────────────────────┐
│  Azure Container Apps                   │
│                                         │
│  ┌──────────────────┐                  │
│  │  Agent Service   │                  │
│  │  (Serverless)    │                  │
│  └────────┬─────────┘                  │
└───────────┼─────────────────────────────┘
            │
            │ HTTPS / Private Link
            ▼
┌─────────────────────────────────────────┐
│  Azure AKS (Customer APIs)              │
│                                         │
│  ┌─────────────────────┐               │
│  │  Internal APIs      │               │
│  │  - Exposed via      │               │
│  │    Private Link or  │               │
│  │    APIM             │               │
│  └─────────────────────┘               │
└─────────────────────────────────────────┘
```

**When to use:**
- Agents don't need ultra-low latency to APIs
- Want serverless scaling (0 to N)
- Prefer managed infrastructure over self-managed
- APIs can be exposed via Private Link or API Management

### Option 3: AI Foundry Agent Hosted Service (Future state)

```
┌─────────────────────────────────────────┐
│  Azure AI Foundry                       │
│  Agent Hosted Service                   │
│                                         │
│  ┌──────────────────┐                  │
│  │  Managed Agent   │                  │
│  │  Execution       │                  │
│  └────────┬─────────┘                  │
└───────────┼─────────────────────────────┘
            │
            │ Via API Management / Private Link
            ▼
┌─────────────────────────────────────────┐
│  Customer APIs in AKS                   │
└─────────────────────────────────────────┘
```

**When this makes sense:**
- Customer wants fully managed agent infrastructure
- Foundry Hosted Service supports private endpoints (roadmap)
- Customer values Foundry governance > infrastructure control
- Cost model works for usage patterns

---

## Why Agent Framework is Production-Ready

### Common Misconception
❌ "Agent Framework is only for development/prototyping"

### Reality
✅ **Agent Framework is production-grade and designed for enterprise deployment**

**Evidence:**
1. **Used by Microsoft internally** for production workloads
2. **Open-source** but enterprise-maintained
3. **Supports all Azure AI capabilities** (models, search, tools)
4. **Built-in observability** (OpenTelemetry, App Insights)
5. **Async/await patterns** for high performance
6. **Extensible** with custom tools and middleware

### What Makes It Production-Ready

```python
# Example: Production-grade Agent Framework implementation
class EnterpriseAgent:
    def __init__(self):
        # 1. Managed Identity for auth
        self.credential = DefaultAzureCredential()
        
        # 2. Observability
        self.observability = MAFObservability()
        
        # 3. Cost tracking
        self.cost_tracker = CostTracker()
        
        # 4. Custom tools (customer APIs)
        self.tools = [
            CustomAPITool(api_endpoint="https://internal-api"),
            DatabaseQueryTool(connection_string=secret),
        ]
        
        # 5. Quality evaluation
        self.evaluator = AgentEvaluator()
    
    async def run(self, query: str):
        # Thread management for conversation
        thread = self.get_or_create_thread()
        
        # Execute with full observability
        with self.observability.create_span("agent.execute"):
            result = await self.agent.run(query, thread=thread)
        
        # Track costs and quality
        self.cost_tracker.record(...)
        metrics = self.evaluator.evaluate(result)
        
        return result
```

**Production Features:**
- ✅ Thread management for conversations
- ✅ Retry logic and error handling
- ✅ Rate limiting and budget controls
- ✅ Custom tool integration
- ✅ Distributed tracing
- ✅ Metrics and monitoring

---

## Decision Matrix

| Requirement | AKS + Agent Framework | ACA + Agent Framework | Foundry Hosted Service |
|-------------|----------------------|----------------------|----------------------|
| **Private API access** | ✅ Native | ⚠️ Via Private Link | ⚠️ Via Private Link |
| **Ultra-low latency** | ✅ Same cluster | ⚠️ Separate service | ⚠️ Separate service |
| **Custom middleware** | ✅ Full control | ✅ Full control | ❌ Limited |
| **Existing AKS integration** | ✅ Seamless | ⚠️ External | ⚠️ External |
| **Infrastructure mgmt** | ⚠️ Self-managed | ✅ Managed | ✅ Fully managed |
| **Scaling flexibility** | ✅ Full control | ✅ Auto-scale | ✅ Auto-scale |
| **Cost model** | 💰 Fixed | 💰 Consumption | 💰 Per-invocation |
| **Data residency** | ✅ Full control | ✅ Regional | ⚠️ Shared tenant |
| **Foundry governance** | ⚠️ Via APIs | ⚠️ Via APIs | ✅ Native |
| **Migration effort** | Low | Low | Very Low |

**Legend:**
- ✅ Best fit
- ⚠️ Possible with extra config
- ❌ Not supported
- 💰 Cost consideration

---

## Recommended Path Forward

### Phase 1: Containerize Agent Framework (Immediate)

**Why:** Fastest path to production with full control

**Steps:**
1. ✅ Use the Dockerfile and deployment guide we created
2. ✅ Deploy to AKS alongside existing APIs
3. ✅ Configure private networking
4. ✅ Implement custom tools for API integration
5. ✅ Set up observability (App Insights)

**Timeline:** 1-2 weeks

**Benefits:**
- Immediate value
- Minimal changes to existing infrastructure
- Full control and customization
- Battle-tested Agent Framework

### Phase 2: Enhance with Enterprise Features (Month 1-2)

1. **Security**
   - Managed Identity for all Azure services
   - Network policies for pod-to-pod communication
   - Secret management via Key Vault

2. **Observability**
   - Distributed tracing with App Insights
   - Custom metrics for agent performance
   - Cost tracking and budget alerts

3. **Reliability**
   - Health checks and liveness probes
   - Circuit breakers for API calls
   - Retry policies with exponential backoff

4. **Governance**
   - Agent versioning strategy
   - A/B testing for agent improvements
   - Quality metrics and SLOs

### Phase 3: Evaluate Foundry Hosted Service (Future)

**When to consider:**
- Foundry Hosted Service supports private endpoints
- Cost model is favorable for usage patterns
- Customer wants to reduce infrastructure management
- Foundry governance features are must-haves

**Migration:**
- Agent Framework code is **compatible**
- Update deployment target from container to Foundry
- Minimal code changes (mostly configuration)

---

## Best Practices for Production Agent Deployment

### 1. Agent Lifecycle Management

```python
# Use centralized agent registry to prevent proliferation
from llmops.core.agent_lifecycle_manager import ProductionAgentManager

# Reuse agents across requests
agent, cred, client = await ProductionAgentManager.get_or_create_agent(
    agent_name="customer-support",
    instructions=instructions,
    enable_web_search=True,
    session_id=session_id
)
```

### 2. Tool Integration with Customer APIs

```python
from agent_framework import Tool

class CustomerAPITool(Tool):
    """Custom tool for secure API integration."""
    
    def __init__(self, api_endpoint: str, credential):
        self.api_endpoint = api_endpoint
        self.credential = credential
    
    async def execute(self, **kwargs):
        # Use managed identity for auth
        token = await self.credential.get_token("https://api.customer.com/.default")
        
        # Call internal API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_endpoint}/query",
                headers={"Authorization": f"Bearer {token.token}"},
                json=kwargs
            )
        
        return response.json()

# Register with agent
agent = ChatAgent(
    instructions="You help customers...",
    tools=[CustomerAPITool(api_endpoint=os.getenv("API_ENDPOINT"))]
)
```

### 3. Observability

```python
from llmops import MAFObservability

observability = MAFObservability()

# Track every agent call
with observability.create_span("agent.customer_support") as span:
    span.set_attribute("user_id", user_id)
    span.set_attribute("query_type", query_type)
    
    result = await agent.run(query)
    
    span.set_attribute("success", True)
    span.set_attribute("tokens", result.usage.total_tokens)
```

### 4. Cost Management

```python
from llmops import TokenBudgetManager

budget_manager = TokenBudgetManager(
    daily_budget=os.getenv("DAILY_TOKEN_BUDGET"),
    max_per_request=os.getenv("MAX_TOKENS_PER_REQUEST")
)

# Check before each request
allowed, message = budget_manager.check_budget(estimated_tokens)
if not allowed:
    raise BudgetExceededException(message)
```

---

## Common Questions

### Q: "Should we wait for Foundry Hosted Service before going to production?"

**A: No.** Agent Framework is production-ready now. You can:
- Deploy to production with Agent Framework today
- Migrate to Foundry Hosted Service later if/when it makes sense
- Keep optionality for deployment target

### Q: "Will we have to rewrite code to move to Foundry Hosted Service?"

**A: No.** Agent Framework is the foundation for Foundry agents. Migration is primarily:
- Configuration changes (deployment target)
- Potentially simpler (no container management)
- Same agent code and tools

### Q: "What about AI Foundry governance features?"

**A: Available now via APIs.** You can:
- Use Foundry project for models and search
- Log agent interactions to Foundry
- Use Foundry evaluation and monitoring
- Containerized agents = full Foundry feature access

### Q: "Is this Microsoft's recommended approach?"

**A: Yes, for customers with existing container infrastructure.** Microsoft uses both:
- Agent Framework for custom deployments (recommended for AKS customers)
- Foundry Hosted Service for simpler scenarios (roadmap feature)

---

## Summary & Recommendation

### For your customer (existing AKS + custom APIs):

✅ **Recommended: Containerize Agent Framework and deploy to AKS**

**Reasoning:**
1. Seamless integration with existing infrastructure
2. Private network access to APIs
3. Full control over security and compliance
4. Production-ready framework with all enterprise features
5. Clear migration path to Foundry Hosted Service later

**Not recommended:** Waiting for Foundry Hosted Service
- Agent Framework is production-ready now
- Customer needs to integrate with private APIs
- AKS deployment gives more control and better latency

### Implementation Resources

We've created everything you need:
- ✅ **Dockerfile** - Production-ready container image
- ✅ **Deployment script** - Automated deployment to Azure Container Apps
- ✅ **DEPLOYMENT.md** - Complete deployment guide
- ✅ **LLMOps components** - Observability, cost tracking, evaluation
- ✅ **Agent lifecycle manager** - Prevent resource proliferation
- ✅ **Streaming UI** - Production Streamlit interface

### Next Steps

1. **Review deployment guide:** `AQ-CODE/llmops/DEPLOYMENT.md`
2. **Adapt for AKS:** Use same Dockerfile, deploy with kubectl/Helm
3. **Configure private networking:** VNet integration with AKS
4. **Implement custom tools:** Integrate with customer APIs
5. **Set up monitoring:** App Insights + custom metrics

---

**Questions or need help with implementation?** Happy to pair on architecture or review deployment plans.

---

## References

- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [AKS Best Practices](https://learn.microsoft.com/azure/aks/best-practices)
- [Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [This LLMOps Implementation](../README.md)

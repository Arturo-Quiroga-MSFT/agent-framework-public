# GitHub Models vs Azure OpenAI vs Azure AI Foundry

A detailed comparison of using GitHub Models, Azure OpenAI, and Azure AI Foundry with Microsoft Agent Framework (MAF).

---

## Quick Comparison Table

| Aspect | GitHub Models | Azure OpenAI | Azure AI Foundry (V2) |
|--------|---------------|--------------|------------------------|
| **Cost** | Free (rate-limited) | Pay-per-token | Pay-per-token + service fees |
| **Setup Time** | < 5 minutes | 15-30 minutes | 30-60 minutes |
| **Authentication** | GitHub PAT | API Key or Azure CLI | Azure CLI + Project setup |
| **Available Models** | GPT-4o, Llama, Phi, Mistral | GPT-4o, GPT-4, GPT-3.5 | All Azure + custom models |
| **Rate Limits (RPM)** | ~15 RPM | 60-1000+ RPM | 60-1000+ RPM |
| **MAF Integration** | ✅ OpenAIChatClient | ✅ AzureOpenAIChatClient | ✅ AzureAIClient |
| **Client-Side Agents** | ✅ Full support | ✅ Full support | ✅ Full support |
| **Server-Side Agents** | ❌ Not supported | ❌ Not supported | ✅ Foundry V2 only |
| **Enterprise Features** | ❌ None | ✅ VNet, RBAC, etc. | ✅ Full governance |
| **Production Ready** | ❌ Dev/test only | ✅ Yes | ✅ Yes |
| **Best For** | Prototyping, learning | Production apps | Enterprise AI systems |

---

## Detailed Comparison

### 1. Cost Analysis

#### GitHub Models
```
Cost: FREE (with rate limits)
- No Azure subscription required
- ~15 requests/minute
- ~150K tokens/minute
- Ideal for: Development, learning, prototyping

Monthly estimate for 1000 agent calls:
- GitHub Models: $0 (within free tier)
```

#### Azure OpenAI
```
Cost: Pay-per-token
- GPT-4o: $0.03/1K input tokens, $0.06/1K output tokens
- GPT-4o-mini: $0.00015/1K input tokens, $0.0006/1K output tokens
- No minimum commitment
- Ideal for: Production applications

Monthly estimate for 1000 agent calls (avg 500 tokens each):
- GPT-4o-mini: ~$0.30
- GPT-4o: ~$30.00
```

#### Azure AI Foundry V2
```
Cost: Service + Models + Infrastructure
- Model costs: Same as Azure OpenAI
- Service fees: ~$0.50-2.00 per hour
- Cosmos DB (state): ~$100-300/month
- Application Insights: ~$50-100/month
- Ideal for: Enterprise deployments

Monthly estimate (small production):
- Total: $450-1400/month
```

### 2. Setup Complexity

#### GitHub Models (Easiest)
```python
# 1. Get GitHub token (2 minutes)
# 2. Set environment variable
export GITHUB_TOKEN="github_pat_..."

# 3. Write code (3 minutes)
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

client = OpenAIChatClient(
    model_id="gpt-4o-mini",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

agent = ChatAgent(chat_client=client, instructions="...")
```

**Total Time:** < 5 minutes

#### Azure OpenAI (Moderate)
```python
# 1. Create Azure subscription (5-10 minutes)
# 2. Create Azure OpenAI resource (5-10 minutes)
# 3. Deploy model (2-3 minutes)
# 4. Get credentials (2 minutes)

from agent_framework.azure import AzureOpenAIChatClient

client = AzureOpenAIChatClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name="gpt-4o-mini",
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

agent = ChatAgent(chat_client=client, instructions="...")
```

**Total Time:** 15-30 minutes

#### Azure AI Foundry V2 (Complex)
```python
# 1. Create Azure subscription
# 2. Create AI Foundry project (10-15 minutes)
# 3. Deploy model to project (5-10 minutes)
# 4. Configure authentication (5-10 minutes)
# 5. Get project endpoint (2 minutes)

from agent_framework.azure import AzureAIClient
from azure.identity import DefaultAzureCredential

client = AzureAIClient(
    endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

agent = client.create_agent(
    model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
    instructions="...",
    name="MyAgent",
    use_latest_version=True  # Server-side agent
)
```

**Total Time:** 30-60 minutes

### 3. Feature Comparison

#### Function Tools (All Support)

**GitHub Models:**
```python
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72°F"

agent = ChatAgent(
    chat_client=github_client,
    tools=[get_weather]
)
```

**Azure OpenAI:**
```python
agent = ChatAgent(
    chat_client=azure_openai_client,
    tools=[get_weather]  # Identical
)
```

**Foundry V2:**
```python
# Option 1: Client-side (like above)
agent = ChatAgent(chat_client=..., tools=[get_weather])

# Option 2: Server-side (Foundry-specific)
agent = client.create_agent(
    model="gpt-4o-mini",
    instructions="...",
    tools=[get_weather]  # Persisted on server
)
```

#### Agent Persistence

| Feature | GitHub Models | Azure OpenAI | Foundry V2 |
|---------|---------------|--------------|------------|
| Client-side agents | ✅ | ✅ | ✅ |
| Server-side agents | ❌ | ❌ | ✅ |
| Agent versioning | ❌ | ❌ | ✅ |
| Thread persistence | Manual | Manual | ✅ Automatic |
| State management | Manual | Manual | ✅ Cosmos DB |

#### Enterprise Features

| Feature | GitHub Models | Azure OpenAI | Foundry V2 |
|---------|---------------|--------------|------------|
| VNet integration | ❌ | ✅ | ✅ |
| Private endpoints | ❌ | ✅ | ✅ |
| Microsoft Entra ID | ❌ | ✅ | ✅ |
| RBAC | ❌ | ✅ | ✅ |
| Audit logs | ❌ | ✅ | ✅ |
| Content filters | Basic | ✅ Advanced | ✅ Advanced |
| Data residency | None | ✅ | ✅ |
| Compliance certs | None | ✅ Many | ✅ Many |

### 4. Performance & Limits

#### Rate Limits

**GitHub Models (Free Tier):**
```
Requests per minute: ~15 RPM
Tokens per minute:   ~150K TPM
Burst capacity:      Limited
```

**Azure OpenAI (Standard):**
```
Requests per minute: 60-1000+ RPM (configurable)
Tokens per minute:   240K-4M+ TPM (configurable)
Burst capacity:      Up to 2x sustained rate
```

**Azure AI Foundry V2:**
```
Same as Azure OpenAI +
- Agent orchestration overhead: ~50-100ms
- Cosmos DB latency: ~5-10ms
- Server-side benefits: Caching, state persistence
```

#### Latency Comparison

**GitHub Models:**
- First token: 500-1500ms
- Average request: 2-5 seconds
- Network: Variable (public internet)

**Azure OpenAI:**
- First token: 300-800ms
- Average request: 1-3 seconds
- Network: Azure backbone (faster)

**Foundry V2:**
- First token: 400-1000ms
- Average request: 1.5-4 seconds
- Additional overhead: Agent orchestration
- Benefits: State persistence, caching

### 5. Available Models

#### GitHub Models
```
OpenAI Models:
- gpt-4o
- gpt-4o-mini

Meta Models:
- Llama-3.3-70B-Instruct
- Llama-3.1-405B-Instruct
- Llama-3.1-70B-Instruct

Microsoft Models:
- Phi-4

Mistral Models:
- Mistral-Large-2
- Mistral-Nemo

Cohere Models:
- Cohere-command-r-plus
```

#### Azure OpenAI
```
OpenAI Models:
- gpt-4o (latest)
- gpt-4o-mini
- gpt-4 (0613, 1106, vision)
- gpt-4-32k
- gpt-3.5-turbo (0613, 1106)
- text-embedding-3-small/large

Note: Model availability varies by region
```

#### Azure AI Foundry V2
```
All Azure OpenAI models +
- Custom fine-tuned models
- Models from AI catalog
- Llama, Mistral, etc. via Model-as-a-Service
- Your own deployed models
```

### 6. Code Migration Path

#### From GitHub Models → Azure OpenAI

```python
# BEFORE (GitHub Models)
from agent_framework.openai import OpenAIChatClient

client = OpenAIChatClient(
    model_id="gpt-4o-mini",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url="https://models.inference.ai.azure.com"
)

agent = ChatAgent(
    chat_client=client,
    instructions="You are helpful."
)

# AFTER (Azure OpenAI) - Minimal changes
from agent_framework.azure import AzureOpenAIChatClient

client = AzureOpenAIChatClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name="gpt-4o-mini",
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

# Agent code unchanged!
agent = ChatAgent(
    chat_client=client,
    instructions="You are helpful."
)
```

#### From Azure OpenAI → Foundry V2

```python
# BEFORE (Azure OpenAI - Client-side)
from agent_framework.azure import AzureOpenAIChatClient

client = AzureOpenAIChatClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name="gpt-4o-mini"
)

agent = ChatAgent(
    chat_client=client,
    instructions="You are helpful."
)

# AFTER (Foundry V2 - Server-side)
from agent_framework.azure import AzureAIClient
from azure.identity import DefaultAzureCredential

client = AzureAIClient(
    endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

# Server-side agent with persistence
agent = client.create_agent(
    model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
    instructions="You are helpful.",
    name="MyAgent",
    use_latest_version=True
)
```

### 7. Use Case Recommendations

#### Use GitHub Models When:
- ✅ Learning MAF and agent development
- ✅ Rapid prototyping and experimentation
- ✅ Low-volume personal projects
- ✅ No budget for cloud services
- ✅ Testing open-source models (Llama, Phi)

#### Use Azure OpenAI When:
- ✅ Production applications
- ✅ Need higher rate limits
- ✅ Enterprise security requirements
- ✅ SLA guarantees needed
- ✅ Azure ecosystem integration
- ✅ Content filtering required

#### Use Azure AI Foundry V2 When:
- ✅ Enterprise AI deployments
- ✅ Multi-agent orchestration at scale
- ✅ Need server-side agent persistence
- ✅ Agent versioning required
- ✅ Compliance and governance critical
- ✅ Multi-region availability needed
- ✅ Agent-to-agent communication

### 8. Decision Tree

```
Start: Do you need this for production?
│
├─ NO → Budget available?
│        │
│        ├─ NO → Use GitHub Models ✓
│        │
│        └─ YES → Want to test production patterns?
│                 │
│                 ├─ YES → Use Azure OpenAI (dev subscription)
│                 │
│                 └─ NO → Use GitHub Models ✓
│
└─ YES → Need enterprise features (VNet, RBAC, etc.)?
         │
         ├─ NO → Single/few agents?
         │        │
         │        ├─ YES → Use Azure OpenAI ✓
         │        │
         │        └─ NO → Use Azure AI Foundry V2 ✓
         │
         └─ YES → Need server-side agent persistence?
                  │
                  ├─ YES → Use Azure AI Foundry V2 ✓
                  │
                  └─ NO → Use Azure OpenAI (with custom state management)
```

### 9. Cost-Benefit Analysis

#### Scenario: 10,000 agent calls/month (avg 500 tokens)

**GitHub Models:**
- Cost: $0 (if within rate limits)
- Pros: Free, easy setup
- Cons: Rate limited, no production support
- **Best for:** Development phase

**Azure OpenAI (GPT-4o-mini):**
- Cost: ~$3-6/month
- Pros: Production-ready, reliable, scalable
- Cons: Need Azure subscription
- **Best for:** Production apps without complex orchestration

**Azure AI Foundry V2:**
- Cost: ~$450-500/month (includes infrastructure)
- Pros: Full platform, governance, agent persistence
- Cons: Higher cost, more complex
- **Best for:** Enterprise deployments with multiple agents

### 10. Summary

| When to Use | GitHub Models | Azure OpenAI | Foundry V2 |
|-------------|---------------|--------------|------------|
| **Phase** | Development | Production | Enterprise |
| **Complexity** | Lowest | Medium | Highest |
| **Cost** | Free | Low | Medium-High |
| **Features** | Basic | Advanced | Complete |
| **Scale** | Limited | High | Unlimited |
| **Support** | Community | Microsoft | Microsoft + SLA |

---

**Recommendation:**

1. **Start** with GitHub Models for development
2. **Graduate** to Azure OpenAI for production
3. **Migrate** to Foundry V2 when you need:
   - Multiple agents with orchestration
   - Server-side persistence
   - Enterprise governance

**The code largely stays the same across all three!** MAF abstracts the differences.

---

**Last Updated:** January 1, 2026  
**Author:** Microsoft Agent Framework Community

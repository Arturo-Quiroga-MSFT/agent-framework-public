# Agent-to-Agent (A2A) Protocol

> **Last Updated**: January 19, 2026  
> **Status**: PREVIEW

## Overview

The **Agent-to-Agent (A2A) protocol** is a standard communication protocol that enables secure, discoverable, and auditable interactions between AI agents. Microsoft Entra Agent ID provides built-in support for A2A, allowing agents to discover, authorize, and communicate with each other using their identity.

## Why A2A Protocol?

### The Challenge

In multi-agent systems, agents need to:
- **Discover** other agents and their capabilities
- **Authorize** access to other agents
- **Communicate** securely and reliably
- **Maintain audit trails** of all interactions

### The Solution

A2A protocol provides:
- Standard discovery mechanism via Agent Registry
- OAuth 2.0-based authorization between agents
- Structured communication patterns
- Built-in security and governance

## A2A Architecture

```
┌──────────────────────────────────────────────────────────┐
│               Agent Registry (Discovery)                  │
│  • Metadata for all agents                                │
│  • Capability search                                      │
│  • Collections & policies                                 │
└────────────────┬─────────────────────────────────────────┘
                 ↓
        ┌────────┴─────────┐
        ↓                  ↓
┌───────────────┐    ┌───────────────┐
│   Agent A     │    │   Agent B     │
│               │    │               │
│ • Identity    │    │ • Identity    │
│ • Discovery   │◄──►│ • Discovery   │
│ • Auth        │    │ • Auth        │
└───────┬───────┘    └───────┬───────┘
        │                    │
        └──── A2A Protocol ──┘
              (OAuth 2.0)
```

## Core Components

### 1. Agent Discovery

Agents discover each other through the Agent Registry:

```python
from azure.identity import DefaultAzureCredential
import requests

def discover_agents(capability=None, collection=None):
    """Discover agents by capability or collection"""
    
    credential = DefaultAzureCredential()
    token = credential.get_token("https://graph.microsoft.com/.default")
    
    # Search Agent Registry
    query = {
        "capability": capability,
        "collection": collection
    }
    
    response = requests.post(
        "https://agent-registry.azure.com/discovery/v1/search",
        headers={"Authorization": f"Bearer {token.token}"},
        json=query
    )
    
    return response.json()["agents"]

# Example: Find all data analysis agents
data_agents = discover_agents(capability="data_analysis")

for agent in data_agents:
    print(f"Agent: {agent['name']}")
    print(f"  ID: {agent['id']}")
    print(f"  Endpoint: {agent['endpoint']}")
    print(f"  Capabilities: {agent['capabilities']}")
```

### 2. Agent Authorization

Agents authorize each other using OAuth 2.0 On-Behalf-Of (OBO) flow:

```
Agent A → Calls → Agent B
  ↓
  1. Agent A has its own token
  ↓
  2. Agent A requests OBO token for Agent B
  ↓
  3. Microsoft Entra validates and issues new token
  ↓
  4. Agent A calls Agent B with new token
  ↓
  5. Agent B validates token and processes request
```

### 3. Agent Communication

Agents communicate using standardized message formats:

```python
class A2AMessage:
    """Standard A2A message format"""
    def __init__(self, sender_id, receiver_id, message_type, payload):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_type = message_type  # "request", "response", "notification"
        self.payload = payload
        self.timestamp = datetime.utcnow()
        self.message_id = str(uuid.uuid4())
```

## Implementation Patterns

### Pattern 1: Sequential Agent Chain

Agent A calls Agent B, which calls Agent C:

```python
from azure.identity import ClientSecretCredential
from msal import ConfidentialClientApplication
import requests

class AgentChain:
    def __init__(self, agent_credential, agent_id):
        self.credential = agent_credential
        self.agent_id = agent_id
        
    def call_next_agent(self, target_agent_id, target_endpoint, message):
        """Call another agent in the chain"""
        
        # 1. Get OBO token for target agent
        obo_token = self.get_obo_token(target_agent_id)
        
        # 2. Call target agent
        response = requests.post(
            target_endpoint,
            headers={
                "Authorization": f"Bearer {obo_token}",
                "Content-Type": "application/json"
            },
            json={
                "sender_id": self.agent_id,
                "message": message
            }
        )
        
        return response.json()
    
    def get_obo_token(self, target_agent_id):
        """Get On-Behalf-Of token for target agent"""
        
        # Using MSAL for OBO flow
        app = ConfidentialClientApplication(
            client_id=self.credential.client_id,
            client_credential=self.credential.client_secret,
            authority=f"https://login.microsoftonline.com/{self.credential.tenant_id}"
        )
        
        # Current token
        current_token = self.credential.get_token("https://management.azure.com/.default")
        
        # Request OBO token
        result = app.acquire_token_on_behalf_of(
            user_assertion=current_token.token,
            scopes=[f"api://{target_agent_id}/.default"]
        )
        
        return result["access_token"]

# Usage
agent_a = AgentChain(
    agent_credential=ClientSecretCredential(
        tenant_id="tenant-id",
        client_id="agent-a-id",
        client_secret="agent-a-secret"
    ),
    agent_id="agent-a-id"
)

# Agent A calls Agent B
result_b = agent_a.call_next_agent(
    target_agent_id="agent-b-id",
    target_endpoint="https://agent-b.contoso.com/process",
    message={"task": "analyze_data", "data": [...]}
)

# Agent B can continue the chain to Agent C
# The user context (if any) is preserved through the OBO chain
```

### Pattern 2: Parallel Agent Execution

Coordinator agent calls multiple agents concurrently:

```python
import asyncio
import aiohttp

class CoordinatorAgent:
    def __init__(self, agent_credential, agent_id):
        self.credential = agent_credential
        self.agent_id = agent_id
    
    async def call_agent_async(self, session, target_agent_id, target_endpoint, task):
        """Call agent asynchronously"""
        
        obo_token = self.get_obo_token(target_agent_id)
        
        async with session.post(
            target_endpoint,
            headers={"Authorization": f"Bearer {obo_token}"},
            json={"task": task}
        ) as response:
            return await response.json()
    
    async def coordinate_agents(self, agent_tasks):
        """Execute multiple agents in parallel"""
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.call_agent_async(
                    session,
                    agent_info["id"],
                    agent_info["endpoint"],
                    agent_info["task"]
                )
                for agent_info in agent_tasks
            ]
            
            results = await asyncio.gather(*tasks)
            return results
    
    def get_obo_token(self, target_agent_id):
        """Get OBO token (same as above)"""
        pass

# Usage
coordinator = CoordinatorAgent(credential, "coordinator-id")

# Define parallel tasks
agent_tasks = [
    {
        "id": "sentiment-agent-id",
        "endpoint": "https://sentiment-agent.contoso.com/analyze",
        "task": {"text": "Customer feedback..."}
    },
    {
        "id": "classification-agent-id",
        "endpoint": "https://classification-agent.contoso.com/classify",
        "task": {"text": "Customer feedback..."}
    },
    {
        "id": "extraction-agent-id",
        "endpoint": "https://extraction-agent.contoso.com/extract",
        "task": {"text": "Customer feedback..."}
    }
]

# Execute in parallel
results = asyncio.run(coordinator.coordinate_agents(agent_tasks))

# Aggregate results
final_result = {
    "sentiment": results[0],
    "classification": results[1],
    "entities": results[2]
}
```

### Pattern 3: Agent Handoff

Agent A determines that Agent B is better suited for the task and hands off:

```python
class HandoffAgent:
    def process_request(self, request):
        """Process request or handoff to specialized agent"""
        
        # Analyze request
        required_capability = self.analyze_requirements(request)
        
        # Check if we can handle it
        if required_capability in self.capabilities:
            return self.handle_internally(request)
        
        # Find appropriate agent
        specialized_agents = discover_agents(capability=required_capability)
        
        if specialized_agents:
            target_agent = specialized_agents[0]
            
            # Handoff to specialized agent
            return self.handoff_to_agent(target_agent, request)
        else:
            raise Exception(f"No agent available for capability: {required_capability}")
    
    def handoff_to_agent(self, target_agent, request):
        """Hand off request to another agent"""
        
        # Get authorization for target agent
        obo_token = self.get_obo_token(target_agent["id"])
        
        # Forward request with handoff context
        response = requests.post(
            target_agent["endpoint"],
            headers={"Authorization": f"Bearer {obo_token}"},
            json={
                "handoff_from": self.agent_id,
                "original_request": request,
                "reason": f"Requires capability: {required_capability}"
            }
        )
        
        return response.json()
```

### Pattern 4: Human-in-the-Loop with Agent Chain

```python
class HumanInTheLoopAgent:
    def process_with_human_review(self, request):
        """Multi-agent workflow with human approval"""
        
        # Step 1: Initial analysis by Agent A
        analysis = self.call_analysis_agent(request)
        
        # Step 2: If confidence is low, request human review
        if analysis["confidence"] < 0.8:
            human_decision = self.request_human_review(analysis)
            
            if not human_decision["approved"]:
                return {"status": "rejected", "reason": human_decision["reason"]}
        
        # Step 3: Proceed with execution agent
        result = self.call_execution_agent(analysis)
        
        return result
    
    def request_human_review(self, analysis):
        """Request human approval before proceeding"""
        
        # Send notification to human reviewer
        approval_request = {
            "agent_id": self.agent_id,
            "analysis": analysis,
            "requested_action": "Proceed with execution",
            "timeout": 3600  # 1 hour
        }
        
        # Wait for human response (via callback or polling)
        return wait_for_human_response(approval_request)
```

## Agent Registry Integration

### Register Agent with A2A Capabilities

```json
{
  "agent_id": "sentiment-analyzer-001",
  "name": "Sentiment Analyzer",
  "description": "Analyzes sentiment in text",
  "capabilities": [
    "sentiment_analysis",
    "emotion_detection"
  ],
  "a2a": {
    "enabled": true,
    "endpoint": "https://sentiment-agent.contoso.com",
    "authentication": {
      "type": "oauth2",
      "authority": "https://login.microsoftonline.com/{tenant-id}",
      "audience": "api://sentiment-agent-001"
    }
  },
  "input_schema": {
    "type": "object",
    "properties": {
      "text": {"type": "string", "required": true}
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
      "confidence": {"type": "number", "min": 0, "max": 1}
    }
  }
}
```

### Query Registry for A2A-Enabled Agents

```python
def find_a2a_agents(capability):
    """Find agents that support A2A protocol"""
    
    agents = discover_agents(capability=capability)
    
    # Filter for A2A-enabled agents
    a2a_agents = [
        agent for agent in agents
        if agent.get("a2a", {}).get("enabled", False)
    ]
    
    return a2a_agents
```

## Security Considerations

### 1. Token Validation

Each agent must validate incoming tokens:

```python
def validate_agent_token(token, expected_sender_id):
    """Validate token from calling agent"""
    
    decoded = jwt.decode(
        token,
        options={"verify_signature": False},  # Simplified
        audience=f"api://{self.agent_id}"
    )
    
    # Verify sender
    if decoded["oid"] != expected_sender_id:
        raise SecurityError("Token sender mismatch")
    
    # Verify it's an OBO token if in a chain
    if "actort" in decoded:  # OBO token includes original user
        original_user = decoded["actort"]
        # Preserve user context for audit
    
    return decoded
```

### 2. Permission Scoping

Define what each agent can request from others:

```python
# Agent A definition
AGENT_A_PERMISSIONS = {
    "can_call": ["agent-b-id", "agent-c-id"],
    "cannot_call": ["admin-agent-id"]
}

def authorize_agent_call(caller_id, target_id):
    """Check if caller can invoke target"""
    
    permissions = load_agent_permissions(caller_id)
    
    if target_id not in permissions.get("can_call", []):
        raise PermissionError(f"Agent {caller_id} cannot call {target_id}")
```

### 3. Audit Logging

Log all A2A interactions:

```python
def log_a2a_interaction(sender_id, receiver_id, message_type, payload, result):
    """Log agent-to-agent interaction"""
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message_type": message_type,
        "payload_hash": hashlib.sha256(str(payload).encode()).hexdigest(),
        "result_status": result["status"],
        "chain_depth": extract_chain_depth_from_token()
    }
    
    # Send to Azure Monitor
    logging.info(f"A2A Interaction: {log_entry}")
```

## Advanced Patterns

### Dynamic Agent Orchestration

```python
class DynamicOrchestrator:
    """Orchestrator that dynamically builds agent workflow"""
    
    def orchestrate(self, task):
        """Determine optimal agent workflow for task"""
        
        # Analyze task requirements
        required_capabilities = self.analyze_task(task)
        
        # Find agents for each capability
        workflow = []
        for capability in required_capabilities:
            agents = discover_agents(capability=capability)
            best_agent = self.select_best_agent(agents, task)
            workflow.append(best_agent)
        
        # Execute workflow
        result = self.execute_workflow(workflow, task)
        return result
    
    def select_best_agent(self, agents, task):
        """Select best agent based on criteria"""
        
        # Factors: performance, cost, availability, specialization
        scored_agents = []
        for agent in agents:
            score = (
                agent.get("performance_score", 0) * 0.4 +
                (1 - agent.get("cost_per_request", 0)) * 0.3 +
                agent.get("availability", 0) * 0.3
            )
            scored_agents.append((score, agent))
        
        return max(scored_agents, key=lambda x: x[0])[1]
    
    def execute_workflow(self, workflow, task):
        """Execute agent workflow"""
        
        current_data = task
        for agent in workflow:
            result = self.call_agent(agent, current_data)
            current_data = result  # Output becomes input for next agent
        
        return current_data
```

### Fault-Tolerant Agent Chains

```python
class FaultTolerantChain:
    """Agent chain with retry and fallback logic"""
    
    def call_with_retry(self, target_agent, message, max_retries=3):
        """Call agent with retry logic"""
        
        for attempt in range(max_retries):
            try:
                result = self.call_agent(target_agent, message)
                return result
            
            except RequestException as e:
                if attempt == max_retries - 1:
                    # Try fallback agent
                    return self.call_fallback_agent(target_agent, message)
                
                # Exponential backoff
                time.sleep(2 ** attempt)
    
    def call_fallback_agent(self, failed_agent, message):
        """Call alternative agent with same capability"""
        
        # Find alternative agents
        capability = failed_agent["capability"]
        alternatives = discover_agents(capability=capability)
        
        # Remove failed agent from alternatives
        alternatives = [a for a in alternatives if a["id"] != failed_agent["id"]]
        
        if not alternatives:
            raise Exception(f"No fallback agent for {capability}")
        
        # Try first alternative
        return self.call_agent(alternatives[0], message)
```

## Monitoring & Observability

### A2A Metrics Dashboard

```kusto
// KQL query for A2A interaction monitoring
A2AInteractionLogs
| where TimeGenerated > ago(24h)
| summarize 
    TotalInteractions=count(),
    UniqueAgentPairs=dcount(strcat(SenderId, "-", ReceiverId)),
    AvgChainDepth=avg(ChainDepth),
    FailureRate=countif(ResultStatus == "failure") * 100.0 / count()
    by bin(TimeGenerated, 1h)
| render timechart
```

### Agent Communication Graph

```python
# Visualize agent communication patterns
import networkx as nx
import matplotlib.pyplot as plt

def build_agent_graph(interactions):
    """Build graph of agent interactions"""
    
    G = nx.DiGraph()
    
    for interaction in interactions:
        sender = interaction["sender_id"]
        receiver = interaction["receiver_id"]
        
        if not G.has_edge(sender, receiver):
            G.add_edge(sender, receiver, weight=0)
        
        G[sender][receiver]["weight"] += 1
    
    return G

# Visualize
G = build_agent_graph(recent_interactions)
nx.draw(G, with_labels=True, node_color='lightblue', 
        node_size=500, font_size=10, arrows=True)
plt.show()
```

## Best Practices

1. ✅ **Always use Agent Registry for discovery** - Don't hardcode agent endpoints
2. ✅ **Validate tokens at every hop** - Each agent must verify caller identity
3. ✅ **Log all interactions** - Complete audit trail for compliance
4. ✅ **Implement retry logic** - Handle transient failures gracefully
5. ✅ **Define clear contracts** - Use schemas for input/output
6. ✅ **Limit chain depth** - Prevent infinite loops (max 5-10 hops)
7. ✅ **Monitor performance** - Track latency and failure rates
8. ✅ **Use circuit breakers** - Prevent cascading failures

## Resources

- [Agent Registry Documentation](04-AGENT-REGISTRY.md)
- [OAuth 2.0 On-Behalf-Of Flow](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow)
- [Microsoft Graph API for Agents](https://learn.microsoft.com/en-us/graph/api/resources/agent)

---

**Next**: [Best Practices →](09-BEST-PRACTICES.md)

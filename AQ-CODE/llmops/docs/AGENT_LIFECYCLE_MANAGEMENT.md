# Agent Lifecycle Management in MAF LLMOps

## Problem Statement

The current `ProductionAgent` class creates a **new agent in Azure AI Foundry every time it's instantiated**. This leads to:

1. **Resource proliferation**: Each instantiation creates a new agent in Foundry
2. **Cost implications**: Unnecessary agent creation overhead
3. **State management issues**: Cannot reuse existing agents or their configurations
4. **Lack of lifecycle control**: No way to list, retrieve, update, or delete agents

## Current Implementation Issues

### Issue 1: Agent Creation in Every Instantiation

```python
# Current implementation in production_agent_enhanced.py
class ProductionAgent:
    async def run(self, query: str, ...):
        # Creates agent INSIDE the run method
        async with DefaultAzureCredential() as credential:
            async with AzureAIAgentClient(async_credential=credential) as client:
                # NEW AGENT CREATED HERE
                agent = ChatAgent(
                    chat_client=client,
                    instructions=self.instructions,
                    name=self.agent_name,
                    tools=tools if tools else None,
                )
```

**Problem**: Every call to `run()` creates a new `ChatAgent` instance, which may create a new agent resource in Foundry.

### Issue 2: No Agent Persistence Strategy

The current implementation doesn't:
- Check if an agent with the same name already exists
- Reuse existing agents
- Store agent IDs for future reference
- Provide agent lifecycle management (list, update, delete)

### Issue 3: Thread Management is Partially Solved

The code **correctly handles thread reuse** through `service_thread_id`:

```python
# GOOD: Thread reuse is handled correctly
if self._thread_id:
    thread = agent.get_new_thread(service_thread_id=self._thread_id)
else:
    thread = agent.get_new_thread()

# Store thread ID for next query
if thread.service_thread_id:
    self._thread_id = thread.service_thread_id
```

**However**, the agent itself is not being reused.

## Solution: Agent Lifecycle Management System

### Design Principles

1. **Agent Registry**: Maintain a registry of created agents (in-memory or persistent)
2. **Agent Reuse**: Check if an agent exists before creating new one
3. **Lazy Initialization**: Only create agents when needed
4. **Proper Cleanup**: Provide methods to delete/cleanup agents
5. **Thread Continuity**: Continue existing pattern of thread reuse (already working)

### Solution Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  ProductionAgent                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Agent Lifecycle Manager                         │   │
│  │  - Check if agent exists                         │   │
│  │  - Create if needed                              │   │
│  │  - Store agent reference                         │   │
│  │  - Provide cleanup methods                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Agent Registry (Persistent/In-Memory)          │   │
│  │  {                                               │   │
│  │    "market_analyst": {                          │   │
│  │      "agent_id": "...",                         │   │
│  │      "created_at": "...",                       │   │
│  │      "last_used": "...",                        │   │
│  │      "session_count": 123                       │   │
│  │    }                                            │   │
│  │  }                                              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Implementation Strategy

### Option 1: In-Memory Agent Registry (Simple)
**Best for**: Single-process applications, demos, development

- Store agent instances in class-level dictionary
- Agents live for the lifetime of the Python process
- Lost on restart (agents remain in Foundry but not tracked)

### Option 2: Persistent Agent Registry (Production)
**Best for**: Multi-process, distributed systems, production

- Store agent metadata in external storage (JSON file, database, Redis)
- Agents persist across restarts
- Enables multi-instance coordination

### Option 3: Foundry-Managed Agent Retrieval (Future)
**Best for**: Full lifecycle management

- Use Foundry API to list/retrieve existing agents
- Check if agent with name exists before creating
- Requires Foundry SDK support for agent management

## Recommended Implementation

### Phase 1: In-Memory Registry with Singleton Pattern

```python
class ProductionAgentManager:
    """Manages agent lifecycle and reuse."""
    
    _agents: Dict[str, Tuple[ChatAgent, DefaultAzureCredential, AzureAIAgentClient]] = {}
    _agent_metadata: Dict[str, Dict[str, Any]] = {}
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_or_create_agent(
        cls,
        agent_name: str,
        instructions: str,
        enable_web_search: bool = False
    ) -> Tuple[ChatAgent, DefaultAzureCredential, AzureAIAgentClient]:
        """Get existing agent or create new one."""
        async with cls._lock:
            if agent_name in cls._agents:
                # Return existing agent
                agent_tuple = cls._agents[agent_name]
                cls._agent_metadata[agent_name]["last_used"] = datetime.now().isoformat()
                cls._agent_metadata[agent_name]["use_count"] += 1
                return agent_tuple
            
            # Create new agent
            credential = DefaultAzureCredential()
            await credential.__aenter__()
            
            client = AzureAIAgentClient(async_credential=credential)
            await client.__aenter__()
            
            tools = None
            if enable_web_search:
                tools = HostedWebSearchTool(...)
            
            agent = ChatAgent(
                chat_client=client,
                instructions=instructions,
                name=agent_name,
                tools=tools,
            )
            
            # Store for reuse
            cls._agents[agent_name] = (agent, credential, client)
            cls._agent_metadata[agent_name] = {
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "use_count": 1,
                "instructions": instructions,
                "web_search_enabled": enable_web_search
            }
            
            return cls._agents[agent_name]
    
    @classmethod
    async def cleanup_agent(cls, agent_name: str):
        """Clean up specific agent."""
        async with cls._lock:
            if agent_name in cls._agents:
                agent, credential, client = cls._agents[agent_name]
                await client.__aexit__(None, None, None)
                await credential.__aexit__(None, None, None)
                del cls._agents[agent_name]
                del cls._agent_metadata[agent_name]
    
    @classmethod
    async def cleanup_all(cls):
        """Clean up all agents."""
        async with cls._lock:
            for agent_name in list(cls._agents.keys()):
                agent, credential, client = cls._agents[agent_name]
                await client.__aexit__(None, None, None)
                await credential.__aexit__(None, None, None)
            cls._agents.clear()
            cls._agent_metadata.clear()
    
    @classmethod
    def get_agent_stats(cls) -> Dict[str, Any]:
        """Get statistics about managed agents."""
        return {
            "total_agents": len(cls._agents),
            "agents": {
                name: {
                    "use_count": meta["use_count"],
                    "created_at": meta["created_at"],
                    "last_used": meta["last_used"]
                }
                for name, meta in cls._agent_metadata.items()
            }
        }
```

### Phase 2: Update ProductionAgent to Use Manager

```python
class ProductionAgent:
    """Production-ready agent with lifecycle management."""
    
    def __init__(
        self,
        agent_name: str,
        instructions: str,
        enable_web_search: bool = False,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
        enable_streaming: bool = False,
        reuse_agent: bool = True  # NEW: Enable agent reuse
    ):
        self.agent_name = agent_name
        self.instructions = instructions
        self.enable_web_search = enable_web_search
        self.progress_callback = progress_callback
        self.enable_streaming = enable_streaming
        self.reuse_agent = reuse_agent
        
        # LLMOps components (these are lightweight, OK to create per instance)
        self.observability = MAFObservability()
        self.cost_tracker = CostTracker()
        self.budget_manager = TokenBudgetManager()
        self.evaluator = AgentEvaluator()
        
        # Agent resources (managed by ProductionAgentManager)
        self._agent: Optional[ChatAgent] = None
        self._credential: Optional[DefaultAzureCredential] = None
        self._client: Optional[AzureAIAgentClient] = None
        
        # Thread management (keep existing pattern)
        self._thread_id = None
        
        # Session management
        self.chat_history: List[Dict[str, str]] = []
        self.session_id = str(uuid.uuid4())
    
    async def _ensure_agent(self):
        """Ensure agent is initialized (using manager for reuse)."""
        if self._agent is not None:
            return  # Already have agent
        
        if self.reuse_agent:
            # Get or create through manager
            agent_tuple = await ProductionAgentManager.get_or_create_agent(
                agent_name=self.agent_name,
                instructions=self.instructions,
                enable_web_search=self.enable_web_search
            )
            self._agent, self._credential, self._client = agent_tuple
        else:
            # Create new agent (old behavior)
            self._credential = DefaultAzureCredential()
            await self._credential.__aenter__()
            
            self._client = AzureAIAgentClient(async_credential=self._credential)
            await self._client.__aenter__()
            
            tools = None
            if self.enable_web_search:
                tools = HostedWebSearchTool(...)
            
            self._agent = ChatAgent(
                chat_client=self._client,
                instructions=self.instructions,
                name=self.agent_name,
                tools=tools,
            )
    
    async def run(self, query: str, ...):
        """Run agent with lifecycle management."""
        # Ensure agent exists (reuses if available)
        await self._ensure_agent()
        
        # Rest of the existing run logic...
        # Use self._agent instead of creating new one
        
        if self._thread_id:
            thread = self._agent.get_new_thread(service_thread_id=self._thread_id)
        else:
            thread = self._agent.get_new_thread()
        
        result = await self._agent.run(query, thread=thread, store=True)
        
        # Store thread ID for next query
        if thread.service_thread_id:
            self._thread_id = thread.service_thread_id
        
        # ... rest of existing logic
    
    async def cleanup(self):
        """Cleanup resources (respects shared agents)."""
        if not self.reuse_agent and self._client is not None:
            # Only cleanup if we own the resources
            await self._client.__aexit__(None, None, None)
            await self._credential.__aexit__(None, None, None)
        
        # Clear local references
        self._agent = None
        self._client = None
        self._credential = None
```

## Migration Path

### Step 1: Add Agent Manager (No Breaking Changes)
- Add `ProductionAgentManager` class
- Keep existing `ProductionAgent` as-is
- Add optional `reuse_agent` parameter (default: `True`)

### Step 2: Update Documentation
- Document agent lifecycle behavior
- Explain when agents are created vs reused
- Provide examples of cleanup patterns

### Step 3: Add Monitoring
- Track agent creation events
- Monitor agent reuse rate
- Alert on excessive agent creation

### Step 4: Future Enhancements
- Add persistent registry (JSON/DB)
- Integrate with Foundry agent management APIs (when available)
- Add agent versioning and updates
- Implement agent health checks

## Best Practices

### 1. Use Agent Manager for Long-Running Applications

```python
# Application startup
async def startup():
    # Pre-warm common agents
    await ProductionAgentManager.get_or_create_agent(
        "market_analyst", instructions=..., enable_web_search=True
    )

# Application shutdown
async def shutdown():
    await ProductionAgentManager.cleanup_all()
```

### 2. Monitor Agent Usage

```python
# Get statistics
stats = ProductionAgentManager.get_agent_stats()
print(f"Total agents: {stats['total_agents']}")
for name, info in stats['agents'].items():
    print(f"  {name}: {info['use_count']} uses")
```

### 3. Cleanup Unused Agents

```python
# Cleanup specific agent
await ProductionAgentManager.cleanup_agent("old_analyst")
```

### 4. Thread Management (Already Working)

```python
# Thread reuse is ALREADY implemented correctly
agent = ProductionAgent(...)
await agent.run("Query 1")  # Creates new thread
await agent.run("Query 2")  # Reuses thread (context preserved)
```

## Testing Strategy

### Unit Tests
- Test agent reuse logic
- Test agent creation when not exists
- Test cleanup methods
- Test concurrent access (lock behavior)

### Integration Tests
- Test with real Azure AI Foundry
- Verify agents are not duplicated
- Test thread continuity with agent reuse
- Test cleanup behavior

### Performance Tests
- Measure agent creation overhead
- Compare reuse vs recreation performance
- Test memory usage with many agents

## Monitoring and Observability

### Metrics to Track
1. **Agent Creation Rate**: How often new agents are created
2. **Agent Reuse Rate**: Percentage of agent retrievals vs creations
3. **Active Agents Count**: Number of agents in registry
4. **Agent Age**: Time since agent was created
5. **Agent Usage**: Number of queries per agent

### Alerts to Configure
1. **Excessive Agent Creation**: Alert if creation rate > threshold
2. **Agent Leaks**: Alert if active agents > expected count
3. **Cleanup Failures**: Alert on cleanup errors

## Documentation Updates Needed

1. **README.md**: Add section on agent lifecycle
2. **QUICKSTART.md**: Show agent reuse patterns
3. **ARCHITECTURE.md**: Document agent manager component
4. **TROUBLESHOOTING.md**: Add agent lifecycle issues

## FAQ

### Q: Will this break existing code?
**A**: No, the change is backward compatible. Default behavior will reuse agents.

### Q: Can I still create unique agents per session?
**A**: Yes, set `reuse_agent=False` when instantiating `ProductionAgent`.

### Q: What happens to agents in Foundry when process restarts?
**A**: Agents remain in Foundry but are no longer tracked. Phase 2 will add persistent registry.

### Q: How does this affect thread management?
**A**: No change. Thread reuse is already working correctly.

### Q: What's the performance impact?
**A**: Positive. Agent reuse eliminates creation overhead on subsequent uses.

## Next Steps

1. **Implement Phase 1**: Add `ProductionAgentManager` with in-memory registry
2. **Update `ProductionAgent`**: Use manager for agent lifecycle
3. **Add Tests**: Unit and integration tests for lifecycle management
4. **Update Documentation**: Add lifecycle management documentation
5. **Monitor in Production**: Track agent creation and reuse metrics
6. **Plan Phase 2**: Design persistent registry for multi-process scenarios

## References

- MAF Agent Framework: [AgentThread documentation](../python/packages/core/agent_framework/_threads.py)
- MAF ChatAgent: [ChatAgent implementation](../python/packages/core/agent_framework/_agents.py)
- Azure AI Foundry: Agent management best practices

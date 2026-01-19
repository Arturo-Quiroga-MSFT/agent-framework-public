# Migration FAQ (Frequently Asked Questions)

## General Questions

### What is Microsoft Agent Framework?

The Microsoft Agent Framework is the evolution and unification of agent development capabilities from Semantic Kernel and AutoGen. It provides a production-ready platform for building AI agents with advanced orchestration, workflows, and enterprise features.

### Why should I migrate?

**Key benefits:**
- ✅ **Production-ready**: Built-in observability, error handling, state management
- ✅ **Unified platform**: One framework instead of juggling multiple tools
- ✅ **Better workflows**: Declarative, type-safe orchestration engine
- ✅ **Microsoft support**: Official support and long-term commitment
- ✅ **Modern patterns**: Latest AI agent architecture patterns

### Is migration required?

**No, but recommended for new projects.** Semantic Kernel and AutoGen aren't being sunset immediately, but:
- Agent Framework is the future direction
- New features will focus on Agent Framework
- Better long-term support and stability

### Can I migrate gradually?

**Yes!** The framework is designed for gradual migration:
- Run both frameworks side-by-side
- Migrate components incrementally
- Use feature flags to toggle implementations
- No forced timeline

---

## Migration Timeline

### When should I start migrating?

**Consider these factors:**

| Situation | Recommendation |
|-----------|---------------|
| Starting new project | ✅ Use Agent Framework from day 1 |
| Prototype/POC | ✅ Start with Agent Framework |
| Stable production app | ⏸️ Plan migration, no urgency |
| Critical business app | ⏸️ Wait for your comfort level |
| Legacy/maintenance mode | ⏸️ No immediate need |

### How long does migration take?

**Depends on complexity:**

| Scenario | Estimated Time |
|----------|---------------|
| Simple single agent | 1-2 hours |
| Agent with plugins | 2-4 hours |
| Multi-agent (2-5 agents) | 1-2 days |
| Complex orchestration | 3-5 days |
| Large system (10+ agents) | 1-2 weeks |

### Is there a deadline?

**No hard deadline**, but consider:
- Semantic Kernel: Will continue evolving, some features may be Agent Framework-only
- AutoGen: Research project, less predictable support timeline
- Best practice: Migrate before building new major features

---

## Technical Questions

### Do I need to rewrite everything?

**No!** Many concepts translate directly:
- **Plugins**: Same pattern, minimal changes
- **Function calling**: Unchanged mechanism
- **AI services**: Same connectors
- **Core logic**: Business logic stays the same

**What changes:**
- Agent construction (simpler)
- Orchestration (more powerful)
- State management (built-in)

### Will my plugins work?

**Yes, mostly unchanged.** Semantic Kernel plugins work in Agent Framework with minimal or no changes:

```csharp
// This plugin works in both frameworks
public class MyPlugin
{
    [KernelFunction]
    [Description("Does something")]
    public string MyFunction(string input)
    {
        return "result";
    }
}
```

**Small change:** How you register them:
```csharp
// SK: kernel.Plugins.Add(...)
// AF: plugins: [new MyPlugin()]
```

### What about my custom agents?

**Custom agents need migration:**

**From Semantic Kernel:**
```csharp
// Old: Inherit from Agent base class
public class MyAgent : Agent { }

// New: Use ChatClientAgent or implement AIAgent
public class MyAgent : ChatClientAgent { }
```

**From AutoGen:**
```python
# Old: Inherit from ConversableAgent
class MyAgent(ConversableAgent): pass

# New: Use ChatAgent or composition
agent = ChatAgent(...)
```

### Are there breaking API changes?

**Some, but gradual:**

**Semantic Kernel:**
- Deprecated APIs marked with `[Obsolete]`
- Old patterns still work (with warnings)
- Clear migration path provided

**AutoGen:**
- More significant API changes
- Different programming model
- Clear patterns documented

### Can I use both frameworks together?

**Yes, but not recommended for production:**

```csharp
// Feature flag example
var agent = useNewFramework 
    ? CreateAgentFrameworkAgent()
    : CreateSemanticKernelAgent();
```

**Better approach:** Migrate service by service rather than mixing in one service.

---

## Semantic Kernel Specific

### Does Agent Framework replace Semantic Kernel?

**No, it extends it.** Semantic Kernel concepts are still present:
- Plugins still exist
- Kernel is optional but available
- Function calling unchanged
- Many APIs are similar

**Think of it as:** Semantic Kernel's agent features graduated and enhanced.

### What happens to my Semantic Kernel code?

**It continues to work:**
- No immediate breaking changes
- Deprecation warnings guide migration
- Old patterns supported for transition period
- Can coexist with Agent Framework

### Do I lose any Semantic Kernel features?

**No major features lost:**
- ✅ Plugins → Still supported
- ✅ Function calling → Enhanced
- ✅ AI services → Same connectors
- ✅ Templating → Available
- ✅ Memory/RAG → Via plugins

**Gained features:**
- ✅ Better workflows
- ✅ State management
- ✅ Enhanced orchestration

### Can I keep using Kernel?

**Yes, but it's optional:**

```csharp
// Still works if you need it
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(...)
    .Build();

var agent = chatClient.AsAIAgent(
    kernel.GetRequiredService<IChatClient>(),
    ...
);
```

**Simpler approach:**
```csharp
// Direct service configuration (no kernel)
var agent = chatClient.AsAIAgent(
    AzureOpenAIChatClient.Create(...),
    ...
);
```

---

## AutoGen Specific

### Is Agent Framework compatible with AutoGen?

**Not directly compatible**, but patterns translate:

| AutoGen | Agent Framework |
|---------|----------------|
| ConversableAgent | ChatAgent |
| GroupChat | Group chat orchestration |
| UserProxyAgent | Human-in-loop executor |
| Magentic-One | Magentic orchestration |

### What about AutoGen's conversational AI?

**Fully supported:**
- Multi-turn conversations via `AgentThread`
- Group chat patterns enhanced
- Better state management
- More orchestration options

### Can I use AutoGen agents in Agent Framework?

**Not directly, but you can wrap them:**

```python
class AutoGenWrapper:
    def __init__(self, autogen_agent):
        self.agent = autogen_agent
    
    async def run(self, message):
        return self.agent.generate_reply(
            messages=[{"role": "user", "content": message}]
        )
```

**Better approach:** Rewrite using Agent Framework patterns.

### What about human-in-the-loop?

**Enhanced in Agent Framework:**

**AutoGen:**
```python
UserProxyAgent(human_input_mode="ALWAYS")
```

**Agent Framework:**
```python
# More flexible workflow-based approach
workflow = (
    WorkflowBuilder()
    .add_agent("assistant", agent)
    .add_executor("human", HumanInputExecutor())
    .add_edge("assistant", "human")
    .build()
)
```

---

## Workflow Questions

### What are workflows?

**Workflows** are declarative, graph-based orchestrations:
- Define agent interactions
- Control flow (sequential, concurrent, conditional)
- State management
- Checkpointing

**Example:**
```yaml
# Declarative YAML workflow
name: ResearchWorkflow
executors:
  - id: researcher
    type: agent
  - id: writer
    type: agent
edges:
  - from: researcher
    to: writer
```

### Do I need workflows?

**Depends on complexity:**

| Use Case | Workflow Needed? |
|----------|-----------------|
| Single agent chat | ❌ No |
| 2-3 agents, simple | ⚠️ Optional |
| Complex multi-agent | ✅ Recommended |
| State management needed | ✅ Yes |
| Checkpointing required | ✅ Yes |
| Human-in-the-loop | ✅ Recommended |

### Can I build agents without workflows?

**Yes!** Simple agents don't need workflows:

```csharp
// Simple agent, no workflow needed
var agent = chatClient.AsAIAgent(...);
var response = await agent.GetResponseAsync("Hello");
```

**Use workflows when:**
- Multiple agents collaborate
- Need state persistence
- Complex control flow
- Human interaction points

### Are workflows required for multi-agent?

**No, but recommended:**

**Without workflow:**
```csharp
// Manual coordination
var response1 = await agent1.GetResponseAsync(input);
var response2 = await agent2.GetResponseAsync(response1.Content);
```

**With workflow:**
```csharp
// Declarative, better error handling, state management
var workflow = new SequentialOrchestration(agents: [agent1, agent2]);
await foreach (var update in workflow.RunStreamingAsync(input)) { }
```

---

## Platform & Infrastructure

### Which programming languages are supported?

| Language | Support Level |
|----------|--------------|
| **C# / .NET** | ✅ Full (native) |
| **Python** | ✅ Full (native) |
| **Java** | ⚠️ Limited |
| **TypeScript** | ⚠️ Planned |

### What about Azure integration?

**First-class Azure support:**
- ✅ Azure OpenAI
- ✅ Azure AI Foundry
- ✅ Azure AI Services
- ✅ Azure Identity (auth)
- ✅ Azure Monitor (telemetry)
- ✅ Azure Container Apps

### Can I use other cloud providers?

**Yes!** Agent Framework is cloud-agnostic:
- Works on AWS, GCP, on-premises
- Can use non-Azure AI services
- Deployment flexibility
- **But**: Best experience on Azure

### What about local development?

**Fully supported:**
- Run locally with Ollama, LM Studio, etc.
- Docker for containerized development
- VS Code debugging
- Local AI models via `IChatClient`

---

## Performance & Scaling

### Is Agent Framework faster than Semantic Kernel/AutoGen?

**Generally yes:**

| Metric | SK | AutoGen | Agent Framework |
|--------|-----|---------|-----------------|
| Cold start | ~500ms | ~800ms | ~200ms |
| Memory | ~150MB | ~200MB | ~100MB |
| Throughput | Good | Variable | Better |

**Optimizations:**
- Better async/await patterns
- Efficient resource management
- Optimized streaming

### How does it scale?

**Well-designed for scale:**
- Stateless agents (horizontal scaling)
- Checkpointing for long-running tasks
- Async/await throughout
- Efficient resource cleanup

### What about cost?

**Similar or lower API costs:**
- Same LLM calls as before
- More efficient orchestration (fewer redundant calls)
- Better retry logic (avoid wasted calls)

---

## Observability & Debugging

### How do I debug Agent Framework?

**Multiple options:**

1. **Built-in logging:**
```csharp
// Structured logging
logger.LogInformation("Agent response: {Content}", response.Content);
```

2. **OpenTelemetry tracing:**
```python
# Automatic spans
setup_observability(enable_sensitive_data=True)
```

3. **VS Code debugging:**
   - Set breakpoints
   - Step through agent execution
   - Inspect workflow state

### Can I see what agents are doing?

**Yes, comprehensive observability:**

**Workflow events:**
```python
async for event in workflow.run_streaming(input):
    if event.type == "agent_response":
        print(f"{event.agent_name}: {event.content}")
    elif event.type == "workflow_state":
        print(f"State: {event.state}")
```

**Telemetry:**
- Automatic spans for agent operations
- Message send/receive tracking
- Function call traces
- Performance metrics

### How do I troubleshoot errors?

**Better error handling:**

```csharp
try
{
    var response = await agent.GetResponseAsync(input);
}
catch (AgentException ex)
{
    // Structured exception with context
    logger.LogError(ex, "Agent failed: {Reason}", ex.Reason);
}
```

**Built-in retry:**
```csharp
var settings = new AgentSettings
{
    MaxRetries = 3,
    RetryDelay = TimeSpan.FromSeconds(2)
};
```

---

## Testing

### How do I test agents?

**Better testing patterns:**

**Mock chat clients:**
```csharp
var mockClient = new MockChatClient();
mockClient.Setup(response: "Test response");

var agent = chatClient.AsAIAgent(mockClient, ...);
var response = await agent.GetResponseAsync("Test");

Assert.Equal("Test response", response.Content);
```

**Workflow testing:**
```csharp
var workflow = new SequentialOrchestration(...);
var results = await workflow.RunAsync("Test input");

Assert.NotNull(results);
Assert.Equal(expected, results.FinalOutput);
```

### Can I unit test workflows?

**Yes, designed for testing:**

```python
@pytest.mark.asyncio
async def test_workflow():
    # Arrange
    mock_agent1 = MockAgent(response="Step 1 done")
    mock_agent2 = MockAgent(response="Step 2 done")
    
    workflow = SequentialOrchestration(agents=[mock_agent1, mock_agent2])
    
    # Act
    results = await workflow.run("Test")
    
    # Assert
    assert results.status == "completed"
```

---

## Cost & Licensing

### Is Agent Framework free?

**Yes, the framework is free:**
- Open source (MIT license)
- No framework licensing costs
- Same as Semantic Kernel and AutoGen

**You pay for:**
- AI service API calls (OpenAI, Azure OpenAI, etc.)
- Azure infrastructure (if using Azure)

### What about support?

**Multiple support options:**

| Level | Availability |
|-------|-------------|
| **Community** | Free (GitHub, docs) |
| **Microsoft Q&A** | Free (Microsoft platform) |
| **Azure Support** | Paid (for Azure customers) |
| **Enterprise** | Paid (Premier support) |

---

## Migration Help

### Where do I start?

**Step-by-step:**

1. ✅ **Read** this migration guide
2. ✅ **Review** your current implementation
3. ✅ **Identify** migration candidates (start simple)
4. ✅ **Test** in development environment
5. ✅ **Monitor** performance and behavior
6. ✅ **Deploy** incrementally

**Resources:**
- [Semantic Kernel Migration Guide](./semantic-kernel-migration.md)
- [AutoGen Migration Guide](./autogen-migration.md)
- [Code Examples](./examples/)

### Can Microsoft help with migration?

**Yes, several options:**

1. **Documentation**: Comprehensive guides (this repo)
2. **Samples**: Code examples and patterns
3. **Community**: GitHub discussions
4. **Support**: Azure Support (for Azure customers)
5. **Consulting**: Microsoft partners for large migrations

### What if I get stuck?

**Help available:**

1. **GitHub Issues**: Report bugs or ask questions
2. **Microsoft Q&A**: Community support
3. **Documentation**: Searchable docs
4. **Stack Overflow**: Tag with `microsoft-agent-framework`
5. **Azure Support**: For Azure customers

### Are there tools to help migrate?

**Currently:**
- ⚠️ No automated migration tools
- ✅ Clear migration patterns documented
- ✅ Code examples for common scenarios
- ✅ Side-by-side comparisons

**Future:**
- 🔄 Migration analyzer tool (planned)
- 🔄 Code transformation helpers (planned)

---

## Common Issues

### "My agent doesn't call functions"

**Check:**
1. ✅ Plugin registered correctly
2. ✅ Model supports function calling (gpt-4, gpt-3.5-turbo)
3. ✅ Function has proper descriptions
4. ✅ Auto-invoke enabled (default)

### "Workflow doesn't maintain state"

**Solution:**
```csharp
// Use thread for state
var thread = new ChatHistoryAgentThread();
await agent.InvokeAsync(messages, thread: thread);
// State maintained in thread
```

### "Migration is too complex"

**Simplify:**
1. Start with one agent
2. Don't migrate everything at once
3. Use side-by-side approach
4. Migrate as you add features

### "Performance is worse"

**Check:**
1. Using async/await correctly?
2. Streaming enabled?
3. Proper resource disposal?
4. Compare apples-to-apples (same model, etc.)

---

## Additional Resources

- [Official Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [GitHub Repository](https://github.com/microsoft/agent-framework)
- [Code Samples](../examples/)
- [Feature Comparison](./feature-comparison.md)

---

**Last Updated**: October 16, 2025

**Have more questions?** Open an issue on GitHub or contribute to this FAQ!

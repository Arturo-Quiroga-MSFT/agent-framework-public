# Migration Overview: Moving to Microsoft Agent Framework

## Executive Summary

The **Microsoft Agent Framework** represents the evolution and consolidation of agent development approaches at Microsoft, building upon the foundations of both **Semantic Kernel** and **AutoGen**. This guide helps teams understand the migration path and leverage new capabilities.

## What's Changing?

### Semantic Kernel Evolution

Semantic Kernel's agent framework has graduated and evolved into the Microsoft Agent Framework:

- **Release Timeline**: Semantic Kernel agents moved from experimental → preview → release candidate → Microsoft Agent Framework
- **Core Concepts Retained**: Plugins, function calling, and AI service abstractions remain familiar
- **New Capabilities**: Enhanced workflows, better orchestration, and production-ready features
- **Compatibility**: Gradual migration path with deprecation warnings (not breaking changes)

### AutoGen Integration

AutoGen patterns and multi-agent orchestration concepts are integrated:

- **Magentic-One Inspiration**: The Magentic orchestration pattern is directly inspired by AutoGen's Magentic-One
- **Group Chat**: Enhanced group chat orchestration available
- **Agent Collaboration**: More flexible multi-agent coordination patterns
- **Conversable Agents**: Available through compatibility layers

## Why Migrate?

### Unified Platform Benefits

1. **Single Framework**: Consolidate Semantic Kernel and AutoGen approaches
2. **Production Features**: Built-in observability, checkpointing, and error handling
3. **Type Safety**: Strongly typed workflows prevent runtime errors
4. **Better Tooling**: Enhanced VS Code integration and debugging support
5. **Microsoft Support**: Unified support and documentation

### New Capabilities

#### Workflows
- **Graph-Based Orchestration**: Define complex multi-step processes declaratively
- **Checkpointing**: Save and resume long-running processes
- **External Integration**: Built-in patterns for human-in-the-loop and API integration

#### Agent Types
- **ChatClientAgent**: Works with any `IChatClient` implementation
- **Service-Hosted Agents**: Azure AI, OpenAI Assistant agents
- **A2A Proxies**: Connect to remote agents via Agent-to-Agent protocol
- **Workflow Agents**: Turn workflows into agents for composition

#### Orchestration Patterns
- **Sequential**: Linear pipelines
- **Concurrent**: Parallel execution with aggregation
- **Handoff**: Dynamic agent switching based on context
- **Magentic**: AutoGen-inspired dynamic coordination

### Microsoft Extensions.AI Integration

The framework leverages `Microsoft.Extensions.AI`:
- **`IChatClient` Interface**: Unified abstraction for AI services
- **Middleware Pattern**: Telemetry, caching, and rate limiting
- **Broad Support**: OpenAI, Azure OpenAI, Ollama, Anthropic, and more

## Migration Philosophy

### Gradual, Not Disruptive

The migration is designed to be incremental:

1. **Coexistence**: Semantic Kernel and Agent Framework can run side-by-side
2. **Deprecation Warnings**: Old patterns marked with `[Obsolete]` but still functional
3. **Progressive Enhancement**: Adopt new features at your own pace
4. **Backward Compatibility**: Critical to maintain business continuity

### Modern Patterns

The framework encourages modern practices:

- **Dependency Injection**: First-class support for DI containers
- **Async/Await**: Fully asynchronous by design
- **Observability**: OpenTelemetry integration out of the box
- **Testing**: Cleaner patterns for unit and integration testing

## Framework Comparison

| Feature | Semantic Kernel | AutoGen | Microsoft Agent Framework |
|---------|----------------|---------|---------------------------|
| **Single Agent** | ✅ ChatCompletionAgent | ✅ ConversableAgent | ✅ ChatAgent |
| **Plugins/Tools** | ✅ Plugins | ✅ Function Calling | ✅ Plugins + Tools |
| **Multi-Agent** | ✅ Basic orchestration | ✅ Advanced patterns | ✅ Comprehensive orchestration |
| **Workflows** | ⚠️ Limited | ❌ Not built-in | ✅ Full graph-based workflows |
| **Checkpointing** | ❌ Not built-in | ✅ In group chat | ✅ Workflow-level |
| **Type Safety** | ⚠️ Partial | ⚠️ Limited | ✅ Strong typing |
| **Observability** | ⚠️ Basic | ⚠️ Custom | ✅ Built-in OpenTelemetry |
| **Human-in-Loop** | ⚠️ Custom | ⚠️ Custom | ✅ Built-in patterns |
| **Declarative** | ❌ Code-only | ❌ Code-only | ✅ YAML workflows |

## Key Concepts Mapping

### From Semantic Kernel

| Semantic Kernel | Microsoft Agent Framework |
|----------------|---------------------------|
| `Kernel` | Optional (agents can work directly with services) |
| `ChatCompletionAgent` | `ChatAgent` or `ChatClientAgent` |
| `OpenAIAssistantAgent` | Service-specific agent implementations |
| `KernelPlugin` | Still used, same patterns |
| `AgentGroupChat` | Workflow orchestration patterns |
| `ChatHistory` | `ChatHistoryAgentThread` or workflow state |

### From AutoGen

| AutoGen | Microsoft Agent Framework |
|---------|---------------------------|
| `ConversableAgent` | `ChatAgent` with function calling |
| `GroupChat` | Group chat orchestration or workflows |
| `Magentic-One` | Magentic orchestration pattern |
| Agent `register_for_llm` | Plugin/function registration |
| `initiate_chat` | `agent.run()` or workflow execution |
| `UserProxyAgent` | Human-in-loop executors |

## Architecture Differences

### Semantic Kernel → Agent Framework

**Before (Semantic Kernel):**
```csharp
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(...)
    .Build();

kernel.AddPlugin(new MyPlugin());

var agent = new ChatCompletionAgent
{
    Kernel = kernel,
    Instructions = "..."
};
```

**After (Agent Framework):**
```csharp
var agent = chatClient.AsAIAgent(
    chatClient: AzureOpenAIChatClient.Create(...),
    instructions: "...",
    plugins: [new MyPlugin()]
);
```

### AutoGen → Agent Framework

**Before (AutoGen):**
```python
assistant = ConversableAgent(
    name="assistant",
    llm_config={"model": "gpt-4"},
    system_message="..."
)

assistant.register_for_llm()(my_function)
user_proxy.initiate_chat(assistant, message="...")
```

**After (Agent Framework):**
```python
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient

agent = ChatAgent(
    chat_client=AzureOpenAIChatClient(model_id="gpt-4"),
    instructions="...",
    plugins=[MyPlugin()]
)

response = await agent.run("...")
```

## Decision Framework

### When to Migrate Now

✅ You're starting a new agent project
✅ Your Semantic Kernel code uses deprecated patterns
✅ You need advanced workflow features
✅ You require production-grade observability
✅ You're building complex multi-agent systems

### When to Wait

⏸️ Your current implementation is working well in production
⏸️ You're in the middle of a critical release cycle
⏸️ Your required features aren't yet in the framework
⏸️ You need time to train your team

### Hybrid Approach

🔄 Migrate new features to Agent Framework
🔄 Keep stable components on Semantic Kernel
🔄 Plan gradual migration over quarters
🔄 Use feature flags to toggle between implementations

## Next Steps

1. **[Read Semantic Kernel Migration Guide](./semantic-kernel-migration.md)** - If coming from SK
2. **[Read AutoGen Migration Guide](./autogen-migration.md)** - If coming from AutoGen
3. **[Review Feature Comparison](./feature-comparison.md)** - Detailed capability mapping
4. **[Explore Examples](./examples/)** - See migration patterns in code
5. **[Check FAQ](./faq.md)** - Common questions and answers

## Getting Help

- **Documentation**: [Microsoft Agent Framework Docs](https://learn.microsoft.com/en-us/agent-framework/)
- **Samples**: [GitHub Repository](https://github.com/microsoft/agent-framework)
- **Issues**: Report on GitHub Issues
- **Community**: Join discussions and Q&A

---

**Last Updated**: October 16, 2025

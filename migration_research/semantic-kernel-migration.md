# Semantic Kernel to Microsoft Agent Framework Migration Guide

## Overview

This guide provides detailed instructions for migrating from **Semantic Kernel's agent framework** to the **Microsoft Agent Framework**. The good news: many core concepts remain the same, and Microsoft has designed a smooth migration path.

## Key Changes Summary

### What Stays the Same ✅

- **Plugins**: Same concept, same patterns
- **Function Calling**: Unchanged mechanism
- **AI Service Connectors**: Still supported
- **Chat Message Types**: Same content types
- **Core Philosophy**: AI orchestration with tools

### What's Different 🔄

- **Agent Construction**: Simplified, less ceremony
- **Service Configuration**: Can be direct, kernel optional
- **Thread Management**: New `AgentThread` abstraction
- **Orchestration**: Enhanced workflow capabilities
- **API Surface**: Streamlined and more intuitive

### What's New ✨

- **Workflows**: Graph-based orchestration engine
- **Multiple Agent Types**: Beyond just chat completion
- **Built-in Patterns**: Sequential, concurrent, handoff, magentic
- **Observability**: OpenTelemetry integration
- **Checkpointing**: State persistence for long-running tasks

## Migration by Component

## 1. Agent Creation

### ChatCompletionAgent

#### Semantic Kernel (Old)
```csharp
// Create kernel with services
var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    deploymentName: "gpt-4",
    endpoint: "https://...",
    apiKey: "..."
);
var kernel = builder.Build();

// Add plugins
kernel.Plugins.AddFromType<MyPlugin>();

// Create agent
var agent = new ChatCompletionAgent
{
    Kernel = kernel,
    Name = "Assistant",
    Instructions = "You are a helpful assistant",
    Arguments = new KernelArguments(
        new OpenAIPromptExecutionSettings 
        { 
            FunctionChoiceBehavior = FunctionChoiceBehavior.Auto() 
        }
    )
};
```

#### Microsoft Agent Framework (New)
```csharp
using Microsoft.Agents.AI;

// Direct service configuration
var chatClient = new AzureOpenAIChatClient(
    endpoint: new Uri("https://..."),
    credential: new AzureKeyCredential("..."),
    deploymentName: "gpt-4"
);

// Create agent with plugins directly
var agent = new ChatClientAgent(
    chatClient,
    instructions: "You are a helpful assistant",
    name: "Assistant",
    plugins: [KernelPluginFactory.CreateFromType<MyPlugin>()]
);
```

**Key Changes:**
- ✅ No kernel required (unless you need shared state)
- ✅ Plugins passed directly in constructor
- ✅ Service configuration more straightforward
- ✅ Less boilerplate code

### Python Example

#### Semantic Kernel (Old)
```python
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent

kernel = Kernel()
kernel.add_service(AzureChatCompletion(
    deployment_name="gpt-4",
    endpoint="https://...",
    api_key="..."
))
kernel.add_plugin(MyPlugin(), plugin_name="my_plugin")

agent = ChatCompletionAgent(
    kernel=kernel,
    name="Assistant",
    instructions="You are a helpful assistant"
)
```

#### Microsoft Agent Framework (New)
```python
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient

agent = ChatAgent(
    chat_client=AzureOpenAIChatClient(
        model_id="gpt-4",
        endpoint="https://...",
        api_key="..."
    ),
    instructions="You are a helpful assistant",
    name="Assistant",
    plugins=[MyPlugin()]
)
```

## 2. Agent Invocation

### Single Turn Interaction

#### Semantic Kernel (Old)
```csharp
// Add message to chat history
var history = new ChatHistory();
history.AddUserMessage("Hello!");

// Invoke agent
await foreach (var message in agent.InvokeAsync(history))
{
    Console.WriteLine(message.Content);
}
```

#### Microsoft Agent Framework (New)
```csharp
// Get single response (no thread continuity)
var response = await agent.GetResponseAsync(messages: "Hello!");
Console.WriteLine(response.Message.Content);

// Or with streaming
await foreach (var update in agent.InvokeStreamingAsync(messages: "Hello!"))
{
    Console.Write(update.Content);
}
```

### Multi-Turn Conversation

#### Semantic Kernel (Old)
```csharp
var history = new ChatHistory();
history.AddUserMessage("What's the weather?");

await foreach (var message in agent.InvokeAsync(history))
{
    history.Add(message);
    Console.WriteLine(message.Content);
}

// Continue conversation
history.AddUserMessage("What about tomorrow?");
await foreach (var message in agent.InvokeAsync(history))
{
    history.Add(message);
    Console.WriteLine(message.Content);
}
```

#### Microsoft Agent Framework (New)
```csharp
// Create a thread for conversation continuity
var thread = new ChatHistoryAgentThread();

// First turn
var response1 = await agent.InvokeAsync(
    messages: "What's the weather?",
    thread: thread
);
Console.WriteLine(response1.Message.Content);

// Second turn (thread maintains context)
var response2 = await agent.InvokeAsync(
    messages: "What about tomorrow?",
    thread: thread
);
Console.WriteLine(response2.Message.Content);
```

**Key Changes:**
- ✅ New `AgentThread` abstraction manages conversation state
- ✅ Cleaner API: `GetResponseAsync()` vs multiple patterns
- ✅ Thread can be created automatically or manually managed
- ✅ Support for multiple message inputs

## 3. OpenAI Assistant Agents

### Semantic Kernel (Old)
```csharp
var provider = new OpenAIClientProvider(...);

var definition = await OpenAIAssistantAgent.CreateAsync(
    provider,
    definition: new OpenAIAssistantDefinition("gpt-4")
    {
        Name = "Assistant",
        Instructions = "You are helpful",
        EnableCodeInterpreter = true
    },
    kernel: kernel
);

var agent = await OpenAIAssistantAgent.RetrieveAsync(
    provider,
    definition.Id,
    kernel
);
```

#### Microsoft Agent Framework (New)
```csharp
// Create OpenAI client
var client = OpenAIAssistantAgent.CreateOpenAIClient(apiKey);
var assistantClient = client.GetAssistantClient();

// Create assistant definition
var assistant = await assistantClient.CreateAssistantAsync(
    model: "gpt-4",
    name: "Assistant",
    instructions: "You are helpful",
    enableCodeInterpreter: true
);

// Create agent
var agent = new OpenAIAssistantAgent(
    assistant,
    client,
    plugins: [KernelPluginFactory.CreateFromType<MyPlugin>()]
);
```

**Key Changes:**
- ✅ Use SDK client directly (more control)
- ✅ No custom provider abstraction needed
- ✅ Plugins can be added at agent creation

## 4. Thread Management

### Creating and Using Threads

#### Semantic Kernel (Old)
```csharp
// Threads were implicit or managed internally
var history = new ChatHistory();
// or
var threadId = await agent.CreateThreadAsync();
```

#### Microsoft Agent Framework (New)
```csharp
// Different thread types for different agent types

// For ChatCompletionAgent
var thread = new ChatHistoryAgentThread();

// For OpenAI Assistant
var thread = new OpenAIAssistantAgentThread(assistantClient);

// For Azure AI Agent
var thread = new AzureAIAgentThread(agentsClient);

// Use with agent
var response = await agent.InvokeAsync(
    messages: "Hello",
    thread: thread
);
```

**Benefits:**
- ✅ Type-safe thread management
- ✅ Thread abstraction works across agent types
- ✅ Explicit control over conversation state
- ✅ Can continue existing threads by ID

## 5. Plugins and Function Calling

### Plugin Registration

#### Both Versions (Mostly Unchanged)
```csharp
// Define plugin
public class WeatherPlugin
{
    [KernelFunction]
    [Description("Get weather for a location")]
    public string GetWeather(
        [Description("City name")] string city)
    {
        return $"Weather in {city}: Sunny, 72°F";
    }
}

// Semantic Kernel
kernel.Plugins.AddFromType<WeatherPlugin>();

// Agent Framework
var agent = new ChatClientAgent(
    chatClient,
    instructions: "...",
    plugins: [KernelPluginFactory.CreateFromType<WeatherPlugin>()]
);
```

**Note:** Plugin patterns are largely unchanged. The main difference is *when* and *how* you register them.

### Function Choice Behavior

#### Semantic Kernel (Old)
```csharp
var settings = new OpenAIPromptExecutionSettings
{
    FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
};

var agent = new ChatCompletionAgent
{
    Kernel = kernel,
    Arguments = new KernelArguments(settings)
};
```

#### Microsoft Agent Framework (New)
```csharp
// Auto function calling enabled by default for ChatClientAgent
var agent = new ChatClientAgent(
    chatClient,
    instructions: "...",
    plugins: [myPlugin]
);

// Customize if needed
var settings = new PromptExecutionSettings
{
    FunctionChoiceBehavior = FunctionChoiceBehavior.Required()
};
```

## 6. Multi-Agent Orchestration

### Agent Group Chat

#### Semantic Kernel (Old)
```csharp
var groupChat = new AgentGroupChat(agent1, agent2, agent3)
{
    ExecutionSettings = new AgentGroupChatSettings
    {
        SelectionStrategy = new SequentialSelectionStrategy()
    }
};

await foreach (var message in groupChat.InvokeAsync())
{
    Console.WriteLine($"{message.AuthorName}: {message.Content}");
}
```

#### Microsoft Agent Framework (New - Workflows)
```csharp
using Microsoft.Agents.Workflows;

// Sequential orchestration
var workflow = new SequentialWorkflowBuilder()
    .AddAgent(agent1)
    .AddAgent(agent2)
    .AddAgent(agent3)
    .Build();

await foreach (var update in workflow.RunStreamingAsync("Task input"))
{
    Console.WriteLine(update);
}
```

#### Microsoft Agent Framework (New - Magentic Pattern)
```csharp
// Dynamic multi-agent coordination (like AutoGen's Magentic-One)
var magentic = new MagenticOrchestration(
    manager: coordinatorAgent,
    agents: [agent1, agent2, agent3]
);

await foreach (var result in magentic.RunAsync("Complex task"))
{
    Console.WriteLine(result);
}
```

**Key Changes:**
- ✅ More orchestration patterns available
- ✅ Workflow-based approach for complex scenarios
- ✅ Better control over agent interaction
- ✅ Built-in support for concurrent, sequential, handoff patterns

## 7. Azure AI Agent Service

#### Semantic Kernel (Old)
```csharp
var agent = await AzureAIAgent.CreateAsync(
    kernel,
    config: new AzureAIAgentConfig
    {
        Endpoint = "...",
        ApiKey = "..."
    }
);
```

#### Microsoft Agent Framework (New)
```csharp
var credential = new AzureKeyCredential("...");
var agentsClient = new AgentsClient(
    new Uri("..."),
    credential
);

var agentDefinition = await agentsClient.CreateAgentAsync(
    model: "gpt-4",
    name: "Assistant",
    instructions: "..."
);

var agent = new AzureAIAgent(
    agentDefinition,
    agentsClient,
    plugins: [myPlugin]
);
```

## 8. Import Changes

### C# Namespaces

#### Semantic Kernel (Old)
```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Agents.OpenAI;
using Microsoft.SemanticKernel.Connectors.OpenAI;
```

#### Microsoft Agent Framework (New)
```csharp
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.OpenAI;
using Microsoft.Agents.Workflows;
```

### Python Imports

#### Semantic Kernel (Old)
```python
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.agents.open_ai import OpenAIAssistantAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
```

#### Microsoft Agent Framework (New)
```python
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.workflows import SequentialOrchestration
```

## Migration Strategies

### Strategy 1: Big Bang (Not Recommended)

Migrate everything at once.

**Pros:** Clean break
**Cons:** High risk, significant downtime

### Strategy 2: Incremental Migration (Recommended)

Migrate component by component:

1. **Start with new features**: Build new agents with Agent Framework
2. **Migrate simple agents**: Begin with single agents without complex orchestration
3. **Update orchestration**: Move multi-agent systems to workflows
4. **Refactor over time**: Gradually update older components

### Strategy 3: Side-by-Side

Run both frameworks in parallel:

```csharp
// Old Semantic Kernel agent
var skAgent = CreateSemanticKernelAgent();

// New Agent Framework agent
var afAgent = CreateAgentFrameworkAgent();

// Route based on feature flags
var agent = featureFlags.UseNewFramework ? afAgent : skAgent;
```

## Common Migration Patterns

### Pattern 1: Simple Chat Agent

**Before:**
```csharp
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(...)
    .Build();

var agent = new ChatCompletionAgent
{
    Kernel = kernel,
    Instructions = "..."
};

var history = new ChatHistory();
history.AddUserMessage("Hello");
await foreach (var msg in agent.InvokeAsync(history)) { }
```

**After:**
```csharp
var agent = new ChatClientAgent(
    AzureOpenAIChatClient.Create(...),
    instructions: "..."
);

var response = await agent.GetResponseAsync("Hello");
```

### Pattern 2: Agent with Plugins

**Before:**
```csharp
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(...)
    .Build();
kernel.Plugins.AddFromType<MyPlugin>();

var agent = new ChatCompletionAgent { Kernel = kernel, ... };
```

**After:**
```csharp
var agent = new ChatClientAgent(
    AzureOpenAIChatClient.Create(...),
    plugins: [KernelPluginFactory.CreateFromType<MyPlugin>()]
);
```

### Pattern 3: Multi-Agent Coordination

**Before:**
```csharp
var groupChat = new AgentGroupChat(agent1, agent2);
await foreach (var msg in groupChat.InvokeAsync()) { }
```

**After:**
```csharp
var workflow = new SequentialWorkflowBuilder()
    .AddAgent(agent1)
    .AddAgent(agent2)
    .Build();
await foreach (var update in workflow.RunStreamingAsync(input)) { }
```

## Testing Your Migration

### Unit Testing

```csharp
[Fact]
public async Task Agent_Responds_Correctly()
{
    // Arrange
    var mockClient = new MockChatClient();
    var agent = new ChatClientAgent(mockClient, instructions: "...");
    
    // Act
    var response = await agent.GetResponseAsync("Test");
    
    // Assert
    Assert.NotNull(response);
    Assert.Contains("expected", response.Message.Content);
}
```

### Integration Testing

```csharp
[Fact]
public async Task Workflow_Executes_Correctly()
{
    // Arrange
    var workflow = new SequentialWorkflowBuilder()
        .AddAgent(agent1)
        .AddAgent(agent2)
        .Build();
    
    // Act
    var results = new List<string>();
    await foreach (var update in workflow.RunStreamingAsync("input"))
    {
        results.Add(update.ToString());
    }
    
    // Assert
    Assert.NotEmpty(results);
}
```

## Troubleshooting

### Common Issues

#### Issue: "Kernel is null"
**Solution:** In Agent Framework, kernel is optional. Pass services directly.

#### Issue: "Function calling not working"
**Solution:** Ensure plugins are registered at agent construction and model supports function calling.

#### Issue: "Chat history not maintained"
**Solution:** Use `AgentThread` to maintain conversation state across turns.

#### Issue: "Can't find AgentGroupChat"
**Solution:** Use workflow orchestration patterns instead.

## Performance Considerations

### Memory Management

**Agent Framework** has better memory management:
- Automatic cleanup of resources
- Better async/await patterns
- Efficient thread management

### Throughput

**Agent Framework** provides:
- Better streaming performance
- Concurrent execution support
- Optimized for production workloads

## Additional Resources

- [Official Migration Guide](https://learn.microsoft.com/en-us/semantic-kernel/support/migration/agent-framework-rc-migration-guide)
- [Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Code Samples](../examples/)
- [API Reference](https://learn.microsoft.com/en-us/dotnet/api/microsoft.agents)

## Next Steps

1. ✅ Review your current Semantic Kernel implementation
2. ✅ Identify agents suitable for migration
3. ✅ Start with simplest agents first
4. ✅ Test thoroughly in non-production environment
5. ✅ Monitor performance and behavior
6. ✅ Gradually roll out to production

---

**Last Updated**: October 16, 2025

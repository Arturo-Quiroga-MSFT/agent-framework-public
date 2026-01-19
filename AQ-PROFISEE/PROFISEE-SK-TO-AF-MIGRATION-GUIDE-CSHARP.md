# Semantic Kernel to Agent Framework Migration Guide for Profisee (C#/.NET)

**Prepared for**: Profisee SK → AF Migration Workshop  
**Author**: Arturo Quiroga  
**Date**: December 15, 2025 (Updated: January 19, 2026)  
**Framework Versions**: Semantic Kernel 1.30+ → Agent Framework 1.0+  
**Target Framework**: .NET 10.0+ (backward compatible with .NET 6+)  
**Language**: C# / .NET

---

## Executive Summary

This guide provides comprehensive migration patterns from **Semantic Kernel (SK)** to **Microsoft Agent Framework (AF)** for C#/.NET applications. Agent Framework represents Microsoft's next-generation agentic platform with simplified APIs, better performance, and unified multi-agent orchestration capabilities.

### Key Benefits of Migration

✅ **Simplified API** - Reduced complexity and boilerplate code  
✅ **Better Performance** - Optimized object creation and memory usage  
✅ **Unified Interface** - Consistent patterns across AI providers  
✅ **Enhanced Developer Experience** - More intuitive and discoverable APIs  
✅ **Microsoft.Extensions.AI Integration** - Standard AI abstractions across .NET ecosystem  
✅ **Advanced Orchestration** - Built-in workflows (Sequential, Concurrent, Handoff)  
✅ **Seamless Migration Path** - Convert existing SK agents via `.AsAIAgent()` extension

---

## Table of Contents

1. [Namespace & Package Updates](#1-namespace--package-updates)
2. [Agent Type Consolidation](#2-agent-type-consolidation)
3. [Agent Creation Simplification](#3-agent-creation-simplification)
4. [Thread Management](#4-thread-management)
5. [Tool Registration](#5-tool-registration)
6. [Invocation Patterns](#6-invocation-patterns)
7. [Options Configuration](#7-options-configuration)
8. [Dependency Injection](#8-dependency-injection)
9. [Multi-Agent Orchestration](#9-multi-agent-orchestration)
 10. [Real-World Migration Examples](#10-real-world-migration-examples)
11. [Migration Checklist](#11-migration-checklist)

---

## 1. Namespace & Package Updates

### Semantic Kernel

```csharp
// Namespaces
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Microsoft.SemanticKernel.ChatCompletion;

// NuGet Packages
// Microsoft.SemanticKernel
// Microsoft.SemanticKernel.Agents.Core
// Microsoft.SemanticKernel.Connectors.OpenAI
```

### Agent Framework

```csharp
// Namespaces
using Microsoft.Agents.AI;              // Core agent types (AIAgent, ChatClientAgent)
using Microsoft.Extensions.AI;          // Standard AI abstractions (ChatMessage, etc.)
using OpenAI;                            // OpenAI SDK
using Azure.AI.OpenAI;                   // Azure OpenAI SDK

// NuGet Packages (install as needed)
// Microsoft.Agents.AI
// Microsoft.Extensions.AI
// Azure.AI.OpenAI
// OpenAI (if using OpenAI directly)
```

**Key Differences**:
- AF uses **`Microsoft.Agents.AI`** for agent types
- AF leverages **`Microsoft.Extensions.AI`** for standardized AI message/content types
- No separate connector packages - use provider SDKs directly
- Unified approach across all .NET AI libraries

---

## 2. Agent Type Consolidation

### Semantic Kernel

Multiple specialized agent classes for different services:

```csharp
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.Agents.OpenAI;
using Microsoft.SemanticKernel.Agents.AzureAI;

// Different agent types for different providers
ChatCompletionAgent chatAgent = new() { ... };           // Chat completion services
OpenAIAssistantAgent openAIAgent = new(...);             // OpenAI Assistants
AzureAIAgent azureAgent = new(...);                       // Azure AI Foundry
OpenAIResponseAgent responseAgent = new(...);            // OpenAI Responses
```

### Agent Framework

**Unified `AIAgent`** works with all `IChatClient`-based services:

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

// Single agent type for all providers implementing IChatClient
AIAgent agent = chatClient.AsAIAgent(
    instructions: "You are a helpful assistant"
);

// Works with:
// - OpenAI ChatClient
// - Azure OpenAI ChatClient  
// - Azure AI Foundry ChatClient
// - Any IChatClient implementation
```

**Benefits**:
- **Single agent type** for most scenarios
- **Swap chat clients** without changing agent code
- **Consistent API** across providers
- **Simpler dependency management**

---

## 3. Agent Creation Simplification

### Semantic Kernel

Every agent depends on a `Kernel` instance:

```csharp
// Build kernel
Kernel kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(modelId, apiKey)
    .Build();

// Create agent with kernel
ChatCompletionAgent agent = new()
{
    Kernel = kernel,
    Name = "Support",
    Instructions = "Answer customer questions in one paragraph."
};
```

**Azure AI Foundry** requires creating hosted agent first:

```csharp
PersistentAgentsClient azureAgentClient = 
    AzureAIAgent.CreateAgentsClient(azureEndpoint, new AzureCliCredential());

// Create hosted agent definition
PersistentAgent definition = await azureAgentClient.Administration.CreateAgentAsync(
    deploymentName,
    name: "Support",
    instructions: "Answer customer questions."
);

// Wrap in local agent class
AzureAIAgent agent = new(definition, azureAgentClient);
```

### Agent Framework

**No Kernel required** - direct construction via extension methods:

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using OpenAI;

// OpenAI - Single line creation
AIAgent openAIAgent = new OpenAIClient(apiKey)
    .GetChatClient(model)
    .AsAIAgent(
        name: "Support",
        instructions: "Answer customer questions."
    );

// Azure OpenAI
AIAgent azureAgent = new AzureOpenAIClient(new Uri(endpoint), new AzureCliCredential())
    .GetChatClient(deploymentName)
    .AsAIAgent(
        name: "Support",
        instructions: "Answer customer questions."
    );

// Azure AI Foundry - Single call creation
var azureAgentClient = new PersistentAgentsClient(azureEndpoint, new AzureCliCredential());
AIAgent foundryAgent = await azureAgentClient.CreateAIAgentAsync(
    deploymentName,
    name: "Support",
    instructions: "Answer customer questions."
);

// OpenAI Assistants
var assistantClient = new AssistantClient(apiKey);
AIAgent assistantAgent = await assistantClient.CreateAIAgentAsync(
    model,
    name: "Support",
    instructions: "Answer customer questions."
);
```

**Retrieve existing hosted agent**:

```csharp
// Get existing agent by ID
AIAgent existingAgent = await persistentAgentsClient.GetAIAgentAsync(agentId);
```

**Benefits**:
- No boilerplate `Kernel` object
- Provider-specific extension methods
- More discoverable API
- Cleaner code

### Provider-Specific Agent Types (New in 2026)

Agent Framework now includes **provider-specific agent classes** for direct construction:

```csharp
using OpenAI;
using OpenAI.Chat;
using Microsoft.Agents.AI;

// OpenAI ChatClient-based agent
ChatClient chatClient = new OpenAIClient(apiKey).GetChatClient(model);
OpenAIChatClientAgent chatAgent = new(chatClient, 
    instructions: "You are helpful", 
    name: "Assistant");

// OpenAI Responses-based agent
ResponsesClient responseClient = new OpenAIClient(apiKey).GetResponsesClient(model);
OpenAIResponseClientAgent responseAgent = new(responseClient,
    instructions: "You are helpful",
    name: "Assistant");
```

**When to use provider-specific types vs. `.AsAIAgent()`:**
- **Provider-specific** (`OpenAIChatClientAgent`): Use when you need strong typing and provider-specific features
- **Extension method** (`.AsAIAgent()`): Use for provider-agnostic code and simpler scenarios

Both approaches are valid and interchangeable. The extension method is more concise for most scenarios.

---

## 4. Thread Management

### Semantic Kernel

**Manual thread creation** - caller must know thread type:

```csharp
// Different thread types for different providers
AgentThread assistantThread = new OpenAIAssistantAgentThread(assistantsClient);
AgentThread azureThread = new AzureAIAgentThread(azureClient);
AgentThread responseThread = new OpenAIResponseAgentThread(openAIClient);
AgentThread chatThread = new ChatHistoryAgentThread(); // In-memory

// Invoke with thread
await foreach (var result in agent.InvokeAsync(userInput, assistantThread))
{
    Console.WriteLine(result.Message);
}
```

**Thread cleanup** - different methods per provider:

```csharp
// SK: Threads have self-deletion methods
await assistantThread.DeleteAsync();  // OpenAI Assistants
```

### Agent Framework

**Agent-managed threads** - let the agent create appropriate thread type:

```csharp
AIAgent agent = ...;

// Agent creates correct thread type automatically
AgentThread thread = agent.GetNewThread();

// Run with thread
AgentRunResponse response = await agent.RunAsync(userInput, thread);
Console.WriteLine(response.Text);
```

**Thread cleanup** - use provider SDK directly:

```csharp
// AF: No universal thread deletion API
// Use provider SDK when needed

// OpenAI Assistants thread deletion
if (thread is ChatClientAgentThread chatThread)
{
    await assistantClient.DeleteThreadAsync(chatThread.ConversationId);
}

// Azure AI Foundry thread deletion
if (thread is ChatClientAgentThread chatThread)
{
    await azureAgentClient.Threads.DeleteThreadAsync(chatThread.ConversationId);
}
```

**Why no universal deletion API?**  
Not all providers support hosted threads or thread deletion. OpenAI Responses and similar services use conversation models that don't require explicit thread management. AF design anticipates this becoming more common.

---

## 5. Tool Registration

### Semantic Kernel

**Multi-step process**: Attribute → Factory → Plugin → Kernel → Agent

```csharp
using Microsoft.SemanticKernel;
using System.ComponentModel;

// Step 1: Mark function with attribute
[KernelFunction]
[Description("Get the weather for a given location")]
static string GetWeather([Description("Location")] string location)
    => $"The weather in {location} is sunny.";

// Step 2: Create KernelFunction
KernelFunction function = KernelFunctionFactory.CreateFromMethod(GetWeather);

// Step 3: Create plugin
KernelPlugin plugin = KernelPluginFactory.CreateFromFunctions(
    "WeatherPlugin", 
    [function]
);

// Step 4: Add to kernel
Kernel kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(model, apiKey)
    .Build();
kernel.Plugins.Add(plugin);

// Step 5: Create agent with kernel
ChatCompletionAgent agent = new()
{
    Kernel = kernel,
    Instructions = "You are a weather assistant."
};
```

### Agent Framework

**Single-step registration** - directly on agent creation:

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using System.ComponentModel;

// Step 1: Define function (no attribute required)
[Description("Get the weather for a given location")]
static string GetWeather([Description("Location")] string location)
    => $"The weather in {location} is sunny.";

// Step 2: Create agent with tool - single call
AIAgent agent = chatClient.AsAIAgent(
    instructions: "You are a weather assistant.",
    tools: [AIFunctionFactory.Create(GetWeather)]
);

// Alternative: Register on options at runtime
var options = new ChatClientAgentRunOptions(new()
{
    Tools = [AIFunctionFactory.Create(GetWeather)]
});
AgentRunResponse response = await agent.RunAsync(userInput, thread, options);
```

**Class-based tools** (similar to SK plugins):

```csharp
public class WeatherTools
{
    [Description("Get current weather")]
    public static string GetWeather([Description("Location")] string location)
        => $"The weather in {location} is sunny.";
    
    [Description("Get 7-day forecast")]
    public static string GetForecast([Description("Location")] string location)
        => $"The forecast for {location} is sunny all week.";
}

// Register multiple methods
AIAgent agent = chatClient.AsAIAgent(
    tools: [
        AIFunctionFactory.Create(WeatherTools.GetWeather),
        AIFunctionFactory.Create(WeatherTools.GetForecast)
    ]
);
```

**Benefits**:
- No kernel required
- No plugin wrapper needed
- Direct function registration
- Simpler, more intuitive

---

### Backward Compatibility: Converting SK Agents to AF

**Critical for migration**: You can convert existing SK agents to AF agents!

```csharp
using Microsoft.SemanticKernel.Agents;
using Microsoft.Agents.AI;

// Existing SK agent
Kernel kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(model, apiKey)
    .Build();

ChatCompletionAgent skAgent = new()
{
    Kernel = kernel,
    Name = "Joker",
    Instructions = "You are good at telling jokes."
};

// Convert to AF agent
#pragma warning disable SKEXP0110
AIAgent afAgent = skAgent.AsAIAgent();
#pragma warning restore SKEXP0110

// Use AF invocation patterns
AgentRunResponse response = await afAgent.RunAsync("Tell me a joke");
Console.WriteLine(response.Text);
```

**Works with**:
- `ChatCompletionAgent`
- `OpenAIAssistantAgent`
- `AzureAIAgent`
- `OpenAIResponseAgent`

**Migration Strategy**:
1. Start by converting existing SK agents using `.AsAIAgent()`
2. Gradually rewrite as native AF agents
3. Maintain both during transition period

---

## 6. Invocation Patterns

### Non-Streaming

#### Semantic Kernel

**Async enumerable pattern** for multiple agent messages:

```csharp
var agentOptions = new AgentInvokeOptions()
{
    KernelArguments = new(new OpenAIPromptExecutionSettings()
    {
        MaxTokens = 1000
    })
};

await foreach (AgentResponseItem<ChatMessageContent> result 
    in agent.InvokeAsync(userInput, thread, agentOptions))
{
    Console.WriteLine(result.Message);
}
```

#### Agent Framework

**Single response object** with all messages:

```csharp
var agentOptions = new ChatClientAgentRunOptions(new()
{
    MaxOutputTokens = 1000
});

AgentRunResponse response = await agent.RunAsync(userInput, thread, agentOptions);

// Access text result
Console.WriteLine(response.Text);          // or response.ToString()

// All messages created during execution
foreach (var message in response.Messages)
{
    Console.WriteLine($"{message.Role}: {message.Text}");
}
```

**Key Differences**:
- AF: Method name `RunAsync` (not `InvokeAsync`)
- AF: Returns `AgentRunResponse` (single object)
- AF: `response.Text` property for main result
- AF: `response.Messages` list for full conversation

---

### Streaming

#### Semantic Kernel

```csharp
await foreach (StreamingChatMessageContent update 
    in agent.InvokeStreamingAsync(userInput, thread))
{
    Console.Write(update.Content);
}
```

#### Agent Framework

```csharp
// Option 1: Stream and print
await foreach (AgentRunResponseUpdate update 
    in agent.RunStreamingAsync(userInput, thread))
{
    Console.Write(update);  // ToString() friendly
}

// Option 2: Collect updates
var updates = new List<AgentRunResponseUpdate>();
await foreach (var update in agent.RunStreamingAsync(userInput, thread))
{
    updates.Add(update);
    Console.Write(update.Text);
}

// Combine into full response (if needed)
AgentRunResponse fullResponse = AgentRunResponse.Combine(updates);
```

**Key Differences**:
- AF: Method name `RunStreamingAsync` (not `InvokeStreamingAsync`)
- AF: Returns `AgentRunResponseUpdate` objects
- AF: Updates are `ToString()` friendly
- AF: Can combine updates into final response

---

## 7. Options Configuration

### Semantic Kernel

**Complex options setup** with nested objects:

```csharp
using Microsoft.SemanticKernel.Connectors.OpenAI;

// Create execution settings
OpenAIPromptExecutionSettings settings = new()
{
    MaxTokens = 1000,
    Temperature = 0.7,
    TopP = 0.9,
    FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
};

// Wrap in kernel arguments
KernelArguments arguments = new(settings);

// Wrap in agent options
AgentInvokeOptions options = new()
{
    KernelArguments = arguments
};

// Invoke with options
var response = await agent.InvokeAsync(userInput, thread, options).FirstAsync();
```

### Agent Framework

**Simplified options** - direct property access:

```csharp
using Microsoft.Extensions.AI;

// Create options directly
ChatClientAgentRunOptions options = new(new()
{
    MaxOutputTokens = 1000,
    Temperature = 0.7f,
    TopP = 0.9f,
    ToolMode = ChatToolMode.Auto
});

// Run with options
AgentRunResponse response = await agent.RunAsync(userInput, thread, options);
```

**Or use ChatOptions directly**:

```csharp
ChatOptions chatOptions = new()
{
    MaxOutputTokens = 1000,
    Temperature = 0.7f,
    TopP = 0.9f
};

ChatClientAgentRunOptions options = new(chatOptions);
AgentRunResponse response = await agent.RunAsync(userInput, thread, options);
```

**Benefits**:
- No nested object hierarchy
- More discoverable via IntelliSense
- Can pass different options per call

---

## 8. Dependency Injection

### Semantic Kernel

**Requires Kernel registration**:

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

var services = new ServiceCollection();

// Register kernel
services.AddKernel()
    .AddOpenAIChatCompletion(model, apiKey);

// Register agent (requires kernel)
services.AddTransient<ChatCompletionAgent>(sp => new()
{
    Kernel = sp.GetRequiredService<Kernel>(),  // Required
    Name = "Joker",
    Instructions = "You are good at telling jokes."
});

// Use SK Agent base type
await using var serviceProvider = services.BuildServiceProvider();
var agent = serviceProvider.GetRequiredService<ChatCompletionAgent>();

await foreach (var item in agent.InvokeAsync(userInput))
{
    Console.WriteLine(item.Message);
}
```

### Agent Framework

**No kernel needed** - direct registration:

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Agents.AI;

var services = new ServiceCollection();

// Register AIAgent directly
services.AddTransient<AIAgent>(sp => 
    new OpenAIClient(apiKey)
        .GetChatClient(model)
        .AsAIAgent(
            name: "Joker",
            instructions: "You are good at telling jokes."
        )
);

// Or with keyed services for multiple agents
services.AddKeyedSingleton<AIAgent>("joker", (sp, key) => 
    new OpenAIClient(apiKey)
        .GetChatClient(model)
        .AsAIAgent(
            name: "Joker",
            instructions: "You are good at telling jokes."
        )
);

// Use AIAgent base type
await using var serviceProvider = services.BuildServiceProvider();
var agent = serviceProvider.GetRequiredService<AIAgent>();

AgentRunResponse response = await agent.RunAsync(userInput);
Console.WriteLine(response.Text);
```

**Benefits**:
- No kernel registration
- Simpler service configuration
- Standard `AIAgent` base type
- Keyed services for multiple agents

---

## 9. Multi-Agent Orchestration

### Sequential Orchestration

#### Semantic Kernel

```csharp
using Microsoft.SemanticKernel.Agents.Orchestration;
using Microsoft.SemanticKernel.Agents.Orchestration.Sequential;
using Microsoft.SemanticKernel.Agents.Runtime.InProcess;

// Create agents
ChatCompletionAgent writer = new() { ... };
ChatCompletionAgent reviewer = new() { ... };

// Create orchestration
SequentialOrchestration orchestration = new(
    members: [writer, reviewer],
    streamingAgentResponseCallback: StreamingCallback
);

// Create runtime
InProcessRuntime runtime = new();
runtime.Start();

try
{
    // Invoke orchestration
    var orchestrationResult = await orchestration.InvokeAsync(
        task: "Write a tagline for a budget-friendly eBike",
        runtime: runtime
    );
    
    var finalMessage = await orchestrationResult.Get(timeout: 20);
    Console.WriteLine(finalMessage);
}
finally
{
    await runtime.StopWhenIdleAsync();
}
```

#### Agent Framework

```csharp
using Microsoft.Agents.AI.Workflows;
using Azure.AI.OpenAI;
using Azure.Identity;

// Create agents
var chatClient = new AzureOpenAIClient(new Uri(endpoint), new AzureCliCredential())
    .GetChatClient(deploymentName);

AIAgent writer = chatClient.AsAIAgent(
    name: "writer",
    instructions: "You are a creative copywriter."
);

AIAgent reviewer = chatClient.AsAIAgent(
    name: "reviewer",
    instructions: "You are a thoughtful reviewer."
);

// Create workflow
var workflow = new SequentialBuilder()
    .Participants([writer, reviewer])
    .Build();

// Run workflow (streaming)
await foreach (var @event in workflow.RunStreamingAsync("Write a tagline for a budget-friendly eBike"))
{
    if (@event is WorkflowOutputEvent output)
    {
        var messages = (List<ChatMessage>)output.Data;
        foreach (var msg in messages)
        {
            Console.WriteLine($"{msg.AuthorName}: {msg.Text}");
        }
    }
}
```

**Key Differences**:
- AF: No runtime management needed
- AF: Builder pattern for construction
- AF: Event-based output via `WorkflowOutputEvent`
- AF: Built-in streaming support

---

### Concurrent Orchestration

#### Semantic Kernel

```csharp
using Microsoft.SemanticKernel.Agents.Orchestration;
using Microsoft.SemanticKernel.Agents.Orchestration.Concurrent;

// Create agents
ChatCompletionAgent physics = new() { ... };
ChatCompletionAgent chemistry = new() { ... };

// Create orchestration
ConcurrentOrchestration orchestration = new(
    members: [physics, chemistry]
);

InProcessRuntime runtime = new();
runtime.Start();

try
{
    var result = await orchestration.InvokeAsync(
        task: "Explain temperature from different perspectives",
        runtime: runtime
    );
    
    var outputs = await result.Get(timeout: 60);
}
finally
{
    await runtime.StopWhenIdleAsync();
}
```

#### Agent Framework

```csharp
using Microsoft.Agents.AI.Workflows;

AIAgent physics = chatClient.AsAIAgent(
    name: "physics",
    instructions: "You are a physics expert."
);

AIAgent chemistry = chatClient.AsAIAgent(
    name: "chemistry",
    instructions: "You are a chemistry expert."
);

// Create workflow
var workflow = new ConcurrentBuilder()
    .Participants([physics, chemistry])
    .Build();

// Run workflow
await foreach (var @event in workflow.RunStreamingAsync("Explain temperature"))
{
    if (@event is WorkflowOutputEvent output)
    {
        // Process concurrent outputs
    }
}
```

---

### Handoff Orchestration

```csharp
using Microsoft.Agents.AI.Workflows;

// Create specialized agents
AIAgent triage = chatClient.AsAIAgent(...);
AIAgent refund = chatClient.AsAIAgent(...);
AIAgent orderStatus = chatClient.AsAIAgent(...);

// Create handoff workflow
var workflow = new HandoffBuilder()
    .AddAgent(triage)
    .AddAgent(refund, handoffCondition: /* when refund needed */)
    .AddAgent(orderStatus, handoffCondition: /* when status needed */)
    .Build();

// Run workflow
await foreach (var @event in workflow.RunStreamingAsync("I need a refund for order 12345"))
{
    // Process handoff events
}
```

---

## 10. Real-World Migration Examples

### Example 1: Basic Chat Agent

#### Before (SK)

```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(deploymentName, endpoint, new AzureCliCredential())
    .Build();

ChatCompletionAgent agent = new()
{
    Kernel = kernel,
    Name = "Support",
    Instructions = "Answer customer questions in one paragraph."
};

var thread = new ChatHistoryAgentThread();
var settings = new OpenAIPromptExecutionSettings() { MaxTokens = 1000 };
var options = new AgentInvokeOptions() { KernelArguments = new(settings) };

await foreach (var result in agent.InvokeAsync(userInput, thread, options))
{
    Console.WriteLine(result.Message);
}
```

#### After (AF)

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Azure.AI.OpenAI;
using Azure.Identity;

AIAgent agent = new AzureOpenAIClient(new Uri(endpoint), new AzureCliCredential())
    .GetChatClient(deploymentName)
    .AsAIAgent(
        name: "Support",
        instructions: "Answer customer questions in one paragraph."
    );

var thread = agent.GetNewThread();
var options = new ChatClientAgentRunOptions(new() { MaxOutputTokens = 1000 });

AgentRunResponse response = await agent.RunAsync(userInput, thread, options);
Console.WriteLine(response.Text);
```

**Lines of code**: 15 → 8 (47% reduction)

---

### Example 2: Agent with Tools

#### Before (SK)

```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using System.ComponentModel;

[KernelFunction]
[Description("Get weather for a location")]
static string GetWeather([Description("Location")] string location)
    => $"The weather in {location} is sunny.";

var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(model, apiKey)
    .Build();

var function = KernelFunctionFactory.CreateFromMethod(GetWeather);
var plugin = KernelPluginFactory.CreateFromFunctions("Weather", [function]);
kernel.Plugins.Add(plugin);

ChatCompletionAgent agent = new()
{
    Kernel = kernel,
    Instructions = "You are a weather assistant",
    Arguments = new KernelArguments(new PromptExecutionSettings()
    {
        FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
    })
};

await foreach (var item in agent.InvokeAsync("What's the weather in Amsterdam?"))
{
    Console.WriteLine(item.Message);
}
```

#### After (AF)

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using System.ComponentModel;

[Description("Get weather for a location")]
static string GetWeather([Description("Location")] string location)
    => $"The weather in {location} is sunny.";

AIAgent agent = new OpenAIClient(apiKey)
    .GetChatClient(model)
    .AsAIAgent(
        instructions: "You are a weather assistant",
        tools: [AIFunctionFactory.Create(GetWeather)]
    );

AgentRunResponse response = await agent.RunAsync("What's the weather in Amsterdam?");
Console.WriteLine(response.Text);
```

**Lines of code**: 26 → 11 (58% reduction)

---

### Example 3: Azure AI Foundry Agent

#### Before (SK)

```csharp
using Microsoft.SemanticKernel.Agents.AzureAI;
using Azure.AI.Agents.Persistent;
using Azure.Identity;

var azureAgentClient = AzureAIAgent.CreateAgentsClient(
    azureEndpoint, 
    new AzureCliCredential()
);

PersistentAgent definition = await azureAgentClient.Administration.CreateAgentAsync(
    deploymentName,
    name: "StoryAgent",
    instructions: "Tell stories suitable for children."
);

AzureAIAgent agent = new(definition, azureAgentClient);

var thread = new AzureAIAgentThread(azureAgentClient);
var settings = new OpenAIPromptExecutionSettings() { MaxTokens = 1000 };
var options = new AzureAIAgentInvokeOptions() { KernelArguments = new(settings) };

await foreach (var result in agent.InvokeAsync(userInput, thread, options))
{
    Console.WriteLine(result.Message);
}

// Cleanup
await thread.DeleteAsync();
await azureAgentClient.Administration.DeleteAgentAsync(agent.Id);
```

#### After (AF)

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Azure.AI.Agents.Persistent;
using Azure.Identity;

var azureAgentClient = new PersistentAgentsClient(
    azureEndpoint, 
    new AzureCliCredential()
);

AIAgent agent = await azureAgentClient.CreateAIAgentAsync(
    deploymentName,
    name: "StoryAgent",
    instructions: "Tell stories suitable for children."
);

var thread = agent.GetNewThread();
var options = new ChatClientAgentRunOptions(new() { MaxOutputTokens = 1000 });

AgentRunResponse response = await agent.RunAsync(userInput, thread, options);
Console.WriteLine(response.Text);

// Cleanup
if (thread is ChatClientAgentThread chatThread)
{
    await azureAgentClient.Threads.DeleteThreadAsync(chatThread.ConversationId);
}
await azureAgentClient.Administration.DeleteAgentAsync(agent.Id);
```

**Key improvements**:
- Single `CreateAIAgentAsync` call (no separate definition step)
- Agent handles thread creation
- Simpler invocation pattern

---

### Example 4: OpenAPI Tools Integration

#### Before (SK)

```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(deploymentName, endpoint, new AzureCliCredential())
    .Build();

// Import OpenAPI plugin
var plugin = await kernel.ImportPluginFromOpenApiAsync("github", "OpenAPISpec.json");

ChatCompletionAgent agent = new()
{
    Kernel = kernel,
    Instructions = "You are a helpful assistant",
    Arguments = new KernelArguments(new PromptExecutionSettings()
    {
        FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
    })
};

await foreach (var result in agent.InvokeAsync(
    "List all labels in the microsoft/agent-framework repository"))
{
    Console.WriteLine(result.Message);
}
```

#### After (AF)

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.OpenApi.Readers;

// Load OpenAPI spec
var openApiDocument = new OpenApiStreamReader().Read(
    File.OpenRead("OpenAPISpec.json"), 
    out var diagnostic
);

// Convert to AF tools
var tools = AIFunctionFactory.CreateFromOpenApi(openApiDocument);

AIAgent agent = new AzureOpenAIClient(new Uri(endpoint), new AzureCliCredential())
    .GetChatClient(deploymentName)
    .AsAIAgent(
        instructions: "You are a helpful assistant",
        tools: tools
    );

AgentRunResponse response = await agent.RunAsync(
    "List all labels in the microsoft/agent-framework repository"
);
Console.WriteLine(response.Text);
```

---

## 11. Migration Checklist

### Phase 1: Assessment (1-2 weeks)

- [ ] **Inventory SK usage** across codebase
  - Count `ChatCompletionAgent`, `OpenAIAssistantAgent`, etc.
  - List all `[KernelFunction]` tools/plugins
  - Document orchestration patterns
  - Note Kernel customizations
  
- [ ] **Identify dependencies**
  - Which SK NuGet packages are used?
  - Any custom SK integrations?
  - OpenAPI plugin usage?
  
- [ ] **Review agent configurations**
  - Document all agent instructions/prompts
  - List execution settings (temperature, max tokens, etc.)
  - Identify domain-specific rules
  
- [ ] **Map tool/function catalog**
  - List all `[KernelFunction]` methods
  - Document plugin classes
  - Note tool dependencies (databases, APIs, etc.)

### Phase 2: Setup (1 week)

- [ ] **Install AF NuGet packages**
  ```bash
  # Core package
  dotnet add package Microsoft.Agents.AI --prerelease
  
  # Extensions.AI (usually included as dependency)
  dotnet add package Microsoft.Extensions.AI --prerelease
  
  # Provider SDKs
  dotnet add package Azure.AI.OpenAI
  dotnet add package OpenAI  # if using OpenAI directly
  ```

- [ ] **Update using statements**
  ```csharp
  using Microsoft.Agents.AI;
  using Microsoft.Extensions.AI;
  ```

- [ ] **Configure credentials**
  ```csharp
  using Azure.Identity;
  var credential = new AzureCliCredential();
  ```

### Phase 3: Parallel Implementation (2-4 weeks)

**Strategy**: Implement AF alongside SK, don't replace immediately.

- [ ] **Convert SK agents to AF using compatibility layer**
  ```csharp
  // Keep SK agent running
  ChatCompletionAgent skAgent = new() { ... };
  
  // Convert to AF agent
  AIAgent afAgent = skAgent.AsAIAgent();
  
  // Compare responses
  var skResponse = await skAgent.InvokeAsync(question).FirstAsync();
  var afResponse = await afAgent.RunAsync(question);
  ```

- [ ] **Create parallel AF implementations**
  - Implement same agents in native AF
  - Keep SK versions for comparison
  - A/B test responses

- [ ] **Migrate tools incrementally**
  ```csharp
  // Phase 1: Convert existing functions
  AIFunctionFactory.Create(ExistingMethod)
  
  // Phase 2: Remove [KernelFunction] attributes if desired
  // (Optional - not required for AF)
  ```

### Phase 4: Native AF Migration (2-4 weeks)

- [ ] **Rewrite agents as native AF**
  ```csharp
  // From SK
  ChatCompletionAgent skAgent = new()
  {
      Kernel = kernel,
      ...
  };
  
  // To AF
  AIAgent afAgent = chatClient.AsAIAgent(...);
  ```

- [ ] **Remove Kernel dependencies**
  - Delete `Kernel.CreateBuilder()` calls
  - Remove kernel plugin registration
  - Clean up using statements

- [ ] **Adopt AF orchestration patterns**
  ```csharp
  // Replace SK orchestration
  var workflow = new SequentialBuilder()
      .Participants([agent1, agent2])
      .Build();
  ```

- [ ] **Update error handling**
  ```csharp
  // AF uses different exception patterns
  try
  {
      var response = await agent.RunAsync(...);
  }
  catch (Exception ex)
  {
      // Handle AF-specific errors
  }
  ```

### Phase 5: Testing & Validation (2-3 weeks)

- [ ] **Unit tests**
  - Test agent creation
  - Test tool invocation
  - Test thread management
  - Test streaming
  
- [ ] **Integration tests**
  - Test full workflows
  - Test orchestration patterns
  - Test error scenarios
  - Test multi-provider scenarios
  
- [ ] **Performance testing**
  - Compare latency (SK vs AF)
  - Measure memory usage
  - Monitor token consumption
  - Load testing
  
- [ ] **Quality assurance**
  - Validate response quality
  - Check for regressions
  - User acceptance testing
  - Security review

### Phase 6: Cutover (1-2 weeks)

- [ ] **Feature flag rollout**
  ```csharp
  if (UseAgentFramework)
  {
      response = await afAgent.RunAsync(question);
  }
  else
  {
      response = await skAgent.InvokeAsync(question).FirstAsync();
  }
  ```

- [ ] **Monitor production**
  - Error rates
  - Response times
  - User satisfaction
  - Token usage

- [ ] **Remove SK code**
  - Delete SK agent implementations
  - Remove SK NuGet packages
  - Clean up dead code
  - Update documentation

- [ ] **Documentation update**
  - Update developer guides
  - Revise architecture docs
  - Create runbooks
  - Update API documentation

---

## Key Takeaways for Profisee

### 1. **Start with Compatibility Layer**

Don't rewrite everything at once. Use `.AsAIAgent()` extension method:

```csharp
// Day 1: Convert existing SK agents
ChatCompletionAgent skAgent = new() { Kernel = kernel, ... };
AIAgent afAgent = skAgent.AsAIAgent();

// Later: Gradually migrate to native AF
AIAgent nativeAgent = chatClient.AsAIAgent(...);
```

### 2. **Leverage Microsoft.Extensions.AI**

Agent Framework builds on standard .NET AI abstractions:
- **`IChatClient`** - Standard chat interface
- **`ChatMessage`** - Standard message type
- **`ChatOptions`** - Standard configuration
- Works across entire .NET AI ecosystem

### 3. **Simplified Dependency Injection**

No Kernel registration needed:

```csharp
// SK: Complex setup
services.AddKernel().AddProvider(...);
services.AddTransient<ChatCompletionAgent>(sp => new() 
{ 
    Kernel = sp.GetRequiredService<Kernel>() 
});

// AF: Direct registration
services.AddTransient<AIAgent>(sp => 
    chatClient.AsAIAgent(...)
);
```

### 4. **Better Developer Experience**

Observed productivity gains:
- **50% less code** for equivalent functionality
- **No Kernel boilerplate**
- **Better IntelliSense** support
- **Clearer error messages**

### 5. **Production-Ready**

Agent Framework is Microsoft's strategic direction:
- **Active development** - Monthly updates
- **First-class Azure integration**
- **Performance optimized**
- **Enterprise support**

---

## Resources

### Official Documentation

- **AF Migration Guide (C#)**: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/?pivots=programming-language-csharp
- **AF Repository**: https://github.com/microsoft/agent-framework
- **SK→AF Samples (C#)**: https://github.com/microsoft/semantic-kernel/tree/main/dotnet/samples/AgentFrameworkMigration

### Profisee-Specific Resources

- **Local AF Code**: `/dotnet/` directory
- **This Guide**: `PROFISEE-SK-TO-AF-MIGRATION-GUIDE-CSHARP.md`

### Migration Samples in SK Repository

The semantic-kernel repository includes comprehensive side-by-side examples:

1. **Azure OpenAI** (`AzureOpenAI/`)
   - Step01_Basics
   - Step02_ToolCall
   - Step03_DependencyInjection
   - Step04_ToolCall_WithOpenAPI

2. **OpenAI** (`OpenAI/`)
   - Step01_Basics
   - Step02_ToolCall
   - Step03_DependencyInjection

3. **Azure OpenAI Assistants** (`AzureOpenAIAssistants/`)
   - Step01_Basics
   - Step02_ToolCall

4. **OpenAI Assistants** (`OpenAIAssistants/`)
   - Step01_Basics
   - Step02_ToolCall
   - Step03_DependencyInjection

5. **OpenAI Responses** (`OpenAIResponses/`)
   - Step01_Basics
   - Step02_ReasoningModel

6. **Azure AI Foundry** (`AzureAIFoundry/`)
   - Step01_Basics
   - Step02_ToolCall

7. **Agent Orchestrations** (`AgentOrchestrations/`)
   - Step01_Concurrent
   - Step02_Sequential
   - Step03_Handoff

---

## Next Steps for Profisee Workshop

### Pre-Workshop

1. **Share your SK codebase** patterns (anonymized if needed)
2. **List your critical tools/functions** for migration assessment
3. **Identify 1-2 pilot agents** for live migration demo
4. **Document your orchestration patterns** (if multi-agent)

### During Workshop

1. **Live migration demo** of one of your agents
2. **Review compatibility layer** using `.AsAIAgent()`
3. **Discuss DI patterns** for your architecture
4. **Walk through orchestration** if you use multi-agent patterns
5. **Q&A on specific migration challenges**

### Post-Workshop

1. **Pilot project** - Migrate 1-2 low-risk agents
2. **Performance validation** - Compare SK vs AF metrics
3. **Roadmap creation** - Plan phased migration
4. **Ongoing support** - Regular check-ins during migration

---

**Let's make your SK → AF migration smooth and successful! 🚀**

---

*Questions? Contact: Arturo Quiroga*  
*Updated: December 15, 2025*

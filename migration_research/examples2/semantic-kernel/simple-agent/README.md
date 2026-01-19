# Simple Agent Migration Example

This example demonstrates migrating a basic chat agent from Semantic Kernel to Microsoft Agent Framework.

## Scenario

A simple chatbot that:
- Uses Azure OpenAI
- Maintains conversation history
- Responds to user messages

## Before: Semantic Kernel

### Code (before.cs)

```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;

// Create kernel with Azure OpenAI service
var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    deploymentName: "gpt-4",
    endpoint: "https://your-resource.openai.azure.com/",
    apiKey: Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY")!
);
var kernel = builder.Build();

// Create agent
var agent = new ChatCompletionAgent
{
    Kernel = kernel,
    Name = "Assistant",
    Instructions = "You are a helpful AI assistant. Be concise and friendly."
};

// Conversation loop
var history = new ChatHistory();
Console.WriteLine("Chat started. Type 'exit' to quit.\n");

while (true)
{
    Console.Write("You: ");
    var userMessage = Console.ReadLine();
    
    if (string.IsNullOrWhiteSpace(userMessage) || userMessage == "exit")
        break;
    
    history.AddUserMessage(userMessage);
    
    // Get agent response
    await foreach (var message in agent.InvokeAsync(history))
    {
        history.Add(message);
        Console.WriteLine($"Assistant: {message.Content}");
    }
}
```

### Key Characteristics (Before)

1. **Kernel Required**: Must create and configure a kernel
2. **Service Configuration**: Added to kernel builder
3. **Agent Creation**: Properties-based initialization
4. **Chat History**: Manual ChatHistory management
5. **Invocation**: `InvokeAsync` with history parameter

## After: Microsoft Agent Framework

### Code (after.cs)

```csharp
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.OpenAI;

// Create agent with direct service configuration
var agent = chatClient.AsAIAgent(
    chatClient: AzureOpenAIChatClient.Create(
        endpoint: new Uri("https://your-resource.openai.azure.com/"),
        credential: new Azure.AzureKeyCredential(
            Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY")!
        ),
        deploymentName: "gpt-4"
    ),
    instructions: "You are a helpful AI assistant. Be concise and friendly.",
    name: "Assistant"
);

// Create thread for conversation continuity
var thread = new ChatHistoryAgentThread();

// Conversation loop
Console.WriteLine("Chat started. Type 'exit' to quit.\n");

while (true)
{
    Console.Write("You: ");
    var userMessage = Console.ReadLine();
    
    if (string.IsNullOrWhiteSpace(userMessage) || userMessage == "exit")
        break;
    
    // Get agent response with automatic history management
    var response = await agent.InvokeAsync(
        messages: userMessage,
        thread: thread
    );
    
    Console.WriteLine($"Assistant: {response.Message.Content}");
}
```

### Key Characteristics (After)

1. **No Kernel Required**: Direct service configuration
2. **Simpler Initialization**: Constructor-based setup
3. **Thread Abstraction**: `AgentThread` manages conversation state
4. **Cleaner Invocation**: Single method with clear parameters
5. **Less Boilerplate**: Fewer lines of code

## Key Changes

### 1. Service Configuration

**Before:**
```csharp
var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(...);
var kernel = builder.Build();
```

**After:**
```csharp
var chatClient = AzureOpenAIChatClient.Create(...);
```

✅ **Benefit**: Direct configuration, no kernel ceremony

### 2. Agent Creation

**Before:**
```csharp
var agent = new ChatCompletionAgent
{
    Kernel = kernel,
    Name = "Assistant",
    Instructions = "..."
};
```

**After:**
```csharp
var agent = chatClient.AsAIAgent(
    chatClient,
    instructions: "...",
    name: "Assistant"
);
```

✅ **Benefit**: Constructor-based, more idiomatic C#

### 3. Conversation Management

**Before:**
```csharp
var history = new ChatHistory();
history.AddUserMessage(userMessage);
await foreach (var message in agent.InvokeAsync(history))
{
    history.Add(message);
}
```

**After:**
```csharp
var thread = new ChatHistoryAgentThread();
var response = await agent.InvokeAsync(
    messages: userMessage,
    thread: thread
);
```

✅ **Benefit**: Thread manages state automatically

## Migration Steps

### Step 1: Update Package References

```xml
<!-- Remove -->
<PackageReference Include="Microsoft.SemanticKernel" Version="..." />

<!-- Add -->
<PackageReference Include="Microsoft.Agents.AI" Version="..." />
<PackageReference Include="Microsoft.Agents.AI.OpenAI" Version="..." />
```

### Step 2: Update Namespaces

```csharp
// Remove
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Agents;

// Add
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.OpenAI;
```

### Step 3: Replace Kernel with Direct Service

```csharp
// Old pattern
var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(...);
var kernel = builder.Build();

// New pattern
var chatClient = AzureOpenAIChatClient.Create(...);
```

### Step 4: Update Agent Creation

```csharp
// Old pattern
var agent = new ChatCompletionAgent
{
    Kernel = kernel,
    Name = "...",
    Instructions = "..."
};

// New pattern
var agent = chatClient.AsAIAgent(
    chatClient,
    instructions: "...",
    name: "..."
);
```

### Step 5: Use Thread for State Management

```csharp
// Old pattern
var history = new ChatHistory();
history.AddUserMessage(msg);
await foreach (var m in agent.InvokeAsync(history)) { }

// New pattern
var thread = new ChatHistoryAgentThread();
var response = await agent.InvokeAsync(messages: msg, thread: thread);
```

## Testing

### Before Migration Test
```bash
dotnet run --project Before/Before.csproj
```

### After Migration Test
```bash
dotnet run --project After/After.csproj
```

### Expected Behavior

Both versions should:
- ✅ Respond to user messages
- ✅ Maintain conversation context
- ✅ Handle multiple turns
- ✅ Exit gracefully

## Benefits of Migration

1. **Less Code**: ~30% reduction in boilerplate
2. **Clearer Intent**: More explicit about what's happening
3. **Better Testing**: Easier to mock and test
4. **Type Safety**: Stronger typing reduces errors
5. **Performance**: Slightly better initialization time

## Common Issues

### Issue: "Cannot find ChatClientAgent"

**Solution**: Ensure you have the correct package:
```bash
dotnet add package Microsoft.Agents.AI --prerelease
```

### Issue: "Thread doesn't maintain context"

**Solution**: Reuse the same thread instance:
```csharp
var thread = new ChatHistoryAgentThread(); // Create once
// Reuse in loop
await agent.InvokeAsync(messages: msg, thread: thread);
```

## Next Steps

Once you're comfortable with basic agent migration:

1. [Agent with Plugins](../agent-with-plugins/)
2. [Multi-Agent Orchestration](../multi-agent/)
3. [OpenAI Assistant Agent](../openai-assistant/)

---

**Last Updated**: October 16, 2025

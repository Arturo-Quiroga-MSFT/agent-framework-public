# Profisee Aisey: Semantic Kernel → Agent Framework Migration Guide (Revised)

**Prepared for:** Profisee (Jayla Ellis)  
**Prepared by:** Arturo Quiroga, Sr. Partner Solutions Architect  
**Date:** December 19, 2025  
**Migration Scope:** Aisey product – SK to Agent Framework (MAF) migration (C#/.NET)

---

## Executive Summary

This revised guide updates the Profisee-specific SK→Agent Framework recommendations to match the current upstream Agent Framework patterns (as mirrored in `maf-upstream/`).

### What changed vs the 2025-12-17 version

- **Agent invocation API:** prefer `RunAsync(...)` / `RunStreamingAsync(...)`.
- **`IChatClient` API:** prefer `.AsIChatClient()` + `GetResponseAsync(...)`.
- **Multimodal:** prefer `UriContent` / `DataContent` (not `ImageContent`).
- **Plugin filters:** SK `IAutoFunctionInvocationFilter` maps to **Agent Framework middleware** (`agent.AsBuilder().Use(...)`).
- **Package versions:** update guidance to reflect upstream snapshot versions and/or stable alternatives.

---

## 1) Migration Mapping Overview (Profisee Aisey)

| Semantic Kernel component | Agent Framework equivalent | Notes |
|---|---|---|
| `IChatCompletionService` | `IChatClient` (`Microsoft.Extensions.AI`) | Use for “just send messages, get response” scenarios.
| Kernel + agent abstractions (`Kernel`, SK Agents) | `AIAgent` (`Microsoft.Agents.AI`) | Use for tool calling, agent persona/instructions, orchestration patterns.
| SK plugins (`IKernelBuilderPlugins`, `[KernelFunction]`) | `AIFunctionFactory.Create(...)` tools | Direct method-to-tool registration.
| SK auto tool invocation filters (`IAutoFunctionInvocationFilter`) | Agent function middleware (`agent.AsBuilder().Use(...)`) | Most direct equivalent.
| SK OpenAI connectors | Provider SDKs (e.g., `Azure.AI.OpenAI`, `OpenAI`) + `.AsIChatClient()` | Use provider SDK clients directly.
| SK image content (`ImageContent`) | `UriContent` / `DataContent` | Matches current upstream dotnet samples.

---

## 2) Packages and Versions

### Recommended (align with upstream snapshot)

If Profisee wants maximum parity with the refreshed upstream patterns:

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Agents.AI" Version="1.0.0-preview.251219.1" />
  <PackageReference Include="Microsoft.Extensions.AI" Version="10.1.1" />
  <PackageReference Include="Azure.AI.OpenAI" Version="2.8.0-beta.1" />
  <PackageReference Include="Azure.Identity" Version="1.17.1" />
</ItemGroup>
```

Optional:
- If calling OpenAI directly (non-Azure):

```xml
<PackageReference Include="OpenAI" Version="2.8.0" />
```

### Migration/compatibility staging (optional)

If Profisee is doing an incremental cutover and wants to keep SK in place temporarily:

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.SemanticKernel" Version="1.x" />
</ItemGroup>
```

Guidance:
- Prefer stable packages when possible, but **tool calling** and **multimodal** are the areas most sensitive to version drift—if Profisee hits differences, align versions with upstream snapshot for the migration window.

---

## 3) Core Chat Migration: `IChatCompletionService` → `IChatClient`

### When to choose `IChatClient`

Use `IChatClient` when Aisey wants:
- simple “prompt in / text out” chat completions
- tight control over orchestration (Aisey decides when to call business logic)
- simpler mocking/unit testing

### Example: Azure OpenAI → `IChatClient`

```csharp
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Extensions.AI;

var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT is not set.");
var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME")
    ?? "gpt-4o-mini";

IChatClient chatClient = new AzureOpenAIClient(
        new Uri(endpoint),
        new AzureCliCredential())
    .GetChatClient(deploymentName)
    .AsIChatClient();

var response = await chatClient.GetResponseAsync(
    "You are Aisey. Say hello in one sentence.");

Console.WriteLine(response.Text);
```

### Notes

- In current upstream samples, the `IChatClient` call shape is `GetResponseAsync(...)`.
- For configuration such as temperature and token limits, use `ChatOptions`.

---

## 4) Agent Migration: SK “agent + plugins + auto tool calls” → `AIAgent`

### When to choose `AIAgent`

Use `AIAgent` when Aisey wants:
- tool calling (function tools) with “model chooses when” behavior
- a first-class “instructions/persona + tools” object
- streaming via agent-run APIs
- agent middleware hooks (tool gating, policy, approvals)

### Example: Create an `AIAgent` with Azure OpenAI

```csharp
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Agents.AI;

var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("AZURE_OPENAI_ENDPOINT is not set.");
var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME")
    ?? "gpt-4o-mini";

AIAgent agent = new AzureOpenAIClient(
        new Uri(endpoint),
        new AzureCliCredential())
    .GetChatClient(deploymentName)
    .CreateAIAgent(
        name: "AiseyAgent",
        instructions: "You are Aisey, Profisee's AI assistant for master data management."
    );

Console.WriteLine(await agent.RunAsync("Say hello."));

await foreach (var update in agent.RunStreamingAsync("Stream a short greeting."))
{
    Console.WriteLine(update);
}
```

**Important update:** prefer `RunAsync` / `RunStreamingAsync` for agent execution.

---

## 5) Plugins/Tools: `[KernelFunction]` / plugins → `AIFunctionFactory.Create(...)`

### Basic conversion pattern

SK plugin classes typically become one of:
- static methods
- instance methods on a service that you register in DI

Register tools when building the agent:

```csharp
using System.ComponentModel;
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

[Description("Retrieve customer master data by ID")]
static async Task<string> GetCustomerDataAsync(
    [Description("The customer ID")] string customerId)
{
    // Replace with Profisee's real data access
    return await Task.FromResult($"Customer {customerId}: <sample>");
}

var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!;
var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ?? "gpt-4o-mini";

AIAgent agent = new AzureOpenAIClient(new Uri(endpoint), new AzureCliCredential())
    .GetChatClient(deploymentName)
    .CreateAIAgent(
        name: "AiseyAgent",
        instructions: "You are Aisey, Profisee's AI assistant.",
        tools: [AIFunctionFactory.Create(GetCustomerDataAsync, name: "get_customer_data")]
    );

Console.WriteLine(await agent.RunAsync("Get customer data for 123."));
```

### Tool naming and descriptions

- Use explicit `name:` values that are stable and aligned to Profisee’s existing tool naming.
- Use `[Description]` attributes (or XML docs) so the model gets good tool metadata.

---

## 6) Equivalent to SK plugin filters (`IAutoFunctionInvocationFilter`)

### SK behavior to preserve

Common Profisee/SK filter use cases:
- require user approval before “dangerous” tools
- validate tool arguments
- log/audit tool calls
- blocklist/allowlist tools
- override results on policy failure

### Agent Framework equivalent: function invocation middleware

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

async ValueTask<object?> ToolPolicyMiddleware(
    AIAgent agent,
    FunctionInvocationContext context,
    Func<FunctionInvocationContext, CancellationToken, ValueTask<object?>> next,
    CancellationToken cancellationToken)
{
    // Example: block a tool by name
    if (string.Equals(context.Function.Name, "delete_master_record", StringComparison.OrdinalIgnoreCase))
    {
        throw new InvalidOperationException("Tool call blocked by policy.");
    }

    // Example: log tool invocation
    Console.WriteLine($"Invoking tool: {context.Function.Name}");

    return await next(context, cancellationToken);
}

var policyEnabledAgent = baseAgent
    .AsBuilder()
    .Use(ToolPolicyMiddleware)
    .Build();
```

### Related: chat client middleware

If you need to intercept *model calls* (PII redaction, telemetry, caching), use `IChatClient` middleware in the chat-client pipeline.

---

## 7) Multimodal / Image Handling (Updated)

Current upstream dotnet samples use `UriContent` (remote content) and `DataContent` (bytes).

### Remote image URL

```csharp
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Extensions.AI;
using OpenAI.Chat;
using ChatMessage = Microsoft.Extensions.AI.ChatMessage;

var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!;
var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ?? "gpt-4o";

var agent = new AzureOpenAIClient(new Uri(endpoint), new AzureCliCredential())
    .GetChatClient(deploymentName)
    .CreateAIAgent(name: "VisionAgent", instructions: "Analyze images.");

ChatMessage message = new(ChatRole.User, [
    new TextContent("What do you see in this image?"),
    new UriContent("https://example.com/image.jpg", "image/jpeg")
]);

var thread = agent.GetNewThread();

await foreach (var update in agent.RunStreamingAsync(message, thread))
{
    Console.WriteLine(update);
}
```

### Local bytes

```csharp
using Microsoft.Extensions.AI;
using OpenAI.Chat;
using ChatMessage = Microsoft.Extensions.AI.ChatMessage;

byte[] bytes = File.ReadAllBytes("assets/walkway.jpg");

ChatMessage message = new(ChatRole.User, [
    new TextContent("Describe this image."),
    new DataContent(bytes, "image/jpeg")
]);
```

---

## 8) Dependency Injection pattern (Updated)

The upstream sample pattern is:
- register `IChatClient` (often keyed) via `.AsIChatClient()`
- create `ChatClientAgent` (or `AIAgent`) from that

```csharp
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!;
var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ?? "gpt-4o-mini";

var builder = Host.CreateApplicationBuilder(args);

builder.Services.AddKeyedChatClient("AzureOpenAI", sp =>
    new AzureOpenAIClient(new Uri(endpoint), new AzureCliCredential())
        .GetChatClient(deploymentName)
        .AsIChatClient());

builder.Services.AddSingleton(new ChatClientAgentOptions
{
    Name = "AiseyAgent",
    ChatOptions = new() { Instructions = "You are Aisey, Profisee's AI assistant." }
});

builder.Services.AddSingleton<AIAgent>(sp => new ChatClientAgent(
    chatClient: sp.GetRequiredKeyedService<IChatClient>("AzureOpenAI"),
    options: sp.GetRequiredService<ChatClientAgentOptions>()));

using var host = builder.Build();
await host.RunAsync();
```

---

## 9) Recommended migration path for Profisee Aisey

### Phase A — “compile and run” cutover

- Replace `IChatCompletionService` usage with `IChatClient` for the simplest chat paths.
- Keep Aisey’s internal orchestration unchanged.

### Phase B — tool calling + governance

- Move SK plugin functions to `AIFunctionFactory.Create(...)` tools.
- Introduce **tool middleware** for:
  - approvals/consent gates
  - tool allow/deny policy
  - audit logging

### Phase C — clean-up

- Remove remaining SK packages and kernel usage.
- Standardize on:
  - `RunAsync` / `RunStreamingAsync` for agent execution
  - `.AsIChatClient()` + `GetResponseAsync` for chat client execution
  - `UriContent` / `DataContent` for multimodal

---

## 10) Quick checklist (engineer-facing)

- [ ] Replace agent calls to `InvokeAsync` → `RunAsync`
- [ ] Replace agent calls to `InvokeStreamingAsync` → `RunStreamingAsync`
- [ ] Replace `AsChatClient(...)`/`CompleteAsync(...)` examples → `.AsIChatClient()`/`GetResponseAsync(...)`
- [ ] Replace `ImageContent` examples → `UriContent`/`DataContent`
- [ ] Add agent tool middleware for approvals/policy (SK filter equivalent)
- [ ] Align package versions to either upstream snapshot or a tested stable set

---

## References (upstream parity points)

For patterns matching this guide, see:
- `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step01_Running/Program.cs`
- `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step03_UsingFunctionTools/Program.cs`
- `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step11_UsingImages/Program.cs`
- `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step14_Middleware/Program.cs`
- `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step09_DependencyInjection/Program.cs`

# Profisee Aisey: SK → Agent Framework Guidance Addendum (2025-12-19)

**Prepared for:** Profisee (Jayla Ellis)  
**Prepared by:** Arturo Quiroga, Sr. Partner Solutions Architect  
**Date:** December 19, 2025  
**Applies to:** Existing docs in this repo under `AQ-PROFISEE/` (leave originals unchanged)

---

## Why this addendum exists

We refreshed the upstream Agent Framework code snapshot under `maf-upstream/`. Since Agent Framework and `Microsoft.Extensions.AI` are moving quickly, a few API shapes and recommended patterns in the original Profisee SK→MAF docs should be updated for accuracy.

This document is a *delta* (what to change / what to prefer) rather than a full reprint of the original guides.

---

## 1) Key API naming updates (C#)

### AIAgent invocation
In current upstream samples, agent execution uses:
- `RunAsync(...)` (non-streaming)
- `RunStreamingAsync(...)` (streaming)

So when migrating SK usage of `InvokeAsync` / `InvokeStreamingAsync`, prefer:

```csharp
// Non-streaming
var text = await agent.RunAsync("Tell me a joke.");

// Streaming
await foreach (var update in agent.RunStreamingAsync("Tell me a joke."))
{
    Console.WriteLine(update);
}
```

**Why this matters:** some earlier snippets used `InvokeAsync` / `InvokeStreamingAsync` on `AIAgent`; those names don’t match current upstream Agent Framework samples.

---

## 2) IChatClient: prefer `.AsIChatClient()` + `GetResponseAsync(...)`

Some earlier snippets used `AsChatClient(...)` and/or `CompleteAsync(...)`. In current upstream (`maf-upstream/dotnet/samples/...`) the recommended pattern is:

```csharp
using Azure.AI.OpenAI;
using Azure.Identity;
using Microsoft.Extensions.AI;

IChatClient chatClient = new AzureOpenAIClient(
        new Uri(endpoint),
        new AzureCliCredential())
    .GetChatClient(deploymentName)
    .AsIChatClient();

var response = await chatClient.GetResponseAsync("Hello!");
Console.WriteLine(response.Text);
```

Notes:
- The `.AsIChatClient()` adapter is the key bridge from provider chat clients into the `Microsoft.Extensions.AI` abstraction.
- `GetResponseAsync(...)` is the common call shape in upstream samples.

---

## 3) Images / multimodal content: `UriContent` and `DataContent`

Some earlier snippets used `ImageContent`. Current upstream dotnet samples use `UriContent` (for remote images) and `DataContent` (for bytes).

### Remote image URL
```csharp
using Microsoft.Extensions.AI;
using OpenAI.Chat;
using ChatMessage = Microsoft.Extensions.AI.ChatMessage;

ChatMessage message = new(ChatRole.User, [
    new TextContent("What do you see in this image?"),
    new UriContent("https://.../image.jpg", "image/jpeg")
]);

await foreach (var update in agent.RunStreamingAsync(message, thread))
{
    Console.WriteLine(update);
}
```

### Local bytes / base64 equivalent
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

## 4) Tool calling + “plugin filters” equivalent

### SK: `IAutoFunctionInvocationFilter`
SK’s `IAutoFunctionInvocationFilter` is commonly used for:
- approval gates / consent
- logging/auditing
- policy-based allow/deny
- argument/result mutation
- retries and short-circuiting

### Agent Framework equivalent
In Agent Framework, the closest equivalent is **agent function invocation middleware**:

```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

async ValueTask<object?> ToolGate(
    AIAgent agent,
    FunctionInvocationContext context,
    Func<FunctionInvocationContext, CancellationToken, ValueTask<object?>> next,
    CancellationToken ct)
{
    // inspect/allow/deny based on context.Function.Name, arguments, etc.
    return await next(context, ct);
}

var gatedAgent = baseAgent.AsBuilder()
    .Use(ToolGate)
    .Build();
```

Two related hooks matter:
- **Agent function middleware** (intercepts tool calls)
- **IChatClient middleware** (intercepts the model call: prompt/response processing, telemetry, caching, PII redaction, etc.)

Practical recommendation for Aisey:
- Put *security/approval gates* at the **tool middleware** layer.
- Put *PII redaction / logging / telemetry* either at **agent-run middleware** or **chat-client middleware** depending on whether you want it applied only to agent runs or to *all* chat client calls.

---

## 5) Package version guidance (as-of upstream snapshot 2025-12-19)

The original Profisee-specific guide pinned some versions that are now behind current upstream.

If Profisee wants to align with the refreshed upstream snapshot, the dotnet repo currently builds with:
- `Microsoft.Agents.AI` **1.0.0-preview.251219.1** (repo package version)
- `Microsoft.Extensions.AI` **10.1.1**
- `Azure.AI.OpenAI` **2.8.0-beta.1**
- `OpenAI` **2.8.0**

Recommendation:
- If you’re doing an incremental migration and want fewer moving parts, prefer *stable* packages where possible.
- If you want maximum parity with upstream patterns/samples, use the versions above (or newer) and test integration behavior (tool calling + multimodal are the areas most sensitive to version drift).

---

## 6) Minor correctness notes (worth addressing in future rev)

If you create a future “vNext” of the Profisee-specific doc set, these are the most important cleanup items:
- Ensure all agent calls use `RunAsync` / `RunStreamingAsync`.
- Use `.AsIChatClient()` + `GetResponseAsync` for `IChatClient`-based examples.
- Update multimodal examples to `UriContent` / `DataContent`.
- Avoid suggesting `KernelFunction.AsAIAgent()`; bridging is typically either:
  - convert SK *agents* to `AIAgent` (SK compatibility story), or
  - re-express tools using `AIFunctionFactory.Create(...)` in Agent Framework.

---

## Pointers to upstream examples (for engineers)

- Middleware patterns: `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step14_Middleware/Program.cs`
- Agent run basics: `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step01_Running/Program.cs`
- Function tools: `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step03_UsingFunctionTools/Program.cs`
- Images: `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step11_UsingImages/Program.cs`
- DI pattern: `maf-upstream/dotnet/samples/GettingStarted/Agents/Agent_Step09_DependencyInjection/Program.cs`

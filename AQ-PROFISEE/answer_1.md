

Yes — the Agent Framework equivalent is **middleware**, specifically **function-calling middleware** on `AIAgent`.

In SK, `IAutoFunctionInvocationFilter` runs “around” automatic tool/function execution (inspect/deny/modify/retry). In Agent Framework, you do the same thing by intercepting tool calls via the agent pipeline:

- **Equivalent hook:** `AIAgent.AsBuilder().Use(...)` with a callback that receives a `FunctionInvocationContext`
- **What you can do there:** log/audit tool calls, require approval/consent, block specific tools, redact args, wrap retries, override results, etc.

Minimal shape (conceptually the same as an SK filter):

```csharp
async ValueTask<object?> ToolGate(
    AIAgent agent,
    FunctionInvocationContext ctx,
    Func<FunctionInvocationContext, CancellationToken, ValueTask<object?>> next,
    CancellationToken ct)
{
    // inspect ctx.Function.Name, ctx.Arguments, etc.
    // optionally short-circuit (block) instead of calling next(...)
    return await next(ctx, ct);
}

var gatedAgent = baseAgent.AsBuilder()
    .Use(ToolGate)
    .Build();
```

Important nuance:
- That middleware is **only relevant when you’re using automatic function/tool invocation**, which (per docs) requires the agent pipeline to include a `FunctionInvokingChatClient` (some agent types include it; otherwise you add it).
- If you’re using **plain `IChatClient`** and doing tool routing yourself (no auto tool calling), then the “filter equivalent” is just *your own orchestration layer* (because there’s nothing automatic to intercept).

Related (also useful):
- There’s also **`IChatClient` middleware** in `Microsoft.Extensions.AI` for intercepting the *model call itself* (prompt redaction, telemetry, caching), which is closer to SK’s “prompt render / LLM call” interception than to tool invocation.

If you tell me whether Profisee wants **(a)** approval/consent gating, **(b)** logging/telemetry, or **(c)** policy-based allow/deny per tool, I can recommend the cleanest middleware pattern and where to enforce it.
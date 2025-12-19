For Step #3 (`IChatCompletionService` → either `IChatClient` or `AIAgent`), think of it like this:

- `IChatClient` = “raw chat completions API” (lowest-level abstraction in this migration)
- `AIAgent` = “chat client + instructions + tool-calling + (often) nicer ergonomics”

Here are the tradeoffs that usually matter in real migrations.

**When `IChatClient` is the better first move**
- **Pros**
  - **Closest mental model to SK chat completion**: you’re basically just sending `List<ChatMessage>` and getting a completion back.
  - **Simpler for existing pipelines**: if Aisey already has its own orchestration (routing, function dispatch, validation, retries), `IChatClient` won’t fight it.
  - **Easier to unit test deterministically**: you can mock `IChatClient.CompleteAsync(...)` and keep everything else as your own code.
  - **Lower “framework gravity”**: fewer concepts to adopt all at once; good for incremental migration.
  - **Great for non-tool workloads**: summarization, classification, rewriting, extraction, etc., where you don’t need tool calls.
- **Cons**
  - **You build more yourself**: tool-calling loops, function registry, retries/backoff policies, conversation state conventions, etc.
  - **More boilerplate creeps back in**: especially if you start adding tool invocation, streaming UX, “system prompt” management, and guardrails.

**When `AIAgent` is the better first move**
- **Pros**
  - **Fastest path to “SK-like agent behavior”**: if you used SK plugins / auto tool invocation, this maps more naturally.
  - **Tool/function calling is first-class**: `AIFunctionFactory.Create(...)` + `InvokeAsync(...)` gives you a coherent story for “assistant decides when to call tools.”
  - **Cleaner separation of concerns**: “agent persona + tools + runtime” is explicit, versus scattered across services.
  - **Streaming ergonomics**: `InvokeStreamingAsync` is a very direct mapping to SK streaming patterns.
- **Cons**
  - **More opinionated**: you’re adopting an “agent runtime” abstraction, which can be overkill if Aisey’s orchestration is already mature/custom.
  - **Testing can shift**: you’ll likely still mock, but now you’re testing “agent behavior” (prompt+tools) which can be less deterministic than “completion call”.
  - **Harder if you need strict control** over when tools run, exact tool routing, or want a fully deterministic function dispatch policy (you can do it, but you may be fighting the default “let the model choose” posture).

**Practical recommendation for Profisee/Aisey (migration-friendly)**
- If Aisey today is **mostly chat + your own code decides when to call business logic** → start with `IChatClient` first (lowest risk), then introduce `AIAgent` later when you’re ready to standardize tool-calling.
- If Aisey today relies heavily on **SK plugins + `ToolCallBehavior.AutoInvokeKernelFunctions`** (model-driven tool selection) → go straight to `AIAgent` to preserve behavior and reduce “rebuild the orchestration” work.

**Decision shortcuts**
- Choose `IChatClient` if: “we want control + predictability + minimal framework change.”
- Choose `AIAgent` if: “we want agent persona + tool calling + streaming with minimal glue code.”

If you tell me whether Aisey currently uses **auto-invoked SK functions** (and roughly how many plugins/tools), I can give a very specific “start here, then evolve to…” recommendation.
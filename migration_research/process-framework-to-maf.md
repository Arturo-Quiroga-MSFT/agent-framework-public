# Mapping: Semantic Kernel Process Framework → Microsoft Agent Framework (MAF)

This document maps core concepts from the Semantic Kernel Process Framework (SK Process Framework) to Microsoft Agent Framework (MAF) constructs, followed by a migration checklist focused on partners using the Process Framework heavily.

## Concept mapping (quick)
- ProcessBuilder (SK) -> WorkflowBuilder (MAF)
- KernelProcess / KernelProcessStep -> WorkflowExecutor / Executor (MAF)
- KernelFunction -> ai_function / tool / handler (MAF)
- Events (emit/send_event) -> Workflow edges / send_event_to / WorkflowOutputEvent
- Stateful step checkpoint -> Executor state persisted via AgentThread/workflow checkpointing
- start / StartAsync -> workflow.run / workflow.run_stream or WorkflowExecutor.run
- Nested processes -> nested WorkflowExecutor or sub-workflows
- Human-in-the-loop (ProxyStep) -> external event hooks + long-running workflow with checkpointing

## Migration checklist (high level)
1. Inventory processes and classify complexity.
2. Map each step to an Executor and KernelFunctions to tools/handlers.
3. Convert step-local state to explicit models and wire persistence.
4. Reimplement event routing as explicit workflow edges.
5. Add telemetry (OpenTelemetry spans) to each Executor for tracing.
6. Implement tests: unit (executor logic), integration (workflow end-to-end), regression (match SK outputs).
7. Canary rollout and traffic split; keep SK available for rollback.

## Notes and references
- **Complete side-by-side examples available**: See `/maf-upstream/python/samples/semantic-kernel-migration/processes/`
  - [fan_out_fan_in_process.py](../maf-upstream/python/samples/semantic-kernel-migration/processes/fan_out_fan_in_process.py) - Fan-out/fan-in pattern
  - [nested_process.py](../maf-upstream/python/samples/semantic-kernel-migration/processes/nested_process.py) - Nested process workflows
- **Comprehensive MAF samples**: See `/maf-upstream/python/samples/getting_started/workflows/`
  - Sequential workflows
  - Concurrent orchestration
  - Graph-based workflows with checkpointing
  - Human-in-the-loop patterns
- Example translation (before/after): fan-out/fan-in

### Before (Semantic Kernel Process Framework - excerpt)

```py
class AStep(KernelProcessStep[None]):
	@kernel_function()
	async def do_it(self, context: KernelProcessStepContext):
		await asyncio.sleep(1)
		await context.emit_event(process_event=CommonEvents.A_STEP_DONE.value, data="I did A")

process = ProcessBuilder(name="Process Framework Sample")
kickoff_step = process.add_step(step_type=KickOffStep)
step_a = process.add_step(step_type=AStep)
...  # wiring via process.on_input_event(...).send_event_to(...)
```

### After (MAF - excerpt)

```py
class DelayedStepExecutor(Executor):
	@handler
	async def handle(self, cycle: int, ctx: WorkflowContext[StepResult]) -> None:
		await asyncio.sleep(self._delay)
		await ctx.send_message(StepResult(origin=self._name, cycle=cycle, data=f"I did {self._name}"))

workflow = (
	WorkflowBuilder()
	.add_edge(kickoff, step_a)
	.add_edge(kickoff, step_b)
	.add_fan_in_edges([step_a, step_b], aggregate)
	.add_edge(aggregate, kickoff)
	.set_start_executor(kickoff)
	.build()
)

async for event in workflow.run_stream(CommonEvents.START_PROCESS):
	if isinstance(event, WorkflowOutputEvent):
		final_text = event.data
```

Notes:
- KernelFunctions become Executor handlers or small ai_function-style tools.
- Event routing becomes explicit edges and fan-in/fan-out builder calls.
- Complete working example available at: `/maf-upstream/python/samples/semantic-kernel-migration/processes/fan_out_fan_in_process.py`

## Additional Resources

### Official Migration Documentation
- [Agent Framework Workflows Overview](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/overview)
- [Migration from Semantic Kernel](https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel)
- [Semantic Kernel Process Framework docs](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/)

### Code Samples
- **SK to MAF Migration Samples**: `/maf-upstream/python/samples/semantic-kernel-migration/`
  - Chat completion agents
  - Azure AI agents
  - OpenAI assistants & responses
  - Orchestrations (sequential, concurrent, group chat, handoff, magentic)
  - **Processes** (fan-out/fan-in, nested)
  
- **MAF Workflow Samples**: `/maf-upstream/python/samples/getting_started/workflows/`
  - Basic workflows
  - Agent integration
  - Orchestration patterns
  - Custom executors

### Framework Documentation
- Python README: `/maf-upstream/python/README.md`
- .NET README: `/maf-upstream/dotnet/README.md`
- Agent Framework Repository: https://github.com/microsoft/agent-framework

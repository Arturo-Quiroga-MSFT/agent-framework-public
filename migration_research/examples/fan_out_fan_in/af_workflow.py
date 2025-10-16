"""Agent Framework (AF) only workflow wrapper for fan-out/fan-in sample.

This module contains the AF Executors and a programmatic runner that mirrors the
AF section of the upstream `fan_out_fan_in_process.py` sample, but without importing
Semantic Kernel artifacts. It's safe to import when `agent_framework` is available.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import cast

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, WorkflowOutputEvent, handler


class CommonEvents:
    START_PROCESS = "StartProcess"
    C_STEP_DONE = "CStepDone"


@dataclass
class StepResult:
    origin: str
    cycle: int
    data: str


class KickOffExecutor(Executor):
    def __init__(self, *, id: str = "kickoff") -> None:
        super().__init__(id=id)
        self._next_cycle = 0

    @handler
    async def handle(self, event: str, ctx: WorkflowContext[int]) -> None:
        if event not in {CommonEvents.START_PROCESS, CommonEvents.C_STEP_DONE}:
            return
        self._next_cycle += 1
        await ctx.send_message(self._next_cycle)


class DelayedStepExecutor(Executor):
    def __init__(self, *, name: str, delay_seconds: float) -> None:
        super().__init__(id=name)
        self._delay = delay_seconds
        self._name = name

    @handler
    async def handle(self, cycle: int, ctx: WorkflowContext[StepResult]) -> None:
        await asyncio.sleep(self._delay)
        await ctx.send_message(StepResult(origin=self._name, cycle=cycle, data=f"I did {self._name}"))


class FanInExecutor(Executor):
    def __init__(self, *, required_cycles: int = 3, id: str = "fanin") -> None:
        super().__init__(id=id)
        self._completed_cycles = 0
        self._required_cycles = required_cycles

    @handler
    async def handle(self, results: list[StepResult], ctx: WorkflowContext[str]) -> None:
        if not results:
            return
        cycle_number = results[0].cycle
        summary = ", ".join(f"{r.origin}: {r.data}" for r in results)
        # In AF sample this prints; we keep silent here for tests
        self._completed_cycles += 1
        if self._completed_cycles >= self._required_cycles:
            await ctx.yield_output(f"Completed {self._completed_cycles} cycles")
            return

        await ctx.send_message(CommonEvents.C_STEP_DONE)


async def run_agent_framework_workflow_example() -> str | None:
    kickoff = KickOffExecutor()
    step_a = DelayedStepExecutor(name="step_a", delay_seconds=0.01)
    step_b = DelayedStepExecutor(name="step_b", delay_seconds=0.01)
    aggregate = FanInExecutor(required_cycles=3)

    workflow = (
        WorkflowBuilder()
        .add_edge(kickoff, step_a)
        .add_edge(kickoff, step_b)
        .add_fan_in_edges([step_a, step_b], aggregate)
        .add_edge(aggregate, kickoff)
        .set_start_executor(kickoff)
        .build()
    )

    final_text: str | None = None
    async for event in workflow.run_stream(CommonEvents.START_PROCESS):
        if isinstance(event, WorkflowOutputEvent):
            final_text = cast(str, event.data)

    return final_text

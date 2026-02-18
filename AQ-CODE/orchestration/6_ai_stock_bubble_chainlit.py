"""
AI Stock Bubble Research — Chainlit UI

5 concurrent financial research agents with real-time Bing web search.
Run with:
    chainlit run 6_ai_stock_bubble_chainlit.py --port 8096
"""

import asyncio
import os
from pathlib import Path

import chainlit as cl
from dotenv import load_dotenv

from agent_framework import (
    AgentExecutorRequest,
    AgentExecutorResponse,
    Executor,
    Message,
    WorkflowContext,
    handler,
)
from agent_framework._workflows import WorkflowBuilder
from agent_framework.azure import AzureAIAgentClient
from azure.identity import DefaultAzureCredential

load_dotenv(Path(__file__).parent / ".env")

# ── agent / workflow setup (done once at module level) ────────────────────────

_workflow = None


async def _build_workflow():
    credential = DefaultAzureCredential()
    agent_client = AzureAIAgentClient(
        credential=credential,
        project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        model_deployment_name=os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1"),
    )

    bing_tool = {
        "type": "bing_grounding",
        "bing_grounding": {
            "search_configurations": [
                {"connection_id": os.environ.get("BING_CONNECTION_ID", "")}
            ]
        },
    }
    opts = {"max_tokens": 600}

    agents_cfg = [
        (
            "market_analyst",
            "📈 Market Analyst",
            "You're a senior market analyst. Use web search to find current P/E ratios, market caps, "
            "and valuation metrics for major AI companies (NVIDIA, Microsoft, Google, Meta, Amazon). "
            "Identify overvaluation warning signs. Be analytical, cite sources, stay concise.",
        ),
        (
            "technical_analyst",
            "📉 Technical Analyst",
            "You're a technical analyst. Use web search to find price movements, RSI, analyst sentiment, "
            "and retail investor behaviour around AI stocks. Look for bubble indicators: parabolic moves, "
            "extreme RSI, retail euphoria, insider selling. Stay concise.",
        ),
        (
            "fundamental_analyst",
            "💼 Fundamental Analyst",
            "You're a fundamental analyst. Use web search for quarterly earnings, revenue growth, "
            "profit margins, and cash flow of major AI companies. Are revenues justifying valuations? "
            "Flag red flags: unprofitable growth, revenue-valuation gaps. Stay concise.",
        ),
        (
            "economic_historian",
            "📚 Economic Historian",
            "You're an economic historian. Use web search to compare current AI stocks to historical bubbles "
            "(dot-com 2000, housing 2008, crypto 2021). Draw parallels with specific data points. Stay concise.",
        ),
        (
            "risk_analyst",
            "⚠️ Risk Analyst",
            "You're a risk specialist. Use web search to analyse AI stock concentration in S&P 500/NASDAQ, "
            "leverage in the system, and cascade effects if AI stocks correct. Quantify exposure risks. Stay concise.",
        ),
    ]

    agent_objs = []
    for name, _, instructions in agents_cfg:
        agent_objs.append(
            agent_client.as_agent(
                instructions=instructions,
                name=name,
                tools=bing_tool,
                default_options=opts,
            )
        )

    _agent_display = {name: display for name, display, _ in agents_cfg}

    class Dispatcher(Executor):
        @handler
        async def dispatch(self, query: str, ctx: WorkflowContext) -> None:
            req = AgentExecutorRequest(
                messages=[Message("user", text=query)],
                should_respond=True,
            )
            await ctx.send_message(req)

    class Aggregator(Executor):
        @handler
        async def aggregate(
            self, results: list[AgentExecutorResponse], ctx: WorkflowContext
        ) -> None:
            lines = []
            for result in results:
                msgs = getattr(result.agent_response, "messages", [])
                for msg in reversed(msgs):
                    name = getattr(msg, "author_name", None)
                    if name and name != "user":
                        display = _agent_display.get(name, name.upper())
                        lines.append(f"### {display}\n\n{msg.text}")
                        break
            await ctx.yield_output("\n\n---\n\n".join(lines))

    dispatcher = Dispatcher(id="dispatcher")
    aggregator = Aggregator(id="aggregator")

    builder = WorkflowBuilder(start_executor=dispatcher)
    builder.add_fan_out_edges(dispatcher, agent_objs)
    builder.add_fan_in_edges(agent_objs, aggregator)
    return builder.build()


# ── Chainlit handlers ─────────────────────────────────────────────────────────

@cl.on_chat_start
async def on_start():
    global _workflow
    if _workflow is None:
        async with cl.Step(name="Initialising agents…", show_input=False) as step:
            _workflow = await _build_workflow()
            step.output = "✅ 5 financial research agents ready."

    await cl.Message(
        content=(
            "## 📊 AI Stock Bubble Research\n\n"
            "Ask me anything about AI stock valuations, bubble indicators, or market risks.\n\n"
            "**Examples:**\n"
            "- *Is there an AI stock bubble forming in 2026?*\n"
            "- *Compare NVIDIA's valuation to the dot-com bubble*\n"
            "- *What % of the S&P 500 is AI-related?*\n\n"
            "Five specialist agents will research your question in parallel using live Bing web search."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    query = message.content.strip()

    # Show a thinking message while agents work
    thinking = await cl.Message(content="🔍 Dispatching to 5 financial research agents…").send()

    step_labels = {
        "market_analyst":      "📈 Market Analyst",
        "technical_analyst":   "📉 Technical Analyst",
        "fundamental_analyst": "💼 Fundamental Analyst",
        "economic_historian":  "📚 Economic Historian",
        "risk_analyst":        "⚠️  Risk Analyst",
    }

    # Open one Chainlit Step per agent so the audience sees them working in parallel
    step_objs = {}
    for key, label in step_labels.items():
        s = cl.Step(name=f"{label} — searching…", show_input=False)
        await s.__aenter__()
        step_objs[key] = s

    result_text = ""
    try:
        stream = _workflow.run(query, stream=True)
        async for event in stream:
            if isinstance(event, dict):
                event_type = event.get("type")
                event_data = event.get("data")
                executor_id = event.get("executor_id")
            else:
                event_type = getattr(event, "type", None)
                event_data = getattr(event, "data", None)
                executor_id = getattr(event, "executor_id", None)  # plain attr, safe on all event types

            if event_type == "output" and event_data is not None:
                result_text = str(event_data)

            # Surface individual agent completions into their step panels
            if event_type in ("executor_completed", "data") and executor_id in step_objs:
                text = getattr(event_data, "text", None) if event_data else None
                if not text and event_data:
                    text = str(event_data)[:600]
                if text:
                    step_objs[executor_id].output = text[:600]

    finally:
        for s in step_objs.values():
            if not s.output:
                s.output = "✅ Done"
            await s.__aexit__(None, None, None)

    if not result_text:
        result_text = "⚠️ No output received — check the console for errors."

    # Update the thinking placeholder with the final report
    thinking.content = result_text
    await thinking.update()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)

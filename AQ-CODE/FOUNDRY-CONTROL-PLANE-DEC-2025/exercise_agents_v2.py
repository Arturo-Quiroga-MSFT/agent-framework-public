#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Agent Exercise Script V2 - Exercises V2 agents in your fleet

Auto-discovers V2 agents from your Azure AI project and exercises them
with prompts to generate telemetry for the Fleet Health Dashboard:
- Success/failure rates
- Token usage and costs
- Latency metrics
- Run counts

Uses agent_framework (AzureAIClient + ChatAgent) which is the correct
pattern for V2 agents with name-based IDs.
Only exercises 'prompt' kind agents (skips hosted/workflow).

USAGE:
    python exercise_agents_v2.py                            # Exercise all prompt agents, 1 iteration
    python exercise_agents_v2.py --iterations 3             # Run 3 iterations
    python exercise_agents_v2.py --prompts 3                # 3 prompts per agent
    python exercise_agents_v2.py --agents 5                 # Exercise only first 5 agents
    python exercise_agents_v2.py --filter "Customer,Weather"  # Only matching agents
    python exercise_agents_v2.py --include-failures         # Include empty prompts
    python exercise_agents_v2.py --telemetry                # Enable App Insights telemetry
    python exercise_agents_v2.py --telemetry-console        # Console telemetry (for testing)
    python exercise_agents_v2.py --list                     # Just list exercisable agents

PREREQUISITES:
    - Azure CLI authenticated: az login
    - .env file configured with AZURE_AI_PROJECT_ENDPOINT
    - pip install agent-framework-core agent-framework-azure-ai azure-identity

UPDATED: February 2026
"""

import os
import sys
import argparse
import asyncio
import random
import time
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables - prefer .env next to this script
_env_path = Path(__file__).with_name(".env")
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv()

# ============================================================================
# TELEMETRY SETUP - Send metrics to Application Insights
# ============================================================================
TELEMETRY_ENABLED = False
tracer = None
trace = None
Status = None
StatusCode = None


def setup_telemetry(enable: bool, *, force_console: bool = False) -> None:
    """Configure OpenTelemetry for tracing agent exercises.

    - If APPLICATIONINSIGHTS_CONNECTION_STRING is set, sends to Azure Monitor.
    - Otherwise (or if force_console=True), uses console span exporter.
    """
    global TELEMETRY_ENABLED, tracer, trace, Status, StatusCode

    TELEMETRY_ENABLED = False
    tracer = None
    trace = None
    Status = None
    StatusCode = None

    if not enable:
        print("  Telemetry: disabled (use --telemetry to enable)")
        return

    try:
        from opentelemetry import trace as otel_trace
        from opentelemetry.trace import Status as OtelStatus, StatusCode as OtelStatusCode

        trace = otel_trace
        Status = OtelStatus
        StatusCode = OtelStatusCode

        app_insights_conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")

        # Try Azure Monitor
        if (not force_console) and app_insights_conn_str:
            try:
                from azure.monitor.opentelemetry import configure_azure_monitor

                configure_azure_monitor(
                    connection_string=app_insights_conn_str,
                    enable_live_metrics=False,
                    enable_performance_counters=False,
                )
                TELEMETRY_ENABLED = True
                tracer = trace.get_tracer(__name__)
                print("  Telemetry: ✅ Azure Monitor (spans appear in App Insights after ~2-5 min)")
                return

            except Exception as e:
                print(f"  Telemetry: ⚠️ Azure Monitor failed ({type(e).__name__}), falling back to console")

        # Console fallback
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        provider = TracerProvider()
        otel_trace.set_tracer_provider(provider)
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        TELEMETRY_ENABLED = True
        tracer = trace.get_tracer(__name__)

        if force_console:
            print("  Telemetry: ✅ Console exporter")
        else:
            print("  Telemetry: ⚠️ Console fallback (no App Insights connection string)")

    except ImportError:
        print("  Telemetry: ⚠️ opentelemetry not installed (pip install opentelemetry-sdk)")
    except Exception as e:
        print(f"  Telemetry: ⚠️ Failed ({type(e).__name__}: {e})")


def shutdown_telemetry() -> None:
    """Best-effort flush/shutdown to avoid process hang."""
    if not TELEMETRY_ENABLED or trace is None:
        return
    try:
        provider = trace.get_tracer_provider()
        if hasattr(provider, "force_flush"):
            provider.force_flush()
        if hasattr(provider, "shutdown"):
            provider.shutdown()
    except Exception:
        pass


# ============================================================================
# IMPORTS - agent_framework for V2 agent exercise
# ============================================================================
try:
    from azure.ai.projects import AIProjectClient as SyncProjectClient       # for discovery
    from azure.ai.projects.aio import AIProjectClient as AsyncProjectClient  # for exercise
    from azure.identity import DefaultAzureCredential as SyncCredential      # for discovery
    from azure.identity.aio import DefaultAzureCredential as AsyncCredential # for exercise
    from agent_framework import ChatAgent
    from agent_framework.azure import AzureAIClient
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Install with: uv pip install -e maf-upstream/python/packages/core -e maf-upstream/python/packages/azure-ai --prerelease=allow")
    sys.exit(1)


# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class AgentInfo:
    """Info about a discoverable agent."""
    name: str
    kind: str
    model: str
    version: str


@dataclass
class ExerciseResult:
    """Result from exercising an agent."""
    agent_name: str
    prompt: str
    success: bool
    response: Optional[str]
    error: Optional[str]
    latency_ms: float
    tokens_used: int


# ============================================================================
# PROMPTS - Categorized by agent specialty
# ============================================================================
GENERAL_PROMPTS = [
    "Hello! What can you help me with?",
    "Give me a brief summary of your capabilities in 2 sentences.",
    "What is 2 + 2?",
    "Tell me a short joke.",
    "What's the capital of France?",
    "Explain what an AI agent is in one sentence.",
    "List 3 colors of the rainbow.",
    "What year did World War II end?",
    "Name the largest planet in our solar system.",
    "Calculate the area of a circle with radius 5.",
]

# Specialty prompts matched by agent name patterns
SPECIALTY_PROMPTS: Dict[str, List[str]] = {
    "customer|support|contoso": [
        "How do I reset my password?",
        "I'm having trouble logging in.",
        "What are your business hours?",
        "I'd like to request a refund.",
    ],
    "writer|technical|doc": [
        "Write a brief README intro for a Python library.",
        "What are the key sections of good API documentation?",
        "Write a brief changelog entry for a bug fix.",
    ],
    "project|manager": [
        "Create a simple timeline for a 3-month software project.",
        "What should be in a project kickoff meeting?",
        "What's the difference between Agile and Waterfall?",
    ],
    "market|research": [
        "Suggest 3 content ideas for a B2B software blog.",
        "What are the key metrics for social media success?",
        "What's the difference between SEO and SEM?",
    ],
    "research|researcher": [
        "Summarize the key benefits of cloud computing.",
        "What are the main differences between REST and GraphQL?",
        "List 5 best practices for API design.",
    ],
    "travel": [
        "I need help planning a trip to Paris.",
        "What's the best time to visit Tokyo?",
        "Suggest a 3-day itinerary for New York City.",
    ],
    "weather": [
        "What's the weather like in Seattle?",
        "Will it rain tomorrow in San Francisco?",
        "What's the temperature in London right now?",
    ],
    "data|analysis|analyst": [
        "Analyze this dataset: [12, 15, 18, 22, 25, 28, 30] - calculate mean and standard deviation.",
        "What statistical test should I use to compare two groups?",
        "Explain the difference between correlation and causation.",
    ],
    "financial|finance": [
        "Calculate the ROI for $10,000 that returns $12,500 after one year.",
        "What is EBITDA and why is it important?",
        "Explain the difference between gross margin and net margin.",
    ],
    "hr|human|employee": [
        "What is the company's PTO policy?",
        "How do I enroll in benefits?",
        "What's the process for requesting time off?",
    ],
    "code|interpreter|coder": [
        "Write a Python function to calculate Fibonacci numbers.",
        "What's the time complexity of quicksort?",
        "Explain the difference between a stack and a queue.",
    ],
    "healthcare|health|medical": [
        "What are the common symptoms of a cold?",
        "When should someone visit a doctor for a headache?",
        "List 3 benefits of regular exercise.",
    ],
    "poet|creative": [
        "Write a haiku about the ocean.",
        "Tell me a very short story about a cat.",
        "What makes good poetry?",
    ],
    "translator|translate": [
        "How do you say 'hello' in Japanese?",
        "Translate 'good morning' into Spanish.",
        "What's the French word for 'computer'?",
    ],
    "chat|basic": [
        "What is the meaning of life?",
        "Tell me something interesting about space.",
        "What's a fun fact about the ocean?",
    ],
    "image|gen": [
        "Describe what a sunset over mountains looks like.",
        "What makes a good photograph composition?",
    ],
    "bing|grounded|websearch": [
        "What are the latest developments in AI?",
        "Tell me about a recent technology trend.",
    ],
}

# Prompts designed to potentially fail
FAILING_PROMPTS = [
    "",  # Empty prompt
]


def get_prompts_for_agent(agent_name: str) -> List[str]:
    """Get appropriate prompts for an agent based on its name."""
    name_lower = agent_name.lower()

    # Find matching specialty prompts
    matched = []
    for pattern, prompts in SPECIALTY_PROMPTS.items():
        keywords = pattern.split("|")
        if any(kw in name_lower for kw in keywords):
            matched.extend(prompts)

    # Include some general prompts too
    if matched:
        return matched + GENERAL_PROMPTS[:2]
    else:
        return GENERAL_PROMPTS


# ============================================================================
# AGENT DISCOVERY (uses sync client)
# ============================================================================
def discover_agents(endpoint: str) -> List[AgentInfo]:
    """Auto-discover V2 agents from the project.

    Returns all agents with their kind and model info.
    """
    credential = SyncCredential()
    client = SyncProjectClient(endpoint=endpoint, credential=credential)

    agents = []
    for agent in client.agents.list():
        name = getattr(agent, "name", None)
        if not name or name.upper() in ("", "NONE", "ONE"):
            continue

        versions = getattr(agent, "versions", {}) or {}
        latest = versions.get("latest", {})
        defn = latest.get("definition", {})
        kind = defn.get("kind", "unknown")
        model = defn.get("model") or "-"
        ver = str(latest.get("version", "?"))

        agents.append(AgentInfo(name=name, kind=kind, model=model, version=ver))

    return agents


def filter_exercisable(agents: List[AgentInfo]) -> List[AgentInfo]:
    """Filter to agents that can be exercised (prompt kind with a model)."""
    return [a for a in agents if a.kind == "prompt" and a.model not in ("unknown", None, "-")]


# ============================================================================
# EXERCISE ENGINE - Uses agent_framework (AzureAIClient + ChatAgent)
# ============================================================================
async def exercise_single_prompt(
    project_client: "AsyncProjectClient",
    agent_name: str,
    prompt: str,
) -> ExerciseResult:
    """Exercise a single prompt against a V2 agent.

    Uses agent_framework's AzureAIClient + ChatAgent which correctly
    handles V2 agents with name-based IDs and use_latest_version.
    """
    start_time = time.time()
    response_text = ""
    tokens_used = 0

    # Create telemetry span if enabled
    span = None
    if tracer:
        span = tracer.start_span(
            "agent.exercise",
            attributes={
                "gen_ai.system": "azure_ai_agents",
                "gen_ai.agent.name": agent_name,
                "gen_ai.prompt": (prompt or "(empty)")[:500],
            },
        )

    try:
        # Connect to existing V2 agent by name
        chat_client = AzureAIClient(
            project_client=project_client,
            agent_name=agent_name,
            use_latest_version=True,
        )

        agent = ChatAgent(chat_client=chat_client)

        # Run the agent
        result = await agent.run(prompt if prompt else "Hello")
        response_text = str(result) if result else "No response"

        # Estimate tokens (rough approximation)
        tokens_used = len((prompt or "").split()) + len(response_text.split()) * 2

        latency_ms = (time.time() - start_time) * 1000

        # Record success in telemetry
        if span:
            span.set_attribute("gen_ai.usage.total_tokens", tokens_used)
            span.set_attribute("gen_ai.response.finish_reason", "stop")
            span.set_attribute("duration_ms", latency_ms)
            span.set_attribute("success", True)
            span.set_status(Status(StatusCode.OK))

        return ExerciseResult(
            agent_name=agent_name,
            prompt=prompt[:100] + "..." if len(prompt) > 100 else (prompt or "(empty)"),
            success=True,
            response=response_text[:200] if response_text else "No response",
            error=None,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000

        # Record failure in telemetry
        if span:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e)[:200])
            span.set_attribute("duration_ms", latency_ms)
            span.set_attribute("success", False)
            span.set_status(Status(StatusCode.ERROR, str(e)[:100]))

        return ExerciseResult(
            agent_name=agent_name,
            prompt=prompt[:100] + "..." if len(prompt) > 100 else (prompt or "(empty)"),
            success=False,
            response=None,
            error=str(e)[:200],
            latency_ms=latency_ms,
            tokens_used=0,
        )
    finally:
        if span:
            span.end()


async def exercise_agents(
    endpoint: str,
    agents: List[AgentInfo],
    iterations: int = 1,
    prompts_per_agent: int = 2,
    include_failures: bool = False,
    delay_between_calls: float = 1.0,
) -> List[ExerciseResult]:
    """Exercise agents using agent_framework async client."""
    print(f"\n{'='*70}")
    print(f"🏋️  Exercising {len(agents)} agents for {iterations} iteration(s)")
    print(f"    {prompts_per_agent} prompts/agent, {delay_between_calls}s delay between calls")
    print(f"{'='*70}")

    results: List[ExerciseResult] = []
    total_calls = 0
    successful_calls = 0
    total_tokens = 0
    total_latency = 0.0

    async with (
        AsyncCredential() as credential,
        AsyncProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        for iteration in range(iterations):
            if iterations > 1:
                print(f"\n📍 Iteration {iteration + 1}/{iterations}")

            for agent_info in agents:
                # Get prompts for this agent
                available = get_prompts_for_agent(agent_info.name)
                if include_failures:
                    available = available + FAILING_PROMPTS

                selected = random.sample(available, min(prompts_per_agent, len(available)))

                print(f"\n🤖 {agent_info.name} ({agent_info.model}, v{agent_info.version})")
                print(f"   Running {len(selected)} prompts...")

                for prompt in selected:
                    result = await exercise_single_prompt(project_client, agent_info.name, prompt)
                    results.append(result)
                    total_calls += 1

                    if result.success:
                        successful_calls += 1
                        total_tokens += result.tokens_used
                        total_latency += result.latency_ms
                        status = "✅"
                    else:
                        status = "❌"

                    prompt_preview = prompt[:40] + "..." if len(prompt) > 40 else (prompt or "(empty)")
                    print(f"   {status} \"{prompt_preview}\" ({result.latency_ms:.0f}ms, ~{result.tokens_used} tok)")
                    if not result.success:
                        print(f"      Error: {result.error}")

                    # Rate limiting
                    await asyncio.sleep(delay_between_calls)

    # Print summary
    avg_latency = total_latency / max(successful_calls, 1)
    success_rate = successful_calls / max(total_calls, 1) * 100

    print(f"\n{'='*70}")
    print("📊 EXERCISE SUMMARY")
    print(f"{'='*70}")
    print(f"   Agents exercised: {len(agents)}")
    print(f"   Total calls:      {total_calls}")
    print(f"   Successful:       {successful_calls}")
    print(f"   Failed:           {total_calls - successful_calls}")
    print(f"   Success rate:     {success_rate:.1f}%")
    print(f"   Total tokens:     {total_tokens:,}")
    print(f"   Avg latency:      {avg_latency:.0f}ms")
    print(f"   Est. cost:        ${total_tokens * 0.00001:.4f}")
    print(f"{'='*70}")
    print("\n💡 Refresh the Fleet Health Dashboard to see updated metrics!")
    print("   http://localhost:8099")

    return results


# ============================================================================
# MAIN
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Exercise V2 AI agents in your fleet to generate dashboard metrics"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of iterations to run (default: 1)",
    )
    parser.add_argument(
        "--prompts",
        type=int,
        default=2,
        help="Number of prompts per agent per iteration (default: 2)",
    )
    parser.add_argument(
        "--agents",
        type=int,
        default=0,
        help="Max agents to exercise (0 = all, default: 0)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default="",
        help="Comma-separated name patterns to match (e.g. 'Customer,Weather')",
    )
    parser.add_argument(
        "--include-failures",
        action="store_true",
        help="Include empty prompts designed to test error handling",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--telemetry",
        action="store_true",
        help="Enable OpenTelemetry (Azure Monitor if configured, else console)",
    )
    parser.add_argument(
        "--telemetry-console",
        action="store_true",
        help="Force console span exporter (implies --telemetry)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Just list exercisable agents and exit",
    )

    args = parser.parse_args()

    # Check endpoint
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT not set")
        print("   Make sure your .env file is configured")
        sys.exit(1)

    print("🎛️  Agent Exercise Script V2 (February 2026)")
    print(f"   Endpoint: {endpoint[:60]}...")

    # Setup telemetry
    telemetry_enabled = args.telemetry or args.telemetry_console
    setup_telemetry(telemetry_enabled, force_console=args.telemetry_console)

    # Discover agents (sync)
    print("\n📋 Discovering agents from project...")
    all_agents = discover_agents(endpoint)
    exercisable = filter_exercisable(all_agents)

    print(f"   Found {len(all_agents)} total agents, {len(exercisable)} exercisable (prompt kind)")

    # Show non-exercisable agents
    skipped = [a for a in all_agents if a not in exercisable]
    if skipped:
        print(f"   Skipped {len(skipped)}: {', '.join(a.name + ' (' + a.kind + ')' for a in skipped)}")

    # Apply filter
    if args.filter:
        patterns = [p.strip().lower() for p in args.filter.split(",") if p.strip()]
        exercisable = [
            a for a in exercisable
            if any(pat in a.name.lower() for pat in patterns)
        ]
        print(f"   After filter '{args.filter}': {len(exercisable)} agents")

    # Apply max agents limit
    if args.agents > 0:
        exercisable = exercisable[: args.agents]
        print(f"   Limited to first {args.agents} agents")

    if not exercisable:
        print("\n⚠️  No exercisable agents found!")
        print("   Deploy some with: python deploy_new_agents.py")
        sys.exit(0)

    # List mode
    if args.list:
        print(f"\n{'#':<4} {'Name':<35} {'Model':<20} {'Kind':<10} {'Ver'}")
        print("-" * 80)
        for i, a in enumerate(exercisable, 1):
            print(f"{i:<4} {a.name:<35} {a.model:<20} {a.kind:<10} v{a.version}")
        print(f"\nTotal: {len(exercisable)} exercisable agents")
        return

    # Run exercise (async)
    try:
        asyncio.run(exercise_agents(
            endpoint=endpoint,
            agents=exercisable,
            iterations=args.iterations,
            prompts_per_agent=args.prompts,
            include_failures=args.include_failures,
            delay_between_calls=args.delay,
        ))
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    finally:
        shutdown_telemetry()


if __name__ == "__main__":
    main()

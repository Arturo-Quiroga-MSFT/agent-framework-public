#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Agent Exercise Script V2 - Uses EXISTING agents (no new agents created)

This script runs prompts against existing agents to generate telemetry data
visible in the Fleet Health Dashboard:
- Success/failure rates
- Token usage and costs
- Latency metrics
- Run counts

AGENTS USED (7 existing agents):
- BasicAgent
- WeatherAgent
- BasicWeatherAgent
- CodeInterpreterAgent
- BingGroundingAgent
- WebSearchAgent
- FileSearchAgent

Telemetry is sent to Application Insights via OpenTelemetry.

USAGE:
    python exercise_agents_v2.py                    # Run 1 iteration
    python exercise_agents_v2.py --iterations 5    # Run 5 iterations
    python exercise_agents_v2.py --include-failures # Include failing prompts

PREREQUISITES:
    - Azure CLI authenticated: az login
    - .env file configured
"""

import os
import asyncio
import argparse
import random
import time
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# TELEMETRY SETUP - Send metrics to Application Insights
# ============================================================================
TELEMETRY_ENABLED = False
tracer = None
trace = None
Status = None
StatusCode = None

try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace as otel_trace
    from opentelemetry.trace import Status as OtelStatus, StatusCode as OtelStatusCode
    
    trace = otel_trace
    Status = OtelStatus
    StatusCode = OtelStatusCode
    
    app_insights_conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn_str:
        configure_azure_monitor(
            connection_string=app_insights_conn_str,
            enable_live_metrics=True,
        )
        TELEMETRY_ENABLED = True
        tracer = trace.get_tracer(__name__)
        print("✅ Telemetry enabled - sending to Application Insights")
    else:
        print("⚠️ APPLICATIONINSIGHTS_CONNECTION_STRING not set - telemetry disabled")
except ImportError:
    print("⚠️ azure-monitor-opentelemetry not installed - telemetry disabled")
    print("   Install with: pip install azure-monitor-opentelemetry")

# ============================================================================
# WORKAROUND for azure-ai-projects 2.0.0b2 gzip encoding bug
# ============================================================================
import azure.core.pipeline.policies as policies
_original_on_request = policies.HeadersPolicy.on_request
def _patched_on_request(self, request):
    _original_on_request(self, request)
    request.http_request.headers['Accept-Encoding'] = 'identity'
policies.HeadersPolicy.on_request = _patched_on_request
# ============================================================================

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential


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


# 7 existing agents to exercise (these already exist in your project)
EXISTING_AGENTS = [
    "BasicAgent",
    "WeatherAgent",
    "BasicWeatherAgent",
    "CodeInterpreterAgent",
    "BingGroundingAgent",
    "WebSearchAgent",
    "FileSearchAgent",
]

# Prompts for exercising agents
GENERAL_PROMPTS = [
    "Hello! What can you help me with?",
    "Give me a brief summary of your capabilities.",
    "What is 2 + 2?",
    "Tell me a short joke.",
    "What's the capital of France?",
    "Explain what an AI agent is in one sentence.",
    "List 3 colors of the rainbow.",
    "What year did World War II end?",
    "Name the largest planet in our solar system.",
    "What is the speed of light?",
]

# Prompts designed to potentially fail
FAILING_PROMPTS = [
    "",  # Empty prompt
]


async def exercise_existing_agent(
    project_client: AIProjectClient,
    agent_name: str,
    prompt: str,
) -> ExerciseResult:
    """Exercise a single prompt against an existing agent."""
    start_time = time.time()
    response_text = ""
    tokens_used = 0
    
    # Create telemetry span if enabled
    span = None
    if tracer:
        span = tracer.start_span(
            "agent.run",
            attributes={
                "gen_ai.system": "azure_ai_agents",
                "gen_ai.agent.name": agent_name,
                "gen_ai.agent.id": agent_name,
                "gen_ai.request.model": os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
                "gen_ai.prompt": prompt[:500] if prompt else "(empty)",
            }
        )
    
    try:
        # Use existing agent with use_latest_version=True
        chat_client = AzureAIClient(
            project_client=project_client,
            agent_name=agent_name,
            use_latest_version=True,
        )
        
        async with ChatAgent(chat_client=chat_client) as agent:
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
            tokens_used=tokens_used
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
            tokens_used=0
        )
    finally:
        if span:
            span.end()


async def exercise_agents(
    iterations: int = 1,
    include_failures: bool = False,
    delay_between_calls: float = 1.0,
    prompts_per_agent: int = 2,
) -> List[ExerciseResult]:
    """
    Exercise existing agents with various prompts.
    
    Args:
        iterations: Number of times to run through all agents
        include_failures: Whether to include prompts designed to fail
        delay_between_calls: Seconds to wait between API calls
        prompts_per_agent: Number of prompts per agent per iteration
    """
    print(f"\n🏋️ Exercising {len(EXISTING_AGENTS)} EXISTING agents for {iterations} iteration(s)")
    print(f"   Agents: {', '.join(EXISTING_AGENTS)}")
    print("=" * 70)
    
    results = []
    total_calls = 0
    successful_calls = 0
    total_tokens = 0
    total_latency = 0
    
    # Build prompt list
    prompts = GENERAL_PROMPTS.copy()
    if include_failures:
        prompts.extend(FAILING_PROMPTS)
    
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=credential
        ) as project_client,
    ):
        for iteration in range(iterations):
            if iterations > 1:
                print(f"\n📍 Iteration {iteration + 1}/{iterations}")
            
            for agent_name in EXISTING_AGENTS:
                # Pick random prompts for this agent
                selected_prompts = random.sample(prompts, min(prompts_per_agent, len(prompts)))
                
                print(f"\n🤖 {agent_name} (existing)")
                print(f"   Running {len(selected_prompts)} prompts...")
                
                for prompt in selected_prompts:
                    result = await exercise_existing_agent(project_client, agent_name, prompt)
                    results.append(result)
                    total_calls += 1
                    
                    if result.success:
                        successful_calls += 1
                        total_tokens += result.tokens_used
                        total_latency += result.latency_ms
                        status = "✅"
                    else:
                        status = "❌"
                        print(f"      Error: {result.error}")
                    
                    # Print progress
                    prompt_preview = prompt[:40] + "..." if len(prompt) > 40 else (prompt or "(empty)")
                    print(f"   {status} \"{prompt_preview}\" ({result.latency_ms:.0f}ms, ~{result.tokens_used} tokens)")
                    
                    # Rate limiting
                    await asyncio.sleep(delay_between_calls)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 EXERCISE SUMMARY")
    print("=" * 70)
    print(f"   Agents exercised: {len(EXISTING_AGENTS)} (EXISTING - no new agents created)")
    print(f"   Total calls:      {total_calls}")
    print(f"   Successful:       {successful_calls}")
    print(f"   Failed:           {total_calls - successful_calls}")
    print(f"   Success rate:     {(successful_calls/max(total_calls,1)*100):.1f}%")
    print(f"   Total tokens:     {total_tokens:,}")
    print(f"   Avg latency:      {(total_latency/max(successful_calls,1)):.0f}ms")
    print(f"   Est. cost:        ${total_tokens * 0.00001:.4f}")
    print("=" * 70)
    print("\n💡 Refresh the Fleet Health Dashboard to see updated metrics!")
    print("   http://localhost:8099")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Exercise EXISTING AI agents to generate metrics (no new agents created)"
    )
    parser.add_argument(
        "--iterations", 
        type=int, 
        default=1,
        help="Number of iterations to run (default: 1)"
    )
    parser.add_argument(
        "--prompts",
        type=int,
        default=2,
        help="Number of prompts per agent per iteration (default: 2)"
    )
    parser.add_argument(
        "--include-failures",
        action="store_true",
        help="Include prompts designed to fail"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (default: 1.0)"
    )
    
    args = parser.parse_args()
    
    # Check endpoint
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT not set")
        print("   Make sure your .env file is configured")
        return
    
    print("🎛️ Agent Exercise Script V2 (using EXISTING agents)")
    print(f"   Endpoint: {endpoint[:50]}...")
    
    # Run exercise
    asyncio.run(exercise_agents(
        iterations=args.iterations,
        include_failures=args.include_failures,
        delay_between_calls=args.delay,
        prompts_per_agent=args.prompts,
    ))


if __name__ == "__main__":
    main()

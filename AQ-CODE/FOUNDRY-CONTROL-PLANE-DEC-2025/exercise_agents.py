#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Agent Exercise Script - Generate metrics for Fleet Health Dashboard

This script runs a variety of prompts against agents to generate
telemetry data visible in the Fleet Health Dashboard:
- Success/failure rates
- Token usage and costs
- Latency metrics
- Run counts

Telemetry is sent to Application Insights via OpenTelemetry.

USAGE:
    # Exercise agents with default prompts
    python exercise_agents.py
    
    # Run more iterations
    python exercise_agents.py --iterations 10
    
    # Include some failing prompts to test error handling
    python exercise_agents.py --include-failures

PREREQUISITES:
    - Azure CLI authenticated: az login
    - .env file configured with AZURE_AI_PROJECT_ENDPOINT
    - APPLICATIONINSIGHTS_CONNECTION_STRING configured for telemetry
"""

import os
import sys
import asyncio
import argparse
import random
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# TELEMETRY SETUP - Send metrics to Application Insights
# ============================================================================
TELEMETRY_ENABLED = False
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    
    app_insights_conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn_str:
        configure_azure_monitor(
            connection_string=app_insights_conn_str,
            enable_live_metrics=True,
        )
        TELEMETRY_ENABLED = True
        print("✅ Telemetry enabled - sending to Application Insights")
    else:
        print("⚠️ APPLICATIONINSIGHTS_CONNECTION_STRING not set - telemetry disabled")
except ImportError:
    print("⚠️ azure-monitor-opentelemetry not installed - telemetry disabled")
    print("   Install with: pip install azure-monitor-opentelemetry")

# Get tracer for custom spans
tracer = trace.get_tracer(__name__) if TELEMETRY_ENABLED else None
# ============================================================================

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

from agent_framework.azure import AzureAIClient
from azure.identity.aio import AzureCliCredential
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


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


# Prompts for different scenarios
GENERAL_PROMPTS = [
    "Hello! What can you help me with?",
    "Give me a brief summary of your capabilities.",
    "What is 2 + 2?",
    "Tell me a short joke.",
    "What's the capital of France?",
    "Explain what an AI agent is in one sentence.",
    "List 3 colors of the rainbow.",
]

# Prompts designed to potentially fail (for testing error handling)
FAILING_PROMPTS = [
    "",  # Empty prompt
]


class AgentExerciser:
    """Exercises agents to generate metrics using agent_framework."""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.results: List[ExerciseResult] = []
    
    def get_all_agents(self) -> List[Dict]:
        """Get list of all agents from the project."""
        agents = []
        client = AIProjectClient(
            endpoint=self.endpoint, 
            credential=DefaultAzureCredential()
        )
        for agent in client.agents.list():
            agents.append({
                "id": getattr(agent, 'id', getattr(agent, 'name', 'unknown')),
                "name": getattr(agent, 'name', 'Unknown'),
            })
        return agents
    
    async def exercise_single_prompt(
        self, 
        agent_name: str,
        instructions: str,
        prompt: str,
    ) -> ExerciseResult:
        """Exercise a single prompt using agent_framework with telemetry."""
        start_time = time.time()
        response_text = ""
        tokens_used = 0
        
        # Create telemetry span if enabled
        span_context = None
        if tracer:
            span_context = tracer.start_as_current_span(
                "agent.run",
                attributes={
                    "gen_ai.system": "azure_ai_agents",
                    "gen_ai.agent.name": agent_name,
                    "gen_ai.request.model": os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
                    "gen_ai.prompt": prompt[:500],
                }
            )
        
        try:
            if span_context:
                span_context.__enter__()
            
            async with (
                AzureCliCredential() as credential,
                AzureAIClient(async_credential=credential).create_agent(
                    name=f"ex{agent_name[:20]}{random.randint(100,999)}",
                    instructions=instructions,
                ) as agent,
            ):
                result = await agent.run(prompt)
                response_text = str(result) if result else "No response"
                
                # Estimate tokens (rough approximation)
                tokens_used = len(prompt.split()) + len(response_text.split()) * 2
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Record success in telemetry
            if span_context:
                current_span = trace.get_current_span()
                current_span.set_attribute("gen_ai.usage.total_tokens", tokens_used)
                current_span.set_attribute("gen_ai.response.finish_reason", "stop")
                current_span.set_attribute("duration_ms", latency_ms)
                current_span.set_status(Status(StatusCode.OK))
            
            return ExerciseResult(
                agent_name=agent_name,
                prompt=prompt[:100] + "..." if len(prompt) > 100 else prompt,
                success=True,
                response=response_text[:200] if response_text else "No response",
                error=None,
                latency_ms=latency_ms,
                tokens_used=tokens_used
            )
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            
            # Record failure in telemetry
            if span_context:
                current_span = trace.get_current_span()
                current_span.set_attribute("error", True)
                current_span.set_attribute("error.message", str(e)[:200])
                current_span.set_attribute("duration_ms", latency_ms)
                current_span.set_status(Status(StatusCode.ERROR, str(e)[:100]))
            
            return ExerciseResult(
                agent_name=agent_name,
                prompt=prompt[:100] + "..." if len(prompt) > 100 else prompt,
                success=False,
                response=None,
                error=str(e)[:200],
                latency_ms=latency_ms,
                tokens_used=0
            )
        finally:
            if span_context:
                span_context.__exit__(None, None, None)
    
    async def exercise_agents(
        self,
        iterations: int = 1,
        include_failures: bool = False,
        delay_between_calls: float = 1.0
    ) -> List[ExerciseResult]:
        """
        Exercise agents by creating temporary agents with various personas.
        
        Args:
            iterations: Number of times to run through all prompts
            include_failures: Whether to include prompts designed to fail
            delay_between_calls: Seconds to wait between API calls
        """
        # Define agent personas to simulate
        agent_personas = [
            ("GeneralAssistant", "You are a helpful general assistant. Be concise."),
            ("WeatherBot", "You are a weather information assistant. Respond briefly."),
            ("CodeHelper", "You are a coding assistant. Keep answers short."),
            ("MathTutor", "You are a math tutor. Be concise and clear."),
            ("CreativeWriter", "You are a creative writing assistant. Be brief."),
        ]
        
        print(f"\n🏋️ Exercising {len(agent_personas)} agent personas for {iterations} iteration(s)")
        print("=" * 60)
        
        total_calls = 0
        successful_calls = 0
        total_tokens = 0
        total_latency = 0
        
        # Build prompt list
        prompts = GENERAL_PROMPTS.copy()
        if include_failures:
            prompts.extend(FAILING_PROMPTS)
        
        for iteration in range(iterations):
            if iterations > 1:
                print(f"\n📍 Iteration {iteration + 1}/{iterations}")
            
            for agent_name, instructions in agent_personas:
                # Pick random prompts for this agent
                selected_prompts = random.sample(prompts, min(3, len(prompts)))
                
                print(f"\n🤖 {agent_name}")
                print(f"   Running {len(selected_prompts)} prompts...")
                
                for prompt in selected_prompts:
                    result = await self.exercise_single_prompt(agent_name, instructions, prompt)
                    self.results.append(result)
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
                    prompt_preview = prompt[:40] + "..." if len(prompt) > 40 else prompt
                    print(f"   {status} \"{prompt_preview}\" ({result.latency_ms:.0f}ms, ~{result.tokens_used} tokens)")
                    
                    # Rate limiting
                    await asyncio.sleep(delay_between_calls)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 EXERCISE SUMMARY")
        print("=" * 60)
        print(f"   Total calls:      {total_calls}")
        print(f"   Successful:       {successful_calls}")
        print(f"   Failed:           {total_calls - successful_calls}")
        print(f"   Success rate:     {(successful_calls/max(total_calls,1)*100):.1f}%")
        print(f"   Total tokens:     {total_tokens:,}")
        print(f"   Avg latency:      {(total_latency/max(successful_calls,1)):.0f}ms")
        print(f"   Est. cost:        ${total_tokens * 0.00001:.4f}")
        print("=" * 60)
        print("\n💡 Refresh the Fleet Health Dashboard to see updated metrics!")
        print("   http://localhost:8099")
        
        return self.results


def main():
    parser = argparse.ArgumentParser(description="Exercise AI agents to generate metrics")
    parser.add_argument(
        "--iterations", 
        type=int, 
        default=1,
        help="Number of iterations to run (default: 1)"
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
    parser.add_argument(
        "--list",
        action="store_true",
        help="Just list available agents and exit"
    )
    
    args = parser.parse_args()
    
    # Get endpoint
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT not set")
        print("   Make sure your .env file is configured")
        sys.exit(1)
    
    print("🎛️ Agent Exercise Script")
    print(f"   Endpoint: {endpoint[:50]}...")
    
    # Create exerciser
    exerciser = AgentExerciser(endpoint)
    
    # List mode
    if args.list:
        agents = exerciser.get_all_agents()
        print(f"\n📋 Existing agents in project ({len(agents)}):")
        for i, a in enumerate(agents, 1):
            print(f"   {i:2}. {a['name']}")
        return
    
    # Run exercise
    asyncio.run(exerciser.exercise_agents(
        iterations=args.iterations,
        include_failures=args.include_failures,
        delay_between_calls=args.delay
    ))


if __name__ == "__main__":
    main()

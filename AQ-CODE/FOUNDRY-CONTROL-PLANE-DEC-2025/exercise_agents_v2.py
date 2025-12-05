#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Agent Exercise Script V2 - Exercises all 10 agents in your fleet

This script runs prompts against all agents to generate telemetry data
visible in the Fleet Health Dashboard:
- Success/failure rates
- Token usage and costs
- Latency metrics
- Run counts

AGENTS USED (10 agents total):
- BingSearchAgent (existing)
- CodeInterpreterAgent (existing)
- DataAnalysisAgent (new)
- ResearchAgent (new)
- CustomerSupportAgent (new)
- FinancialAnalystAgent (new)
- TechnicalWriterAgent (new)
- HRAssistantAgent (new)
- MarketingStrategistAgent (new)
- ProjectManagerAgent (new)

Telemetry is sent to Application Insights via OpenTelemetry.

USAGE:
    python exercise_agents_v2.py                    # Run 1 iteration
    python exercise_agents_v2.py --iterations 5    # Run 5 iterations
    python exercise_agents_v2.py --include-failures # Include failing prompts

PREREQUISITES:
    - Azure CLI authenticated: az login
    - .env file configured
    - Run deploy_new_agents.py first to create the 8 new agents
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


# 10 agents to exercise (2 existing + 8 newly created)
EXISTING_AGENTS = [
    # Original existing agents
    "BingSearchAgent",
    "CodeInterpreterAgent",
    # Newly created agents
    "DataAnalysisAgent",
    "ResearchAgent",
    "CustomerSupportAgent",
    "FinancialAnalystAgent",
    "TechnicalWriterAgent",
    "HRAssistantAgent",
    "MarketingStrategistAgent",
    "ProjectManagerAgent",
]

# Prompts for exercising agents - general purpose
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
    "Calculate the area of a circle with radius 5.",
    "Convert 100 degrees Fahrenheit to Celsius.",
]

# Data Analysis specific prompts
DATA_ANALYSIS_PROMPTS = [
    "Analyze this dataset: [12, 15, 18, 22, 25, 28, 30] - calculate mean and standard deviation.",
    "Create a simple bar chart showing: Product A=50, Product B=75, Product C=60.",
    "What statistical test should I use to compare two groups?",
    "Explain the difference between correlation and causation.",
]

# Research Agent specific prompts
RESEARCH_PROMPTS = [
    "Summarize the key benefits of cloud computing.",
    "What are the main differences between REST and GraphQL?",
    "List 5 best practices for API design.",
]

# Customer Support specific prompts
CUSTOMER_SUPPORT_PROMPTS = [
    "How do I reset my password?",
    "I'm having trouble logging into my account.",
    "What are your business hours?",
    "I'd like to request a refund.",
]

# Financial Analyst specific prompts
FINANCIAL_PROMPTS = [
    "Calculate the ROI for an investment of $10,000 that returns $12,500 after one year.",
    "What is EBITDA and why is it important?",
    "Explain the difference between gross margin and net margin.",
    "Calculate the compound interest on $5,000 at 5% for 3 years.",
]

# Technical Writer specific prompts
TECHNICAL_WRITER_PROMPTS = [
    "Write a brief README introduction for a Python library.",
    "What are the key sections of good API documentation?",
    "How should I document a REST endpoint?",
    "Write a brief changelog entry for a bug fix.",
]

# HR Assistant specific prompts
HR_PROMPTS = [
    "What is the company's PTO policy?",
    "How do I enroll in benefits?",
    "What's the process for requesting time off?",
    "Who do I contact about payroll questions?",
]

# Marketing Strategist specific prompts
MARKETING_PROMPTS = [
    "Suggest 3 content ideas for a B2B software blog.",
    "What are the key metrics for measuring social media success?",
    "How should I structure an A/B test for email subject lines?",
    "What's the difference between SEO and SEM?",
]

# Project Manager specific prompts
PROJECT_MANAGER_PROMPTS = [
    "Create a simple project timeline for a 3-month software project.",
    "What should be included in a project kickoff meeting?",
    "How do I handle scope creep?",
    "What's the difference between Agile and Waterfall?",
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
    print(f"\n🏋️ Exercising {len(EXISTING_AGENTS)} agents in your fleet for {iterations} iteration(s)")
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
                # Select appropriate prompts based on agent type
                if agent_name == "DataAnalysisAgent":
                    available_prompts = DATA_ANALYSIS_PROMPTS + prompts[:3]
                elif agent_name == "ResearchAgent":
                    available_prompts = RESEARCH_PROMPTS + prompts[:3]
                elif agent_name == "CustomerSupportAgent":
                    available_prompts = CUSTOMER_SUPPORT_PROMPTS + prompts[:2]
                elif agent_name == "FinancialAnalystAgent":
                    available_prompts = FINANCIAL_PROMPTS + prompts[:2]
                elif agent_name == "TechnicalWriterAgent":
                    available_prompts = TECHNICAL_WRITER_PROMPTS + prompts[:2]
                elif agent_name == "HRAssistantAgent":
                    available_prompts = HR_PROMPTS + prompts[:2]
                elif agent_name == "MarketingStrategistAgent":
                    available_prompts = MARKETING_PROMPTS + prompts[:2]
                elif agent_name == "ProjectManagerAgent":
                    available_prompts = PROJECT_MANAGER_PROMPTS + prompts[:2]
                elif agent_name == "CodeInterpreterAgent":
                    # Code-focused prompts
                    available_prompts = [
                        "Calculate the factorial of 10.",
                        "Generate a list of the first 10 Fibonacci numbers.",
                        "What is 15% of 250?",
                    ] + prompts[:2]
                elif agent_name == "BingSearchAgent":
                    # Search-focused prompts
                    available_prompts = [
                        "What are the latest tech news headlines?",
                        "Find information about Azure AI services.",
                    ] + prompts[:2]
                else:
                    # Use general prompts for other agents
                    available_prompts = prompts
                
                selected_prompts = random.sample(available_prompts, min(prompts_per_agent, len(available_prompts)))
                
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
    print(f"   Agents exercised: {len(EXISTING_AGENTS)} (your full fleet)")
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
        description="Exercise all 10 AI agents in your fleet to generate metrics"
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
    
    print("🎛️ Agent Exercise Script V2 (exercising all 10 fleet agents)")
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

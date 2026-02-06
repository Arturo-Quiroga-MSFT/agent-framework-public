# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Agent Observability Demo (Updated February 2026)

This sample demonstrates how to setup telemetry for an Azure AI agent using
the AzureAIClient and Application Insights via the Foundry Control Plane.

RECOMMENDED PATTERN: AzureAIClient.configure_azure_monitor()
This single call automatically:
1. Retrieves Application Insights connection string from Foundry project
2. Configures Azure Monitor OpenTelemetry exporters (traces, logs, metrics)
3. Enables Agent Framework instrumentation
4. Optionally enables Live Metrics streaming

FEATURES:
- AzureAIClient-based setup (current recommended pattern)
- Automatic Application Insights configuration from Foundry project
- Live Metrics support for real-time monitoring in Azure Portal
- Agent `id` parameter for Foundry Control Plane fleet tracking
- @tool decorator with approval_mode for production safety
- Real OpenWeatherMap API integration with async httpx
- Multi-turn conversation tracking
- Trace ID output for Azure Portal + Foundry Portal investigation
- Compatible with Grafana dashboards (https://aka.ms/amg/dash/af-agent)

PREREQUISITES:
- Azure AI Foundry Project with Application Insights attached
- Azure CLI authentication: Run 'az login'
- AZURE_AI_PROJECT_ENDPOINT configured in .env file
- OPENWEATHER_API_KEY configured in .env file (https://openweathermap.org/api)
- pip install agent-framework[azure] azure-monitor-opentelemetry

WHAT CHANGED FROM DEC 2025:
- AzureAIClient replaces separate AgentsClient + manual setup_observability()
- configure_azure_monitor() replaces deprecated setup_observability()
- @tool(approval_mode=...) decorator replaces plain function definition
- Agent `id` parameter enables Foundry Control Plane fleet visibility
- Standard OTEL env vars (OTEL_EXPORTER_OTLP_ENDPOINT) replace custom vars
- agent.name replaces agent.display_name

WORKSHOP NOTES:
- Run this after setting up your .env file
- Traces visible in: Azure Portal > App Insights > Transaction Search
- Also visible in: Foundry Portal > Operate > Assets > [agent] > Traces
- Use the Trace ID printed to console to find specific executions
- Grafana dashboards: https://aka.ms/amg/dash/af-agent
- Compare with workflow_observability.py for workflow telemetry patterns
"""

import asyncio
import os
from pathlib import Path
from typing import Annotated

import httpx
from dotenv import load_dotenv
from agent_framework import ChatAgent, tool
from agent_framework.azure import AzureAIClient
from agent_framework.observability import get_tracer
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from pydantic import Field

# Load environment variables from .env in this directory
load_dotenv(Path(__file__).parent / ".env")


# NOTE: approval_mode="never_require" is for sample brevity.
# Use "always_require" in production for tools that perform sensitive actions.
# See: samples/getting_started/tools/function_tool_with_approval.py
@tool(approval_mode="never_require")
async def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the current weather for a given location using OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return (
            "Error: OPENWEATHER_API_KEY not found in environment variables. "
            "Get a free API key at https://openweathermap.org/api"
        )

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        return (
            f"The weather in {location} is {description} with a temperature of "
            f"{temp}°C (feels like {feels_like}°C) and {humidity}% humidity."
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{location}' not found."
        return f"Error fetching weather data: {e}"
    except Exception as e:
        return f"Error: {str(e)}"


async def main():
    print("=" * 80)
    print("Azure AI Agent Observability Demo")
    print("  Pattern: AzureAIClient + configure_azure_monitor() (Feb 2026)")
    print("=" * 80)
    print()

    # Validate environment variables
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("ERROR: AZURE_AI_PROJECT_ENDPOINT not found in environment variables")
        print("  Please configure your .env file")
        return

    print(f"Azure AI Foundry Project: {endpoint}")
    print()

    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        AzureAIClient(project_client=project_client) as client,
    ):
        # =====================================================================
        # NEW RECOMMENDED PATTERN (replaces deprecated setup_observability())
        #
        # AzureAIClient.configure_azure_monitor() does everything in one call:
        #   1. Gets App Insights connection string from the Foundry project
        #   2. Calls azure-monitor-opentelemetry's configure_azure_monitor()
        #   3. Calls enable_instrumentation() for Agent Framework telemetry
        #   4. Optionally enables Live Metrics streaming
        #
        # For non-Azure projects, use configure_otel_providers() instead.
        # See: maf-upstream/python/samples/getting_started/observability/
        # =====================================================================
        await client.configure_azure_monitor(enable_live_metrics=True)
        print("Observability configured via AzureAIClient.configure_azure_monitor()")
        print("  - Application Insights: connected")
        print("  - Live Metrics: enabled")
        print("  - Sensitive data: controlled via ENABLE_SENSITIVE_DATA env var")
        print()

        questions = [
            "What's the weather in Amsterdam?",
            "and in Paris, and which is better?",
            "Why is the sky blue?",
        ]

        with get_tracer().start_as_current_span(
            "Single Agent Chat", kind=SpanKind.CLIENT
        ) as current_span:
            trace_id = format_trace_id(current_span.get_span_context().trace_id)
            print(f"Trace ID: {trace_id}")
            print("Use this Trace ID to find this execution in:")
            print("  - Azure Portal > Application Insights > Transaction Search")
            print("  - Foundry Portal > Operate > Assets > [agent] > Traces tab")
            print()

            # =====================================================================
            # The `id` parameter is KEY for Foundry Control Plane integration.
            # When set, the agent appears in Operate > Assets and traces link
            # back to the registered agent for fleet-wide monitoring.
            # =====================================================================
            agent = ChatAgent(
                chat_client=client,
                tools=get_weather,
                name="WeatherAgent",
                instructions="You are a weather assistant.",
                id="weather-agent",
            )
            thread = agent.get_new_thread()

            for question in questions:
                print(f"User: {question}")
                print(f"{agent.name}: ", end="")
                async for update in agent.run_stream(
                    question,
                    thread=thread,
                ):
                    if update.text:
                        print(update.text, end="")
                print()
                print()

    print("=" * 80)
    print("Demo completed!")
    print()
    print("View traces:")
    print(f"  Trace ID: {trace_id}")
    print("  Azure Portal > Application Insights > Transaction Search")
    print("  Foundry Portal > Operate > Assets > WeatherAgent > Traces")
    print()
    print("Grafana dashboards (if configured):")
    print("  Agent Overview:    https://aka.ms/amg/dash/af-agent")
    print("  Workflow Overview:  https://aka.ms/amg/dash/af-workflow")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

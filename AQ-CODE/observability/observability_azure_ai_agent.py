# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Agent Observability Demo

This sample demonstrates how to setup telemetry for an Azure AI agent using Application Insights.
It shows how the Azure AI project automatically configures tracing to send telemetry data to
the Application Insights instance attached to your Azure AI project.

FEATURES:
- Automatic telemetry setup from Azure AI Project
- Application Insights integration
- Traces sent to Azure Monitor
- Weather tool function calls
- Multi-turn conversation tracking
- Trace ID output for investigation in Azure Portal

PREREQUISITES:
- Azure AI Project with Application Insights attached
- Azure CLI authentication: Run 'az login'
- AZURE_AI_PROJECT_ENDPOINT configured in .env file
- AZURE_AI_MODEL_DEPLOYMENT_NAME configured in .env file
- OPENWEATHER_API_KEY configured in .env file (get free key at https://openweathermap.org/api)

TRACING:
This sample uses setup_azure_ai_observability() which automatically:
1. Retrieves Application Insights connection string from Azure AI Project
2. Configures OpenTelemetry to send traces to Application Insights
3. Enables full distributed tracing for the agent workflow

WORKSHOP NOTES:
- Run this after setting up your .env file
- Check Azure Portal > Application Insights > Transaction Search to see traces
- Use the Trace ID printed to the console to find specific executions
- Compare with workflow_observability.py to see different telemetry patterns
"""

import asyncio
import os
from pathlib import Path
from typing import Annotated

import httpx
from dotenv import load_dotenv
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from agent_framework.observability import get_tracer
from azure.ai.agents.aio import AgentsClient
from azure.ai.projects.aio import AIProjectClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from pydantic import Field

# Load environment variables from AQ-CODE/.env
load_dotenv(Path(__file__).parent / ".env")


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the current weather for a given location using OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return f"Error: OPENWEATHER_API_KEY not found in environment variables. Get a free API key at https://openweathermap.org/api"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        return f"The weather in {location} is {description} with a temperature of {temp}°C (feels like {feels_like}°C) and {humidity}% humidity."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{location}' not found."
        return f"Error fetching weather data: {e}"
    except Exception as e:
        return f"Error: {str(e)}"


async def setup_azure_ai_observability(
    project_client: AIProjectClient, enable_sensitive_data: bool | None = None
) -> None:
    """Use this method to setup tracing in your Azure AI Project.

    This will take the connection string from the AIProjectClient.
    It will override any connection string that is set in the environment variables.
    It will disable any OTLP endpoint that might have been set.
    """
    try:
        conn_string = await project_client.telemetry.get_application_insights_connection_string()
        print(f"✓ Application Insights connection string retrieved from Azure AI Project")
    except ResourceNotFoundError:
        print("✗ No Application Insights connection string found for the Azure AI Project.")
        print("  Please attach Application Insights to your Azure AI project in Azure AI Studio.")
        return
    
    from agent_framework.observability import setup_observability

    setup_observability(applicationinsights_connection_string=conn_string, enable_sensitive_data=enable_sensitive_data)
    print(f"✓ Observability configured - telemetry will be sent to Application Insights")


async def main():
    print("=" * 80)
    print("Azure AI Agent Observability Demo")
    print("=" * 80)
    print()
    
    # Validate environment variables
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("✗ ERROR: AZURE_AI_PROJECT_ENDPOINT not found in environment variables")
        print("  Please configure your .env file in AQ-CODE/.env")
        return
    
    print(f"Azure AI Project: {endpoint}")
    print()
    
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        AgentsClient(endpoint=endpoint, credential=credential) as agents_client,
        AzureAIAgentClient(agents_client=agents_client) as client,
    ):
        # This will enable tracing and configure the application to send telemetry data to the
        # Application Insights instance attached to the Azure AI project.
        # This will override any existing configuration.
        await setup_azure_ai_observability(project_client, enable_sensitive_data=True)

        questions = [
            "What's the weather in Amsterdam?",
            "and in Paris, and which is better?",
            "Why is the sky blue?"
        ]

        with get_tracer().start_as_current_span("Single Agent Chat", kind=SpanKind.CLIENT) as current_span:
            trace_id = format_trace_id(current_span.get_span_context().trace_id)
            print(f"Trace ID: {trace_id}")
            print(f"Use this Trace ID to find this execution in Azure Portal > Application Insights")
            print()

            agent = ChatAgent(
                chat_client=client,
                tools=get_weather,
                name="WeatherAgent",
                instructions="You are a weather assistant.",
            )
            thread = agent.get_new_thread()
            
            for question in questions:
                print(f"User: {question}")
                print(f"{agent.display_name}: ", end="")
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
    print("Check Azure Portal > Application Insights > Transaction Search")
    print(f"Filter by Trace ID: {trace_id}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

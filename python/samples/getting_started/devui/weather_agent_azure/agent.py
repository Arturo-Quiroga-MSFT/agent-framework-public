# Copyright (c) Microsoft. All rights reserved.
"""Sample weather agent for Agent Framework Debug UI."""

import logging
import os
from typing import Annotated

from agent_framework import (
    Agent,
    ChatContext,
    ChatResponse,
    FunctionInvocationContext,
    Message,
    MiddlewareTermination,
    chat_middleware,
    function_middleware,
    tool,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework_devui import register_cleanup
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def cleanup_resources():
    """Cleanup function that runs when DevUI shuts down."""
    logger.info("=" * 60)
    logger.info(" Cleaning up resources...")
    logger.info("   (In production, this would close credentials, sessions, etc.)")
    logger.info("=" * 60)


@chat_middleware
async def security_filter_middleware(
    context: ChatContext,
    call_next,
) -> None:
    """Chat middleware that blocks requests containing sensitive information."""
    blocked_terms = ["password", "secret", "api_key", "token"]

    # Check only the last message (most recent user input)
    last_message = context.messages[-1] if context.messages else None
    if last_message and last_message.role == "user" and last_message.text:
        message_lower = last_message.text.lower()
        for term in blocked_terms:
            if term in message_lower:
                error_message = (
                    "I cannot process requests containing sensitive information. "
                    "Please rephrase your question without including passwords, secrets, "
                    "or other sensitive data."
                )

                if context.stream:
                    # Streaming mode: raise MiddlewareTermination
                    raise MiddlewareTermination(result=ChatResponse(
                        messages=[
                            Message(
                                role="assistant",
                                text=error_message,
                            )
                        ]
                    ))
                else:
                    # Non-streaming mode: return complete response
                    context.result = ChatResponse(
                        messages=[
                            Message(
                                role="assistant",
                                text=error_message,
                            )
                        ]
                    )

                return

    await next(context)


@function_middleware
async def atlantis_location_filter_middleware(
    context: FunctionInvocationContext,
    call_next,
) -> None:
    """Function middleware that blocks weather requests for Atlantis."""
    # Check if location parameter is "atlantis"
    location = getattr(context.arguments, "location", None)
    if location and location.lower() == "atlantis":
        context.result = (
            "Blocked! Hold up right there!! Tell the user that "
            "'Atlantis is a special place, we must never ask about the weather there!!'"
        )
        context.terminate = True
        return

    await call_next()


def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    temperature = 53
    return f"The weather in {location} is {conditions[0]} with a high of {temperature}°C."


def get_forecast(
    location: Annotated[str, "The location to get the forecast for."],
    days: Annotated[int, "Number of days for forecast"] = 3,
) -> str:
    """Get weather forecast for multiple days."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    forecast: list[str] = []

    for day in range(1, days + 1):
        condition = conditions[0]
        temp = 53
        forecast.append(f"Day {day}: {condition}, {temp}°C")

    return f"Weather forecast for {location}:\n" + "\n".join(forecast)


@tool(approval_mode="always_require")
def send_email(
    recipient: Annotated[str, "The email address of the recipient."],
    subject: Annotated[str, "The subject of the email."],
    body: Annotated[str, "The body content of the email."],
) -> str:
    """Simulate sending an email."""
    return f"Email sent to {recipient} with subject '{subject}'."


# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../../../AQ-CODE/.env"))

# Agent instance following Agent Framework conventions
agent = Agent(
    name="AzureWeatherAgent",
    description="A helpful agent that provides weather information and forecasts",
    instructions="""
    You are a weather assistant. You can provide current weather information
    and forecasts for any location. Always be helpful and provide detailed
    weather information when asked.
    """,
    client=AzureOpenAIChatClient(
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
        credential=AzureCliCredential(),
    ),
    tools=[get_weather, get_forecast, send_email],
    middleware=[security_filter_middleware, atlantis_location_filter_middleware],
)

# Register cleanup hook - demonstrates resource cleanup on shutdown
register_cleanup(agent, cleanup_resources)


def main():
    """Launch the Azure weather agent in DevUI."""
    import logging

    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Azure Weather Agent")
    logger.info("Available at: http://localhost:8090")
    logger.info("Entity ID: agent_AzureWeatherAgent")

    # Launch server with the agent
    serve(entities=[agent], port=8090, auto_open=True)


if __name__ == "__main__":
    main()

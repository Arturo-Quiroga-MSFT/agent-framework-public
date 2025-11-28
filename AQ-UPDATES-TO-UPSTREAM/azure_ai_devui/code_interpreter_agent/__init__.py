"""
Azure AI Agent: Code Interpreter Agent

Demonstrates Python code execution for calculations and data analysis.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from agent_framework import HostedCodeInterpreterTool
from agent_framework.azure import AzureAIClient
from agent_framework.observability import setup_observability
from azure.identity.aio import AzureCliCredential

# Load environment variables
local_env_path = Path(__file__).parent.parent.parent / "azure_ai" / ".env"
parent_env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=local_env_path)
load_dotenv(dotenv_path=parent_env_path)

# Setup observability for tracing
if os.getenv("ENABLE_OTEL", "").lower() == "true":
    app_insights_conn = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn:
        setup_observability(
            enable_sensitive_data=os.getenv("ENABLE_SENSITIVE_DATA", "").lower() == "true",
            applicationinsights_connection_string=app_insights_conn,
        )

# Create the agent
credential = AzureCliCredential()

agent = AzureAIClient(async_credential=credential).create_agent(
    name="CodeInterpreterAgent",
    description=(
        "Code Interpreter Agent - Python Execution\n"
        "\n"
        "Can write and execute Python code to solve problems.\n"
        "\n"
        "TRY THESE:\n"
        "  • Calculate the factorial of 100\n"
        "  • Generate the first 20 Fibonacci numbers\n"
        "  • Create a plot of y = x^2 from -10 to 10\n"
        "  • Calculate compound interest on $1000 at 5% for 10 years\n"
        "  • Sort this list: [64, 34, 25, 12, 22, 11, 90]\n"
        "\n"
        "FEATURES:\n"
        "  • Python code generation\n"
        "  • Safe code execution\n"
        "  • Math and data analysis\n"
        "  • Plotting and visualization"
    ),
    instructions="You are a helpful assistant that can write and execute Python code to solve problems. Always explain what your code does.",
    tools=HostedCodeInterpreterTool(),
)

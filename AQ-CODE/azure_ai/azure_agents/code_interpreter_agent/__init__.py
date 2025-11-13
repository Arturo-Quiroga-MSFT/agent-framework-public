"""
Azure AI Agent: Python Code Interpreter

Demonstrates Azure AI Agent with Code Interpreter for executing Python code.
Perfect for mathematical calculations, data analysis, and algorithm demonstrations.
"""

import os
from pathlib import Path

from agent_framework import HostedCodeInterpreterTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables - go up to azure_ai/ directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Check required environment variables
project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model_deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

if not project_endpoint:
    raise ValueError("AZURE_AI_PROJECT_ENDPOINT not found in environment")

# Create Code Interpreter tool
code_interpreter = HostedCodeInterpreterTool()

# Create Azure AI Agent with Code Interpreter
credential = DefaultAzureCredential()

agent = AzureAIAgentClient(
    project_endpoint=project_endpoint,
    model_deployment_name=model_deployment_name,
    async_credential=credential
).create_agent(
    name="CodeInterpreterAgent",
    description=(
        "AZURE AI DEMO: Python Code Interpreter\n"
        "\n"
        "Shows Azure AI Agent that can write and execute Python code.\n"
        "\n"
        "TRY THESE QUERIES:\n"
        "  • Calculate the factorial of 100\n"
        "  • Generate the first 20 Fibonacci numbers\n"
        "  • Create a simple plot of y = x^2 from -10 to 10\n"
        "  • Calculate the square root of 12345\n"
        "  • Write code to check if 17 is a prime number\n"
        "  • Generate a list of all prime numbers between 1 and 100\n"
        "\n"
        "FEATURES:\n"
        "  • Executes Python code in secure sandbox\n"
        "  • Can perform complex mathematical calculations\n"
        "  • Supports data manipulation and analysis\n"
        "  • Shows code before executing it\n"
        "  • Returns execution results\n"
        "\n"
        "CAPABILITIES:\n"
        "  • Math operations and algorithms\n"
        "  • Data processing and analysis\n"
        "  • Iterative calculations\n"
        "  • Code generation and execution"
    ),
    instructions=(
        "You are a helpful assistant that can write and execute Python code to solve problems. "
        "When asked to perform calculations or computations, write clear Python code, "
        "explain what the code does, and execute it to get the result. "
        "Always show the code you're running before execution."
    ),
    tools=code_interpreter,
)

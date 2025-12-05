"""
Data Analysis Agent - Advanced analytics with visualization

Uses Code Interpreter for statistical analysis, data visualization,
and computational tasks. Perfect for analyzing datasets and creating charts.
"""

import os
from pathlib import Path

from agent_framework import HostedCodeInterpreterTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
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
    name="DataAnalysisAgent",
    description=(
        "Data Analysis Agent - Advanced Statistical Analysis\n"
        "\n"
        "Performs statistical analysis, creates visualizations, and analyzes datasets.\n"
        "\n"
        "TRY THESE:\n"
        "  • Analyze a dataset: [10, 20, 15, 30, 25] - calculate mean, median, std dev\n"
        "  • Create a bar chart comparing sales: Q1=100, Q2=150, Q3=120, Q4=180\n"
        "  • Calculate correlation between two variables\n"
        "  • Perform linear regression on sample data\n"
        "  • Generate a histogram of random normal distribution (100 samples)\n"
        "\n"
        "FEATURES:\n"
        "  • Statistical analysis (mean, median, std dev, correlation)\n"
        "  • Data visualization (charts, plots, histograms)\n"
        "  • Python pandas and numpy operations\n"
        "  • Matplotlib/seaborn plotting\n"
        "  • Machine learning basics\n"
        "\n"
        "TOOLS:\n"
        "  • Code Interpreter: Python execution with data science libraries\n"
    ),
    instructions=(
        "You are a data analysis expert that can write and execute Python code "
        "for statistical analysis and data visualization. "
        "Use pandas, numpy, matplotlib, and seaborn for advanced data operations. "
        "Always explain your code and provide clear interpretations of results. "
        "When creating visualizations, describe what the chart shows."
    ),
    tools=code_interpreter,
)

# Export the agent
__all__ = ["agent"]

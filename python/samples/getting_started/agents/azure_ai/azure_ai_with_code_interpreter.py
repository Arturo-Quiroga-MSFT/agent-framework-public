# Copyright (c) Microsoft. All rights reserved.

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import AgentRunResponse, ChatResponseUpdate, HostedCodeInterpreterTool
from agent_framework.azure import AzureAIAgentClient
from azure.ai.agents.models import (
    RunStepDeltaCodeInterpreterDetailItemObject,
)
from azure.identity.aio import AzureCliCredential

# Load environment variables from .env file in the current directory
load_dotenv(Path(__file__).parent / ".env")

"""
Azure AI Agent with Code Interpreter Example

This sample demonstrates using HostedCodeInterpreterTool with Azure AI Agents
for Python code execution and mathematical problem solving.
"""


def print_code_interpreter_inputs(response: AgentRunResponse) -> None:
    """Helper method to access code interpreter data."""

    print("\nCode Interpreter Inputs during the run:")
    if response.raw_representation is None:
        return
    for chunk in response.raw_representation:
        if isinstance(chunk, ChatResponseUpdate) and isinstance(
            chunk.raw_representation, RunStepDeltaCodeInterpreterDetailItemObject
        ):
            print(chunk.raw_representation.input, end="")
    print("\n")


async def main() -> None:
    """Example showing how to use the HostedCodeInterpreterTool with Azure AI."""
    print("=== Azure AI Agent with Code Interpreter Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as chat_client,
    ):
        agent = chat_client.create_agent(
            name="CodingAgent",
            instructions=(
                "You are a helpful assistant that can write and execute Python code to solve problems. "
                "Always show your code before executing it and explain your approach."
            ),
            tools=HostedCodeInterpreterTool(),
        )
        # More challenging query options:
        # Option 1: Data analysis with visualization
        query = """Analyze the Collatz conjecture for numbers 1-100:
        1. For each starting number, count how many steps it takes to reach 1
        2. Find which number takes the longest sequence
        3. Create a visualization showing the relationship between starting numbers and steps
        4. Calculate statistics (mean, median, max steps)
        Explain any interesting patterns you observe."""
        
        # Option 2: Algorithm implementation
        # query = '''Implement a function to solve the N-Queens problem for N=8:
        # 1. Find all valid solutions
        # 2. Visualize one solution as a chessboard
        # 3. Analyze how many solutions exist and any symmetries
        # Show your code and explain your algorithm.'''
        
        # Option 3: Mathematical exploration
        # query = '''Explore the Mandelbrot set:
        # 1. Generate a visualization of the Mandelbrot set for complex numbers in the range [-2, 1] × [-1.5, 1.5]
        # 2. Use at least 50 iterations to determine set membership
        # 3. Create a colorful visualization showing iteration counts
        # 4. Zoom into an interesting region and show the fractal detail
        # Explain what the Mandelbrot set represents.'''
        
        # Option 4: Data science challenge
        # query = '''Generate synthetic data and perform analysis:
        # 1. Create a dataset of 1000 points with 3 features that form 3 distinct clusters
        # 2. Add realistic noise to the data
        # 3. Implement k-means clustering from scratch (no sklearn)
        # 4. Visualize the original data and the clustering results
        # 5. Calculate and report clustering quality metrics
        # Show all your code and explain the math behind k-means.'''
        
        # Option 5: Prime number exploration
        # query = '''Explore prime number patterns:
        # 1. Find all prime numbers up to 10,000 using the Sieve of Eratosthenes
        # 2. Analyze gaps between consecutive primes - what's the distribution?
        # 3. Check Goldbach's conjecture: test that every even number from 4-1000 is the sum of two primes
        # 4. Visualize the prime number spiral (Ulam spiral) for numbers up to 400
        # Explain any interesting patterns you discover.'''
        
        print(f"User: {query}")
        response = await AgentRunResponse.from_agent_response_generator(agent.run_stream(query))
        print(f"Agent: {response}")
        # To review the code interpreter outputs, you can access
        # them from the response raw_representations, just uncomment the next line:
        print()
        print_code_interpreter_inputs(response)
        print()


if __name__ == "__main__":
    asyncio.run(main())

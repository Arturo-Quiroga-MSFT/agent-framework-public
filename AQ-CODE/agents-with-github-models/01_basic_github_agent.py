#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Basic Agent with GitHub Models

This example demonstrates creating a simple AI agent using Microsoft Agent Framework (MAF)
with GitHub Models as the LLM provider instead of Azure OpenAI or Azure AI Foundry.

GitHub Models provides free access to popular models like GPT-4o, GPT-4o-mini, Llama, Phi, etc.
through an OpenAI-compatible API endpoint.

Prerequisites:
    1. GitHub Personal Access Token (PAT):
       - Go to: https://github.com/settings/tokens
       - Generate token with appropriate scopes
       - Set as GITHUB_TOKEN environment variable
    
    2. Install dependencies:
       pip install agent-framework python-dotenv

Environment Variables:
    GITHUB_TOKEN: Your GitHub Personal Access Token (required)
    GITHUB_MODEL: Model to use (default: gpt-4o-mini)
    GITHUB_BASE_URL: API endpoint (default: https://models.inference.ai.azure.com)

Usage:
    python 01_basic_github_agent.py
"""

import asyncio
import os
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# Load environment variables from .env file
load_dotenv()


async def main():
    """Run a basic agent using GitHub Models."""
    
    # Configuration
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "GITHUB_TOKEN environment variable is required.\n"
            "Get your token at: https://github.com/settings/tokens"
        )
    
    model_id = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
    base_url = os.getenv("GITHUB_BASE_URL", "https://models.inference.ai.azure.com")
    
    print("=" * 70)
    print("🚀 MAF Agent with GitHub Models - Basic Example")
    print("=" * 70)
    print(f"\n🔧 Configuration:")
    print(f"   Endpoint: {base_url}")
    print(f"   Model:    {model_id}")
    print(f"   Token:    {github_token[:20]}...")
    print()
    
    # Create OpenAI-compatible client pointing to GitHub Models
    print("🔧 Creating GitHub Models client...")
    chat_client = OpenAIChatClient(
        model_id=model_id,
        api_key=github_token,
        base_url=base_url
    )
    
    # Create MAF agent with the GitHub Models client
    print("🤖 Creating MAF agent...")
    agent = ChatAgent(
        chat_client=chat_client,
        instructions=(
            "You are a helpful AI assistant powered by GitHub Models. "
            "You provide clear, concise, and accurate information. "
            "You acknowledge that you are using GitHub Models for inference."
        ),
        name="GitHubModelsAgent"
    )
    
    # Test queries
    queries = [
        "What are the benefits of using AI agents in software development?",
        "Explain the difference between client-side and server-side agents in 2 sentences.",
        "What is Microsoft Agent Framework (MAF)?"
    ]
    
    print("\n💬 Running agent queries...")
    print("=" * 70)
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}/{len(queries)}:")
        print(f"   User: {query}")
        print()
        
        try:
            # Run the agent
            result = await agent.run(query)
            
            print(f"   Assistant: {result}")
            print()
            
            # Rate limiting - wait between requests to respect GitHub Models limits
            if i < len(queries):
                print("   ⏳ Waiting 5 seconds (rate limit)...\n")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            if "429" in str(e):
                print("   💡 Rate limit exceeded. GitHub Models free tier has ~15 requests/minute.")
            elif "401" in str(e):
                print("   💡 Authentication failed. Check your GITHUB_TOKEN.")
            print()
    
    print("=" * 70)
    print("✅ Demo completed!")
    print()
    print("💡 Next Steps:")
    print("   - Try different models (gpt-4o, Llama-3.3-70B-Instruct, Phi-4)")
    print("   - Run 02_github_with_tools.py for function calling examples")
    print("   - See README.md for full model list and rate limits")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

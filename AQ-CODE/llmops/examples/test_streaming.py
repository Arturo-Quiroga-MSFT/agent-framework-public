"""
Test script to verify streaming implementation works correctly
"""
import asyncio
import os
from azure.identity import DefaultAzureCredential
from agent_framework.ai_clients import AzureAIAgentClient
from agent_framework import ChatAgent


async def test_streaming():
    """Test basic streaming functionality"""
    print("=== Testing Streaming Response ===\n")
    
    async with DefaultAzureCredential() as credential:
        async with AzureAIAgentClient(async_credential=credential) as client:
            agent = ChatAgent(
                chat_client=client,
                instructions="You are a helpful assistant. Provide concise answers.",
            )
            
            query = "Write a short 2-sentence summary of what streaming responses are."
            print(f"User: {query}\n")
            print("Agent: ", end="", flush=True)
            
            full_response = ""
            async for chunk in agent.run_stream(query):
                if chunk.text:
                    full_response += chunk.text
                    print(chunk.text, end="", flush=True)
            
            print("\n")
            print(f"\n=== Streaming Complete ===")
            print(f"Total response length: {len(full_response)} characters")
            print(f"Full response: {full_response}")
            
            return full_response


if __name__ == "__main__":
    result = asyncio.run(test_streaming())
    print("\n✅ Streaming test completed successfully!")

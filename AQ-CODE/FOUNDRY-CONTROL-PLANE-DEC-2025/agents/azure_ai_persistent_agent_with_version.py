#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Persistent Agent with Versioning (Fixed)

This is a CORRECTED version of azure_ai_with_existing_agent.py that demonstrates:
1. Creating a persistent agent with versioning using create_version()
2. NOT deleting the agent in the finally block (key fix!)
3. Agent persists and appears in the new Microsoft Foundry portal

Differences from original azure_ai_with_existing_agent.py:
- ❌ Original: Deletes agent in finally block → NOT persistent
- ✅ This version: Comments out deletion → Agent persists

Use this pattern when you want:
- Agent versioning (multiple versions of same agent)
- Persistent agents in production
- Visibility in new Foundry portal (ai.azure.com)

For simpler persistence without versioning, see: azure_ai_persistent_agent_v2.py

PREREQUISITES:
    - Azure CLI: az login
    - Environment variables:
        AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
        AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

USAGE:
    python azure_ai_persistent_agent_with_version.py
"""

import asyncio
import os
from datetime import datetime

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIClient
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity.aio import AzureCliCredential


async def main() -> None:
    print("=" * 70)
    print("Creating Persistent Agent with Versioning")
    print("=" * 70)
    print()
    
    # Create the client
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
    ):
        # List existing agents and versions
        print("📋 Listing existing agents...")
        agents_list = []
        async for agent in project_client.agents.list():
            agents_list.append(agent)
        print(f"   Found {len(agents_list)} existing agent(s)\n")
        
        # Create a new version of the agent
        agent_name = "MyPersistentAgent"
        print(f"🔧 Creating new version of agent: {agent_name}")
        
        azure_ai_agent = await project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                # Setting specific requirements to verify that this agent is used.
                instructions=f"""You are a helpful assistant that persists in Azure AI Foundry.

Created: {datetime.now().isoformat()}

Your purpose is to demonstrate persistent agents with versioning.
Always end each response with [PERSISTENT-v{datetime.now().strftime('%Y%m%d-%H%M%S')}].""",
            ),
        )
        
        print(f"   ✅ Created version:")
        print(f"      Name: {azure_ai_agent.name}")
        print(f"      Version: {azure_ai_agent.version}")
        print(f"      Model: {azure_ai_agent.model}")
        print()
        
        # Use the agent
        chat_client = AzureAIClient(
            project_client=project_client,
            agent_name=azure_ai_agent.name,
            # Property agent_version is required for existing agents.
            # If this property is not configured, the client will try to create a new agent using
            # provided agent_name.
            # It's also possible to leave agent_version empty but set use_latest_version=True.
            # This will pull latest available agent version and use that version for operations.
            agent_version=azure_ai_agent.version,
        )
        
        try:
            print("💬 Testing the agent...")
            async with ChatAgent(
                chat_client=chat_client,
            ) as agent:
                query = "How are you? Confirm you're persistent."
                print(f"   User: {query}")
                result = await agent.run(query)
                # Response that indicates that previously created agent was used:
                # "I'm here and ready to help you! ... [PERSISTENT-vXXX]"
                print(f"   Agent: {result}\n")
                
        finally:
            # ✅ KEY FIX: Comment out the deletion to make the agent persistent!
            #
            # ❌ ORIGINAL (Non-persistent):
            # await project_client.agents.delete_version(
            #     agent_name=azure_ai_agent.name, agent_version=azure_ai_agent.version
            # )
            #
            # ✅ FIXED (Persistent):
            # Don't delete the agent - let it persist in Azure AI
            
            print("=" * 70)
            print("✅ SUCCESS - Persistent Agent Created")
            print("=" * 70)
            print()
            print("📌 Agent Details:")
            print(f"   Name: {azure_ai_agent.name}")
            print(f"   Version: {azure_ai_agent.version}")
            print(f"   Model: {azure_ai_agent.model}")
            print()
            print("🌐 View in Portal:")
            print("   1. Go to https://ai.azure.com")
            print("   2. Select your project")
            print("   3. Navigate to 'Agents' section")
            print(f"   4. Look for agent: {azure_ai_agent.name}")
            print()
            print("🔄 Reuse this agent in your code:")
            print(f"   agent_name = '{azure_ai_agent.name}'")
            print(f"   agent_version = '{azure_ai_agent.version}'")
            print("   chat_client = AzureAIClient(")
            print("       project_client=project_client,")
            print("       agent_name=agent_name,")
            print("       agent_version=agent_version")
            print("   )")
            print()
            print("🗑️  To delete this version later:")
            print(f"   await project_client.agents.delete_version(")
            print(f"       agent_name='{azure_ai_agent.name}',")
            print(f"       agent_version='{azure_ai_agent.version}'")
            print(f"   )")
            print()


if __name__ == "__main__":
    asyncio.run(main())

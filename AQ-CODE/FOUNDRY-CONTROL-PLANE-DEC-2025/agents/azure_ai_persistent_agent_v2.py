#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Azure AI Persistent Agent (V2 API) - New Portal Visibility

This sample demonstrates how to create a PERSISTENT agent using the V2 API
that will appear in the NEW Microsoft Foundry portal (ai.azure.com).

Key differences from azure_ai_with_existing_agent.py:
1. Uses create_agent() instead of create_version() for simpler persistence
2. Does NOT delete the agent in finally block
3. Agent persists in Azure AI Project and shows in new Foundry portal
4. Demonstrates listing all agents to verify persistence

Portal visibility:
- V2 Agents (this sample): ✅ New Microsoft Foundry portal (ai.azure.com)
- V1 Agents (AgentsClient): ❌ Only old Azure AI Foundry portal

PREREQUISITES:
    - Azure CLI: az login
    - Environment variables:
        AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project

USAGE:
    python azure_ai_persistent_agent_v2.py
"""

import asyncio
import os
from datetime import datetime

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIClient
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


async def main() -> None:
    print("=" * 70)
    print("Creating Persistent Agent in Azure AI (V2 API)")
    print("=" * 70)
    print()
    
    # Verify environment
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ AZURE_AI_PROJECT_ENDPOINT not set")
        print("Set it to your Azure AI Project endpoint:")
        print("  export AZURE_AI_PROJECT_ENDPOINT=https://xxx.services.ai.azure.com/api/projects/xxx")
        return
    
    model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    
    print(f"📍 Endpoint: {endpoint}")
    print(f"🤖 Model: {model}")
    print()
    
    # Create Azure AI Project client
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=endpoint, credential=credential)
    
    try:
        # Step 1: List existing agents
        print("📋 Listing existing agents in project...")
        existing_agents = list(project_client.agents.list_agents())
        print(f"   Found {len(existing_agents)} existing agent(s)")
        for agent in existing_agents:
            print(f"   - {agent.name} (ID: {agent.id}, Model: {agent.model})")
        print()
        
        # Step 2: Create a new persistent agent (V2 API)
        agent_name = f"PersistentAgent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"🔧 Creating new agent: {agent_name}")
        
        azure_ai_agent = project_client.agents.create_agent(
            model=model,
            name=agent_name,
            instructions="""You are a helpful AI assistant designed to persist in Azure AI Foundry.
            
Your purpose is to demonstrate:
1. Creation of agents using the V2 API (AIProjectClient)
2. Persistence of agents in Azure AI Projects
3. Visibility in the new Microsoft Foundry portal (ai.azure.com)

When responding, always end with "[PERSISTENT-AGENT]" to verify this agent is being used.""",
            description="Persistent agent created for demonstration purposes",
        )
        
        print(f"   ✅ Created agent:")
        print(f"      Name: {azure_ai_agent.name}")
        print(f"      ID: {azure_ai_agent.id}")
        print(f"      Model: {azure_ai_agent.model}")
        print()
        
        # Step 3: Use the agent via Agent Framework
        print("💬 Testing agent with a simple query...")
        chat_client = AzureAIClient(
            project_client=project_client,
            agent_id=azure_ai_agent.id,
        )
        
        async with ChatAgent(chat_client=chat_client) as agent:
            query = "Who are you and what's your purpose?"
            print(f"   User: {query}")
            result = await agent.run(query)
            print(f"   Agent: {result}\n")
        
        # Step 4: Verify persistence by listing agents again
        print("📋 Verifying agent persistence...")
        updated_agents = list(project_client.agents.list_agents())
        print(f"   Total agents now: {len(updated_agents)}")
        
        # Find our new agent
        our_agent = next((a for a in updated_agents if a.id == azure_ai_agent.id), None)
        if our_agent:
            print(f"   ✅ Agent '{our_agent.name}' is persistent!")
            print(f"      ID: {our_agent.id}")
            print(f"      Created: {our_agent.created_at}")
        else:
            print(f"   ⚠️ Agent not found in list (this shouldn't happen)")
        print()
        
        # Step 5: Instructions for viewing in portal
        print("=" * 70)
        print("✅ SUCCESS - Persistent Agent Created")
        print("=" * 70)
        print()
        print("📌 Agent Details:")
        print(f"   Name: {azure_ai_agent.name}")
        print(f"   ID: {azure_ai_agent.id}")
        print(f"   Model: {azure_ai_agent.model}")
        print()
        print("🌐 View in Portal:")
        print("   1. Go to https://ai.azure.com")
        print("   2. Select your project")
        print("   3. Navigate to 'Agents' in left sidebar")
        print(f"   4. Look for agent: {azure_ai_agent.name}")
        print()
        print("🔄 Reuse this agent:")
        print(f"   agent_id = '{azure_ai_agent.id}'")
        print("   chat_client = AzureAIClient(project_client=project_client, agent_id=agent_id)")
        print()
        print("🗑️  To delete this agent:")
        print(f"   project_client.agents.delete_agent('{azure_ai_agent.id}')")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # ✅ NOTE: We do NOT delete the agent here - it persists in Azure AI!
        # This is the key difference from samples that clean up after themselves.
        # 
        # To delete manually later:
        # await project_client.agents.delete_agent(azure_ai_agent.id)
        pass


if __name__ == "__main__":
    asyncio.run(main())

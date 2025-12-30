#!/usr/bin/env python3
"""
Update workflow models in Cosmos DB from gpt-4o to gpt-4.1
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


async def update_workflow_models():
    """Update all workflows to use gpt-4.1 instead of gpt-4o"""
    
    # Get configuration
    cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
    cosmos_key = os.getenv("COSMOS_DB_KEY", "")
    database_name = os.getenv("COSMOS_DB_DATABASE", "workflows")
    container_name = os.getenv("COSMOS_DB_CONTAINER", "workflow_definitions")
    
    if not cosmos_endpoint:
        print("❌ COSMOS_DB_ENDPOINT not set")
        return
    
    print(f"🔗 Connecting to Cosmos DB: {cosmos_endpoint}")
    print(f"📁 Database: {database_name}")
    print(f"📦 Container: {container_name}")
    
    # Choose authentication method
    if cosmos_key and cosmos_key.strip():
        print("🔑 Using key-based authentication")
        client = CosmosClient(cosmos_endpoint, credential=cosmos_key)
    else:
        print("🔐 Using Azure AD authentication")
        credential = DefaultAzureCredential()
        client = CosmosClient(cosmos_endpoint, credential=credential)
    
    try:
        # Get database and container
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        # Query all workflows
        print("\n🔍 Querying workflows...")
        query = "SELECT * FROM c WHERE c.type = 'workflow'"
        
        workflows = []
        async for item in container.query_items(query=query):
            workflows.append(item)
        
        print(f"📊 Found {len(workflows)} workflows")
        
        # Update each workflow
        updated_count = 0
        for workflow in workflows:
            workflow_id = workflow.get("id")
            current_model = workflow.get("agent_config", {}).get("model", "unknown")
            
            if current_model == "gpt-4o":
                print(f"\n✏️  Updating {workflow_id}")
                print(f"   Current model: {current_model}")
                
                # Update model
                workflow["agent_config"]["model"] = "gpt-4.1"
                
                # Update timestamp
                from datetime import datetime
                workflow["metadata"]["updated_at"] = datetime.utcnow().isoformat() + "Z"
                
                # Replace item in Cosmos
                await container.upsert_item(workflow)
                
                print(f"   ✅ Updated to: gpt-4.1")
                updated_count += 1
            else:
                print(f"\n⏭️  Skipping {workflow_id} (model: {current_model})")
        
        print(f"\n✅ Updated {updated_count} workflows")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(update_workflow_models())

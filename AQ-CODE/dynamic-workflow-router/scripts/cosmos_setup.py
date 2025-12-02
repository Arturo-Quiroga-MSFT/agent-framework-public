#!/usr/bin/env python3
"""
Cosmos DB Setup Script

Initialize Cosmos DB with database, container, and sample workflows.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
COSMOS_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_DB_KEY")
DATABASE_NAME = os.getenv("COSMOS_DB_DATABASE", "workflows")
CONTAINER_NAME = os.getenv("COSMOS_DB_CONTAINER", "workflow_definitions")


async def setup_cosmos_db():
    """Setup Cosmos DB database and container."""
    print("=" * 80)
    print("🔧 Cosmos DB Setup")
    print("=" * 80)
    print()
    
    if not COSMOS_ENDPOINT or not COSMOS_KEY:
        print("❌ Error: COSMOS_DB_ENDPOINT and COSMOS_DB_KEY must be set")
        print("   Copy .env.example to .env and configure")
        return False
    
    print(f"📍 Endpoint: {COSMOS_ENDPOINT}")
    print(f"📁 Database: {DATABASE_NAME}")
    print(f"📦 Container: {CONTAINER_NAME}")
    print()
    
    # Create client
    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
    
    try:
        # Create database
        print("Creating database...")
        database = await client.create_database_if_not_exists(id=DATABASE_NAME)
        print(f"✅ Database '{DATABASE_NAME}' ready")
        
        # Create container with hierarchical partition key
        print("Creating container with hierarchical partition keys...")
        partition_key_def = {
            "paths": ["/partitionKey"],
            "kind": "MultiHash",
            "version": 2
        }
        
        container = await database.create_container_if_not_exists(
            id=CONTAINER_NAME,
            partition_key=partition_key_def,
            offer_throughput=400  # Minimum throughput
        )
        print(f"✅ Container '{CONTAINER_NAME}' ready")
        
        # Load and insert sample workflows
        print("\nLoading sample workflows...")
        schemas_dir = Path(__file__).parent.parent / "schemas" / "examples"
        
        if not schemas_dir.exists():
            print(f"⚠️  Schemas directory not found: {schemas_dir}")
            return True
        
        workflow_files = list(schemas_dir.glob("*.json"))
        print(f"Found {len(workflow_files)} workflow files")
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow = json.load(f)
                
                # Upsert workflow (create or replace)
                await container.upsert_item(body=workflow)
                print(f"✅ Loaded: {workflow['id']}")
            
            except Exception as e:
                print(f"⚠️  Error loading {workflow_file.name}: {e}")
        
        print()
        print("=" * 80)
        print("✅ Cosmos DB setup complete!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Verify workflows in Azure portal")
        print("  2. Run: python examples/basic_routing.py")
        print("  3. Or launch UI: streamlit run ui/streamlit_workflow_ui.py")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await client.close()


if __name__ == "__main__":
    success = asyncio.run(setup_cosmos_db())
    sys.exit(0 if success else 1)

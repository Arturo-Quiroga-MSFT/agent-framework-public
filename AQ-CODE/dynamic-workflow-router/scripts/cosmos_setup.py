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
from azure.identity.aio import DefaultAzureCredential
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
    
    if not COSMOS_ENDPOINT:
        print("❌ Error: COSMOS_DB_ENDPOINT must be set")
        print("   Configure it in .env")
        return False
    
    print(f"📍 Endpoint: {COSMOS_ENDPOINT}")
    print(f"📁 Database: {DATABASE_NAME}")
    print(f"📦 Container: {CONTAINER_NAME}")
    print()
    
    # Create client
    credential = None
    use_key_auth = bool(COSMOS_KEY and COSMOS_KEY.strip())
    if use_key_auth:
        print("🔑 Using key-based authentication")
        client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
    else:
        print("🔐 Using Azure AD authentication (Cosmos native RBAC)")
        credential = DefaultAzureCredential()
        client = CosmosClient(COSMOS_ENDPOINT, credential=credential)
    
    try:
        if use_key_auth:
            # Key auth typically implies Local Authorization is enabled.
            # Create database + container via data-plane.
            print("Creating database...")
            database = await client.create_database_if_not_exists(id=DATABASE_NAME)
            print(f"✅ Database '{DATABASE_NAME}' ready")

            # Create container with hierarchical partition key
            print("Creating container with hierarchical partition keys...")
            partition_key_def = {
                "paths": ["/partitionKey"],
                "kind": "MultiHash",
                "version": 2,
            }

            container = await database.create_container_if_not_exists(
                id=CONTAINER_NAME,
                partition_key=partition_key_def,
                offer_throughput=400,  # Minimum throughput
            )
            print(f"✅ Container '{CONTAINER_NAME}' ready")
        else:
            # In Cosmos native RBAC mode, principals often don't have permissions to create
            # databases/containers. Validate they exist, then proceed to load workflows.
            print("Validating database/container exist...")
            database = client.get_database_client(DATABASE_NAME)
            container = database.get_container_client(CONTAINER_NAME)
            try:
                await database.read()
                await container.read()
            except Exception as e:
                print(f"❌ Database/container not found or not accessible: {e}")
                print("\nCreate them first (example):")
                print(f"  az cosmosdb sql database create -g <rg> -a <account> -n {DATABASE_NAME}")
                print(
                    f"  az cosmosdb sql container create -g <rg> -a <account> -d {DATABASE_NAME} -n {CONTAINER_NAME} -p /category"
                )
                return False
        
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
        if credential is not None:
            await credential.close()


if __name__ == "__main__":
    success = asyncio.run(setup_cosmos_db())
    sys.exit(0 if success else 1)

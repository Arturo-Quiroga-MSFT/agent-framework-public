#!/usr/bin/env python3
"""
Azure OpenAI V1 Assistants Cleanup Script

This script lists and deletes V1 Assistants created through the Azure OpenAI API
(the "legacy" Assistants API). These show up in the old Azure AI Foundry portal
but NOT in the new Microsoft Foundry portal.

V1 Assistants have IDs like: asst_CsBpSN8eof0hEnUmOLSOG6Db
V2 Agents (new) are managed through Azure AI Projects SDK.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Try OpenAI SDK (works with Azure OpenAI)
try:
    from openai import AzureOpenAI
except ImportError:
    print("❌ OpenAI SDK not found. Install with: pip install openai")
    exit(1)


def get_azure_openai_client() -> AzureOpenAI:
    """Create Azure OpenAI client for Assistants API."""
    
    # Try different environment variable patterns
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    # Fall back to AI Project endpoint pattern
    if not endpoint:
        project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
        # Extract the OpenAI endpoint from project endpoint
        # e.g., https://xxx.services.ai.azure.com/api/projects/xxx
        # OpenAI endpoint: https://xxx.openai.azure.com
        if "services.ai.azure.com" in project_endpoint:
            # Need to use the Azure OpenAI resource directly
            print("⚠️  Using AI Foundry endpoint - may need separate Azure OpenAI endpoint")
    
    if not endpoint or not api_key:
        print("""
❌ Azure OpenAI credentials not found.

V1 Assistants require direct Azure OpenAI API access.
Please set these environment variables:

  AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
  AZURE_OPENAI_API_KEY=your-api-key

You can find these in Azure Portal:
  1. Go to your Azure OpenAI resource
  2. Keys and Endpoint section
""")
        return None
    
    return AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-05-01-preview"  # Assistants API version
    )


def list_v1_assistants(client: AzureOpenAI) -> list:
    """List all V1 assistants."""
    assistants = []
    
    try:
        # Paginate through all assistants
        response = client.beta.assistants.list(limit=100)
        assistants.extend(response.data)
        
        while response.has_more:
            response = client.beta.assistants.list(
                limit=100,
                after=response.data[-1].id
            )
            assistants.extend(response.data)
            
    except Exception as e:
        print(f"❌ Error listing assistants: {e}")
        return []
    
    return assistants


def delete_assistant(client: AzureOpenAI, assistant_id: str) -> bool:
    """Delete a single assistant."""
    try:
        client.beta.assistants.delete(assistant_id)
        return True
    except Exception as e:
        print(f"  ❌ Failed to delete {assistant_id}: {e}")
        return False


def main():
    print("=" * 60)
    print("  Azure OpenAI V1 Assistants Cleanup")
    print("=" * 60)
    print()
    
    client = get_azure_openai_client()
    if not client:
        return
    
    print("📋 Fetching V1 assistants...")
    assistants = list_v1_assistants(client)
    
    if not assistants:
        print("✅ No V1 assistants found (or unable to list them)")
        return
    
    print(f"\n Found {len(assistants)} V1 assistant(s):\n")
    print(f"{'#':<4} {'Name':<25} {'ID':<35} {'Model':<15} {'Created'}")
    print("-" * 100)
    
    for i, asst in enumerate(assistants, 1):
        name = asst.name or "(unnamed)"
        name = name[:24] if len(name) > 24 else name
        created = asst.created_at
        print(f"{i:<4} {name:<25} {asst.id:<35} {asst.model:<15} {created}")
    
    print()
    print("=" * 60)
    print("  Options:")
    print("=" * 60)
    print("  1. Delete ALL assistants")
    print("  2. Delete by name pattern (e.g., 'DBA_UI', 'InteractiveDBA')")
    print("  3. Keep specific assistants, delete the rest")
    print("  4. Exit without deleting")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        confirm = input(f"\n⚠️  Delete ALL {len(assistants)} assistants? Type 'DELETE ALL' to confirm: ")
        if confirm == "DELETE ALL":
            deleted = 0
            for asst in assistants:
                if delete_assistant(client, asst.id):
                    print(f"  ✅ Deleted: {asst.name or asst.id}")
                    deleted += 1
            print(f"\n✅ Deleted {deleted}/{len(assistants)} assistants")
        else:
            print("Cancelled.")
            
    elif choice == "2":
        pattern = input("Enter name pattern to delete (e.g., 'DBA_UI'): ").strip()
        if not pattern:
            print("No pattern entered. Cancelled.")
            return
            
        matches = [a for a in assistants if pattern.lower() in (a.name or "").lower()]
        print(f"\nFound {len(matches)} assistants matching '{pattern}':")
        for a in matches:
            print(f"  - {a.name} ({a.id})")
        
        if matches:
            confirm = input(f"\nDelete these {len(matches)} assistants? (yes/no): ")
            if confirm.lower() == "yes":
                deleted = 0
                for asst in matches:
                    if delete_assistant(client, asst.id):
                        print(f"  ✅ Deleted: {asst.name or asst.id}")
                        deleted += 1
                print(f"\n✅ Deleted {deleted}/{len(matches)} assistants")
            else:
                print("Cancelled.")
                
    elif choice == "3":
        keep_names = input("Enter names to KEEP (comma-separated): ").strip()
        keep_list = [n.strip() for n in keep_names.split(",") if n.strip()]
        
        if not keep_list:
            print("No names entered. Cancelled.")
            return
            
        to_delete = [a for a in assistants if a.name not in keep_list]
        to_keep = [a for a in assistants if a.name in keep_list]
        
        print(f"\nWill KEEP {len(to_keep)} assistants:")
        for a in to_keep:
            print(f"  ✅ {a.name}")
            
        print(f"\nWill DELETE {len(to_delete)} assistants:")
        for a in to_delete[:10]:
            print(f"  ❌ {a.name or a.id}")
        if len(to_delete) > 10:
            print(f"  ... and {len(to_delete) - 10} more")
        
        confirm = input(f"\nProceed with deletion? (yes/no): ")
        if confirm.lower() == "yes":
            deleted = 0
            for asst in to_delete:
                if delete_assistant(client, asst.id):
                    print(f"  ✅ Deleted: {asst.name or asst.id}")
                    deleted += 1
            print(f"\n✅ Deleted {deleted}/{len(to_delete)} assistants")
        else:
            print("Cancelled.")
            
    else:
        print("Exiting without changes.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Map Azure AI Foundry Agents to their Entra ID Agent Identities (REST API Version)

This script uses Azure REST API directly to retrieve agent information.

Usage:
    python map_agent_identities_rest.py

Prerequisites:
    - Azure CLI installed and logged in (az login)
    - pip install azure-identity requests python-dotenv
"""

import os
import json
import requests
from datetime import datetime
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def parse_foundry_endpoint(endpoint):
    """Parse Foundry project endpoint to extract components."""
    # Handle both old ARM format and new Foundry format
    # New format: https://<region>.services.ai.azure.com/api/projects/<project-name>
    # Old format: https://<region>.api.azureml.ms/rp/workspaces/subscriptions/<sub>/...
    
    if 'services.ai.azure.com' in endpoint:
        # New Foundry format
        parts = endpoint.rstrip('/').split('/')
        region = endpoint.split('//')[1].split('.')[0]
        project_name = parts[-1]
        
        print(f"   Detected new Foundry format")
        print(f"   Region: {region}")
        print(f"   Project: {project_name}")
        
        return {
            'type': 'foundry',
            'region': region,
            'project_name': project_name,
            'base_url': endpoint
        }
    else:
        # Old ARM format
        parts = endpoint.split('/')
        if 'subscriptions' in parts:
            sub_idx = parts.index('subscriptions') + 1
            rg_idx = parts.index('resourceGroups') + 1
            ws_idx = parts.index('workspaces') + 1
            
            return {
                'type': 'arm',
                'subscription_id': parts[sub_idx],
                'resource_group': parts[rg_idx],
                'workspace_name': parts[ws_idx]
            }
    
    return None

def get_agents_via_foundry_api(endpoint_info, credential):
    """Get agents using Foundry API."""
    
    print(f"\n📡 Calling Foundry Agents API...")
    
    # Get token for Foundry
    token = credential.get_token("https://ml.azure.com/.default").token
    
    # Foundry agents API endpoint
    base_url = endpoint_info['base_url'].rstrip('/')
    agents_url = f"{base_url}/agents"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"   URL: {agents_url}")
    
    try:
        response = requests.get(agents_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            agents = data.get('value', data.get('agents', []))
            print(f"   ✅ Retrieved {len(agents)} agents")
            return agents
        else:
            print(f"   ❌ API call failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def get_agents_via_arm_api(endpoint_info, credential):
    """Get agents using ARM API."""
    
    print(f"\n📡 Calling Azure Resource Manager API...")
    
    token = credential.get_token("https://management.azure.com/.default").token
    
    subscription_id = endpoint_info['subscription_id']
    resource_group = endpoint_info['resource_group']
    workspace_name = endpoint_info['workspace_name']
    
    # Try different API versions
    api_versions = [
        "2024-10-01-preview",
        "2024-07-01-preview",
        "2024-04-01-preview"
    ]
    
    for api_version in api_versions:
        agents_url = (
            f"https://management.azure.com/subscriptions/{subscription_id}"
            f"/resourceGroups/{resource_group}"
            f"/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"
            f"/agents?api-version={api_version}"
        )
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"   Trying API version: {api_version}")
        
        try:
            response = requests.get(agents_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                agents = data.get('value', [])
                print(f"   ✅ Retrieved {len(agents)} agents")
                return agents
            elif response.status_code == 404:
                print(f"   ⚠️  API version not supported")
                continue
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    return []

def extract_agent_info(agent_data):
    """Extract relevant info from agent data."""
    
    # Handle nested properties structure
    properties = agent_data.get('properties', {})
    
    agent_info = {
        "agent_name": agent_data.get('name', properties.get('name', 'Unknown')),
        "agent_id": agent_data.get('id', 'N/A'),
        "model": properties.get('model', 'N/A'),
        "created_at": properties.get('createdAt', agent_data.get('systemData', {}).get('createdAt', 'N/A')),
        "agent_identity_id": None,
        "object_id": None,
        "blueprint_id": None,
        "status": "Unknown"
    }
    
    # Look for agent identity in various locations
    agent_identity = (
        properties.get('agentIdentityId') or
        properties.get('agentIdentity') or
        agent_data.get('agentIdentityId') or
        agent_data.get('identity', {}).get('principalId')
    )
    
    if agent_identity:
        agent_info["agent_identity_id"] = agent_identity
        agent_info["object_id"] = agent_identity
        agent_info["status"] = "Published with Identity"
    else:
        agent_info["status"] = "Draft (Shared Identity)"
    
    # Look for blueprint ID
    blueprint_id = (
        properties.get('blueprintId') or
        properties.get('agentBlueprintId') or
        agent_data.get('blueprintId')
    )
    
    if blueprint_id:
        agent_info["blueprint_id"] = blueprint_id
    
    return agent_info

def display_mapping(agent_mapping, shared_identity=None):
    """Display the agent to identity mapping in a formatted table."""
    
    print("\n" + "=" * 120)
    print("🎯 AGENT IDENTITY MAPPING")
    print("=" * 120)
    
    if shared_identity:
        print(f"\n📦 Project Shared Identity (for unpublished agents):")
        print(f"   Object ID: {shared_identity}")
        print()
    
    if not agent_mapping:
        print("\n⚠️  No agents found")
        return
    
    # Header
    print(f"{'Agent Name':<35} {'Status':<28} {'Object ID':<40}")
    print("-" * 120)
    
    # Rows
    for agent in agent_mapping:
        name = agent['agent_name'][:33]
        status = agent['status'][:26]
        obj_id = agent['object_id'] if agent['object_id'] else "N/A (using shared identity)"
        
        print(f"{name:<35} {status:<28} {obj_id:<40}")
    
    print("=" * 120)
    print(f"\n✅ Found {len(agent_mapping)} agent(s)")

def save_mapping_to_file(agent_mapping, shared_identity=None):
    """Save the mapping to a JSON file."""
    
    output = {
        "generated_at": datetime.now().isoformat(),
        "shared_project_identity": shared_identity,
        "agents": agent_mapping
    }
    
    filename = f"agent_identity_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Mapping saved to: {filename}")
    return filename

def generate_rbac_commands(agent_mapping):
    """Generate example RBAC assignment commands."""
    
    published_agents = [a for a in agent_mapping if a['object_id'] and a['object_id'] != "N/A"]
    
    if not published_agents:
        print("\n⚠️  No published agents with unique identities found.")
        print("   Publish your agents in the Foundry portal to get individual agent identities.")
        return
    
    print("\n" + "=" * 120)
    print("🔐 EXAMPLE RBAC ASSIGNMENT COMMANDS")
    print("=" * 120)
    print("\nUse these commands to grant permissions to your agents:\n")
    
    for agent in published_agents:
        print(f"# {agent['agent_name']}")
        print(f"az role assignment create \\")
        print(f"  --assignee {agent['object_id']} \\")
        print(f"  --role \"Storage Blob Data Reader\" \\")
        print(f"  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>")
        print()

def main():
    print("=" * 120)
    print("🤖 Azure AI Foundry Agent Identity Mapper (REST API)")
    print("=" * 120)
    
    # Get endpoint
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    if not endpoint:
        print("\n🔧 Foundry Project Configuration")
        print("=" * 60)
        print("\nEnter your Foundry project endpoint:")
        print("Format: https://<region>.services.ai.azure.com/api/projects/<project-name>")
        endpoint = input("\nEndpoint: ").strip()
        
        save = input("\nSave to .env file? (y/n): ").strip().lower()
        if save == 'y':
            with open('.env', 'a') as f:
                f.write(f"\nFOUNDRY_PROJECT_ENDPOINT={endpoint}\n")
            print("✅ Saved to .env")
    
    # Parse endpoint
    endpoint_info = parse_foundry_endpoint(endpoint)
    
    if not endpoint_info:
        print("\n❌ Could not parse endpoint format")
        return
    
    # Authenticate
    print("\n🔐 Authenticating to Azure...")
    credential = DefaultAzureCredential()
    
    # Get agents based on endpoint type
    if endpoint_info['type'] == 'foundry':
        agents_data = get_agents_via_foundry_api(endpoint_info, credential)
    else:
        agents_data = get_agents_via_arm_api(endpoint_info, credential)
    
    if not agents_data:
        print("\n❌ No agents found or API call failed")
        print("\nTroubleshooting:")
        print("1. Verify you're logged in: az login")
        print("2. Check the endpoint URL is correct")
        print("3. Ensure you have Reader permissions on the project")
        print("4. Verify agents exist in the Foundry portal")
        return
    
    # Extract agent info
    print("\n🔍 Processing agent data...")
    agent_mapping = [extract_agent_info(agent) for agent in agents_data]
    
    # Display results
    display_mapping(agent_mapping)
    
    # Save to file
    save_mapping_to_file(agent_mapping)
    
    # Generate RBAC commands
    generate_rbac_commands(agent_mapping)
    
    print("\n" + "=" * 120)
    print("✨ Done! You can now use these Object IDs in the Entra ID portal.")
    print("=" * 120)
    print("\n💡 Next steps:")
    print("   1. Search for these Object IDs in Entra ID → Agent ID → All agent identities")
    print("   2. Assign RBAC roles for Azure resource access")
    print("   3. Configure conditional access policies")
    print("   4. Add custom security attributes for better identification\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

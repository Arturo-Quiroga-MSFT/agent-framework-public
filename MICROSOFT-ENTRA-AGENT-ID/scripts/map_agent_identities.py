#!/usr/bin/env python3
"""
Map Azure AI Foundry Agents to their Entra ID Agent Identities

This script queries your Foundry project and retrieves the mapping between
agent names and their assigned Entra ID agent identity Object IDs.

Usage:
    python map_agent_identities.py

Prerequisites:
    - Azure CLI installed and logged in (az login)
    - pip install azure-ai-projects azure-identity python-dotenv
"""

import os
import json
from datetime import datetime
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_project_endpoint():
    """Get Foundry project endpoint from environment or prompt user."""
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    
    if not endpoint:
        print("\n🔧 Foundry Project Configuration")
        print("=" * 60)
        print("\nYour Foundry project endpoint looks like:")
        print("https://<region>.api.azureml.ms/rp/workspaces/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<project-name>")
        print("\nOr from Azure portal:")
        print("Go to your Foundry project → Overview → Copy 'Project endpoint'\n")
        
        endpoint = input("Enter your Foundry project endpoint: ").strip()
        
        # Save to .env for future use
        save = input("\nSave to .env file for future use? (y/n): ").strip().lower()
        if save == 'y':
            with open('.env', 'a') as f:
                f.write(f"\nFOUNDRY_PROJECT_ENDPOINT={endpoint}\n")
            print("✅ Saved to .env file")
    
    return endpoint

def list_agents_with_identities(project_endpoint):
    """List all agents in the Foundry project with their agent identities."""
    
    print("\n🔐 Authenticating to Azure...")
    credential = DefaultAzureCredential()
    
    print(f"📡 Connecting to Foundry project...")
    print(f"   Endpoint: {project_endpoint[:50]}...")
    
    try:
        # Create project client
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=credential
        )
        
        print("\n🤖 Retrieving agents...")
        
        # List all agents - try different methods
        agents = []
        try:
            # Try the list method
            agents = list(project_client.agents.list())
        except AttributeError:
            try:
                # Try alternative method
                agents = project_client.agents.list_agents()
            except:
                pass
        
        if not agents:
            print("\n⚠️  Could not list agents using standard methods.")
            print("   Trying alternative approach...")
            
            # Try to get agents via REST API directly
            import requests
            token = credential.get_token("https://ml.azure.com/.default").token
            
            # Extract components from endpoint
            parts = project_endpoint.split('/')
            if 'subscriptions' in parts:
                sub_idx = parts.index('subscriptions') + 1
                rg_idx = parts.index('resourceGroups') + 1
                ws_idx = parts.index('workspaces') + 1
                
                subscription_id = parts[sub_idx]
                resource_group = parts[rg_idx]
                workspace_name = parts[ws_idx]
                
                # Try REST API
                api_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}/agents?api-version=2024-07-01-preview"
                
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(api_url, headers=headers)
                
                if response.status_code == 200:
                    agents_data = response.json().get('value', [])
                    print(f"   ✅ Found {len(agents_data)} agents via REST API")
                else:
                    print(f"   ❌ REST API call failed: {response.status_code}")
                    agents_data = []
        else:
            agents_data = [{"name": a.name, "id": a.id, "properties": vars(a)} for a in agents]
        
        agent_mapping = []
        
        for agent in agents_data:
            # Handle both SDK object and dict responses
            if isinstance(agent, dict):
                agent_name = agent.get('name', 'Unknown')
                agent_id = agent.get('id', 'Unknown')
                properties = agent.get('properties', {})
            else:
                agent_name = getattr(agent, 'name', 'Unknown')
                agent_id = getattr(agent, 'id', 'Unknown')
                properties = vars(agent) if hasattr(agent, '__dict__') else {}
            
            agent_info = {
                "agent_name": agent_name,
                "agent_id": agent_id,
                "model": properties.get('model', 'N/A'),
                "created_at": properties.get('createdAt', properties.get('created_at', 'N/A')),
                "agent_identity_id": None,
                "object_id": None,
                "status": "Unknown"
            }
            
            # Try to get agent identity information
            try:
                # Check for agent identity in various possible locations
                if isinstance(properties, dict):
                    agent_info["agent_identity_id"] = properties.get('agentIdentityId') or properties.get('agent_identity_id')
                    agent_info["object_id"] = agent_info["agent_identity_id"]
                    agent_info["status"] = "Published with Identity" if agent_info["agent_identity_id"] else "Draft (Shared Identity)"
                elif hasattr(properties, 'agent_identity_id'):
                    agent_info["agent_identity_id"] = properties.agent_identity_id
                    agent_info["object_id"] = properties.agent_identity_id
                    agent_info["status"] = "Published with Identity"
                else:
                    agent_info["status"] = "Draft (Shared Identity)"
                    
            except Exception as e:
                agent_info["status"] = f"Error: {str(e)[:50]}"
            
            agent_mapping.append(agent_info)
        
        return agent_mapping
        
    except Exception as e:
        print(f"\n❌ Error connecting to Foundry: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you're logged in: az login")
        print("2. Verify the project endpoint is correct")
        print("3. Check you have Reader permissions on the Foundry project")
        return None

def get_project_shared_identity(project_endpoint):
    """Get the shared project-level agent identity."""
    try:
        credential = DefaultAzureCredential()
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=credential
        )
        
        # Try to get project properties
        # Note: This might need adjustment based on actual SDK
        if hasattr(project_client, 'get_properties'):
            props = project_client.get_properties()
            return props.get('agentIdentityId')
        
    except Exception as e:
        print(f"Note: Could not retrieve shared project identity: {e}")
    
    return None

def display_mapping(agent_mapping, shared_identity=None):
    """Display the agent to identity mapping in a formatted table."""
    
    print("\n" + "=" * 120)
    print("🎯 AGENT IDENTITY MAPPING")
    print("=" * 120)
    
    if shared_identity:
        print(f"\n📦 Project Shared Identity (for unpublished agents):")
        print(f"   Object ID: {shared_identity}")
        print()
    
    # Header
    print(f"{'Agent Name':<30} {'Status':<25} {'Object ID':<40}")
    print("-" * 120)
    
    # Rows
    for agent in agent_mapping:
        name = agent['agent_name'][:28]
        status = agent['status'][:23]
        obj_id = agent['object_id'] if agent['object_id'] else "N/A (using shared identity)"
        
        print(f"{name:<30} {status:<25} {obj_id:<40}")
    
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
    
    print("\n" + "=" * 120)
    print("🔐 EXAMPLE RBAC ASSIGNMENT COMMANDS")
    print("=" * 120)
    print("\nUse these commands to grant permissions to your agents:\n")
    
    for agent in agent_mapping:
        if agent['object_id'] and agent['object_id'] != "N/A":
            print(f"# {agent['agent_name']}")
            print(f"az role assignment create \\")
            print(f"  --assignee {agent['object_id']} \\")
            print(f"  --role \"Storage Blob Data Reader\" \\")
            print(f"  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>")
            print()

def main():
    print("=" * 120)
    print("🤖 Azure AI Foundry Agent Identity Mapper")
    print("=" * 120)
    
    # Get project endpoint
    project_endpoint = get_project_endpoint()
    
    # Get shared identity
    shared_identity = get_project_shared_identity(project_endpoint)
    
    # List agents and their identities
    agent_mapping = list_agents_with_identities(project_endpoint)
    
    if not agent_mapping:
        print("\n❌ Failed to retrieve agent information")
        return
    
    if not agent_mapping:
        print("\n⚠️  No agents found in the project")
        return
    
    # Display mapping
    display_mapping(agent_mapping, shared_identity)
    
    # Save to file
    save_mapping_to_file(agent_mapping, shared_identity)
    
    # Generate RBAC commands
    generate_rbac_commands(agent_mapping)
    
    print("\n" + "=" * 120)
    print("✨ Done! You can now use these Object IDs in the Entra ID portal.")
    print("=" * 120)
    print("\n💡 Tips:")
    print("   1. Use the Object IDs to assign RBAC roles for Azure resource access")
    print("   2. Configure conditional access policies targeting these identities")
    print("   3. Monitor agent activity in Entra ID sign-in logs")
    print("   4. Add custom security attributes in Entra ID for better organization\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

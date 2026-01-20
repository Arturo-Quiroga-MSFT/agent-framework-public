#!/usr/bin/env python3
"""
Agent Registry Testing Script
=============================
This script tests agent registration with minimal and full metadata.
Easier for troubleshooting than notebook format.

Prerequisites:
    - .env file with TENANT_ID, AGENT_CLIENT_ID, AGENT_CLIENT_SECRET
    - Graph API permissions: AgentInstance.ReadWrite.All
    
Usage:
    python test_agent_registry.py
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential

# ============================================================================
# CONFIGURATION
# ============================================================================

def load_config():
    """Load configuration from .env file."""
    print("="*70)
    print("STEP 1: Loading Configuration")
    print("="*70)
    
    # Find .env file
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print(f"❌ .env file not found at: {env_path}")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("AGENT_CLIENT_ID")
    client_secret = os.getenv("AGENT_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        print("❌ Missing required environment variables")
        print("   Required: TENANT_ID, AGENT_CLIENT_ID, AGENT_CLIENT_SECRET")
        sys.exit(1)
    
    print(f"✓ Loaded .env from: {env_path}")
    print(f"✓ Tenant ID: {tenant_id}")
    print(f"✓ Client ID: {client_id}")
    print(f"✓ Client Secret: {'*' * 10}...{client_secret[-4:]}")
    print()
    
    return {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "client_secret": client_secret
    }


# ============================================================================
# GRAPH API CLIENT
# ============================================================================

def create_graph_client(config):
    """Create authenticated Graph API client."""
    print("="*70)
    print("STEP 2: Creating Graph API Client")
    print("="*70)
    
    try:
        credential = ClientSecretCredential(
            tenant_id=config["tenant_id"],
            client_id=config["client_id"],
            client_secret=config["client_secret"]
        )
        print("✓ Created credential object")
        
        # Test token acquisition
        token = credential.get_token("https://graph.microsoft.com/.default")
        print(f"✓ Acquired access token")
        print(f"  Token length: {len(token.token)} chars")
        print(f"  Expires at: {token.expires_on}")
        print()
        
        return credential
    
    except Exception as e:
        print(f"❌ Failed to create Graph client: {e}")
        sys.exit(1)


def get_graph_token(credential):
    """Get Graph API access token."""
    token = credential.get_token("https://graph.microsoft.com/.default")
    return token.token


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_response(response, show_full_body=False):
    """Print HTTP response details."""
    print(f"  HTTP Status: {response.status_code}")
    
    if response.status_code in [200, 201, 204]:
        print(f"  ✓ Success")
        if show_full_body and response.text:
            try:
                body = response.json()
                print(f"  Response Body:")
                print(json.dumps(body, indent=4)[:1000] + ("..." if len(response.text) > 1000 else ""))
            except:
                print(f"  Response: {response.text[:500]}")
    else:
        print(f"  ❌ Failed")
        print(f"  Response: {response.text}")
        
        # Try to parse error details
        try:
            error_data = response.json()
            if 'error' in error_data:
                error = error_data['error']
                print(f"  Error Code: {error.get('code')}")
                print(f"  Error Message: {error.get('message')}")
        except:
            pass
    
    print()


# ============================================================================
# AGENT REGISTRY OPERATIONS
# ============================================================================

def list_existing_agents(credential):
    """List all existing agents in the registry."""
    print("="*70)
    print("STEP 3: Listing Existing Agents")
    print("="*70)
    
    token = get_graph_token(credential)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = "https://graph.microsoft.com/beta/agentRegistry/agentInstances"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print_response(response)
        
        if response.status_code == 200:
            agents = response.json().get("value", [])
            print(f"Found {len(agents)} existing agent(s)")
            
            for idx, agent in enumerate(agents, 1):
                print(f"\n  Agent {idx}:")
                print(f"    ID: {agent.get('id')}")
                print(f"    Display Name: {agent.get('displayName')}")
                print(f"    Source Agent ID: {agent.get('sourceAgentId')}")
                print(f"    Has Agent Card: {'Yes' if agent.get('agentCardManifest') else 'No'}")
            
            return agents
        else:
            print("Could not retrieve agents")
            return []
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []


def register_minimal_agent(credential, config):
    """Register agent with minimal (operational) metadata only."""
    print("="*70)
    print("STEP 4: Registering Agent with Minimal Metadata")
    print("="*70)
    
    token = get_graph_token(credential)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Minimal payload - operational fields only
    payload = {
        "displayName": "Test Agent - Minimal",
        "sourceAgentId": f"test-minimal-{config['client_id'][:8]}",
        "originatingStore": "Python Test Script",
        "url": "https://example.com/agents/test-minimal",
        "preferredTransport": "JSONRPC",
        "agentIdentityId": config["client_id"]
    }
    
    print("Payload (minimal operational fields):")
    print(json.dumps(payload, indent=2))
    print()
    
    url = "https://graph.microsoft.com/beta/agentRegistry/agentInstances"
    print(f"POST {url}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print_response(response, show_full_body=True)
        
        if response.status_code in [200, 201]:
            result = response.json()
            agent_id = result.get("id")
            print(f"✓✓✓ SUCCESS! Agent registered with minimal metadata")
            print(f"    Agent Instance ID: {agent_id}")
            return agent_id
        elif response.status_code == 409:
            print("⚠️  Agent already exists (409 Conflict)")
            print("    This is expected if you've run this script before")
            return None
        else:
            print("❌ Registration failed")
            return None
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def register_full_agent(credential, config):
    """Register agent with full metadata including agentCardManifest."""
    print("="*70)
    print("STEP 5: Registering Agent with Full Metadata (Including Agent Card)")
    print("="*70)
    
    token = get_graph_token(credential)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Full payload with agentCardManifest
    payload = {
        # Operational fields
        "displayName": "Test Agent - Full Metadata",
        "sourceAgentId": f"test-full-{config['client_id'][:8]}",
        "originatingStore": "Python Test Script",
        "url": "https://example.com/agents/test-full",
        "preferredTransport": "JSONRPC",
        "agentIdentityId": config["client_id"],
        
        # Agent Card Manifest (discovery metadata)
        "agentCardManifest": {
            "displayName": "Test Agent Full",
            "description": "Test agent with full metadata including skills and capabilities",
            "version": "1.0.0",
            "supportsAuthenticatedExtendedCard": False,
            "skills": [
                {
                    "identifier": "test-skill-1",
                    "name": "Test Skill 1",
                    "description": "First test skill"
                },
                {
                    "identifier": "test-skill-2",
                    "name": "Test Skill 2",
                    "description": "Second test skill"
                }
            ],
            "defaultInputModes": ["application/json"],
            "defaultOutputModes": ["application/json"],
            "provider": {
                "name": "Test Provider",
                "contactUrl": "https://example.com/contact"
            }
        }
    }
    
    print("Payload (with agentCardManifest):")
    print(json.dumps(payload, indent=2))
    print()
    
    url = "https://graph.microsoft.com/beta/agentRegistry/agentInstances"
    print(f"POST {url}")
    print("⚠️  This will likely fail with 403 Forbidden if not using Agent Identity Blueprint")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print_response(response, show_full_body=True)
        
        if response.status_code in [200, 201]:
            result = response.json()
            agent_id = result.get("id")
            
            print(f"✓✓✓ SUCCESS! Agent registered with full metadata")
            print(f"    Agent Instance ID: {agent_id}")
            
            # Check if card was included
            if 'agentCardManifest' in result:
                card = result['agentCardManifest']
                print(f"    ✓ Agent Card Manifest present")
                print(f"      Skills count: {len(card.get('skills', []))}")
            else:
                print(f"    ⚠️  Agent card not in response")
            
            return agent_id
        
        elif response.status_code == 403:
            print("❌ 403 FORBIDDEN - As Expected!")
            print()
            print("This confirms that agentCardManifest requires an Agent Identity Blueprint.")
            print("Standard app registrations cannot use this field.")
            print()
            print("To enable full metadata:")
            print("  1. Create an Agent Identity Blueprint (requires admin)")
            print("  2. Use blueprint credentials instead of standard app registration")
            print("  3. See documentation: https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/create-blueprint")
            return None
        
        elif response.status_code == 409:
            print("⚠️  Agent already exists (409 Conflict)")
            return None
        
        else:
            print("❌ Registration failed")
            return None
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def verify_agent(credential, agent_id):
    """Verify agent was registered by retrieving its details."""
    if not agent_id:
        return
    
    print("="*70)
    print(f"STEP 6: Verifying Agent Registration")
    print("="*70)
    
    token = get_graph_token(credential)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://graph.microsoft.com/beta/agentRegistry/agentInstances/{agent_id}"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print_response(response)
        
        if response.status_code == 200:
            agent = response.json()
            print("✓ Agent Details Retrieved:")
            print(f"  ID: {agent.get('id')}")
            print(f"  Display Name: {agent.get('displayName')}")
            print(f"  Source Agent ID: {agent.get('sourceAgentId')}")
            print(f"  URL: {agent.get('url')}")
            print(f"  Originating Store: {agent.get('originatingStore')}")
            
            card = agent.get('agentCardManifest')
            if card:
                print(f"  ✓ Agent Card Manifest Present:")
                print(f"    Version: {card.get('version')}")
                print(f"    Description: {card.get('description', 'N/A')}")
                print(f"    Skills: {len(card.get('skills', []))}")
            else:
                print(f"  ⚠️  No Agent Card Manifest")
    
    except Exception as e:
        print(f"❌ Exception: {e}")


def cleanup_test_agents(credential):
    """Delete test agents created by this script."""
    print("="*70)
    print("STEP 7: Cleanup (Optional)")
    print("="*70)
    
    print("Do you want to delete the test agents? (y/n): ", end='')
    response = input().strip().lower()
    
    if response != 'y':
        print("Skipping cleanup. Test agents remain in registry.")
        return
    
    token = get_graph_token(credential)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # List all agents
    list_url = "https://graph.microsoft.com/beta/agentRegistry/agentInstances"
    response = requests.get(list_url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        agents = response.json().get("value", [])
        
        # Filter test agents
        test_agents = [
            a for a in agents 
            if a.get('sourceAgentId', '').startswith('test-')
        ]
        
        print(f"\nFound {len(test_agents)} test agent(s) to delete")
        
        for agent in test_agents:
            agent_id = agent.get('id')
            display_name = agent.get('displayName')
            
            print(f"\nDeleting: {display_name} ({agent_id})")
            delete_url = f"https://graph.microsoft.com/beta/agentRegistry/agentInstances/{agent_id}"
            
            delete_response = requests.delete(delete_url, headers=headers, timeout=30)
            
            if delete_response.status_code in [200, 204]:
                print(f"  ✓ Deleted successfully")
            else:
                print(f"  ❌ Failed: {delete_response.status_code}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution flow."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "AGENT REGISTRY TEST SCRIPT" + " "*22 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    try:
        # Load configuration
        config = load_config()
        
        # Create Graph API client
        credential = create_graph_client(config)
        
        # List existing agents
        existing_agents = list_existing_agents(credential)
        
        # Test 1: Register with minimal metadata
        minimal_agent_id = register_minimal_agent(credential, config)
        if minimal_agent_id:
            verify_agent(credential, minimal_agent_id)
        
        # Test 2: Register with full metadata (including agent card)
        full_agent_id = register_full_agent(credential, config)
        if full_agent_id:
            verify_agent(credential, full_agent_id)
        
        # Cleanup
        print()
        cleanup_test_agents(credential)
        
        # Summary
        print("\n")
        print("="*70)
        print("SUMMARY")
        print("="*70)
        print()
        print("✓ Configuration loaded successfully")
        print("✓ Graph API client authenticated")
        print(f"✓ Found {len(existing_agents)} existing agent(s) in registry")
        print(f"✓ Minimal metadata registration: {'SUCCESS' if minimal_agent_id else 'FAILED or SKIPPED'}")
        print(f"✓ Full metadata registration: {'SUCCESS' if full_agent_id else 'FAILED (Expected with standard app)'}")
        print()
        
        if not full_agent_id:
            print("📘 Note: Full metadata (agentCardManifest) requires Agent Identity Blueprint")
            print("   See: https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/create-blueprint")
        
        print()
        print("Script completed successfully!")
        print()
    
    except KeyboardInterrupt:
        print("\n\n❌ Script interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

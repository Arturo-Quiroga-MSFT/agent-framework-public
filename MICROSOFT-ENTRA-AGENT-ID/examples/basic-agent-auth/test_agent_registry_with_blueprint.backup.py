#!/usr/bin/env python3
"""
Enhanced Agent Registry Test Script
====================================
Tests both standard app and Agent Identity Blueprint scenarios.

This script demonstrates:
1. Standard app registration (minimal metadata only)
2. Agent Identity Blueprint creation (requires admin)
3. Full metadata registration with agentCardManifest

Prerequisites:
    - .env file with TENANT_ID, AGENT_CLIENT_ID, AGENT_CLIENT_SECRET
    - USER_ID in .env (required for blueprint creation)
    - Global Admin or Privileged Role Admin permissions (for blueprint)
    - Graph API permissions:  
        FOR STANDARD APP (AGENT_CLIENT_ID):
        - AgentInstance.ReadWrite.All
        - AgentIdentityBlueprint.Create
        - AgentIdentityBlueprintPrincipal.Create
        - AgentCardManifest.ReadWrite.All (for registration)
        - Application.ReadWrite.All (to add secrets to blueprint)
        
Known Limitations:
    - agentCardManifest registration may still return 403 even with correct permissions
    - This appears to be a preview API limitation or tenant-level restriction
    - The blueprint and principal creation will work successfully
    - Agent Identity creation from standard app will fail (expected - requires blueprint principal token)
    
Usage:
    python test_agent_registry_with_blueprint.py
"""

import os
import sys
import json
import requests
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential


GRAPH_BETA = "https://graph.microsoft.com/beta"
GRAPH_V1 = "https://graph.microsoft.com/v1.0"
MS_GRAPH_APP_ID = "00000003-0000-0000-c000-000000000000"

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
    user_id = os.getenv("USER_ID")  # Required for blueprint creation
    
    if not all([tenant_id, client_id, client_secret]):
        print("❌ Missing required environment variables")
        print("   Required: TENANT_ID, AGENT_CLIENT_ID, AGENT_CLIENT_SECRET")
        print("   Optional: USER_ID (required for blueprint creation)")
        sys.exit(1)
    
    print(f"✓ Loaded .env from: {env_path}")
    print(f"✓ Tenant ID: {tenant_id}")
    print(f"✓ Client ID: {client_id}")
    print(f"✓ Client Secret: {'*' * 10}...{client_secret[-4:]}")
    
    if user_id:
        print(f"✓ User ID: {user_id}")
    else:
        print(f"⚠️  USER_ID not set - blueprint creation will be skipped")
    
    print()
    
    return {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "client_secret": client_secret,
        "user_id": user_id
    }


# ============================================================================
# GRAPH API CLIENT
# ============================================================================

def create_graph_client(tenant_id, client_id, client_secret):
    """Create authenticated Graph API client."""
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Test token acquisition
        token = credential.get_token("https://graph.microsoft.com/.default")
        return credential
    
    except Exception as e:
        print(f"❌ Failed to create Graph client: {e}")
        return None


def create_graph_client_with_retry(tenant_id, client_id, client_secret, *, max_attempts=6, base_wait_s=10):
    """Create authenticated Graph client; retry to accommodate Entra propagation delays."""
    last_error = None
    for attempt in range(1, max_attempts + 1):
        credential = create_graph_client(tenant_id, client_id, client_secret)
        if credential:
            return credential
        wait_s = base_wait_s * attempt
        last_error = "failed"
        print(f"⏳ Auth not ready yet (attempt {attempt}/{max_attempts}); waiting {wait_s}s...")
        time.sleep(wait_s)
    if last_error:
        print("❌ Blueprint auth never succeeded after retries")
    return None


def get_graph_token(credential):
    """Get Graph API access token."""
    token = credential.get_token("https://graph.microsoft.com/.default")
    return token.token


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def make_request(method, url, token, data=None):
    """Make HTTP request to Graph API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        result = {
            "status_code": response.status_code,
            "body": response.json() if response.text else {}
        }
        
        return result
    
    except requests.exceptions.JSONDecodeError:
        return {
            "status_code": response.status_code,
            "body": {}
        }
    except Exception as e:
        print(f"❌ Request exception: {e}")
        return {"status_code": 0, "body": {}}


def print_response_status(response):
    """Print HTTP response status."""
    status = response.get('status_code')
    print(f"  HTTP Status: {status}")
    
    if status in [200, 201, 204]:
        print(f"  ✓ Success")
    else:
        print(f"  ❌ Failed")
        error = response.get('body', {}).get('error', {})
        if error:
            print(f"  Response: {json.dumps(error, indent=2)}")


def _get_blueprint_with_retry(token, blueprint_object_id, max_attempts=8, base_wait_s=3):
    """Wait for a newly-created blueprint to become readable and return it."""
    for attempt in range(1, max_attempts + 1):
        url = f"{GRAPH_BETA}/applications/{blueprint_object_id}/microsoft.graph.agentIdentityBlueprint?$select=id,appId,displayName"
        resp = make_request("GET", url, token)
        if resp.get('status_code') == 200 and resp.get('body', {}).get('appId'):
            return resp.get('body')
        wait_s = base_wait_s * attempt
        print(f"  ⏳ Blueprint not ready yet (attempt {attempt}/{max_attempts}); waiting {wait_s}s...")
        time.sleep(wait_s)
    return None


def _ensure_blueprint_principal(token, blueprint_app_id):
    """Create blueprint principal if needed; return its object id."""
    principal_url = f"{GRAPH_BETA}/servicePrincipals/microsoft.graph.agentIdentityBlueprintPrincipal"
    create_payload = {"appId": blueprint_app_id}

    # Directory propagation can make the backing application temporarily unavailable.
    for attempt in range(1, 9):
        create_resp = make_request("POST", principal_url, token, data=create_payload)
        if create_resp.get('status_code') == 201:
            return create_resp.get('body', {}).get('id')
        if create_resp.get('status_code') == 409:
            break

        if create_resp.get('status_code') == 400:
            msg = (create_resp.get('body', {}).get('error', {}) or {}).get('message', '')
            transient_markers = [
                "NoBackingApplicationObject",
                "does not reference a valid application object",
            ]
            if any(m in msg for m in transient_markers):
                wait_s = 5 * attempt
                print(f"  ⏳ Blueprint principal not ready yet (attempt {attempt}/8); waiting {wait_s}s...")
                time.sleep(wait_s)
                continue

        print("⚠️  Blueprint principal create failed")
        print_response_status(create_resp)
        break

    # 409 or create failed: try resolve by appId
    lookup_url = f"{GRAPH_BETA}/servicePrincipals?$filter=appId%20eq%20'{blueprint_app_id}'&$select=id,appId,displayName,servicePrincipalType"
    lookup_resp = make_request("GET", lookup_url, token)
    if lookup_resp.get('status_code') != 200:
        return None
    values = lookup_resp.get('body', {}).get('value', [])
    match = values[0] if values else None
    return match.get('id') if match else None


# ============================================================================
# AGENT REGISTRY OPERATIONS (Standard App)
# ============================================================================

def list_agents(credential):
    """List all existing agents in the registry."""
    print("="*70)
    print("STEP 2: Listing Existing Agents")
    print("="*70)
    
    token = get_graph_token(credential)
    url = f"{GRAPH_BETA}/agentRegistry/agentInstances"
    print(f"GET {url}")
    
    response = make_request("GET", url, token)
    print_response_status(response)
    
    if response.get('status_code') == 200:
        agents = response.get('body', {}).get("value", [])
        print(f"\nFound {len(agents)} existing agent(s)")
        
        for idx, agent in enumerate(agents, 1):
            print(f"\n  Agent {idx}:")
            print(f"    ID: {agent.get('id')}")
            print(f"    Display Name: {agent.get('displayName')}")
            print(f"    Source Agent ID: {agent.get('sourceAgentId')}")
            print(f"    Has Agent Card: {'Yes' if agent.get('agentCardManifest') else 'No'}")
        
        return agents
    
    return []


def register_minimal_agent(credential, client_id, run_id):
    """Register agent with minimal (operational) metadata only."""
    print("\n" + "="*70)
    print("STEP 3: Registering Agent with Minimal Metadata (Standard App)")
    print("="*70)
    
    token = get_graph_token(credential)
    
    payload = {
        "displayName": f"Test Agent - Minimal ({run_id})",
        "sourceAgentId": f"test-minimal-{client_id[:8]}-{run_id}",
        "originatingStore": "Python Test Script",
        "url": f"https://example.com/agents/test-minimal/{run_id}",
        "preferredTransport": "JSONRPC",
    }
    
    print("Payload (minimal operational fields):")
    print(json.dumps(payload, indent=2))
    
    url = f"{GRAPH_BETA}/agentRegistry/agentInstances"
    print(f"\nPOST {url}")
    
    response = make_request("POST", url, token, data=payload)
    print_response_status(response)
    
    if response.get('status_code') == 201:
        result = response.get('body', {})
        agent_id = result.get("id")
        print(f"\n✓✓✓ SUCCESS! Agent registered with minimal metadata")
        print(f"    Agent Instance ID: {agent_id}")
        return agent_id
    elif response.get('status_code') == 409:
        print(f"\n⚠️  Agent already exists (409 Conflict)")
        print(f"    This shouldn't happen with unique run IDs; check uniqueness constraints.")
        return None
    else:
        print(f"\n❌ Registration failed")
        return None


# ============================================================================
# AGENT IDENTITY BLUEPRINT OPERATIONS
# ============================================================================

def create_agent_identity_blueprint(credential, user_id, run_id):
    """Create an Agent Identity Blueprint."""
    print("\n" + "="*70)
    print("STEP 4: Creating Agent Identity Blueprint")
    print("="*70)
    
    if not user_id:
        print("⚠️  Skipping - USER_ID not provided in .env")
        print("   Blueprint creation requires Global Admin or Privileged Role Admin")
        return None, None, None, None
    
    token = get_graph_token(credential)
    
    blueprint_name = f"Test Blueprint {run_id}"
    
    blueprint_payload = {
        "displayName": blueprint_name,
        "description": "Test Agent Identity Blueprint for full metadata registration",
        "sponsors@odata.bind": [
            f"{GRAPH_V1}/users/{user_id}"
        ],
    }
    
    print(f"Creating blueprint: {blueprint_name}")
    print(f"Sponsor/Owner: {user_id}")
    
    url = f"{GRAPH_BETA}/applications/microsoft.graph.agentIdentityBlueprint"
    print(f"\nPOST {url}")
    
    response = make_request("POST", url, token, data=blueprint_payload)
    print_response_status(response)
    
    if response.get('status_code') != 201:
        error = response.get('body', {}).get('error', {})
        error_code = error.get('code')
        error_message = error.get('message')
        print(f"\n❌ Blueprint creation failed")
        print(f"  Error Code: {error_code}")
        print(f"  Error Message: {error_message}")
        print("\n💡 Blueprint creation requires:")
        print("   - Global Admin or Privileged Role Admin role")
        print("   - AgentIdentityBlueprint.Create permission")
        return None, None, None, None
    
    blueprint = response.get('body', {})
    blueprint_app_id = blueprint.get('appId')
    blueprint_object_id = blueprint.get('id')
    
    print(f"\n✓ Blueprint created successfully")
    print(f"  Object ID: {blueprint_object_id}")
    print(f"  App ID: {blueprint_app_id}")

    print(f"\n⏳ Waiting for blueprint propagation...")
    bp = _get_blueprint_with_retry(token, blueprint_object_id)
    if not bp:
        print("❌ Blueprint did not become readable in time; cannot continue")
        return None, None, None, None
    blueprint_app_id = bp.get('appId') or blueprint_app_id
    print(f"  ✓ Blueprint ready")
    print(f"    Object ID: {bp.get('id')}")
    print(f"    App ID: {blueprint_app_id}")

    print("\nCreating/Resolving Blueprint Principal...")
    principal_id = _ensure_blueprint_principal(token, blueprint_app_id)
    if not principal_id:
        print("\n❌ Cannot continue without Blueprint Principal")
        return None, None, None, None
    print(f"✓ Blueprint Principal ID: {principal_id}")
    
    # Step 3: Add client secret
    print("\nAdding client secret to blueprint...")
    secret_payload = {
        "passwordCredential": {
            "displayName": "Test Script Secret",
            "endDateTime": "2027-12-31T23:59:59Z"
        }
    }
    
    secret_url = f"{GRAPH_BETA}/applications/{blueprint_object_id}/microsoft.graph.agentIdentityBlueprint/addPassword"
    secret_response = make_request("POST", secret_url, token, data=secret_payload)
    
    if secret_response.get('status_code') != 200:
        print("❌ Failed to create client secret via blueprint addPassword")
        print_response_status(secret_response)
        print("\n↪️  Trying fallback: standard application addPassword (requires Application.ReadWrite.All)")
        fallback_url = f"{GRAPH_BETA}/applications/{blueprint_object_id}/addPassword"
        secret_response = make_request("POST", fallback_url, token, data=secret_payload)
        if secret_response.get('status_code') != 200:
            print("❌ Fallback addPassword also failed")
            print_response_status(secret_response)
            print("\n💡 If the first call failed with 403, grant 'AgentIdentityBlueprint.AddRemoveCreds.All' to your standard app.")
            return blueprint_app_id, blueprint_object_id, None, principal_id
    
    secret_data = secret_response.get('body', {})
    blueprint_secret = secret_data.get('secretText')
    if not blueprint_secret:
        print("❌ addPassword response missing secretText")
        print(json.dumps(secret_data, indent=2))
        return blueprint_app_id, blueprint_object_id, None, principal_id

    print(f"✓ Client secret created")
    print(f"  Secret length: {len(blueprint_secret)}")
    print(f"  Secret: {'*' * 10}...{blueprint_secret[-4:]}")

    # Secret propagation can be slow; allow time before attempting client credentials auth.
    print("\n⏳ Waiting 30 seconds for secret propagation...")
    time.sleep(30)
    
    return blueprint_app_id, blueprint_object_id, blueprint_secret, principal_id


def create_agent_identity_from_blueprint(blueprint_credential, blueprint_app_id, sponsor_user_id, run_id):
    """Create an Agent Identity using the blueprint principal token."""
    print("\n" + "="*70)
    print("STEP 5: Creating Agent Identity (Using Blueprint Credentials)")
    print("="*70)

    token = get_graph_token(blueprint_credential)
    payload = {
        "displayName": f"Test Agent Identity ({run_id})",
        # Note: agentIdentity expects the *appId* of the blueprint
        "agentIdentityBlueprintId": blueprint_app_id,
        "sponsors@odata.bind": [
            f"{GRAPH_V1}/users/{sponsor_user_id}"
        ],
    }
    url = f"{GRAPH_BETA}/servicePrincipals/microsoft.graph.agentIdentity"
    print(f"POST {url}")
    response = make_request("POST", url, token, data=payload)
    print_response_status(response)

    if response.get('status_code') != 201:
        print("\n❌ Agent identity creation failed")
        return None

    agent_identity = response.get('body', {})
    agent_identity_object_id = agent_identity.get('id')
    print(f"\n✓ Agent Identity created")
    print(f"  Object ID: {agent_identity_object_id}")
    print(f"  Blueprint appId: {agent_identity.get('agentIdentityBlueprintId')}")
    return agent_identity_object_id


def _try_get_agent_card_manifest(credential, agent_instance_id):
    """Preflight: try reading agentCardManifest for an instance (may be empty)."""
    if not agent_instance_id:
        return

    token = get_graph_token(credential)
    url = f"https://graph.microsoft.com/beta/agentRegistry/agentInstances/{agent_instance_id}/agentCardManifest"
    print(f"\nPreflight GET {url}")
    response = make_request("GET", url, token)
    print_response_status(response)


def register_full_agent_instance(credential, *, managed_by_app_id, blueprint_object_id, agent_identity_object_id, owner_user_id, run_id):
    """Register agent with full metadata in Agent Registry using the standard app token."""
    print("\n" + "="*70)
    print("STEP 6: Registering Agent with Full Metadata (Agent Registry)")
    print("="*70)
    
    token = get_graph_token(credential)
    
    payload = {
        "displayName": f"Test Agent - Full Metadata ({run_id})",
        "sourceAgentId": f"test-full-{managed_by_app_id[:8]}-{run_id}",
        "originatingStore": "Python Test Script",
        "url": f"https://example.com/agents/test-full/{run_id}",
        "preferredTransport": "JSONRPC",
        "managedBy": managed_by_app_id,
        "ownerIds": [owner_user_id] if owner_user_id else [],
        # Agent Registry expects *object ids* for blueprint/agent identity
        "agentIdentityBlueprintId": blueprint_object_id,
        "agentIdentityId": agent_identity_object_id,
        "agentCardManifest": {
            "displayName": "Test Agent Full",
            "description": "Test agent with full metadata including skills and capabilities",
            "protocolVersion": "1.0",
            "version": "1.0.0",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False,
                "stateTransitionHistory": False,
                "extensions": [],
            },
            "supportsAuthenticatedExtendedCard": False,
            "skills": [
                {
                    "id": "test-skill-1",
                    "displayName": "Test Skill 1",
                    "description": "First test skill",
                    "examples": ["Example usage 1"],
                    "tags": ["test", "demo"]
                },
                {
                    "id": "test-skill-2",
                    "displayName": "Test Skill 2",
                    "description": "Second test skill",
                    "examples": ["Example usage 2"],
                    "tags": ["test", "demo"]
                }
            ],
            "defaultInputModes": ["application/json"],
            "defaultOutputModes": ["application/json"],
            "provider": {
                "organization": "Test Provider",
                "url": "https://example.com/contact"
            }
        }
    }
    
    print("Payload (with agentCardManifest):")
    print(json.dumps(payload, indent=2))
    
    url = f"{GRAPH_BETA}/agentRegistry/agentInstances"
    print(f"\nPOST {url}")
    
    response = make_request("POST", url, token, data=payload)
    print_response_status(response)
    
    if response.get('status_code') == 201:
        result = response.get('body', {})
        agent_id = result.get("id")
        
        print(f"\n✓✓✓ SUCCESS! Agent registered with full metadata")
        print(f"    Agent Instance ID: {agent_id}")
        
        if 'agentCardManifest' in result:
            card = result['agentCardManifest']
            print(f"    Agent Card Manifest:")
            print(f"      Display Name: {card.get('displayName')}")
            print(f"      Description: {card.get('description')}")
            print(f"      Version: {card.get('version')}")
            print(f"      Skills: {len(card.get('skills', []))}")
            
            for i, skill in enumerate(card.get('skills', []), 1):
                print(f"      Skill {i}:")
                print(f"        ID: {skill.get('id')}")
                print(f"        Name: {skill.get('displayName')}")
                print(f"        Description: {skill.get('description')}")
        
        return agent_id
    elif response.get('status_code') == 409:
        print(f"\n⚠️  Agent already exists (409 Conflict)")
        return None
    else:
        error = response.get('body', {}).get('error', {})
        print(f"\n❌ Registration failed")
        print(f"  Error: {error.get('code')} - {error.get('message')}")
        return None


# =========================================================================
# CLEANUP
# ============================================================================

def cleanup_agents_and_blueprint(credential, blueprint_object_id=None):
    """Delete test agents and blueprint."""
    print("\n" + "="*70)
    print("STEP 6: Cleanup (Optional)")
    print("="*70)
    
    response = input("\nDo you want to delete the test agents and blueprint? (y/n): ")
    if response.lower() != 'y':
        print("Skipping cleanup. Test agents remain in registry.")
        return
    
    token = get_graph_token(credential)
    
    # Delete agents
    list_url = f"{GRAPH_BETA}/agentRegistry/agentInstances"
    response = make_request("GET", list_url, token)
    
    if response.get('status_code') == 200:
        agents = response.get('body', {}).get("value", [])
        test_agents = [a for a in agents if a.get('sourceAgentId', '').startswith('test-')]
        
        print(f"\nFound {len(test_agents)} test agent(s) to delete")
        
        for agent in test_agents:
            agent_id = agent.get('id')
            display_name = agent.get('displayName')
            
            print(f"\nDeleting: {display_name} ({agent_id})")
            delete_url = f"https://graph.microsoft.com/beta/agentRegistry/agentInstances/{agent_id}"
            delete_response = make_request("DELETE", delete_url, token)
            
            if delete_response.get('status_code') in [200, 204]:
                print(f"  ✓ Deleted successfully")
            else:
                print(f"  ⚠️  Failed to delete")
    
    # Delete blueprint
    if blueprint_object_id:
        print(f"\nDeleting blueprint: {blueprint_object_id}")
        blueprint_url = f"{GRAPH_BETA}/applications/{blueprint_object_id}"
        blueprint_response = make_request("DELETE", blueprint_url, token)
        
        if blueprint_response.get('status_code') in [200, 204]:
            print("  ✓ Blueprint deleted successfully")
        else:
            print("  ⚠️  Failed to delete blueprint")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution flow."""
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*12 + "ENHANCED AGENT REGISTRY TEST SCRIPT" + " "*21 + "║")
    print("║" + " "*16 + "(With Blueprint Support)" + " "*29 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    try:
        # Step 1: Load configuration
        config = load_config()
        
        # Step 2: Create Graph API client with standard app credentials
        print("="*70)
        print("STEP 1a: Authenticating with Standard App Credentials")
        print("="*70)
        
        standard_credential = create_graph_client(
            config["tenant_id"],
            config["client_id"],
            config["client_secret"]
        )
        
        if not standard_credential:
            print("❌ Failed to authenticate with standard credentials")
            sys.exit(1)
        
        token = get_graph_token(standard_credential)
        print(f"✓ Authenticated with standard app credentials")
        print(f"  Token length: {len(token)} chars")
        print()

        run_id = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        print(f"Run ID: {run_id}")
        print()
        
        # Step 3: List existing agents
        existing_agents = list_agents(standard_credential)
        
        # Step 4: Register with minimal metadata (standard app)
        minimal_agent_id = register_minimal_agent(standard_credential, config["client_id"], run_id)
        
        # Step 5: Create Agent Identity Blueprint
        blueprint_app_id, blueprint_object_id, blueprint_secret, blueprint_principal_id = create_agent_identity_blueprint(
            standard_credential,
            config["user_id"],
            run_id,
        )
        
        # Step 6: Create Agent Identity using blueprint creds, then register full agent instance using standard creds
        full_agent_id = None
        if blueprint_app_id and blueprint_secret and config["user_id"]:
            print("\n" + "="*70)
            print("STEP 4a: Authenticating with Blueprint Credentials")
            print("="*70)
            
            blueprint_credential = create_graph_client_with_retry(
                config["tenant_id"],
                blueprint_app_id,
                blueprint_secret,
            )
            
            if blueprint_credential:
                token = get_graph_token(blueprint_credential)
                print(f"✓ Authenticated with blueprint credentials")
                print(f"  Token length: {len(token)} chars")

                agent_identity_object_id = create_agent_identity_from_blueprint(
                    blueprint_credential,
                    blueprint_app_id,
                    config["user_id"],
                    run_id,
                )

                if agent_identity_object_id:
                    full_agent_id = register_full_agent_instance(
                        standard_credential,
                        managed_by_app_id=config["client_id"],
                        blueprint_object_id=blueprint_object_id,
                        agent_identity_object_id=agent_identity_object_id,
                        owner_user_id=config["user_id"],
                        run_id=run_id,
                    )
            else:
                print("❌ Failed to authenticate with blueprint credentials")
        else:
            print("\n⚠️  Skipping full metadata flow - blueprint/secret not created or USER_ID missing")
        
        # Step 7: Cleanup
        cleanup_agents_and_blueprint(standard_credential, blueprint_object_id)
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print()
        print("✓ Configuration loaded successfully")
        print("✓ Standard app authentication successful")
        print(f"✓ Found {len(existing_agents)} existing agent(s) in registry")
        print(f"✓ Minimal metadata registration: {'SUCCESS' if minimal_agent_id else 'FAILED or SKIPPED'}")
        
        if blueprint_app_id:
            print(f"✓ Agent Identity Blueprint: CREATED")
            print(f"✓ Full metadata registration: {'SUCCESS' if full_agent_id else 'FAILED'}")
        else:
            print(f"✓ Agent Identity Blueprint: SKIPPED (requires USER_ID and admin permissions)")
            print(f"✓ Full metadata registration: SKIPPED")
        
        print("\n🎉 Script completed successfully!")
        
        if not blueprint_app_id:
            print("\n📘 To test full metadata registration:")
            print("   1. Add USER_ID to .env (your user object ID)")
            print("   2. Ensure you have Global Admin or Privileged Role Admin role")
            print("   3. Run this script again")
        
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

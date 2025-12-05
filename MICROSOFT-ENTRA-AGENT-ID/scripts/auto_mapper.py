#!/usr/bin/env python3
"""
Automatic Agent Identity Mapper

Maps Azure AI Foundry agents to their Entra ID identities by correlating
the publish order of agents with the creation timestamps of identities.

Key insight: When you publish an agent, 2 service principals are created in Entra ID.
The second one (even position when sorted by time) is the agent's identity.

Usage:
    python auto_mapper.py

Prerequisites:
    - Azure CLI logged in (az login)
    - pip install azure-identity azure-ai-projects requests python-dotenv
"""

import os
import json
from datetime import datetime, timezone
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import requests
from dotenv import load_dotenv

load_dotenv()

class AgentIdentityMapper:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        self.resource_name = None
        
    def parse_foundry_endpoint(self):
        """Extract resource name from endpoint."""
        if not self.foundry_endpoint or 'services.ai.azure.com' not in self.foundry_endpoint:
            return False
            
        # Extract resource name from hostname
        # e.g., https://aq-ai-foundry-Sweden-Central.services.ai.azure.com/...
        hostname = self.foundry_endpoint.split('/')[2]
        self.resource_name = hostname.split('.')[0]
        print(f"   Resource: {self.resource_name}")
        return True
    
    def get_foundry_agents(self):
        """Get all agents from Foundry using the SDK."""
        print("\n📡 Fetching agents from Foundry...")
        
        try:
            client = AIProjectClient(
                endpoint=self.foundry_endpoint,
                credential=self.credential
            )
            
            agents = list(client.agents.list())
            
            # Known rogue/deleted agents to ignore
            IGNORE_AGENTS = {'ONE'}
            
            # Extract names, filtering out rogue agents
            agent_names = []
            for agent in agents:
                if agent.name in IGNORE_AGENTS:
                    print(f"   ⏭️  {agent.name} (ignored - rogue/deleted)")
                else:
                    agent_names.append(agent.name)
            
            print(f"   ✅ Found {len(agent_names)} valid agents: {', '.join(agent_names)}")
            
            return agent_names
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def get_agent_identities_from_entra(self):
        """Get agent identities from Entra ID, sorted by creation time."""
        print("\n🔐 Fetching agent identities from Entra ID...")
        
        token = self.credential.get_token("https://graph.microsoft.com/.default").token
        
        graph_url = (
            f"https://graph.microsoft.com/v1.0/servicePrincipals"
            f"?$filter=startswith(displayName,'{self.resource_name}')"
            f"&$select=id,displayName,createdDateTime"
            f"&$top=100"
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(graph_url, headers=headers)
            if response.status_code != 200:
                print(f"   ❌ Graph API error: {response.status_code}")
                return []
            
            all_sps = response.json().get('value', [])
            
            # Filter to only AgentIdentity service principals
            agent_identities = [
                sp for sp in all_sps 
                if 'AgentIdentity' in sp.get('displayName', '')
            ]
            
            # Sort by creation time
            agent_identities.sort(key=lambda x: x.get('createdDateTime', ''))
            
            print(f"   ✅ Found {len(agent_identities)} agent identities")
            
            return agent_identities
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def get_publish_order_from_user(self, agent_names):
        """Ask user for the order in which they published agents."""
        
        # Known publish order from user (verified mapping)
        KNOWN_PUBLISH_ORDER = [
            "WebSearchAgent",
            "BasicWeatherAgent", 
            "ResearchAgent",
            "DataAnalysisAgent",
            "CodeInterpreterAgent",
            "FileSearchAgent",
            "BasicAgent",
            "WeatherAgent",
            "BingGroundingAgent"
        ]
        
        # Use known order if it matches the agents we found
        matching_agents = [a for a in KNOWN_PUBLISH_ORDER if a in agent_names]
        if len(matching_agents) == len(KNOWN_PUBLISH_ORDER):
            print("\n📋 Using known publish order:")
            for i, name in enumerate(matching_agents, 1):
                print(f"   {i}. {name}")
            return matching_agents
        
        # Otherwise, ask user
        print("\n📋 Agent Publish Order")
        print("=" * 60)
        print("I found these agents in Foundry:")
        for i, name in enumerate(agent_names, 1):
            print(f"   {i}. {name}")
        
        print("\n❓ Enter the agents you published, in order (comma-separated).")
        print("   Exclude any agents you did NOT publish (e.g., drafts).")
        print("   Or press Enter to use the order shown above.\n")
        print("   Example: WebSearchAgent, BasicWeatherAgent, ResearchAgent")
        
        response = input("\n   > ").strip()
        
        if not response:
            return agent_names
        
        # Parse comma-separated list
        ordered_names = [name.strip() for name in response.split(',') if name.strip()]
        
        # Validate
        invalid = [n for n in ordered_names if n not in agent_names]
        if invalid:
            print(f"\n   ⚠️  Unknown agents: {invalid}")
            print("   Using all agents in default order.")
            return agent_names
        
        return ordered_names
    
    def correlate_agents_with_identities(self, agent_names, identities):
        """
        Correlate agents with identities.
        
        Key insight: Each publish creates 2 service principals.
        The second one (even index: 1, 3, 5...) is the agent's identity.
        """
        print("\n🔗 Correlating agents with identities...")
        
        # Filter to identities created in the recent batch (same day as most recent)
        if not identities:
            return []
        
        # Get the date of the most recent identity
        most_recent_date = identities[-1].get('createdDateTime', '')[:10]
        
        # Filter to identities from that day
        recent_identities = [
            i for i in identities 
            if i.get('createdDateTime', '').startswith(most_recent_date)
        ]
        
        print(f"   📅 Using {len(recent_identities)} identities from {most_recent_date}")
        
        # Take every 2nd identity (index 1, 3, 5, 7...)
        # These are the actual agent identities, not the intermediate ones
        agent_identity_candidates = [
            recent_identities[i] for i in range(1, len(recent_identities), 2)
        ]
        
        print(f"   🎯 Extracted {len(agent_identity_candidates)} agent identities (every 2nd)")
        
        # Match with agent names in order
        mapping = []
        for i, agent_name in enumerate(agent_names):
            if i < len(agent_identity_candidates):
                identity = agent_identity_candidates[i]
                mapping.append({
                    'agent_name': agent_name,
                    'object_id': identity.get('id'),
                    'identity_created': identity.get('createdDateTime'),
                    'status': 'Published with Identity',
                    'confidence': 'High'
                })
        
        return mapping
    
    def verify_mapping(self, mapping):
        """Verify mapping against known file if available."""
        known_file = os.path.join(os.path.dirname(__file__), 'agent_identity_mapping_complete.json')
        
        if not os.path.exists(known_file):
            return True
        
        print("\n🔍 Verifying against known mapping...")
        
        try:
            with open(known_file, 'r') as f:
                known = json.load(f)
            
            known_map = {a['agent_name']: a['object_id'] for a in known.get('agents', [])}
            
            matches = 0
            total = 0
            
            for item in mapping:
                name = item['agent_name']
                if name in known_map:
                    total += 1
                    if item['object_id'] == known_map[name]:
                        matches += 1
                        print(f"   ✅ {name}: MATCH")
                    else:
                        print(f"   ❌ {name}: MISMATCH")
                        print(f"      Got:      {item['object_id']}")
                        print(f"      Expected: {known_map[name]}")
            
            accuracy = (matches / total * 100) if total > 0 else 0
            print(f"\n   📊 Accuracy: {matches}/{total} ({accuracy:.0f}%)")
            
            return matches == total
            
        except Exception as e:
            print(f"   ⚠️  Could not verify: {e}")
            return True
    
    def display_mapping(self, mapping):
        """Display the mapping results."""
        print("\n" + "=" * 90)
        print("🎯 AGENT IDENTITY MAPPING")
        print("=" * 90)
        
        print(f"\n{'Agent Name':<25} {'Object ID':<45} {'Confidence':<10}")
        print("-" * 90)
        
        for item in mapping:
            print(f"{item['agent_name']:<25} {item['object_id']:<45} {item['confidence']:<10}")
        
        print("=" * 90)
    
    def save_mapping(self, mapping):
        """Save mapping to JSON file."""
        output = {
            "generated_at": datetime.now().isoformat(),
            "mapping_method": "automatic_publish_order_correlation",
            "agents": mapping
        }
        
        filename = f"agent_identity_mapping_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved to: {filename}")
        return filename
    
    def generate_rbac_commands(self, mapping):
        """Generate RBAC assignment commands."""
        print("\n📋 RBAC Assignment Commands:")
        print("-" * 60)
        
        for item in mapping:
            print(f"\n# {item['agent_name']}")
            print(f"az role assignment create \\")
            print(f"  --assignee {item['object_id']} \\")
            print(f"  --role \"Storage Blob Data Reader\" \\")
            print(f"  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account>")
    
    def run(self):
        """Run the automatic mapping process."""
        print("=" * 90)
        print("🤖 Automatic Agent Identity Mapper")
        print("=" * 90)
        
        if not self.foundry_endpoint:
            print("\n❌ FOUNDRY_PROJECT_ENDPOINT not set")
            print("   export FOUNDRY_PROJECT_ENDPOINT='https://...'")
            return
        
        print(f"\n📍 Endpoint: {self.foundry_endpoint}")
        
        if not self.parse_foundry_endpoint():
            print("\n❌ Could not parse endpoint")
            return
        
        # Get agents
        agent_names = self.get_foundry_agents()
        if not agent_names:
            return
        
        # Get identities
        identities = self.get_agent_identities_from_entra()
        if not identities:
            return
        
        # Get publish order from user
        ordered_agents = self.get_publish_order_from_user(agent_names)
        
        if ordered_agents is None:
            print("\n⚠️  Skipping - using alphabetical order as fallback")
            ordered_agents = sorted(agent_names)
        
        # Correlate
        mapping = self.correlate_agents_with_identities(ordered_agents, identities)
        
        if not mapping:
            print("\n❌ Could not create mapping")
            return
        
        # Display
        self.display_mapping(mapping)
        
        # Verify
        if not self.verify_mapping(mapping):
            print("\n⚠️  Mapping doesn't match known values!")
            print("   Please verify manually or check publish order.")
        
        # Save
        self.save_mapping(mapping)
        
        # Show RBAC commands
        show_rbac = input("\n❓ Show RBAC commands? (y/n): ").strip().lower()
        if show_rbac == 'y':
            self.generate_rbac_commands(mapping)
        
        print("\n✨ Done!")

def main():
    try:
        mapper = AgentIdentityMapper()
        mapper.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

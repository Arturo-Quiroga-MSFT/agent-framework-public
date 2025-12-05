#!/usr/bin/env python3
"""
Interactive Agent Identity Mapper

Since the Foundry API doesn't return agent identity IDs reliably, this script
helps you manually map agent names to their Object IDs by checking the Foundry portal.

Usage:
    python interactive_mapper.py
"""

import json
from datetime import datetime

# Known Object IDs from Entra ID portal
KNOWN_OBJECT_IDS = [
    "420c8552-5d64-4c44-869c-037ad07ef351",
    "ff55957a-bbf1-4be8-9e41-0046b2b2494c",
    "bde46d80-de73-4bd9-9416-4515799ae72d",  # BasicAgent (corrected)
    "0e1584e6-f309-4e4b-9909-3200e3bca7a5",
    "d73547cc-9f5f-4de5-8f3b-97e14f882016",
    "a3be091d-da7b-4696-b0f6-b7f41f5cca84",
    "9350dda6-b732-4b1c-a111-c5d8c4ffc64a",
    "966ccc07-512a-4698-bafb-4d5686973d27",  # BasicWeatherAgent
    "38c14420-a914-4370-a0f8-1b014598c1d0",  # WebSearchAgent
]

# Agent names from Foundry
AGENT_NAMES = [
    "WebSearchAgent",
    "BasicWeatherAgent",
    "ResearchAgent",
    "ONE",
    "DataAnalysisAgent",
    "CodeInterpreterAgent",
    "FileSearchAgent",
    "BasicAgent",
    "WeatherAgent",
    "BingGroundingAgent",
]

def display_instructions():
    """Display instructions for manual mapping."""
    print("\n" + "=" * 100)
    print("🔍 INTERACTIVE AGENT IDENTITY MAPPER")
    print("=" * 100)
    print("\n📋 Instructions:")
    print("   1. Open Azure AI Foundry portal in your browser")
    print("   2. For each agent below, click on it in the Foundry portal")
    print("   3. Look for 'Agent Identity ID' or 'Object ID' in the agent's properties/settings")
    print("   4. Copy the Object ID and paste it when prompted")
    print("   5. Press Enter to continue to the next agent")
    print("   6. Type 'skip' to skip an agent")
    print("   7. Type 'quit' to save and exit")
    print("\n💡 Tip: You can also check the 'Properties' or 'JSON View' of each agent")
    print("=" * 100)

def manual_mapping():
    """Interactively map agent names to Object IDs."""
    
    display_instructions()
    
    mapping = []
    
    print(f"\n📝 Found {len(AGENT_NAMES)} agents to map:")
    for i, name in enumerate(AGENT_NAMES, 1):
        print(f"   {i}. {name}")
    
    print(f"\n🆔 Found {len(KNOWN_OBJECT_IDS)} Object IDs in Entra ID portal")
    
    input("\n👉 Press Enter when ready to start mapping...")
    
    for i, agent_name in enumerate(AGENT_NAMES, 1):
        print("\n" + "-" * 100)
        print(f"🤖 Agent {i}/{len(AGENT_NAMES)}: {agent_name}")
        print("-" * 100)
        print("\nIn Foundry portal:")
        print(f"  1. Click on '{agent_name}'")
        print(f"  2. Find the 'Agent Identity ID' or 'Object ID'")
        print(f"  3. Copy and paste it below")
        
        while True:
            object_id = input(f"\n{agent_name} Object ID: ").strip()
            
            if object_id.lower() == 'quit':
                print("\n⚠️  Saving partial mapping and exiting...")
                return mapping
            
            if object_id.lower() == 'skip':
                print(f"⏭️  Skipping {agent_name}")
                mapping.append({
                    "agent_name": agent_name,
                    "object_id": None,
                    "status": "Skipped",
                    "notes": "User skipped during manual mapping"
                })
                break
            
            if not object_id:
                print("❌ Object ID cannot be empty. Try again or type 'skip'")
                continue
            
            # Validate format (basic GUID check)
            if len(object_id) == 36 and object_id.count('-') == 4:
                # Check if it's in our known list
                if object_id in KNOWN_OBJECT_IDS:
                    print(f"✅ Valid Object ID (found in Entra ID list)")
                    KNOWN_OBJECT_IDS.remove(object_id)  # Remove to avoid duplicates
                else:
                    print(f"⚠️  Object ID not in the known list from Entra ID")
                    confirm = input("   Continue anyway? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                mapping.append({
                    "agent_name": agent_name,
                    "object_id": object_id,
                    "status": "Published with Identity",
                    "mapped_at": datetime.now().isoformat()
                })
                break
            else:
                print("❌ Invalid Object ID format. Should be like: 420c8552-5d64-4c44-869c-037ad07ef351")
    
    return mapping

def display_mapping(mapping):
    """Display the completed mapping."""
    
    print("\n" + "=" * 100)
    print("🎯 COMPLETED AGENT IDENTITY MAPPING")
    print("=" * 100)
    
    print(f"\n{'Agent Name':<30} {'Object ID':<40} {'Status':<20}")
    print("-" * 100)
    
    for item in mapping:
        name = item['agent_name'][:28]
        obj_id = item['object_id'] if item['object_id'] else "N/A"
        status = item['status']
        print(f"{name:<30} {obj_id:<40} {status:<20}")
    
    print("=" * 100)
    
    mapped_count = sum(1 for item in mapping if item['object_id'])
    print(f"\n✅ Successfully mapped: {mapped_count}/{len(mapping)} agents")

def save_mapping(mapping):
    """Save the mapping to a JSON file."""
    
    output = {
        "generated_at": datetime.now().isoformat(),
        "mapping_method": "manual_interactive",
        "agents": mapping
    }
    
    filename = f"agent_identity_mapping_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Mapping saved to: {filename}")
    return filename

def generate_rbac_commands(mapping):
    """Generate RBAC commands for mapped agents."""
    
    mapped_agents = [a for a in mapping if a.get('object_id')]
    
    if not mapped_agents:
        return
    
    print("\n" + "=" * 100)
    print("🔐 RBAC ASSIGNMENT COMMANDS")
    print("=" * 100)
    print("\nUse these commands to grant permissions:\n")
    
    for agent in mapped_agents:
        print(f"# {agent['agent_name']}")
        print(f"az role assignment create \\")
        print(f"  --assignee {agent['object_id']} \\")
        print(f"  --role \"Storage Blob Data Reader\" \\")
        print(f"  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>")
        print()

def generate_entra_search_guide(mapping):
    """Generate a guide for searching agents in Entra ID."""
    
    print("\n" + "=" * 100)
    print("🔍 FINDING YOUR AGENTS IN ENTRA ID PORTAL")
    print("=" * 100)
    print("\nTo identify which agent is which in the Entra ID portal:")
    print("\n1. Copy an Object ID from the mapping above")
    print("2. Go to Entra ID → Agent ID → All agent identities")
    print("3. Use the search box to search for the Object ID")
    print("4. Click on the agent to add custom attributes:\n")
    
    for agent in mapping:
        if agent.get('object_id'):
            print(f"   Object ID: {agent['object_id']}")
            print(f"   → Add custom attribute 'AgentName' = '{agent['agent_name']}'")
            print()

def main():
    print("=" * 100)
    print("🤖 Azure AI Foundry - Interactive Agent Identity Mapper")
    print("=" * 100)
    
    # Perform manual mapping
    mapping = manual_mapping()
    
    if not mapping:
        print("\n⚠️  No mappings created")
        return
    
    # Display results
    display_mapping(mapping)
    
    # Save to file
    filename = save_mapping(mapping)
    
    # Generate RBAC commands
    generate_rbac_commands(mapping)
    
    # Generate search guide
    generate_entra_search_guide(mapping)
    
    print("\n" + "=" * 100)
    print("✨ Done! Use the Object IDs to identify and manage your agents in Entra ID.")
    print("=" * 100)
    print("\n💡 Recommended next steps:")
    print("   1. Add custom security attributes in Entra ID for each agent")
    print("   2. Assign RBAC permissions using the commands above")
    print("   3. Configure conditional access policies")
    print("   4. Set up monitoring and alerting\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

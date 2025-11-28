#!/usr/bin/env python3
"""
Check which agents are V1 (classic) vs V2 (new) in your Azure AI Foundry project.

This diagnostic script helps you understand which API version was used to create
each agent in your project.

🔍 DETECTION LOGIC:
   - V1 (Classic): Agents created with create_agent() - no 'version' attribute
   - V2 (New): Agents created with create_version() - has 'version' attribute

Usage:
    # Check all agents
    python check_agent_versions.py
    
    # Export results to JSON
    python check_agent_versions.py --output version-report.json
    
    # Show summary only
    python check_agent_versions.py --summary

Environment Variables:
    AZURE_AI_PROJECT_ENDPOINT: Azure AI Foundry project endpoint URL

Authentication:
    Uses DefaultAzureCredential (run `az login` first)

Author: Azure AI Team
Last Updated: November 26, 2025
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Error: Required package not found: {e}")
    print("\n📦 Install required packages:")
    print("   pip install azure-ai-projects azure-identity python-dotenv")
    sys.exit(1)


def load_environment() -> bool:
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from: {env_path}")
        return True
    return False


def categorize_agents(agents: List[Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize agents into V1 (classic) and V2 (new) based on attributes.
    
    Args:
        agents: List of agent objects from agents.list()
        
    Returns:
        Dictionary with 'v1' and 'v2' keys containing categorized agents
    """
    categorized = {
        'v1': [],
        'v2': []
    }
    
    for agent in agents:
        agent_info = {
            'name': getattr(agent, 'name', 'Unknown'),
            'id': agent.id,
            'object_type': getattr(agent, 'object', 'Unknown')
        }
        
        # All new agents have versions.latest structure
        if hasattr(agent, 'versions') and agent.versions:
            latest = agent.versions.get('latest', {})
            agent_info['version'] = latest.get('version', 'Unknown')
            agent_info['created_at'] = latest.get('created_at')
            
            # Get model from definition
            definition = latest.get('definition', {})
            if isinstance(definition, dict):
                agent_info['model'] = definition.get('model', 'Unknown')
                agent_info['definition_kind'] = definition.get('kind', 'Unknown')
            elif hasattr(definition, 'model'):
                agent_info['model'] = getattr(definition, 'model', 'Unknown')
                agent_info['definition_kind'] = getattr(definition, 'kind', 'Unknown')
            else:
                agent_info['model'] = 'Unknown'
                agent_info['definition_kind'] = 'Unknown'
            
            agent_info['api_type'] = 'V2 (New)'
            categorized['v2'].append(agent_info)
        else:
            # Legacy V1 agents (if any exist without versions structure)
            agent_info['model'] = getattr(agent, 'model', 'Unknown')
            agent_info['created_at'] = getattr(agent, 'created_at', None)
            agent_info['api_type'] = 'V1 (Classic)'
            categorized['v1'].append(agent_info)
    
    return categorized


def format_timestamp(timestamp: int) -> str:
    """Convert Unix timestamp to readable date string."""
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return 'Unknown'


def print_agent_report(categorized: Dict[str, List[Dict[str, Any]]], summary_only: bool = False):
    """Print a formatted report of agent versions."""
    total_v1 = len(categorized['v1'])
    total_v2 = len(categorized['v2'])
    total_agents = total_v1 + total_v2
    
    print("\n" + "="*70)
    print("🔍 AZURE AI FOUNDRY AGENT VERSION REPORT")
    print("="*70)
    print(f"\n📊 SUMMARY:")
    print(f"   Total Agents: {total_agents}")
    print(f"   V1 (Classic): {total_v1} ({total_v1/total_agents*100:.1f}%)" if total_agents > 0 else "   V1 (Classic): 0")
    print(f"   V2 (New):     {total_v2} ({total_v2/total_agents*100:.1f}%)" if total_agents > 0 else "   V2 (New):     0")
    
    if summary_only:
        return
    
    # V1 (Classic) Agents
    if total_v1 > 0:
        print(f"\n" + "-"*70)
        print(f"📦 V1 (CLASSIC) AGENTS ({total_v1} total)")
        print(f"   Created with: create_agent()")
        print(f"   Characteristics: No versioning, OpenAI-compatible API")
        print("-"*70)
        
        for i, agent in enumerate(categorized['v1'], 1):
            print(f"\n{i}. {agent['name']}")
            print(f"   ID: {agent['id']}")
            print(f"   Model: {agent['model']}")
            print(f"   Created: {format_timestamp(agent['created_at'])}")
            print(f"   Object Type: {agent['object_type']}")
    
    # V2 (New) Agents
    if total_v2 > 0:
        print(f"\n" + "-"*70)
        print(f"🆕 V2 (NEW) AGENTS ({total_v2} total)")
        print(f"   Created with: create_version()")
        print(f"   Characteristics: Versioned, new features (workflows, tools)")
        print("-"*70)
        
        for i, agent in enumerate(categorized['v2'], 1):
            print(f"\n{i}. {agent['name']} (Version {agent['version']})")
            print(f"   ID: {agent['id']}")
            print(f"   Model: {agent['model']}")
            print(f"   Created: {format_timestamp(agent['created_at'])}")
            print(f"   Object Type: {agent['object_type']}")
    
    print("\n" + "="*70)


def export_to_json(categorized: Dict[str, List[Dict[str, Any]]], output_path: str):
    """Export categorized agents to JSON file."""
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_agents': len(categorized['v1']) + len(categorized['v2']),
            'v1_count': len(categorized['v1']),
            'v2_count': len(categorized['v2'])
        },
        'agents': categorized
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Check which agents are V1 (classic) vs V2 (new)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all agents
  python check_agent_versions.py
  
  # Export to JSON
  python check_agent_versions.py --output version-report.json
  
  # Show summary only
  python check_agent_versions.py --summary

For more information, see V1_VS_V2_AGENTS.md
        """
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Export report to JSON file'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary only (no detailed listing)'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_environment()
    
    # Get project endpoint from environment
    project_endpoint = os.getenv('AZURE_AI_PROJECT_ENDPOINT')
    if not project_endpoint:
        print("❌ Error: AZURE_AI_PROJECT_ENDPOINT environment variable not set")
        print("\n📝 Please set it in your .env file or environment:")
        print("   AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>")
        sys.exit(1)
    
    try:
        # Initialize client
        print(f"\n🔄 Connecting to Azure AI Foundry...")
        print(f"   Endpoint: {project_endpoint}")
        
        credential = DefaultAzureCredential()
        client = AIProjectClient(endpoint=project_endpoint, credential=credential)
        
        # List all agents
        print(f"\n🔍 Fetching agents...")
        agents = list(client.agents.list())
        
        if not agents:
            print("\n⚠️  No agents found in this project")
            return
        
        # Categorize agents
        categorized = categorize_agents(agents)
        
        # Print report
        print_agent_report(categorized, summary_only=args.summary)
        
        # Export if requested
        if args.output:
            export_to_json(categorized, args.output)
        
        # Recommendations
        if len(categorized['v1']) > 0 and not args.summary:
            print("\n💡 RECOMMENDATIONS:")
            print("   - V1 agents will continue to work but lack new features")
            print("   - Consider migrating to V2 for versioning and new capabilities")
            print("   - See V1_VS_V2_AGENTS.md for migration guidance")
        
    except AttributeError as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 This might indicate an SDK version mismatch.")
        print("   Try upgrading: pip install --upgrade azure-ai-projects")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure you're logged in: az login")
        print("   2. Verify AZURE_AI_PROJECT_ENDPOINT is correct")
        print("   3. Check network connectivity to Azure")
        sys.exit(1)


if __name__ == "__main__":
    main()

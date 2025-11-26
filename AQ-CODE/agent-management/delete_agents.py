#!/usr/bin/env python3
"""
Delete agents from Azure AI Foundry project.

This script provides a safe and efficient way to delete agents from your
Azure AI Foundry project. It supports deleting all agents or specific agents
by name, with a dry-run option for safety.

Usage:
    # Delete all agents
    python delete_agents.py --all
    
    # Delete specific agent by name
    python delete_agents.py --name "MyAgent"
    
    # Delete multiple specific agents
    python delete_agents.py --names "Agent1" "Agent2" "Agent3"
    
    # Dry run (list without deleting)
    python delete_agents.py --all --dry-run

Environment Variables:
    AZURE_AI_PROJECT_ENDPOINT: Azure AI Foundry project endpoint URL
                               Format: https://<account>.services.ai.azure.com/api/projects/<project>

Authentication:
    Uses DefaultAzureCredential which tries:
    1. Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
    2. Managed Identity (for Azure resources)
    3. Azure CLI (run `az login` first)
    4. Visual Studio Code
    5. Azure PowerShell

Examples:
    # Safe preview before deletion
    $ python delete_agents.py --all --dry-run
    Found 5 agent(s):
      - WeatherAgent (version: 1)
      - ResearchAgent (version: 2)
      - CodeAgent (version: 1)
    [DRY RUN] No agents were deleted.
    
    # Delete all agents
    $ python delete_agents.py --all
    Found 5 agent(s)...
    Deleting agents...
    ✓ Deleted: WeatherAgent
    ✓ Deleted: ResearchAgent
    ✓ Deleted: CodeAgent
    Completed: 3/3 agents deleted successfully.
    
    # Delete specific agents
    $ python delete_agents.py --names "TestAgent1" "TestAgent2"
    Deleting 2 agent(s)...
    ✓ Deleted: TestAgent1
    ✓ Deleted: TestAgent2
    Completed: 2/2 agents deleted successfully.

Requirements:
    pip install azure-ai-projects azure-identity

Author: Azure AI Team
Last Updated: November 26, 2025
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    from dotenv import load_dotenv
except ImportError as e:
    print("Error: Required packages not installed.")
    print("Run: pip install azure-ai-projects azure-identity python-dotenv")
    print(f"Details: {e}")
    sys.exit(1)

# Load environment variables from .env file in the same directory
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment variables from: {env_path}")
else:
    print(f"Note: .env file not found at {env_path}")
    print("Using system environment variables only.")


def get_client() -> AIProjectClient:
    """Create and return AIProjectClient.
    
    Returns:
        AIProjectClient: Initialized client for Azure AI Foundry
        
    Raises:
        SystemExit: If AZURE_AI_PROJECT_ENDPOINT is not set
    """
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("Error: AZURE_AI_PROJECT_ENDPOINT environment variable not set")
        print("\nSet it with:")
        print('  export AZURE_AI_PROJECT_ENDPOINT="https://<account>.services.ai.azure.com/api/projects/<project>"')
        print("\nFind your endpoint at: https://ai.azure.com → Your Project → Settings")
        sys.exit(1)
    
    # Try DefaultAzureCredential first, fallback to AzureCliCredential
    try:
        credential = DefaultAzureCredential()
        # Test the credential by making a quick call
        test_client = AIProjectClient(endpoint=endpoint, credential=credential)
        _ = list(test_client.agents.list())  # This will fail fast if auth is wrong
        return test_client
    except Exception as e:
        print(f"DefaultAzureCredential failed: {e}")
        print("Falling back to AzureCliCredential...")
        print("Make sure you're logged in: az login")
        credential = AzureCliCredential()
        return AIProjectClient(endpoint=endpoint, credential=credential)


def list_agents(client: AIProjectClient) -> List:
    """List all agents in the project.
    
    Args:
        client: AIProjectClient instance
        
    Returns:
        List of agent objects
    """
    try:
        agents = list(client.agents.list())
        return agents
    except AttributeError as e:
        print(f"Error: The Azure AI Projects SDK may not have the expected API. {e}")
        print("\nPlease ensure you have the latest SDK installed:")
        print("  pip install --upgrade azure-ai-projects azure-identity")
        return []
    except Exception as e:
        print(f"Error listing agents: {e}")
        return []


def delete_agent(client: AIProjectClient, agent_id: str, agent_name: str, dry_run: bool = False) -> bool:
    """Delete a specific agent by ID.
    
    Args:
        client: AIProjectClient instance
        agent_id: ID of the agent to delete
        agent_name: Name of the agent (for display purposes)
        dry_run: If True, only print what would be deleted
        
    Returns:
        True if successful (or dry run), False otherwise
    """
    if dry_run:
        print(f"[DRY RUN] Would delete: {agent_name} (ID: {agent_id})")
        return True
    
    try:
        client.agents.delete_agent(agent_id)
        print(f"✓ Deleted: {agent_name} (ID: {agent_id})")
        return True
    except Exception as e:
        print(f"✗ Error deleting {agent_name} (ID: {agent_id}): {e}")
        return False


def delete_all_agents(dry_run: bool = False):
    """Delete all agents in the project.
    
    Args:
        dry_run: If True, only preview what would be deleted
    """
    with get_client() as client:
        agents = list_agents(client)
        
        if not agents:
            print("No agents found.")
            return
        
        print(f"Found {len(agents)} agent(s):")
        for agent in agents:
            name = getattr(agent, 'name', 'Unknown')
            agent_id = agent.id
            print(f"  - {name} (ID: {agent_id})")
        
        if dry_run:
            print("\n[DRY RUN] No agents were deleted.")
            return
        
        print("\nDeleting agents...")
        success_count = 0
        for agent in agents:
            agent_name = getattr(agent, 'name', 'Unknown')
            agent_id = agent.id
            if delete_agent(client, agent_id, agent_name, dry_run):
                success_count += 1
        
        if not dry_run:
            print(f"\nCompleted: {success_count}/{len(agents)} agents deleted successfully.")


def delete_specific_agents(agent_names: List[str], dry_run: bool = False):
    """Delete specific agents by name.
    
    Args:
        agent_names: List of agent names to delete
        dry_run: If True, only preview what would be deleted
    """
    with get_client() as client:
        # First list all agents to find matching IDs
        agents = list_agents(client)
        if not agents:
            print("No agents found.")
            return
        
        print(f"Deleting {len(agent_names)} agent(s)...")
        success_count = 0
        
        for agent in agents:
            agent_name = getattr(agent, 'name', 'Unknown')
            agent_id = agent.id
            
            if agent_name in agent_names:
                if delete_agent(client, agent_id, agent_name, dry_run):
                    success_count += 1
        
        if not dry_run:
            print(f"\nCompleted: {success_count}/{len(agent_names)} agents deleted successfully.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Delete agents from Azure AI Foundry project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all agents (dry run)
  python delete_agents.py --all --dry-run
  
  # Delete all agents
  python delete_agents.py --all
  
  # Delete specific agent
  python delete_agents.py --name "MyAgent"
  
  # Delete multiple agents
  python delete_agents.py --names "Agent1" "Agent2" "Agent3"

Environment Variables:
  AZURE_AI_PROJECT_ENDPOINT    Your Azure AI Foundry project endpoint
                               (Find at: https://ai.azure.com → Project → Settings)

Authentication:
  Run 'az login' before executing this script, or set up service principal
  environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID).
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Delete all agents")
    group.add_argument("--name", type=str, help="Delete specific agent by name")
    group.add_argument("--names", nargs="+", help="Delete multiple agents by name")
    
    parser.add_argument("--dry-run", action="store_true", 
                       help="List agents without deleting (dry run)")
    
    args = parser.parse_args()
    
    try:
        if args.all:
            delete_all_agents(dry_run=args.dry_run)
        elif args.name:
            delete_specific_agents([args.name], dry_run=args.dry_run)
        elif args.names:
            delete_specific_agents(args.names, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

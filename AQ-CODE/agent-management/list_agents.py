#!/usr/bin/env python3
"""
List all agents in Azure AI Foundry project.

This script provides various ways to view agents in your Azure AI Foundry project,
including basic listing, detailed information, filtering, and export options.

🔄 SUPPORTS BOTH V1 (CLASSIC) AND V2 (NEW) AGENTS
   - V1 agents created with create_agent() (no version field)
   - V2 agents created with create_version() (has version field)
   - See V1_VS_V2_AGENTS.md for details

Usage:
    # Basic listing
    python list_agents.py
    
    # Detailed view with instructions and tools
    python list_agents.py --verbose
    
    # Export to JSON
    python list_agents.py --output agents.json
    
    # Export to YAML
    python list_agents.py --output agents.yaml
    
    # Filter by name pattern
    python list_agents.py --filter "Test*"
    
    # Show only names (useful for scripting)
    python list_agents.py --names-only

Environment Variables:
    AZURE_AI_PROJECT_ENDPOINT: Azure AI Foundry project endpoint URL

Authentication:
    Uses DefaultAzureCredential (run `az login` first)

Examples:
    # Basic listing
    $ python list_agents.py
    === Azure AI Foundry Agents ===
    Project: https://myproject.services.ai.azure.com/api/projects/demo
    Total Agents: 3
    
    1. WeatherAgent (version: 1)
       Model: gpt-4o
       Created: 2025-11-25 10:30:15
    
    # Verbose details
    $ python list_agents.py --verbose
    Agent: WeatherAgent
      Version: 1
      Model: gpt-4o
      Instructions: You are a helpful weather assistant...
      Tools: 1
        - FunctionTool: get_weather

Requirements:
    pip install azure-ai-projects azure-identity

Author: Azure AI Team
Last Updated: November 26, 2025
"""

import argparse
import json
import os
import sys
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import List, Optional

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
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
    """Create and return AIProjectClient."""
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("Error: AZURE_AI_PROJECT_ENDPOINT environment variable not set")
        sys.exit(1)
    
    credential = DefaultAzureCredential()
    return AIProjectClient(endpoint=endpoint, credential=credential)


def list_agents_basic(agents: List, endpoint: str):
    """Display basic agent information.
    
    Args:
        agents: List of agent objects
        endpoint: Project endpoint URL
    """
    print("=== Azure AI Foundry Agents ===")
    print(f"Project: {endpoint}")
    print(f"\nTotal Agents: {len(agents)}\n")
    
    if not agents:
        print("No agents found.")
        return
    
    for idx, agent in enumerate(agents, 1):
        name = getattr(agent, 'name', 'Unknown')
        agent_id = getattr(agent, 'id', 'Unknown')
        
        # Get latest version details if available
        model = 'Unknown'
        created_at = None
        tools = []
        version_info = None
        
        if hasattr(agent, 'versions') and agent.versions:
            latest = agent.versions.get('latest', {})
            version_info = latest.get('version', 'N/A')
            created_at = latest.get('created_at')
            
            # Get definition details
            definition = latest.get('definition', {})
            if isinstance(definition, dict):
                model = definition.get('model', 'Unknown')
                tools = definition.get('tools', [])
            elif hasattr(definition, 'model'):
                model = getattr(definition, 'model', 'Unknown')
                tools = getattr(definition, 'tools', [])
        
        print(f"{idx}. {name} (ID: {agent_id})")
        if version_info:
            print(f"   Version: {version_info}")
        print(f"   Model: {model}")
        
        # Display created timestamp if available
        if created_at:
            from datetime import datetime
            try:
                created = datetime.fromtimestamp(created_at)
                print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print(f"   Created: {created_at}")
        
        # Count tools
        if tools:
            tool_types = []
            for tool in tools:
                if isinstance(tool, dict):
                    tool_types.append(tool.get('type', 'unknown'))
                else:
                    tool_types.append(getattr(tool, 'type', type(tool).__name__))
            print(f"   Tools: {len(tools)} ({', '.join(set(tool_types))})")
        else:
            print(f"   Tools: 0")
        
        print()


def list_agents_verbose(agents: List):
    """Display detailed agent information.
    
    Args:
        agents: List of agent objects
    """
    print("=== Azure AI Foundry Agents (Detailed) ===\n")
    
    if not agents:
        print("No agents found.")
        return
    
    for agent in agents:
        name = getattr(agent, 'name', 'Unknown')
        agent_id = getattr(agent, 'id', 'Unknown')
        
        # Get latest version details
        model = 'Unknown'
        created_at = None
        instructions = None
        tools = []
        version_info = None
        definition_kind = 'Unknown'
        
        if hasattr(agent, 'versions') and agent.versions:
            latest = agent.versions.get('latest', {})
            version_info = latest.get('version', 'N/A')
            created_at = latest.get('created_at')
            
            # Get definition details
            definition = latest.get('definition', {})
            if isinstance(definition, dict):
                definition_kind = definition.get('kind', 'Unknown')
                model = definition.get('model', 'Unknown')
                instructions = definition.get('instructions', '')
                tools = definition.get('tools', [])
            elif hasattr(definition, 'kind'):
                definition_kind = getattr(definition, 'kind', 'Unknown')
                model = getattr(definition, 'model', 'Unknown')
                instructions = getattr(definition, 'instructions', '')
                tools = getattr(definition, 'tools', [])
        
        print(f"Agent: {name}")
        print(f"  ID: {agent_id}")
        if version_info:
            print(f"  Version: {version_info}")
        print(f"  Type: {definition_kind}")
        print(f"  Model: {model}")
        
        if created_at:
            from datetime import datetime
            try:
                created = datetime.fromtimestamp(created_at)
                print(f"  Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print(f"  Created: {created_at}")
        
        if instructions:
            inst_display = instructions[:200]
            if len(instructions) > 200:
                inst_display += "..."
            print(f"  Instructions:")
            for line in inst_display.split('\n'):
                print(f"    {line}")
        
        if tools:
            print(f"  Tools: {len(tools)}")
            for tool in tools:
                if isinstance(tool, dict):
                    tool_type = tool.get('type', 'unknown')
                    print(f"    - {tool_type}")
                    if 'function' in tool:
                        func = tool['function']
                        if 'name' in func:
                            print(f"      Name: {func['name']}")
                        if 'description' in func:
                            print(f"      Description: {func['description']}")
                else:
                    tool_type = getattr(tool, 'type', type(tool).__name__)
                    print(f"    - {tool_type}")
                    if hasattr(tool, 'function') and tool.function:
                        func = tool.function
                        if hasattr(func, 'name'):
                            print(f"      Name: {func.name}")
                        if hasattr(func, 'description'):
                            print(f"      Description: {func.description}")
        else:
            print(f"  Tools: 0")
        
        if hasattr(agent, 'metadata') and agent.metadata:
            print(f"  Metadata:")
            for key, value in agent.metadata.items():
                print(f"    {key}: {value}")
        
        print("\n" + "─" * 60 + "\n")


def list_agents_names_only(agents: List):
    """Display only agent names (useful for scripting).
    
    Args:
        agents: List of agent objects
    """
    for agent in agents:
        print(agent.name)


def export_agents(agents: List, output_path: str, pretty: bool = True):
    """Export agents to JSON or YAML file.
    
    Args:
        agents: List of agent objects
        output_path: Output file path
        pretty: If True, format output for readability
    """
    # Convert agents to dictionaries
    agents_data = []
    for agent in agents:
        agent_dict = {
            "name": getattr(agent, 'name', 'Unknown'),
            "id": getattr(agent, 'id', 'Unknown'),
            "model": getattr(agent, 'model', 'Unknown'),
        }
        
        if hasattr(agent, 'instructions'):
            agent_dict["instructions"] = agent.instructions
        
        if hasattr(agent, 'created_at'):
            agent_dict["created_at"] = str(agent.created_at)
        
        tools = getattr(agent, 'tools', [])
        if tools:
            agent_dict["tools"] = []
            for tool in tools:
                tool_dict = {"type": getattr(tool, 'type', type(tool).__name__)}
                
                if hasattr(tool, 'function') and tool.function:
                    tool_dict["function"] = {
                        "name": getattr(tool.function, 'name', None),
                        "description": getattr(tool.function, 'description', None),
                    }
                
                agent_dict["tools"].append(tool_dict)
        
        if hasattr(agent, 'metadata') and agent.metadata:
            agent_dict["metadata"] = dict(agent.metadata)
        
        agents_data.append(agent_dict)
    
    # Determine format from extension
    is_yaml = output_path.endswith(('.yaml', '.yml'))
    
    # Export
    with open(output_path, 'w') as f:
        if is_yaml:
            try:
                import yaml
                yaml.dump(agents_data, f, default_flow_style=False, sort_keys=False)
            except ImportError:
                print("Warning: PyYAML not installed. Falling back to JSON.")
                json.dump(agents_data, f, indent=2 if pretty else None)
        else:
            json.dump(agents_data, f, indent=2 if pretty else None)
    
    print(f"Exported {len(agents_data)} agent(s) to: {output_path}")


def filter_agents(agents: List, pattern: str) -> List:
    """Filter agents by name pattern.
    
    Args:
        agents: List of agent objects
        pattern: Wildcard pattern (e.g., "Test*", "*Agent", "Demo*")
        
    Returns:
        Filtered list of agents
    """
    return [agent for agent in agents 
            if fnmatch(getattr(agent, 'name', ''), pattern)]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="List agents in Azure AI Foundry project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic listing
  python list_agents.py
  
  # Detailed view
  python list_agents.py --verbose
  
  # Export to JSON
  python list_agents.py --output agents.json
  
  # Export to YAML
  python list_agents.py --output agents.yaml
  
  # Filter by pattern
  python list_agents.py --filter "Test*"
  
  # Only show names (for scripting)
  python list_agents.py --names-only

Environment Variables:
  AZURE_AI_PROJECT_ENDPOINT    Your Azure AI Foundry project endpoint
        """
    )
    
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed information")
    parser.add_argument("--output", "-o", type=str,
                       help="Export to file (JSON or YAML based on extension)")
    parser.add_argument("--filter", "-f", type=str,
                       help="Filter agents by name pattern (supports wildcards)")
    parser.add_argument("--names-only", action="store_true",
                       help="Show only agent names (useful for scripting)")
    parser.add_argument("--pretty", action="store_true", default=True,
                       help="Pretty print JSON output (default: True)")
    
    args = parser.parse_args()
    
    try:
        with get_client() as client:
            # Get endpoint for display
            endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
            
            # List agents
            agents = list(client.agents.list())
            
            # Apply filter if specified
            if args.filter:
                agents = filter_agents(agents, args.filter)
                if not agents:
                    print(f"No agents matching pattern: {args.filter}")
                    return
            
            # Output based on options
            if args.output:
                export_agents(agents, args.output, pretty=args.pretty)
            elif args.names_only:
                list_agents_names_only(agents)
            elif args.verbose:
                list_agents_verbose(agents)
            else:
                list_agents_basic(agents, endpoint)
    
    except AttributeError as e:
        print(f"Error: The Azure AI Projects SDK may not have the expected API. {e}")
        print("\nPlease ensure you have the latest SDK installed:")
        print("  pip install --upgrade azure-ai-projects azure-identity")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

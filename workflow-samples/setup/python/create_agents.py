#!/usr/bin/env python3
"""
Create Azure AI Foundry agents from YAML definitions.

This is the Python equivalent of the .NET CreateAgents/Program.cs.
It reads agent definition YAML files, creates agents in Azure AI Foundry,
and outputs environment variable commands for shell configuration.

Usage:
    python create_agents.py [yaml_files...]
    
    If no files specified, processes all *.yaml files in parent directory.

Environment Variables Required:
    FOUNDRY_PROJECT_ENDPOINT         - Azure AI Foundry project endpoint
    FOUNDRY_MODEL_DEPLOYMENT_NAME    - Model deployment name (e.g., gpt-4o-mini)
    FOUNDRY_CONNECTION_GROUNDING_TOOL - Bing grounding connection name (optional)

Example:
    export FOUNDRY_PROJECT_ENDPOINT="https://myresource.services.ai.azure.com/api/projects/myproject"
    export FOUNDRY_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
    export FOUNDRY_CONNECTION_GROUNDING_TOOL="mybinggrounding"
    
    python create_agents.py
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

import yaml
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    Agent,
    CodeInterpreterTool,
    BingGroundingTool,
    OpenApiTool,
    OpenApiAnonymousAuthDetails,
    OpenApiToolDefinition,
)
from azure.identity import AzureCliCredential
from azure.core.credentials import TokenCredential


class AgentCreator:
    """Creates Azure AI Foundry agents from YAML definitions."""
    
    def __init__(self, project_endpoint: str, credential: TokenCredential):
        """
        Initialize the agent creator.
        
        Args:
            project_endpoint: Azure AI Foundry project endpoint URL
            credential: Azure credential for authentication
        """
        self.project_endpoint = project_endpoint
        self.credential = credential
        self.client = AIProjectClient.from_connection_string(
            conn_str=project_endpoint,
            credential=credential
        )
        
    def substitute_env_vars(self, text: str) -> str:
        """
        Replace ${VAR_NAME} placeholders with environment variable values.
        
        Args:
            text: Text containing ${VAR_NAME} placeholders
            
        Returns:
            Text with substituted values
            
        Raises:
            ValueError: If required environment variable is not set
        """
        def replacer(match):
            var_name = match.group(1)
            value = os.getenv(var_name)
            if value is None:
                raise ValueError(f"Environment variable not set: {var_name}")
            return value
        
        return re.sub(r'\$\{(\w+)\}', replacer, text)
    
    def parse_yaml_with_env_vars(self, yaml_path: Path) -> Dict[str, Any]:
        """
        Parse YAML file and substitute environment variables.
        
        Args:
            yaml_path: Path to YAML file
            
        Returns:
            Parsed YAML content with substituted values
        """
        with open(yaml_path, 'r') as f:
            content = f.read()
        
        # Substitute environment variables
        content = self.substitute_env_vars(content)
        
        # Parse YAML
        return yaml.safe_load(content)
    
    def create_tools(self, tools_config: List[Dict[str, Any]]) -> List[Any]:
        """
        Create tool objects from YAML tool configurations.
        
        Args:
            tools_config: List of tool configurations from YAML
            
        Returns:
            List of tool objects for agent creation
        """
        tools = []
        
        for tool_config in tools_config:
            tool_type = tool_config.get('type')
            
            if tool_type == 'code_interpreter':
                tools.append(CodeInterpreterTool())
                
            elif tool_type == 'bing_grounding':
                # Bing grounding tool with connection
                tool = BingGroundingTool()
                if 'options' in tool_config and 'tool_connections' in tool_config['options']:
                    # Note: Connection configuration handled by Azure AI Foundry
                    pass
                tools.append(tool)
                
            elif tool_type == 'openapi':
                # OpenAPI tool with inline specification
                options = tool_config.get('options', {})
                spec = options.get('specification')
                
                if isinstance(spec, str):
                    spec = json.loads(spec)
                
                tool_def = OpenApiToolDefinition(
                    name=tool_config.get('id'),
                    description=tool_config.get('description'),
                    spec=spec,
                    auth=OpenApiAnonymousAuthDetails()
                )
                tools.append(OpenApiTool(tool_definition=tool_def))
        
        return tools
    
    def create_agent_from_yaml(self, yaml_path: Path) -> Agent:
        """
        Create an agent in Azure AI Foundry from YAML definition.
        
        Args:
            yaml_path: Path to agent definition YAML file
            
        Returns:
            Created Agent object
        """
        print(f"\n📄 Processing: {yaml_path.name}")
        
        # Parse YAML
        config = self.parse_yaml_with_env_vars(yaml_path)
        
        # Extract agent configuration
        agent_type = config.get('type')
        if agent_type != 'foundry_agent':
            raise ValueError(f"Unsupported agent type: {agent_type}")
        
        name = config.get('name')
        description = config.get('description', '')
        instructions = config.get('instructions', '')
        model_id = config.get('model', {}).get('id')
        tools_config = config.get('tools', [])
        
        # Create tools
        tools = self.create_tools(tools_config) if tools_config else None
        
        # Create agent
        agent = self.client.agents.create_agent(
            model=model_id,
            name=name,
            description=description,
            instructions=instructions,
            tools=tools
        )
        
        print(f"  ✓ Created agent: {agent.name}")
        print(f"    ID:          {agent.id}")
        print(f"    Model:       {model_id}")
        print(f"    Description: {description}")
        if tools:
            print(f"    Tools:       {len(tools)} tool(s)")
        
        return agent
    
    def format_env_var_name(self, agent_name: str) -> str:
        """
        Format agent name as environment variable name.
        
        Args:
            agent_name: Agent name from YAML
            
        Returns:
            Environment variable name (e.g., FOUNDRY_AGENT_ANSWER)
        """
        return f"FOUNDRY_AGENT_{agent_name.upper()}"
    
    def generate_export_commands(self, agents: List[tuple[str, Agent]]) -> tuple[str, str]:
        """
        Generate shell export commands for created agents.
        
        Args:
            agents: List of (yaml_filename, Agent) tuples
            
        Returns:
            Tuple of (bash_commands, powershell_commands)
        """
        bash_lines = []
        powershell_lines = []
        
        bash_lines.append("# Add these to your ~/.bashrc or ~/.zshrc:")
        bash_lines.append("")
        
        powershell_lines.append("# Run these commands in PowerShell:")
        powershell_lines.append("")
        
        for yaml_name, agent in agents:
            env_var = self.format_env_var_name(agent.name)
            bash_lines.append(f'export {env_var}="{agent.id}"')
            powershell_lines.append(f'$env:{env_var} = "{agent.id}"')
        
        return '\n'.join(bash_lines), '\n'.join(powershell_lines)


def main():
    """Main execution function."""
    
    # Check required environment variables
    project_endpoint = os.getenv('FOUNDRY_PROJECT_ENDPOINT')
    if not project_endpoint:
        print("❌ Error: FOUNDRY_PROJECT_ENDPOINT environment variable not set")
        print("\nSet it with:")
        print('  export FOUNDRY_PROJECT_ENDPOINT="https://your-resource.services.ai.azure.com/api/projects/your-project"')
        sys.exit(1)
    
    model_deployment = os.getenv('FOUNDRY_MODEL_DEPLOYMENT_NAME')
    if not model_deployment:
        print("❌ Error: FOUNDRY_MODEL_DEPLOYMENT_NAME environment variable not set")
        print("\nSet it with:")
        print('  export FOUNDRY_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"')
        sys.exit(1)
    
    print(f"\n🚀 Creating Azure AI Foundry Agents")
    print(f"   Project: {project_endpoint}")
    print(f"   Model:   {model_deployment}")
    
    # Get YAML files to process
    if len(sys.argv) > 1:
        yaml_files = [Path(f) for f in sys.argv[1:]]
    else:
        # Process all .yaml files in parent directory
        setup_dir = Path(__file__).parent.parent
        yaml_files = sorted(setup_dir.glob('*.yaml'))
    
    if not yaml_files:
        print("\n❌ No YAML files found")
        sys.exit(1)
    
    print(f"\n📋 Found {len(yaml_files)} agent definition(s)")
    
    # Create agent creator
    try:
        credential = AzureCliCredential()
        creator = AgentCreator(project_endpoint, credential)
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nMake sure you're logged in with Azure CLI:")
        print("  az login")
        sys.exit(1)
    
    # Create agents
    created_agents = []
    errors = []
    
    for yaml_path in yaml_files:
        try:
            agent = creator.create_agent_from_yaml(yaml_path)
            created_agents.append((yaml_path.stem, agent))
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors.append((yaml_path.name, str(e)))
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"✅ Successfully created {len(created_agents)} agent(s)")
    if errors:
        print(f"❌ Failed to create {len(errors)} agent(s)")
        for filename, error in errors:
            print(f"   - {filename}: {error}")
    
    if not created_agents:
        print("\n❌ No agents were created")
        sys.exit(1)
    
    # Generate export commands
    bash_cmds, ps_cmds = creator.generate_export_commands(created_agents)
    
    print(f"\n{'='*80}")
    print("\n📋 BASH/ZSH Configuration:")
    print(f"\n{bash_cmds}\n")
    
    print(f"{'='*80}")
    print("\n📋 PowerShell Configuration:")
    print(f"\n{ps_cmds}\n")
    
    print(f"{'='*80}")
    print("\n✅ Setup complete!")
    print("\n💡 Next steps:")
    print("   1. Copy the export commands above to your shell")
    print("   2. Run the commands to set environment variables")
    print("   3. Test workflows with the .NET demo:")
    print("      cd dotnet/samples/GettingStarted/Workflows/Declarative/ExecuteWorkflow")
    print("      dotnet run Marketing")


if __name__ == '__main__':
    main()

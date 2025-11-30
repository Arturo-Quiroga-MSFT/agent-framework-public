import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agent_framework import MCPStdioTool

async def test():
    mcp_server_path = Path('MssqlMcp/Node/dist/index.js')
    mcp_env = {
        'SERVER_NAME': os.getenv('SERVER_NAME', ''),
        'DATABASE_NAME': os.getenv('DATABASE_NAME', ''),
        'SQL_USERNAME': os.getenv('SQL_USERNAME', ''),
        'SQL_PASSWORD': os.getenv('SQL_PASSWORD', ''),
        'TRUST_SERVER_CERTIFICATE': os.getenv('TRUST_SERVER_CERTIFICATE', 'true'),
        'READONLY': os.getenv('READONLY', 'false'),
    }
    
    print("Starting MCP server...")
    async with MCPStdioTool(
        name='mssql',
        command='node',
        args=[str(mcp_server_path)],
        env=mcp_env,
        description='Microsoft SQL Server database operations',
    ) as mcp_tool:
        print(f'✅ Connected to MCP server')
        
        # MCPStdioTool loads tools automatically and exposes them via .functions property
        tools = mcp_tool.functions
        print(f'Number of tools: {len(tools)}')
        print(f'\nTool names:')
        
        tool_names = [tool.name for tool in tools]
        for name in sorted(set(tool_names)):
            count = tool_names.count(name)
            if count > 1:
                print(f'  ❌ {name} (DUPLICATE - appears {count} times)')
            else:
                print(f'  ✅ {name}')
        
        print(f'\nTotal unique tools: {len(set(tool_names))}')
        print(f'Total tool instances: {len(tool_names)}')
        
        if len(tool_names) != len(set(tool_names)):
            print(f'\n⚠️  WARNING: Found {len(tool_names) - len(set(tool_names))} duplicate tool names!')
            print('This will cause "Function tools must have unique names" error.')
        else:
            print(f'\n✅ All tool names are unique!')

asyncio.run(test())

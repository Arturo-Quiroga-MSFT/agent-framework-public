# Copyright (c) Microsoft. All rights reserved.

"""
Interactive DBA Assistant

An AI-powered assistant for SQL Database administrators to manage and query
Azure SQL databases using natural language. Built on Microsoft Agent Framework
and integrated with the Microsoft MSSQL MCP Server.

Features:
- Natural language database queries
- Schema exploration and documentation
- Performance analysis and tuning recommendations
- Health monitoring and diagnostics
- Maintenance task guidance
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✓ Loaded environment from: {env_path}")
else:
    print(f"⚠️  No .env file found at: {env_path}")
    load_dotenv()  # Try to load from default locations

from agent_framework import MCPStdioTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential


async def run_interactive_session() -> None:
    """
    Interactive DBA assistant session with natural language interface.
    """
    print(f"\n{'='*80}")
    print("INTERACTIVE DBA ASSISTANT")
    print("Ask questions about your databases in natural language")
    print("Type 'exit' to quit")
    print(f"{'='*80}\n")
    
    # Get server name and database from environment
    server = os.getenv("SERVER_NAME", "localhost")
    database = os.getenv("DATABASE_NAME", "master")
    
    print(f"📡 Using server: {server}")
    print(f"📊 Database: {database}")
    print(f"⏳ Starting MCP server...\n")
    
    # Path to the MCP server
    mcp_server_path = Path(__file__).parent / "MssqlMcp" / "Node" / "dist" / "index.js"
    
    if not mcp_server_path.exists():
        print(f"❌ MCP server not found at: {mcp_server_path}")
        print("Please build the MCP server first:")
        print("  cd MssqlMcp/Node")
        print("  npm install")
        print("  npm run build")
        return
    
    # Create MCP tool with environment variables for SQL authentication
    mcp_env = {
        "SERVER_NAME": server,
        "DATABASE_NAME": database,
        "SQL_USERNAME": os.getenv("SQL_USERNAME", ""),
        "SQL_PASSWORD": os.getenv("SQL_PASSWORD", ""),
        "TRUST_SERVER_CERTIFICATE": os.getenv("TRUST_SERVER_CERTIFICATE", "true"),
        "READONLY": os.getenv("READONLY", "false"),
    }
    
    async with (
        AzureCliCredential() as credential,
        MCPStdioTool(
            name="mssql",
            command="node",
            args=[str(mcp_server_path)],
            env=mcp_env,
            description="Microsoft SQL Server database operations and management tools",
        ) as mcp_tool,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="InteractiveDBA",
            instructions=f"""You are a helpful SQL Server DBA assistant for server '{server}' and database '{database}'.

You help database administrators with:
- Health monitoring and diagnostics
- Performance analysis and tuning
- Query optimization
- Index recommendations
- Troubleshooting blocking and deadlocks
- Capacity planning
- Maintenance task guidance

IMPORTANT: 
- First connect to the database using mssql_connect with the server name: {server}
- Use the connection ID returned for all subsequent database operations
- Maintain context from our conversation
- Remember what database we're working with and previous questions

Always explain your findings clearly and provide actionable recommendations.
When suggesting SQL queries, ensure they are safe and read-only unless explicitly asked for changes.""",
            tools=mcp_tool,
        ) as agent,
    ):
        print(f"✅ MCP server started")
        print(f"✅ Agent ready")
        print("💬 You can now ask questions...\n")
        
        while True:
            try:
                user_input = input("DBA> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                print("\n🤖 Agent: ", end="", flush=True)
                
                # Stream the response
                async for chunk in agent.run_stream(user_input):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                
                print("\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")



async def main() -> None:
    """Main entry point - starts the interactive DBA assistant."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       Interactive DBA Assistant                              ║
║                   Powered by Microsoft Agent Framework                       ║
║                         & MSSQL MCP Server                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Check if Azure credentials are configured
    if not os.getenv("AZURE_AI_PROJECT_ENDPOINT"):
        print("⚠️  Warning: AZURE_AI_PROJECT_ENDPOINT not set")
        print("   Create a .env file with your Azure AI project endpoint")
        print("   Copy .env.template to .env and fill in your values\n")
    
    # Start interactive session directly
    await run_interactive_session()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise

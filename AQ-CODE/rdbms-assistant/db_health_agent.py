# Copyright (c) Microsoft. All rights reserved.

"""
Database Health Monitor Agent

This agent monitors SQL database health, checking for common issues like:
- Index fragmentation
- Blocking sessions
- Database size and growth
- Performance bottlenecks

Based on: /maf-upstream/python/samples/getting_started/agents/azure_ai_agent/azure_ai_basic.py
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Import MCP tools
from mcp_client import (
    mssql_list_servers,
    mssql_connect,
    mssql_disconnect,
    mssql_list_databases,
    mssql_run_query,
    mssql_get_connection_details,
    QUERY_TOOLS,
    DBA_QUERY_TEMPLATES,
)


async def check_database_health(server_name: str, database_name: str | None = None) -> None:
    """
    Run a comprehensive health check on a database.
    
    Args:
        server_name: SQL Server name (from mssql_list_servers)
        database_name: Optional specific database, otherwise checks all
    """
    print(f"\n{'='*80}")
    print(f"DATABASE HEALTH CHECK")
    print(f"Server: {server_name}")
    print(f"Database: {database_name or 'All databases'}")
    print(f"{'='*80}\n")
    
    # For authentication, run `az login` in terminal
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="DatabaseHealthMonitor",
            instructions="""You are an expert SQL Server DBA focused on database health monitoring.
            
Your responsibilities:
1. Check index fragmentation and recommend maintenance
2. Detect blocking sessions and deadlocks
3. Monitor database size and space usage
4. Identify performance bottlenecks
5. Review query performance metrics

Always provide:
- Clear diagnosis of issues found
- Severity assessment (Critical, Warning, Info)
- Specific recommendations for remediation
- SQL commands to fix issues (when applicable)

Be concise but thorough. Prioritize critical issues first.""",
            tools=QUERY_TOOLS,
        ) as agent,
    ):
        # Run health checks
        queries = [
            "Connect to the server and check overall database health",
            "Check for index fragmentation above 30% that needs attention",
            "Look for any blocking sessions causing performance issues",
            "Show database size and space utilization",
            "Identify the top 5 most resource-intensive queries",
        ]
        
        for query in queries:
            print(f"\n📊 {query}")
            print("-" * 80)
            result = await agent.run(query)
            print(f"{result}\n")


async def streaming_health_check(server_name: str) -> None:
    """
    Run health check with streaming output for real-time feedback.
    
    Args:
        server_name: SQL Server name
    """
    print(f"\n{'='*80}")
    print(f"STREAMING HEALTH CHECK - Real-time Analysis")
    print(f"Server: {server_name}")
    print(f"{'='*80}\n")
    
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="DatabaseHealthMonitor",
            instructions="""You are an expert SQL Server DBA performing rapid health assessments.
            
Provide immediate analysis of:
- Critical performance issues
- Database availability concerns  
- Resource contention problems
- Maintenance tasks needed

Stream your findings as you discover them.""",
            tools=QUERY_TOOLS,
        ) as agent,
    ):
        query = f"Perform a quick health assessment of server {server_name} and report critical findings"
        print(f"🔍 Query: {query}\n")
        print("📡 Live Results:\n")
        
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


async def interactive_dba_session() -> None:
    """
    Interactive session where DBA can ask questions naturally.
    """
    print(f"\n{'='*80}")
    print("INTERACTIVE DBA SESSION")
    print("Ask questions about your databases in natural language")
    print("Type 'exit' to quit")
    print(f"{'='*80}\n")
    
    # Get server name from user
    print("Available servers (example - actual list from mssql_list_servers):")
    print("  - localhost")
    print("  - myserver.database.windows.net")
    print()
    
    server = input("Enter server name: ").strip()
    if not server:
        server = "localhost"
    
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="InteractiveDBA",
            instructions=f"""You are a helpful SQL Server DBA assistant for server '{server}'.

You help database administrators with:
- Health monitoring and diagnostics
- Performance analysis and tuning
- Query optimization
- Index recommendations
- Troubleshooting blocking and deadlocks
- Capacity planning
- Maintenance task guidance

Always explain your findings clearly and provide actionable recommendations.
When suggesting SQL queries, ensure they are safe and read-only unless explicitly asked for changes.""",
            tools=QUERY_TOOLS,
        ) as agent,
    ):
        print(f"\n✅ Connected to {server}")
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
    """Main entry point - demonstrates different usage patterns."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   SQL Database Health Monitor Agent                          ║
║                   Powered by Microsoft Agent Framework                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Check if Azure credentials are configured
    if not os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING"):
        print("⚠️  Warning: AZURE_AI_PROJECT_CONNECTION_STRING not set")
        print("   Create a .env file with your Azure AI project connection string")
        print("   Copy .env.template to .env and fill in your values\n")
    
    print("Choose a demo mode:")
    print("  1. Comprehensive Health Check (non-streaming)")
    print("  2. Quick Health Assessment (streaming)")
    print("  3. Interactive DBA Session (recommended)")
    print()
    
    choice = input("Enter choice (1-3) [3]: ").strip() or "3"
    
    if choice == "1":
        await check_database_health("localhost", "AdventureWorks")
    elif choice == "2":
        await streaming_health_check("localhost")
    elif choice == "3":
        await interactive_dba_session()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise

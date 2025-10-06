# Copyright (c) Microsoft. All rights reserved.

"""
NL2SQL Pipeline using MSSQL MCP Server - DevUI Version

This workflow uses the Node.js MSSQL MCP server for robust SQL operations.
The MCP server handles authentication, query validation, and SQL execution.

ARCHITECTURE:
1. 🎯 Intent Analyzer - Understands user's natural language question
2. 📊 Schema Expert - Uses list_table and describe_table MCP tools
3. 💻 SQL Generator - Writes SQL Server queries  
4. ✅ SQL Validator - Validates syntax and logic
5. 🔧 Query Executor - Uses read_data MCP tool to execute
6. 📝 Results Formatter - Formats results with insights

MCP SERVER TOOLS USED:
- list_table: Lists all tables in the database
- describe_table: Gets table schema (columns and types)
- read_data: Executes SELECT queries with security validation

PREREQUISITES:
- Azure OpenAI access configured via .env file
- MSSQL MCP Server built and configured in MssqlMcp/Node/
- Azure SQL Database credentials in MssqlMcp/Node/.env
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agent_framework import (
    ChatMessage,
    Executor,
    MCPStdioTool,
    Role,
    SequentialBuilder,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import setup_observability
from agent_framework_devui import serve
from azure.identity import AzureCliCredential

# Load environment variables
load_dotenv()


class NL2SQLInput(BaseModel):
    """Input model for NL2SQL queries."""
    
    question: str = Field(
        description="Natural language question about the database"
    )
    database_context: str | None = Field(
        default=None,
        description="Optional context about the database or specific requirements"
    )


class InputDispatcher(Executor):
    """Dispatcher that converts user input to conversation for the agent pipeline."""
    
    @handler
    async def dispatch(self, input_data: NL2SQLInput, ctx: WorkflowContext) -> None:
        """Convert input to conversation and pass to agents."""
        user_message = ChatMessage(
            content=input_data.question,
            author_name="user",
            role=Role.USER
        )
        
        if input_data.database_context:
            user_message.content += f"\n\nContext: {input_data.database_context}"
        
        # Send conversation to next executor
        await ctx.send_message([user_message])


class SequentialWorkflowExecutor(Executor):
    """Executor that wraps a sequential workflow and runs it internally."""
    
    def __init__(self, agents: list, **kwargs):
        """Initialize with list of agents for sequential processing.
        
        Args:
            agents: List of agents to process sequentially
            **kwargs: Additional Executor arguments
        """
        super().__init__(**kwargs)
        self.agents = agents
        self._workflow = SequentialBuilder().participants(agents).build()
    
    @handler
    async def run_sequential(self, conversation: list[ChatMessage], ctx: WorkflowContext) -> None:
        """Run the sequential workflow and capture the final conversation.
        
        Args:
            conversation: Initial conversation messages
            ctx: WorkflowContext for sending the result
        """
        from agent_framework import WorkflowOutputEvent
        
        # Run the sequential workflow starting with the input conversation
        outputs: list[list[ChatMessage]] = []
        async for event in self._workflow.run_stream(conversation):
            if isinstance(event, WorkflowOutputEvent):
                outputs.append(event.data)
        
        # Send the final conversation to the next executor
        if outputs:
            await ctx.send_message(outputs[-1])



def format_nl2sql_results(conversation: list[ChatMessage]) -> str:
    """Format the complete NL2SQL conversation for display."""
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("🔍 NL2SQL PIPELINE WITH MCP SERVER")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("📋 PIPELINE STAGES:")
    output_lines.append("   1. 🎯 Intent Analysis")
    output_lines.append("   2. 📊 Schema Discovery (via MCP)")
    output_lines.append("   3. 💻 SQL Generation")
    output_lines.append("   4. ✅ SQL Validation")
    output_lines.append("   5. 🔧 Query Execution (via MCP)")
    output_lines.append("   6. 📝 Results Formatting")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Map author names to stage titles
    stage_map = {
        "user": ("💬 USER QUESTION", 1),
        "intent_analyzer": ("🎯 INTENT ANALYZER", 2),
        "schema_agent": ("📊 SCHEMA AGENT (with MCP tools)", 3),
        "sql_agent": ("💻 SQL AGENT (with MCP execution)", 4),
        "formatter": ("📝 RESULTS FORMATTER", 5),
    }
    
    for msg in conversation:
        author = msg.author_name or "unknown"
        if author in stage_map:
            title, stage_num = stage_map[author]
            output_lines.append("─" * 80)
            output_lines.append(f"{title}")
            output_lines.append("─" * 80)
            output_lines.append("")
            output_lines.append(msg.text)
            output_lines.append("")
    
    output_lines.append("=" * 80)
    output_lines.append("✅ NL2SQL Pipeline Complete - All Stages Executed")
    output_lines.append("=" * 80)
    
    return "\n".join(output_lines)


class NL2SQLOutputFormatter(Executor):
    """Executor that formats and saves the complete conversation."""
    
    @handler
    async def format_output(self, conversation: list[ChatMessage], ctx: WorkflowContext) -> None:
        """Format the conversation and save to file."""
        formatted_output = format_nl2sql_results(conversation)
        
        # Save to file
        output_dir = Path("workflow_outputs")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"nl2sql_mcp_pipeline_{timestamp}.txt"
        
        output_file.write_text(formatted_output, encoding='utf-8')
        print(f"\n📄 Results saved to: {output_file}")
        
        await ctx.yield_output(formatted_output)


def setup_tracing():
    """Set up observability tracing."""
    enable_console = os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true"
    
    if enable_console:
        print("📊 Tracing: Console tracing enabled")
        setup_observability(enable_sensitive_data=True)
    else:
        print("📊 Tracing: Disabled")


def launch_devui():
    """Launch the DevUI server with MCP-connected workflow."""
    mcp_server_path = Path(__file__).parent.parent.parent / "MssqlMcp" / "Node"
    
    print(f"🔌 Connecting to MSSQL MCP Server at: {mcp_server_path}")
    
    # Load MCP server's .env file to get database credentials
    mcp_env_file = mcp_server_path / ".env"
    if mcp_env_file.exists():
        from dotenv import dotenv_values
        mcp_env = dotenv_values(mcp_env_file)
        print(f"📋 Loaded MCP config: SERVER={mcp_env.get('SERVER_NAME')}, DB={mcp_env.get('DATABASE_NAME')}")
    else:
        print(f"⚠️  Warning: MCP .env file not found at {mcp_env_file}")
        mcp_env = {}
    
    # Merge MCP environment with current environment
    combined_env = {
        **os.environ,
        **mcp_env,  # MCP server's .env takes precedence
    }
    
    # Create MCP tool - connection happens lazily when agents use it
    mssql_mcp = MCPStdioTool(
        name="mssql_server",
        command="node",
        args=["dist/index.js"],
        env=combined_env,
        cwd=str(mcp_server_path),
        description="MSSQL Database server providing secure SQL operations",
    )
    
    # Create workflow with MCP tool - connection will be established when needed
    workflow = asyncio.run(create_workflow_with_tools(mssql_mcp))
    
    print("=" * 70)
    print("🚀 Launching NL2SQL Pipeline with MSSQL MCP Server")
    print("=" * 70)
    print("✅ Workflow Type: Sequential Agent Chain with MCP Tools")
    print("✅ Pipeline Agents:")
    print("    1. 🎯 Intent Analyzer - Understand natural language")
    print("    2. 📊 Schema Agent - Discover schema via MCP tools")
    print("    3. 💻 SQL Agent - Generate and execute SQL via MCP")
    print("    4. 📝 Results Formatter - Format with insights")
    print("✅ MCP Server: MSSQL Node.js Server")
    print("✅ MCP Tools: list_table, describe_table, read_data")
    print("✅ Web UI: http://localhost:8099")
    print("=" * 70)
    print()
    print("💡 Example questions to try:")
    print("   - Show me all tables in the database")
    print("   - What is the schema of the Company table?")
    print("   - Show me the top 10 companies by employee count")
    print("   - How many loans do we have in total?")
    print("=" * 70)
    
    # serve() blocks, MCP connection managed by tool lifecycle
    serve(entities=[workflow], port=8099)



async def create_workflow_with_tools(mssql_mcp: MCPStdioTool):
    """Create workflow with agents that have access to MSSQL MCP server tools."""
    
    # Create Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
    
    # Agent 1: Intent Analyzer (no tools needed)
    intent_analyzer = chat_client.create_agent(
        instructions=(
            "You're an intent analysis expert for NL2SQL. "
            "Analyze the user's natural language question and identify: "
            "1) Primary intent (SELECT, aggregate, filter, join, etc.) "
            "2) Entities mentioned (what data they want) "
            "3) Conditions/filters requested "
            "4) Required aggregations or calculations "
            "5) Expected output format. "
            "Provide clear, structured analysis in 3-5 bullet points."
        ),
        name="intent_analyzer",
    )
    
    # Agent 2: Schema Agent (with MCP tools for list_table and describe_table)
    schema_agent = chat_client.create_agent(
        instructions=(
            "You're a database schema expert. "
            "Based on the intent analysis, discover the database schema using your tools: "
            "\n"
            "TOOL USAGE:\n"
            "- list_table: Call with parameters=[] (empty array) to list all tables\n"
            "  Example: {\"parameters\": []}\n"
            "- describe_table: Call with tableName to see columns and types\n"
            "  Example: {\"tableName\": \"dbo.Company\"}\n"
            "\n"
            "IMPORTANT: Always provide 'parameters' as an empty array [] for list_table, never null or omit it.\n"
            "\n"
            "Then provide schema mapping: "
            "1) Relevant tables needed "
            "2) Specific columns to query "
            "3) JOIN relationships required "
            "4) Any schema limitations "
            "Be thorough and call tools as needed to understand the schema."
        ),
        name="schema_agent",
        tools=mssql_mcp,  # This agent can call MCP tools
    )
    
    # Agent 3: SQL Agent (generates SQL, validates, executes via read_data tool)
    sql_agent = chat_client.create_agent(
        instructions=(
            "You're an SQL Server expert with database execution capabilities. "
            "Based on the intent and schema above: "
            "1) Write an optimized SQL Server SELECT query "
            "2) Use proper SQL Server syntax (DB_NAME(), TOP N, etc.) "
            "3) Execute the query using the 'read_data' tool "
            "4) IMPORTANT: Pass your complete SQL query to the read_data tool's 'query' parameter "
            "5) Present the results returned by the tool "
            "The read_data tool will validate and execute your query safely. "
            "Always call the tool to get real data - don't just describe what would happen."
        ),
        name="sql_agent",
        tools=mssql_mcp,  # This agent can call read_data tool
    )
    
    # Agent 4: Results Formatter (interprets tool results)
    formatter_agent = chat_client.create_agent(
        instructions=(
            "You're a results presentation expert. "
            "Based on the complete conversation above (including tool execution results): "
            "1) Summarize what was requested in natural language "
            "2) Explain what the SQL query does in simple terms "
            "3) Present the actual query results clearly (look for tool_result messages) "
            "4) Provide insights or recommendations based on the actual data "
            "5) Note any limitations or caveats "
            "Create a clear, business-friendly summary highlighting the REAL DATA returned by the tools."
        ),
        name="formatter",
    )
    
    # Create sequential executor for the 4 agents
    sequential_executor = SequentialWorkflowExecutor(
        agents=[
            intent_analyzer,
            schema_agent,
            sql_agent,
            formatter_agent
        ],
        id="sequential_pipeline"
    )
    
    # Create dispatcher to handle input and convert to conversation
    dispatcher = InputDispatcher(id="input_dispatcher")
    
    # Create output formatter
    output_formatter = NL2SQLOutputFormatter(id="output_formatter")
    
    # Build complete workflow with input/output handling
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    builder.add_edge(dispatcher, sequential_executor)
    builder.add_edge(sequential_executor, output_formatter)
    
    workflow = builder.build()
    
    return workflow


if __name__ == "__main__":
    launch_devui()

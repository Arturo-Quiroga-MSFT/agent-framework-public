# Copyright (c) Microsoft. All rights reserved.
"""
NL2SQL Pipeline - Natural Language to SQL Workflow

A sequential workflow that converts natural language questions into SQL queries,
executes them against Azure SQL Database, and returns intelligent insights.

GOAL:
Transform user questions into accurate SQL queries, execute safely, and provide
natural language answers with context.

PIPELINE (Sequential):
1. Input Normalizer: Parse and structure user input
2. Schema Retriever: Fetch database schema context
3. SQL Generator Agent: LLM generates SQL from question + schema
4. SQL Validator: Safety checks and query optimization
5. Query Executor: Execute against Azure SQL DB
6. Results Interpreter Agent: Convert results to natural language insights

OUTPUT: Natural language answer with supporting data and insights

PREREQUISITES: 
- Azure OpenAI endpoint + deployment configured
- Azure SQL Database accessible
- MSSQL MCP server available
- az login authenticated

USAGE:
    python nl2sql-cli/nl2sql_workflow.py "Your question here"
    
    Runs in CLI mode without web interface
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
import json
from agent_framework import ChatMessage, Role, WorkflowContext, handler, Executor
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import setup_observability
from agent_framework._workflows._sequential import SequentialBuilder, _ResponseToConversation
from agent_framework._workflows import WorkflowBuilder
from agent_framework._workflows._agent_executor import AgentExecutorResponse
from azure.identity import AzureCliCredential

# Import custom executors
from executors import (
    SchemaRetrieverExecutor,
    SQLValidatorExecutor,
    QueryExecutorExecutor,
    ResultsExporterExecutor,
    ResultsVisualizerExecutor,
)

# Load environment
load_dotenv()

# Global timing
START_TIME: datetime | None = None


# =============================================================================
# Input Model
# =============================================================================


class NL2SQLInput(BaseModel):
    """Input model for NL2SQL pipeline."""
    
    question: str = Field(
        ...,
        description="Your natural language question about the database",
        examples=[
            "What are the top 10 customers by total revenue?",
            "Show me all orders placed in the last 30 days",
            "How many products are currently out of stock?",
            "What is the average order value by region?",
            "List all employees hired after January 1, 2024",
        ]
    )
    # Optional session id to enable follow-up questions in the same conversational context
    session_id: Optional[str] = Field(
        None,
        description="Optional session identifier for conversational follow-ups. When provided, the workflow will load prior conversation history (if available) and persist the updated conversation at the end."
    )


# =============================================================================
# Tracing Setup
# =============================================================================


def setup_tracing():
    """Configure observability based on environment variables."""
    otlp = os.environ.get("OTLP_ENDPOINT")
    if otlp:
        print(f"📊 Tracing Mode: OTLP ({otlp})")
        setup_observability(enable_sensitive_data=True, otlp_endpoint=otlp)
        return
    
    ai_conn = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if ai_conn:
        print("📊 Tracing Mode: App Insights")
        setup_observability(enable_sensitive_data=True, applicationinsights_connection_string=ai_conn)
        return
    
    if os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true":
        print("📊 Tracing Mode: Console")
        setup_observability(enable_sensitive_data=True)
        return
    
    print("📊 Tracing: Disabled")


def get_mssql_connection() -> str:
    """Get MSSQL connection ID from environment.
    
    Note: MSSQL MCP tools are available through the framework's MCP integration,
    but for this workflow we require a pre-configured connection ID.
    
    To get a connection ID:
    1. Use VS Code with MSSQL MCP extension configured
    2. Connect to your database through the extension
    3. Copy the connection ID to your .env file
    
    Alternative: Use SQL Server Management Studio or Azure Data Studio to establish
    connection, then use that connection string pattern in your environment.
    """
    connection_id = os.environ.get("MSSQL_CONNECTION_ID")
    
    if connection_id:
        print(f"✅ Using MSSQL connection: {connection_id}")
        return connection_id
    
    # Provide helpful error message
    server_name = os.environ.get("MSSQL_SERVER_NAME", "not-set")
    database_name = os.environ.get("MSSQL_DATABASE_NAME", "not-set")
    
    error_msg = f"""
❌ MSSQL Connection Not Configured

Required: Set MSSQL_CONNECTION_ID in your .env file

Current settings:
  MSSQL_SERVER_NAME: {server_name}
  MSSQL_DATABASE_NAME: {database_name}

How to get a connection ID:

Option 1: Use Python MSSQL Tools Directly
  ```python
  from agent_framework import MCPTool
  
  # Create MCP tool for MSSQL (requires MCP server running)
  mssql = MCPTool(command="path-to-mssql-mcp-server")
  await mssql.connect()
  
  # Get connection - returns connection ID
  result = await mssql.call_tool("mssql_connect", 
                                   server_name="{server_name}",
                                   database="{database_name}")
  ```

Option 2: Use VS Code MSSQL Extension
  1. Install MSSQL MCP extension in VS Code
  2. Connect to your database
  3. Get connection ID from extension
  4. Add to .env: MSSQL_CONNECTION_ID=<your-id>

Option 3: Manual Connection String
  For testing, you can use a simplified workflow that connects directly
  using connection strings (not recommended for production).

📖 See QUICKSTART.md for detailed setup instructions.
"""
    raise ValueError(error_msg)


async def create_nl2sql_workflow():
    """Create the NL2SQL sequential workflow."""
    
    # Setup Azure OpenAI client
    credential = AzureCliCredential()
    client = AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )
    
    # Determine if we should use real database or mock
    use_real_db = False
    try:
        # Check if database credentials are configured
        server = os.environ.get("MSSQL_SERVER_NAME")
        database = os.environ.get("MSSQL_DATABASE_NAME")
        username = os.environ.get("MSSQL_USERNAME")
        password = os.environ.get("MSSQL_PASSWORD")
        
        if server and database and username and password:
            print(f"\n✅ Database Configuration Found")
            print(f"   Server: {server}")
            print(f"   Database: {database}")
            print(f"   Authentication: SQL Password")
            use_real_db = True
        else:
            print(f"\n⚠️  Database credentials not fully configured")
            print(f"   Server: {server or 'NOT SET'}")
            print(f"   Database: {database or 'NOT SET'}")
            print(f"   Username: {'SET' if username else 'NOT SET'}")
            print(f"   Password: {'SET' if password else 'NOT SET'}")
            print(f"\n📝 Running in DEMO MODE with mock data")
            print(f"   Configure credentials in .env for real database access\n")
    except Exception as e:
        print(f"\n⚠️  Error checking database configuration: {e}")
        print(f"📝 Running in DEMO MODE with mock data\n")
    
    # Create agents
    sql_generator = client.create_agent(
        instructions="""You are an expert SQL query generator for Azure SQL Database.

Given a user question and database schema context, generate accurate SQL queries.

CRITICAL RULES:
1. **ONLY USE COLUMNS THAT EXIST IN THE PROVIDED SCHEMA** - Never invent or assume column names
2. **If a column doesn't exist, use the closest available column** - For example:
   - If "Region" doesn't exist but "CustomerSegment" does, use CustomerSegment
   - If "Revenue" doesn't exist but "AnnualRevenue" does, use AnnualRevenue
3. **Choose the simplest query** - Prefer dimension tables over complex joins when possible
4. **For customer revenue questions** - Use DimCustomer.AnnualRevenue or DimCustomer.LifetimeRevenue directly
5. **For aggregate questions** - Only join fact tables if dimension tables don't have the needed data
6. **Use only SELECT statements** unless explicitly told otherwise
7. **Always include TOP clause** to limit results (e.g., TOP 10, TOP 100)
8. **Use descriptive aliases** for better readability
9. **Test your logic** - Make sure joins won't produce empty results

SCHEMA VALIDATION:
Before writing your query, CHECK the schema to verify:
- The table name exists
- ALL column names exist in that table
- The column data types match your query logic

QUERY STRATEGY:
- For "top customers by revenue" → Use DimCustomer.AnnualRevenue
- For "loan information" → Use FACT_LOAN_ORIGINATION
- For "financial metrics" → Use FACT_CUSTOMER_FINANCIALS
- For "payments" → Use FACT_PAYMENT_TRANSACTION

COLUMN SELECTION FOR BETTER VISUALIZATION:
- **Always prefer descriptive names over IDs** (CompanyName instead of CustomerID)
- For customers: Select CompanyName, CustomerName, or similar descriptive fields
- For products: Select ProductName instead of ProductID
- For locations: Select City/Region/Country instead of LocationID
- IDs should only be included if specifically requested or as a secondary column

OUTPUT FORMAT:
```sql
[Your SQL query here]
```

Brief explanation of what the query does and why you chose this approach.""",
        name="sql_generator",
    )
    
    results_interpreter = client.create_agent(
        instructions="""You are a data insights specialist who explains database query results.

Given query results, provide:
1. Direct answer to the user's question
2. Key insights and patterns in the data
3. Any notable trends or anomalies
4. Suggestions for follow-up questions

FORMAT:
**Answer:** [Direct answer to the question]

**Insights:**
- [Key finding 1]
- [Key finding 2]
- [Key finding 3]

**Suggestions:**
- [Follow-up question 1]
- [Follow-up question 2]

Be concise, clear, and actionable.""",
        name="results_interpreter",
    )
    
    # Create custom executors with real DB flag
    schema_retriever = SchemaRetrieverExecutor(use_real_db=use_real_db)
    sql_validator = SQLValidatorExecutor(max_rows=1000, allow_write=False)
    query_executor = QueryExecutorExecutor(use_real_db=use_real_db)
    
    # Create input dispatcher to convert NL2SQLInput to ChatMessage
    class InputDispatcher(Executor):
        """Dispatcher that converts NL2SQLInput to ChatMessage format."""
        
        @handler
        async def dispatch(self, input_data: NL2SQLInput, ctx: WorkflowContext[list[ChatMessage]]) -> None:
            """Convert NL2SQLInput to ChatMessage for the pipeline.
            
            Args:
                input_data: NL2SQLInput with question field
                ctx: WorkflowContext for sending messages
            """
            # If a session id is provided, publish a SYSTEM message with the session id
            # and attempt to load previous conversation messages from disk so agents
            # can use the prior context to resolve follow-ups.
            if getattr(input_data, "session_id", None):
                session_id = input_data.session_id
                # Announce session id as a system message so downstream components
                # (and the output formatter) can detect and persist session state.
                session_msg = ChatMessage(role=Role.SYSTEM, text=f"SESSION_ID:{session_id}")
                await ctx.send_message([session_msg])

                # Try to load prior conversation if available
                session_dir = Path(__file__).parent / "workflow_outputs" / "sessions"
                session_dir.mkdir(parents=True, exist_ok=True)
                session_file = session_dir / f"{session_id}.json"
                if session_file.exists():
                    try:
                        with open(session_file, "r", encoding="utf-8") as sf:
                            data = json.load(sf)
                        for m in data.get("conversation", []):
                            role_name = m.get("role", "SYSTEM")
                            try:
                                role = getattr(Role, role_name)
                            except Exception:
                                role = Role.SYSTEM
                            # Reconstruct ChatMessage from saved dict
                            msg = ChatMessage(role=role, text=m.get("text", ""), author_name=m.get("author_name"))
                            await ctx.send_message([msg])
                    except Exception as e:
                        print(f"⚠️ Failed to load session {session_id}: {e}")

            # Create user message with the question
            message = ChatMessage(role=Role.USER, text=input_data.question)
            await ctx.send_message([message])
    
    input_dispatcher = InputDispatcher(id="input_dispatcher")
    
    # Create output formatter for CLI display
    class OutputFormatter(Executor):
        """Formats the final conversation into readable output."""
        
        @handler
        async def format_output(
            self, conversation: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage], str]
        ) -> None:
            """Format complete NL2SQL conversation for display."""
            from datetime import datetime
            
            output_lines = []
            output_lines.append("=" * 80)
            output_lines.append("🔍 NL2SQL PIPELINE RESULTS")
            output_lines.append("=" * 80)
            output_lines.append("")
            
            # Add model information
            model_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "Unknown")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output_lines.append(f"🤖 Model: {model_name}")
            output_lines.append(f"📅 Timestamp: {timestamp}")
            output_lines.append("")
            output_lines.append("=" * 80)
            output_lines.append("")
            
            # Extract the original user question from first USER message
            user_question = None
            for msg in conversation:
                if msg.role == Role.USER:
                    user_question = msg.text
                    break
            
            # Display the user's question at the top
            if user_question:
                output_lines.append("❓ USER QUESTION")
                output_lines.append("─" * 80)
                output_lines.append(user_question)
                output_lines.append("")
                output_lines.append("=" * 80)
                output_lines.append("")
            
            # Extract and format each step (skip USER messages and internal/technical messages)
            step_num = 1
            for msg in conversation:
                if msg.role == Role.USER:
                    continue  # Skip user messages in the step-by-step output
                
                # Skip internal schema context messages
                if "DATABASE SCHEMA CONTEXT:" in msg.text:
                    continue
                
                # Skip SQL validation messages (technical detail)
                if "VALIDATED SQL QUERY:" in msg.text:
                    continue
                
                # Skip SQL generator output (technical detail) - check by author or SQL block
                if msg.author_name == "sql_generator" or (msg.text.startswith("```sql") or "```sql\n" in msg.text[:100]):
                    continue
                
                role_emoji = "🤖"
                author = msg.author_name or msg.role.value
                
                # Clean the message text (remove visualization data comments)
                import re
                clean_text = re.sub(r'<!-- VISUALIZATION_DATA\n.*?\n-->', '', msg.text, flags=re.DOTALL).strip()
                
                output_lines.append("─" * 80)
                output_lines.append(f"{role_emoji} Step {step_num}: {author}")
                output_lines.append("─" * 80)
                output_lines.append("")
                output_lines.append(clean_text)
                output_lines.append("")
                step_num += 1
            
            output_lines.append("=" * 80)
            output_lines.append("✅ NL2SQL Pipeline Complete")
            output_lines.append("=" * 80)
            
            formatted_output = "\n".join(output_lines)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(__file__).parent / "workflow_outputs"
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"nl2sql_results_{timestamp}.txt"
            
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(formatted_output)
                print(f"\n💾 Results saved to: {output_file}")
            except Exception as e:
                print(f"\n⚠️ Failed to save output: {e}")
            
            # Persist session conversation if a session id was provided earlier
            try:
                session_id = None
                for msg in conversation:
                    if msg.role == Role.SYSTEM and isinstance(msg.text, str) and msg.text.startswith("SESSION_ID:"):
                        session_id = msg.text.split("SESSION_ID:", 1)[1].strip()
                        break

                if session_id:
                    session_dir = Path(__file__).parent / "workflow_outputs" / "sessions"
                    session_dir.mkdir(parents=True, exist_ok=True)
                    session_file = session_dir / f"{session_id}.json"
                    # Persist a compact session summary instead of the full conversation.
                    # We capture the last SQL generated (if present) and a small sample of results.
                    last_sql = None
                    last_result_sample = []
                    # Walk messages in reverse to find SQL and results
                    for msg in reversed(conversation):
                        if last_sql is None and isinstance(msg.text, str) and msg.text.strip().startswith("```sql"):
                            # Extract SQL block
                            try:
                                sql_block = msg.text.strip().split("```sql", 1)[1].rsplit("```", 1)[0].strip()
                                last_sql = sql_block
                            except Exception:
                                last_sql = None
                        # Heuristic: results interpreter often outputs a small table or 'Rows Returned' line
                        if not last_result_sample and isinstance(msg.text, str) and ("Rows Returned:" in msg.text or "|" in msg.text[:200]):
                            # Save a small snippet as sample
                            sample = msg.text.strip()
                            last_result_sample = sample.splitlines()[:20]
                        if last_sql and last_result_sample:
                            break

                    session_summary = {
                        "session_id": session_id,
                        "last_sql": last_sql,
                        "last_result_sample": last_result_sample,
                        "saved_at": datetime.now().isoformat(),
                    }

                    with open(session_file, "w", encoding="utf-8") as sf:
                        json.dump(session_summary, sf, indent=2)

                    print(f"💾 Session summary persisted: {session_file}")
            except Exception as e:
                print(f"⚠️ Failed to persist session: {e}")

            await ctx.yield_output(formatted_output)
    
    output_formatter = OutputFormatter(id="output_formatter")
    
    # Create results exporter
    results_exporter = ResultsExporterExecutor(export_dir="exports", id="results_exporter")
    
    # Create results visualizer
    results_visualizer = ResultsVisualizerExecutor(id="results_visualizer")
    
    # Create conversation adapters for agent -> executor conversions
    sql_gen_adapter = _ResponseToConversation(id="to-conversation:sql_generator")
    results_adapter = _ResponseToConversation(id="to-conversation:results_interpreter")
    
    # Build workflow: dispatcher -> sequential pipeline with adapters -> exporter -> formatter
    builder = WorkflowBuilder()
    builder.set_start_executor(input_dispatcher)
    
    # Chain the pipeline with conversation adapters after agents
    builder.add_edge(input_dispatcher, schema_retriever)
    builder.add_edge(schema_retriever, sql_generator)         # agent
    builder.add_edge(sql_generator, sql_gen_adapter)          # convert AgentExecutorResponse -> list[ChatMessage]
    builder.add_edge(sql_gen_adapter, sql_validator)
    builder.add_edge(sql_validator, query_executor)
    builder.add_edge(query_executor, results_interpreter)     # agent
    builder.add_edge(results_interpreter, results_adapter)    # convert AgentExecutorResponse -> list[ChatMessage]
    builder.add_edge(results_adapter, results_visualizer)     # create charts if applicable
    builder.add_edge(results_visualizer, results_exporter)    # export to CSV/Excel
    builder.add_edge(results_exporter, output_formatter)      # final formatting
    
    workflow = builder.build()
    return workflow


async def run_cli(question: str, session_id: Optional[str] = None):
    """Run the NL2SQL workflow in CLI mode."""
    setup_tracing()
    workflow = await create_nl2sql_workflow()
    
    print("=" * 80)
    print("🚀 NL2SQL Pipeline - CLI Mode")
    print("=" * 80)
    print(f"❓ Question: {question}")
    if session_id:
        print(f"🔑 Session: {session_id}")
    print("=" * 80)
    print()
    
    # Create input
    input_data = NL2SQLInput(question=question, session_id=session_id)
    
    # Run workflow
    result = await workflow.run(input_data)
    
    print("\n" + "=" * 80)
    print("✅ Pipeline Complete")
    print("=" * 80)
    print()
    print(result)
    print()
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python nl2sql_workflow.py \"Your question here\" [session_id]")
        print()
        print("Examples:")
        print('  python nl2sql_workflow.py "What are the top 10 customers by revenue?"')
        print('  python nl2sql_workflow.py "Show me all orders from last month" mysession123')
        sys.exit(1)
    
    question = sys.argv[1]
    session_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        asyncio.run(run_cli(question, session_id))
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

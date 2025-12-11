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
- Full observability with OpenTelemetry and Application Insights
"""

import asyncio
import os
import logging
from pathlib import Path
from datetime import datetime
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
from agent_framework.observability import setup_observability, get_tracer
from azure.identity.aio import AzureCliCredential
from azure.ai.projects.aio import AIProjectClient
from azure.core.exceptions import ResourceNotFoundError
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_azure_ai_observability(
    project_client: AIProjectClient, 
    enable_sensitive_data: bool = True
) -> str | None:
    """Setup tracing using Application Insights from Azure AI Project.
    
    This retrieves the connection string from the AIProjectClient and configures
    OpenTelemetry to send traces to Application Insights.
    
    Returns:
        Connection string if successful, None otherwise.
    """
    try:
        conn_string = await project_client.telemetry.get_application_insights_connection_string()
        logger.info("✓ Application Insights connection string retrieved from Azure AI Project")
        
        setup_observability(
            applicationinsights_connection_string=conn_string, 
            enable_sensitive_data=enable_sensitive_data
        )
        logger.info("✓ Observability configured - telemetry will be sent to Application Insights")
        return conn_string
    except ResourceNotFoundError:
        logger.warning("✗ No Application Insights found for Azure AI Project - using fallback")
        return None
    except Exception as e:
        logger.warning(f"✗ Error setting up Azure AI observability: {e}")
        return None


def setup_local_observability() -> None:
    """Setup observability using environment variables.
    
    Supports multiple tracing backends:
    - Application Insights (via APPLICATIONINSIGHTS_CONNECTION_STRING)
    - OTLP endpoint (via OTLP_ENDPOINT)
    - Console tracing (via ENABLE_CONSOLE_TRACING)
    - DevUI tracing (via ENABLE_DEVUI_TRACING)
    """
    enable_otel = os.getenv("ENABLE_OTEL", "true").lower() == "true"
    enable_sensitive_data = os.getenv("ENABLE_SENSITIVE_DATA", "true").lower() == "true"
    
    if not enable_otel:
        logger.info("📊 OpenTelemetry disabled (ENABLE_OTEL=false)")
        return
    
    # Try Application Insights connection string from environment
    ai_conn_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    otlp_endpoint = os.getenv("OTLP_ENDPOINT")
    enable_devui = os.getenv("ENABLE_DEVUI_TRACING", "false").lower() == "true"
    enable_console = os.getenv("ENABLE_CONSOLE_TRACING", "false").lower() == "true"
    
    if ai_conn_string:
        setup_observability(
            applicationinsights_connection_string=ai_conn_string,
            enable_sensitive_data=enable_sensitive_data
        )
        logger.info("✓ Observability configured with Application Insights")
    elif otlp_endpoint:
        setup_observability(
            otlp_endpoint=otlp_endpoint,
            enable_sensitive_data=enable_sensitive_data
        )
        logger.info(f"✓ Observability configured with OTLP endpoint: {otlp_endpoint}")
    elif enable_devui:
        setup_observability(enable_sensitive_data=enable_sensitive_data)
        logger.info("✓ Observability configured for DevUI tracing")
    elif enable_console:
        setup_observability(enable_sensitive_data=enable_sensitive_data)
        logger.info("✓ Observability configured with console tracing")
    else:
        # Default: enable basic observability
        setup_observability(enable_sensitive_data=enable_sensitive_data)
        logger.info("✓ Observability configured with default settings")


def get_dba_instructions(server: str, database: str) -> str:
    """Generate the DBA assistant instructions.
    
    Separated into a function to avoid f-string issues with backticks.
    """
    # Using regular string concatenation to avoid backtick issues in f-strings
    backtick = "`"
    triple_backtick = "```"
    
    return f"""You are a helpful SQL Server DBA assistant for server '{server}' and database '{database}'.

⚠️ **CRITICAL: ERD DIAGRAMS MUST USE MERMAID TEXT FORMAT ONLY** ⚠️
NEVER execute Python code to generate diagrams. NEVER use graphviz, networkx, matplotlib, or any image generation libraries.
ALWAYS output Mermaid erDiagram syntax as plain text in a {triple_backtick}mermaid code block.
This is NON-NEGOTIABLE. See ERD section below for exact format.

You help database administrators with:
- Health monitoring and diagnostics
- Performance analysis and tuning  
- Query optimization
- Index recommendations
- Troubleshooting blocking and deadlocks
- Capacity planning
- Maintenance task guidance

**CRITICAL BEHAVIORAL RULES - FOLLOW STRICTLY:**

1. **EXECUTE, DON'T ASK** - When you create a plan, EXECUTE IT IMMEDIATELY. Do NOT ask "do you want me to proceed?" - just proceed.

2. **NO REPEATED QUESTIONS** - If the user confirms a plan or says "yes, do it", DO NOT ask again. Execute the entire plan in one response.

3. **MAINTAIN CONTEXT** - Remember the conversation. If you already listed tables and relationships, DO NOT ask to list them again. Reference what you already know.

4. **BE DECISIVE** - Don't present options if the user already chose one. Example: If user says "PNG format", don't ask "PNG or Mermaid?" - just generate PNG.

5. **COMPLETE TASKS** - When asked to "create ER diagram", that means:
   - Query FK relationships (do it, don't ask)
   - Generate the diagram IN MERMAID SYNTAX (do it, don't ask)
   - Provide the Mermaid code in a code block
   - DONE. No follow-up questions unless there's an error.

6. **ERD DIAGRAMS: ALWAYS USE MERMAID TEXT FORMAT** - Never try to execute Python code to generate PNG files. Always output Mermaid erDiagram syntax directly in your response. Users can paste it into mermaid.live to visualize.

7. **INTELLIGENT TABLE MATCHING** - Use fuzzy matching for table names.

8. **USE SCHEMA-QUALIFIED NAMES** - Always use "schema.table" format in queries and descriptions.

9. **NO CIRCULAR PLANNING** - If you create a plan, execute it. Don't create a new plan to execute the previous plan.

10. **ASSUME PRODUCTION MINDSET** - This is a DBA tool for professionals. Be efficient, direct, and action-oriented.

11. **WHEN USER SAYS "NO MORE QUESTIONS"** - That's an explicit command. Execute everything without asking for confirmation.

**EXAMPLES OF CORRECT BEHAVIOR:**

User: "Create ER diagram in PNG format"
✅ CORRECT: [Execute query for FKs] [Generate diagram] "Here's your ER diagram: [PNG output]"
❌ WRONG: "Do you want me to proceed with creating the diagram?"

User: "yes" (after a plan was presented)
✅ CORRECT: [Execute the entire plan] [Show results]
❌ WRONG: "What would you like me to do?" or "Should I proceed?"

User: "build ER diagram, no more questions"
✅ CORRECT: [Query FKs] [Generate diagram] [Provide PNG] DONE.
❌ WRONG: "Do you want all tables or specific ones?" - THIS IS A QUESTION!

User: "export as PDF"
✅ CORRECT: [Convert to PDF] "Here's your PDF: [download link]"
❌ WRONG: "Do you also want PNG?" - They asked for PDF, give them PDF!

User: "produce a high-resolution PNG"
✅ CORRECT: [Generate PNG with high DPI] "Here's your PNG: [image]"
❌ WRONG: "Do you want me to include all tables or limit to four?" - JUST MAKE A DECISION AND EXECUTE!

**CRITICAL: STOP OFFERING UNSOLICITED NEXT STEPS:**
When you complete a task, STOP. Don't ask "Do you want me to also do X?" That's still a question!

✅ CORRECT: "Here are the relationships. ✅ Analysis complete."
❌ WRONG: "Here are the relationships. Do you want me to build a diagram?"

✅ CORRECT: "ER diagram generated. [show diagram]"
❌ WRONG: "ER diagram generated. Do you want me to also export as PDF?"

If the user wants something else, THEY WILL ASK. Your job is to complete the requested task, not to suggest more work.

**REMEMBER:**
- "Do you want..." = FORBIDDEN after user confirms
- "Should I..." = FORBIDDEN after user says yes
- "Would you like..." = FORBIDDEN after explicit request
- "Do you want me to include..." = FORBIDDEN - make the best decision yourself
- "Do you want me to also..." = FORBIDDEN - don't suggest additional tasks
- "Do you want me to proceed?" after presenting a plan = FORBIDDEN
- When user says "no more questions" = STOP ASKING ENTIRELY

**EXCEPTION:** Only offer to execute if the action is DESTRUCTIVE (DROP, DELETE, TRUNCATE, REBUILD with downtime).
For read-only analysis or safe operations, just do it.

Just execute and deliver results. DBAs want action, not conversation.

**OUTPUT FORMATTING RULES:**

1. **Always format tabular data as Markdown tables:**
   - Use pipe-separated columns with header row
   - Include separator row with dashes
   - Align columns properly for readability
   
   Example:
   {triple_backtick}
   | Schema | Table Name | Row Count | Size MB |
   |--------|-----------|-----------|---------|
   | dbo    | Customers | 150000    | 245.2   |
   | dbo    | Orders    | 500000    | 890.5   |
   {triple_backtick}

2. **Use consistent column widths** - align data for easy scanning

3. **Add summaries after tables** - total counts, averages, key insights

4. **For query results with multiple columns:**
   - Show the most important columns first
   - Limit to top N rows if dataset is large (mention total count)
   - Format numbers appropriately (commas for thousands, 2 decimals for percentages)

5. **For lists without structure:**
   - Use bullet points or numbered lists
   - Keep items concise

6. **For metrics/KPIs:**
   - Format as key-value pairs or small summary tables
   - Highlight critical values

**ERD DIAGRAM GENERATION:**

**⚠️ MANDATORY: OUTPUT MERMAID TEXT ONLY - NO CODE EXECUTION ⚠️**

When asked to generate an ERD (Entity Relationship Diagram), you MUST:

1. **Query foreign key relationships** using mssql_list_foreign_keys tool
2. **Output Mermaid syntax directly** - DO NOT execute any Python code
3. **Use this exact format:**

{triple_backtick}mermaid
erDiagram
    FACT_LOAN_ORIGINATION {{{{
        int LoanKey PK
        int CustomerKey FK
        int ProductKey FK
        int OriginationDateKey FK
        decimal OriginalAmount
        decimal InterestRate
    }}}}
    DimCustomer {{{{
        int CustomerKey PK
        string CompanyName
        string CustomerType
        string CreditRating
    }}}}
    DimLoanProduct {{{{
        int ProductKey PK
        string ProductName
        string ProductType
    }}}}
    DimDate {{{{
        int DateKey PK
        date FullDate
        int Year
        int Quarter
    }}}}
    
    FACT_LOAN_ORIGINATION }}}}o--|| DimCustomer : "customer"
    FACT_LOAN_ORIGINATION }}}}o--|| DimLoanProduct : "product"
    FACT_LOAN_ORIGINATION }}}}o--|| DimDate : "originated_on"
{triple_backtick}

**Relationship Syntax:**
- {backtick}}}}}o--||{backtick} : Many to one (FK relationship)
- {backtick}||--o{{{{{backtick} : One to many
- {backtick}||--||{backtick} : One to one
- {backtick}}}}}o--o{{{{{backtick} : Many to many

**FORBIDDEN ACTIONS:**
❌ NEVER write: {backtick}import graphviz{backtick}, {backtick}import networkx{backtick}, {backtick}import matplotlib{backtick}
❌ NEVER write: {backtick}plt.savefig(){backtick}, {backtick}graph.render(){backtick}, any file creation code
❌ NEVER attempt to execute Python code for diagram generation
❌ NEVER try to create PNG, SVG, or any image files

**CORRECT RESPONSE PATTERN:**
1. Query: "Let me get the foreign key relationships..."
2. Show FK table
3. Output: "Here's the Mermaid ERD diagram:"
4. Provide {triple_backtick}mermaid code block
5. DONE - no further questions about format

**User can visualize by pasting into:**
- https://mermaid.live
- VS Code with Mermaid extension
- GitHub/GitLab (auto-renders Mermaid)
- Pasting in GitHub/GitLab markdown

**Available visualization libraries in this environment:**
- ✅ {backtick}graphviz{backtick} - Use this for ERD generation (creates .dot files and renders to PNG/SVG)
- ✅ {backtick}matplotlib{backtick} - Available for charts and plots
- ✅ {backtick}pandas{backtick} - Available for data manipulation
- ❌ {backtick}pygraphviz{backtick} - NOT INSTALLED - Do not attempt to use
- ❌ {backtick}networkx{backtick} - NOT INSTALLED - Do not attempt to use

**CRITICAL: When generating ERD diagrams:**
1. ONLY use {backtick}from graphviz import Digraph{backtick}
2. DO NOT import networkx, pygraphviz, or any other graph libraries
3. If you attempt to use unavailable libraries, the diagram generation will fail
4. The graphviz package is the ONLY graph visualization library available

Always explain your findings clearly and provide actionable recommendations.
When suggesting SQL queries, ensure they are safe and read-only unless explicitly asked for changes."""


async def run_interactive_session(trace_id: str | None = None) -> None:
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
    
    # Path to our enhanced MCP server with DBA tools
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
            instructions=get_dba_instructions(server, database),
            tools=mcp_tool,
        ) as agent,
    ):
        print(f"✅ MCP server started")
        print(f"✅ Agent ready")
        if trace_id:
            print(f"📊 Trace ID: {trace_id}")
        print("💬 You can now ask questions...\n")
        
        query_count = 0
        while True:
            try:
                user_input = input("DBA> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                query_count += 1
                
                # Create a span for each query
                with get_tracer().start_as_current_span(
                    f"DBA Query #{query_count}",
                    kind=SpanKind.CLIENT
                ) as query_span:
                    query_span.set_attribute("dba.query.text", user_input)
                    query_span.set_attribute("dba.query.number", query_count)
                    query_span.set_attribute("dba.database.server", os.getenv("SERVER_NAME", "unknown"))
                    query_span.set_attribute("dba.database.name", os.getenv("DATABASE_NAME", "unknown"))
                    
                    print("\n🤖 Agent: ", end="", flush=True)
                    
                    response_text = ""
                    start_time = datetime.now()
                    
                    # Stream the response
                    async for chunk in agent.run_stream(user_input):
                        if chunk.text:
                            print(chunk.text, end="", flush=True)
                            response_text += chunk.text
                    
                    elapsed = (datetime.now() - start_time).total_seconds()
                    query_span.set_attribute("dba.response.length", len(response_text))
                    query_span.set_attribute("dba.response.elapsed_seconds", elapsed)
                
                print("\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Query error: {e}")
                print(f"\n❌ Error: {e}\n")



async def main() -> None:
    """Main entry point - starts the interactive DBA assistant with observability."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       Interactive DBA Assistant                              ║
║                   Powered by Microsoft Agent Framework                       ║
║                         & MSSQL MCP Server                                   ║
║                      with OpenTelemetry Observability                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Check if Azure credentials are configured
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("⚠️  Warning: AZURE_AI_PROJECT_ENDPOINT not set")
        print("   Create a .env file with your Azure AI project endpoint")
        print("   Copy .env.template to .env and fill in your values\n")
    
    # Setup observability
    print("📊 Setting up observability...")
    
    enable_azure_ai_tracing = os.getenv("ENABLE_AZURE_AI_TRACING", "false").lower() == "true"
    
    if enable_azure_ai_tracing and endpoint:
        # Use Azure AI Project's Application Insights
        async with AzureCliCredential() as credential:
            async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:
                await setup_azure_ai_observability(project_client)
    else:
        # Use local configuration from environment variables
        setup_local_observability()
    
    # Create a parent span for the entire session
    with get_tracer().start_as_current_span(
        "DBA Assistant Session",
        kind=SpanKind.SERVER
    ) as session_span:
        trace_id = format_trace_id(session_span.get_span_context().trace_id)
        session_span.set_attribute("dba.session.start_time", datetime.now().isoformat())
        session_span.set_attribute("dba.database.server", os.getenv("SERVER_NAME", "unknown"))
        session_span.set_attribute("dba.database.name", os.getenv("DATABASE_NAME", "unknown"))
        session_span.set_attribute("dba.model", os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "unknown"))
        
        print(f"📊 Session Trace ID: {trace_id}")
        print(f"   Use this to find traces in Azure Portal > Application Insights\n")
        
        # Start interactive session with trace ID
        await run_interactive_session(trace_id=trace_id)
        
        session_span.set_attribute("dba.session.end_time", datetime.now().isoformat())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        raise

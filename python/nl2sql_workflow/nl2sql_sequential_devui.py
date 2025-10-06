# Copyright (c) Microsoft. All rights reserved.

"""
NL2SQL Sequential Pipeline Workflow - DevUI Version with Azure SQL Database

This workflow demonstrates a complete Natural Language to SQL pipeline where
each stage is handled by a specialized agent working sequentially:

PIPELINE STAGES:
1. 🎯 Intent Analyzer - Understands user's natural language question
2. 📊 Schema Expert - Maps intent to database schema (tables/columns)
3. 💻 SQL Generator - Writes optimized SQL Server query
4. ✅ SQL Validator - Validates SQL Server syntax and logic
5. 🔧 Query Executor - Executes query against Azure SQL Database
6. 📝 Results Formatter - Formats results with natural language summary

TARGET DATABASE: Microsoft SQL Server / Azure SQL Database
- All SQL queries use SQL Server syntax (not MySQL/PostgreSQL)
- Use TOP N (not LIMIT), DB_NAME() (not DATABASE()), etc.

The workflow uses SequentialBuilder for proper conversation history accumulation,
showing how each agent builds upon the previous agent's analysis.

PREREQUISITES:
- Azure OpenAI access configured via .env file
- Azure CLI authentication: Run 'az login'
- Azure SQL Database with SQL authentication credentials in .env
- pyodbc and Microsoft ODBC Driver for SQL Server installed

TRACING OPTIONS:
1. Console Tracing: Set ENABLE_CONSOLE_TRACING=true
2. Azure AI Tracing: Set ENABLE_AZURE_AI_TRACING=true
3. OTLP Tracing: Set OTLP_ENDPOINT (e.g., http://localhost:4317)
4. DevUI Tracing: Set ENABLE_DEVUI_TRACING=true
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

import pyodbc
from dotenv import load_dotenv
from agent_framework import (
    ChatMessage,
    Executor,
    Role,
    SequentialBuilder,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowOutputEvent,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import setup_observability
from azure.identity import AzureCliCredential
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / ".env")


class NL2SQLInput(BaseModel):
    """Input model for natural language SQL queries."""
    
    question: str = Field(
        description="Natural language question about your database",
        examples=[
            "Show me the top 10 customers by total purchase amount",
            "What are the sales trends by month for the last year?",
            "Which products have inventory below 50 units?",
            "List all employees hired in 2024 with their departments",
            "What is the average order value per customer segment?"
        ]
    )
    
    database_context: str = Field(
        default="",
        description="Optional: Additional context about your database schema or business domain"
    )


def format_nl2sql_results(conversation: list[ChatMessage]) -> str:
    """Format the complete NL2SQL pipeline conversation into a readable report.
    
    Args:
        conversation: Complete list of ChatMessage objects from sequential workflow
        
    Returns:
        Formatted string with all pipeline stages
    """
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("🔍 NL2SQL PIPELINE ANALYSIS REPORT")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("📋 PIPELINE STAGES:")
    output_lines.append("   1. 🎯 Intent Analysis")
    output_lines.append("   2. 📊 Schema Mapping")
    output_lines.append("   3. 💻 SQL Generation")
    output_lines.append("   4. ✅ Validation")
    output_lines.append("   5. 🔧 Execution")
    output_lines.append("   6. 📝 Results Formatting")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Emoji mapping for agents
    agent_emoji = {
        "user": "💬",
        "intent_analyzer": "🎯",
        "schema_expert": "📊",
        "sql_generator": "💻",
        "sql_validator": "✅",
        "query_executor": "🔧",
        "results_formatter": "📝"
    }
    
    # Display names
    agent_names = {
        "user": "USER QUESTION",
        "intent_analyzer": "INTENT ANALYZER",
        "schema_expert": "SCHEMA EXPERT",
        "sql_generator": "SQL GENERATOR",
        "sql_validator": "SQL VALIDATOR",
        "query_executor": "QUERY EXECUTOR",
        "results_formatter": "RESULTS FORMATTER"
    }
    
    # Process each message in the conversation
    step_num = 1
    for msg in conversation:
        role = msg.role
        author = msg.author_name or ("user" if role == Role.USER else "assistant")
        
        # Get emoji and display name
        emoji = agent_emoji.get(author, "💬")
        display_name = agent_names.get(author, author.upper())
        
        # Add separator and header
        output_lines.append("─" * 80)
        output_lines.append(f"{emoji} STAGE {step_num}: {display_name}")
        output_lines.append("─" * 80)
        output_lines.append("")
        
        # Add message content
        output_lines.append(msg.text)
        output_lines.append("")
        
        step_num += 1
    
    output_lines.append("=" * 80)
    output_lines.append("✅ NL2SQL Pipeline Complete - All 6 Stages Executed")
    output_lines.append("=" * 80)
    
    result = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"nl2sql_pipeline_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n💾 NL2SQL pipeline output saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️ Failed to save output to file: {e}")
    
    return result


def get_database_connection():
    """Create and return Azure SQL Database connection using SQL authentication.
    
    Returns:
        pyodbc.Connection object or None if connection fails
    """
    try:
        server = os.environ.get("AZURE_SQL_SERVER")
        database = os.environ.get("AZURE_SQL_DATABASE")
        username = os.environ.get("AZURE_SQL_USERNAME")
        password = os.environ.get("AZURE_SQL_PASSWORD")
        driver = os.environ.get("AZURE_SQL_DRIVER", "{ODBC Driver 18 for SQL Server}")
        
        if not all([server, database, username, password]):
            print("⚠️ Missing Azure SQL credentials in .env file")
            return None
        
        connection_string = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        
        connection = pyodbc.connect(connection_string)
        return connection
        
    except Exception as e:
        print(f"⚠️ Database connection error: {e}")
        return None


def execute_sql_query(sql_query: str, max_rows: int = 100) -> str:
    """Execute SQL query against Azure SQL Database and return formatted results.
    
    Args:
        sql_query: SQL query to execute
        max_rows: Maximum number of rows to return (default 100)
        
    Returns:
        Formatted string with query results or error message
    """
    try:
        connection = get_database_connection()
        if not connection:
            return "⚠️ Unable to connect to database. Query not executed."
        
        cursor = connection.cursor()
        cursor.execute(sql_query)
        
        # Get column names
        columns = [column[0] for column in cursor.description] if cursor.description else []
        
        # Fetch results (limited to max_rows)
        rows = cursor.fetchmany(max_rows)
        
        if not rows:
            connection.close()
            return "✅ Query executed successfully. No rows returned."
        
        # Format results as a table
        result_lines = []
        result_lines.append(f"\n✅ Query executed successfully. Returned {len(rows)} row(s):\n")
        result_lines.append("─" * 80)
        
        # Header
        header = " | ".join(str(col).ljust(20)[:20] for col in columns)
        result_lines.append(header)
        result_lines.append("─" * 80)
        
        # Rows
        for row in rows:
            row_str = " | ".join(str(val).ljust(20)[:20] if val is not None else "NULL".ljust(20) for val in row)
            result_lines.append(row_str)
        
        result_lines.append("─" * 80)
        
        if len(rows) == max_rows:
            result_lines.append(f"\n⚠️ Results limited to {max_rows} rows. More data may exist.")
        
        connection.close()
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"❌ Query execution error: {str(e)}"


def extract_sql_from_text(text: str) -> str:
    """Extract SQL query from agent's response text.
    
    Args:
        text: Text containing SQL query
        
    Returns:
        Extracted SQL query or empty string
    """
    # Look for SQL between common delimiters
    import re
    
    # Try to find SQL in code blocks (with or without sql marker)
    # Pattern 1: ```sql ... ```
    code_block_pattern = r'```sql\s+(.*?)```'
    match = re.search(code_block_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
        # Remove comments and get just the query
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)  # Remove /* */ comments
        sql = '\n'.join(line for line in sql.split('\n') if not line.strip().startswith('--'))  # Remove -- comments
        return sql.strip()
    
    # Pattern 2: ``` ... ``` (no language marker)
    code_block_pattern2 = r'```\s*(SELECT.*?)```'
    match = re.search(code_block_pattern2, text, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        sql = '\n'.join(line for line in sql.split('\n') if not line.strip().startswith('--'))
        return sql.strip()
    
    # Try to find SELECT statement directly (no code block)
    select_pattern = r'(SELECT\s+.*?)(?:;|\n\n|\Z)'
    match = re.search(select_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
        # Remove trailing semicolon if present
        if sql.endswith(';'):
            sql = sql[:-1]
        return sql.strip()
    
    return ""


def fix_sql_server_syntax(sql: str) -> str:
    """Automatically fix common MySQL/generic SQL syntax to SQL Server syntax.
    
    Args:
        sql: SQL query that may contain non-SQL Server syntax
        
    Returns:
        SQL query with SQL Server compatible syntax
    """
    import re
    
    if not sql:
        return sql
    
    print(f"\n🔍 Checking SQL syntax...")
    fixes_applied = []
    
    # Fix 1: DATABASE() -> DB_NAME()
    if 'DATABASE()' in sql.upper():
        sql = re.sub(r'\bDATABASE\(\)', 'DB_NAME()', sql, flags=re.IGNORECASE)
        fixes_applied.append("DATABASE() → DB_NAME()")
    
    # Fix 2: LIMIT N -> TOP N (must move to after SELECT)
    limit_match = re.search(r'\bLIMIT\s+(\d+)', sql, re.IGNORECASE)
    if limit_match:
        limit_value = limit_match.group(1)
        # Remove LIMIT clause
        sql = re.sub(r'\bLIMIT\s+\d+', '', sql, flags=re.IGNORECASE)
        # Add TOP after SELECT if not already present
        if 'TOP' not in sql.upper():
            sql = re.sub(r'\bSELECT\b', f'SELECT TOP {limit_value}', sql, flags=re.IGNORECASE, count=1)
            fixes_applied.append(f"LIMIT {limit_value} → SELECT TOP {limit_value}")
    
    # Fix 3: NOW() -> GETDATE()
    if 'NOW()' in sql.upper():
        sql = re.sub(r'\bNOW\(\)', 'GETDATE()', sql, flags=re.IGNORECASE)
        fixes_applied.append("NOW() → GETDATE()")
    
    # Fix 4: LENGTH() -> LEN()
    if 'LENGTH(' in sql.upper():
        sql = re.sub(r'\bLENGTH\(', 'LEN(', sql, flags=re.IGNORECASE)
        fixes_applied.append("LENGTH() → LEN()")
    
    if fixes_applied:
        print("✏️  Applied SQL Server syntax fixes:")
        for fix in fixes_applied:
            print(f"    • {fix}")
    else:
        print("✅ No syntax fixes needed")
    
    return sql


def get_database_schema():
    """Retrieve database schema information from Azure SQL Database.
    
    Returns:
        String containing schema information (tables and columns)
    """
    try:
        connection = get_database_connection()
        if not connection:
            return "⚠️ Unable to connect to database. Using simulated schema."
        
        cursor = connection.cursor()
        
        # Query to get all tables and their columns
        schema_query = """
        SELECT 
            t.TABLE_SCHEMA,
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.TABLES t
        JOIN INFORMATION_SCHEMA.COLUMNS c 
            ON t.TABLE_SCHEMA = c.TABLE_SCHEMA 
            AND t.TABLE_NAME = c.TABLE_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
        """
        
        cursor.execute(schema_query)
        rows = cursor.fetchall()
        
        # Format schema information
        schema_lines = ["DATABASE SCHEMA:\n"]
        current_table = None
        
        for row in rows:
            schema_name, table_name, column_name, data_type, is_nullable, default_value = row
            full_table_name = f"{schema_name}.{table_name}"
            
            if current_table != full_table_name:
                if current_table:
                    schema_lines.append("")
                schema_lines.append(f"\nTable: {full_table_name}")
                schema_lines.append("-" * 40)
                current_table = full_table_name
            
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default = f" DEFAULT {default_value}" if default_value else ""
            schema_lines.append(f"  - {column_name} ({data_type}) {nullable}{default}")
        
        connection.close()
        return "\n".join(schema_lines)
        
    except Exception as e:
        print(f"⚠️ Schema retrieval error: {e}")
        return f"⚠️ Unable to retrieve schema: {str(e)}"
    """Retrieve database schema information from Azure SQL Database.
    
    Returns:
        String containing schema information (tables and columns)
    """
    try:
        connection = get_database_connection()
        if not connection:
            return "⚠️ Unable to connect to database. Using simulated schema."
        
        cursor = connection.cursor()
        
        # Query to get all tables and their columns
        schema_query = """
        SELECT 
            t.TABLE_SCHEMA,
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.TABLES t
        JOIN INFORMATION_SCHEMA.COLUMNS c 
            ON t.TABLE_SCHEMA = c.TABLE_SCHEMA 
            AND t.TABLE_NAME = c.TABLE_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
        """
        
        cursor.execute(schema_query)
        rows = cursor.fetchall()
        
        # Format schema information
        schema_lines = ["DATABASE SCHEMA:\n"]
        current_table = None
        
        for row in rows:
            schema_name, table_name, column_name, data_type, is_nullable, default_value = row
            full_table_name = f"{schema_name}.{table_name}"
            
            if current_table != full_table_name:
                if current_table:
                    schema_lines.append("")
                schema_lines.append(f"\nTable: {full_table_name}")
                schema_lines.append("-" * 40)
                current_table = full_table_name
            
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default = f" DEFAULT {default_value}" if default_value else ""
            schema_lines.append(f"  - {column_name} ({data_type}) {nullable}{default}")
        
        connection.close()
        return "\n".join(schema_lines)
        
    except Exception as e:
        print(f"⚠️ Schema retrieval error: {e}")
        return f"⚠️ Unable to retrieve schema: {str(e)}"


async def create_nl2sql_agents():
    """Create the 5 sequential NL2SQL pipeline agents (removed query_executor agent)."""
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
    
    # Get database schema for agents to reference
    db_schema = get_database_schema()
    
    # Agent 1: Intent Analyzer
    intent_analyzer = chat_client.create_agent(
        instructions=(
            "You're an intent analysis expert for NL2SQL. "
            "Analyze the user's natural language question and identify: "
            "1) Primary intent (SELECT, aggregate, filter, join, etc.) "
            "2) Entities mentioned (what data they want) "
            "3) Conditions/filters requested "
            "4) Required aggregations or calculations "
            "5) Expected output format. "
            "Provide a clear, structured analysis in 3-5 bullet points. "
            "Your analysis guides the schema expert."
        ),
        name="intent_analyzer",
    )
    
    # Agent 2: Schema Expert
    schema_expert = chat_client.create_agent(
        instructions=(
            f"You're a database schema expert for Microsoft SQL Server / Azure SQL Database. "
            f"Based on the intent analysis above, map the user's request to specific database objects. "
            f"Here's the actual database schema:\n\n{db_schema}\n\n"
            f"IMPORTANT: This is Azure SQL Database (SQL Server syntax). "
            f"Remember: Use TOP N not LIMIT, DB_NAME() not DATABASE(), GETDATE() not NOW(). "
            f"Identify: "
            f"1) Relevant tables needed "
            f"2) Specific columns to query "
            f"3) JOIN relationships required "
            f"4) Indexes that could help performance "
            f"5) Any potential schema limitations. "
            f"Provide schema mapping in 3-5 bullet points. Your mapping guides SQL Server query generation."
        ),
        name="schema_expert",
    )
    
    # Agent 3: SQL Generator
    sql_generator = chat_client.create_agent(
        instructions=(
            "You're an expert SQL Server / Azure SQL Database developer. "
            "Based on the intent analysis and schema mapping above, write an optimized SQL query. "
            "CRITICAL REQUIREMENTS: "
            "- Target database: Microsoft SQL Server / Azure SQL Database "
            "- Use SQL Server syntax ONLY (not MySQL, PostgreSQL, or Oracle) "
            "- For current database name, use DB_NAME() not DATABASE() "
            "- For schema info, use INFORMATION_SCHEMA views or sys.tables "
            "- Use TOP N instead of LIMIT N for row limiting "
            "- Wrap your SQL query in triple backticks with 'sql' language marker:\n"
            "```sql\nSELECT ...\n```\n"
            "Include: "
            "1) Complete, executable SQL Server query (wrapped in ```sql code block) "
            "2) Comments explaining key parts "
            "3) Use proper JOINs, WHERE clauses, and aggregations "
            "4) Apply SQL Server best practices (aliases, formatting) "
            "5) Consider performance (indexes, query structure). "
            "Your query will be validated for SQL Server compatibility next."
        ),
        name="sql_generator",
    )
    
    # Agent 4: SQL Validator
    sql_validator = chat_client.create_agent(
        instructions=(
            "You're a SQL Server / Azure SQL Database validation and optimization expert. "
            "Review the SQL query above and ensure SQL Server compatibility: "
            "CRITICAL VALIDATION RULES: "
            "- Target: Microsoft SQL Server / Azure SQL Database "
            "- Use DB_NAME() NOT DATABASE() for current database "
            "- Use TOP N NOT LIMIT N for row limiting "
            "- Use GETDATE() NOT NOW() for current date "
            "- Use LEN() NOT LENGTH() for string length "
            "- Use + for string concatenation, not CONCAT() when simple "
            "- Verify INFORMATION_SCHEMA or sys.* catalog views are used correctly "
            "1) Check SQL Server syntax correctness "
            "2) Verify it matches the original intent "
            "3) Identify potential issues (missing JOINs, wrong aggregations) "
            "4) Suggest optimizations if needed "
            "5) Provide final validated/corrected SQL wrapped in ```sql code block. "
            "IMPORTANT: Your final validated query MUST be wrapped in triple backticks with 'sql' marker:\n"
            "```sql\nSELECT ...\n```\n"
            "This query will be automatically executed against Azure SQL Database."
        ),
        name="sql_validator",
    )
    
    # Agent 5: Results Formatter (receives conversation + execution results)
    # NOTE: This agent is NOT in the sequential pipeline - it runs AFTER sql_executor
    results_formatter = chat_client.create_agent(
        instructions=(
            "You're a results presentation expert. "
            "Based on the complete pipeline above (including actual query execution results): "
            "1) Summarize what was requested in natural language "
            "2) Explain what the SQL query does in simple terms "
            "3) Present the actual query results clearly "
            "4) Provide insights or recommendations based on the actual data "
            "5) Note any limitations or caveats. "
            "Create a clear, business-friendly summary highlighting the REAL DATA returned. "
            "This is the final output the user will see."
        ),
        name="results_formatter",
    )
    
    return [
        intent_analyzer,
        schema_expert,
        sql_generator,
        sql_validator,
        # results_formatter removed from pipeline - runs separately after SQL execution
    ]


class NL2SQLInputDispatcher(Executor):
    """Dispatcher that converts NL2SQLInput to a string for the sequential workflow."""
    
    @handler
    async def dispatch_to_sequential(self, input_data: NL2SQLInput, ctx: WorkflowContext[str]) -> None:
        """Extract question from NL2SQLInput and send as string.
        
        Args:
            input_data: NL2SQLInput with question and optional context
            ctx: WorkflowContext for sending messages
        """
        # Combine question with optional context
        full_input = input_data.question
        if input_data.database_context:
            full_input += f"\n\nAdditional Context: {input_data.database_context}"
        
        # Sequential workflow expects a string input
        await ctx.send_message(full_input)


class SQLExecutor(Executor):
    """Custom executor that extracts SQL from conversation, executes it, and injects results."""
    
    @handler
    async def execute_and_inject(self, conversation: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]) -> None:
        """Extract SQL from the last message (validator), execute it, and inject results.
        
        Args:
            conversation: List of ChatMessage objects from the workflow so far
            ctx: WorkflowContext for sending the updated conversation
        """
        # Get the last message (should be from SQL validator)
        if not conversation:
            await ctx.send_message(conversation)
            return
        
        last_message = conversation[-1]
        
        # Debug: Print last message info
        print(f"\n🔍 DEBUG: Last message author: {last_message.author_name}")
        print(f"🔍 DEBUG: Last message text length: {len(last_message.text)}")
        print(f"🔍 DEBUG: First 500 chars: {last_message.text[:500]}")
        
        sql_query = extract_sql_from_text(last_message.text)
        
        # Apply SQL Server syntax fixes if needed
        if sql_query:
            sql_query = fix_sql_server_syntax(sql_query)
        
        if not sql_query:
            # No SQL found, add error message with debug info
            error_msg = (
                f"\n\n❌ Could not extract SQL query from validator response.\n"
                f"Debug info: Message from '{last_message.author_name}', length {len(last_message.text)} chars"
            )
            execution_message = ChatMessage(
                Role.ASSISTANT,
                text=error_msg,
                author_name="query_executor"
            )
        else:
            # Execute the SQL query
            print(f"\n🔧 Executing SQL query...")
            print(f"🔧 Extracted SQL: {sql_query[:200]}...")
            results = execute_sql_query(sql_query)
            
            # Create execution message with results
            execution_text = f"\n🔧 SQL QUERY EXECUTED:\n\n```sql\n{sql_query}\n```\n\n{results}"
            execution_message = ChatMessage(
                Role.ASSISTANT,
                text=execution_text,
                author_name="query_executor"
            )
        
        # Append execution results to conversation
        updated_conversation = conversation + [execution_message]
        await ctx.send_message(updated_conversation)


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
    async def run_sequential(self, input_text: str, ctx: WorkflowContext[list[ChatMessage]]) -> None:
        """Run the sequential workflow and capture the final conversation.
        
        Args:
            input_text: User input text to process through sequential agents
            ctx: WorkflowContext for sending the result
        """
        # Run the sequential workflow and collect outputs
        outputs: list[list[ChatMessage]] = []
        async for event in self._workflow.run_stream(input_text):
            if isinstance(event, WorkflowOutputEvent):
                outputs.append(event.data)
        
        # Send the final conversation (list of ChatMessages) to the next executor
        if outputs:
            await ctx.send_message(outputs[-1])


class NL2SQLOutputFormatter(Executor):
    """Executor that formats the complete NL2SQL conversation for display."""
    
    @handler
    async def format_output(self, conversation: list[ChatMessage], ctx: WorkflowContext) -> None:
        """Format the complete NL2SQL conversation and yield it.
        
        Args:
            conversation: Complete list of ChatMessage objects from the sequential workflow
            ctx: WorkflowContext for yielding formatted output
        """
        formatted_output = format_nl2sql_results(conversation)
        await ctx.yield_output(formatted_output)


class ResultsFormatterExecutor(Executor):
    """Executor that runs the results_formatter agent on a conversation."""
    
    def __init__(self, agent, **kwargs):
        """Initialize with the results_formatter agent.
        
        Args:
            agent: The results_formatter agent to run
            **kwargs: Additional Executor arguments
        """
        super().__init__(**kwargs)
        self.agent = agent
    
    @handler
    async def format_results(self, conversation: list[ChatMessage], ctx: WorkflowContext[list[ChatMessage]]) -> None:
        """Run the results_formatter agent on the conversation.
        
        Args:
            conversation: List of ChatMessage objects including SQL execution results
            ctx: WorkflowContext for sending updated conversation
        """
        # Run the agent with the conversation
        response = await self.agent.run(conversation)
        
        # Get the formatter's response message (AgentRunResponse has 'messages' list)
        if response.messages:
            formatter_message = response.messages[0]  # Get first message from response
        else:
            # Fallback if no messages returned
            formatter_message = ChatMessage(
                Role.ASSISTANT,
                text="No formatting response available.",
                author_name="results_formatter"
            )
        
        # Append formatter's response to conversation
        updated_conversation = conversation + [formatter_message]
        await ctx.send_message(updated_conversation)


async def create_nl2sql_workflow():
    """Create and return the DevUI-compatible NL2SQL sequential workflow."""
    # Get the 4 sequential agents (without query_executor or results_formatter)
    pipeline_agents = await create_nl2sql_agents()
    
    # Create results_formatter agent separately (runs after SQL execution)
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
    results_formatter_agent = chat_client.create_agent(
        instructions=(
            "You're a results presentation expert. "
            "Based on the complete pipeline above (including actual query execution results): "
            "1) Summarize what was requested in natural language "
            "2) Explain what the SQL query does in simple terms "
            "3) Present the actual query results clearly "
            "4) Provide insights or recommendations based on the actual data "
            "5) Note any limitations or caveats. "
            "Create a clear, business-friendly summary highlighting the REAL DATA returned. "
            "This is the final output the user will see."
        ),
        name="results_formatter",
    )
    
    # Create a wrapper executor that runs the 4-agent sequential workflow internally
    sequential_executor = SequentialWorkflowExecutor(
        agents=pipeline_agents,
        id="nl2sql_pipeline"
    )
    
    # Create dispatcher that converts NL2SQLInput to string
    dispatcher = NL2SQLInputDispatcher(id="input_dispatcher")
    
    # Create SQL executor that extracts SQL from validator, executes it, and injects results
    sql_executor = SQLExecutor(id="sql_executor")
    
    # Create formatter executor that runs the results_formatter agent on the conversation
    formatter_executor = ResultsFormatterExecutor(
        agent=results_formatter_agent,
        id="results_formatter_executor"
    )
    
    # Create output formatter to handle the final conversation list
    output_formatter = NL2SQLOutputFormatter(id="output_formatter")
    
    # Build the workflow: dispatcher -> 4-agent pipeline -> SQL executor -> formatter agent -> output formatter
    # SQLExecutor receives conversation from validator (last agent in pipeline)
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    builder.add_edge(dispatcher, sequential_executor)           # Run 4 agents
    builder.add_edge(sequential_executor, sql_executor)         # Execute SQL on validator output
    builder.add_edge(sql_executor, formatter_executor)          # Format results with agent
    builder.add_edge(formatter_executor, output_formatter)      # Final output
    
    workflow = builder.build()
    
    return workflow


def setup_tracing():
    """Set up observability tracing based on environment variables."""
    enable_console = os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true"
    enable_azure_ai = os.environ.get("ENABLE_AZURE_AI_TRACING", "").lower() == "true"
    otlp_endpoint = os.environ.get("OTLP_ENDPOINT")
    
    if enable_console:
        print("📊 Tracing: Console tracing enabled")
        setup_observability(enable_sensitive_data=True)
    elif enable_azure_ai:
        print("📊 Tracing: Azure AI tracing enabled")
        setup_observability(enable_sensitive_data=True)
    elif otlp_endpoint:
        print(f"📊 Tracing: OTLP endpoint configured: {otlp_endpoint}")
        setup_observability(enable_sensitive_data=True, otlp_endpoint=otlp_endpoint)
    else:
        print("📊 Tracing: Disabled")


def launch_devui():
    """Launch the DevUI interface with the NL2SQL sequential workflow."""
    from agent_framework.devui import serve
    
    # Set up tracing
    setup_tracing()
    
    # Test database connection
    print("\n🔌 Testing Azure SQL Database connection...")
    connection = get_database_connection()
    if connection:
        print("✅ Database connection successful")
        connection.close()
    else:
        print("⚠️ Database connection failed - check .env configuration")
    
    # Create the workflow
    workflow = asyncio.run(create_nl2sql_workflow())
    
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching NL2SQL Sequential Pipeline in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Sequential (4-Agent Pipeline + SQL Execution + Formatter)")
    print("✅ Pipeline Stages:")
    print("    1. 🎯 Intent Analyzer - Understand natural language")
    print("    2. 📊 Schema Expert - Map to database schema")
    print("    3. 💻 SQL Generator - Write optimized SQL")
    print("    4. ✅ SQL Validator - Validate and optimize")
    print("    5. 🔧 SQL Executor - Execute against Azure SQL DB (REAL DATA)")
    print("    6. 📝 Results Formatter - Format with insights")
    print("✅ Web UI: http://localhost:8099")
    print("✅ API: http://localhost:8099/v1/*")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    print("=" * 70)
    print()
    print("💡 Example questions to try:")
    print()
    print("📊 Analytics:")
    print("   - Show me the top 10 customers by total purchase amount")
    print("   - What are the sales trends by month for the last year?")
    print()
    print("📦 Inventory:")
    print("   - Which products have inventory below 50 units?")
    print("   - List all products that need reordering")
    print()
    print("👥 HR:")
    print("   - List all employees hired in 2024 with their departments")
    print("   - What is the average salary by department?")
    print()
    print("💰 Finance:")
    print("   - What is the average order value per customer segment?")
    print("   - Show revenue by product category for Q4 2024")
    print()
    print("=" * 70)
    
    # Serve the workflow through DevUI
    serve(
        entities=[workflow],
        port=8099,
        auto_open=True,
        tracing_enabled=enable_devui_tracing
    )


if __name__ == "__main__":
    launch_devui()

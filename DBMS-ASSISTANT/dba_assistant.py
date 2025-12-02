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
            instructions=f"""You are a helpful SQL Server DBA assistant for server '{server}' and database '{database}'.

⚠️ **CRITICAL: ERD DIAGRAMS MUST USE MERMAID TEXT FORMAT ONLY** ⚠️
NEVER execute Python code to generate diagrams. NEVER use graphviz, networkx, matplotlib, or any image generation libraries.
ALWAYS output Mermaid erDiagram syntax as plain text in a ```mermaid code block.
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
   ```
   | Schema | Table Name | Row Count | Size MB |
   |--------|-----------|-----------|---------|
   | dbo    | Customers | 150000    | 245.2   |
   | dbo    | Orders    | 500000    | 890.5   |
   ```

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

```mermaid
erDiagram
    FACT_LOAN_ORIGINATION {
        int LoanKey PK
        int CustomerKey FK
        int ProductKey FK
        int OriginationDateKey FK
        decimal OriginalAmount
        decimal InterestRate
    }
    DimCustomer {
        int CustomerKey PK
        string CompanyName
        string CustomerType
        string CreditRating
    }
    DimLoanProduct {
        int ProductKey PK
        string ProductName
        string ProductType
    }
    DimDate {
        int DateKey PK
        date FullDate
        int Year
        int Quarter
    }
    
    FACT_LOAN_ORIGINATION }o--|| DimCustomer : "customer"
    FACT_LOAN_ORIGINATION }o--|| DimLoanProduct : "product"
    FACT_LOAN_ORIGINATION }o--|| DimDate : "originated_on"
```

**Relationship Syntax:**
- `}o--||` : Many to one (FK relationship)
- `||--o{` : One to many
- `||--||` : One to one
- `}o--o{` : Many to many

**FORBIDDEN ACTIONS:**
❌ NEVER write: `import graphviz`, `import networkx`, `import matplotlib`
❌ NEVER write: `plt.savefig()`, `graph.render()`, any file creation code
❌ NEVER attempt to execute Python code for diagram generation
❌ NEVER try to create PNG, SVG, or any image files

**CORRECT RESPONSE PATTERN:**
1. Query: "Let me get the foreign key relationships..."
2. Show FK table
3. Output: "Here's the Mermaid ERD diagram:"
4. Provide ```mermaid code block
5. DONE - no further questions about format

**User can visualize by pasting into:**
- https://mermaid.live
- VS Code with Mermaid extension
- GitHub/GitLab (auto-renders Mermaid)
- Pasting in GitHub/GitLab markdown

**Available visualization libraries in this environment:**
- ✅ `graphviz` - Use this for ERD generation (creates .dot files and renders to PNG/SVG)
- ✅ `matplotlib` - Available for charts and plots
- ✅ `pandas` - Available for data manipulation
- ❌ `pygraphviz` - NOT INSTALLED - Do not attempt to use
- ❌ `networkx` - NOT INSTALLED - Do not attempt to use

**CRITICAL: When generating ERD diagrams:**
1. ONLY use `from graphviz import Digraph`
2. DO NOT import networkx, pygraphviz, or any other graph libraries
3. If you attempt to use unavailable libraries, the diagram generation will fail
4. The graphviz package is the ONLY graph visualization library available

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

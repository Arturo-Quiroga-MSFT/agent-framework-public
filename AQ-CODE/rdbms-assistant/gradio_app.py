"""
Gradio UI for RDBMS DBA Assistant
Modern chat interface for database administrators
"""
import asyncio
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
from threading import Thread
import time

# Load environment
load_dotenv()

from agent_framework import MCPStdioTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Global state
_agent_context = {
    "mcp_tool": None,
    "agent": None,
    "credential": None,
    "client": None,
    "initialized": False,
    "loop": None,
    "thread": None,
}

def start_event_loop():
    """Start dedicated event loop in background thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _agent_context["loop"] = loop
    loop.run_forever()

# Start background event loop
_agent_context["thread"] = Thread(target=start_event_loop, daemon=True)
_agent_context["thread"].start()
time.sleep(0.1)  # Give thread time to start

def run_in_loop(coro):
    """Run coroutine in the background event loop"""
    future = asyncio.run_coroutine_threadsafe(coro, _agent_context["loop"])
    return future.result()

async def initialize_agent():
    """Initialize the MCP server and agent - keeps them alive"""
    if _agent_context["initialized"]:
        return "✅ Agent already initialized"
    
    try:
        server = os.getenv("SERVER_NAME", "localhost")
        database = os.getenv("DATABASE_NAME", "master")
        
        # Path to MCP server
        mcp_server_path = Path(__file__).parent / "MssqlMcp" / "Node" / "dist" / "index.js"
        
        if not mcp_server_path.exists():
            return f"❌ MCP server not found at: {mcp_server_path}\nPlease build it first: cd MssqlMcp/Node && npm install && npm run build"
        
        # MCP environment
        mcp_env = {
            "SERVER_NAME": server,
            "DATABASE_NAME": database,
            "SQL_USERNAME": os.getenv("SQL_USERNAME", ""),
            "SQL_PASSWORD": os.getenv("SQL_PASSWORD", ""),
            "TRUST_SERVER_CERTIFICATE": os.getenv("TRUST_SERVER_CERTIFICATE", "true"),
            "READONLY": os.getenv("READONLY", "false"),
        }
        
        # Create credential
        _agent_context["credential"] = AzureCliCredential()
        
        # Create MCP tool
        _agent_context["mcp_tool"] = MCPStdioTool(
            name="mssql",
            command="node",
            args=[str(mcp_server_path)],
            env=mcp_env,
            description="Microsoft SQL Server database operations and management tools",
        )
        
        # Enter context managers to keep them alive
        await _agent_context["mcp_tool"].__aenter__()
        await _agent_context["credential"].__aenter__()
        
        # Create Azure AI client
        _agent_context["client"] = AzureAIAgentClient(async_credential=_agent_context["credential"])
        
        # Create agent
        # TEST VERSION: Switch between MINIMAL, BALANCED, or STRUCTURED
        prompt_version = "MINIMAL"  # Change to test different approaches
        
        if prompt_version == "MINIMAL":
            # VERSION 1: MINIMAL - Persona-driven, trust model intelligence
            instructions = f"""You are a senior SQL Server DBA working with '{database}' on server '{server}'.

**Your Role:**
Help database administrators analyze, optimize, and maintain this SQL Server database through conversation and tool use.

**Your Working Style:**
- Execute tasks immediately when requested - don't ask for confirmation unless the operation is destructive (DROP, DELETE, TRUNCATE)
- Complete multi-step tasks in a single response when possible
- Use schema-qualified table names (schema.table) for clarity
- When you've completed a task, stop and wait for the next request

**Tool Usage:**
You have 12 MCP tools including:
- Database operations: describe_table, list_tables, run_query, read_data
- Analysis: index_fragmentation, table_sizes, query_stats, foreign_keys
- Visualization: python_execute (for generating charts, graphs, and diagrams)

Use tools proactively. For visualizations, use python_execute with matplotlib/seaborn to create PNG charts.

**Visualization Workflow:**
1. Query data using run_query or read_data
2. Generate Python code to create chart (matplotlib, seaborn, pandas)
3. Call python_execute with code and filename
4. Present the generated chart to user

**Examples:**

User: "What are the relationships between tables?"
You: [Query FK metadata] [Present relationships] "Analysis complete."

User: "Create an ER diagram"
You: [Query FKs] [Generate diagram] [Show output]

User: "Show index fragmentation chart"
You: [Query fragmentation data] [Generate bar chart with python_execute] [Display chart] "Chart generated."

User: "Can you make it vertical?"
You: [Convert layout] [Show updated diagram]

Be direct, professional, and action-oriented."""
        
        elif prompt_version == "BALANCED":
            # VERSION 2: BALANCED - Core principles with selective examples
            instructions = f"""You are a SQL Server DBA assistant for '{database}' on server '{server}'.

**Core Principles:**

1. **Action-Oriented:** Execute requests immediately. Only ask for confirmation on destructive operations (DROP, DELETE, TRUNCATE).

2. **Context-Aware:** Remember previous queries and results. Don't re-fetch data you already have.

3. **Complete Tasks Fully:** Multi-step requests should be completed in one response.
   - "Create ER diagram" = Query FKs + Generate diagram + Show output
   - "Analyze performance" = Check indexes + Query stats + Provide recommendations
   - "Show fragmentation chart" = Query data + Generate visualization + Display PNG

4. **Professional Communication:** 
   - Use schema.table format
   - Provide clear analysis with actionable recommendations
   - End with completion statement, not follow-up questions

**Available Tools:**
12 MCP tools for database operations:
- Metadata: describe_table, list_tables, foreign_keys, list_indexes
- Analysis: index_fragmentation, table_sizes, query_stats
- Data: run_query, read_data
- DDL: create_index, create_table
- Visualization: python_execute (generates charts/graphs with matplotlib/seaborn)

**Visualization Capabilities:**
When asked for charts or visualizations:
1. Query the necessary data
2. Generate Python code using matplotlib/seaborn/pandas
3. Call python_execute with: code, data (optional JSON), and filename
4. The tool saves PNG and returns filepath - chart displays automatically

Common visualizations:
- Index fragmentation bar charts
- Table size comparisons
- Query performance trends
- Row count distributions
- Growth over time

**Behavior Examples:**

User: "Show table relationships"
You: [Use foreign_keys tool] [Format results] "Found 34 FK relationships across 7 fact tables and 15 dimension tables."

User: "Chart the top 10 fragmented indexes"
You: [Query index_fragmentation] [Generate Python chart code] [Call python_execute] "Chart generated showing fragmentation levels."

User: "yes" or "do it" (after presenting a plan)
You: [Execute the plan immediately] [Show results]

User: "Can you export as PDF?" (after showing diagram)
You: [Convert to PDF] [Provide download]

**What to Avoid:**
- Asking "Do you want me to proceed?" after user already confirmed
- Suggesting additional tasks after completing the current one
- Re-presenting options the user already chose

You're a tool for experienced DBAs - be efficient and decisive."""
        
        else:  # STRUCTURED
            # VERSION 3: STRUCTURED - Clear decision framework with sections
            instructions = f"""You are an expert SQL Server DBA assistant for database '{database}' on server '{server}'.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR MISSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Help DBAs monitor health, optimize performance, troubleshoot issues, and maintain this production database.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ DECISION FRAMEWORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When user makes a request:

✓ READ-ONLY (queries, analysis, diagrams) → Execute immediately
✓ SAFE WRITE (comments, statistics updates) → Execute immediately  
⚠ DESTRUCTIVE (DROP, DELETE, TRUNCATE, REBUILD) → Present plan, wait for confirmation

When user says "yes", "do it", "proceed":
→ Execute the previously discussed plan without re-asking

When user requests format change ("make it vertical", "export as PDF"):
→ Apply the transformation immediately

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ YOUR TOOLS (12 MCP Functions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metadata: list_tables, describe_table, foreign_keys, list_indexes
Analysis: index_fragmentation, table_sizes, query_stats
Data: run_query, read_data
DDL: create_index, create_table
Visualization: python_execute

Use tools proactively. For "show relationships" → query foreign_keys automatically.

📊 VISUALIZATION TOOL:
python_execute generates charts/graphs using matplotlib/seaborn/pandas
- Input: Python code, optional data JSON, output filename (e.g., "fragmentation.png")
- Output: PNG file saved to python_outputs/ directory
- Common uses: bar charts, line graphs, heatmaps, distribution plots

Visualization Workflow:
1. Query data (run_query or read_data)
2. Generate Python visualization code
3. Call python_execute with code + filename
4. Chart displays automatically in UI

Example Charts:
- Index fragmentation levels (bar chart)
- Table growth trends (line chart)
- Query performance comparison (bar chart)
- Row distribution by partition (pie/bar)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 RESPONSE PATTERN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [Execute tool calls]
2. [Present results with clear formatting]
3. [Provide brief analysis if relevant]
4. [End with completion marker: "✅ Analysis complete" or "✅ Chart generated"]

❌ DON'T: Add "Would you like me to also..." or "Should I proceed with..."
✅ DO: Stop cleanly after completing the task

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: "What tables have the most rows?"
A: [Query table_sizes] [Sort by row count] [Show top 10] "✅ Analysis complete."

Q: "Create ER diagram"
A: [Query foreign_keys] [Generate Mermaid ERD] [Display diagram] "✅ Diagram generated."

Q: "Show index fragmentation chart"
A: [Query index_fragmentation] [Generate matplotlib bar chart] [Call python_execute] "✅ Chart generated."

Q: "Make it vertical"
A: [Modify to rankdir=TB] [Regenerate diagram] [Display]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Always use schema.table format. Provide actionable insights. Be concise and professional."""
        
        _agent_context["agent"] = _agent_context["client"].create_agent(
            name="InteractiveDBA",
            instructions=instructions,
            tools=_agent_context["mcp_tool"],
        )
        
        await _agent_context["agent"].__aenter__()
        
        tool_count = len(_agent_context["mcp_tool"].functions)
        tool_names = [t.name for t in _agent_context["mcp_tool"].functions]
        
        _agent_context["initialized"] = True
        
        return f"""✅ **Agent Initialized Successfully**

**Server:** {server}
**Database:** {database}
**Available Tools:** {tool_count}

**Tools:** {', '.join(tool_names)}

You can now start asking questions!"""
        
    except Exception as e:
        return f"❌ **Initialization Failed**\n\n```\n{str(e)}\n```"

async def cleanup_agent():
    """Cleanup agent and MCP tool"""
    try:
        if _agent_context["agent"]:
            await _agent_context["agent"].__aexit__(None, None, None)
        if _agent_context["mcp_tool"]:
            await _agent_context["mcp_tool"].__aexit__(None, None, None)
        if _agent_context["credential"]:
            await _agent_context["credential"].__aexit__(None, None, None)
        
        _agent_context["initialized"] = False
        _agent_context["agent"] = None
        _agent_context["mcp_tool"] = None
        _agent_context["credential"] = None
        
        return "✅ Agent cleaned up"
    except Exception as e:
        return f"⚠️ Cleanup error: {e}"

async def chat_async(message: str, history: list):
    """Process chat message asynchronously"""
    if not _agent_context["initialized"]:
        return (history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "❌ **Agent not initialized.** Please click 'Initialize Agent' first."}
        ], [])
    
    if not message.strip():
        return history, []
    
    try:
        # Start collecting response
        response_text = ""
        generated_files = []
        
        # Stream response from agent
        async for chunk in _agent_context["agent"].run_stream(message):
            if chunk.text:
                response_text += chunk.text
        
        # Check if response contains file references from python_execute tool
        # Look for JSON responses with filepath
        try:
            # Try to find JSON blocks in the response
            json_pattern = r'\{[^{}]*"filepath"[^{}]*\}'
            matches = re.finditer(json_pattern, response_text)
            for match in matches:
                try:
                    file_info = json.loads(match.group())
                    if "filepath" in file_info and file_info.get("success"):
                        filepath = file_info["filepath"]
                        if os.path.exists(filepath):
                            generated_files.append(filepath)
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass
        
        # Add to history in messages format like the working example
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response_text})
        
        return history, generated_files
        
    except Exception as e:
        error_msg = f"❌ **Error:** {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return history, []

def chat(message: str, history: list):
    """Synchronous wrapper for chat"""
    return run_in_loop(chat_async(message, history))

def initialize():
    """Synchronous wrapper for initialization"""
    return run_in_loop(initialize_agent())

def get_connection_info():
    """Get current connection information"""
    server = os.getenv("SERVER_NAME", "Not configured")
    database = os.getenv("DATABASE_NAME", "Not configured")
    readonly = os.getenv("READONLY", "false")
    
    status = "🟢 Connected" if _agent_context["initialized"] else "🔴 Not Connected"
    mode = "🔒 Read-Only" if readonly.lower() == "true" else "✏️ Read-Write"
    
    return f"""**Connection Status:** {status}
**Mode:** {mode}
**Server:** `{server}`
**Database:** `{database}`"""

def get_sample_queries():
    """Get sample DBA queries"""
    return """### 📊 Sample Queries

**🔍 Connect → Discover → Analyze → Query → Optimize**

**Connect & Monitor:**
- Test database connection and get server info
- What's the database size?
- Show database statistics

**Discover Schema:**
- How many tables are in the database?
- List all dimension tables
- What are the relationships between tables?
- Show me the schema for dim.DimCustomer

**Analyze Performance:**
- Show tables with most rows
- Check for missing indexes
- Which fact tables are largest?
- Show index usage statistics

**Query & Explore:**
- Show top 10 records from FACT_LOAN_ORIGINATION
- Count records in all fact tables
- Get recent loan applications
- List active loans by product type

**Optimize:**
- Find tables with no data
- Check for NULL values in key columns
- Show data distribution across date ranges"""

# Create Gradio interface
with gr.Blocks(title="RDBMS DBA Assistant") as demo:
    gr.Markdown("""
    # 🗄️ RDBMS DBA Assistant
    ### AI-Powered Database Administration Assistant
    
    **11 MCP Tools Available:** Connect, Discover, Analyze, Query, Optimize
    
    **Workflow:** 🔍 Connect → 📊 Discover → 📈 Analyze → 🔎 Query → ⚡ Optimize
    
    *Powered by Microsoft Agent Framework & MSSQL MCP Server*
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Main chat interface
            chatbot = gr.Chatbot(
                label="Chat with DBA Assistant",
                height=600,
            )
            
            # File gallery for visualizations
            with gr.Accordion("📊 Generated Visualizations", open=True):
                file_output = gr.Gallery(
                    label="Charts & Graphs",
                    show_label=False,
                    columns=2,
                    height=300,
                    object_fit="contain",
                )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask about database health, performance, schema, or run queries...",
                    lines=2,
                    scale=4,
                )
                send_btn = gr.Button("Send 📤", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("Clear Chat 🗑️", size="sm")
                retry_btn = gr.Button("Retry Last ↺", size="sm")
        
        with gr.Column(scale=1):
            # Status and controls
            gr.Markdown("### 🔧 Controls")
            
            init_btn = gr.Button("Initialize Agent 🚀", variant="primary", size="lg")
            init_status = gr.Markdown("**Status:** 🔴 Not Initialized")
            
            gr.Markdown("### 📡 Connection Info")
            connection_info = gr.Markdown(get_connection_info())
            refresh_btn = gr.Button("Refresh Info ↻", size="sm")
            
            gr.Markdown("### 💡 Quick Reference")
            samples = gr.Markdown(get_sample_queries())
    
    # Event handlers
    def send_message(message, history):
        if not message.strip():
            return history, "", []
        new_history, files = chat(message, history)
        return new_history, "", files
    
    def retry_last(history):
        if len(history) > 0:
            # Find last user message in messages format
            for i in range(len(history) - 1, -1, -1):
                if history[i].get("role") == "user":
                    last_msg = history[i]["content"]
                    # Remove from that point onwards
                    history = history[:i]
                    new_history, files = chat(last_msg, history)
                    return new_history, "", files
        return history, "", []
    
    # Button actions
    send_btn.click(send_message, [msg, chatbot], [chatbot, msg, file_output])
    msg.submit(send_message, [msg, chatbot], [chatbot, msg, file_output])
    clear_btn.click(lambda: ([], []), None, [chatbot, file_output])
    retry_btn.click(retry_last, [chatbot], [chatbot, msg, file_output])
    
    init_btn.click(initialize, None, init_status)
    refresh_btn.click(get_connection_info, None, connection_info)
    
    # Keyboard shortcuts
    demo.load(lambda: None, None, None)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RDBMS DBA Assistant - Gradio UI                           ║
║                 Powered by Microsoft Agent Framework                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
    
Starting Gradio interface...
    """)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )

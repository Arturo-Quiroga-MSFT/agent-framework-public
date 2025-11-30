"""
Gradio UI for RDBMS DBA Assistant - Simplified Version
Modern chat interface for database administrators
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
from threading import Thread
import asyncio
import queue

# Load environment
load_dotenv()

from agent_framework import MCPStdioTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Global state
agent_state = {
    "mcp_tool": None,
    "agent": None,
    "credential": None,
    "loop": None,
    "initialized": False
}

# Queue for async operations
request_queue = queue.Queue()
response_queue = queue.Queue()

def run_async_loop():
    """Run the async event loop in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    agent_state["loop"] = loop
    
    async def process_requests():
        while True:
            try:
                request = await asyncio.get_event_loop().run_in_executor(
                    None, request_queue.get, True, 0.1
                )
                
                if request["action"] == "initialize":
                    result = await initialize_agent_async()
                    response_queue.put(result)
                elif request["action"] == "chat":
                    result = await chat_async(request["message"], request["history"])
                    response_queue.put(result)
                elif request["action"] == "stop":
                    break
            except queue.Empty:
                continue
            except Exception as e:
                response_queue.put(f"Error: {str(e)}")
    
    loop.run_until_complete(process_requests())

# Start async loop in background thread
async_thread = Thread(target=run_async_loop, daemon=True)
async_thread.start()

async def initialize_agent_async():
    """Initialize the MCP server and agent"""
    if agent_state["initialized"]:
        return "✅ Agent already initialized"
    
    try:
        server = os.getenv("SERVER_NAME", "localhost")
        database = os.getenv("DATABASE_NAME", "master")
        
        # Path to MCP server
        mcp_server_path = Path(__file__).parent / "MssqlMcp" / "Node" / "dist" / "index.js"
        
        if not mcp_server_path.exists():
            return f"❌ MCP server not found at: {mcp_server_path}"
        
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
        agent_state["credential"] = AzureCliCredential()
        
        # Create MCP tool
        agent_state["mcp_tool"] = MCPStdioTool(
            name="mssql",
            command="node",
            args=[str(mcp_server_path)],
            env=mcp_env,
            description="Microsoft SQL Server database operations",
        )
        
        # Connect to MCP server
        await agent_state["mcp_tool"].__aenter__()
        
        # Create Azure AI client
        client = AzureAIAgentClient(async_credential=agent_state["credential"])
        
        # Create agent
        agent_state["agent"] = client.create_agent(
            name="InteractiveDBA",
            instructions=f"""You are a helpful SQL Server DBA assistant for '{server}/{database}'.

Help with monitoring, performance analysis, troubleshooting, and maintenance tasks.
Explain findings clearly and provide actionable recommendations.""",
            tools=agent_state["mcp_tool"],
        )
        
        await agent_state["agent"].__aenter__()
        
        tool_count = len(agent_state["mcp_tool"].functions)
        agent_state["initialized"] = True
        
        return f"""✅ **Agent Initialized**

**Server:** {server}
**Database:** {database}
**Tools:** {tool_count}

Ask questions now!"""
        
    except Exception as e:
        return f"❌ **Error:** {str(e)}"

async def chat_async(message: str, history: list):
    """Process chat message asynchronously"""
    if not agent_state["initialized"]:
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "❌ Agent not initialized. Click 'Initialize Agent' first."}
        ]
    
    if not message.strip():
        return history
    
    try:
        response_text = ""
        
        async for chunk in agent_state["agent"].run_stream(message):
            if chunk.text:
                response_text += chunk.text
        
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response_text})
        return history
        
    except Exception as e:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": f"❌ **Error:** {str(e)}"})
        return history

def initialize():
    """Initialize agent (sync wrapper)"""
    request_queue.put({"action": "initialize"})
    return response_queue.get(timeout=30)

def chat(message: str, history: list):
    """Chat with agent (sync wrapper)"""
    request_queue.put({"action": "chat", "message": message, "history": history})
    return response_queue.get(timeout=60)

def get_connection_info():
    """Get connection information"""
    server = os.getenv("SERVER_NAME", "Not configured")
    database = os.getenv("DATABASE_NAME", "Not configured")
    readonly = os.getenv("READONLY", "false")
    
    status = "🟢 Connected" if agent_state["initialized"] else "🔴 Not Connected"
    mode = "🔒 Read-Only" if readonly.lower() == "true" else "✏️ Read-Write"
    
    return f"""**Status:** {status}
**Mode:** {mode}
**Server:** `{server}`
**Database:** `{database}`"""

def get_sample_queries():
    """Get sample queries"""
    return """### 📊 Sample Queries

- How many tables are in the database?
- List all dimension tables
- What's the database size?
- Show top 10 customers
- Check for blocking sessions
- Show database statistics"""

# Create Gradio interface
with gr.Blocks(title="RDBMS DBA Assistant") as demo:
    gr.Markdown("""
    # 🗄️ RDBMS DBA Assistant
    ### AI-Powered Database Administration
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Chat", height=600)
            
            with gr.Row():
                msg = gr.Textbox(
                    label="Your Question",
                    placeholder="Ask about database...",
                    lines=2,
                    scale=4,
                )
                send_btn = gr.Button("Send 📤", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("Clear 🗑️", size="sm")
        
        with gr.Column(scale=1):
            gr.Markdown("### 🔧 Controls")
            init_btn = gr.Button("Initialize Agent 🚀", variant="primary", size="lg")
            init_status = gr.Markdown("**Status:** 🔴 Not Initialized")
            
            gr.Markdown("### 📡 Connection")
            connection_info = gr.Markdown(get_connection_info())
            refresh_btn = gr.Button("Refresh ↻", size="sm")
            
            gr.Markdown("### 💡 Examples")
            samples = gr.Markdown(get_sample_queries())
    
    # Event handlers
    def send_message(message, history):
        if not message.strip():
            return history, ""
        new_history = chat(message, history)
        return new_history, ""
    
    send_btn.click(send_message, [msg, chatbot], [chatbot, msg])
    msg.submit(send_message, [msg, chatbot], [chatbot, msg])
    clear_btn.click(lambda: [], None, chatbot)
    init_btn.click(initialize, None, init_status)
    refresh_btn.click(get_connection_info, None, connection_info)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RDBMS DBA Assistant - Gradio UI                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    
Starting Gradio interface...
    """)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )

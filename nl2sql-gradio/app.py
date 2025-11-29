"""
NL2SQL Gradio Chat Interface

A rich chat UI for the NL2SQL pipeline with:
- Interactive chat interface
- Inline chart visualization
- Export downloads (CSV/Excel)
- Session management
- Query history
"""
import asyncio
import os
from pathlib import Path
from typing import Optional
import gradio as gr
from dotenv import load_dotenv

# Import the workflow
from nl2sql_workflow import create_nl2sql_workflow, NL2SQLInput, setup_tracing

load_dotenv()

# Global workflow instance
workflow = None


async def init_workflow():
    """Initialize the workflow once."""
    global workflow
    if workflow is None:
        setup_tracing()
        workflow = await create_nl2sql_workflow()
    return workflow


async def process_query(question: str, session_id: Optional[str] = None):
    """Process a query and return results with visualization."""
    wf = await init_workflow()
    
    # Create input
    input_data = NL2SQLInput(question=question, session_id=session_id)
    
    # Run workflow
    result = await wf.run(input_data)
    
    # Extract formatted output
    formatted_output = None
    for event in result:
        if hasattr(event, 'data') and isinstance(event.data, str) and '🔍 NL2SQL PIPELINE RESULTS' in event.data:
            formatted_output = event.data
            break
    
    # Find latest chart
    viz_dir = Path(__file__).parent / "visualizations"
    chart_files = sorted(viz_dir.glob("chart_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    latest_chart = str(chart_files[0]) if chart_files else None
    
    # Find latest exports
    export_dir = Path(__file__).parent / "exports"
    csv_files = sorted(export_dir.glob("query_results_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    xlsx_files = sorted(export_dir.glob("query_results_*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    latest_csv = str(csv_files[0]) if csv_files else None
    latest_xlsx = str(xlsx_files[0]) if xlsx_files else None
    
    return formatted_output or "No output generated", latest_chart, latest_csv, latest_xlsx


def chat_interface(message, history, session_id):
    """Handle chat messages."""
    if not message.strip():
        return history, None, None, None
    
    # Add user message to history
    history = history + [[message, "Processing..."]]
    
    # Process query
    try:
        output, chart, csv, xlsx = asyncio.run(process_query(message, session_id or None))
        
        # Extract just the answer section for chat
        answer_lines = []
        in_answer = False
        for line in output.split('\n'):
            if '🤖 Step 2: results_interpreter' in line:
                in_answer = True
                continue
            if in_answer:
                if '────────' in line and answer_lines:
                    break
                if line.strip() and not line.startswith('────'):
                    answer_lines.append(line)
        
        answer = '\n'.join(answer_lines).strip() or output
        
        # Update last message with response
        history[-1][1] = answer
        
        return history, chart, csv, xlsx
        
    except Exception as e:
        history[-1][1] = f"❌ Error: {str(e)}"
        return history, None, None, None


def build_ui():
    """Build Gradio interface."""
    with gr.Blocks(title="NL2SQL Chat", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🔍 NL2SQL Chat Interface
        
        Ask questions about your database in natural language. The AI will:
        1. Generate SQL queries
        2. Execute them safely
        3. Provide insights and visualizations
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    height=500,
                    label="Conversation",
                    show_label=True,
                    avatar_images=(None, "🤖")
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask a question about your database...",
                        label="Your Question",
                        scale=4
                    )
                    session = gr.Textbox(
                        placeholder="Optional: session ID for follow-ups",
                        label="Session ID",
                        scale=1
                    )
                
                with gr.Row():
                    submit = gr.Button("Send", variant="primary")
                    clear = gr.Button("Clear")
                
                gr.Examples(
                    examples=[
                        "What are the top 10 customers by revenue?",
                        "Show me all orders from last month",
                        "How many products are out of stock?",
                        "What's the average order value by region?",
                        "List employees hired in 2024"
                    ],
                    inputs=msg
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Visualization")
                chart_output = gr.Image(label="Generated Chart", height=300)
                
                gr.Markdown("### 📥 Downloads")
                csv_output = gr.File(label="CSV Export")
                xlsx_output = gr.File(label="Excel Export")
        
        # Event handlers
        submit_event = submit.click(
            chat_interface,
            inputs=[msg, chatbot, session],
            outputs=[chatbot, chart_output, csv_output, xlsx_output]
        )
        
        msg.submit(
            chat_interface,
            inputs=[msg, chatbot, session],
            outputs=[chatbot, chart_output, csv_output, xlsx_output]
        )
        
        clear.click(lambda: ([], None, None, None), outputs=[chatbot, chart_output, csv_output, xlsx_output])
        
        # Clear input after submit
        submit.click(lambda: "", outputs=msg)
        msg.submit(lambda: "", outputs=msg)
    
    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

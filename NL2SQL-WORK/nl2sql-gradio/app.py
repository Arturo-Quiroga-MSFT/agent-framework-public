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
    
    # Extract suggestions from output
    suggestions = []
    if formatted_output:
        lines = formatted_output.split('\n')
        in_suggestions = False
        for line in lines:
            if '**Suggestions:**' in line:
                in_suggestions = True
                continue
            if in_suggestions:
                if line.strip().startswith('- '):
                    # Remove markdown list marker and clean up
                    suggestion = line.strip()[2:].strip()
                    if suggestion and '?' in suggestion:
                        suggestions.append(suggestion)
                elif line.strip().startswith('────') or not line.strip():
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
    
    return formatted_output or "No output generated", latest_chart, latest_csv, latest_xlsx, suggestions


def chat_interface(message, history, session_id):
    """Handle chat messages."""
    if not message.strip():
        return history, None, None, None, gr.update(choices=[], visible=False)
    
    # Add user message to history
    history = history + [{"role": "user", "content": message}]
    
    # Process query
    try:
        output, chart, csv, xlsx, suggestions = asyncio.run(process_query(message, session_id or None))
        
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
        
        # Add assistant response
        history = history + [{"role": "assistant", "content": answer}]
        
        # Update suggestions dropdown
        suggestion_update = gr.update(
            choices=suggestions if suggestions else [],
            visible=bool(suggestions),
            value=None
        )
        
        return history, chart, csv, xlsx, suggestion_update
        
    except Exception as e:
        history = history + [{"role": "assistant", "content": f"❌ Error: {str(e)}"}]
        return history, None, None, None, gr.update(choices=[], visible=False)


def build_ui():
    """Build Gradio interface."""
    with gr.Blocks(title="NL2SQL Chat") as demo:
        gr.Markdown("""
        # 🏦 TERADATA-FI Financial Intelligence Chat
        
        **Connected to:** TERADATA-FI Database | aqsqlserver001.database.windows.net
        
        Ask natural language questions about your financial data. The AI will:
        1. Generate optimized SQL queries against dim.DimCustomer and FACT tables
        2. Execute them safely with validation
        3. Provide intelligent insights with automatic visualizations
        
        **Database Coverage:** Customer profiles, loan originations, payment transactions, financial metrics, and risk indicators.
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    height=500,
                    label="Conversation",
                    show_label=True
                )
                
                # Suggestions dropdown
                suggestions_dropdown = gr.Dropdown(
                    label="💡 Suggested Follow-up Questions",
                    choices=[],
                    visible=False,
                    interactive=True
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
                        "Show me high-risk customers with loan volume over $100M",
                        "What's the distribution of customers by tier?",
                        "List VIP customers with more than 15 loans",
                        "Show me loan volume trends by fiscal month",
                        "Which customer segment has the highest default rate?",
                        "Compare Bronze vs Platinum tier customers by total loan volume",
                        "Show me customers in the Large Corporate segment with delinquent loans",
                        "What's the average lifetime revenue by customer tier?",
                        "List customers with internal risk rating above 8",
                        "Show me loan origination volume by fiscal year and month",
                        "Which customers have the highest loan-to-revenue ratio?"
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
            outputs=[chatbot, chart_output, csv_output, xlsx_output, suggestions_dropdown]
        )
        
        msg.submit(
            chat_interface,
            inputs=[msg, chatbot, session],
            outputs=[chatbot, chart_output, csv_output, xlsx_output, suggestions_dropdown]
        )
        
        # Handle suggestion selection
        def use_suggestion(suggestion, history, session_id):
            if suggestion:
                return chat_interface(suggestion, history, session_id)
            return history, None, None, None, gr.update()
        
        suggestions_dropdown.change(
            use_suggestion,
            inputs=[suggestions_dropdown, chatbot, session],
            outputs=[chatbot, chart_output, csv_output, xlsx_output, suggestions_dropdown]
        )
        
        clear.click(
            lambda: ([], None, None, None, gr.update(choices=[], visible=False)), 
            outputs=[chatbot, chart_output, csv_output, xlsx_output, suggestions_dropdown]
        )
        
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

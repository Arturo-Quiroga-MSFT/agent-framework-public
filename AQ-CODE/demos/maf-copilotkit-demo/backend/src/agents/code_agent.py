"""
Code Interpreter Agent with Human-in-the-Loop Approval
"""

from agent_framework import ChatAgent, HostedCodeInterpreterTool
from agent_framework._clients import ChatClientProtocol
from agent_framework_ag_ui import AgentFrameworkAgent


def create_code_interpreter_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create code interpreter agent with execution approval workflow."""
    
    base_agent = ChatAgent(
        name="code-interpreter-agent",
        instructions="""You are an expert Python programmer with code execution capabilities.

Your capabilities:
- Write and execute Python code for calculations, data analysis, and visualizations
- Generate matplotlib plots and charts
- Perform mathematical computations
- Analyze data and create statistical summaries

Best practices:
1. Always explain what the code will do before writing it
2. Write clean, well-commented code
3. When creating plots, use descriptive titles and labels
4. For visualizations, use appropriate color schemes and layouts
5. Save plots as images that can be displayed in the UI

When asked to create visualizations:
- Use matplotlib for all plots
- Set figure size appropriately (e.g., plt.figure(figsize=(10, 6)))
- Add titles, axis labels, and legends where appropriate
- Use plt.tight_layout() to prevent label cutoff
- Save with plt.savefig() when needed

Remember previous code and results for context in follow-up questions.
""",
        chat_client=chat_client,
        tools=HostedCodeInterpreterTool(),
    )
    
    return AgentFrameworkAgent(
        agent=base_agent,
        name="CodeInterpreterAgent",
        description="Python code execution agent with visualization capabilities",
        state_schema={
            "code_history": {
                "type": "array",
                "items": {"type": "string"},
                "description": "History of executed code snippets",
            }
        },
        require_confirmation=True,  # Enable HITL for code execution
    )

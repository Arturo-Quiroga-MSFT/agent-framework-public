# Copyright (c) Microsoft. All rights reserved.

"""
Magentic Orchestration with DevUI Support

Converts the Magentic multi-agent workflow to work with DevUI.
Adds proper input handling and serves the workflow on port 8100.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agent_framework import (
    ChatAgent,
    Executor,
    HostedCodeInterpreterTool,
    MagenticBuilder,
    MagenticCallbackMode,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowOutputEvent,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from agent_framework_devui import serve

# Load environment variables from .env file
# Try multiple possible locations
possible_env_files = [
    Path(__file__).parent.parent.parent / ".env",
    Path(__file__).parent.parent.parent / "python" / "nl2sql_workflow" / ".env",
]

env_loaded = False
for env_file in possible_env_files:
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from: {env_file}")
        env_loaded = True
        break

if not env_loaded:
    print(f"⚠️  Warning: No .env file found. Using existing environment variables.")
    print(f"   Searched: {[str(f) for f in possible_env_files]}")


class ResearchTaskInput(BaseModel):
    """Input model for research and analysis tasks."""
    
    task: str = Field(
        description="The research or analysis task to perform"
    )


class InputDispatcher(Executor):
    """Dispatcher that passes user input to the Magentic workflow."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = None
    
    @handler
    async def dispatch(self, input_data: ResearchTaskInput, ctx: WorkflowContext) -> None:
        """Pass the task string to the Magentic workflow."""
        from datetime import datetime
        
        # Track start time
        self.start_time = datetime.now()
        
        print(f"📥 Received task: {input_data.task[:100]}...")
        print(f"⏱️  Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        await ctx.send_message(input_data.task)


class MagenticWorkflowExecutor(Executor):
    """Executor that wraps the Magentic workflow."""
    
    def __init__(self, magentic_workflow, **kwargs):
        super().__init__(**kwargs)
        self._workflow = magentic_workflow
    
    @handler
    async def run_magentic(self, task: str, ctx: WorkflowContext) -> None:
        """Run the Magentic workflow with the given task."""
        print(f"🔄 Starting Magentic workflow with task: {task[:100]}...")
        
        # Run the Magentic workflow and collect final output
        result = None
        async for event in self._workflow.run_stream(task):
            if isinstance(event, WorkflowOutputEvent):
                # The event.data might be a ChatMessage object or string
                data = event.data
                if hasattr(data, 'content'):
                    # It's a ChatMessage object
                    result = str(data.content)
                elif hasattr(data, 'text'):
                    # It might have a text attribute
                    result = str(data.text)
                else:
                    # Otherwise just convert to string
                    result = str(data)
                print(f"✅ Magentic workflow completed with result length: {len(result)} chars")
        
        # Send result to output formatter
        if result:
            await ctx.send_message(result)
        else:
            print("⚠️  No result from Magentic workflow")
            await ctx.send_message("No result was produced by the workflow.")


class OutputFormatter(Executor):
    """Formats the final result from the Magentic workflow."""
    
    def __init__(self, dispatcher=None, **kwargs):
        super().__init__(**kwargs)
        self.dispatcher = dispatcher
    
    @handler
    async def format_output(self, result: str, ctx: WorkflowContext) -> None:
        """Format and yield the final result."""
        from datetime import datetime
        
        # Calculate execution time
        end_time = datetime.now()
        start_time = self.dispatcher.start_time if self.dispatcher else None
        
        if start_time:
            duration = end_time - start_time
            duration_seconds = duration.total_seconds()
            duration_str = f"{duration_seconds:.2f} seconds ({duration.seconds // 60}m {duration.seconds % 60}s)"
        else:
            duration_str = "Unknown (start time not recorded)"
        
        print(f"⏱️  End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Total duration: {duration_str}")
        
        formatted = f"""
{'=' * 80}
🎯 MAGENTIC WORKFLOW RESULT
{'=' * 80}

{result}

{'=' * 80}
⏱️  EXECUTION TIME
{'=' * 80}
Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else 'Unknown'}
End Time:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration:   {duration_str}
{'=' * 80}
✅ Workflow Complete
{'=' * 80}
"""
        
        # Save to file
        output_dir = Path("workflow_outputs")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"magentic_result_{timestamp}.txt"
        
        output_file.write_text(formatted, encoding='utf-8')
        print(f"\n📄 Results saved to: {output_file}")
        
        await ctx.yield_output(formatted)


def create_magentic_workflow():
    """Create the Magentic workflow with researcher and coder agents."""
    
    # Get Azure OpenAI configuration from environment
    deployment_name = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not deployment_name:
        raise ValueError(
            "Azure OpenAI deployment name not found. Please set one of:\n"
            "  - AZURE_OPENAI_CHAT_DEPLOYMENT_NAME\n"
            "  - AZURE_OPENAI_DEPLOYMENT_NAME\n"
            "in your .env file or environment variables."
        )
    
    print(f"🤖 Using Azure OpenAI deployment: {deployment_name}")
    
    # Create Azure OpenAI chat client with Azure CLI credentials
    chat_client = AzureOpenAIChatClient(
        credential=AzureCliCredential(),
        deployment_name=deployment_name
    )
    
    researcher_agent = ChatAgent(
        name="ResearcherAgent",
        description="Specialist in research and information gathering",
        instructions=(
            "You are a Researcher. You find information without additional computation or quantitative analysis. "
            "Provide detailed, well-researched information on the topic requested."
        ),
        chat_client=chat_client,
    )

    coder_agent = ChatAgent(
        name="CoderAgent",
        description="A helpful assistant that writes and executes code to process and analyze data.",
        instructions="You solve questions using code. Please provide detailed analysis and computation process.",
        chat_client=chat_client,
        tools=HostedCodeInterpreterTool(),
    )

    # Build Magentic workflow with Azure OpenAI manager
    magentic_workflow = (
        MagenticBuilder()
        .participants(researcher=researcher_agent, coder=coder_agent)
        .with_standard_manager(
            chat_client=chat_client,
            max_round_count=5,  # Reduced for faster completion
            max_stall_count=2,
            max_reset_count=1,
        )
        .build()
    )
    
    # Wrap Magentic workflow with input/output handling for DevUI
    dispatcher = InputDispatcher(id="input_dispatcher")
    magentic_executor = MagenticWorkflowExecutor(
        magentic_workflow=magentic_workflow,
        id="magentic_workflow"
    )
    output_formatter = OutputFormatter(id="output_formatter", dispatcher=dispatcher)
    
    # Build complete workflow
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    builder.add_edge(dispatcher, magentic_executor)
    builder.add_edge(magentic_executor, output_formatter)
    
    return builder.build()


def launch_devui():
    """Launch the Magentic workflow with DevUI interface."""
    
    print("=" * 70)
    print("🚀 Launching Magentic Multi-Agent Workflow with DevUI")
    print("=" * 70)
    print("✅ Agents:")
    print("   1. 🔍 ResearcherAgent - Information gathering")
    print("   2. 💻 CoderAgent - Code execution and analysis")
    print("✅ Orchestration: Magentic Standard Manager")
    print("✅ Chat Client: Azure OpenAI (via Azure CLI credentials)")
    print("✅ Max Rounds: 5 | Max Stalls: 2 | Max Resets: 1")
    print("✅ Web UI: http://localhost:8100")
    print("=" * 70)
    print()
    print("💡 Example tasks:")
    print("   - Analyze energy efficiency of ML models")
    print("   - Research and compute complex calculations")
    print("   - Multi-step research with data analysis")
    print("=" * 70)
    
    workflow = create_magentic_workflow()
    
    # Serve through DevUI
    serve(
        entities=[workflow],
        port=8100,
        auto_open=False,
        tracing_enabled=False
    )


if __name__ == "__main__":
    launch_devui()

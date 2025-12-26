"""
Agentic UI - Planning Agent that breaks down tasks into structured plans.
"""
import asyncio
import json
import uuid
from typing import AsyncIterator, Optional

from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from models import Plan, Step, StepStatus, JsonPatchOperation


class PlanningAgent:
    """Agent that creates and manages task plans with streaming updates."""
    
    def __init__(self, chat_client):
        """Initialize the planning agent."""
        self.chat_client = chat_client
        self.current_plan: Optional[Plan] = None
        self.console = Console()
        
        # Create the agent with planning tools
        self.agent = ChatAgent(
            name="PlanningAgent",
            instructions="""You are an expert project planner and task breakdown specialist.

When a user asks you to plan or break down a task:
1. Use create_plan to generate a comprehensive plan with 5-10 steps
2. Each step should be clear, actionable, and properly sequenced
3. Include rationale for why each step is necessary
4. Estimate realistic durations for each step

Guidelines:
- Make steps specific and measurable
- Consider dependencies between steps
- Include validation/testing steps where appropriate
- Think about edge cases and error handling

After creating the plan, provide a brief summary explaining the approach.""",
            chat_client=self.chat_client,
            tools=[self.create_plan_tool, self.update_step_status_tool]
        )
    
    @ai_function
    async def create_plan_tool(
        self,
        title: str,
        description: str,
        steps: list[dict]
    ) -> str:
        """Create a new task plan.
        
        Args:
            title: Brief title for the plan
            description: What this plan will accomplish
            steps: List of steps, each with: description, rationale, estimated_duration
            
        Returns:
            Confirmation message with plan ID
        """
        plan_id = str(uuid.uuid4())[:8]
        
        # Convert dict steps to Step objects
        step_objects = []
        for i, step_data in enumerate(steps, start=1):
            step_objects.append(Step(
                step_number=i,
                description=step_data.get("description", ""),
                rationale=step_data.get("rationale"),
                estimated_duration=step_data.get("estimated_duration"),
                status=StepStatus.NOT_STARTED
            ))
        
        self.current_plan = Plan(
            id=plan_id,
            title=title,
            description=description,
            steps=step_objects
        )
        
        return f"Plan '{title}' created with {len(step_objects)} steps (ID: {plan_id})"
    
    @ai_function
    async def update_step_status_tool(
        self,
        step_number: int,
        status: str
    ) -> str:
        """Update the status of a specific step.
        
        Args:
            step_number: The step number to update (1-based)
            status: New status (not_started, in_progress, completed, failed)
            
        Returns:
            Confirmation message
        """
        if not self.current_plan:
            return "No active plan to update"
        
        try:
            new_status = StepStatus(status)
            if self.current_plan.update_step_status(step_number, new_status):
                return f"Step {step_number} status updated to {status}"
            else:
                return f"Step {step_number} not found"
        except ValueError:
            return f"Invalid status: {status}"
    
    async def create_plan(self, task: str) -> Optional[Plan]:
        """Ask the agent to create a plan for a task."""
        self.console.print(f"\n[bold blue]Creating plan for:[/bold blue] {task}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task_id = progress.add_task("Analyzing task and generating plan...", total=None)
            
            # Run agent to create plan
            response = await self.agent.run(task)
            progress.stop()
        
        # Display the agent's response
        self.console.print(f"\n[dim]{response.text}[/dim]\n")
        
        # Display the created plan
        if self.current_plan:
            self.display_plan(self.current_plan)
            return self.current_plan
        
        return None
    
    async def execute_plan_with_updates(self, plan: Plan) -> AsyncIterator[JsonPatchOperation]:
        """Simulate executing a plan with streaming status updates."""
        self.console.print("\n[bold green]🚀 Starting plan execution...[/bold green]\n")
        
        for step in plan.steps:
            # Update to in_progress
            patch = JsonPatchOperation(
                op="replace",
                path=f"/steps/{step.step_number - 1}/status",
                value=StepStatus.IN_PROGRESS.value
            )
            yield patch
            plan.update_step_status(step.step_number, StepStatus.IN_PROGRESS)
            self.display_plan(plan, highlight_step=step.step_number)
            
            # Simulate work
            duration = 2.0 + (step.step_number * 0.5)  # Increasing duration
            await asyncio.sleep(duration)
            
            # Update to completed
            patch = JsonPatchOperation(
                op="replace",
                path=f"/steps/{step.step_number - 1}/status",
                value=StepStatus.COMPLETED.value
            )
            yield patch
            plan.update_step_status(step.step_number, StepStatus.COMPLETED)
            self.display_plan(plan, highlight_step=step.step_number)
        
        self.console.print("\n[bold green]✅ Plan execution completed![/bold green]")
    
    def display_plan(self, plan: Plan, highlight_step: Optional[int] = None):
        """Display the plan in a nice table format."""
        self.console.clear()
        
        # Header
        self.console.print(f"\n[bold magenta]📋 {plan.title}[/bold magenta]")
        self.console.print(f"[dim]{plan.description}[/dim]")
        self.console.print(f"[dim]Plan ID: {plan.id}[/dim]")
        
        # Progress
        progress_pct = plan.get_progress_percentage()
        self.console.print(f"\n[bold]Progress:[/bold] {progress_pct:.0f}%")
        
        # Steps table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=3)
        table.add_column("Step", min_width=40)
        table.add_column("Status", width=15)
        table.add_column("Duration", width=12)
        
        for step in plan.steps:
            # Status styling
            status_style = {
                StepStatus.NOT_STARTED: "[dim]⭕ Not Started[/dim]",
                StepStatus.IN_PROGRESS: "[yellow]🔄 In Progress[/yellow]",
                StepStatus.COMPLETED: "[green]✅ Completed[/green]",
                StepStatus.FAILED: "[red]❌ Failed[/red]"
            }.get(step.status, step.status.value)
            
            # Highlight current step
            step_style = "bold" if step.step_number == highlight_step else ""
            
            table.add_row(
                str(step.step_number),
                f"[{step_style}]{step.description}[/{step_style}]",
                status_style,
                step.estimated_duration or "-"
            )
        
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")


async def main():
    """Demo the planning agent."""
    import os
    
    # Initialize Azure OpenAI client
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    if not endpoint:
        print("❌ AZURE_OPENAI_ENDPOINT environment variable not set")
        return
    
    client = AzureOpenAIResponsesClient(
        endpoint=endpoint,
        deployment_name=deployment,
        credential=DefaultAzureCredential()
    )
    
    chat_client = client.create_chat_client()
    agent = PlanningAgent(chat_client)
    
    # Example tasks
    console = Console()
    
    console.print("\n[bold cyan]🤖 Agentic UI Planning Agent Demo[/bold cyan]")
    console.print("[dim]This agent creates structured plans that can be rendered as interactive UI[/dim]\n")
    
    tasks = [
        "Build a REST API for user management",
        "Set up CI/CD pipeline for a Python project",
        "Migrate database from PostgreSQL to Azure Cosmos DB"
    ]
    
    console.print("[bold]Available example tasks:[/bold]")
    for i, task in enumerate(tasks, start=1):
        console.print(f"  {i}. {task}")
    console.print("  [dim]Or type your own task[/dim]\n")
    
    choice = console.input("[bold]Enter task number or custom task:[/bold] ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(tasks):
        task = tasks[int(choice) - 1]
    else:
        task = choice
    
    # Create the plan
    plan = await agent.create_plan(task)
    
    if plan:
        console.input("\n[dim]Press Enter to simulate execution with streaming updates...[/dim]")
        
        # Execute with streaming updates
        async for patch in agent.execute_plan_with_updates(plan):
            # In a real UI, you'd apply these JSON patches to update the display
            pass


if __name__ == "__main__":
    asyncio.run(main())

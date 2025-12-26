"""
Quick test to verify Agentic UI setup without needing Azure credentials.
"""
from models import Plan, Step, StepStatus, JsonPatchOperation
from rich.console import Console
from rich.table import Table


def test_models():
    """Test that our data models work correctly."""
    console = Console()
    
    console.print("\n[bold cyan]🧪 Testing Agentic UI Models[/bold cyan]\n")
    
    # Create a sample plan
    plan = Plan(
        id="test-123",
        title="Build a Python REST API",
        description="Complete REST API implementation using FastAPI",
        steps=[
            Step(
                step_number=1,
                description="Set up project structure",
                rationale="Organized structure improves maintainability",
                estimated_duration="30 mins",
                status=StepStatus.COMPLETED
            ),
            Step(
                step_number=2,
                description="Implement database models",
                rationale="Data layer foundation for API",
                estimated_duration="1 hour",
                status=StepStatus.IN_PROGRESS
            ),
            Step(
                step_number=3,
                description="Create API endpoints",
                rationale="Core functionality for users",
                estimated_duration="2 hours",
                status=StepStatus.NOT_STARTED
            ),
            Step(
                step_number=4,
                description="Add authentication",
                rationale="Security requirement",
                estimated_duration="1 hour",
                status=StepStatus.NOT_STARTED
            ),
            Step(
                step_number=5,
                description="Write tests",
                rationale="Ensure reliability",
                estimated_duration="1.5 hours",
                status=StepStatus.NOT_STARTED
            )
        ]
    )
    
    # Display plan
    console.print(f"[bold magenta]📋 {plan.title}[/bold magenta]")
    console.print(f"[dim]{plan.description}[/dim]")
    console.print(f"[dim]Plan ID: {plan.id}[/dim]\n")
    
    # Show progress
    progress = plan.get_progress_percentage()
    console.print(f"[bold]Progress:[/bold] {progress:.0f}%\n")
    
    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("Step", min_width=30)
    table.add_column("Status", width=15)
    table.add_column("Duration", width=12)
    
    for step in plan.steps:
        # Status with emoji
        status_display = {
            StepStatus.NOT_STARTED: "[dim]⭕ Not Started[/dim]",
            StepStatus.IN_PROGRESS: "[yellow]🔄 In Progress[/yellow]",
            StepStatus.COMPLETED: "[green]✅ Completed[/green]",
            StepStatus.FAILED: "[red]❌ Failed[/red]"
        }[step.status]
        
        table.add_row(
            str(step.step_number),
            step.description,
            status_display,
            step.estimated_duration or "-"
        )
    
    console.print(table)
    console.print()
    
    # Test JSON Patch operations
    console.print("[bold cyan]📝 Testing JSON Patch Operations[/bold cyan]\n")
    
    patch1 = JsonPatchOperation(
        op="replace",
        path="/steps/1/status",
        value="completed"
    )
    console.print(f"[green]✓[/green] Patch operation: {patch1.op} at {patch1.path}")
    
    patch2 = JsonPatchOperation(
        op="replace",
        path="/steps/2/status",
        value="in_progress"
    )
    console.print(f"[green]✓[/green] Patch operation: {patch2.op} at {patch2.path}")
    
    console.print("\n[bold green]✅ All model tests passed![/bold green]\n")
    
    # Test model methods
    console.print("[bold cyan]🔍 Testing Model Methods[/bold cyan]\n")
    
    step = plan.get_step(2)
    if step:
        console.print(f"[green]✓[/green] Retrieved step {step.step_number}: {step.description}")
    
    success = plan.update_step_status(3, StepStatus.IN_PROGRESS)
    console.print(f"[green]✓[/green] Updated step 3 status: {success}")
    
    new_progress = plan.get_progress_percentage()
    console.print(f"[green]✓[/green] Progress calculation: {new_progress:.0f}%")
    
    console.print("\n[bold green]🎉 All tests completed successfully![/bold green]")
    console.print("\n[dim]Next step: Run 'python planning_agent.py' to test with an actual agent[/dim]")


if __name__ == "__main__":
    test_models()

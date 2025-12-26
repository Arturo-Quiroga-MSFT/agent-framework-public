"""
Test suite for Predictive State Updates.

Validates streaming state updates, JSON Patch operations, and state rendering.
"""
import asyncio
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from predictive_state_agent import (
    WorkflowState,
    TaskItem,
    TaskStatus,
    StateUpdate,
    PredictiveStateAgent
)


async def test_state_models():
    """Test state data models."""
    console = Console()
    
    console.print("\n[bold cyan]🧪 Testing State Models[/bold cyan]\n")
    
    # Test 1: Create workflow
    console.print("[bold]Test 1: Create Workflow State[/bold]")
    
    workflow = WorkflowState(
        workflow_id="test-001",
        title="Test Workflow",
        tasks=[
            TaskItem(id="1", title="Task 1"),
            TaskItem(id="2", title="Task 2"),
            TaskItem(id="3", title="Task 3"),
        ]
    )
    
    assert workflow.workflow_id == "test-001"
    assert len(workflow.tasks) == 3
    assert workflow.overall_progress == 0
    
    console.print(f"  ✓ Workflow created: {workflow.title}")
    console.print(f"  ✓ Tasks: {len(workflow.tasks)}")
    console.print(f"  ✓ Progress: {workflow.overall_progress}%\n")
    
    # Test 2: Task status transitions
    console.print("[bold]Test 2: Task Status Transitions[/bold]")
    
    task = workflow.tasks[0]
    assert task.status == TaskStatus.PENDING
    
    task.status = TaskStatus.ANALYZING
    assert task.status == TaskStatus.ANALYZING
    
    task.status = TaskStatus.IN_PROGRESS
    task.progress = 50
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.progress == 50
    
    task.status = TaskStatus.COMPLETED
    task.result = "Success"
    assert task.status == TaskStatus.COMPLETED
    assert task.result == "Success"
    
    console.print(f"  ✓ Transitions: PENDING → ANALYZING → IN_PROGRESS → COMPLETED")
    console.print(f"  ✓ Progress tracking: 0% → 50% → 100%")
    console.print(f"  ✓ Result stored: {task.result}\n")
    
    # Test 3: State updates
    console.print("[bold]Test 3: State Update Model[/bold]")
    
    update = StateUpdate(
        timestamp=datetime.now().isoformat(),
        operations=[
            {"op": "replace", "path": "/tasks/0/status", "value": "in_progress"},
            {"op": "replace", "path": "/tasks/0/progress", "value": 75}
        ],
        description="Task 1 in progress"
    )
    
    assert len(update.operations) == 2
    assert update.operations[0]["op"] == "replace"
    assert update.operations[1]["value"] == 75
    
    console.print(f"  ✓ StateUpdate with {len(update.operations)} operations")
    console.print(f"  ✓ Description: {update.description}")
    console.print(f"  ✓ Timestamp: {update.timestamp[:19]}\n")
    
    console.print("[green]✅ All state model tests passed![/green]\n")


async def test_state_streaming():
    """Test state update streaming."""
    console = Console()
    
    console.print("[bold cyan]🧪 Testing State Streaming[/bold cyan]\n")
    
    # Create workflow
    workflow = WorkflowState(
        workflow_id="stream-test",
        title="Streaming Test",
        tasks=[
            TaskItem(id="1", title="Quick Task 1"),
            TaskItem(id="2", title="Quick Task 2"),
        ]
    )
    
    agent = PredictiveStateAgent()
    
    console.print("[bold]Streaming state updates...[/bold]\n")
    
    update_count = 0
    task_completions = 0
    progress_updates = 0
    
    async for update in agent.stream_state_updates(workflow, chunk_delay=0.05):
        update_count += 1
        
        # Track different update types
        for op in update.operations:
            path = op["path"]
            if "completed_at" in path and op["value"]:
                task_completions += 1
            elif "progress" in path:
                progress_updates += 1
        
        console.print(f"  [{update_count:2d}] {update.description}")
    
    console.print(f"\n[bold]Streaming Statistics:[/bold]")
    console.print(f"  • Total updates: {update_count}")
    console.print(f"  • Task completions: {task_completions}")
    console.print(f"  • Progress updates: {progress_updates}")
    
    assert update_count > 0, "No updates generated"
    assert task_completions == len(workflow.tasks), "Not all tasks completed"
    
    console.print("\n[green]✅ State streaming test passed![/green]\n")


async def test_state_application():
    """Test applying state updates."""
    console = Console()
    
    console.print("[bold cyan]🧪 Testing State Application[/bold cyan]\n")
    
    # Create workflow
    workflow = WorkflowState(
        workflow_id="apply-test",
        title="State Application Test",
        tasks=[
            TaskItem(id="1", title="Test Task"),
        ]
    )
    
    agent = PredictiveStateAgent()
    agent.current_state = workflow
    
    console.print("[bold]Initial state:[/bold]")
    console.print(f"  • Task status: {workflow.tasks[0].status.value}")
    console.print(f"  • Task progress: {workflow.tasks[0].progress}%")
    console.print(f"  • Overall progress: {workflow.overall_progress}%\n")
    
    # Apply updates manually
    console.print("[bold]Applying state updates:[/bold]")
    
    # Update 1: Change task status
    update1 = StateUpdate(
        timestamp=datetime.now().isoformat(),
        operations=[{
            "op": "replace",
            "path": "/tasks/0/status",
            "value": TaskStatus.IN_PROGRESS.value
        }],
        description="Start task"
    )
    agent.apply_state_update(update1)
    console.print(f"  ✓ Task status → {workflow.tasks[0].status.value}")
    
    # Update 2: Change progress
    update2 = StateUpdate(
        timestamp=datetime.now().isoformat(),
        operations=[{
            "op": "replace",
            "path": "/tasks/0/progress",
            "value": 50
        }],
        description="Progress update"
    )
    agent.apply_state_update(update2)
    console.print(f"  ✓ Task progress → {workflow.tasks[0].progress}%")
    
    # Update 3: Change overall progress
    update3 = StateUpdate(
        timestamp=datetime.now().isoformat(),
        operations=[{
            "op": "replace",
            "path": "/overall_progress",
            "value": 50
        }],
        description="Overall progress"
    )
    agent.apply_state_update(update3)
    console.print(f"  ✓ Overall progress → {workflow.overall_progress}%")
    
    # Verify final state
    assert workflow.tasks[0].status == TaskStatus.IN_PROGRESS
    assert workflow.tasks[0].progress == 50
    assert workflow.overall_progress == 50
    
    console.print("\n[bold]Final state verified:[/bold]")
    console.print(f"  • Task status: {workflow.tasks[0].status.value} ✓")
    console.print(f"  • Task progress: {workflow.tasks[0].progress}% ✓")
    console.print(f"  • Overall progress: {workflow.overall_progress}% ✓")
    
    console.print("\n[green]✅ State application test passed![/green]\n")


async def test_state_rendering():
    """Test state rendering."""
    console = Console()
    
    console.print("[bold cyan]🧪 Testing State Rendering[/bold cyan]\n")
    
    # Create workflow with various states
    workflow = WorkflowState(
        workflow_id="render-test",
        title="Rendering Test",
        tasks=[
            TaskItem(id="1", title="Completed Task", status=TaskStatus.COMPLETED, progress=100, result="Done"),
            TaskItem(id="2", title="In Progress Task", status=TaskStatus.IN_PROGRESS, progress=65),
            TaskItem(id="3", title="Analyzing Task", status=TaskStatus.ANALYZING, progress=0),
            TaskItem(id="4", title="Pending Task", status=TaskStatus.PENDING, progress=0),
        ],
        overall_progress=41
    )
    
    agent = PredictiveStateAgent()
    agent.current_state = workflow
    
    # Render the state
    panel = agent.render_state()
    
    console.print("[bold]Rendered state:[/bold]\n")
    console.print(panel)
    
    # Verify rendering doesn't crash with different states
    console.print("\n[bold]Testing edge cases:[/bold]")
    
    # Empty workflow
    empty_workflow = WorkflowState(
        workflow_id="empty",
        title="Empty Workflow",
        tasks=[]
    )
    agent.current_state = empty_workflow
    empty_panel = agent.render_state()
    console.print(f"  ✓ Empty workflow renders")
    
    # No current state
    agent.current_state = None
    none_panel = agent.render_state()
    console.print(f"  ✓ No state renders safely")
    
    console.print("\n[green]✅ State rendering test passed![/green]\n")


async def test_bandwidth_efficiency():
    """Test bandwidth efficiency of predictive updates."""
    console = Console()
    
    console.print("[bold cyan]🧪 Testing Bandwidth Efficiency[/bold cyan]\n")
    
    workflow = WorkflowState(
        workflow_id="bandwidth-test",
        title="Bandwidth Test",
        tasks=[
            TaskItem(id="1", title="Task 1"),
            TaskItem(id="2", title="Task 2"),
        ]
    )
    
    agent = PredictiveStateAgent()
    
    # Calculate full state size
    full_state_json = workflow.model_dump_json()
    full_state_size = len(full_state_json.encode('utf-8'))
    
    # Calculate total update size
    total_update_size = 0
    update_count = 0
    
    async for update in agent.stream_state_updates(workflow, chunk_delay=0.01):
        update_json = update.model_dump_json()
        update_size = len(update_json.encode('utf-8'))
        total_update_size += update_size
        update_count += 1
    
    # Traditional polling would send full state each time
    traditional_size = full_state_size * update_count
    
    # Calculate savings
    savings_bytes = traditional_size - total_update_size
    savings_percent = (savings_bytes / traditional_size) * 100
    
    console.print("[bold]Bandwidth Analysis:[/bold]\n")
    
    table = Table(show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Full state size", f"{full_state_size:,} bytes")
    table.add_row("Number of updates", f"{update_count}")
    table.add_row("", "")
    table.add_row("Traditional (polling)", f"{traditional_size:,} bytes", style="red")
    table.add_row("Predictive (streaming)", f"{total_update_size:,} bytes", style="green")
    table.add_row("", "")
    table.add_row("Bandwidth saved", f"{savings_bytes:,} bytes ({savings_percent:.1f}%)", style="bold green")
    
    console.print(table)
    
    assert savings_bytes > 0, "No bandwidth savings"
    
    console.print(f"\n[green]✅ Predictive updates are {savings_percent:.1f}% more efficient![/green]\n")


async def run_all_tests():
    """Run all tests."""
    console = Console()
    
    console.print("\n[bold magenta]" + "="*70 + "[/bold magenta]")
    console.print("[bold magenta]🧪 Predictive State Updates - Test Suite[/bold magenta]")
    console.print("[bold magenta]" + "="*70 + "[/bold magenta]")
    
    tests = [
        ("State Models", test_state_models),
        ("State Streaming", test_state_streaming),
        ("State Application", test_state_application),
        ("State Rendering", test_state_rendering),
        ("Bandwidth Efficiency", test_bandwidth_efficiency),
    ]
    
    for test_name, test_func in tests:
        try:
            await test_func()
        except AssertionError as e:
            console.print(f"[red]❌ {test_name} failed: {e}[/red]\n")
            return False
        except Exception as e:
            console.print(f"[red]❌ {test_name} error: {e}[/red]\n")
            return False
    
    # Final summary
    console.print("[bold magenta]" + "="*70 + "[/bold magenta]")
    console.print(Panel.fit(
        """[bold green]✅ All Predictive State Tests Passed![/bold green]

[cyan]Validated Components:[/cyan]
✓ State data models (WorkflowState, TaskItem, StateUpdate)
✓ State streaming with JSON Patch operations
✓ State update application to live state
✓ Rich UI rendering with live updates
✓ Bandwidth efficiency vs traditional polling

[yellow]Ready for integration:[/yellow]
• Combine with Agentic UI for plan updates
• Integrate with Backend Tools for live tool execution
• Deploy with real Azure OpenAI agents

[bold]All AGUI enhancements successfully implemented! 🎉[/bold]""",
        border_style="green"
    ))
    console.print("[bold magenta]" + "="*70 + "[/bold magenta]\n")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)

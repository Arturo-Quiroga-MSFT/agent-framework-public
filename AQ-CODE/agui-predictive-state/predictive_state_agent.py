"""
Predictive State Updates - Stream partial state changes for real-time UI updates.

This demonstrates how agents can stream incremental state updates to clients
using JSON Patch operations, enabling progressive UI rendering without waiting
for full completion.
"""
import asyncio
import os
from datetime import datetime
from typing import AsyncIterator, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text


# ============================================================================
# DATA MODELS
# ============================================================================

class TaskStatus(Enum):
    """Status of a task in the workflow."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskItem(BaseModel):
    """Individual task in a workflow."""
    id: str
    title: str
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0  # 0-100
    result: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class WorkflowState(BaseModel):
    """Complete state of a workflow execution."""
    workflow_id: str
    title: str
    tasks: list[TaskItem]
    overall_progress: int = 0
    current_task_index: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class StateUpdate(BaseModel):
    """A single state update using JSON Patch operations."""
    timestamp: str
    operations: list[dict[str, Any]]
    description: str


# ============================================================================
# PREDICTIVE STATE AGENT
# ============================================================================

class PredictiveStateAgent:
    """Agent that streams state updates as work progresses."""
    
    def __init__(self):
        """Initialize the predictive state agent."""
        self.console = Console()
        self.current_state: Optional[WorkflowState] = None
    
    async def stream_state_updates(
        self,
        workflow: WorkflowState,
        chunk_delay: float = 0.3
    ) -> AsyncIterator[StateUpdate]:
        """Stream state updates as the workflow progresses.
        
        Args:
            workflow: Initial workflow state
            chunk_delay: Delay between state updates (seconds)
            
        Yields:
            StateUpdate objects with JSON Patch operations
        """
        self.current_state = workflow
        
        # Initial state update
        yield StateUpdate(
            timestamp=datetime.now().isoformat(),
            operations=[{
                "op": "replace",
                "path": "/started_at",
                "value": datetime.now().isoformat()
            }],
            description="Workflow started"
        )
        
        await asyncio.sleep(chunk_delay)
        
        # Process each task
        for task_idx, task in enumerate(workflow.tasks):
            # Update current task index
            yield StateUpdate(
                timestamp=datetime.now().isoformat(),
                operations=[{
                    "op": "replace",
                    "path": "/current_task_index",
                    "value": task_idx
                }],
                description=f"Moving to task {task_idx + 1}"
            )
            await asyncio.sleep(chunk_delay * 0.5)
            
            # Start task - update status
            yield StateUpdate(
                timestamp=datetime.now().isoformat(),
                operations=[
                    {
                        "op": "replace",
                        "path": f"/tasks/{task_idx}/status",
                        "value": TaskStatus.ANALYZING.value
                    },
                    {
                        "op": "replace",
                        "path": f"/tasks/{task_idx}/started_at",
                        "value": datetime.now().isoformat()
                    }
                ],
                description=f"Analyzing: {task.title}"
            )
            await asyncio.sleep(chunk_delay)
            
            # Mark as in progress
            yield StateUpdate(
                timestamp=datetime.now().isoformat(),
                operations=[{
                    "op": "replace",
                    "path": f"/tasks/{task_idx}/status",
                    "value": TaskStatus.IN_PROGRESS.value
                }],
                description=f"Executing: {task.title}"
            )
            await asyncio.sleep(chunk_delay * 0.5)
            
            # Stream progress updates (0% -> 100%)
            for progress in [25, 50, 75, 100]:
                yield StateUpdate(
                    timestamp=datetime.now().isoformat(),
                    operations=[{
                        "op": "replace",
                        "path": f"/tasks/{task_idx}/progress",
                        "value": progress
                    }],
                    description=f"{task.title}: {progress}% complete"
                )
                await asyncio.sleep(chunk_delay * 0.3)
            
            # Complete task
            result = f"✓ {task.title} completed successfully"
            yield StateUpdate(
                timestamp=datetime.now().isoformat(),
                operations=[
                    {
                        "op": "replace",
                        "path": f"/tasks/{task_idx}/status",
                        "value": TaskStatus.COMPLETED.value
                    },
                    {
                        "op": "replace",
                        "path": f"/tasks/{task_idx}/result",
                        "value": result
                    },
                    {
                        "op": "replace",
                        "path": f"/tasks/{task_idx}/completed_at",
                        "value": datetime.now().isoformat()
                    }
                ],
                description=f"Completed: {task.title}"
            )
            await asyncio.sleep(chunk_delay)
            
            # Update overall progress
            overall_progress = int(((task_idx + 1) / len(workflow.tasks)) * 100)
            yield StateUpdate(
                timestamp=datetime.now().isoformat(),
                operations=[{
                    "op": "replace",
                    "path": "/overall_progress",
                    "value": overall_progress
                }],
                description=f"Workflow {overall_progress}% complete"
            )
            await asyncio.sleep(chunk_delay * 0.5)
        
        # Final completion
        yield StateUpdate(
            timestamp=datetime.now().isoformat(),
            operations=[{
                "op": "replace",
                "path": "/completed_at",
                "value": datetime.now().isoformat()
            }],
            description="Workflow completed"
        )
    
    def apply_state_update(self, update: StateUpdate) -> None:
        """Apply a state update to the current state.
        
        Args:
            update: StateUpdate with JSON Patch operations
        """
        if not self.current_state:
            return
        
        for operation in update.operations:
            op = operation["op"]
            path = operation["path"]
            value = operation.get("value")
            
            # Parse path (e.g., "/tasks/0/status")
            parts = [p for p in path.split("/") if p]
            
            # Navigate to the target
            target = self.current_state
            for i, part in enumerate(parts[:-1]):
                if part.isdigit():
                    target = target[int(part)]
                else:
                    target = getattr(target, part)
            
            # Apply operation
            last_part = parts[-1]
            if op == "replace":
                if isinstance(target, list) and last_part.isdigit():
                    target[int(last_part)] = value
                elif isinstance(target, dict):
                    target[last_part] = value
                else:
                    # Handle TaskStatus enum conversion
                    if last_part == "status" and isinstance(value, str):
                        value = TaskStatus(value)
                    setattr(target, last_part, value)
    
    def render_state(self) -> Panel:
        """Render current state as a rich panel.
        
        Returns:
            Rich Panel with current state visualization
        """
        if not self.current_state:
            return Panel("No active workflow", border_style="dim")
        
        state = self.current_state
        
        # Build task table
        table = Table(show_header=True, header_style="bold cyan", box=None)
        table.add_column("Task", style="white", width=30)
        table.add_column("Status", width=12)
        table.add_column("Progress", width=15)
        table.add_column("Result", style="dim")
        
        for task in state.tasks:
            # Status with emoji
            status_map = {
                TaskStatus.PENDING: ("⏸️  Pending", "dim"),
                TaskStatus.ANALYZING: ("🔍 Analyzing", "yellow"),
                TaskStatus.IN_PROGRESS: ("⚙️  Working", "cyan"),
                TaskStatus.COMPLETED: ("✅ Done", "green"),
                TaskStatus.FAILED: ("❌ Failed", "red")
            }
            status_text, status_style = status_map[task.status]
            
            # Progress bar
            if task.progress == 0:
                progress_text = "—"
            else:
                bar_length = 10
                filled = int((task.progress / 100) * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                progress_text = f"{bar} {task.progress}%"
            
            # Result (truncate if too long)
            result_text = task.result[:40] + "..." if task.result and len(task.result) > 40 else task.result or ""
            
            table.add_row(
                task.title,
                Text(status_text, style=status_style),
                progress_text,
                result_text
            )
        
        # Build panel title with overall progress
        title = f"{state.title} - {state.overall_progress}% Complete"
        
        return Panel(
            table,
            title=title,
            border_style="cyan",
            padding=(1, 2)
        )


# ============================================================================
# DEMO
# ============================================================================

async def demo_predictive_state():
    """Demonstrate predictive state updates with live rendering."""
    console = Console()
    
    console.print("\n[bold cyan]🔄 Predictive State Updates Demo[/bold cyan]")
    console.print("[dim]Demonstrates streaming state changes for real-time UI updates[/dim]\n")
    
    # Create sample workflow
    workflow = WorkflowState(
        workflow_id="workflow-123",
        title="Deploy Web Application",
        tasks=[
            TaskItem(id="1", title="Build Docker image"),
            TaskItem(id="2", title="Run security scan"),
            TaskItem(id="3", title="Push to registry"),
            TaskItem(id="4", title="Deploy to staging"),
            TaskItem(id="5", title="Run integration tests"),
        ]
    )
    
    agent = PredictiveStateAgent()
    agent.current_state = workflow
    
    console.print("[bold]Initial State:[/bold]")
    console.print(agent.render_state())
    console.print("\n[yellow]Streaming state updates...[/yellow]\n")
    
    await asyncio.sleep(1)
    
    # Stream updates with live rendering
    with Live(agent.render_state(), console=console, refresh_per_second=10) as live:
        update_count = 0
        async for update in agent.stream_state_updates(workflow, chunk_delay=0.2):
            update_count += 1
            
            # Apply the update
            agent.apply_state_update(update)
            
            # Update the live display
            live.update(agent.render_state())
            
            # Log update details (optional, commented out for cleaner output)
            # console.log(f"[dim]Update {update_count}: {update.description}[/dim]")
    
    console.print("\n[bold green]✅ Workflow Completed![/bold green]")
    console.print(agent.render_state())
    
    # Show benefits
    console.print("\n[bold cyan]🎯 Benefits of Predictive State Updates[/bold cyan]\n")
    
    benefits = Table(show_header=False, box=None)
    benefits.add_row("✓", "[green]Real-time progress visibility")
    benefits.add_row("✓", "[green]Progressive UI rendering (no full reload)")
    benefits.add_row("✓", "[green]Reduced perceived latency")
    benefits.add_row("✓", "[green]Better user experience for long operations")
    benefits.add_row("✓", "[green]Efficient bandwidth usage (only deltas sent)")
    
    console.print(benefits)
    
    console.print("\n[bold]State Update Efficiency:[/bold]")
    console.print(f"  • Total updates streamed: {update_count}")
    console.print(f"  • Average update size: ~50-100 bytes (JSON Patch)")
    console.print(f"  • vs Full state: ~{len(workflow.model_dump_json())} bytes each time")
    console.print(f"  • [green]Bandwidth saved: ~{(update_count * len(workflow.model_dump_json())) // 1024}KB[/green]\n")


async def demo_comparison():
    """Show comparison between traditional vs predictive updates."""
    console = Console()
    
    console.print("\n[bold cyan]📊 Traditional vs Predictive State Updates[/bold cyan]\n")
    
    comparison = Table(title="State Update Patterns")
    comparison.add_column("Aspect", style="cyan")
    comparison.add_column("Traditional (Polling)", style="red")
    comparison.add_column("Predictive (Streaming)", style="green")
    
    comparison.add_row(
        "Update Frequency",
        "❌ Fixed interval (e.g., 1s)",
        "✅ As changes occur"
    )
    comparison.add_row(
        "Bandwidth",
        "❌ Full state each poll",
        "✅ Only deltas (JSON Patch)"
    )
    comparison.add_row(
        "Latency",
        "❌ Up to polling interval",
        "✅ Near real-time"
    )
    comparison.add_row(
        "Server Load",
        "❌ Constant polling load",
        "✅ Push-based (lower load)"
    )
    comparison.add_row(
        "Complexity",
        "✅ Simple to implement",
        "⚠️  Requires streaming support"
    )
    
    console.print(comparison)
    
    console.print("\n[bold]Example Scenario:[/bold] Deploy workflow with 5 tasks\n")
    
    scenarios = Table(show_header=False, box=None)
    scenarios.add_row(
        "[red]Traditional:[/red]",
        "Client polls every 1s → Receives full state (~500 bytes) × 20 polls = 10KB"
    )
    scenarios.add_row(
        "[green]Predictive:[/green]",
        "Server pushes updates (~80 bytes) × 25 updates = 2KB"
    )
    scenarios.add_row(
        "",
        "[bold green]✓ 80% bandwidth reduction[/bold green]"
    )
    
    console.print(scenarios)


if __name__ == "__main__":
    asyncio.run(demo_predictive_state())
    print("\n" + "="*70 + "\n")
    asyncio.run(demo_comparison())

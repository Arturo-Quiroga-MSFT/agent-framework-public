"""
Data models for Agentic UI - Plan and Step structures.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    """Status of a task step."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Step(BaseModel):
    """A single step in a plan."""
    step_number: int = Field(..., description="Sequential step number (1-based)")
    description: str = Field(..., description="Brief description of the step")
    status: StepStatus = Field(default=StepStatus.NOT_STARTED, description="Current status")
    rationale: Optional[str] = Field(None, description="Why this step is necessary")
    estimated_duration: Optional[str] = Field(None, description="Expected time to complete")


class Plan(BaseModel):
    """A complete plan with multiple steps."""
    id: str = Field(..., description="Unique identifier for the plan")
    title: str = Field(..., description="Plan title")
    description: str = Field(..., description="What this plan accomplishes")
    steps: list[Step] = Field(default_factory=list, description="Ordered list of steps")
    
    def get_step(self, step_number: int) -> Optional[Step]:
        """Get a specific step by number."""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None
    
    def update_step_status(self, step_number: int, status: StepStatus) -> bool:
        """Update the status of a specific step."""
        step = self.get_step(step_number)
        if step:
            step.status = status
            return True
        return False
    
    def get_progress_percentage(self) -> float:
        """Calculate completion percentage."""
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        return (completed / len(self.steps)) * 100


class JsonPatchOperation(BaseModel):
    """JSON Patch operation for incremental updates."""
    op: str = Field(..., description="Operation: 'add', 'remove', 'replace', 'move', 'copy', 'test'")
    path: str = Field(..., description="JSON pointer to the target location")
    value: Optional[str] = Field(None, description="Value for add/replace/test operations")
    from_: Optional[str] = Field(None, alias="from", description="Source path for move/copy")

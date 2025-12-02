"""
Dynamic Workflow Router - Core Module

This package provides dynamic workflow routing with Cosmos DB integration.
"""

from .workflow_router import DynamicWorkflowRouter
from .cosmos_loader import CosmosWorkflowLoader
from .agent_factory import WorkflowAgentFactory
from .workflow_executor import WorkflowExecutor

__all__ = [
    "DynamicWorkflowRouter",
    "CosmosWorkflowLoader",
    "WorkflowAgentFactory",
    "WorkflowExecutor",
]

__version__ = "1.0.0"

#!/usr/bin/env python3
"""
Workflow Agent Factory

Creates and manages workflow agents with lifecycle management integration.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add llmops to path for agent lifecycle manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "llmops"))

from azure.ai.projects.aio import AIProjectClient


class WorkflowAgentFactory:
    """
    Factory for creating and managing workflow agents.
    
    Integrates with LLMOps agent lifecycle manager to prevent
    agent proliferation in Azure AI Foundry.
    """
    
    def __init__(self, project_client: AIProjectClient):
        """
        Initialize agent factory.
        
        Args:
            project_client: Azure AI Project client
        """
        self.project_client = project_client
        self._agent_registry: Dict[str, str] = {}  # workflow_id -> agent_id
    
    async def get_or_create_agent(
        self,
        workflow_id: str,
        workflow_config: Dict[str, Any]
    ) -> str:
        """
        Get existing agent or create new one for workflow.
        
        Args:
            workflow_id: Workflow identifier
            workflow_config: Workflow configuration
            
        Returns:
            Agent ID
        """
        # Check if agent already exists
        if workflow_id in self._agent_registry:
            agent_id = self._agent_registry[workflow_id]
            
            # Verify agent still exists in Foundry
            try:
                await self.project_client.agents.get(agent_id)
                print(f"♻️  Reusing agent: {workflow_id}")
                return agent_id
            except Exception:
                # Agent no longer exists, remove from registry
                del self._agent_registry[workflow_id]
        
        # Create new agent
        agent_config = workflow_config.get("agent_config", {})
        
        agent = await self.project_client.agents.create(
            model=agent_config.get("model", "gpt-4o"),
            name=workflow_config.get("name", workflow_id),
            instructions=agent_config.get("instructions", ""),
            tools=self._prepare_tools(agent_config.get("tools", [])),
            temperature=agent_config.get("temperature"),
            top_p=agent_config.get("top_p")
        )
        
        self._agent_registry[workflow_id] = agent.id
        print(f"✨ Created agent: {workflow_id} ({agent.id})")
        
        return agent.id
    
    def _prepare_tools(self, tools: list) -> list:
        """
        Prepare tools configuration for MAF agent.
        
        Args:
            tools: Tool configurations from workflow
            
        Returns:
            MAF-compatible tools list
        """
        prepared_tools = []
        
        for tool in tools:
            tool_type = tool.get("type")
            
            if tool_type == "bing_grounding":
                prepared_tools.append({"type": "bing_grounding"})
            elif tool_type == "code_interpreter":
                prepared_tools.append({"type": "code_interpreter"})
            elif tool_type == "function":
                # Custom function tool
                prepared_tools.append({
                    "type": "function",
                    "function": tool.get("function", {})
                })
        
        return prepared_tools
    
    async def get_agent_id(self, workflow_id: str) -> Optional[str]:
        """
        Get agent ID for workflow if it exists.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Agent ID or None
        """
        return self._agent_registry.get(workflow_id)
    
    async def cleanup_agent(self, workflow_id: str) -> bool:
        """
        Cleanup agent for workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            True if cleaned up successfully
        """
        if workflow_id not in self._agent_registry:
            return False
        
        agent_id = self._agent_registry[workflow_id]
        
        try:
            await self.project_client.agents.delete(agent_id)
            del self._agent_registry[workflow_id]
            print(f"🧹 Cleaned up agent: {workflow_id}")
            return True
        except Exception as e:
            print(f"⚠️  Error cleaning up agent {workflow_id}: {e}")
            return False
    
    async def cleanup_all(self):
        """Cleanup all agents."""
        workflow_ids = list(self._agent_registry.keys())
        for workflow_id in workflow_ids:
            await self.cleanup_agent(workflow_id)
    
    def get_agent_count(self) -> int:
        """Get count of active agents."""
        return len(self._agent_registry)
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "total_agents": len(self._agent_registry),
            "workflow_ids": list(self._agent_registry.keys())
        }

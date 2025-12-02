#!/usr/bin/env python3
"""
Workflow Executor

Executes workflow agents and manages streaming responses.
"""

import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from azure.ai.projects.aio import AIProjectClient


class WorkflowExecutor:
    """
    Executes workflow agents with streaming support and observability.
    """
    
    def __init__(
        self,
        project_client: AIProjectClient,
        observability: Optional[Any] = None
    ):
        """
        Initialize workflow executor.
        
        Args:
            project_client: Azure AI Project client
            observability: Optional observability client
        """
        self.project_client = project_client
        self.observability = observability
        
        # Import agent factory
        from .agent_factory import WorkflowAgentFactory
        self.agent_factory = WorkflowAgentFactory(project_client)
    
    async def execute(
        self,
        workflow_config: Dict[str, Any],
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Execute a workflow with streaming support.
        
        Args:
            workflow_config: Workflow configuration from Cosmos DB
            user_input: User's input text
            context: Optional additional context
            stream: Stream responses (default: True)
            
        Yields:
            Response chunks if streaming
        """
        workflow_id = workflow_config["id"]
        start_time = datetime.utcnow()
        
        try:
            # Get or create agent
            agent_id = await self.agent_factory.get_or_create_agent(
                workflow_id=workflow_id,
                workflow_config=workflow_config
            )
            
            # Create thread
            thread = await self.project_client.agents.create_thread()
            
            # Prepare input with context
            full_input = user_input
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                full_input = f"{user_input}\n\nAdditional Context:\n{context_str}"
            
            # Add message
            await self.project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=full_input
            )
            
            # Execute with streaming
            total_tokens = 0
            response_text = ""
            
            if stream:
                async with self.project_client.agents.create_stream(
                    thread_id=thread.id,
                    assistant_id=agent_id
                ) as event_stream:
                    async for event in event_stream:
                        event_type = event.event
                        
                        if event_type == "thread.message.delta":
                            # Text content delta
                            if hasattr(event.data, 'delta') and hasattr(event.data.delta, 'content'):
                                for content in event.data.delta.content:
                                    if hasattr(content, 'text') and hasattr(content.text, 'value'):
                                        text = content.text.value
                                        response_text += text
                                        yield text
                        
                        elif event_type == "thread.run.completed":
                            # Track token usage
                            if hasattr(event.data, 'usage'):
                                total_tokens = event.data.usage.total_tokens
            
            else:
                # Non-streaming execution
                run = await self.project_client.agents.create_run(
                    thread_id=thread.id,
                    assistant_id=agent_id
                )
                
                # Wait for completion
                while run.status in ["queued", "in_progress"]:
                    await asyncio.sleep(0.5)
                    run = await self.project_client.agents.get_run(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                
                if run.status == "completed":
                    # Get response
                    messages = await self.project_client.agents.list_messages(
                        thread_id=thread.id
                    )
                    response_text = messages.data[0].content[0].text.value
                    
                    if hasattr(run, 'usage'):
                        total_tokens = run.usage.total_tokens
                    
                    yield response_text
                else:
                    yield f"Error: Workflow execution failed with status {run.status}"
            
            # Cleanup thread
            await self.project_client.agents.delete_thread(thread.id)
            
            # Track observability
            if self.observability:
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.observability.track_agent_call(
                    agent_name=workflow_id,
                    duration_ms=duration_ms,
                    tokens=total_tokens,
                    success=True
                )
        
        except Exception as e:
            error_msg = f"Error executing workflow {workflow_id}: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Track error
            if self.observability:
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.observability.track_agent_call(
                    agent_name=workflow_id,
                    duration_ms=duration_ms,
                    tokens=0,
                    success=False
                )
            
            yield f"Error: {error_msg}"

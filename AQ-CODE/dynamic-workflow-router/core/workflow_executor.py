#!/usr/bin/env python3
"""
Workflow Executor

Executes workflow agents and manages streaming responses.
"""

import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.aio import AgentsClient


class WorkflowExecutor:
    """
    Executes workflow agents with streaming support and observability.
    """
    
    def __init__(
        self,
        project_client: AIProjectClient,
        agents_client: Optional[AgentsClient] = None,
        observability: Optional[Any] = None
    ):
        """
        Initialize workflow executor.
        
        Args:
            project_client: Azure AI Project client
            agents_client: Optional Azure Agents client (if not provided, creates new one)
            observability: Optional observability client
        """
        self.project_client = project_client
        self.observability = observability
        
        # Use provided agents_client or create new one
        if agents_client:
            self.agents_client = agents_client
        else:
            # Create AgentsClient from the same endpoint
            from azure.identity.aio import DefaultAzureCredential
            endpoint = project_client._config.endpoint
            self.agents_client = AgentsClient(
                endpoint=endpoint,
                credential=DefaultAzureCredential()
            )
        
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
            thread = await self.agents_client.threads.create()
            
            # Prepare input with context
            full_input = user_input
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                full_input = f"{user_input}\n\nAdditional Context:\n{context_str}"
            
            # Add message
            await self.agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=full_input
            )
            
            # Execute with streaming
            total_tokens = 0
            response_text = ""
            
            if stream:
                # Create and run (non-streaming first for debugging)
                run = await self.agents_client.runs.create(
                    thread_id=thread.id,
                    agent_id=agent_id
                )
                
                # Poll for completion
                while run.status in ["queued", "in_progress", "requires_action"]:
                    await asyncio.sleep(0.5)
                    run = await self.agents_client.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                
                if run.status == "completed":
                    # Get messages
                    messages = await self.agents_client.messages.list(thread_id=thread.id)
                    if messages.data:
                        latest_message = messages.data[0]
                        if latest_message.content:
                            for content_item in latest_message.content:
                                # Handle different content types safely
                                try:
                                    if hasattr(content_item, 'text'):
                                        text_obj = content_item.text
                                        if hasattr(text_obj, 'value'):
                                            text = str(text_obj.value)  # Ensure it's a string
                                        else:
                                            # text object might be the string itself
                                            text = str(text_obj)
                                    else:
                                        # Content item might have the text directly
                                        text = str(content_item)
                                    
                                    response_text = text
                                    # Simulate streaming by yielding in chunks
                                    words = text.split()
                                    for word in words:
                                        yield word + " "
                                        await asyncio.sleep(0.05)  # Small delay for visual effect
                                except Exception as content_error:
                                    print(f"⚠️  Error processing content item: {content_error}")
                                    yield f"[Error reading response content: {content_error}]"
                    
                    if hasattr(run, 'usage'):
                        total_tokens = run.usage.total_tokens
                else:
                    yield f"Error: Run ended with status {run.status}"
            
            else:
                # Non-streaming execution
                run = await self.agents_client.runs.create(
                    thread_id=thread.id,
                    agent_id=agent_id
                )
                
                # Wait for completion
                while run.status in ["queued", "in_progress"]:
                    await asyncio.sleep(0.5)
                    run = await self.agents_client.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                
                if run.status == "completed":
                    # Get response
                    messages = await self.agents_client.messages.list(
                        thread_id=thread.id
                    )
                    try:
                        if messages.data and messages.data[0].content:
                            content_item = messages.data[0].content[0]
                            if hasattr(content_item, 'text'):
                                text_obj = content_item.text
                                if hasattr(text_obj, 'value'):
                                    response_text = str(text_obj.value)
                                else:
                                    response_text = str(text_obj)
                            else:
                                response_text = str(content_item)
                        else:
                            response_text = "[No response content]"
                    except Exception as parse_error:
                        response_text = f"[Error parsing response: {parse_error}]"
                    
                    if hasattr(run, 'usage'):
                        total_tokens = run.usage.total_tokens
                    
                    yield response_text
                else:
                    yield f"Error: Workflow execution failed with status {run.status}"
            
            # Cleanup thread
            await self.agents_client.threads.delete(thread.id)
            
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

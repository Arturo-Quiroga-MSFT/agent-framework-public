#!/usr/bin/env python3
"""
Dynamic Workflow Router

Main orchestrator that routes user requests to appropriate workflows
stored in Azure Cosmos DB using MAF agents.
"""

import asyncio
import os
import uuid
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

from .cosmos_loader import CosmosWorkflowLoader
from .agent_factory import WorkflowAgentFactory
from .workflow_executor import WorkflowExecutor


class DynamicWorkflowRouter:
    """
    Dynamic workflow router that uses LLM-based intent classification
    to route requests to appropriate workflow agents stored in Cosmos DB.
    """
    
    def __init__(
        self,
        project_connection_string: Optional[str] = None,
        cosmos_endpoint: Optional[str] = None,
        cosmos_key: Optional[str] = None,
        cosmos_database: str = "workflows",
        cosmos_container: str = "workflow_definitions",
        enable_cache: bool = True,
        cache_ttl_seconds: int = 300,
        fallback_workflow_id: Optional[str] = None,
        enable_observability: bool = False,
        observability_client: Optional[Any] = None
    ):
        """
        Initialize the dynamic workflow router.
        
        Args:
            project_connection_string: Azure AI Foundry connection string
            cosmos_endpoint: Cosmos DB endpoint URL
            cosmos_key: Cosmos DB access key
            cosmos_database: Database name (default: workflows)
            cosmos_container: Container name (default: workflow_definitions)
            enable_cache: Enable workflow caching
            cache_ttl_seconds: Cache TTL in seconds
            fallback_workflow_id: Workflow to use if no match found
            enable_observability: Enable observability tracking
            observability_client: Observability client instance
        """
        # Configuration
        self.project_connection_string = project_connection_string or os.getenv("PROJECT_CONNECTION_STRING")
        self.cosmos_endpoint = cosmos_endpoint or os.getenv("COSMOS_DB_ENDPOINT")
        self.cosmos_key = cosmos_key or os.getenv("COSMOS_DB_KEY")
        self.fallback_workflow_id = fallback_workflow_id
        
        # Clients (initialized on first use)
        self._project_client: Optional[AIProjectClient] = None
        self._orchestrator_agent_id: Optional[str] = None
        
        # Components
        self.workflow_loader = CosmosWorkflowLoader(
            endpoint=self.cosmos_endpoint,
            key=self.cosmos_key,
            database_name=cosmos_database,
            container_name=cosmos_container,
            enable_cache=enable_cache,
            cache_ttl_seconds=cache_ttl_seconds
        )
        
        self.agent_factory: Optional[WorkflowAgentFactory] = None
        self.workflow_executor: Optional[WorkflowExecutor] = None
        
        # Observability
        self.enable_observability = enable_observability
        self.observability = observability_client
        
        # State
        self._initialized = False
    
    async def _initialize(self):
        """Initialize clients and components (lazy initialization)."""
        if self._initialized:
            return
        
        if not self.project_connection_string:
            raise ValueError("PROJECT_CONNECTION_STRING is required")
        
        # Initialize Azure AI Project client
        # Handle both formats:
        # 1. Direct URL: https://...
        # 2. Connection string: key1=value1;key2=value2
        
        if self.project_connection_string.startswith('http'):
            # Direct URL format
            endpoint = self.project_connection_string
        else:
            # Parse connection string format
            conn_parts = {}
            for part in self.project_connection_string.split(';'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    conn_parts[key.strip()] = value.strip()
            
            # Extract endpoint
            endpoint = conn_parts.get('endpoint') or conn_parts.get('Endpoint')
            if not endpoint and 'HostName' in conn_parts:
                endpoint = f"https://{conn_parts['HostName']}"
            
            if not endpoint:
                raise ValueError("Invalid PROJECT_CONNECTION_STRING format - no endpoint found")
        
        self._project_client = AIProjectClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential()
        )
        
        # Initialize Cosmos DB loader
        await self.workflow_loader.initialize()
        
        # Initialize agent factory
        self.agent_factory = WorkflowAgentFactory(self._project_client)
        
        # Initialize workflow executor
        self.workflow_executor = WorkflowExecutor(
            project_client=self._project_client,
            observability=self.observability if self.enable_observability else None
        )
        
        # Create orchestrator agent
        await self._create_orchestrator_agent()
        
        self._initialized = True
        print("✅ Dynamic Workflow Router initialized")
    
    async def _create_orchestrator_agent(self):
        """Create the orchestrator agent for intent classification."""
        # Get all workflow metadata for context
        workflows = await self.workflow_loader.list_workflows()
        
        # Build workflow catalog for orchestrator
        workflow_catalog = "\n".join([
            f"- {wf['id']}: {wf.get('description', 'No description')}"
            for wf in workflows
            if wf.get('metadata', {}).get('enabled', True)
        ])
        
        instructions = f"""You are an intelligent workflow router. Your job is to analyze user input and determine which workflow should handle the request.

Available workflows:
{workflow_catalog}

Instructions:
1. Carefully analyze the user's input to understand their intent
2. Match the intent to the most appropriate workflow
3. Return ONLY the workflow ID (e.g., "customer_support_workflow")
4. If no workflow matches, return "no_match"
5. Be concise - return only the workflow ID

Examples:
User: "I need help with my order"
You: customer_support_workflow

User: "How do I integrate the API?"
You: technical_support_workflow

User: "I want to buy your product"
You: sales_inquiry_workflow
"""
        
        # Create orchestrator using agent factory
        self._orchestrator_agent_id = await self.agent_factory.get_or_create_agent(
            workflow_id="__orchestrator__",
            workflow_config={
                "agent_config": {
                    "model": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
                    "instructions": instructions,
                    "temperature": 0.3,  # Lower for more deterministic routing
                    "tools": []
                }
            }
        )
    
    async def classify_intent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Classify user intent and return workflow ID.
        
        Args:
            user_input: User's input text
            context: Optional additional context
            
        Returns:
            Workflow ID to execute
        """
        await self._initialize()
        
        start_time = datetime.utcnow()
        
        # Create thread for orchestrator
        thread = await self._project_client.agents.create_thread()
        
        # Add context if provided
        full_input = user_input
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_input = f"User input: {user_input}\n\nContext:\n{context_str}"
        
        # Send message
        await self._project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=full_input
        )
        
        # Get classification
        run = await self._project_client.agents.create_run(
            thread_id=thread.id,
            assistant_id=self._orchestrator_agent_id
        )
        
        # Wait for completion (with timeout)
        timeout = 30  # seconds
        elapsed = 0
        while run.status in ["queued", "in_progress"]:
            await asyncio.sleep(0.5)
            elapsed += 0.5
            if elapsed > timeout:
                raise TimeoutError("Intent classification timed out")
            
            run = await self._project_client.agents.get_run(
                thread_id=thread.id,
                run_id=run.id
            )
        
        if run.status != "completed":
            raise RuntimeError(f"Intent classification failed: {run.status}")
        
        # Get workflow ID from response
        messages = await self._project_client.agents.list_messages(thread_id=thread.id)
        workflow_id = messages.data[0].content[0].text.value.strip()
        
        # Track observability
        if self.enable_observability and self.observability:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.observability.track_agent_call(
                agent_name="orchestrator",
                duration_ms=duration_ms,
                tokens=run.usage.total_tokens if hasattr(run, 'usage') else 0,
                success=True
            )
        
        # Cleanup thread
        await self._project_client.agents.delete_thread(thread.id)
        
        return workflow_id
    
    async def route_and_execute(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Complete workflow: classify intent, load workflow, execute.
        
        Args:
            user_input: User's input text
            context: Optional additional context
            stream: Stream responses (default: True)
            
        Yields:
            Response chunks if streaming, else complete response
        """
        await self._initialize()
        
        print(f"📨 Processing: {user_input[:100]}...")
        
        # Step 1: Classify intent
        print("🔍 Classifying intent...")
        workflow_id = await self.classify_intent(user_input, context)
        print(f"✅ Selected workflow: {workflow_id}")
        
        # Handle no match
        if workflow_id == "no_match":
            if self.fallback_workflow_id:
                print(f"⚠️  No match, using fallback: {self.fallback_workflow_id}")
                workflow_id = self.fallback_workflow_id
            else:
                yield "I'm sorry, I couldn't determine how to help with that request. Please try rephrasing or provide more details."
                return
        
        # Step 2: Load workflow
        print(f"📥 Loading workflow configuration...")
        workflow_config = await self.workflow_loader.get_workflow(workflow_id)
        if not workflow_config:
            yield f"Error: Workflow '{workflow_id}' not found in database."
            return
        
        # Step 3: Execute workflow
        print(f"🚀 Executing workflow...")
        async for chunk in self.workflow_executor.execute(
            workflow_config=workflow_config,
            user_input=user_input,
            context=context,
            stream=stream
        ):
            yield chunk
    
    async def execute_workflow(
        self,
        workflow_id: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Execute a specific workflow directly (bypass intent classification).
        
        Args:
            workflow_id: Workflow ID to execute
            user_input: User's input text
            context: Optional additional context
            stream: Stream responses
            
        Yields:
            Response chunks
        """
        await self._initialize()
        
        # Load workflow
        workflow_config = await self.workflow_loader.get_workflow(workflow_id)
        if not workflow_config:
            yield f"Error: Workflow '{workflow_id}' not found."
            return
        
        # Execute
        async for chunk in self.workflow_executor.execute(
            workflow_config=workflow_config,
            user_input=user_input,
            context=context,
            stream=stream
        ):
            yield chunk
    
    async def list_workflows(self) -> list:
        """
        List all available workflows.
        
        Returns:
            List of workflow metadata
        """
        await self._initialize()
        return await self.workflow_loader.list_workflows()
    
    async def get_workflow_info(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow configuration
        """
        await self._initialize()
        return await self.workflow_loader.get_workflow(workflow_id)
    
    async def reload_workflows(self):
        """Reload workflow catalog (clears cache)."""
        await self._initialize()
        await self.workflow_loader.clear_cache()
        # Recreate orchestrator with updated catalog
        await self._create_orchestrator_agent()
        print("🔄 Workflows reloaded")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self._project_client:
            await self._project_client.close()
        
        if self.workflow_loader:
            await self.workflow_loader.close()
        
        if self.agent_factory:
            await self.agent_factory.cleanup_all()
        
        print("🧹 Cleanup complete")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

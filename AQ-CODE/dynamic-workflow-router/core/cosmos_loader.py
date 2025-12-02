#!/usr/bin/env python3
"""
Cosmos DB Workflow Loader

Loads workflow definitions from Azure Cosmos DB with caching support.
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey


class CosmosWorkflowLoader:
    """
    Loads and caches workflow definitions from Azure Cosmos DB.
    
    Supports:
    - Hierarchical partition keys
    - In-memory caching with TTL
    - Async operations
    - Query optimization
    """
    
    def __init__(
        self,
        endpoint: str,
        key: str,
        database_name: str = "workflows",
        container_name: str = "workflow_definitions",
        enable_cache: bool = True,
        cache_ttl_seconds: int = 300
    ):
        """
        Initialize Cosmos DB loader.
        
        Args:
            endpoint: Cosmos DB endpoint URL
            key: Cosmos DB access key
            database_name: Database name
            container_name: Container name
            enable_cache: Enable in-memory caching
            cache_ttl_seconds: Cache TTL in seconds
        """
        self.endpoint = endpoint
        self.key = key
        self.database_name = database_name
        self.container_name = container_name
        self.enable_cache = enable_cache
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        
        # Cosmos clients
        self.client: Optional[CosmosClient] = None
        self.database = None
        self.container = None
        
        # Cache
        self._workflow_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._list_cache: Optional[List[Dict[str, Any]]] = None
        self._list_cache_timestamp: Optional[datetime] = None
        
        # Initialized flag
        self._initialized = False
    
    async def initialize(self):
        """Initialize Cosmos DB client and connections."""
        if self._initialized:
            return
        
        if not self.endpoint or not self.key:
            raise ValueError("Cosmos DB endpoint and key are required")
        
        # Create async Cosmos client
        self.client = CosmosClient(self.endpoint, credential=self.key)
        
        # Get database and container
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)
        
        self._initialized = True
        print(f"✅ Connected to Cosmos DB: {self.database_name}/{self.container_name}")
    
    def _is_cache_valid(self, workflow_id: str) -> bool:
        """Check if cached workflow is still valid."""
        if not self.enable_cache:
            return False
        
        if workflow_id not in self._cache_timestamps:
            return False
        
        age = datetime.utcnow() - self._cache_timestamps[workflow_id]
        return age < self.cache_ttl
    
    def _is_list_cache_valid(self) -> bool:
        """Check if workflow list cache is valid."""
        if not self.enable_cache or not self._list_cache_timestamp:
            return False
        
        age = datetime.utcnow() - self._list_cache_timestamp
        return age < self.cache_ttl
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow configuration by ID.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow configuration or None if not found
        """
        if not self._initialized:
            await self.initialize()
        
        # Check cache
        if self._is_cache_valid(workflow_id):
            print(f"📦 Cache hit: {workflow_id}")
            return self._workflow_cache[workflow_id]
        
        try:
            # Query by ID (we don't know partition key)
            query = "SELECT * FROM c WHERE c.id = @workflow_id"
            parameters = [{"name": "@workflow_id", "value": workflow_id}]
            
            items = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ):
                items.append(item)
            
            if not items:
                print(f"⚠️  Workflow not found: {workflow_id}")
                return None
            
            workflow = items[0]
            
            # Validate workflow is enabled
            if not workflow.get("metadata", {}).get("enabled", True):
                print(f"⚠️  Workflow disabled: {workflow_id}")
                return None
            
            # Cache it
            if self.enable_cache:
                self._workflow_cache[workflow_id] = workflow
                self._cache_timestamps[workflow_id] = datetime.utcnow()
                print(f"💾 Cached: {workflow_id}")
            
            return workflow
        
        except Exception as e:
            print(f"❌ Error loading workflow {workflow_id}: {e}")
            return None
    
    async def list_workflows(
        self,
        category: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List all workflows or filter by category.
        
        Args:
            category: Optional category filter
            enabled_only: Only return enabled workflows
            
        Returns:
            List of workflow metadata
        """
        if not self._initialized:
            await self.initialize()
        
        # Check cache
        if not category and self._is_list_cache_valid():
            print("📦 Cache hit: workflow list")
            return self._list_cache
        
        try:
            # Build query
            conditions = []
            parameters = []
            
            if category:
                conditions.append("c.category = @category")
                parameters.append({"name": "@category", "value": category})
            
            if enabled_only:
                conditions.append("c.metadata.enabled = true")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            query = f"SELECT * FROM c WHERE {where_clause}"
            
            workflows = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters if parameters else None,
                enable_cross_partition_query=True
            ):
                workflows.append(item)
            
            # Cache if no filters
            if not category and self.enable_cache:
                self._list_cache = workflows
                self._list_cache_timestamp = datetime.utcnow()
                print(f"💾 Cached workflow list ({len(workflows)} items)")
            
            return workflows
        
        except Exception as e:
            print(f"❌ Error listing workflows: {e}")
            return []
    
    async def get_workflow_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all workflows in a category.
        
        Args:
            category: Category name
            
        Returns:
            List of workflows
        """
        return await self.list_workflows(category=category)
    
    async def search_workflows(
        self,
        keywords: List[str],
        search_fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search workflows by keywords.
        
        Args:
            keywords: Keywords to search for
            search_fields: Fields to search in (default: description, name, tags)
            
        Returns:
            Matching workflows
        """
        if not self._initialized:
            await self.initialize()
        
        search_fields = search_fields or ["description", "name", "metadata.tags"]
        
        try:
            # Build search conditions
            conditions = []
            parameters = []
            
            for i, keyword in enumerate(keywords):
                field_conditions = []
                for field in search_fields:
                    field_conditions.append(f"CONTAINS(LOWER(c.{field}), @keyword{i})")
                
                conditions.append(f"({' OR '.join(field_conditions)})")
                parameters.append({"name": f"@keyword{i}", "value": keyword.lower()})
            
            where_clause = " AND ".join(conditions)
            query = f"SELECT * FROM c WHERE {where_clause} AND c.metadata.enabled = true"
            
            results = []
            async for item in self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ):
                results.append(item)
            
            return results
        
        except Exception as e:
            print(f"❌ Error searching workflows: {e}")
            return []
    
    async def add_workflow(self, workflow: Dict[str, Any]) -> bool:
        """
        Add a new workflow to Cosmos DB.
        
        Args:
            workflow: Workflow configuration
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Add metadata
            if "metadata" not in workflow:
                workflow["metadata"] = {}
            
            workflow["metadata"]["created_at"] = datetime.utcnow().isoformat()
            workflow["metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            if "enabled" not in workflow["metadata"]:
                workflow["metadata"]["enabled"] = True
            
            # Create item
            await self.container.create_item(body=workflow)
            
            print(f"✅ Added workflow: {workflow['id']}")
            
            # Invalidate caches
            await self.clear_cache()
            
            return True
        
        except Exception as e:
            print(f"❌ Error adding workflow: {e}")
            return False
    
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing workflow.
        
        Args:
            workflow_id: Workflow ID
            updates: Fields to update
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get existing workflow
            workflow = await self.get_workflow(workflow_id)
            if not workflow:
                print(f"⚠️  Workflow not found: {workflow_id}")
                return False
            
            # Apply updates
            workflow.update(updates)
            workflow["metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            # Replace item
            await self.container.replace_item(
                item=workflow_id,
                body=workflow
            )
            
            print(f"✅ Updated workflow: {workflow_id}")
            
            # Invalidate cache
            if workflow_id in self._workflow_cache:
                del self._workflow_cache[workflow_id]
            if workflow_id in self._cache_timestamps:
                del self._cache_timestamps[workflow_id]
            
            return True
        
        except Exception as e:
            print(f"❌ Error updating workflow: {e}")
            return False
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow (soft delete by disabling).
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            True if successful
        """
        return await self.update_workflow(
            workflow_id,
            {"metadata": {"enabled": False}}
        )
    
    async def clear_cache(self):
        """Clear all caches."""
        self._workflow_cache.clear()
        self._cache_timestamps.clear()
        self._list_cache = None
        self._list_cache_timestamp = None
        print("🧹 Cache cleared")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "workflow_cache_size": len(self._workflow_cache),
            "list_cache_valid": self._is_list_cache_valid(),
            "cache_enabled": self.enable_cache,
            "cache_ttl_seconds": self.cache_ttl.total_seconds()
        }
    
    async def close(self):
        """Close Cosmos DB client."""
        if self.client:
            await self.client.close()
            print("🔌 Cosmos DB client closed")

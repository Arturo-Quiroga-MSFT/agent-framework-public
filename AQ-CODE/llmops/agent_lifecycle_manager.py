"""
Agent Lifecycle Manager for MAF LLMOps

Provides centralized management of agent instances to prevent resource proliferation
and enable agent reuse across multiple sessions.

Key Features:
- Agent registry with reuse capability
- Automatic cleanup on shutdown
- Thread-safe operations
- Usage statistics and monitoring
- Optional persistent registry (future)

Run: python AQ-CODE/llmops/agent_lifecycle_manager.py (for demo)
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from azure.identity.aio import DefaultAzureCredential

from agent_framework import ChatAgent, HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient


@dataclass
class AgentMetadata:
    """Metadata about a managed agent."""
    agent_name: str
    instructions: str
    web_search_enabled: bool
    created_at: str
    last_used: str
    use_count: int
    session_ids: list
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ProductionAgentManager:
    """
    Centralized manager for agent lifecycle.
    
    Prevents creating duplicate agents in Azure AI Foundry by maintaining
    a registry of active agents and reusing them across sessions.
    
    Features:
    - Agent reuse: Get existing agent or create new one
    - Thread-safe operations: Lock protects concurrent access
    - Usage tracking: Monitor agent usage patterns
    - Cleanup: Proper resource cleanup on shutdown
    
    Example:
        >>> # Get or create agent (reuses if exists)
        >>> agent, cred, client = await ProductionAgentManager.get_or_create_agent(
        ...     agent_name="market_analyst",
        ...     instructions="You are a market analyst...",
        ...     enable_web_search=True
        ... )
        >>> 
        >>> # Cleanup specific agent
        >>> await ProductionAgentManager.cleanup_agent("market_analyst")
        >>> 
        >>> # Cleanup all agents
        >>> await ProductionAgentManager.cleanup_all()
    """
    
    # Class-level storage (in-memory registry)
    _agents: Dict[str, Tuple[ChatAgent, DefaultAzureCredential, AzureAIAgentClient]] = {}
    _agent_metadata: Dict[str, AgentMetadata] = {}
    _lock = asyncio.Lock()
    _registry_path: Optional[Path] = None
    
    @classmethod
    def configure_persistent_registry(cls, registry_path: str | Path):
        """
        Configure persistent registry (optional).
        
        Enables saving agent metadata to disk for persistence across restarts.
        Note: Agent instances themselves cannot be persisted, only metadata.
        
        Args:
            registry_path: Path to JSON file for storing agent metadata
        """
        cls._registry_path = Path(registry_path)
        if cls._registry_path.exists():
            cls._load_registry()
    
    @classmethod
    def _load_registry(cls):
        """Load agent metadata from persistent storage."""
        if cls._registry_path and cls._registry_path.exists():
            try:
                with open(cls._registry_path, 'r') as f:
                    data = json.load(f)
                    # Note: We only load metadata, agents must be recreated
                    print(f"📁 Loaded agent registry from {cls._registry_path}")
                    print(f"   Found {len(data)} agent entries")
            except Exception as e:
                print(f"⚠️  Failed to load registry: {e}")
    
    @classmethod
    def _save_registry(cls):
        """Save agent metadata to persistent storage."""
        if cls._registry_path:
            try:
                data = {
                    name: meta.to_dict()
                    for name, meta in cls._agent_metadata.items()
                }
                cls._registry_path.parent.mkdir(parents=True, exist_ok=True)
                with open(cls._registry_path, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"⚠️  Failed to save registry: {e}")
    
    @classmethod
    async def get_or_create_agent(
        cls,
        agent_name: str,
        instructions: str,
        enable_web_search: bool = False,
        session_id: Optional[str] = None
    ) -> Tuple[ChatAgent, DefaultAzureCredential, AzureAIAgentClient]:
        """
        Get existing agent or create new one.
        
        This is the primary method for obtaining agent instances. It checks if
        an agent with the given name already exists and returns it, otherwise
        creates a new agent and stores it in the registry.
        
        Args:
            agent_name: Unique name for the agent
            instructions: System instructions for the agent
            enable_web_search: Whether to enable web search tool
            session_id: Optional session ID for tracking
            
        Returns:
            Tuple of (ChatAgent, DefaultAzureCredential, AzureAIAgentClient)
            
        Note:
            The returned resources should NOT be closed by the caller.
            Use cleanup_agent() or cleanup_all() for proper cleanup.
        """
        async with cls._lock:
            # Check if agent exists
            if agent_name in cls._agents:
                print(f"♻️  Reusing existing agent: {agent_name}")
                
                # Update metadata
                meta = cls._agent_metadata[agent_name]
                meta.last_used = datetime.now().isoformat()
                meta.use_count += 1
                if session_id and session_id not in meta.session_ids:
                    meta.session_ids.append(session_id)
                
                cls._save_registry()
                
                return cls._agents[agent_name]
            
            # Create new agent
            print(f"🆕 Creating new agent: {agent_name}")
            
            credential = DefaultAzureCredential()
            await credential.__aenter__()
            
            client = AzureAIAgentClient(async_credential=credential)
            await client.__aenter__()
            
            # Create tools if enabled
            tools = None
            if enable_web_search:
                tools = HostedWebSearchTool(
                    name="Web Search",
                    description="Search the web for current information"
                )
            
            # Create agent
            agent = ChatAgent(
                chat_client=client,
                instructions=instructions,
                name=agent_name,
                tools=tools if tools else None,
            )
            
            # Store in registry
            cls._agents[agent_name] = (agent, credential, client)
            cls._agent_metadata[agent_name] = AgentMetadata(
                agent_name=agent_name,
                instructions=instructions,
                web_search_enabled=enable_web_search,
                created_at=datetime.now().isoformat(),
                last_used=datetime.now().isoformat(),
                use_count=1,
                session_ids=[session_id] if session_id else []
            )
            
            cls._save_registry()
            
            print(f"✅ Agent '{agent_name}' created and registered")
            
            return cls._agents[agent_name]
    
    @classmethod
    async def cleanup_agent(cls, agent_name: str) -> bool:
        """
        Clean up specific agent and release its resources.
        
        Args:
            agent_name: Name of the agent to cleanup
            
        Returns:
            True if agent was cleaned up, False if not found
        """
        async with cls._lock:
            if agent_name not in cls._agents:
                print(f"⚠️  Agent '{agent_name}' not found in registry")
                return False
            
            print(f"🧹 Cleaning up agent: {agent_name}")
            
            agent, credential, client = cls._agents[agent_name]
            
            # Cleanup Azure resources
            try:
                await client.__aexit__(None, None, None)
                await credential.__aexit__(None, None, None)
            except Exception as e:
                print(f"⚠️  Error during cleanup: {e}")
            
            # Remove from registry
            del cls._agents[agent_name]
            del cls._agent_metadata[agent_name]
            
            cls._save_registry()
            
            print(f"✅ Agent '{agent_name}' cleaned up")
            return True
    
    @classmethod
    async def cleanup_all(cls):
        """Clean up all managed agents."""
        async with cls._lock:
            agent_names = list(cls._agents.keys())
            
            if not agent_names:
                print("ℹ️  No agents to cleanup")
                return
            
            print(f"🧹 Cleaning up {len(agent_names)} agent(s)...")
            
            for agent_name in agent_names:
                agent, credential, client = cls._agents[agent_name]
                try:
                    await client.__aexit__(None, None, None)
                    await credential.__aexit__(None, None, None)
                    print(f"   ✅ {agent_name}")
                except Exception as e:
                    print(f"   ⚠️  {agent_name}: {e}")
            
            cls._agents.clear()
            cls._agent_metadata.clear()
            
            cls._save_registry()
            
            print(f"✅ All agents cleaned up")
    
    @classmethod
    def get_agent_stats(cls) -> Dict[str, Any]:
        """
        Get statistics about managed agents.
        
        Returns:
            Dictionary with agent statistics including count, metadata, etc.
        """
        return {
            "total_agents": len(cls._agents),
            "agents": {
                name: {
                    "use_count": meta.use_count,
                    "created_at": meta.created_at,
                    "last_used": meta.last_used,
                    "sessions": len(meta.session_ids),
                    "web_search_enabled": meta.web_search_enabled
                }
                for name, meta in cls._agent_metadata.items()
            }
        }
    
    @classmethod
    def is_agent_registered(cls, agent_name: str) -> bool:
        """Check if agent is already registered."""
        return agent_name in cls._agents
    
    @classmethod
    def get_agent_metadata(cls, agent_name: str) -> Optional[AgentMetadata]:
        """Get metadata for a specific agent."""
        return cls._agent_metadata.get(agent_name)
    
    @classmethod
    def list_agents(cls) -> list[str]:
        """List all registered agent names."""
        return list(cls._agents.keys())


async def demo():
    """Demonstrate agent lifecycle management."""
    
    print("\n" + "="*80)
    print("🎯 Agent Lifecycle Manager - Demo")
    print("="*80 + "\n")
    
    # Configure persistent registry (optional)
    registry_path = Path(__file__).parent / "agent_registry.json"
    ProductionAgentManager.configure_persistent_registry(registry_path)
    
    print("📋 Phase 1: Creating agents\n")
    
    # Create first agent
    agent1, cred1, client1 = await ProductionAgentManager.get_or_create_agent(
        agent_name="market_analyst",
        instructions="You are a market analyst",
        enable_web_search=True,
        session_id="session_001"
    )
    
    # Create second agent
    agent2, cred2, client2 = await ProductionAgentManager.get_or_create_agent(
        agent_name="tech_advisor",
        instructions="You are a technical advisor",
        enable_web_search=False,
        session_id="session_002"
    )
    
    print("\n📊 Agent Statistics:")
    stats = ProductionAgentManager.get_agent_stats()
    print(f"   Total agents: {stats['total_agents']}")
    for name, info in stats['agents'].items():
        print(f"   - {name}: {info['use_count']} uses, {info['sessions']} sessions")
    
    print(f"\n📋 Phase 2: Reusing agents\n")
    
    # Try to get same agent (should reuse)
    agent1_reused, _, _ = await ProductionAgentManager.get_or_create_agent(
        agent_name="market_analyst",
        instructions="You are a market analyst",  # Same config
        enable_web_search=True,
        session_id="session_003"
    )
    
    # Verify it's the same instance
    print(f"\n🔍 Verification:")
    print(f"   Same agent instance? {agent1 is agent1_reused}")
    
    print("\n📊 Updated Statistics:")
    stats = ProductionAgentManager.get_agent_stats()
    for name, info in stats['agents'].items():
        print(f"   - {name}: {info['use_count']} uses, {info['sessions']} sessions")
    
    print(f"\n📋 Phase 3: List agents\n")
    
    agents = ProductionAgentManager.list_agents()
    print(f"   Registered agents: {', '.join(agents)}")
    
    print(f"\n📋 Phase 4: Cleanup\n")
    
    # Cleanup specific agent
    await ProductionAgentManager.cleanup_agent("tech_advisor")
    
    print(f"\n   Remaining agents: {', '.join(ProductionAgentManager.list_agents())}")
    
    # Cleanup all
    await ProductionAgentManager.cleanup_all()
    
    print(f"\n   Remaining agents: {ProductionAgentManager.list_agents() or 'None'}")
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80)
    print(f"\n💡 Key Takeaways:")
    print(f"   ✓ Agents are created once and reused")
    print(f"   ✓ Usage statistics are tracked")
    print(f"   ✓ Proper cleanup releases Azure resources")
    print(f"   ✓ Registry can be persisted to disk (optional)")
    print()


if __name__ == "__main__":
    asyncio.run(demo())

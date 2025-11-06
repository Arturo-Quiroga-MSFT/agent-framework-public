"""
Enhanced Production-Ready MAF Agent with Lifecycle Management

This version includes agent lifecycle management to prevent creating duplicate
agents in Azure AI Foundry on every instantiation.

Key Enhancements:
- Agent reuse through ProductionAgentManager
- Prevents resource proliferation in Foundry
- Maintains all existing LLMOps capabilities
- Backward compatible (optional reuse flag)

Run: python AQ-CODE/llmops/production_agent_with_lifecycle.py
"""

import asyncio
import os
import time
import uuid
import json
from pathlib import Path
from typing import Optional, Callable, Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv

from agent_framework import ChatMessage, Role, HostedWebSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

# Import LLMOps components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.observability import MAFObservability
from core.cost_tracker import CostTracker, TokenBudgetManager
from core.evaluator import AgentEvaluator

# Import lifecycle manager
from core.agent_lifecycle_manager import ProductionAgentManager

# Load environment
load_dotenv(Path(__file__).parent.parent.parent / "orchestration" / ".env")


class AgentStatus(Enum):
    """Agent execution status for UI updates."""
    INITIALIZING = "initializing"
    CHECKING_BUDGET = "checking_budget"
    RUNNING = "running"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ProgressUpdate:
    """Progress update for UI callbacks."""
    status: AgentStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class AgentResponse:
    """Structured agent response with all metadata."""
    success: bool
    response: Optional[str] = None
    request_id: Optional[str] = None
    agent_name: Optional[str] = None
    query: Optional[str] = None
    error: Optional[str] = None
    budget_exceeded: bool = False
    metrics: Optional[Dict[str, Any]] = None
    timestamp: str = None
    agent_reused: bool = False  # NEW: Track if agent was reused
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AgentPreset:
    """Pre-configured agent templates."""
    
    MARKET_ANALYST = {
        "name": "market_analyst",
        "instructions": (
            "You're a senior market analyst specializing in technology stock valuations. "
            "Use web search to find current stock prices, P/E ratios, and market data. "
            "Provide specific numbers, company names, and cite sources with dates. "
            "Be analytical and data-driven in your responses."
        ),
        "enable_web_search": True,
        "expected_topics": ["market data", "analysis", "numbers", "sources"]
    }
    
    RESEARCH_ASSISTANT = {
        "name": "research_assistant",
        "instructions": (
            "You're a thorough research assistant that helps users find accurate information. "
            "Always cite your sources and provide detailed, well-structured responses. "
            "Use web search when you need current information."
        ),
        "enable_web_search": True,
        "expected_topics": ["research", "sources", "detailed analysis"]
    }
    
    TECHNICAL_ADVISOR = {
        "name": "technical_advisor",
        "instructions": (
            "You're a technical advisor specializing in software development and architecture. "
            "Provide clear, actionable technical guidance with code examples when relevant. "
            "Focus on best practices, security, and scalability."
        ),
        "enable_web_search": False,
        "expected_topics": ["technical", "best practices", "examples"]
    }
    
    @classmethod
    def get_preset(cls, preset_name: str) -> Dict[str, Any]:
        """Get a preset configuration by name."""
        presets = {
            "market_analyst": cls.MARKET_ANALYST,
            "research_assistant": cls.RESEARCH_ASSISTANT,
            "technical_advisor": cls.TECHNICAL_ADVISOR,
        }
        return presets.get(preset_name, cls.RESEARCH_ASSISTANT)
    
    @classmethod
    def list_presets(cls) -> List[str]:
        """List available preset names."""
        return ["market_analyst", "research_assistant", "technical_advisor"]


class ProductionAgent:
    """
    Production-ready agent with LLMOps integration and lifecycle management.
    
    This version uses ProductionAgentManager to prevent creating duplicate agents
    in Azure AI Foundry. Agents are reused across instances with the same configuration.
    
    Key Features:
    - Agent reuse (via ProductionAgentManager)
    - Thread management for conversation continuity
    - Full LLMOps integration (observability, cost tracking, evaluation)
    - Progress callbacks for UI integration
    - Session management
    
    Example:
        >>> # Agent is created in Foundry only on first instantiation
        >>> agent1 = ProductionAgent("analyst", "You are an analyst", reuse_agent=True)
        >>> await agent1.run("What's NVIDIA's P/E ratio?")
        >>> 
        >>> # Subsequent instances reuse the same Foundry agent
        >>> agent2 = ProductionAgent("analyst", "You are an analyst", reuse_agent=True)
        >>> await agent2.run("What about Microsoft?")  # Same agent, new session
    """
    
    def __init__(
        self,
        agent_name: str,
        instructions: str,
        enable_web_search: bool = False,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
        enable_streaming: bool = False,
        reuse_agent: bool = True  # NEW: Enable agent reuse by default
    ):
        """Initialize production agent.
        
        Args:
            agent_name: Name of the agent
            instructions: System instructions for the agent
            enable_web_search: Whether to enable web search tool
            progress_callback: Optional callback for progress updates (for UI)
            enable_streaming: Enable streaming responses (future enhancement)
            reuse_agent: If True, reuse existing agent; if False, create new one
        """
        self.agent_name = agent_name
        self.instructions = instructions
        self.enable_web_search = enable_web_search
        self.progress_callback = progress_callback
        self.enable_streaming = enable_streaming
        self.reuse_agent = reuse_agent
        
        # Initialize LLMOps components (lightweight, OK per instance)
        self.observability = MAFObservability()
        self.cost_tracker = CostTracker()
        self.budget_manager = TokenBudgetManager()
        self.evaluator = AgentEvaluator()
        
        # Agent resources (managed by ProductionAgentManager if reuse_agent=True)
        self._agent = None
        self._credential = None
        self._client = None
        self._agent_was_reused = False
        
        # Store thread ID for conversation continuity (string, not object)
        self._thread_id = None
        
        # Session management
        self.chat_history: List[Dict[str, str]] = []
        self.session_id = str(uuid.uuid4())
    
    async def _ensure_agent(self):
        """
        Ensure agent is initialized.
        
        If reuse_agent=True, uses ProductionAgentManager to get or create agent.
        If reuse_agent=False, creates a new agent instance (old behavior).
        """
        if self._agent is not None:
            return  # Already initialized
        
        if self.reuse_agent:
            # Use lifecycle manager for agent reuse
            was_registered = ProductionAgentManager.is_agent_registered(self.agent_name)
            
            agent_tuple = await ProductionAgentManager.get_or_create_agent(
                agent_name=self.agent_name,
                instructions=self.instructions,
                enable_web_search=self.enable_web_search,
                session_id=self.session_id
            )
            
            self._agent, self._credential, self._client = agent_tuple
            self._agent_was_reused = was_registered
            
            if was_registered:
                self._emit_progress(
                    AgentStatus.INITIALIZING,
                    f"Reusing existing agent '{self.agent_name}'",
                    {"agent_reused": True}
                )
        else:
            # Create new agent (legacy behavior)
            self._emit_progress(
                AgentStatus.INITIALIZING,
                f"Creating new agent '{self.agent_name}'",
                {"agent_reused": False}
            )
            
            self._credential = DefaultAzureCredential()
            await self._credential.__aenter__()
            
            self._client = AzureAIAgentClient(async_credential=self._credential)
            await self._client.__aenter__()
            
            # Create tools if enabled
            tools = None
            if self.enable_web_search:
                tools = HostedWebSearchTool(
                    name="Web Search",
                    description="Search the web for current information"
                )
            
            # Create agent
            from agent_framework import ChatAgent
            self._agent = ChatAgent(
                chat_client=self._client,
                instructions=self.instructions,
                name=self.agent_name,
                tools=tools if tools else None,
            )
            
            self._agent_was_reused = False
    
    def _emit_progress(self, status: AgentStatus, message: str, data: Optional[Dict] = None):
        """Emit progress update if callback is set."""
        if self.progress_callback:
            update = ProgressUpdate(status=status, message=message, data=data)
            self.progress_callback(update)
    
    def add_to_history(self, role: str, content: str):
        """Add message to chat history."""
        self.chat_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get chat history."""
        return self.chat_history.copy()
    
    def clear_history(self):
        """Clear chat history and reset thread."""
        self.chat_history.clear()
        # Reset thread ID so a new thread is created on next query
        self._thread_id = None
    
    async def run(
        self,
        query: str,
        expected_topics: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> AgentResponse:
        """Run agent with full LLMOps pipeline.
        
        Args:
            query: User query
            expected_topics: Expected topics for evaluation
            user_id: Optional user identifier for tracking
            
        Returns:
            AgentResponse with structured data
        """
        # Ensure agent exists (creates or reuses)
        await self._ensure_agent()
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add to history
        self.add_to_history("user", query)
        
        try:
            # Step 1: Budget Check
            self._emit_progress(AgentStatus.CHECKING_BUDGET, "Checking token budget...")
            
            with self.observability.create_span("budget.check"):
                estimated_tokens = len(query.split()) * 1.5 + 500
                allowed, message = self.budget_manager.check_budget(int(estimated_tokens))
                
                if not allowed:
                    budget_stats = self.budget_manager.get_usage_stats()
                    self._emit_progress(
                        AgentStatus.ERROR,
                        f"Budget exceeded: {message}",
                        {"budget_stats": budget_stats}
                    )
                    return AgentResponse(
                        success=False,
                        error=message,
                        budget_exceeded=True,
                        request_id=request_id,
                        agent_name=self.agent_name,
                        query=query,
                        agent_reused=self._agent_was_reused
                    )
                
                self._emit_progress(
                    AgentStatus.CHECKING_BUDGET,
                    f"Budget check passed (estimated {int(estimated_tokens)} tokens)",
                    {"estimated_tokens": int(estimated_tokens)}
                )
            
            # Step 2: Run Agent
            self._emit_progress(AgentStatus.RUNNING, "Agent is processing your request...")
            
            with self.observability.create_span(
                f"agent.{self.agent_name}.execute",
                attributes={
                    "query_length": len(query),
                    "user_id": user_id or "anonymous",
                    "agent_reused": self._agent_was_reused
                }
            ):
                # Create or reuse thread (using stored ID)
                if self._thread_id:
                    thread = self._agent.get_new_thread(service_thread_id=self._thread_id)
                else:
                    thread = self._agent.get_new_thread()
                
                # Run agent with thread for conversation continuity
                result = await self._agent.run(query, thread=thread, store=True)
                
                # Store thread ID for next query
                if thread.service_thread_id:
                    self._thread_id = thread.service_thread_id
                
                response_text = str(result.text)
            
            # Add to history
            self.add_to_history("assistant", response_text)
            
            # Step 3: Track Costs
            prompt_tokens = int(len(query.split()) * 1.5)
            completion_tokens = int(len(response_text.split()) * 1.5)
            total_tokens = prompt_tokens + completion_tokens
            
            model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1")
            self.cost_tracker.record_cost(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                agent_name=self.agent_name
            )
            self.budget_manager.record_usage(request_id, total_tokens)
            
            cost_data = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "estimated_cost_usd": self.cost_tracker.get_total_cost()
            }
            
            self._emit_progress(
                AgentStatus.RUNNING,
                "Cost tracking updated",
                cost_data
            )
            
            # Step 4: Evaluation
            self._emit_progress(AgentStatus.EVALUATING, "Evaluating response quality...")
            
            with self.observability.create_span("evaluation"):
                eval_metrics = self.evaluator.evaluate_response(
                    response=response_text,
                    expected_topics=expected_topics or []
                )
            
            quality_label = self.evaluator.get_quality_label(eval_metrics['overall_score'])
            
            self._emit_progress(
                AgentStatus.EVALUATING,
                f"Quality evaluation: {quality_label}",
                {"evaluation": eval_metrics, "quality_label": quality_label}
            )
            
            # Success tracking
            duration_ms = (time.time() - start_time) * 1000
            self.observability.track_agent_call(
                agent_name=self.agent_name,
                duration_ms=duration_ms,
                tokens=total_tokens,
                success=True
            )
            
            # Build response
            agent_response = AgentResponse(
                success=True,
                response=response_text,
                request_id=request_id,
                agent_name=self.agent_name,
                query=query,
                agent_reused=self._agent_was_reused,
                metrics={
                    "duration_ms": duration_ms,
                    "tokens": cost_data,
                    "evaluation": eval_metrics,
                    "quality_label": quality_label,
                    "session_id": self.session_id,
                    "user_id": user_id,
                    "agent_reused": self._agent_was_reused
                }
            )
            
            self._emit_progress(
                AgentStatus.COMPLETED,
                "Request completed successfully",
                {"duration_ms": duration_ms, "request_id": request_id}
            )
            
            return agent_response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            self._emit_progress(
                AgentStatus.ERROR,
                f"Error occurred: {error_msg}",
                {"error": error_msg, "duration_ms": duration_ms}
            )
            
            self.observability.track_agent_call(
                agent_name=self.agent_name,
                duration_ms=duration_ms,
                tokens=0,
                success=False
            )
            
            return AgentResponse(
                success=False,
                error=error_msg,
                request_id=request_id,
                agent_name=self.agent_name,
                query=query,
                agent_reused=self._agent_was_reused
            )
    
    async def cleanup(self):
        """
        Cleanup resources.
        
        If reuse_agent=True, resources are managed by ProductionAgentManager,
        so we only clear local references.
        
        If reuse_agent=False, we own the resources and must clean them up.
        """
        if not self.reuse_agent and self._client is not None:
            # We own these resources, clean them up
            try:
                await self._client.__aexit__(None, None, None)
                await self._credential.__aexit__(None, None, None)
            except Exception as e:
                print(f"⚠️  Error during cleanup: {e}")
        
        # Clear local references
        self._agent = None
        self._client = None
        self._credential = None
    
    def get_cumulative_stats(self) -> Dict[str, Any]:
        """Get cumulative statistics for display."""
        cost_by_agent = self.cost_tracker.get_cost_by_agent()
        tokens_by_agent = self.cost_tracker.get_token_usage()
        budget_stats = self.budget_manager.get_usage_stats()
        
        return {
            "total_cost_usd": self.cost_tracker.get_total_cost(),
            "total_tokens": sum(tokens_by_agent.values()),
            "budget_stats": budget_stats,
            "cost_by_agent": cost_by_agent,
            "tokens_by_agent": tokens_by_agent,
            "session_id": self.session_id,
            "chat_history_length": len(self.chat_history),
            "agent_reused": self._agent_was_reused
        }
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export complete session data for analysis or download."""
        return {
            "session_id": self.session_id,
            "agent_name": self.agent_name,
            "agent_reused": self._agent_was_reused,
            "timestamp": datetime.now().isoformat(),
            "chat_history": self.get_history(),
            "statistics": self.get_cumulative_stats(),
            "configuration": {
                "instructions": self.instructions,
                "web_search_enabled": self.enable_web_search,
                "reuse_agent": self.reuse_agent
            }
        }
    
    @classmethod
    def from_preset(
        cls,
        preset_name: str,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
        reuse_agent: bool = True
    ) -> "ProductionAgent":
        """Create agent from preset configuration.
        
        Args:
            preset_name: Name of the preset (market_analyst, research_assistant, etc.)
            progress_callback: Optional callback for progress updates
            reuse_agent: If True, reuse existing agent; if False, create new one
            
        Returns:
            ProductionAgent instance
        """
        preset = AgentPreset.get_preset(preset_name)
        return cls(
            agent_name=preset["name"],
            instructions=preset["instructions"],
            enable_web_search=preset["enable_web_search"],
            progress_callback=progress_callback,
            reuse_agent=reuse_agent
        )


async def main():
    """Demo: Production MAF agent with lifecycle management."""
    
    print("\n" + "="*80)
    print("🚀 MAF Production Agent with Lifecycle Management - Demo")
    print("="*80)
    
    # Progress callback for demonstration
    def print_progress(update: ProgressUpdate):
        status_icons = {
            AgentStatus.INITIALIZING: "🔧",
            AgentStatus.CHECKING_BUDGET: "💰",
            AgentStatus.RUNNING: "🤖",
            AgentStatus.EVALUATING: "📊",
            AgentStatus.COMPLETED: "✅",
            AgentStatus.ERROR: "❌"
        }
        icon = status_icons.get(update.status, "ℹ️")
        print(f"{icon} [{update.timestamp}] {update.message}")
        if update.data:
            print(f"   Data: {json.dumps(update.data, indent=2)}")
    
    # Test 1: Create first agent (should create in Foundry)
    print(f"\n\n{'#'*80}")
    print(f"# Test 1: First Agent Instance")
    print(f"{'#'*80}\n")
    
    agent1 = ProductionAgent.from_preset(
        "market_analyst",
        progress_callback=print_progress,
        reuse_agent=True
    )
    
    result1 = await agent1.run(
        query="What is NVIDIA's current P/E ratio?",
        expected_topics=["P/E ratio", "NVIDIA"],
        user_id="demo_user_1"
    )
    
    print(f"\n📊 Result 1:")
    print(f"   Agent Reused: {result1.agent_reused}")
    print(f"   Success: {result1.success}")
    
    # Test 2: Create second agent with SAME config (should reuse)
    print(f"\n\n{'#'*80}")
    print(f"# Test 2: Second Agent Instance (Same Config)")
    print(f"{'#'*80}\n")
    
    agent2 = ProductionAgent.from_preset(
        "market_analyst",  # SAME preset
        progress_callback=print_progress,
        reuse_agent=True
    )
    
    result2 = await agent2.run(
        query="What about Microsoft's P/E ratio?",
        expected_topics=["P/E ratio", "Microsoft"],
        user_id="demo_user_2"
    )
    
    print(f"\n📊 Result 2:")
    print(f"   Agent Reused: {result2.agent_reused}")
    print(f"   Success: {result2.success}")
    
    # Show lifecycle manager stats
    print(f"\n\n{'#'*80}")
    print(f"# Agent Lifecycle Statistics")
    print(f"{'#'*80}\n")
    
    stats = ProductionAgentManager.get_agent_stats()
    print(f"📈 Lifecycle Manager Stats:")
    print(f"   Total Agents in Registry: {stats['total_agents']}")
    for name, info in stats['agents'].items():
        print(f"   - {name}:")
        print(f"      Uses: {info['use_count']}")
        print(f"      Sessions: {info['sessions']}")
        print(f"      Created: {info['created_at']}")
        print(f"      Last Used: {info['last_used']}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up resources...")
    await agent1.cleanup()
    await agent2.cleanup()
    await ProductionAgentManager.cleanup_all()
    
    print(f"\n\n{'='*80}")
    print("✅ Demo Complete!")
    print("="*80)
    print(f"\n💡 Key Features Demonstrated:")
    print(f"   ✓ Agent reuse across instances")
    print(f"   ✓ Lifecycle management through ProductionAgentManager")
    print(f"   ✓ Agent creation only on first use")
    print(f"   ✓ Thread management for conversation continuity")
    print(f"   ✓ Full LLMOps integration maintained")
    print(f"   ✓ Proper resource cleanup")
    print()


if __name__ == "__main__":
    asyncio.run(main())

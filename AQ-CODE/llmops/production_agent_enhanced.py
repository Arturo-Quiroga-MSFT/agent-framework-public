"""
Enhanced Production-Ready MAF Agent with LLMOps Integration

Enhancements for Streamlit UI:
- Callback system for real-time progress updates
- Session state management
- Streaming support
- Better error handling with user-friendly messages
- Configurable agent presets
- Chat history management
- Export functionality for metrics/responses

Run: python AQ-CODE/llmops/production_agent_enhanced.py
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
from observability import MAFObservability
from cost_tracker import CostTracker, TokenBudgetManager
from evaluator import AgentEvaluator

# Load environment
load_dotenv(Path(__file__).parent.parent / "orchestration" / ".env")


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
    """Production-ready agent with LLMOps integration and UI support."""
    
    def __init__(
        self,
        agent_name: str,
        instructions: str,
        enable_web_search: bool = False,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
        enable_streaming: bool = False
    ):
        """Initialize production agent.
        
        Args:
            agent_name: Name of the agent
            instructions: System instructions for the agent
            enable_web_search: Whether to enable web search tool
            progress_callback: Optional callback for progress updates (for UI)
            enable_streaming: Enable streaming responses (future enhancement)
        """
        self.agent_name = agent_name
        self.instructions = instructions
        self.enable_web_search = enable_web_search
        self.progress_callback = progress_callback
        self.enable_streaming = enable_streaming
        
        # Initialize LLMOps components
        self.observability = MAFObservability()
        self.cost_tracker = CostTracker()
        self.budget_manager = TokenBudgetManager()
        self.evaluator = AgentEvaluator()
        
        # Store thread ID for conversation continuity (string, not object)
        self._thread_id = None
        
        # Session management
        self.chat_history: List[Dict[str, str]] = []
        self.session_id = str(uuid.uuid4())
    
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
        await self.initialize()
        
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
                        query=query
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
                attributes={"query_length": len(query), "user_id": user_id or "anonymous"}
            ):
                # Create agent inside async context managers (working demo pattern)
                async with DefaultAzureCredential() as credential:
                    async with AzureAIAgentClient(async_credential=credential) as client:
                        # Create tools if enabled
                        tools = None
                        if self.enable_web_search:
                            tools = HostedWebSearchTool(
                                name="Web Search",
                                description="Search the web for current information"
                            )
                        
                        # Create agent
                        from agent_framework import ChatAgent
                        agent = ChatAgent(
                            chat_client=client,
                            instructions=self.instructions,
                            name=self.agent_name,
                            tools=tools if tools else None,
                        )
                        
                        # Create or reuse thread (using stored ID)
                        if self._thread_id:
                            thread = agent.get_new_thread(service_thread_id=self._thread_id)
                        else:
                            thread = agent.get_new_thread()
                        
                        # Run agent with thread for conversation continuity
                        result = await agent.run(query, thread=thread, store=True)
                        
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
                metrics={
                    "duration_ms": duration_ms,
                    "tokens": cost_data,
                    "evaluation": eval_metrics,
                    "quality_label": quality_label,
                    "session_id": self.session_id,
                    "user_id": user_id
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
                query=query
            )
    
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
            "chat_history_length": len(self.chat_history)
        }
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export complete session data for analysis or download."""
        return {
            "session_id": self.session_id,
            "agent_name": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "chat_history": self.get_history(),
            "statistics": self.get_cumulative_stats(),
            "configuration": {
                "instructions": self.instructions,
                "web_search_enabled": self.enable_web_search
            }
        }
    
    @classmethod
    def from_preset(
        cls,
        preset_name: str,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None
    ) -> "ProductionAgent":
        """Create agent from preset configuration.
        
        Args:
            preset_name: Name of the preset (market_analyst, research_assistant, etc.)
            progress_callback: Optional callback for progress updates
            
        Returns:
            ProductionAgent instance
        """
        preset = AgentPreset.get_preset(preset_name)
        return cls(
            agent_name=preset["name"],
            instructions=preset["instructions"],
            enable_web_search=preset["enable_web_search"],
            progress_callback=progress_callback
        )


async def main():
    """Demo: Enhanced production MAF agent."""
    
    print("\n" + "="*80)
    print("🚀 Enhanced MAF Production Agent - Demo")
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
    
    # Create agent from preset
    agent = ProductionAgent.from_preset("market_analyst", progress_callback=print_progress)
    
    # Test queries
    test_queries = [
        {
            "query": "What is NVIDIA's current P/E ratio and how does it compare to industry averages?",
            "expected_topics": ["P/E ratio", "NVIDIA", "comparison", "industry average"]
        },
        {
            "query": "What's your analysis of the previous stock?",  # Tests conversation context
            "expected_topics": ["NVIDIA", "analysis"]
        }
    ]
    
    # Run test queries
    for i, test in enumerate(test_queries, 1):
        print(f"\n\n{'#'*80}")
        print(f"# Query {i}/{len(test_queries)}")
        print(f"{'#'*80}\n")
        
        result = await agent.run(
            query=test["query"],
            expected_topics=test["expected_topics"],
            user_id="demo_user"
        )
        
        if result.success:
            print(f"\n📄 Response Preview:")
            print(f"{'-'*80}")
            print(result.response[:500] + "..." if len(result.response) > 500 else result.response)
            print(f"{'-'*80}\n")
        else:
            print(f"\n⚠️  Query failed: {result.error}\n")
        
        # Show cumulative stats
        stats = agent.get_cumulative_stats()
        print(f"\n📈 Cumulative Statistics:")
        print(f"   Total Cost: ${stats['total_cost_usd']:.4f}")
        print(f"   Total Tokens: {stats['total_tokens']:,}")
        print(f"   Budget Used: {stats['budget_stats']['percentage_used']:.1f}%")
        print(f"   Chat History: {stats['chat_history_length']} messages")
    
    # Export session data
    print(f"\n\n{'='*80}")
    print("📦 Exporting Session Data")
    print(f"{'='*80}\n")
    
    session_data = agent.export_session_data()
    export_path = Path(__file__).parent / f"session_export_{agent.session_id}.json"
    
    with open(export_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    print(f"✅ Session data exported to: {export_path}")
    print(f"   Session ID: {session_data['session_id']}")
    print(f"   Total Interactions: {len(session_data['chat_history']) // 2}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up resources...")
    await agent.cleanup()
    
    print(f"\n\n{'='*80}")
    print("✅ Demo Complete!")
    print("="*80)
    print(f"\n💡 Key Features Demonstrated:")
    print(f"   ✓ Progress callbacks for UI integration")
    print(f"   ✓ Structured responses with metadata")
    print(f"   ✓ Session management and chat history")
    print(f"   ✓ Agent presets for quick setup")
    print(f"   ✓ Export functionality for analysis")
    print(f"   ✓ Comprehensive error handling")
    print()


if __name__ == "__main__":
    asyncio.run(main())

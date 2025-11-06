"""
Example: Production-Ready MAF Agent with LLMOps Integration

This example demonstrates how to create a MAF agent with full LLMOps capabilities:
- Observability (tracing, metrics)
- Cost tracking and budget management
- Response evaluation
- Structured output

Run: python AQ-CODE/llmops/example_production_agent.py
"""

import asyncio
import os
import time
import uuid
from pathlib import Path
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

# Load environment
load_dotenv(Path(__file__).parent.parent.parent / "orchestration" / ".env")


class ProductionAgent:
    """Production-ready agent with LLMOps integration."""
    
    def __init__(self, agent_name: str, instructions: str, enable_web_search: bool = False):
        """Initialize production agent.
        
        Args:
            agent_name: Name of the agent
            instructions: System instructions for the agent
            enable_web_search: Whether to enable web search tool
        """
        self.agent_name = agent_name
        self.instructions = instructions
        self.enable_web_search = enable_web_search
        
        # Initialize LLMOps components
        self.observability = MAFObservability()
        self.cost_tracker = CostTracker()
        self.budget_manager = TokenBudgetManager()
        self.evaluator = AgentEvaluator()
        
        # Agent client (initialized lazily)
        self._client = None
        self._agent = None
        self._credential = None
    
    async def initialize(self):
        """Initialize Azure AI client and agent."""
        if self._agent is not None:
            return
        
        self._credential = await DefaultAzureCredential().__aenter__()
        self._client = await AzureAIAgentClient(async_credential=self._credential).__aenter__()
        
        # Create tools if enabled
        tools = None
        if self.enable_web_search:
            tools = HostedWebSearchTool(
                name="Web Search",
                description="Search the web for current information"
            )
        
        # Create agent
        self._agent = self._client.create_agent(
            instructions=self.instructions,
            name=self.agent_name,
            tools=tools
        )
        
        print(f"✅ Agent '{self.agent_name}' initialized")
    
    async def cleanup(self):
        """Cleanup Azure resources."""
        if self._client is not None:
            await self._client.__aexit__(None, None, None)
            self._client = None
        
        if self._credential is not None:
            await self._credential.__aexit__(None, None, None)
            self._credential = None
        
        self._agent = None
    
    async def run(self, query: str, expected_topics: list = None):
        """Run agent with full LLMOps pipeline.
        
        Args:
            query: User query
            expected_topics: Expected topics for evaluation
            
        Returns:
            Dictionary with response and metrics
        """
        await self.initialize()
        
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"🤖 Agent: {self.agent_name}")
        print(f"📝 Query: {query}")
        print(f"🆔 Request ID: {request_id}")
        print(f"{'='*80}")
        
        try:
            # Step 1: Budget Check
            with self.observability.create_span("budget.check"):
                estimated_tokens = len(query.split()) * 1.5 + 500
                allowed, message = self.budget_manager.check_budget(int(estimated_tokens))
                
                if not allowed:
                    print(f"❌ Budget Error: {message}")
                    budget_stats = self.budget_manager.get_usage_stats()
                    print(f"📊 Budget Status: {budget_stats['total_tokens']:,} / {budget_stats['budget']:,} tokens used ({budget_stats['percentage_used']:.1f}%)")
                    return {"error": message, "budget_exceeded": True}
                
                print(f"✅ Budget Check: OK (estimated {int(estimated_tokens)} tokens)")
            
            # Step 2: Run Agent
            print(f"🔄 Running agent...")
            with self.observability.create_span(
                f"agent.{self.agent_name}.execute",
                attributes={"query_length": len(query)}
            ):
                response = await self._agent.run(query)
                response_text = response.messages[-1].text if response.messages else ""
            
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
            
            print(f"💰 Cost Tracking:")
            print(f"   Prompt tokens: {prompt_tokens:,}")
            print(f"   Completion tokens: {completion_tokens:,}")
            print(f"   Total tokens: {total_tokens:,}")
            print(f"   Estimated cost: ${self.cost_tracker.get_total_cost():.4f}")
            
            # Step 4: Evaluation
            with self.observability.create_span("evaluation"):
                eval_metrics = self.evaluator.evaluate_response(
                    response=response_text,
                    expected_topics=expected_topics or []
                )
            
            quality_label = self.evaluator.get_quality_label(eval_metrics['overall_score'])
            print(f"\n📊 Quality Evaluation:")
            print(f"   Overall Score: {eval_metrics['overall_score']:.2f} ({quality_label})")
            print(f"   Topic Coverage: {eval_metrics['topic_coverage']:.0%}")
            print(f"   Has Citations: {'✅' if eval_metrics['has_citations'] else '❌'}")
            print(f"   Has Numbers: {'✅' if eval_metrics['has_numbers'] else '❌'}")
            print(f"   Well Structured: {'✅' if eval_metrics['has_structure'] else '❌'}")
            
            # Success tracking
            duration_ms = (time.time() - start_time) * 1000
            self.observability.track_agent_call(
                agent_name=self.agent_name,
                duration_ms=duration_ms,
                tokens=total_tokens,
                success=True
            )
            
            print(f"\n⏱️  Duration: {duration_ms:.0f}ms")
            print(f"\n💬 Response:")
            print(f"{'-'*80}")
            print(response_text)
            print(f"{'-'*80}")
            
            return {
                "success": True,
                "response": response_text,
                "request_id": request_id,
                "metrics": {
                    "duration_ms": duration_ms,
                    "tokens": total_tokens,
                    "evaluation": eval_metrics,
                    "cost_usd": self.cost_tracker.get_total_cost()
                }
            }
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            print(f"\n❌ Error: {str(e)}")
            
            self.observability.track_agent_call(
                agent_name=self.agent_name,
                duration_ms=duration_ms,
                tokens=0,
                success=False
            )
            
            return {"success": False, "error": str(e)}


async def main():
    """Demo: Production MAF agent with LLMOps."""
    
    print("\n" + "="*80)
    print("🚀 MAF Production Agent with LLMOps - Demo")
    print("="*80)
    
    # Create market analyst agent
    market_analyst = ProductionAgent(
        agent_name="market_analyst",
        instructions=(
            "You're a senior market analyst specializing in technology stock valuations. "
            "Use web search to find current stock prices, P/E ratios, and market data. "
            "Provide specific numbers, company names, and cite sources with dates. "
            "Be analytical and data-driven in your responses."
        ),
        enable_web_search=True
    )
    
    # Test queries
    test_queries = [
        {
            "query": "What is NVIDIA's current P/E ratio and how does it compare to industry averages?",
            "expected_topics": ["P/E ratio", "NVIDIA", "comparison", "industry average"]
        },
        {
            "query": "Is Microsoft overvalued based on its AI revenue?",
            "expected_topics": ["Microsoft", "valuation", "AI revenue", "analysis"]
        }
    ]
    
    # Run test queries
    for i, test in enumerate(test_queries, 1):
        print(f"\n\n{'#'*80}")
        print(f"# Test Query {i}/{len(test_queries)}")
        print(f"{'#'*80}")
        
        result = await market_analyst.run(
            query=test["query"],
            expected_topics=test["expected_topics"]
        )
        
        if not result.get("success"):
            print(f"\n⚠️  Query failed: {result.get('error')}")
        
        # Show cumulative stats
        print(f"\n📈 Cumulative Statistics:")
        cost_by_agent = market_analyst.cost_tracker.get_cost_by_agent()
        tokens_by_agent = market_analyst.cost_tracker.get_token_usage()
        budget_stats = market_analyst.budget_manager.get_usage_stats()
        
        print(f"   Total Cost: ${market_analyst.cost_tracker.get_total_cost():.4f}")
        print(f"   Total Tokens: {sum(tokens_by_agent.values()):,}")
        print(f"   Budget Used: {budget_stats['percentage_used']:.1f}% ({budget_stats['total_tokens']:,} / {budget_stats['budget']:,})")
        print(f"   Remaining: {budget_stats['remaining_tokens']:,} tokens")
    
    # Cleanup resources
    print(f"\n🧹 Cleaning up resources...")
    await market_analyst.cleanup()
    
    print(f"\n\n{'='*80}")
    print("✅ Demo Complete!")
    print("="*80)
    print(f"\n💡 Next Steps:")
    print(f"   - Review Application Insights for traces")
    print(f"   - Check cost tracking in the dashboard")
    print(f"   - Adjust budget limits in .env file")
    print(f"   - Add more evaluation metrics as needed")
    print()


if __name__ == "__main__":
    asyncio.run(main())

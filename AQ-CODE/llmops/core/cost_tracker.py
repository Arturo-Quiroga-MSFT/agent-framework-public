"""Cost tracking and budget management for MAF agents."""

import os
from typing import Tuple, Dict
from datetime import datetime
from collections import defaultdict
import threading


class CostTracker:
    """Track and analyze LLM costs for MAF agents."""
    
    # Pricing per 1K tokens (as of Nov 2025)
    PRICING = {
        "gpt-4.1": {"prompt": 0.03, "completion": 0.06},
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
        "gpt-5-mini": {"prompt": 0.0001, "completion": 0.0004}
    }
    
    def __init__(self):
        self.costs = []
        self.lock = threading.Lock()
    
    def record_cost(self, model: str, prompt_tokens: int, 
                   completion_tokens: int, agent_name: str):
        """Record cost for an LLM call.
        
        Args:
            model: Model name (e.g., 'gpt-4.1')
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            agent_name: Name of the agent making the call
        """
        if model not in self.PRICING:
            return
        
        cost = (
            (prompt_tokens / 1000) * self.PRICING[model]["prompt"] +
            (completion_tokens / 1000) * self.PRICING[model]["completion"]
        )
        
        with self.lock:
            self.costs.append({
                "timestamp": datetime.utcnow(),
                "model": model,
                "agent": agent_name,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost_usd": cost
            })
    
    def get_total_cost(self) -> float:
        """Get total accumulated cost."""
        with self.lock:
            return sum(entry["cost_usd"] for entry in self.costs)
    
    def get_cost_by_agent(self) -> Dict[str, float]:
        """Get costs grouped by agent."""
        with self.lock:
            agent_costs = defaultdict(float)
            for entry in self.costs:
                agent_costs[entry["agent"]] += entry["cost_usd"]
            return dict(agent_costs)
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get total token usage by agent."""
        with self.lock:
            agent_tokens = defaultdict(int)
            for entry in self.costs:
                agent_tokens[entry["agent"]] += entry["total_tokens"]
            return dict(agent_tokens)


class TokenBudgetManager:
    """Manage token budgets to control costs."""
    
    def __init__(self):
        self.daily_budget = int(os.getenv("DAILY_TOKEN_BUDGET", 1000000))
        self.per_request_limit = int(os.getenv("MAX_TOKENS_PER_REQUEST", 4000))
        self.usage = defaultdict(int)
        self.lock = threading.Lock()
        self.current_date = datetime.utcnow().date()
    
    def check_budget(self, estimated_tokens: int) -> Tuple[bool, str]:
        """Check if request is within budget.
        
        Args:
            estimated_tokens: Estimated tokens for the request
            
        Returns:
            Tuple of (allowed: bool, message: str)
        """
        with self.lock:
            # Reset daily counter if new day
            today = datetime.utcnow().date()
            if today != self.current_date:
                self.usage.clear()
                self.current_date = today
            
            # Check per-request limit
            if estimated_tokens > self.per_request_limit:
                return False, f"Request exceeds per-request limit ({self.per_request_limit} tokens)"
            
            # Check daily budget
            current_usage = sum(self.usage.values())
            if current_usage + estimated_tokens > self.daily_budget:
                return False, f"Daily budget exceeded ({self.daily_budget} tokens)"
            
            return True, "OK"
    
    def record_usage(self, request_id: str, tokens: int):
        """Record token usage for a request.
        
        Args:
            request_id: Unique request identifier
            tokens: Number of tokens used
        """
        with self.lock:
            self.usage[request_id] = tokens
    
    def get_usage_stats(self) -> dict:
        """Get current usage statistics."""
        with self.lock:
            total = sum(self.usage.values())
            return {
                "date": self.current_date.isoformat(),
                "total_tokens": total,
                "budget": self.daily_budget,
                "percentage_used": (total / self.daily_budget * 100) if self.daily_budget > 0 else 0,
                "requests_count": len(self.usage),
                "remaining_tokens": self.daily_budget - total
            }

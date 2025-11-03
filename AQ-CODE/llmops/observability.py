"""
Observability module for MAF agents.
Provides tracing, metrics, and monitoring integration with Application Insights.
"""

import os
import time
from typing import Optional
from agent_framework.observability import setup_observability
from opentelemetry import trace, metrics


class MAFObservability:
    """Observability setup for MAF agents with Application Insights integration."""
    
    def __init__(self):
        self.connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        self.enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() == "true"
        
        if self.enable_tracing:
            # Setup MAF observability
            if self.connection_string:
                setup_observability(
                    enable_sensitive_data=True,
                    applicationinsights_connection_string=self.connection_string
                )
            else:
                setup_observability(enable_sensitive_data=True)
            
            # Get tracers and meters
            self.tracer = trace.get_tracer(__name__)
            self.meter = metrics.get_meter(__name__)
            
            # Create custom metrics
            self.agent_calls_counter = self.meter.create_counter(
                name="maf.agent.calls",
                description="Number of agent calls",
                unit="1"
            )
            
            self.agent_latency_histogram = self.meter.create_histogram(
                name="maf.agent.latency",
                description="Agent call latency",
                unit="ms"
            )
            
            self.token_usage_counter = self.meter.create_counter(
                name="maf.tokens.used",
                description="Total tokens consumed",
                unit="tokens"
            )
        else:
            self.tracer = None
            self.meter = None
    
    def track_agent_call(self, agent_name: str, duration_ms: float, 
                        tokens: int, success: bool):
        """Track agent call metrics.
        
        Args:
            agent_name: Name of the agent
            duration_ms: Call duration in milliseconds
            tokens: Total tokens used
            success: Whether the call succeeded
        """
        if not self.enable_tracing:
            return
        
        attributes = {
            "agent.name": agent_name,
            "success": str(success)
        }
        
        self.agent_calls_counter.add(1, attributes)
        self.agent_latency_histogram.record(duration_ms, attributes)
        self.token_usage_counter.add(tokens, attributes)
    
    def create_span(self, name: str, attributes: dict = None):
        """Create a custom trace span.
        
        Args:
            name: Span name
            attributes: Optional attributes dictionary
            
        Returns:
            Trace span context manager
        """
        if not self.enable_tracing or not self.tracer:
            # Return a no-op context manager
            from contextlib import nullcontext
            return nullcontext()
        
        return self.tracer.start_as_current_span(
            name=name,
            attributes=attributes or {}
        )

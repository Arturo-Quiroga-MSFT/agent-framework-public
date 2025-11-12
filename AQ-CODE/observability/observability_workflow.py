# Copyright (c) Microsoft. All rights reserved.

"""
Workflow Observability Demo - Customer Feedback Analysis

This sample demonstrates the telemetry collected when running an Agent Framework workflow.
It shows a realistic business scenario with a 3-stage customer feedback analysis pipeline.

BUSINESS SCENARIO:
Process customer feedback through automated analysis:
1. Sentiment Analysis - Determine positive/negative/neutral sentiment
2. Category Classification - Tag with business categories (pricing, features, bugs, etc.)
3. Action Recommendation - Generate follow-up actions based on analysis

FEATURES:
- Sequential workflow pattern (3 executors)
- Detailed span tracking for each executor
- Message passing telemetry with enriched data
- Workflow build and execution spans
- Realistic business logic with visual output
- Configurable telemetry backends (Console, OTLP, Application Insights)

TELEMETRY COLLECTED:
- Overall workflow build & execution spans
- Individual executor processing spans
- Message publishing between executors
- Workflow input and output events
- Business metrics (sentiment scores, categories, priorities)

PREREQUISITES:
- Azure CLI authentication: Run 'az login' (if using Azure AI tracing)
- AZURE_AI_PROJECT_ENDPOINT configured in .env (optional)
- Choose tracing option in .env:
  * ENABLE_CONSOLE_TRACING=true (simplest - outputs to console)
  * ENABLE_AZURE_AI_TRACING=true (requires Application Insights)
  * OTLP_ENDPOINT=http://localhost:4317 (for Jaeger/Zipkin)
  * APPLICATIONINSIGHTS_CONNECTION_STRING=... (direct connection)

WORKSHOP NOTES:
- Run this to see how workflows generate telemetry
- Compare the trace structure with observability_azure_ai_agent.py
- Try different tracing backends by modifying .env
- Observe the parent-child span relationships
- See how messages flow between executors
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowOutputEvent,
    handler,
)
from agent_framework.observability import get_tracer, setup_observability
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from typing_extensions import Never

# Load environment variables from AQ-CODE/.env
load_dotenv(Path(__file__).parent / ".env")


# Executors for customer feedback analysis workflow
class SentimentAnalyzer(Executor):
    """Analyzes sentiment of customer feedback."""

    @handler
    async def analyze_sentiment(self, feedback: str, ctx: WorkflowContext[dict]) -> None:
        """Analyze sentiment and extract key information from customer feedback."""
        print(f"📊 SentimentAnalyzer: Analyzing feedback...")
        print(f"   Input: '{feedback[:60]}...'")
        
        # Simulate sentiment analysis processing
        await asyncio.sleep(0.5)
        
        # Simple sentiment analysis
        positive_words = ["great", "excellent", "love", "amazing", "fantastic", "good", "happy", "helpful", "wonderful", "perfect"]
        negative_words = ["bad", "terrible", "hate", "poor", "disappointing", "slow", "broken", "bug", "issue", "problem"]
        
        feedback_lower = feedback.lower()
        positive_count = sum(1 for word in positive_words if word in feedback_lower)
        negative_count = sum(1 for word in negative_words if word in feedback_lower)
        
        # Consider overall tone - if significantly more positive, it's positive
        if positive_count > negative_count + 1:  # More forgiving threshold
            sentiment = "POSITIVE"
            score = min(0.9, 0.6 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
            score = max(0.2, 0.5 - (negative_count - positive_count) * 0.1)
        else:
            sentiment = "NEUTRAL"
            score = 0.5
        
        result = {
            "original_feedback": feedback,
            "sentiment": sentiment,
            "confidence_score": score,
            "word_count": len(feedback.split()),
            "timestamp": "2025-11-12T12:15:00Z"
        }
        
        print(f"   ✓ Sentiment: {sentiment} (confidence: {score:.1%})")
        print()
        
        # Send the result to the next executor
        await ctx.send_message(result)


class CategoryClassifier(Executor):
    """Classifies feedback into business categories."""

    @handler
    async def classify_category(self, data: dict, ctx: WorkflowContext[dict]) -> None:
        """Classify the feedback into business categories."""
        print(f"🏷️  CategoryClassifier: Categorizing feedback...")
        
        # Simulate classification processing
        await asyncio.sleep(0.3)
        
        feedback = data["original_feedback"].lower()
        
        # Determine categories
        categories = []
        if any(word in feedback for word in ["price", "cost", "expensive", "cheap", "value"]):
            categories.append("PRICING")
        if any(word in feedback for word in ["fast", "slow", "quick", "speed", "performance"]):
            categories.append("PERFORMANCE")
        if any(word in feedback for word in ["support", "help", "service", "team"]):
            categories.append("CUSTOMER_SERVICE")
        if any(word in feedback for word in ["feature", "function", "capability", "option"]):
            categories.append("FEATURES")
        if any(word in feedback for word in ["bug", "error", "broken", "issue", "problem"]):
            categories.append("BUG_REPORT")
        
        if not categories:
            categories.append("GENERAL")
        
        # Determine priority based on sentiment and categories
        priority = "HIGH" if data["sentiment"] == "NEGATIVE" and "BUG_REPORT" in categories else "MEDIUM"
        if data["sentiment"] == "POSITIVE":
            priority = "LOW"
        
        data["categories"] = categories
        data["priority"] = priority
        data["requires_followup"] = priority in ["HIGH", "MEDIUM"]
        
        print(f"   ✓ Categories: {', '.join(categories)}")
        print(f"   ✓ Priority: {priority}")
        print()
        
        # Send to next executor
        await ctx.send_message(data)


class ActionRecommender(Executor):
    """Recommends actions based on the analysis."""

    @handler
    async def recommend_actions(self, data: dict, ctx: WorkflowContext[Never, dict]) -> None:
        """Generate recommended actions based on the analysis."""
        print(f"💡 ActionRecommender: Generating recommendations...")
        
        # Simulate recommendation generation
        await asyncio.sleep(0.4)
        
        actions = []
        
        # Generate actions based on categories and sentiment
        if "BUG_REPORT" in data["categories"]:
            actions.append("Create Jira ticket for engineering team")
        if "CUSTOMER_SERVICE" in data["categories"]:
            actions.append("Route to customer success manager")
        if data["sentiment"] == "NEGATIVE" and data["priority"] == "HIGH":
            actions.append("Send to escalation team within 24 hours")
        if data["sentiment"] == "POSITIVE":
            actions.append("Add to testimonials database")
            actions.append("Send thank you email")
        if "PRICING" in data["categories"] and data["sentiment"] == "NEGATIVE":
            actions.append("Review pricing concerns with product team")
        
        if not actions:
            actions.append("Archive for future analysis")
        
        # Add summary for output
        data["recommended_actions"] = actions
        data["processing_complete"] = True
        
        print(f"   ✓ Recommended Actions:")
        for i, action in enumerate(actions, 1):
            print(f"      {i}. {action}")
        print()
        
        # Final output
        await ctx.yield_output(data)


async def run_sequential_workflow() -> None:
    """Run a customer feedback analysis workflow demonstrating telemetry collection.

    This workflow processes customer feedback through three executors in sequence:
    1. SentimentAnalyzer - Analyzes sentiment and confidence score
    2. CategoryClassifier - Classifies into business categories and assigns priority
    3. ActionRecommender - Generates recommended actions based on analysis
    """
    # Step 1: Create the executors.
    sentiment_analyzer = SentimentAnalyzer(id="sentiment_analyzer")
    category_classifier = CategoryClassifier(id="category_classifier")
    action_recommender = ActionRecommender(id="action_recommender")

    # Step 2: Build the workflow with the defined edges.
    print("Building Customer Feedback Analysis Workflow...")
    print("   Pipeline: Sentiment Analysis → Category Classification → Action Recommendation")
    workflow = (
        WorkflowBuilder()
        .add_edge(sentiment_analyzer, category_classifier)
        .add_edge(category_classifier, action_recommender)
        .set_start_executor(sentiment_analyzer)
        .build()
    )
    print("✓ Workflow built successfully")
    print()

    # Step 3: Run the workflow with sample customer feedback.
    sample_feedback = (
        "I love the new features in this product! The performance is amazing and "
        "the customer support team was incredibly helpful. However, I found a bug "
        "in the export function that needs to be fixed. Overall, great experience!"
    )
    
    print("=" * 80)
    print(f"📝 Customer Feedback Input:")
    print(f"   \"{sample_feedback}\"")
    print("=" * 80)
    print()

    output_event = None
    async for event in workflow.run_stream(sample_feedback):
        if isinstance(event, WorkflowOutputEvent):
            # The WorkflowOutputEvent contains the final result.
            output_event = event

    print("=" * 80)
    if output_event:
        print(f"✅ WORKFLOW COMPLETED - Analysis Summary:")
        print(f"   • Sentiment: {output_event.data['sentiment']} ({output_event.data['confidence_score']:.1%} confidence)")
        print(f"   • Categories: {', '.join(output_event.data['categories'])}")
        print(f"   • Priority: {output_event.data['priority']}")
        print(f"   • Requires Follow-up: {'Yes' if output_event.data['requires_followup'] else 'No'}")
        print(f"   • Actions: {len(output_event.data['recommended_actions'])} recommended")
    print("=" * 80)
    print()


def check_tracing_config():
    """Check and display the current tracing configuration."""
    print("Tracing Configuration:")
    print("-" * 80)
    
    configs = [
        ("ENABLE_CONSOLE_TRACING", "Console output tracing"),
        ("ENABLE_AZURE_AI_TRACING", "Azure AI Application Insights"),
        ("OTLP_ENDPOINT", "OTLP Endpoint (Jaeger/Zipkin)"),
        ("APPLICATIONINSIGHTS_CONNECTION_STRING", "Application Insights Direct"),
        ("ENABLE_DEVUI_TRACING", "DevUI tracing"),
    ]
    
    enabled = False
    for var_name, description in configs:
        value = os.getenv(var_name)
        if value and value.lower() not in ["false", "0", ""]:
            print(f"✓ {description}: Enabled")
            enabled = True
    
    if not enabled:
        print("⚠ No tracing configured in .env file")
        print("  Add one of the following to your .env:")
        print("  - ENABLE_CONSOLE_TRACING=true")
        print("  - ENABLE_AZURE_AI_TRACING=true")
        print("  - OTLP_ENDPOINT=http://localhost:4317")
        print("  - APPLICATIONINSIGHTS_CONNECTION_STRING=...")
    
    print("-" * 80)
    print()


async def main():
    """Run the telemetry sample with a customer feedback analysis workflow."""
    print("=" * 80)
    print("🔍 Workflow Observability Demo - Customer Feedback Analysis")
    print("=" * 80)
    print()
    
    # Check tracing configuration
    check_tracing_config()
    
    # This will enable tracing and create the necessary tracing, logging and metrics providers
    # based on environment variables from the .env file
    setup_observability()
    print("✓ Observability setup completed")
    print()

    with get_tracer().start_as_current_span("Customer Feedback Analysis Workflow", kind=SpanKind.CLIENT) as current_span:
        trace_id = format_trace_id(current_span.get_span_context().trace_id)
        print(f"🔗 Trace ID: {trace_id}")
        print(f"   Use this ID to find the complete execution trace in Azure Portal")
        print()

        # Run the customer feedback analysis workflow
        await run_sequential_workflow()
    
    print()
    print("=" * 80)
    print("✅ Demo completed successfully!")
    print("=" * 80)
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        print(f"📊 View telemetry: Azure Portal > Application Insights > Transaction Search")
        print(f"🔍 Filter by Trace ID: {trace_id}")
        print()
        print(f"   ⏱️  NOTE: Traces may take 2-5 minutes to appear in Application Insights")
        print(f"   💡 TIP: Try 'Oldest first' sorting and wait a moment if no data shows initially")
        print()
        print("   You'll see:")
        print("   • 3 executor spans (SentimentAnalyzer → CategoryClassifier → ActionRecommender)")
        print("   • Message passing events between executors")
        print("   • Custom properties (sentiment, categories, priority)")
        print("   • Performance metrics for each stage")
        print()
        print("   Alternative views:")
        print("   • Live Metrics: Real-time telemetry stream")
        print("   • Application Map: Visual workflow topology")
        print("   • Performance: Analyze operation durations")
    if os.getenv("OTLP_ENDPOINT"):
        print(f"📊 Check your OTLP endpoint: {os.getenv('OTLP_ENDPOINT')}")
    if os.getenv("ENABLE_CONSOLE_TRACING"):
        print(f"📝 Console tracing enabled - check terminal output above for spans")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

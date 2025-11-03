# LLMOps Best Practices for Microsoft Agent Framework (MAF)

**Version:** 1.0  
**Last Updated:** November 3, 2025  
**Author:** Technical Documentation Team

---

## Table of Contents

1. [Introduction](#introduction)
2. [LLMOps Pillars for MAF](#llmops-pillars-for-maf)
3. [Development Phase](#development-phase)
4. [Testing & Evaluation](#testing--evaluation)
5. [Deployment & Operations](#deployment--operations)
6. [Monitoring & Observability](#monitoring--observability)
7. [Governance & Compliance](#governance--compliance)
8. [Cost Management](#cost-management)
9. [Implementation Examples](#implementation-examples)
10. [Recommended Tools & Services](#recommended-tools--services)

---

## Introduction

### What is LLMOps?

LLMOps (Large Language Model Operations) is the discipline of operationalizing LLM-based applications through the entire lifecycle—from development to production. For Microsoft Agent Framework (MAF) projects, LLMOps ensures your AI agents are:

- **Reliable**: Consistent performance in production
- **Monitored**: Full visibility into agent behavior
- **Governed**: Compliant with policies and regulations
- **Optimized**: Cost-efficient and performant
- **Maintainable**: Easy to update and improve

### MAF + LLMOps: Why They're Complementary

| **MAF Role** | **LLMOps Role** |
|--------------|-----------------|
| Build agents with code | Operationalize agents at scale |
| Define workflows and tools | Monitor and improve workflows |
| Create agent interactions | Track interaction quality |
| Integrate models | Manage model versions and costs |

---

## LLMOps Pillars for MAF

### 1. **Prompt Engineering & Management** 📝
- Version control for agent instructions
- A/B testing different prompts
- Prompt template libraries

### 2. **Model Management** 🤖
- Model selection and versioning
- Fallback strategies
- Performance benchmarking

### 3. **Evaluation & Testing** ✅
- Automated quality assessment
- Regression testing
- Multi-agent workflow validation

### 4. **Deployment** 🚀
- CI/CD pipelines
- Environment management
- Gradual rollouts

### 5. **Monitoring & Observability** 📊
- Real-time tracing
- Performance metrics
- Cost tracking

### 6. **Governance & Compliance** 🔒
- Content filtering
- Data privacy
- Audit trails

---

## Development Phase

### 1. Project Structure

**Best Practice**: Organize MAF projects for maintainability and version control.

```
project-root/
├── agents/
│   ├── config/
│   │   ├── prompts.yaml          # Centralized prompt management
│   │   ├── model_config.yaml     # Model configurations
│   │   └── tools_config.yaml     # Tool definitions
│   ├── market_analyst.py         # Individual agent definitions
│   ├── risk_analyst.py
│   └── workflow.py               # Multi-agent orchestration
├── evaluation/
│   ├── test_cases.json           # Test scenarios
│   ├── eval_metrics.py           # Custom evaluation metrics
│   └── run_evaluation.py         # Evaluation runner
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── azure-deploy.yaml
├── monitoring/
│   ├── dashboards/               # App Insights dashboards
│   └── alerts.yaml               # Alert configurations
├── .env.template                 # Environment variable template
├── requirements.txt
└── README.md
```

### 2. Prompt Management

**Best Practice**: Externalize prompts for version control and easy updates.

**❌ Bad Practice:**
```python
# Hard-coded prompts are difficult to version and update
agent = client.create_agent(
    instructions="You're a market analyst. Analyze stocks...",
    name="market_analyst"
)
```

**✅ Good Practice:**

**prompts.yaml:**
```yaml
agents:
  market_analyst:
    version: "1.2.0"
    system_prompt: |
      You're a senior market analyst specializing in technology stock valuations.
      
      Your responsibilities:
      - Analyze current stock prices and P/E ratios
      - Compare valuations to historical averages
      - Identify overvaluation warning signs
      
      Guidelines:
      - Always cite sources with dates
      - Provide specific numbers and metrics
      - Use web search for current data
    
    model: "gpt-4.1"
    temperature: 0.7
    max_tokens: 2000
```

**Python code:**
```python
import yaml
from pathlib import Path

def load_agent_config(agent_name: str) -> dict:
    """Load agent configuration from YAML."""
    config_path = Path(__file__).parent / "config" / "prompts.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['agents'][agent_name]

# Use in agent creation
config = load_agent_config("market_analyst")
agent = client.create_agent(
    instructions=config['system_prompt'],
    name="market_analyst",
    model=config['model']
)
```

**Benefits:**
- ✅ Version control with Git
- ✅ Easy A/B testing (swap YAML files)
- ✅ Non-developers can update prompts
- ✅ Audit trail of prompt changes

### 3. Environment-Based Configuration

**Best Practice**: Use environment variables for all configurable parameters.

**.env.template:**
```bash
# Model Configuration
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1
AZURE_AI_MODEL_FALLBACK=gpt-4o-mini

# Feature Flags
ENABLE_WEB_SEARCH=true
ENABLE_CONTENT_SAFETY=true
MAX_AGENT_RETRIES=3

# Monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=<your-connection-string>
ENABLE_TRACING=true
LOG_LEVEL=INFO

# Cost Controls
MAX_TOKENS_PER_REQUEST=4000
DAILY_TOKEN_BUDGET=1000000
```

**Python implementation:**
```python
import os
from typing import Optional

class AgentConfig:
    """Centralized configuration management."""
    
    def __init__(self):
        self.model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1")
        self.fallback_model = os.getenv("AZURE_AI_MODEL_FALLBACK")
        self.enable_web_search = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
        self.max_retries = int(os.getenv("MAX_AGENT_RETRIES", "3"))
        self.enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() == "true"
        
    def get_model_with_fallback(self) -> str:
        """Get primary model with fallback logic."""
        try:
            # Try primary model
            return self.model
        except Exception as e:
            if self.fallback_model:
                print(f"Falling back to {self.fallback_model}: {e}")
                return self.fallback_model
            raise

config = AgentConfig()
```

### 4. Structured Logging

**Best Practice**: Use structured logging for better observability.

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured logger for MAF agents."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
    def log_agent_interaction(self, agent_name: str, event: str, 
                             metadata: dict = None):
        """Log agent interactions with structured data."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "event": event,
            "metadata": metadata or {}
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_llm_call(self, model: str, prompt_tokens: int, 
                     completion_tokens: int, latency_ms: float):
        """Log LLM API calls for cost tracking."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "llm_call",
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_ms": latency_ms,
            "estimated_cost_usd": self._calculate_cost(model, prompt_tokens, completion_tokens)
        }
        self.logger.info(json.dumps(log_entry))
    
    def _calculate_cost(self, model: str, prompt_tokens: int, 
                       completion_tokens: int) -> float:
        """Calculate estimated cost based on model pricing."""
        pricing = {
            "gpt-4.1": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
            "gpt-4o": {"prompt": 0.005 / 1000, "completion": 0.015 / 1000},
            "gpt-4o-mini": {"prompt": 0.00015 / 1000, "completion": 0.0006 / 1000}
        }
        
        if model not in pricing:
            return 0.0
        
        cost = (prompt_tokens * pricing[model]["prompt"] + 
                completion_tokens * pricing[model]["completion"])
        return round(cost, 6)

# Usage
logger = StructuredLogger("market_analyst")
logger.log_agent_interaction(
    agent_name="market_analyst",
    event="analysis_started",
    metadata={"query": "Analyze NVIDIA valuation"}
)
```

---

## Testing & Evaluation

### 1. Unit Testing for Agents

**Best Practice**: Test individual agent components.

```python
import pytest
from unittest.mock import Mock, AsyncMock
from agents.market_analyst import MarketAnalyst

@pytest.mark.asyncio
async def test_market_analyst_valuation():
    """Test market analyst valuation logic."""
    
    # Mock the LLM client
    mock_client = Mock()
    mock_agent = AsyncMock()
    mock_agent.run.return_value = "NVIDIA P/E ratio is 45.2, above industry average of 28.5"
    mock_client.create_agent.return_value = mock_agent
    
    # Create analyst with mocked client
    analyst = MarketAnalyst(client=mock_client)
    
    # Test analysis
    result = await analyst.analyze("What is NVIDIA's P/E ratio?")
    
    # Assertions
    assert "45.2" in result
    assert "P/E ratio" in result
    mock_agent.run.assert_called_once()

@pytest.mark.asyncio
async def test_market_analyst_with_web_search():
    """Test that web search tool is properly configured."""
    
    mock_client = Mock()
    analyst = MarketAnalyst(client=mock_client, enable_web_search=True)
    
    # Verify web search tool is added
    assert analyst.tools is not None
    assert any("search" in str(tool).lower() for tool in analyst.tools)
```

### 2. Integration Testing for Workflows

**Best Practice**: Test multi-agent workflows end-to-end.

```python
import pytest
from workflows.stock_bubble_research import create_ai_stock_research_workflow

@pytest.mark.asyncio
@pytest.mark.integration
async def test_stock_bubble_workflow():
    """Integration test for stock bubble research workflow."""
    
    # Create workflow
    workflow = await create_ai_stock_research_workflow()
    
    # Test input
    test_query = "Is NVIDIA overvalued based on P/E ratio?"
    
    # Run workflow
    result = await workflow.run(query=test_query)
    
    # Assertions
    assert result is not None
    assert len(result) > 100  # Substantial response
    assert "NVIDIA" in result or "NVDA" in result
    assert any(term in result.lower() for term in ["p/e", "valuation", "overvalued"])
    
    # Verify all agents participated
    assert "Market Analyst" in result or "MARKET" in result
    assert "Risk Analyst" in result or "RISK" in result

@pytest.mark.asyncio
async def test_workflow_error_handling():
    """Test workflow handles errors gracefully."""
    
    workflow = await create_ai_stock_research_workflow()
    
    # Test with invalid input
    result = await workflow.run(query="")
    
    # Should handle gracefully
    assert result is not None
    assert "error" in result.lower() or "invalid" in result.lower()
```

### 3. Evaluation Metrics

**Best Practice**: Define quantitative metrics for agent quality.

**evaluation/eval_metrics.py:**
```python
from typing import List, Dict
import re
from datetime import datetime

class AgentEvaluator:
    """Evaluation metrics for MAF agents."""
    
    def evaluate_response(self, response: str, expected_topics: List[str]) -> Dict:
        """Evaluate agent response quality."""
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "length": len(response),
            "word_count": len(response.split()),
            "topic_coverage": self._check_topic_coverage(response, expected_topics),
            "has_citations": self._check_citations(response),
            "has_numbers": self._check_numbers(response),
            "sentiment_neutral": self._check_sentiment(response),
            "overall_score": 0.0
        }
        
        # Calculate overall score
        metrics["overall_score"] = (
            metrics["topic_coverage"] * 0.4 +
            (1.0 if metrics["has_citations"] else 0.0) * 0.3 +
            (1.0 if metrics["has_numbers"] else 0.0) * 0.2 +
            (1.0 if metrics["sentiment_neutral"] else 0.0) * 0.1
        )
        
        return metrics
    
    def _check_topic_coverage(self, response: str, topics: List[str]) -> float:
        """Check what percentage of expected topics are covered."""
        response_lower = response.lower()
        covered = sum(1 for topic in topics if topic.lower() in response_lower)
        return covered / len(topics) if topics else 0.0
    
    def _check_citations(self, response: str) -> bool:
        """Check if response includes citations or sources."""
        citation_patterns = [
            r'\d{4}',  # Years (e.g., 2025)
            r'according to',
            r'source:',
            r'https?://',
            r'reported by'
        ]
        return any(re.search(pattern, response, re.IGNORECASE) 
                  for pattern in citation_patterns)
    
    def _check_numbers(self, response: str) -> bool:
        """Check if response includes quantitative data."""
        # Look for numbers, percentages, currencies
        return bool(re.search(r'\d+\.?\d*\s*%?|\$\d+', response))
    
    def _check_sentiment(self, response: str) -> bool:
        """Check if response maintains neutral, analytical tone."""
        # Simple heuristic: avoid overly positive/negative language
        emotional_words = ['amazing', 'terrible', 'awful', 'fantastic', 
                          'horrible', 'love', 'hate']
        response_lower = response.lower()
        return not any(word in response_lower for word in emotional_words)

# Usage
evaluator = AgentEvaluator()
result = evaluator.evaluate_response(
    response="NVIDIA's P/E ratio is 45.2 as of Q3 2025, significantly above...",
    expected_topics=["P/E ratio", "NVIDIA", "valuation"]
)
print(f"Overall Score: {result['overall_score']:.2f}")
```

### 4. Test Dataset Management

**Best Practice**: Maintain versioned test datasets.

**evaluation/test_cases.json:**
```json
{
  "version": "1.0",
  "test_suite": "stock_bubble_research",
  "test_cases": [
    {
      "id": "test_001",
      "category": "valuation_analysis",
      "input": {
        "query": "Is NVIDIA overvalued based on current P/E ratios?"
      },
      "expected_topics": ["P/E ratio", "NVIDIA", "valuation", "comparison"],
      "expected_behavior": "Should provide current P/E data and compare to industry averages",
      "pass_criteria": {
        "min_length": 200,
        "must_include_numbers": true,
        "must_include_citations": true,
        "topic_coverage_min": 0.75
      }
    },
    {
      "id": "test_002",
      "category": "historical_comparison",
      "input": {
        "query": "Compare current AI stock valuations to the dot-com bubble"
      },
      "expected_topics": ["dot-com", "bubble", "comparison", "historical"],
      "expected_behavior": "Should reference specific metrics from 1999-2000",
      "pass_criteria": {
        "min_length": 300,
        "must_include_numbers": true,
        "must_mention_year": true,
        "topic_coverage_min": 0.8
      }
    }
  ]
}
```

**evaluation/run_evaluation.py:**
```python
import json
import asyncio
from pathlib import Path
from eval_metrics import AgentEvaluator
from workflows.stock_bubble_research import create_ai_stock_research_workflow

async def run_evaluation_suite():
    """Run evaluation test suite."""
    
    # Load test cases
    test_file = Path(__file__).parent / "test_cases.json"
    with open(test_file, 'r') as f:
        test_data = json.load(f)
    
    # Create workflow
    workflow = await create_ai_stock_research_workflow()
    evaluator = AgentEvaluator()
    
    results = []
    
    for test_case in test_data['test_cases']:
        print(f"\nRunning test: {test_case['id']} - {test_case['category']}")
        
        # Run workflow
        response = await workflow.run(query=test_case['input']['query'])
        
        # Evaluate response
        metrics = evaluator.evaluate_response(
            response=response,
            expected_topics=test_case['expected_topics']
        )
        
        # Check pass criteria
        criteria = test_case['pass_criteria']
        passed = (
            metrics['length'] >= criteria.get('min_length', 0) and
            (not criteria.get('must_include_numbers', False) or metrics['has_numbers']) and
            (not criteria.get('must_include_citations', False) or metrics['has_citations']) and
            metrics['topic_coverage'] >= criteria.get('topic_coverage_min', 0.0)
        )
        
        result = {
            "test_id": test_case['id'],
            "category": test_case['category'],
            "passed": passed,
            "metrics": metrics
        }
        results.append(result)
        
        print(f"  Result: {'✅ PASSED' if passed else '❌ FAILED'}")
        print(f"  Score: {metrics['overall_score']:.2f}")
    
    # Save results
    output_file = Path(__file__).parent / f"eval_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    passed_count = sum(1 for r in results if r['passed'])
    print(f"\n{'='*60}")
    print(f"Evaluation Complete: {passed_count}/{len(results)} tests passed")
    print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(run_evaluation_suite())
```

---

## Deployment & Operations

### 1. CI/CD Pipeline

**Best Practice**: Automate testing and deployment.

**.github/workflows/maf-agent-deploy.yml:**
```yaml
name: MAF Agent Deployment

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

env:
  AZURE_CONTAINER_REGISTRY: myregistry.azurecr.io
  IMAGE_NAME: maf-stock-bubble-agent

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run unit tests
        run: pytest tests/unit --verbose
      
      - name: Run integration tests
        env:
          AZURE_AI_MODEL_DEPLOYMENT_NAME: gpt-4o-mini
          ENABLE_WEB_SEARCH: false  # Mock in CI
        run: pytest tests/integration --verbose
      
      - name: Run evaluation suite
        run: python evaluation/run_evaluation.py
  
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Container Registry Login
        uses: azure/docker-login@v1
        with:
          login-server: ${{ env.AZURE_CONTAINER_REGISTRY }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      
      - name: Build and push Docker image
        run: |
          docker build -t ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .
          docker tag ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
                     ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          docker push ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          docker push ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.IMAGE_NAME }}:latest
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to Azure Container Apps
        run: |
          az containerapp update \
            --name maf-stock-bubble-agent \
            --resource-group maf-agents-rg \
            --image ${{ env.AZURE_CONTAINER_REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
      
      - name: Verify deployment
        run: |
          az containerapp show \
            --name maf-stock-bubble-agent \
            --resource-group maf-agents-rg \
            --query "properties.latestRevisionName" -o tsv
```

### 2. Blue-Green Deployment

**Best Practice**: Zero-downtime deployments with gradual rollout.

**deployment/blue-green-deploy.sh:**
```bash
#!/bin/bash
set -e

# Configuration
RESOURCE_GROUP="maf-agents-rg"
CONTAINER_APP="maf-stock-bubble-agent"
NEW_IMAGE="$1"

echo "Starting blue-green deployment..."
echo "New image: $NEW_IMAGE"

# Create new revision with traffic weight 0
echo "Creating new revision..."
az containerapp update \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --image $NEW_IMAGE \
  --revision-suffix $(date +%Y%m%d-%H%M%S)

# Get latest two revisions
REVISIONS=$(az containerapp revision list \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --query "[].name" -o tsv)

NEW_REVISION=$(echo "$REVISIONS" | head -n 1)
OLD_REVISION=$(echo "$REVISIONS" | sed -n 2p)

echo "New revision: $NEW_REVISION"
echo "Old revision: $OLD_REVISION"

# Gradual traffic shift: 10% -> 50% -> 100%
echo "Shifting 10% traffic to new revision..."
az containerapp ingress traffic set \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --revision-weight $NEW_REVISION=10 $OLD_REVISION=90

sleep 60  # Monitor for 1 minute

echo "Shifting 50% traffic to new revision..."
az containerapp ingress traffic set \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --revision-weight $NEW_REVISION=50 $OLD_REVISION=50

sleep 120  # Monitor for 2 minutes

echo "Shifting 100% traffic to new revision..."
az containerapp ingress traffic set \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --revision-weight $NEW_REVISION=100

echo "Deployment complete! Old revision kept for rollback."
echo "To rollback, run: ./rollback.sh $OLD_REVISION"
```

### 3. Health Checks

**Best Practice**: Implement health endpoints for monitoring.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
from typing import Optional

app = FastAPI()

class HealthStatus(BaseModel):
    status: str
    version: str
    model: str
    uptime_seconds: float
    checks: dict

startup_time = time.time()

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness_check():
    """Readiness check - is the service ready to accept requests?"""
    
    checks = {
        "azure_ai_client": False,
        "model_available": False,
        "web_search_available": False
    }
    
    try:
        # Check Azure AI client connection
        # (implement actual check)
        checks["azure_ai_client"] = True
        
        # Check if model is available
        # (implement actual check)
        checks["model_available"] = True
        
        # Check if web search is configured
        checks["web_search_available"] = bool(os.getenv("BING_CONNECTION_ID"))
        
        all_ready = all(checks.values())
        
        status = HealthStatus(
            status="ready" if all_ready else "not_ready",
            version=os.getenv("APP_VERSION", "unknown"),
            model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "unknown"),
            uptime_seconds=time.time() - startup_time,
            checks=checks
        )
        
        if not all_ready:
            raise HTTPException(status_code=503, detail=status.dict())
        
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail={"status": "error", "error": str(e)}
        )

@app.get("/health/live")
async def liveness_check():
    """Liveness check - is the service alive?"""
    return {"status": "alive", "uptime_seconds": time.time() - startup_time}
```

---

## Monitoring & Observability

### 1. Application Insights Integration

**Best Practice**: Comprehensive tracing and metrics.

```python
from agent_framework.observability import setup_observability
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace, metrics
import os

class MAFObservability:
    """Observability setup for MAF agents."""
    
    def __init__(self):
        self.connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        self.enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() == "true"
        
        if self.enable_tracing and self.connection_string:
            # Configure Azure Monitor
            configure_azure_monitor(connection_string=self.connection_string)
            
            # Setup MAF observability
            setup_observability(
                enable_sensitive_data=True,
                applicationinsights_connection_string=self.connection_string
            )
            
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
    
    def track_agent_call(self, agent_name: str, duration_ms: float, 
                        tokens: int, success: bool):
        """Track agent call metrics."""
        
        attributes = {
            "agent.name": agent_name,
            "success": success
        }
        
        self.agent_calls_counter.add(1, attributes)
        self.agent_latency_histogram.record(duration_ms, attributes)
        self.token_usage_counter.add(tokens, attributes)
    
    def create_span(self, name: str, attributes: dict = None):
        """Create a custom trace span."""
        return self.tracer.start_as_current_span(
            name=name,
            attributes=attributes or {}
        )

# Usage in workflow
observability = MAFObservability()

async def run_agent_with_tracking(agent, query: str):
    """Run agent with observability tracking."""
    
    start_time = time.time()
    success = False
    tokens = 0
    
    with observability.create_span(
        name=f"agent.{agent.name}.run",
        attributes={"query": query}
    ):
        try:
            result = await agent.run(query)
            success = True
            tokens = estimate_tokens(result)  # Implement token counting
            return result
        except Exception as e:
            observability.tracer.get_current_span().set_status(
                trace.Status(trace.StatusCode.ERROR, str(e))
            )
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            observability.track_agent_call(
                agent_name=agent.name,
                duration_ms=duration_ms,
                tokens=tokens,
                success=success
            )
```

### 2. Custom Dashboards

**Best Practice**: Create Application Insights dashboards for MAF metrics.

**monitoring/dashboards/maf_agent_dashboard.json:**
```json
{
  "name": "MAF Agent Performance Dashboard",
  "tiles": [
    {
      "title": "Agent Calls per Minute",
      "query": "customMetrics | where name == 'maf.agent.calls' | summarize sum(value) by bin(timestamp, 1m), tostring(customDimensions['agent.name'])"
    },
    {
      "title": "Average Agent Latency",
      "query": "customMetrics | where name == 'maf.agent.latency' | summarize avg(value) by tostring(customDimensions['agent.name'])"
    },
    {
      "title": "Token Usage by Agent",
      "query": "customMetrics | where name == 'maf.tokens.used' | summarize sum(value) by tostring(customDimensions['agent.name'])"
    },
    {
      "title": "Error Rate",
      "query": "customMetrics | where name == 'maf.agent.calls' | summarize ErrorRate = todouble(countif(customDimensions['success'] == 'false')) / count() * 100 by bin(timestamp, 5m)"
    },
    {
      "title": "Cost per Hour (Estimated)",
      "query": "customMetrics | where name == 'maf.tokens.used' | extend cost = value * 0.00003 | summarize sum(cost) by bin(timestamp, 1h)"
    }
  ]
}
```

### 3. Alerting

**Best Practice**: Set up proactive alerts for issues.

**monitoring/alerts.yaml:**
```yaml
alerts:
  - name: High Error Rate
    condition: |
      customMetrics
      | where name == 'maf.agent.calls'
      | summarize ErrorRate = todouble(countif(customDimensions['success'] == 'false')) / count() * 100 by bin(timestamp, 5m)
      | where ErrorRate > 10
    severity: 2
    frequency: 5m
    action_group: maf-alerts
  
  - name: High Token Usage
    condition: |
      customMetrics
      | where name == 'maf.tokens.used'
      | summarize TotalTokens = sum(value) by bin(timestamp, 1h)
      | where TotalTokens > 500000
    severity: 3
    frequency: 1h
    action_group: maf-cost-alerts
  
  - name: Slow Agent Response
    condition: |
      customMetrics
      | where name == 'maf.agent.latency'
      | summarize p95 = percentile(value, 95) by bin(timestamp, 5m)
      | where p95 > 10000
    severity: 3
    frequency: 5m
    action_group: maf-performance-alerts
```

---

## Governance & Compliance

### 1. Content Safety Integration

**Best Practice**: Implement content filtering for inputs and outputs.

```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from typing import Tuple, Optional

class ContentSafetyGuard:
    """Content safety guard for MAF agents."""
    
    def __init__(self):
        endpoint = os.getenv("CONTENT_SAFETY_ENDPOINT")
        key = os.getenv("CONTENT_SAFETY_KEY")
        
        if endpoint and key:
            self.client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
            self.enabled = True
        else:
            self.enabled = False
            print("Warning: Content Safety not configured")
    
    async def check_content(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check content for safety violations.
        
        Returns:
            (is_safe, reason) tuple
        """
        if not self.enabled:
            return True, None
        
        try:
            response = self.client.analyze_text(text=text)
            
            # Check severity thresholds
            thresholds = {
                "hate": 4,
                "sexual": 4,
                "violence": 4,
                "self_harm": 4
            }
            
            for category, result in response.categories_analysis.items():
                if result.severity >= thresholds.get(category, 4):
                    return False, f"Content blocked: {category} (severity: {result.severity})"
            
            return True, None
            
        except Exception as e:
            print(f"Content safety check failed: {e}")
            return True, None  # Fail open

# Usage in agent workflow
safety_guard = ContentSafetyGuard()

async def safe_agent_run(agent, query: str):
    """Run agent with content safety checks."""
    
    # Check input
    is_safe, reason = await safety_guard.check_content(query)
    if not is_safe:
        return f"Request blocked: {reason}"
    
    # Run agent
    result = await agent.run(query)
    
    # Check output
    is_safe, reason = await safety_guard.check_content(result)
    if not is_safe:
        return "Response blocked due to content policy violation"
    
    return result
```

### 2. Audit Logging

**Best Practice**: Maintain detailed audit trails.

```python
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient

class AuditLogger:
    """Audit logger for MAF agent interactions."""
    
    def __init__(self):
        self.connection_string = os.getenv("AUDIT_STORAGE_CONNECTION_STRING")
        self.container_name = "maf-audit-logs"
        
        if self.connection_string:
            self.blob_service = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self.enabled = True
        else:
            self.enabled = False
    
    def log_interaction(self, user_id: str, agent_name: str, 
                       query: str, response: str, metadata: dict = None):
        """Log agent interaction for audit purposes."""
        
        if not self.enabled:
            return
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "agent_name": agent_name,
            "query": query,
            "response": response,
            "metadata": metadata or {},
            "compliance_flags": {
                "content_filtered": False,
                "pii_detected": False
            }
        }
        
        # Store in blob storage
        blob_name = f"audit-{datetime.utcnow().strftime('%Y/%m/%d')}/{user_id}-{datetime.utcnow().timestamp()}.json"
        blob_client = self.blob_service.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )
        
        blob_client.upload_blob(
            json.dumps(audit_entry, indent=2),
            overwrite=True
        )
```

---

## Cost Management

### 1. Token Budget Enforcement

**Best Practice**: Implement token usage limits.

```python
from datetime import datetime, timedelta
from collections import defaultdict
import threading

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
        
        Returns:
            (allowed, message) tuple
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
        """Record token usage."""
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
                "requests_count": len(self.usage)
            }

# Usage
budget_manager = TokenBudgetManager()

async def run_agent_with_budget(agent, query: str):
    """Run agent with budget enforcement."""
    
    # Estimate tokens (rough approximation)
    estimated_tokens = len(query.split()) * 1.3 + 500
    
    # Check budget
    allowed, message = budget_manager.check_budget(int(estimated_tokens))
    if not allowed:
        raise Exception(f"Budget limit reached: {message}")
    
    # Run agent
    request_id = str(uuid.uuid4())
    result = await agent.run(query)
    
    # Record actual usage
    actual_tokens = estimate_tokens(result)
    budget_manager.record_usage(request_id, actual_tokens)
    
    return result
```

### 2. Cost Tracking Dashboard

**Best Practice**: Track and visualize costs.

```python
import pandas as pd
from datetime import datetime, timedelta

class CostTracker:
    """Track and analyze LLM costs."""
    
    def __init__(self):
        self.pricing = {
            "gpt-4.1": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
            "gpt-4o": {"prompt": 0.005 / 1000, "completion": 0.015 / 1000},
            "gpt-4o-mini": {"prompt": 0.00015 / 1000, "completion": 0.0006 / 1000}
        }
        self.costs = []
    
    def record_cost(self, model: str, prompt_tokens: int, 
                   completion_tokens: int, agent_name: str):
        """Record cost for an LLM call."""
        
        if model not in self.pricing:
            return
        
        cost = (
            prompt_tokens * self.pricing[model]["prompt"] +
            completion_tokens * self.pricing[model]["completion"]
        )
        
        self.costs.append({
            "timestamp": datetime.utcnow(),
            "model": model,
            "agent": agent_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": cost
        })
    
    def get_daily_report(self) -> pd.DataFrame:
        """Generate daily cost report."""
        
        df = pd.DataFrame(self.costs)
        
        if df.empty:
            return df
        
        # Filter last 24 hours
        cutoff = datetime.utcnow() - timedelta(days=1)
        df = df[df['timestamp'] >= cutoff]
        
        # Aggregate by agent
        report = df.groupby('agent').agg({
            'total_tokens': 'sum',
            'cost_usd': 'sum',
            'timestamp': 'count'
        }).rename(columns={'timestamp': 'requests'})
        
        report['avg_cost_per_request'] = report['cost_usd'] / report['requests']
        
        return report.round(4)
    
    def get_monthly_projection(self) -> float:
        """Project monthly costs based on recent usage."""
        
        df = pd.DataFrame(self.costs)
        
        if df.empty:
            return 0.0
        
        # Get last 7 days
        cutoff = datetime.utcnow() - timedelta(days=7)
        recent = df[df['timestamp'] >= cutoff]
        
        if recent.empty:
            return 0.0
        
        # Calculate daily average and project to 30 days
        daily_avg = recent['cost_usd'].sum() / 7
        monthly_projection = daily_avg * 30
        
        return round(monthly_projection, 2)
```

---

## Implementation Examples

### Complete Example: Production-Ready MAF Agent

**agents/production_agent.py:**
```python
"""
Production-ready MAF agent with full LLMOps capabilities.
"""

import asyncio
import os
import time
import uuid
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv
from agent_framework import ChatMessage, Role
from agent_framework.azure import AzureAIAgentClient
from agent_framework.observability import setup_observability
from azure.identity.aio import DefaultAzureCredential

# Import LLMOps components
from llmops.observability import MAFObservability
from llmops.content_safety import ContentSafetyGuard
from llmops.audit_logger import AuditLogger
from llmops.budget_manager import TokenBudgetManager
from llmops.cost_tracker import CostTracker
from llmops.evaluator import AgentEvaluator

# Load configuration
load_dotenv()

class ProductionAgent:
    """Production-ready agent with full LLMOps integration."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
        # Load agent configuration
        self.config = self._load_config(agent_name)
        
        # Initialize LLMOps components
        self.observability = MAFObservability()
        self.safety_guard = ContentSafetyGuard()
        self.audit_logger = AuditLogger()
        self.budget_manager = TokenBudgetManager()
        self.cost_tracker = CostTracker()
        self.evaluator = AgentEvaluator()
        
        # Agent client (initialized lazily)
        self._client = None
        self._agent = None
    
    def _load_config(self, agent_name: str) -> dict:
        """Load agent configuration from YAML."""
        config_file = Path(__file__).parent / "config" / "prompts.yaml"
        with open(config_file, 'r') as f:
            all_configs = yaml.safe_load(f)
        return all_configs['agents'][agent_name]
    
    async def initialize(self):
        """Initialize Azure AI client and agent."""
        if self._agent is not None:
            return
        
        credential = DefaultAzureCredential()
        self._client = AzureAIAgentClient(
            async_credential=credential,
            model=self.config.get('model', os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"))
        )
        
        # Create agent with tools if specified
        tools = self._load_tools() if self.config.get('enable_tools') else None
        
        self._agent = self._client.create_agent(
            instructions=self.config['system_prompt'],
            name=self.agent_name,
            tools=tools
        )
    
    def _load_tools(self):
        """Load tools based on configuration."""
        from agent_framework import HostedWebSearchTool
        
        tools = []
        
        if self.config.get('enable_web_search', False):
            tools.append(HostedWebSearchTool(
                name="Web Search",
                description="Search the web for current information"
            ))
        
        return tools if tools else None
    
    async def run(self, query: str, user_id: str = "anonymous", 
                 metadata: Optional[Dict] = None) -> Dict:
        """
        Run agent with full LLMOps pipeline.
        
        Returns:
            Dictionary with response and metadata
        """
        
        # Initialize if needed
        await self.initialize()
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.agent_name,
            "success": False,
            "response": None,
            "error": None,
            "metrics": {}
        }
        
        try:
            # Step 1: Content Safety - Input
            with self.observability.create_span("content_safety.input"):
                is_safe, reason = await self.safety_guard.check_content(query)
                if not is_safe:
                    result["error"] = f"Content blocked: {reason}"
                    return result
            
            # Step 2: Budget Check
            with self.observability.create_span("budget.check"):
                estimated_tokens = len(query.split()) * 1.3 + 500
                allowed, message = self.budget_manager.check_budget(int(estimated_tokens))
                if not allowed:
                    result["error"] = f"Budget limit: {message}"
                    return result
            
            # Step 3: Run Agent
            with self.observability.create_span(
                f"agent.{self.agent_name}.execute",
                attributes={"query_length": len(query)}
            ):
                response = await self._agent.run(query)
                response_text = response.messages[-1].text if response.messages else ""
            
            # Step 4: Content Safety - Output
            with self.observability.create_span("content_safety.output"):
                is_safe, reason = await self.safety_guard.check_content(response_text)
                if not is_safe:
                    result["error"] = "Response blocked by content filter"
                    return result
            
            # Step 5: Evaluation
            with self.observability.create_span("evaluation"):
                eval_metrics = self.evaluator.evaluate_response(
                    response=response_text,
                    expected_topics=metadata.get('expected_topics', []) if metadata else []
                )
            
            # Step 6: Track Costs
            prompt_tokens = len(query.split()) * 1.3  # Rough estimate
            completion_tokens = len(response_text.split()) * 1.3
            self.cost_tracker.record_cost(
                model=self.config['model'],
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                agent_name=self.agent_name
            )
            self.budget_manager.record_usage(
                request_id,
                int(prompt_tokens + completion_tokens)
            )
            
            # Step 7: Audit Logging
            self.audit_logger.log_interaction(
                user_id=user_id,
                agent_name=self.agent_name,
                query=query,
                response=response_text,
                metadata={
                    "request_id": request_id,
                    "eval_score": eval_metrics['overall_score'],
                    **(metadata or {})
                }
            )
            
            # Success
            duration_ms = (time.time() - start_time) * 1000
            result.update({
                "success": True,
                "response": response_text,
                "metrics": {
                    "duration_ms": duration_ms,
                    "prompt_tokens": int(prompt_tokens),
                    "completion_tokens": int(completion_tokens),
                    "total_tokens": int(prompt_tokens + completion_tokens),
                    "evaluation": eval_metrics
                }
            })
            
            # Track observability metrics
            self.observability.track_agent_call(
                agent_name=self.agent_name,
                duration_ms=duration_ms,
                tokens=int(prompt_tokens + completion_tokens),
                success=True
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result["error"] = str(e)
            
            # Track failure
            self.observability.track_agent_call(
                agent_name=self.agent_name,
                duration_ms=duration_ms,
                tokens=0,
                success=False
            )
        
        return result

# Usage example
async def main():
    """Example usage of production agent."""
    
    agent = ProductionAgent("market_analyst")
    
    result = await agent.run(
        query="What is NVIDIA's current P/E ratio?",
        user_id="demo_user",
        metadata={
            "expected_topics": ["P/E ratio", "NVIDIA", "valuation"]
        }
    )
    
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    print(f"Metrics: {result['metrics']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Recommended Tools & Services

### Azure Services for LLMOps

| **Service** | **Purpose** | **MAF Integration** |
|-------------|-------------|---------------------|
| **Azure AI Foundry** | Model catalog, evaluation, prompt flow | Native integration |
| **Application Insights** | Tracing, metrics, logging | Built-in via observability module |
| **Azure Container Apps** | Deployment, scaling | Docker + CI/CD |
| **Azure Key Vault** | Secrets management | Managed Identity |
| **Azure Storage** | Audit logs, artifacts | Blob storage |
| **Azure Monitor** | Alerts, dashboards | Log Analytics integration |
| **Content Safety** | Input/output filtering | API integration |
| **Azure DevOps / GitHub Actions** | CI/CD pipelines | YAML workflows |

### Third-Party Tools

| **Tool** | **Purpose** | **Integration** |
|----------|-------------|-----------------|
| **LangSmith** | Tracing, debugging | OpenTelemetry |
| **W&B (Weights & Biases)** | Experiment tracking | Custom logging |
| **MLflow** | Model versioning, registry | Python SDK |
| **Prometheus + Grafana** | Metrics visualization | OTLP endpoint |
| **Jaeger / Zipkin** | Distributed tracing | OTLP endpoint |

---

## Next Steps

### Quick Start Checklist

- [ ] Set up Azure AI Foundry project
- [ ] Configure Application Insights
- [ ] Implement structured logging
- [ ] Create prompt configuration files
- [ ] Set up CI/CD pipeline
- [ ] Configure content safety
- [ ] Implement budget controls
- [ ] Create evaluation test suite
- [ ] Set up monitoring dashboards
- [ ] Configure alerts

### Continuous Improvement

1. **Weekly**: Review evaluation metrics and update prompts
2. **Monthly**: Analyze costs and optimize model selection
3. **Quarterly**: Review security and compliance posture
4. **Ongoing**: Monitor dashboards and respond to alerts

---

## Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Application Insights Best Practices](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)
- [MAF GitHub Repository](https://github.com/microsoft/agent-framework)

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**Maintained by:** AI Solutions Architecture Team

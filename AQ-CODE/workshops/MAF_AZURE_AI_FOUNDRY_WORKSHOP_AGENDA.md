# Microsoft Agent Framework Workshop
## Building Multi-Agent Solutions with Azure AI Foundry
**Duration:** 2 hours  
**Target Audience:** Teradata Technical Solution Architects  
**Level:** Intermediate

---

## Workshop Overview

This hands-on workshop introduces the **Microsoft Agent Framework (MAF)** with a focus on creating and orchestrating agents using **Azure AI Foundry**. Participants will learn the fundamentals of agent-based architecture, explore Azure AI Foundry's agent capabilities, understand orchestration patterns, and build practical multi-agent solutions.

### Learning Objectives
By the end of this workshop, you will be able to:
- Understand the Microsoft Agent Framework architecture and ecosystem
- Create and configure agents using Azure AI Foundry
- Implement various orchestration patterns for multi-agent collaboration
- Build interactive agent applications with real-world scenarios
- Apply best practices for agent development and deployment

### Prerequisites
- Azure subscription with access to Azure AI Foundry
- Basic Python programming knowledge
- Familiarity with AI concepts (LLMs, prompts, function calling)
- VS Code or similar IDE installed
- Azure CLI installed and authenticated (`az login`)

---

## Agenda

### 🎯 Module 1: Introduction & Foundations (20 minutes)

#### Welcome & Context (5 minutes)
- Workshop goals and structure
- Overview of AI agent landscape
- Microsoft's agent ecosystem positioning

#### Microsoft Agent Framework Overview (15 minutes)
- **What is MAF?**
  - Agent-based programming model
  - Key components: BaseAgent, ChatAgent, Workflow
  - Framework architecture and design principles
  
- **Agent Types in MAF**
  - Azure AI Foundry Agents (persistent, service-based)
  - Azure OpenAI Agents (stateless, client-based)
  - OpenAI Assistants API Agents
  - Microsoft 365 Copilot Studio Agents
  
- **Why Use MAF?**
  - Unified abstraction across agent platforms
  - Built-in orchestration patterns
  - Extensible with middleware and tools
  - Production-ready observability (OpenTelemetry)

**Resources:**
- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- Repo: `README.md` - Framework overview and installation
- Repo: `docs/design/` - Architecture documents

---

### ☁️ Module 2: Azure AI Foundry Agents (35 minutes)

#### Azure AI Foundry Agent Service Architecture (10 minutes)
- **What is Azure AI Foundry?**
  - Unified platform for AI application development
  - Project-based resource management
  - Built-in model deployments and management
  
- **Agent Service Components**
  - **Models:** GPT-4o, GPT-4o-mini, custom deployments
  - **Customization:** Instructions, system prompts, personas
  - **Tools:** Code Interpreter, File Search, Function Calling, OpenAPI tools
  - **Orchestration:** Service-managed conversation threads
  - **Observability:** Built-in tracing and monitoring
  - **Trust & Safety:** Content filtering, managed identity authentication

- **Agent vs Chat Playground**
  - When to use agents vs. direct chat completions
  - Persistent state management benefits
  - Tool integration advantages

**Resources:**
- [Azure AI Foundry Agents Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)
- [Agent Service Architecture](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-ai-foundry-agent)

#### Hands-On: Create Your First Azure AI Agent (15 minutes)

**Lab 1: Portal-Based Agent Creation**
1. Navigate to [Azure AI Foundry Portal](https://ai.azure.com)
2. Create a new project (or use existing)
3. Deploy gpt-4o-mini model
4. Create an agent with custom instructions
5. Test in the Agents Playground
6. Add File Search tool with sample document

**Demo Script:**
```plaintext
1. Click "Create an agent"
2. Name: "Technical Solution Assistant"
3. Instructions: "You are a technical advisor for data warehousing solutions. 
   Provide expert guidance on architecture, performance optimization, and 
   integration patterns."
4. Upload: sample_documents/teradata_migration_guide.md (example)
5. Test queries:
   - "What are best practices for data migration?"
   - "How should I approach performance tuning?"
```

**Lab 2: Programmatic Agent Creation with MAF**

Navigate to: `python/samples/getting_started/agents/azure_ai/`

**Explore:** `azure_ai_basic.py`
```python
# Key concepts demonstrated:
# 1. AzureAIAgentClient initialization
# 2. Create agent with instructions
# 3. Run agent with query
# 4. Get response text

# Run the sample:
cd python/samples/getting_started/agents/azure_ai
python azure_ai_basic.py
```

**Explore:** `azure_ai_with_function_tools.py`
```python
# Key concepts demonstrated:
# 1. Define function tools (weather, time)
# 2. Attach tools to agent
# 3. Agent automatically calls functions
# 4. Review function call tracing

# Run the sample:
python azure_ai_with_function_tools.py
```

**Discussion Points:**
- Environment variable configuration (`AZURE_AI_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME`)
- Authentication with `AzureCliCredential`
- Async programming patterns in MAF
- Agent lifecycle management (create, run, cleanup)

**Resources:**
- [Quickstart: Create a new agent](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart)
- Repo samples: `python/samples/getting_started/agents/azure_ai/`
- [Azure AI Foundry Python SDK](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-ai-foundry-agent#configuration)

#### Advanced Agent Features (10 minutes)

**Tool Integration Deep Dive**
- **Code Interpreter:** Execute Python code, generate visualizations
  - Demo: `azure_ai_with_code_interpreter.py`
  
- **File Search (RAG):** Knowledge retrieval from documents
  - Demo: `azure_ai_with_file_search.py`
  
- **Function Calling:** Custom business logic integration
  - Demo: `azure_ai_with_function_tools.py`
  
- **OpenAPI Tools:** Integrate with REST APIs
  - Demo: `azure_ai_with_openapi_tools.py`
  
- **MCP (Model Context Protocol):** External tool integration
  - Demo: `azure_ai_with_hosted_mcp.py`

**Reusing Existing Agents**
```python
# Connect to existing agent by ID
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async with AzureCliCredential() as credential:
    async with AzureAIAgentClient(
        async_credential=credential,
        agent_id="your-existing-agent-id"
    ) as agent:
        result = await agent.run("Hello!")
        print(result.text)
```

**Best Practices:**
- Use environment variables for configuration
- Implement proper error handling and retries
- Monitor token usage and costs
- Version control agent configurations
- Test with diverse inputs before production

---

### 🔀 Module 3: Orchestration Patterns with MAF (35 minutes)

#### Understanding Agent Orchestration (10 minutes)

**Why Orchestrate Agents?**
- Complex tasks require specialized expertise
- Parallel processing for efficiency
- Dynamic routing based on context
- Error handling and fallback strategies

**MAF Orchestration Primitives**
- **BaseAgent:** Core agent abstraction
- **ChatAgent:** Conversational agent with message history
- **Workflow:** Orchestration engine for multi-agent coordination
- **Middleware:** Cross-cutting concerns (logging, auth, rate limiting)

#### Core Orchestration Patterns (15 minutes)

**1. Sequential Pattern**
```python
# Agents execute in order, each building on previous results
# Use case: Research → Analysis → Report Generation

async def sequential_workflow(query: str):
    research_result = await researcher_agent.run(query)
    analysis_result = await analyst_agent.run(
        f"Analyze this research: {research_result.text}"
    )
    report = await writer_agent.run(
        f"Create a report from: {analysis_result.text}"
    )
    return report.text
```

**Demo:** Explore `workflow-samples/sequential/` patterns

**2. Concurrent Pattern**
```python
# Multiple agents work in parallel on independent tasks
# Use case: Gather insights from multiple perspectives simultaneously

import asyncio

async def concurrent_workflow(query: str):
    results = await asyncio.gather(
        market_researcher.run(query),
        financial_analyst.run(query),
        legal_advisor.run(query),
        technical_architect.run(query)
    )
    return results
```

**Demo:** `AQ-CODE/orchestration/concurrent_agents_interactive_devui.py`
- 5 specialized agents (Market Research, Marketing, Legal, Financial, Technical)
- DevUI backend on port 8092
- Concurrent execution with independent conversation threads

**3. Handoff Pattern**
```python
# Transfer conversation from one agent to another based on context
# Use case: Customer support routing to specialists

async def handoff_workflow(user_message: str):
    triage_result = await triage_agent.run(user_message)
    
    if "technical" in triage_result.text.lower():
        return await tech_support_agent.run(user_message)
    elif "billing" in triage_result.text.lower():
        return await billing_agent.run(user_message)
    else:
        return await general_support_agent.run(user_message)
```

**Demo:** Review `workflow-samples/handoff/` examples

**4. Magentic Pattern** (Multi-Agent Genetic)
```python
# Agents collaborate through shared context and dynamic coordination
# Use case: Creative problem-solving with iterative refinement

async def magentic_workflow(problem: str):
    shared_context = {"problem": problem, "iterations": []}
    
    for iteration in range(3):
        critique = await critic_agent.run(str(shared_context))
        solution = await solver_agent.run(str(shared_context) + critique.text)
        shared_context["iterations"].append({
            "critique": critique.text,
            "solution": solution.text
        })
    
    return shared_context
```

**Discussion: Choosing the Right Pattern**
- **Sequential:** Dependency chains, step-by-step processing
- **Concurrent:** Independent tasks, speed optimization
- **Handoff:** Routing, specialization, context switching
- **Magentic:** Complex problem-solving, iterative refinement

**Resources:**
- [Orchestration Patterns Documentation](https://learn.microsoft.com/en-us/agent-framework/concepts/orchestration)
- Repo: `workflow-samples/` - Pattern implementations
- [Connected Agents Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/connected-agents)

#### Hands-On: Build a Multi-Agent Solution (10 minutes)

**Lab 3: Product Launch Advisory System**

**Scenario:** You're launching a new telemedicine platform. Get advice from 5 specialized agents simultaneously.

**Run the Demo:**
```bash
# Terminal 1: Start DevUI backend
cd AQ-CODE/orchestration
python concurrent_agents_interactive_devui.py
# Backend runs on http://localhost:8092

# Terminal 2: Start Streamlit dashboard
cd AQ-CODE/orchestration
streamlit run multi_agent_dashboard_concurrent.py --server.port 8095
# Dashboard at http://localhost:8095
```

**Dashboard Features:**
- **Concurrent Queries:** Send same question to all 5 agents
- **Example Questions:** Pre-loaded product launch scenarios
  - E-bike subscription service
  - Telemedicine platform
  - Smart irrigation system
  - Smart home security
  - AI-powered learning platform
- **Real-time Updates:** Auto-refresh to display agent responses
- **Full Responses:** Scrollable text areas for complete outputs

**Exercise:**
1. Click "Telemedicine Platform Launch"
2. Observe all 5 agents processing simultaneously
3. Compare responses from different perspectives:
   - Market Researcher: Market size, competition, trends
   - Marketing Strategist: Positioning, campaigns, channels
   - Legal Advisor: Compliance (HIPAA, FDA), risk mitigation
   - Financial Analyst: Revenue models, costs, ROI
   - Technical Architect: System design, security, scalability

**Discussion:**
- How does concurrent processing improve decision-making?
- What orchestration pattern is being used? (Concurrent)
- How would you extend this for sequential refinement? (Add synthesis agent)
- What real-world use cases fit this pattern?

**Resources:**
- Code: `AQ-CODE/orchestration/multi_agent_dashboard_concurrent.py`
- Backend: `AQ-CODE/orchestration/concurrent_agents_interactive_devui.py`

---

### 🔧 Module 4: Production Considerations (20 minutes)

#### Observability & Tracing (8 minutes)

**OpenTelemetry Integration**
- MAF includes built-in tracing support
- Capture agent execution spans
- Monitor performance and bottlenecks
- Debug complex orchestration flows

**Example: Enable Tracing**
```python
from agent_framework.tracing import configure_tracing

# Configure OpenTelemetry exporter
configure_tracing(
    service_name="multi-agent-system",
    endpoint="http://localhost:4318"  # OTLP endpoint
)

# Traces automatically captured for all agent operations
result = await agent.run("Complex query")
```

**What Gets Traced:**
- Agent creation and initialization
- Message processing start/end
- Function tool invocations
- LLM API calls (latency, tokens, costs)
- Orchestration workflow steps

**Resources:**
- [Tracing and Observability Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/observability/tracing)
- Repo: `AQ-CODE/llmops/` - LLMOps best practices

#### Testing & Evaluation (7 minutes)

**Agent Testing Strategies**
1. **Unit Tests:** Individual agent capabilities
   ```python
   async def test_market_research_agent():
       result = await researcher_agent.run("Analyze EV market")
       assert "electric vehicle" in result.text.lower()
       assert len(result.text) > 100
   ```

2. **Integration Tests:** Multi-agent orchestration
   ```python
   async def test_product_launch_workflow():
       results = await concurrent_workflow("Launch telemedicine app")
       assert len(results) == 5
       assert all(r.text for r in results)
   ```

3. **Evaluation Metrics:**
   - Response quality (relevance, coherence)
   - Latency and performance
   - Tool usage accuracy
   - Cost efficiency (tokens, API calls)

**Example: Verification Script**
```bash
# Run comprehensive agent tests
python AQ-CODE/verify_agent_framework.py
# Tests: BaseAgent, ChatAgent, Workflow, Tools, Streaming
```

**Resources:**
- [Testing Best Practices](https://learn.microsoft.com/en-us/agent-framework/user-guide/testing)
- Repo: `AQ-CODE/verify_agent_framework.py`

#### Deployment & Scaling (5 minutes)

**Deployment Options**
1. **Azure Container Apps:** Serverless, auto-scaling
2. **Azure Kubernetes Service (AKS):** Full orchestration control
3. **Azure Functions:** Event-driven agent invocations
4. **Azure App Service:** Traditional web app hosting

**Sample: Docker Deployment**
```dockerfile
# See: AQ-CODE/Dockerfile
FROM python:3.11-slim

# Install Agent Framework
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy agent code
COPY orchestration/ /app/orchestration/

# Run DevUI backend
CMD ["python", "/app/orchestration/concurrent_agents_interactive_devui.py"]
```

**Scaling Considerations**
- **Horizontal Scaling:** Multiple agent instances behind load balancer
- **Rate Limiting:** Prevent API quota exhaustion
- **Caching:** Store frequent queries (Redis, Azure Cache)
- **Async Processing:** Use queues (Azure Service Bus) for long-running tasks

**Security Best Practices**
- Use Managed Identity for Azure authentication
- Store secrets in Azure Key Vault
- Implement content filtering (Azure AI Content Safety)
- Apply RBAC for agent access control
- Monitor for prompt injection attacks

**Resources:**
- [Deployment Guide](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/deployment)
- Repo: `AQ-CODE/deploy-to-azure.sh`

---

### 💡 Module 5: Real-World Use Cases & Q&A (10 minutes)

#### Industry Applications (5 minutes)

**1. Data Warehousing Advisory System** (Teradata-specific)
```plaintext
Agents:
- Migration Planner: Assess source systems, plan migration strategy
- Performance Optimizer: Query tuning, indexing recommendations
- Compliance Auditor: Data governance, GDPR/CCPA checks
- Cost Estimator: TCO analysis, resource sizing

Pattern: Sequential → Concurrent → Handoff
```

**2. Customer Support Automation**
```plaintext
Agents:
- Triage: Classify inquiry, route to specialist
- Technical Support: Debug issues, provide solutions
- Account Manager: Billing, subscription changes
- Escalation: Complex cases to human agents

Pattern: Handoff → Sequential
```

**3. Document Intelligence Pipeline**
```plaintext
Agents:
- Extractor: Pull structured data from documents (invoices, contracts)
- Validator: Check accuracy, completeness
- Enricher: Add metadata, categorization
- Publisher: Route to downstream systems

Pattern: Sequential → Concurrent (for multiple documents)
```

**4. Financial Analysis Platform**
```plaintext
Agents:
- Market Analyzer: Real-time market data, trends
- Risk Assessor: Portfolio risk, compliance checks
- Report Generator: Executive summaries, visualizations
- Alert Manager: Anomaly detection, notifications

Pattern: Concurrent → Sequential
```

#### Q&A Session (5 minutes)

**Common Questions:**

**Q: How do I choose between Azure AI Foundry Agents vs Azure OpenAI Agents?**
- **Azure AI Foundry:** Persistent state, managed threads, built-in tools (Code Interpreter, File Search)
- **Azure OpenAI:** Stateless, full control, lower cost for simple use cases
- **Rule:** Use Foundry for complex, multi-turn conversations with tools; use OpenAI for stateless, high-throughput scenarios

**Q: Can I migrate from LangChain/Semantic Kernel/AutoGen?**
- Yes! MAF provides migration guides
- Core concepts map: Agent → BaseAgent, Chain → Workflow, Memory → Thread Management
- See: `migration_research/` directory in repo

**Q: How do I handle agent errors and retries?**
```python
from agent_framework.middleware import RetryMiddleware

# Add retry middleware to agent
agent.use_middleware(RetryMiddleware(max_retries=3, backoff=2.0))

# Automatic retry on transient failures (429, 503)
result = await agent.run("Query")
```

**Q: What are the costs of running agents?**
- **Model Costs:** Per-token pricing (input + output)
- **Agent Service:** Included in Azure AI Foundry project costs
- **Storage:** For file uploads, thread persistence
- **Compute:** Minimal (serverless execution)
- **Optimization:** Use smaller models (gpt-4o-mini), caching, prompt engineering

**Q: How do I debug orchestration flows?**
- Enable tracing (OpenTelemetry)
- Use logging middleware
- Test agents individually before orchestration
- Visualize workflows with tools like Jaeger/Zipkin

---

## Workshop Wrap-Up

### Key Takeaways
✅ **Microsoft Agent Framework** provides a unified abstraction for building agent-based AI applications  
✅ **Azure AI Foundry Agents** offer persistent, tool-augmented agents with managed state  
✅ **Orchestration patterns** (sequential, concurrent, handoff, magentic) enable complex multi-agent workflows  
✅ **Production-ready features** (tracing, testing, security) are built into the framework  
✅ **Real-world applications** span customer support, data analysis, document processing, and more

### Next Steps
1. **Explore the Repo:** Clone `agent-framework-public`, run samples in `python/samples/`
2. **Build a Prototype:** Start with a simple agent, add tools, implement orchestration
3. **Deploy to Azure:** Use provided scripts (`deploy-to-azure.sh`, Dockerfile)
4. **Join the Community:** Contribute to GitHub, follow Microsoft Learn docs
5. **Advanced Topics:** Explore MCP integration, RAG patterns, multi-modal agents

### Resources

#### Official Documentation
- [Microsoft Agent Framework Home](https://learn.microsoft.com/en-us/agent-framework/)
- [Azure AI Foundry Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)
- [Agent Types Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/overview)
- [Orchestration Patterns](https://learn.microsoft.com/en-us/agent-framework/concepts/orchestration)
- [Tracing & Observability](https://learn.microsoft.com/en-us/agent-framework/user-guide/observability/tracing)

#### GitHub Repository
- **Main Repo:** [microsoft/agent-framework](https://github.com/microsoft/agent-framework)
- **This Workshop Repo:** `agent-framework-public` (forked)
- **Samples:** `python/samples/`, `dotnet/samples/`
- **Workflows:** `workflow-samples/`
- **Documentation:** `docs/`

#### Hands-On Resources
- `AQ-CODE/orchestration/` - Multi-agent dashboard demos
- `AQ-CODE/azure_ai/` - Azure AI Foundry samples
- `AQ-CODE/llmops/` - LLMOps best practices
- `AQ-CODE/verify_agent_framework.py` - Comprehensive test suite

#### Community & Support
- [Microsoft Learn Q&A](https://learn.microsoft.com/answers/topics/azure-ai-foundry.html)
- [Azure AI Foundry Discord](https://discord.gg/ByRwuEEgH4)
- [GitHub Discussions](https://github.com/microsoft/agent-framework/discussions)

---

## Appendix: Lab Setup Instructions

### Prerequisites Installation

**1. Python Environment**
```bash
# Install Python 3.11+
# macOS:
brew install python@3.11

# Windows:
# Download from python.org

# Create virtual environment
cd agent-framework-public
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# Install Agent Framework
pip install -e python
pip install -r requirements.txt
```

**2. Azure CLI**
```bash
# macOS:
brew install azure-cli

# Windows:
# Download MSI from docs.microsoft.com/cli/azure

# Login to Azure
az login
```

**3. Environment Variables**
```bash
# Create .env file
cat > .env << EOF
AZURE_AI_PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<project-id>
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
OPENWEATHER_API_KEY=<your-api-key>  # Optional for weather samples
EOF

# Load environment variables
export $(cat .env | xargs)
```

**4. Verify Installation**
```bash
python AQ-CODE/verify_agent_framework.py
# Expected: 11 tests passed
```

### Troubleshooting

**Issue: "Module not found: agent_framework"**
```bash
# Reinstall in editable mode
pip install -e python --force-reinstall
```

**Issue: "Authentication failed"**
```bash
# Re-authenticate Azure CLI
az logout
az login
az account show  # Verify correct subscription
```

**Issue: "Model deployment not found"**
```bash
# Check available deployments in Azure AI Foundry portal
# Ensure AZURE_AI_MODEL_DEPLOYMENT_NAME matches exactly
```

**Issue: "Port already in use"**
```bash
# Kill process on port 8092
lsof -ti:8092 | xargs kill -9

# Or use different port
python concurrent_agents_interactive_devui.py --port 8093
```

---

## Appendix: Additional Learning Paths

### For Beginners
1. **Start Here:** `python/samples/getting_started/agents/azure_ai/azure_ai_basic.py`
2. **Add Tools:** `azure_ai_with_function_tools.py`
3. **Multi-Agent:** `AQ-CODE/orchestration/concurrent_agents_interactive_devui.py`
4. **Dashboard:** `AQ-CODE/orchestration/multi_agent_dashboard_concurrent.py`

### For Advanced Users
1. **Custom Middleware:** `docs/design/middleware.md`
2. **RAG Patterns:** `python/samples/getting_started/agents/azure_ai/azure_ai_with_file_search.py`
3. **MCP Integration:** `python/samples/getting_started/agents/azure_ai/azure_ai_with_hosted_mcp.py`
4. **OpenAPI Tools:** `python/samples/getting_started/agents/azure_ai/azure_ai_with_openapi_tools.py`

### Migration from Other Frameworks
- **From LangChain:** `migration_research/langchain-migration.md`
- **From Semantic Kernel:** [Official Migration Guide](https://learn.microsoft.com/en-us/agent-framework/migration/semantic-kernel)
- **From AutoGen:** `migration_research/autogen-migration.md`

---

**Workshop Prepared By:** Microsoft Agent Framework Team  
**Last Updated:** January 2025  
**Version:** 1.0

**Feedback:** Please share your experience and suggestions to improve this workshop!

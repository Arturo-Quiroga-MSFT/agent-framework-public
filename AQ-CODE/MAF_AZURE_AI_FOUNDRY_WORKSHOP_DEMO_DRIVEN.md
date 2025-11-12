# Microsoft Agent Framework Workshop
## Building Multi-Agent Solutions with Azure AI Foundry (Demo-Driven)
**Duration:** 2 hours  
**Target Audience:** Teradata Technical Solution Architects  
**Format:** Lecture + Live Demonstrations  
**Level:** Intermediate

---

## Workshop Overview

This demonstration-driven workshop introduces the **Microsoft Agent Framework (MAF)** with a focus on creating and orchestrating agents using **Azure AI Foundry**. Through live demonstrations and real-world examples, participants will learn agent-based architecture, Azure AI Foundry's capabilities, orchestration patterns, and production deployment strategies.

### Learning Objectives
By the end of this workshop, you will understand:
- Microsoft Agent Framework architecture and ecosystem
- How to create and configure agents using Azure AI Foundry
- Multi-agent orchestration patterns and when to use them
- Production deployment and observability strategies
- Real-world applications and use cases

### Workshop Format
- **Instructor-led presentations** with conceptual explanations
- **Live demonstrations** of agent creation, orchestration, and deployment
- **Code walkthroughs** of working samples from the repository
- **Q&A throughout** for clarification and discussion

---

## Agenda

### 🎯 Module 1: Introduction & Microsoft Agent Framework Foundations (25 minutes)

#### Welcome & Context (5 minutes)
- Workshop objectives and structure
- Current AI agent landscape
- Microsoft's agent ecosystem positioning

#### Microsoft Agent Framework Deep Dive (20 minutes)

**What is MAF?**
- Agent-based programming paradigm shift
- Core architecture: BaseAgent, ChatAgent, Workflow
- Design principles and philosophy
- Framework evolution and roadmap

**Agent Types Ecosystem**
- **Azure AI Foundry Agents:** Persistent, service-managed, tool-augmented
- **Azure OpenAI Agents:** Stateless, client-side, flexible
- **OpenAI Assistants API:** Direct OpenAI integration
- **Microsoft 365 Copilot Studio:** Enterprise agent builder

**Why Choose MAF?**
- Unified abstraction across platforms
- Built-in orchestration primitives
- Production-ready observability (OpenTelemetry)
- Extensibility through middleware
- Migration support from LangChain, Semantic Kernel, AutoGen

**Comparison Matrix:**
| Feature | Azure AI Foundry | Azure OpenAI | Copilot Studio |
|---------|------------------|--------------|----------------|
| State Management | Persistent threads | Stateless | Platform-managed |
| Built-in Tools | Code Interpreter, File Search | Custom only | Pre-built connectors |
| Hosting | Azure-managed | Self-hosted | Microsoft 365 |
| Best For | Complex workflows | High-throughput | Enterprise integration |

**Resources:**
- Microsoft Agent Framework Documentation
- Repository: `README.md`, `docs/design/`

---

### ☁️ Module 2: Azure AI Foundry Agents (35 minutes)

#### Azure AI Foundry Agent Service Architecture (15 minutes)

**Platform Overview**
- Azure AI Foundry as unified AI development platform
- Project-based resource organization
- Built-in model catalog and deployment
- Integration with Azure services (Search, Key Vault, Storage)

**Agent Service Components**
- **Models:** GPT-4o, GPT-4o-mini, custom fine-tuned models
- **Customization:** System instructions, personas, temperature control
- **Tools:**
  - Code Interpreter: Execute Python, generate visualizations
  - File Search: RAG for document knowledge bases
  - Function Calling: Custom business logic integration
  - OpenAPI: REST API integration
  - MCP (Model Context Protocol): External tool protocols
- **Orchestration:** Service-managed conversation threads and context
- **Observability:** Request tracing, token usage, performance metrics
- **Trust & Safety:** Azure AI Content Safety, managed identities, RBAC

**Agent vs. Chat Playground**
- When to use agents vs. direct completions
- Persistent state benefits
- Tool integration advantages
- Cost considerations

**Demo 1: Portal-Based Agent Creation** (10 minutes)
```
Live demonstration in Azure AI Foundry Portal:
1. Navigate to ai.azure.com
2. Create new project / use existing
3. Deploy gpt-4o-mini model
4. Create agent: "Technical Solution Assistant"
5. Configure instructions:
   "You are a technical advisor for data warehousing solutions.
    Provide expert guidance on architecture, performance optimization,
    and integration patterns."
6. Add File Search tool
7. Upload sample document (migration guide)
8. Test in Agents Playground:
   - "What are best practices for data migration?"
   - "How should I approach performance tuning?"
   - Show how agent searches uploaded document
9. Review conversation thread persistence
10. Demonstrate agent settings (temperature, top_p, tools)
```

**Key Takeaways:**
- Portal provides quick agent prototyping
- Built-in tools require minimal configuration
- Conversation threads persist across sessions
- Agent configurations can be exported/imported

#### Programmatic Agent Creation & Management (10 minutes)

**Demo 2: Python SDK Agent Creation**
```
Code walkthrough: python/samples/getting_started/agents/azure_ai/

File: azure_ai_basic.py
- Show AzureAIAgentClient initialization
- Environment variable configuration
- Create agent with instructions
- Run agent with query
- Display response text
- Agent cleanup and lifecycle

File: azure_ai_with_function_tools.py
- Define custom function tools (weather, time)
- Attach tools to agent
- Agent automatically invokes functions
- Review function call logs
- Demonstrate parallel function calling

File: azure_ai_with_code_interpreter.py
- Upload data file (CSV)
- Agent generates Python code for analysis
- Agent executes code in sandbox
- Agent returns results and visualizations
- Show generated plots
```

**Configuration Best Practices:**
```python
# Environment variables
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<id>
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Authentication
AzureCliCredential() - for development
ManagedIdentityCredential() - for production
```

**Demo 3: Advanced Tool Integration** (10 minutes)
```
Code walkthrough: Advanced agent samples

File: azure_ai_with_file_search.py
- Create vector store for documents
- Upload multiple files
- Configure file search tool
- Query across document corpus
- Show semantic search results

File: azure_ai_with_openapi_tools.py
- Define OpenAPI specification
- Register API as tool
- Agent calls external REST API
- Handle authentication (API keys, OAuth)
- Parse and present API responses

File: azure_ai_with_hosted_mcp.py
- Connect to Model Context Protocol server
- Expose external tools to agent
- Agent discovers and uses MCP tools
- Show tool orchestration
```

**Reusing Existing Agents:**
```python
# Connect to existing agent by ID
agent = await client.get_agent(agent_id="existing-agent-uuid")

# Use existing conversation thread
thread = await client.get_thread(thread_id="existing-thread-uuid")

# Continue conversation
result = await agent.run("Follow-up question", thread_id=thread.id)
```

**Resources:**
- Azure AI Foundry Agents Documentation
- Repository samples: `python/samples/getting_started/agents/azure_ai/`
- SDK reference documentation

---

### 🔀 Module 3: Multi-Agent Orchestration Patterns (35 minutes)

#### Understanding Orchestration (10 minutes)

**Why Multi-Agent Systems?**
- Complex problems require specialized expertise
- Parallel processing improves efficiency
- Dynamic routing based on context
- Redundancy and error recovery
- Separation of concerns and modularity

**MAF Orchestration Primitives**
- **BaseAgent:** Core agent abstraction and interface
- **ChatAgent:** Conversational agent with message history
- **Workflow:** Multi-agent coordination engine
- **Middleware:** Cross-cutting concerns (logging, auth, rate limiting, retry logic)

**Orchestration Design Considerations**
- Agent specialization vs. generalization
- Communication patterns (synchronous, asynchronous, event-driven)
- State management and context sharing
- Error handling and fallback strategies
- Performance optimization (caching, batching, streaming)

#### Four Core Orchestration Patterns (15 minutes)

**1. Sequential Pattern**
```
Use Case: Research → Analysis → Report Generation
Characteristics:
- Agents execute in order
- Each agent builds on previous results
- Linear dependency chain
- Predictable execution flow

Example: Document Processing Pipeline
1. Extractor Agent: Pull structured data from PDF
2. Validator Agent: Check accuracy and completeness
3. Enricher Agent: Add metadata and categorization
4. Publisher Agent: Route to downstream systems

Demo code walkthrough:
workflow-samples/sequential/document_pipeline.py
```

**2. Concurrent Pattern**
```
Use Case: Gather insights from multiple perspectives simultaneously
Characteristics:
- Multiple agents work in parallel
- Independent tasks
- No inter-agent dependencies
- Aggregate results at end

Example: Product Launch Advisory
- Market Researcher: Market size, competition, trends
- Marketing Strategist: Positioning, campaigns, channels
- Legal Advisor: Compliance, risk mitigation
- Financial Analyst: Revenue models, costs, ROI
- Technical Architect: System design, security, scalability

All agents process same query simultaneously
```

**3. Handoff Pattern**
```
Use Case: Customer support routing to specialists
Characteristics:
- Transfer conversation between agents
- Dynamic routing based on context
- Specialization by domain
- Context preservation across handoffs

Example: IT Support System
1. Triage Agent: Classify inquiry (billing, technical, account)
2. Route to specialist agent based on classification
3. Escalation Agent: Complex cases to human agents

Demo code walkthrough:
workflow-samples/handoff/support_routing.py
```

**4. Magentic Pattern** (Multi-Agent Genetic)
```
Use Case: Creative problem-solving with iterative refinement
Characteristics:
- Agents collaborate through shared context
- Iterative improvement cycles
- Critique and refinement loops
- Emergent solutions

Example: Technical Architecture Design
1. Architect Agent: Propose initial design
2. Security Agent: Critique security aspects
3. Performance Agent: Critique scalability
4. Cost Agent: Critique cost efficiency
5. Architect Agent: Refine design based on feedback
Repeat for N iterations

Demo code walkthrough:
workflow-samples/magentic/architecture_review.py
```

**Pattern Selection Guide:**
| Pattern | When to Use | Complexity | Latency |
|---------|-------------|------------|---------|
| Sequential | Dependency chain, step-by-step | Low | High |
| Concurrent | Independent tasks, speed critical | Medium | Low |
| Handoff | Specialization, routing | Medium | Medium |
| Magentic | Complex problem-solving | High | High |

#### Live Multi-Agent Demo (10 minutes)

**Demo 4: Product Launch Advisory System**
```
System: 5-Agent Concurrent Orchestration

Architecture:
- DevUI Backend (port 8092): Manages 5 ChatAgent instances
- Streamlit Dashboard (port 8095): Interactive UI with auto-refresh
- Concurrent execution with threading.Thread
- Queue-based result collection

Agents:
1. Market_Researcher: Market analysis, competitive landscape
2. Marketing_Strategist: Go-to-market strategy, campaigns
3. Legal_Compliance_Advisor: Regulatory compliance, risk assessment
4. Financial_Analyst: Business model, financial projections
5. Technical_Architect: System architecture, technology stack

Live Demonstration:
1. Start DevUI backend
   cd AQ-CODE/orchestration
   python concurrent_agents_interactive_devui.py

2. Launch Streamlit dashboard
   streamlit run multi_agent_dashboard_concurrent.py --server.port 8095

3. Test scenario: "Telemedicine Platform Launch"
   - Click pre-loaded example button
   - Watch all 5 agents process simultaneously
   - Auto-refresh polls for completed responses
   - Compare perspectives from different domains

4. Show concurrent execution benefits:
   - Total time vs. sequential execution
   - Independent agent reasoning
   - Comprehensive multi-perspective analysis

5. Review agent responses:
   - Market Researcher: Healthcare market trends, competition
   - Marketing: Patient acquisition strategies
   - Legal: HIPAA compliance, FDA regulations
   - Financial: Subscription pricing, CAC, LTV
   - Technical: FHIR integration, security architecture

6. Demonstrate other scenarios:
   - E-bike subscription service
   - Smart irrigation system
   - AI-powered learning platform
```

**Architecture Highlights:**
```python
# Concurrent execution pattern
async def query_all_agents(question: str):
    results = await asyncio.gather(
        market_researcher.run(question),
        marketing_strategist.run(question),
        legal_advisor.run(question),
        financial_analyst.run(question),
        technical_architect.run(question)
    )
    return results

# Threading for non-blocking UI
def send_message_thread(agent, message, result_queue):
    response = agent.send_message(message)
    result_queue.put((agent.name, response))

# Auto-refresh for real-time updates
if auto_refresh:
    time.sleep(2)
    st.rerun()
```

**Key Takeaways:**
- Concurrent pattern reduces total latency by ~5x
- Each agent maintains independent reasoning
- UI remains responsive during processing
- Easy to scale horizontally (add more agents)

**Resources:**
- Repository: `AQ-CODE/orchestration/`
- Workflow samples: `workflow-samples/`
- Orchestration patterns documentation

---

### 🔧 Module 4: Production Deployment & Best Practices (20 minutes)

#### Observability & Monitoring (8 minutes)

**Built-in Tracing with OpenTelemetry**
```python
from agent_framework.tracing import configure_tracing

# Configure OTLP exporter
configure_tracing(
    service_name="multi-agent-system",
    endpoint="http://localhost:4318"
)

# Automatic trace capture for:
# - Agent initialization
# - Message processing
# - Function tool invocations
# - LLM API calls (latency, tokens, costs)
# - Orchestration workflow steps
```

**What Gets Traced:**
- Request/response latency
- Token usage (input/output)
- Model selection and parameters
- Tool invocations and results
- Error rates and types
- Inter-agent communication

**Demo 5: Tracing Visualization**
```
Show Jaeger/Zipkin traces:
1. Agent execution spans
2. LLM API call latency
3. Function tool execution time
4. Total workflow duration
5. Error propagation paths

Metrics to monitor:
- Average response time
- P95/P99 latency
- Token consumption rate
- Error rate by agent
- Tool invocation frequency
```

**Cost Monitoring:**
- Track tokens per request
- Model pricing differences (gpt-4o vs gpt-4o-mini)
- Tool execution costs (Code Interpreter, API calls)
- Storage costs (thread persistence, file uploads)

#### Testing & Quality Assurance (6 minutes)

**Testing Strategy Pyramid**
```
1. Unit Tests: Individual agent capabilities
   - Test agent instructions and persona
   - Validate function tool definitions
   - Check response format and structure

2. Integration Tests: Multi-agent orchestration
   - Test workflow execution
   - Validate agent handoffs
   - Check context preservation

3. Evaluation Tests: Quality metrics
   - Response relevance and accuracy
   - Hallucination detection
   - Consistency across runs
```

**Demo 6: Verification Test Suite**
```bash
# Run comprehensive agent tests
python AQ-CODE/verify_agent_framework.py

Tests executed:
✓ BaseAgent initialization
✓ ChatAgent conversation flow
✓ Function tool registration
✓ Workflow orchestration
✓ Streaming responses
✓ Error handling
✓ Middleware integration
✓ Context management
✓ Thread persistence
✓ Agent cleanup
✓ Performance benchmarks

Results: 11/11 tests passed
```

**Evaluation Metrics:**
- **Accuracy:** Correct information retrieval
- **Relevance:** Response addresses query
- **Coherence:** Logical flow and structure
- **Groundedness:** Citations from sources
- **Latency:** Response time targets
- **Cost:** Token efficiency

#### Deployment Strategies (6 minutes)

**Deployment Options Comparison**

| Option | Best For | Scaling | Cost Model |
|--------|----------|---------|------------|
| Azure Container Apps | Microservices, auto-scale | Automatic | Consumption |
| Azure Kubernetes (AKS) | Complex orchestration | Manual/HPA | Reserved |
| Azure Functions | Event-driven, serverless | Automatic | Consumption |
| Azure App Service | Traditional web apps | Manual/auto | App Service Plan |

**Demo 7: Docker Containerization**
```dockerfile
# Show: AQ-CODE/Dockerfile

FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy agent code
COPY orchestration/ /app/orchestration/
COPY azure_ai/ /app/azure_ai/

# Environment variables
ENV AZURE_AI_PROJECT_ENDPOINT=https://...
ENV AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Run application
CMD ["python", "/app/orchestration/concurrent_agents_interactive_devui.py"]

# Build and run
docker build -t maf-agents .
docker run -p 8092:8092 maf-agents
```

**Deployment Script Walkthrough:**
```bash
# Show: AQ-CODE/deploy-to-azure.sh

# 1. Build container image
# 2. Push to Azure Container Registry
# 3. Deploy to Azure Container Apps
# 4. Configure environment variables from Key Vault
# 5. Set up Application Insights for monitoring
# 6. Configure auto-scaling rules
# 7. Enable managed identity
```

**Production Best Practices**

**Security:**
- ✅ Use Managed Identity for Azure authentication
- ✅ Store secrets in Azure Key Vault
- ✅ Implement Azure AI Content Safety filters
- ✅ Apply RBAC for agent access control
- ✅ Enable network isolation (VNet integration)
- ✅ Monitor for prompt injection attacks

**Scalability:**
- ✅ Horizontal scaling: Multiple agent instances behind load balancer
- ✅ Rate limiting: Prevent API quota exhaustion
- ✅ Caching: Redis for frequent queries
- ✅ Async processing: Service Bus queues for long-running tasks
- ✅ Connection pooling: Reuse HTTP clients

**Reliability:**
- ✅ Retry middleware for transient failures
- ✅ Circuit breakers for external dependencies
- ✅ Graceful degradation (fallback responses)
- ✅ Health checks and readiness probes
- ✅ Blue-green deployments for zero downtime

**Resources:**
- Azure AI Foundry deployment guide
- Repository: `AQ-CODE/deploy-to-azure.sh`, `AQ-CODE/Dockerfile`
- LLMOps best practices: `AQ-CODE/llmops/`

---

### 💡 Module 5: Real-World Applications & Q&A (15 minutes)

#### Industry Use Cases (10 minutes)

**1. Data Warehousing Advisory System** (Teradata-Specific)
```
Scenario: Automated consulting for data platform optimization

Agents:
- Migration_Planner: Assess source systems, estimate effort, plan phased migration
- Performance_Optimizer: Analyze query patterns, recommend indexing strategies
- Compliance_Auditor: Validate data governance, GDPR/CCPA compliance
- Cost_Estimator: TCO analysis, resource sizing, licensing optimization
- Integration_Architect: ETL/ELT design, real-time streaming, API integration

Orchestration Pattern: Sequential → Concurrent → Synthesis
1. Migration Planner creates initial assessment (Sequential)
2. All specialists analyze in parallel (Concurrent)
3. Synthesis agent creates unified recommendation (Sequential)

Benefits:
- 24/7 availability for partner/customer inquiries
- Consistent best practice recommendations
- Comprehensive multi-perspective analysis
- Knowledge base integration (past migrations, case studies)
```

**2. Customer Support Automation**
```
Scenario: Intelligent ticket routing and resolution

Agents:
- Triage_Agent: Classify inquiry, detect urgency, route appropriately
- Technical_Support: Debug issues, provide solutions, escalate if needed
- Account_Manager: Handle billing, subscriptions, account changes
- Knowledge_Base: Search documentation, return relevant articles
- Escalation_Agent: Complex cases to human agents with full context

Orchestration Pattern: Handoff
- Dynamic routing based on intent classification
- Context preservation across agent handoffs
- Human-in-the-loop for edge cases

Metrics:
- 60% ticket auto-resolution
- 40% reduction in mean time to resolution
- Consistent 24/7 coverage
```

**3. Document Intelligence Pipeline**
```
Scenario: Automated contract analysis and processing

Agents:
- Extractor: Pull structured data (parties, dates, amounts, clauses)
- Validator: Check accuracy, completeness, flag anomalies
- Compliance_Checker: Validate against regulatory requirements
- Risk_Assessor: Identify potential legal/financial risks
- Classifier: Categorize by type, route to appropriate workflow

Orchestration Pattern: Sequential with branching
- Extract → Validate → (Compliance + Risk) in parallel → Classify

Tools:
- Code Interpreter: Data extraction and transformation
- File Search: Reference clause library
- OpenAPI: Integration with document management systems
```

**4. Financial Analysis Platform**
```
Scenario: Real-time market intelligence and portfolio management

Agents:
- Market_Analyzer: Real-time data feeds, trend identification
- Risk_Assessor: Portfolio risk metrics, compliance checks
- Report_Generator: Executive summaries, visualizations
- Alert_Manager: Anomaly detection, threshold notifications
- Trading_Advisor: Strategy recommendations (read-only, no execution)

Orchestration Pattern: Concurrent → Sequential
- All analysts gather intelligence simultaneously
- Report generator synthesizes findings

Integration:
- OpenAPI tools: Bloomberg, Reuters, internal trading systems
- Code Interpreter: Statistical analysis, backtesting
- File Search: Historical reports, research notes
```

**5. Intelligent DevOps Assistant**
```
Scenario: Automated troubleshooting and incident response

Agents:
- Log_Analyzer: Parse logs, identify errors, correlate events
- Metrics_Analyzer: Monitor performance metrics, detect anomalies
- Root_Cause_Investigator: Trace errors to source
- Remediation_Advisor: Suggest fixes, generate runbooks
- Documentation_Agent: Update incident reports, post-mortems

Orchestration Pattern: Concurrent detection → Sequential investigation
- Real-time monitoring by multiple agents
- Coordinated investigation workflow
- Automatic ticket creation and escalation
```

#### Q&A Session (5 minutes)

**Common Questions:**

**Q: How do I choose between Azure AI Foundry Agents vs. Azure OpenAI Agents?**
```
Azure AI Foundry Agents:
✓ Persistent conversation threads
✓ Built-in tools (Code Interpreter, File Search)
✓ Managed infrastructure
✓ Best for: Complex, multi-turn conversations

Azure OpenAI Agents:
✓ Stateless, lower cost
✓ Full control over implementation
✓ Custom tool integration
✓ Best for: High-throughput, simple interactions

Decision Matrix:
- Need state? → Azure AI Foundry
- Need built-in tools? → Azure AI Foundry
- Cost-sensitive? → Azure OpenAI
- High volume (>1000 req/min)? → Azure OpenAI
```

**Q: Can I migrate from LangChain/Semantic Kernel/AutoGen?**
```
Yes! MAF provides migration paths:

From LangChain:
- Agent → BaseAgent
- Chain → Workflow
- Memory → Thread Management
- Tools → Function Tools

From Semantic Kernel:
- Kernel → AgentClient
- Plugin → Function Tools
- Planner → Workflow orchestration

From AutoGen:
- ConversableAgent → ChatAgent
- GroupChat → Workflow
- Function calling → Direct mapping

See: migration_research/ directory for detailed guides
```

**Q: What are the costs of running agents?**
```
Cost Components:
1. Model tokens: $0.15-$10 per 1M tokens (model-dependent)
2. Agent Service: Included in Azure AI Foundry project
3. Storage: File uploads, thread persistence (~$0.02/GB/month)
4. Compute: Container Apps (~$0.000024/vCPU-second)
5. Tools: Code Interpreter, API calls (minimal)

Optimization Strategies:
✓ Use gpt-4o-mini for non-critical tasks (10x cheaper)
✓ Implement response caching
✓ Optimize prompts (reduce input tokens)
✓ Set max_tokens limits
✓ Monitor and alert on usage spikes

Example: 10,000 queries/day
- Input: 500 tokens/query = 5M tokens
- Output: 200 tokens/query = 2M tokens
- Cost: ~$5-15/day (depends on model)
```

**Q: How do I handle agent errors and failures?**
```python
# Retry middleware for transient failures
from agent_framework.middleware import RetryMiddleware

agent.use_middleware(RetryMiddleware(
    max_retries=3,
    backoff=2.0,  # Exponential backoff
    retriable_errors=[429, 500, 502, 503, 504]
))

# Circuit breaker for cascading failures
from agent_framework.middleware import CircuitBreakerMiddleware

agent.use_middleware(CircuitBreakerMiddleware(
    failure_threshold=5,
    recovery_timeout=60
))

# Fallback responses
try:
    result = await agent.run(query)
except Exception:
    result = await fallback_agent.run(query)
```

**Q: How do I debug orchestration flows?**
```
Debugging Strategies:
1. Enable tracing (OpenTelemetry)
   - View spans in Jaeger/Zipkin
   - Identify bottlenecks and errors

2. Add logging middleware
   - Log all agent inputs/outputs
   - Track execution flow

3. Test agents individually
   - Verify each agent before orchestration
   - Use unit tests

4. Use synchronous mode during development
   - Easier to debug than async
   - Switch to async for production

5. Visualize workflows
   - Draw diagrams of orchestration
   - Document expected behavior
```

**Q: What about data privacy and security?**
```
Security Measures:
✓ Azure Private Link: Keep traffic in Azure network
✓ Customer-Managed Keys: Encrypt data at rest
✓ Managed Identity: No secrets in code
✓ Content Filtering: Detect harmful content
✓ Audit Logs: Track all agent interactions
✓ Data Residency: Control where data is processed
✓ PII Detection: Automatic scrubbing/redaction

Compliance:
✓ SOC 2 Type 2
✓ ISO 27001
✓ HIPAA (with BAA)
✓ GDPR
✓ FedRAMP (in progress)
```

---

## Workshop Summary

### Key Takeaways
✅ **Microsoft Agent Framework** provides unified abstraction for agent-based AI applications  
✅ **Azure AI Foundry Agents** offer persistent, tool-augmented agents with managed infrastructure  
✅ **Four orchestration patterns** (Sequential, Concurrent, Handoff, Magentic) solve different coordination challenges  
✅ **Production-ready features** (tracing, testing, security) built into the framework  
✅ **Real-world applications** span consulting, support, document processing, financial analysis, and DevOps

### What We Demonstrated
- Portal-based and programmatic agent creation
- Tool integration (Code Interpreter, File Search, Functions, OpenAPI)
- Multi-agent concurrent orchestration (5-agent product launch system)
- Tracing and observability
- Verification test suite
- Docker containerization and deployment

### Next Steps for Participants
1. **Explore Repository:** Clone `agent-framework-public`, review samples in `python/samples/`
2. **Create Proof of Concept:** Start with single agent, add tools, implement orchestration
3. **Deploy to Azure:** Use provided scripts and Dockerfiles
4. **Join Community:** GitHub discussions, Microsoft Learn Q&A
5. **Advanced Topics:** RAG patterns, multi-modal agents, MCP integration

---

## Resources

### Official Documentation
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/)
- [Azure AI Foundry Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)
- [Agent Types Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/overview)
- [Orchestration Patterns](https://learn.microsoft.com/en-us/agent-framework/concepts/orchestration)
- [Tracing & Observability](https://learn.microsoft.com/en-us/agent-framework/user-guide/observability/tracing)

### GitHub Repository
- **Main Repository:** [microsoft/agent-framework](https://github.com/microsoft/agent-framework)
- **Workshop Repository:** `agent-framework-public` (forked)
- **Samples:** `python/samples/`, `dotnet/samples/`
- **Workflows:** `workflow-samples/`
- **Documentation:** `docs/`

### Demo Code
- `python/samples/getting_started/agents/azure_ai/` - Azure AI Foundry samples
- `AQ-CODE/orchestration/` - Multi-agent dashboard demos
- `AQ-CODE/verify_agent_framework.py` - Test suite
- `AQ-CODE/deploy-to-azure.sh` - Deployment automation
- `AQ-CODE/llmops/` - LLMOps best practices

### Community & Support
- [Microsoft Learn Q&A](https://learn.microsoft.com/answers/topics/azure-ai-foundry.html)
- [Azure AI Foundry Discord](https://discord.gg/ByRwuEEgH4)
- [GitHub Discussions](https://github.com/microsoft/agent-framework/discussions)

---

## Appendix: Setup Guide for Follow-Along

While this workshop is demo-driven, participants who want to follow along or experiment afterward can use this setup guide.

### Prerequisites
- Azure subscription with Azure AI Foundry access
- Azure CLI installed (`az login`)
- Python 3.11+ environment
- Git installed

### Quick Setup
```bash
# Clone repository
git clone https://github.com/Arturo-Quiroga-MSFT/agent-framework-public.git
cd agent-framework-public

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e python
pip install -r requirements.txt

# Configure environment variables
export AZURE_AI_PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<id>"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"

# Verify installation
python AQ-CODE/verify_agent_framework.py
```

### Running Demos
```bash
# Azure AI basic agent
cd python/samples/getting_started/agents/azure_ai
python azure_ai_basic.py

# Multi-agent dashboard
cd AQ-CODE/orchestration
python concurrent_agents_interactive_devui.py  # Terminal 1
streamlit run multi_agent_dashboard_concurrent.py --server.port 8095  # Terminal 2
```

### Troubleshooting
**"Module not found":** `pip install -e python --force-reinstall`  
**"Authentication failed":** `az logout && az login`  
**"Port in use":** `lsof -ti:8092 | xargs kill -9`

---

**Workshop Prepared By:** Microsoft Agent Framework Team  
**Last Updated:** January 2025  
**Version:** 1.0 (Demo-Driven Format)

**Feedback Welcome:** Share your experience and suggestions to improve future workshops!

Subject: Microsoft Agent Framework Workshop - Demo-Driven Format (Agenda for Review)

---

Dear Teradata Team,

I'm pleased to share an alternative format for our **Microsoft Agent Framework Workshop** focused on Azure AI Foundry agents. This 2-hour session is structured as **lecture + live demonstrations** by the instructor, allowing participants to observe and learn without the need for hands-on setup.

This format is ideal for larger groups, diverse technical backgrounds, or when participants prefer to focus on learning concepts before implementing them independently.

Please review the agenda below and let me know your preference between this demo-driven format and the hands-on lab format.

---

## Workshop Overview
**Title:** Building Multi-Agent Solutions with Azure AI Foundry (Demo-Driven)  
**Duration:** 2 hours  
**Target Audience:** Technical Solution Architects  
**Format:** Instructor-led lecture with live demonstrations  
**Level:** Intermediate

---

## Detailed Agenda

### Module 1: Introduction & Microsoft Agent Framework Foundations ⏱️ 25 minutes

**Topics:**
- Workshop objectives and Microsoft's agent ecosystem overview
- Microsoft Agent Framework (MAF) architecture deep dive
- Agent types comparison: Azure AI Foundry, Azure OpenAI, Copilot Studio, Assistants API
- Why choose MAF: Unified abstraction, orchestration, observability, migration support

**Subtopics:**
- Core architecture: BaseAgent, ChatAgent, Workflow
- Design principles and framework philosophy
- Agent type comparison matrix (state management, tools, hosting, use cases)
- Framework evolution and roadmap

**Delivery:**
- Conceptual presentation with diagrams
- Code repository walkthrough
- Architecture documentation review

---

### Module 2: Azure AI Foundry Agents ⏱️ 35 minutes

**Topics:**
- Azure AI Foundry Agent Service architecture
- Platform components: models, customization, tools, orchestration, observability
- Agent creation (portal and programmatic)
- Advanced tool integration

**Subtopics:**
- Project-based resource organization
- Model catalog: GPT-4o, GPT-4o-mini, fine-tuned models
- Built-in tools: Code Interpreter, File Search, Function Calling, OpenAPI, MCP
- Service-managed conversation threads
- Trust & safety: Content filtering, managed identity, RBAC

**Live Demonstrations:**

**Demo 1: Portal-Based Agent Creation** (10 minutes)
- Navigate Azure AI Foundry Portal (ai.azure.com)
- Create new project and deploy model
- Configure agent: "Technical Solution Assistant"
- Add File Search tool with sample document
- Test in Agents Playground with real queries
- Show conversation thread persistence
- Review agent settings and configurations

**Demo 2: Python SDK Agent Creation** (10 minutes)
- Walkthrough: `azure_ai_basic.py` (basic agent creation)
- Walkthrough: `azure_ai_with_function_tools.py` (custom function tools)
- Walkthrough: `azure_ai_with_code_interpreter.py` (data analysis)
- Environment configuration and authentication
- Agent lifecycle management

**Demo 3: Advanced Tool Integration** (10 minutes)
- Walkthrough: `azure_ai_with_file_search.py` (RAG with documents)
- Walkthrough: `azure_ai_with_openapi_tools.py` (REST API integration)
- Walkthrough: `azure_ai_with_hosted_mcp.py` (Model Context Protocol)
- Reusing existing agents by ID
- Thread management for conversations

**Discussion:**
- Portal vs. programmatic creation trade-offs
- When to use each tool type
- Configuration best practices

---

### Module 3: Multi-Agent Orchestration Patterns ⏱️ 35 minutes

**Topics:**
- Why multi-agent systems for complex problems
- MAF orchestration primitives (BaseAgent, Workflow, Middleware)
- Four core orchestration patterns with use cases
- Pattern selection criteria

**Subtopics:**

**1. Sequential Pattern** (Dependency chains, step-by-step processing)
- Example: Document Processing Pipeline (Extract → Validate → Enrich → Publish)
- Code walkthrough: `workflow-samples/sequential/`
- When to use: Linear workflows with dependencies

**2. Concurrent Pattern** (Parallel execution for independent tasks)
- Example: Product Launch Advisory (5 specialists analyze simultaneously)
- Benefits: 5x latency reduction, comprehensive multi-perspective analysis
- When to use: Independent tasks, speed critical

**3. Handoff Pattern** (Dynamic routing and specialization)
- Example: IT Support System (Triage → Route to specialist → Escalate)
- Context preservation across handoffs
- When to use: Routing, domain specialization

**4. Magentic Pattern** (Collaborative problem-solving, iterative refinement)
- Example: Technical Architecture Design (Propose → Critique → Refine → Repeat)
- Emergent solutions through collaboration
- When to use: Complex problem-solving, creative tasks

**Pattern Selection Guide:**
- Comparison table: Use case, complexity, latency characteristics
- Decision tree for pattern selection

**Live Demonstration:**

**Demo 4: Product Launch Advisory System** (15 minutes)
- Architecture: 5-agent concurrent orchestration
  - DevUI Backend (port 8092): Manages ChatAgent instances
  - Streamlit Dashboard (port 8095): Interactive UI
- Start system and show architecture
- Demonstrate agents:
  - Market_Researcher: Market analysis, competition
  - Marketing_Strategist: Go-to-market strategy
  - Legal_Compliance_Advisor: Regulatory compliance
  - Financial_Analyst: Business model, ROI
  - Technical_Architect: System design, scalability
- Test scenario: "Telemedicine Platform Launch"
- Show concurrent execution in real-time
- Compare responses from different perspectives
- Demonstrate other scenarios (e-bikes, smart irrigation, AI learning)
- Show auto-refresh and threading architecture
- Discuss concurrent vs. sequential performance

**Discussion:**
- Real-world orchestration applications
- Scaling considerations
- Error handling strategies

---

### Module 4: Production Deployment & Best Practices ⏱️ 20 minutes

**Topics:**
- Observability and monitoring with OpenTelemetry
- Testing strategies and quality assurance
- Deployment options and scaling
- Security best practices

**Subtopics:**

**Observability** (8 minutes)
- Built-in tracing capabilities
- What gets traced: latency, tokens, tool invocations, errors
- Cost monitoring and optimization

**Live Demonstration:**

**Demo 5: Tracing Visualization**
- Show Jaeger/Zipkin traces
- Agent execution spans
- LLM API call latency breakdown
- Function tool execution time
- Total workflow duration
- Error propagation paths
- Token consumption metrics

**Testing & QA** (6 minutes)
- Testing pyramid: Unit → Integration → Evaluation
- Quality metrics: accuracy, relevance, coherence, latency, cost

**Live Demonstration:**

**Demo 6: Verification Test Suite**
- Run: `python AQ-CODE/verify_agent_framework.py`
- Show 11 test categories
- Review test results and coverage
- Discuss evaluation strategies

**Deployment** (6 minutes)
- Deployment options comparison: Container Apps, AKS, Functions, App Service
- Best use cases for each option

**Live Demonstration:**

**Demo 7: Docker Containerization**
- Walkthrough: `AQ-CODE/Dockerfile`
- Show container build process
- Review deployment script: `AQ-CODE/deploy-to-azure.sh`
- Discuss Azure Container Apps deployment
- Environment variable management
- Managed identity configuration

**Production Best Practices:**
- Security: Managed identity, Key Vault, content filtering, RBAC
- Scalability: Horizontal scaling, rate limiting, caching, async processing
- Reliability: Retry middleware, circuit breakers, graceful degradation

---

### Module 5: Real-World Applications & Q&A ⏱️ 15 minutes

**Topics:**
- Industry-specific multi-agent applications
- Teradata-focused use cases
- Common questions and troubleshooting

**Real-World Use Cases:** (10 minutes)

**1. Data Warehousing Advisory System** (Teradata-Specific)
- Agents: Migration Planner, Performance Optimizer, Compliance Auditor, Cost Estimator, Integration Architect
- Pattern: Sequential → Concurrent → Synthesis
- Benefits: 24/7 availability, consistent best practices, comprehensive analysis

**2. Customer Support Automation**
- Agents: Triage, Technical Support, Account Manager, Knowledge Base, Escalation
- Pattern: Handoff with context preservation
- Metrics: 60% auto-resolution, 40% reduced resolution time

**3. Document Intelligence Pipeline**
- Agents: Extractor, Validator, Compliance Checker, Risk Assessor, Classifier
- Pattern: Sequential with parallel branches
- Tools: Code Interpreter, File Search, OpenAPI integration

**4. Financial Analysis Platform**
- Agents: Market Analyzer, Risk Assessor, Report Generator, Alert Manager, Trading Advisor
- Pattern: Concurrent → Sequential synthesis
- Integration: Real-time data feeds, statistical analysis

**5. Intelligent DevOps Assistant**
- Agents: Log Analyzer, Metrics Analyzer, Root Cause Investigator, Remediation Advisor, Documentation
- Pattern: Concurrent detection → Sequential investigation
- Automation: Incident response, runbook generation

**Q&A Session:** (5 minutes)

**Common Questions:**
- Azure AI Foundry vs. Azure OpenAI agents: When to use each?
- Migration from LangChain/Semantic Kernel/AutoGen
- Cost breakdown and optimization strategies
- Error handling and retry strategies
- Debugging orchestration flows
- Data privacy and security compliance (HIPAA, GDPR, SOC 2)

---

## Workshop Format Benefits

### Demo-Driven Advantages
✅ **No Setup Required:** Participants can focus on learning without technical setup  
✅ **Consistent Experience:** Everyone sees the same demonstrations  
✅ **Larger Groups:** Scales better for multiple participants  
✅ **Faster Pace:** No waiting for individual lab completion  
✅ **Expert Guidance:** Instructor can highlight best practices in real-time  
✅ **Q&A Flexibility:** More time for questions and discussion

### What Participants Will See
- Live portal navigation and agent creation
- Real code execution and outputs
- Multi-agent system running concurrently
- Tracing and monitoring dashboards
- Deployment automation scripts
- Test suite execution

### Post-Workshop Support
- Complete workshop documentation (25+ pages)
- All demonstration code from repository
- Setup guide for independent exploration
- Links to Microsoft Learn tutorials
- Community resources and support channels

---

## Prerequisites

**Required:**
- Basic understanding of Python programming
- Familiarity with AI/LLM concepts (prompts, completions, function calling)
- Azure fundamentals (subscriptions, resource groups)

**Optional (helpful but not required):**
- Azure subscription (for post-workshop exploration)
- Experience with REST APIs and web services
- Knowledge of Docker and containerization

**No Setup Required for Workshop:**
- All demonstrations performed by instructor
- Participants can follow along with provided slides
- Code repository access provided for later reference

---

## Comparison: Demo-Driven vs. Hands-On Lab

| Aspect | Demo-Driven | Hands-On Lab |
|--------|-------------|--------------|
| **Participant Setup** | None required | Azure account, Python, IDE |
| **Workshop Pace** | Consistent, instructor-led | Variable, depends on participants |
| **Group Size** | Unlimited | Limited by support capacity |
| **Interaction Style** | Observe and discuss | Implement and experiment |
| **Time for Q&A** | More time available | Less time due to labs |
| **Technical Issues** | Minimal (instructor only) | Potential setup/config issues |
| **Follow-Up Learning** | Self-paced with materials | Continue building PoC |
| **Best For** | Large groups, concept learning | Small groups, hands-on skills |

---

## Questions for Review

Please provide feedback on:

1. **Format Preference:** Would you prefer demo-driven or hands-on lab format?
   - Demo-driven: More participants, faster pace, less setup
   - Hands-on lab: Direct experience, smaller groups, more setup

2. **Content Focus:** Is the balance between theory and demonstrations appropriate?
   - 25 min: Foundations
   - 35 min: Azure AI Foundry agents
   - 35 min: Orchestration patterns
   - 20 min: Production best practices
   - 15 min: Use cases & Q&A

3. **Demonstrations:** Are the 7 live demos covering the right topics?
   - Portal agent creation
   - Python SDK usage
   - Advanced tool integration
   - Multi-agent orchestration
   - Tracing visualization
   - Test suite
   - Docker deployment

4. **Use Cases:** Would you like additional Teradata-specific scenarios?

5. **Audience Size:** How many participants do you anticipate?
   - <10: Either format works well
   - 10-25: Demo-driven recommended
   - 25+: Demo-driven strongly recommended

6. **Follow-Up:** Would you like optional office hours for hands-on support after the workshop?

---

## Next Steps

Please review and provide feedback by **[DATE]**. Let me know:
- Format preference (demo-driven vs. hands-on)
- Any content adjustments
- Participant count
- Specific use cases to emphasize

Once confirmed, I'll:
- Send calendar invites
- Prepare demonstration environment
- Share workshop materials and slides
- Provide repository access for follow-up
- Schedule optional office hours if desired

Looking forward to your thoughts!

Best regards,  
[Your Name]

---

**Quick Reference:**
- **Total Duration:** 2 hours
- **Format:** Lecture + 7 live demonstrations
- **No Participant Setup Required**
- **Materials:** Workshop guide + code repository + Microsoft Learn resources
- **Post-Workshop:** Setup guide for independent exploration

Subject: Microsoft Agent Framework Workshop - Agenda for Review

---

Dear Teradata Team,

I'm excited to share the agenda for our upcoming **Microsoft Agent Framework Workshop** focused on Azure AI Foundry agents. This 2-hour technical session is designed specifically for solution architects and will cover practical, hands-on implementation of multi-agent systems.

Please review the agenda below and let me know if you have any questions or would like to adjust the focus areas.

---

## Workshop Overview
**Title:** Building Multi-Agent Solutions with Azure AI Foundry  
**Duration:** 2 hours  
**Target Audience:** Technical Solution Architects  
**Format:** Hands-on with live demos and interactive labs  

---

## Detailed Agenda

### Module 1: Introduction & Foundations ⏱️ 20 minutes
**Topics:**
- Workshop goals and Microsoft's agent ecosystem overview
- Microsoft Agent Framework (MAF) architecture and components
- Agent types: Azure AI Foundry, Azure OpenAI, Copilot Studio
- Why use MAF: Unified abstraction, orchestration, observability

**Subtopics:**
- BaseAgent and ChatAgent fundamentals
- Framework design principles
- When to use agent-based architecture

---

### Module 2: Azure AI Foundry Agents ⏱️ 35 minutes
**Topics:**
- Azure AI Foundry Agent Service architecture
- Agent components: Models, customization, tools, orchestration
- Creating agents (portal and programmatic)
- Advanced features: Code Interpreter, File Search, Function Calling, OpenAPI integration

**Subtopics:**
- Model deployments (GPT-4o, GPT-4o-mini)
- Built-in tool integration
- Persistent vs. stateless agents
- Authentication and configuration

**Hands-On Labs:**
- **Lab 1:** Create agent in Azure AI Foundry Portal (15 min)
  - Deploy model
  - Configure instructions and persona
  - Add File Search tool
  - Test in playground
  
- **Lab 2:** Programmatic agent creation with Python SDK (10 min)
  - Basic agent with `azure_ai_basic.py`
  - Function tools with `azure_ai_with_function_tools.py`
  - Review environment configuration

**Demos:**
- Exploring sample code from repository
- Tool integration patterns
- Reusing existing agents

---

### Module 3: Orchestration Patterns with MAF ⏱️ 35 minutes
**Topics:**
- Why orchestrate multiple agents
- MAF orchestration primitives (BaseAgent, Workflow, Middleware)
- Four core patterns: Sequential, Concurrent, Handoff, Magentic
- Pattern selection criteria

**Subtopics:**
- **Sequential Pattern:** Dependency chains, step-by-step processing
- **Concurrent Pattern:** Parallel execution for independent tasks
- **Handoff Pattern:** Dynamic routing and specialization
- **Magentic Pattern:** Collaborative problem-solving

**Hands-On Lab:**
- **Lab 3:** Multi-Agent Product Launch Advisory System (15 min)
  - Run 5-agent concurrent system (DevUI backend)
  - Launch Streamlit dashboard
  - Test with pre-loaded scenarios:
    - E-bike subscription service
    - Telemedicine platform
    - Smart irrigation system
    - Smart home security
    - AI-powered learning platform
  - Compare responses from Market Research, Marketing, Legal, Financial, and Technical perspectives

**Discussion:**
- Real-world orchestration use cases
- Performance optimization strategies
- Error handling in multi-agent workflows

---

### Module 4: Production Considerations ⏱️ 20 minutes
**Topics:**
- Observability and tracing with OpenTelemetry
- Testing strategies (unit, integration, evaluation metrics)
- Deployment options (Container Apps, AKS, Functions, App Service)
- Scaling and security best practices

**Subtopics:**
- Built-in tracing capabilities
- Monitoring agent performance and costs
- Docker containerization
- Managed Identity authentication
- Content filtering and security

**Demos:**
- Verification test suite walkthrough
- Deployment script review
- Tracing visualization

---

### Module 5: Real-World Use Cases & Q&A ⏱️ 10 minutes
**Topics:**
- Industry applications for multi-agent systems
- Teradata-specific use case: Data Warehousing Advisory System
- Common questions and troubleshooting

**Subtopics:**
- Migration planning agents
- Customer support automation
- Document intelligence pipelines
- Financial analysis platforms
- Cost optimization strategies
- Framework migration guidance (LangChain, Semantic Kernel, AutoGen)

**Open Discussion:**
- Your specific use cases and requirements
- Technical questions
- Next steps and continued learning

---

## Prerequisites

**Required:**
- Azure subscription with Azure AI Foundry access
- Basic Python programming knowledge
- Familiarity with AI/LLM concepts

**Software:**
- VS Code or similar IDE
- Azure CLI (authenticated with `az login`)
- Python 3.11+ environment

**Optional (will provide during workshop):**
- Workshop repository access
- Sample code and configuration files
- Documentation links

---

## What You'll Learn

By the end of this workshop, you will be able to:
✅ Understand Microsoft Agent Framework architecture  
✅ Create and configure Azure AI Foundry agents  
✅ Implement multi-agent orchestration patterns  
✅ Build interactive agent applications with real scenarios  
✅ Deploy production-ready agent systems  

---

## Workshop Materials

All materials will be shared including:
- Comprehensive workshop guide (25+ pages)
- Sample code and demos from Microsoft's agent-framework repository
- Links to Microsoft Learn documentation
- Hands-on lab instructions
- Docker deployment scripts
- Troubleshooting guide

---

## Questions for Review

Please confirm:
1. **Timing:** Does the 2-hour duration and module breakdown work for your team?
2. **Focus Areas:** Is the balance between Azure AI Foundry agents and orchestration appropriate?
3. **Labs:** Are the hands-on labs aligned with your learning objectives?
4. **Use Cases:** Would you like to explore additional Teradata-specific scenarios?
5. **Technical Level:** Is the intermediate/advanced level suitable for your audience?
6. **Logistics:** Any specific tools, environments, or integrations you'd like to see?

---

## Next Steps

Please review and provide feedback by **[DATE]**. Once confirmed, I'll:
- Send calendar invites
- Provide pre-workshop setup instructions
- Share the repository and access credentials
- Prepare customized demos based on your feedback

Looking forward to your thoughts!

Best regards,  
[Your Name]

---

**Quick Reference:**
- **Total Duration:** 2 hours
- **Hands-On Labs:** 3 interactive sessions (~40 minutes total)
- **Live Demos:** Repository samples, multi-agent dashboard, deployment scripts
- **Materials:** Comprehensive guide + code repository + Microsoft Learn resources

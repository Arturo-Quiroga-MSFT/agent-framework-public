# Teradata Presentation: Microsoft Agent Framework (MAF)
**Duration:** 90 minutes  
**Date:** Monday (upcoming)  
**Audience:** Teradata technical team (Max and team)  
**Presenter:** Arturo Quiroga

---

## 🎯 Presentation Objectives

1. **Position MAF** as the enterprise-grade framework for building production AI agents
2. **Demonstrate** real capabilities with live demos
3. **Connect to Teradata use cases** (data analytics, multi-agent orchestration)
4. **Show the path** from prototype to production
5. **Establish credibility** through technical depth and best practices

---

## 📋 Recommended 90-Minute Structure

### **Part 1: Introduction & Foundation (15 min)**
*Slides 1-5 from pitch deck*

#### Content:
- **Opening (2 min)**: Brief intro, set context for Teradata's data-centric use cases
- **MAF Overview (5 min)**: 
  - What is MAF and why Microsoft built it
  - Key differentiators: Multi-provider, production-ready, open-source
  - Architecture overview (show framework layers)
- **Azure AI Foundry Agents (8 min)**:
  - V2 API (`AzureAIClient`) vs V1 (`AzureAIAgentClient`)
  - Built-in tools: Code interpreter, file search, web search
  - Integration with Azure ecosystem

#### Key Slides to Use:
- MAF positioning slide
- Architecture diagram
- Azure AI Foundry integration points

#### Demo Opportunity:
- **Quick live demo**: Show your simplest `azure_ai_basic.py` running
  - "This is how easy it is to get started"
  - Takes 2 minutes to show agent responding

---

### **Part 2: Multi-Agent Orchestration Patterns (25 min)**
*Slides focused on orchestration + LIVE DEMOS*

#### Content:
- **Orchestration Overview (5 min)**:
  - Sequential, parallel, hierarchical patterns
  - When to use each pattern
  - MAF's orchestration primitives
  
- **DEMO 1: Simple Multi-Agent (10 min)**:
  - Show agent-to-agent communication
  - Use case: Research agent → Analysis agent workflow
  - Highlight: How agents hand off context
  - **File to demo**: `maf-upstream/python/samples/getting_started/agents/azure_ai/azure_ai_with_agent_to_agent.py`
  
- **DEMO 2: Teradata Data Integration (10 min)**:
  - Show agent querying data (use your nl2sql work or similar)
  - Highlight: Function tools calling database
  - Use case: "Natural language to Teradata query"
  - **Files to reference**: Your `AQ-CODE/azure_ai/` examples

#### Key Slides to Use:
- Orchestration pattern diagrams
- Multi-agent architecture
- Data integration patterns

#### Teradata Relevance:
💡 **Call out**: "Imagine agents that can query your Teradata warehouse, analyze results, and generate reports - all through natural language"

---

### **Part 3: Production Deployment & Best Practices (20 min)**
*Slides on enterprise concerns + show production patterns*

#### Content:
- **Production Readiness (8 min)**:
  - Observability & tracing (OpenTelemetry support)
  - Error handling & reliability patterns
  - Cost management & token optimization
  - Security & governance
  
- **DEMO 3: Observability in Action (7 min)**:
  - Show traces and spans
  - Demonstrate error handling
  - **Files to use**: `maf-upstream/python/samples/getting_started/observability/`
  
- **Deployment Options (5 min)**:
  - Azure Container Apps
  - Azure Functions
  - Kubernetes patterns
  - CI/CD integration

#### Key Slides to Use:
- Production architecture diagram
- Observability stack
- Deployment patterns
- Cost optimization strategies

#### Teradata Relevance:
💡 **Call out**: "For enterprise deployments at Teradata's scale, these production patterns are critical"

---

### **Part 4: Real-World Applications & Advanced Patterns (20 min)**
*Show cutting-edge capabilities*

#### Content:
- **Advanced Features (10 min)**:
  - Structured outputs (Pydantic models)
  - RAG patterns (Azure AI Search integration)
  - Code interpreter for data analysis
  - File search for document processing
  
- **DEMO 4: Data Analysis Agent (10 min)**:
  - Show code interpreter analyzing data
  - Or: Show file search with technical docs
  - **Files**: `azure_ai_with_code_interpreter.py` or `azure_ai_with_file_search.py`
  - Make it data-centric for Teradata

#### Key Slides to Use:
- Advanced capabilities showcase
- RAG architecture
- Tool ecosystem diagram

#### Teradata Use Cases to Mention:
1. **Automated Data Analysis**: Agents that write and execute Teradata SQL queries
2. **Documentation Assistant**: Query Teradata documentation via RAG
3. **Data Quality Monitoring**: Multi-agent system monitoring data pipelines
4. **Customer Analytics**: Agents analyzing customer data and generating insights

---

### **Part 5: Q&A and Next Steps (10 min)**

#### Structure:
- Open floor for questions (5 min)
- Next steps & engagement model (3 min):
  - Proof of concept opportunity
  - Technical workshop/deep dive
  - GitHub repo access
  - Support channels
- Closing remarks (2 min)

#### Have Ready:
- GitHub repo link: https://github.com/microsoft/agent-framework
- Your demo repo (if sharing)
- Contact information
- Follow-up resources

---

## 🎬 Demo Preparation Checklist

### **Environment Setup (Before Presentation)**
- [ ] Test all demos in clean environment
- [ ] Have `.env` file configured with credentials
- [ ] Pre-load any required data or files
- [ ] Test network connectivity to Azure
- [ ] Have backup recordings/screenshots ready

### **Demo 1: Basic Agent (Warmup)**
**File**: `maf-upstream/python/samples/getting_started/agents/azure_ai/azure_ai_basic.py`
- [ ] Simple weather function tool
- [ ] Show both streaming and non-streaming
- [ ] Takes 2-3 minutes

### **Demo 2: Agent-to-Agent**
**File**: `maf-upstream/python/samples/getting_started/agents/azure_ai/azure_ai_with_agent_to_agent.py`
- [ ] Show A2A protocol in action
- [ ] Highlight context passing
- [ ] Takes 5-7 minutes

### **Demo 3: Data Integration** (Custom)
**Option A**: Use your `nl2sql-pipeline/` work
**Option B**: Create simple Teradata connector example
- [ ] Show natural language → SQL query
- [ ] Display results formatting
- [ ] Takes 8-10 minutes

### **Demo 4: Observability**
**File**: `maf-upstream/python/samples/getting_started/observability/`
- [ ] Show traces in console or Azure Monitor
- [ ] Demonstrate span details
- [ ] Takes 5-7 minutes

### **Demo 5: Code Interpreter**
**File**: `maf-upstream/python/samples/getting_started/agents/azure_ai/azure_ai_with_code_interpreter.py`
- [ ] Show agent writing Python to analyze data
- [ ] Display generated plots/tables
- [ ] Takes 5-7 minutes

---

## 📊 Slide Selection from Pitch Deck

### **Must-Use Slides (Estimate ~15-20 slides)**

#### Introduction (3-4 slides)
- Title slide
- MAF positioning/value proposition
- Architecture overview
- Azure AI Foundry integration

#### Multi-Agent Orchestration (4-5 slides)
- Orchestration patterns diagram
- Sequential workflow example
- Parallel execution pattern
- Agent-to-agent communication
- Multi-agent architecture

#### Production & Best Practices (4-5 slides)
- Production architecture
- Observability & monitoring
- Deployment options
- Security & governance
- Cost optimization

#### Advanced Features (3-4 slides)
- Advanced capabilities overview
- RAG architecture
- Tool ecosystem
- Enterprise integration points

#### Closing (1-2 slides)
- Summary/key takeaways
- Next steps & contact

### **Slides to SKIP (Keep presentation focused)**
- Deep technical implementation details (unless asked)
- Marketing/positioning slides (keep it technical)
- Competitive comparisons (stay positive)
- Overly detailed API documentation (that's for docs)

---

## 🎨 Presentation Flow Tips

### **Timing Breakdown**
```
0:00-0:15   Part 1: Foundation (slides + quick demo)
0:15-0:40   Part 2: Multi-Agent (slides + 2 demos)
0:40-1:00   Part 3: Production (slides + observability demo)
1:00-1:20   Part 4: Advanced (slides + code interpreter demo)
1:20-1:30   Part 5: Q&A and wrap-up
```

### **Engagement Strategies**

1. **Start with Impact**: Open with a compelling use case
   > "Imagine your data analysts asking questions in plain English and getting SQL queries, results, and visualizations automatically..."

2. **Demo Early and Often**: Don't wait 30 minutes to show something working
   - First demo at minute 10
   - Every 15-20 minutes thereafter

3. **Connect to Teradata Context**: 
   - Reference data analytics scenarios
   - Mention multi-tenant architectures
   - Highlight enterprise scale/security

4. **Pause for Questions**: After each major section, ask:
   > "Any questions on [topic] before we move on?"

5. **Technical Depth Available**: Signal that you can go deeper
   > "I have examples of [X] if you want to dive into that..."

---

## 💡 Teradata-Specific Talking Points

### **Why MAF for Teradata?**

1. **Data-Centric Workflows**
   - Agents that understand and query data warehouses
   - Natural language to SQL translation
   - Automated data analysis and reporting

2. **Enterprise Scale**
   - Multi-tenant agent architectures
   - Observability for production workloads
   - Security and compliance built-in

3. **Multi-Agent for Complex Analytics**
   - Data ingestion → Analysis → Reporting pipelines
   - Parallel query execution across agents
   - Hierarchical orchestration for complex workflows

4. **Integration Flexibility**
   - Connect to Teradata via function tools
   - Use Azure AI Search for hybrid search
   - OpenAPI tools for REST APIs

5. **Production-Ready**
   - Not just a prototype framework
   - Microsoft-supported and enterprise-proven
   - Open-source with active community

---

## 🔧 Technical Preparation

### **Pre-Demo Setup Script**
```bash
# 1. Activate your environment
cd /Users/arturoquiroga/GITHUB/agent-framework-public
source .venv/bin/activate

# 2. Verify dependencies
pip list | grep agent-framework
pip list | grep azure-ai

# 3. Test Azure connection
az account show

# 4. Verify environment variables
echo $AZURE_AI_PROJECT_ENDPOINT
echo $AZURE_AI_MODEL_DEPLOYMENT_NAME

# 5. Test one demo
cd maf-upstream/python/samples/getting_started/agents/azure_ai
python azure_ai_basic.py
```

### **Backup Plans**

1. **If Live Demo Fails**:
   - Have screen recordings ready
   - Have code walkthrough prepared
   - Show logs/outputs from previous runs

2. **If Network Issues**:
   - Have offline slides/diagrams
   - Show code structure and explain
   - Use cached responses if possible

3. **If Time Runs Long**:
   - Skip Demo 4 or 5 (keep most impactful ones)
   - Summarize advanced features instead of showing
   - Offer follow-up deep dive session

---

## 📝 Post-Presentation Follow-Up

### **Materials to Share**

1. **GitHub Links**:
   - Main MAF repo: https://github.com/microsoft/agent-framework
   - Your demo code (if appropriate)

2. **Documentation**:
   - MAF Python docs
   - Azure AI Foundry docs
   - Your comparison documents (V1 vs V2)

3. **Sample Code**:
   - Teradata-specific examples you created
   - Integration patterns
   - Deployment templates

### **Proposed Next Steps**

1. **Technical Workshop** (3-4 hours):
   - Hands-on MAF development
   - Build Teradata integration together
   - Q&A with your team

2. **Proof of Concept**:
   - 2-4 week engagement
   - Build specific use case
   - Technical support included

3. **Architecture Review**:
   - Review Teradata's AI strategy
   - Design multi-agent architecture
   - Deployment planning

---

## ✅ Final Checklist (Day Before)

### **Technical**
- [ ] All demos tested and working
- [ ] Environment variables configured
- [ ] Azure resources provisioned and tested
- [ ] Network connectivity verified
- [ ] Backup recordings prepared

### **Content**
- [ ] Slides reviewed and finalized
- [ ] Demo scripts practiced
- [ ] Timing rehearsed (aim for 75 min, leaving 15 for Q&A)
- [ ] Talking points memorized
- [ ] Teradata use cases prepared

### **Logistics**
- [ ] Meeting link confirmed
- [ ] Screen sharing tested
- [ ] Microphone and camera checked
- [ ] Water nearby
- [ ] Phone on silent
- [ ] Backup computer ready (if possible)

### **Materials**
- [ ] Slide deck on desktop
- [ ] Demo code open in VS Code
- [ ] Terminal windows prepared
- [ ] Browser tabs ready (docs, GitHub, etc.)
- [ ] Notes document open

---

## 🎤 Opening Script (Suggested)

> "Good morning/afternoon everyone, and thank you for joining today's session on the Microsoft Agent Framework.
>
> I'm Arturo Quiroga, and I'm excited to show you how MAF can transform the way you build AI agent applications - particularly for data-intensive scenarios like those you work with at Teradata.
>
> Over the next 90 minutes, we'll cover five key areas: the foundations of MAF, how to work with Azure AI Foundry Agents, multi-agent orchestration patterns, production deployment best practices, and real-world applications. Throughout the session, I'll be showing you live demos and code examples.
>
> This is an interactive session, so please feel free to jump in with questions at any time. With that, let's dive in..."

---

## 🎯 Key Messages to Reinforce

### **Throughout the Presentation, Emphasize:**

1. **Production-Ready**: "MAF is not a toy framework - it's used in production by Microsoft and partners"

2. **Data-Centric**: "Perfect for data analytics use cases - exactly what Teradata excels at"

3. **Multi-Provider**: "Not locked into one AI provider - use Azure OpenAI, Anthropic, local models, etc."

4. **Enterprise Scale**: "Built for the scale and complexity of enterprise deployments"

5. **Open Source**: "Fully open source with active community and Microsoft support"

---

## 🚀 Stretch Goals (If Time Permits)

### **Bonus Demos to Have Ready**

1. **Structured Outputs Demo** (5 min)
   - Show Pydantic model enforcement
   - File: `azure_ai_with_response_format.py`

2. **RAG with Azure AI Search** (7 min)
   - Show semantic or agentic search
   - Files: `azure_ai_with_search_context_*.py`

3. **Browser Automation** (5 min)
   - Show agent browsing the web
   - File: `azure_ai_with_browser_automation.py`

4. **Your Streamlit Demo** (10 min)
   - Show interactive UI
   - File: `AQ-CODE/demos/streamlit_azure_ai_demo.py`

---

## 📧 Sample Follow-Up Email Template

```
Subject: MAF Presentation Follow-Up & Next Steps

Hi Max and team,

Thank you for your time during Monday's Microsoft Agent Framework session. 
I hope you found the content valuable and applicable to Teradata's use cases.

As promised, here are the key resources:

📚 Resources:
- MAF GitHub: https://github.com/microsoft/agent-framework
- Documentation: [link]
- Demo code: [link if sharing]

🎯 Proposed Next Steps:
1. Technical workshop (hands-on MAF development)
2. POC scoping session (identify specific use case)
3. Architecture review (design multi-agent solution)

I'm available for a follow-up discussion to explore which approach 
makes the most sense for Teradata.

Best regards,
Arturo
```

---

## 🎓 Presentation Success Metrics

### **During Presentation**
- [ ] All demos executed successfully
- [ ] At least 5 substantive questions asked
- [ ] Positive body language from audience
- [ ] Engagement throughout (not just at end)

### **Post-Presentation**
- [ ] Follow-up meeting scheduled
- [ ] Technical questions via email
- [ ] Request for additional demos/workshops
- [ ] POC or next engagement discussed

---

## 💪 Confidence Builders

### **You Have Strong Material**
- ✅ Deep technical knowledge of MAF
- ✅ Working code examples and demos
- ✅ Real production experience
- ✅ Understanding of V1 vs V2 (latest knowledge)
- ✅ Multi-agent orchestration patterns
- ✅ Data integration experience

### **Your Unique Strengths**
- You've done the migration research
- You understand the technical details deeply
- You have hands-on code and working examples
- You can go technical or stay high-level as needed

---

## 🎬 Final Thoughts

**Key to Success**: Balance slides, code, and demos
- **Too many slides**: Boring, academic
- **Too much code**: Overwhelming, hard to follow
- **Right mix**: Concept → Code → Demo → Insight

**Remember**: 
- They want to see it WORK, not just hear about it
- Data integration examples will resonate most
- Leave time for their questions and use cases
- Position yourself as ongoing technical resource

**You've got this!** 🚀

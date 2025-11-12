# Workflow-Samples Directory Guide

## Overview

The `/workflow-samples` directory contains **declarative workflow definitions** for the Microsoft Agent Framework. These are YAML-based orchestration patterns that demonstrate different multi-agent collaboration strategies without requiring code.

## Directory Structure

```
workflow-samples/
├── DeepResearch.yaml          # Complex Magentic pattern workflow
├── Marketing.yaml             # Simple Sequential pattern workflow
├── MathChat.yaml              # Handoff pattern workflow
├── HumanInLoop.yaml          # Interactive workflow with human intervention
├── wttr.json                  # Weather API OpenAPI specification
├── README.md                  # Overview and setup instructions
└── setup/                     # Agent definitions and creation scripts
    ├── Create.ps1            # PowerShell script to create all agents
    ├── AnalystAgent.yaml     # Fact analysis agent definition
    ├── ManagerAgent.yaml     # Planning and delegation agent
    ├── CoderAgent.yaml       # Code execution agent (Code Interpreter)
    ├── WeatherAgent.yaml     # Weather API integration (OpenAPI)
    ├── WebAgent.yaml         # Web search agent (Bing Grounding)
    ├── StudentAgent.yaml     # Student agent for MathChat
    ├── TeacherAgent.yaml     # Teacher agent for MathChat
    ├── QuestionAgent.yaml    # General Q&A agent
    └── README.md             # Agent setup documentation
```

## What Are Declarative Workflows?

**Declarative workflows** are YAML-based agent orchestration definitions that:
- Define multi-agent coordination patterns without writing code
- Can be executed locally using the .NET Declarative Workflow demo
- Can be hosted in Azure AI Foundry for production use
- Support complex logic: conditionals, loops, state management, error recovery

### Key Advantages:
✅ **No Coding Required** - Define workflows in YAML  
✅ **Reusable Patterns** - Template-based orchestration  
✅ **Version Control** - Track workflow changes easily  
✅ **Azure Foundry Integration** - Deploy to cloud seamlessly  
✅ **Production Ready** - Built-in error handling and recovery  

---

## Workflow Examples

### 1. Marketing.yaml - Sequential Pattern ⭐ Easy

**Use Case:** Product marketing copy generation

**Pattern:** Sequential (Linear pipeline)

**Agents Required:**
- QuestionAgent (any general-purpose Azure AI Foundry agent)

**Flow:**
```
User Input (Product Description)
    ↓
[Analyst Agent] → Identifies features, audience, USPs
    ↓
[Copywriter Agent] → Creates draft marketing copy
    ↓
[Editor Agent] → Polishes and formats final copy
    ↓
Output: Polished Marketing Copy
```

**Example Input:**
```
"An eco-friendly stainless steel water bottle that keeps drinks cold for 24 hours."
```

**Expected Output:**
```
Polished marketing copy highlighting sustainability, 24-hour insulation, 
target audience (eco-conscious consumers), and unique selling points.
```

**Execution Time:** ~30 seconds

**When to Use:**
- Simple dependency chains
- Step-by-step processing where each step builds on the previous
- Content generation pipelines

---

### 2. MathChat.yaml - Handoff Pattern ⭐⭐ Medium

**Use Case:** Educational tutoring with student-teacher interaction

**Pattern:** Handoff (Conversational loop with role switching)

**Agents Required:**
- StudentAgent (makes intentional mistakes, math skills of 6th grader)
- TeacherAgent (provides guidance, congratulates when done)

**Flow:**
```
User Input (Math Problem)
    ↓
[Student Agent] → Attempts solution with intentional mistakes
    ↓
[Teacher Agent] → Reviews and provides coaching
    ↓
[Student Agent] → Incorporates feedback, tries again
    ↓
[Teacher Agent] → More guidance or congratulations
    ↓
Loop continues for max 4 turns or until "congratulations" detected
    ↓
Output: Complete conversation with learning progression
```

**Example Input:**
```
"If a train travels 60 miles in 45 minutes, what is its speed in mph?"
```

**Expected Conversation:**
```
Turn 1: Student makes calculation error
Turn 2: Teacher points out unit conversion issue
Turn 3: Student corrects approach
Turn 4: Teacher congratulates on correct solution
```

**Execution Time:** ~1-2 minutes

**When to Use:**
- Dynamic routing based on context
- Conversational workflows with turn-taking
- Educational or coaching scenarios
- Iterative refinement with feedback loops

---

### 3. DeepResearch.yaml - Magentic Pattern ⭐⭐⭐ Advanced

**Use Case:** Complex multi-agent research with adaptive planning

**Pattern:** Magentic (Multi-Agent Genetic - collaborative problem-solving with self-correction)

**Agents Required:**
- AnalystAgent (with Bing Grounding tool)
- ManagerAgent (planning and coordination)
- WebAgent (with Bing Grounding for web search)
- CoderAgent (with Code Interpreter for data analysis)
- WeatherAgent (with OpenAPI tool using wttr.json)

**Flow:**
```
User Input (Research Question)
    ↓
[Analyst Agent] → Analyzes facts (given, to look up, to derive, guesses)
    ↓
[Manager Agent] → Creates research plan, assigns team members
    ↓
[Orchestrator] → Tracks progress, detects loops, monitors completion
    ↓
[Specialist Agents] → Execute tasks in parallel based on plan
    ↓
[Manager Agent] → Evaluates progress, decides next steps
    ↓
Loop continues until:
  - Request satisfied ✓
  - OR Stuck in loop → Re-analyze facts & create new plan
  - OR Max restarts exceeded → Stop
    ↓
[Manager Agent] → Synthesizes final comprehensive report
```

**Self-Correction Features:**
- **Loop Detection:** Identifies repeated actions or responses
- **Progress Monitoring:** Evaluates if making forward progress
- **Adaptive Re-planning:** Re-analyzes facts and creates new strategies
- **Restart Mechanism:** Attempts up to 3 restarts before giving up

**Example Input:**
```
"Research the top 3 cities in Europe for digital nomads. Provide current weather 
forecasts and cost of living comparisons."
```

**Expected Execution:**
1. Analyst identifies: need city rankings, weather data, cost metrics
2. Manager assigns: WebAgent (city research), WeatherAgent (forecasts), CoderAgent (cost analysis)
3. Agents execute in parallel
4. Manager synthesizes comprehensive report with rankings, weather, and costs

**Execution Time:** ~2-5 minutes

**When to Use:**
- Complex research requiring multiple data sources
- Problems needing specialized expertise from different agents
- Scenarios requiring adaptive planning and error recovery
- High-value tasks where thoroughness is critical

---

## Prerequisites & Setup

### 1. Environment Configuration

Set these environment variables:

```bash
# Azure AI Foundry Project endpoint
export FOUNDRY_PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project-id>"

# Model deployment name
export FOUNDRY_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"

# Bing Grounding connection name (for web search)
export FOUNDRY_CONNECTION_GROUNDING_TOOL="mybinggrounding"
```

### 2. Azure Authentication

```bash
# Login to Azure
az login

# Verify token
az account get-access-token
```

### 3. Create Agents in Azure AI Foundry

The workflows require agents to be pre-created in your Azure AI Foundry project.

```bash
# Navigate to setup directory
cd workflow-samples/setup

# Run PowerShell creation script
pwsh Create.ps1

# Script outputs environment variable commands like:
# $env:FOUNDRY_AGENT_ANSWER="asst_xxxxx"
# $env:FOUNDRY_AGENT_STUDENT="asst_yyyyy"
# etc.

# Copy and run these commands to set agent IDs
```

**Agents Created:**
- `FOUNDRY_AGENT_ANSWER` - General Q&A agent (used by Marketing workflow)
- `FOUNDRY_AGENT_STUDENT` - Student agent (MathChat)
- `FOUNDRY_AGENT_TEACHER` - Teacher agent (MathChat)
- `FOUNDRY_AGENT_RESEARCHANALYST` - Analyst (DeepResearch)
- `FOUNDRY_AGENT_RESEARCHMANAGER` - Manager (DeepResearch)
- `FOUNDRY_AGENT_RESEARCHWEB` - Web search (DeepResearch)
- `FOUNDRY_AGENT_RESEARCHCODER` - Code execution (DeepResearch)
- `FOUNDRY_AGENT_RESEARCHWEATHER` - Weather API (DeepResearch)

---

## Running Workflows

### .NET Execution (Current)

```bash
# Navigate to demo project
cd dotnet/samples/GettingStarted/Workflows/Declarative/ExecuteWorkflow

# Option 1: Run by workflow name (searches /workflow-samples)
dotnet run Marketing

# Option 2: Run by full path
dotnet run /Users/arturoquiroga/GITHUB/agent-framework-public/workflow-samples/Marketing.yaml

# Option 3: Run with custom workflow
dotnet run /path/to/your/custom-workflow.yaml
```

### Python Execution (Coming Soon)

According to the README, Python support is "in the works" - not yet available as of November 2025.

---

## Demo Scenarios

### Scenario 1: Marketing Copy Generation (Sequential)

**Objective:** Generate polished marketing copy for a product

**Steps:**
```bash
# 1. Run Marketing workflow
cd dotnet/samples/GettingStarted/Workflows/Declarative/ExecuteWorkflow
dotnet run Marketing

# 2. When prompted, enter product description:
"A smart home thermostat with voice control, learning algorithms, 
and energy savings of up to 30%"

# 3. Observe sequential flow:
#    - Analyst identifies features, audience, USPs
#    - Copywriter creates draft
#    - Editor polishes final copy

# 4. Review output (polished marketing copy)
```

**Expected Result:**
Professional marketing copy highlighting smart features, ease of use, and cost savings targeted at homeowners.

---

### Scenario 2: Math Tutoring Session (Handoff)

**Objective:** Demonstrate conversational learning with feedback

**Steps:**
```bash
# 1. Run MathChat workflow
dotnet run MathChat

# 2. When prompted, enter math problem:
"Calculate 15% of 240"

# 3. Observe conversation:
#    Turn 1: Student makes mistake (e.g., forgets to divide by 100)
#    Turn 2: Teacher points out error
#    Turn 3: Student corrects calculation
#    Turn 4: Teacher congratulates

# 4. Review complete learning conversation
```

**Expected Result:**
4-turn conversation showing student learning from mistakes with teacher guidance, ending with correct answer and congratulations.

---

### Scenario 3: Multi-Source Research (Magentic)

**Objective:** Comprehensive research using multiple specialized agents

**Steps:**
```bash
# 1. Run DeepResearch workflow
dotnet run DeepResearch

# 2. When prompted, enter research question:
"What are the best outdoor activities in Seattle this weekend based 
on the weather forecast?"

# 3. Observe complex orchestration:
#    - Analyst: Identifies need for weather data and activity recommendations
#    - Manager: Creates plan (WeatherAgent + WebAgent)
#    - WeatherAgent: Gets Seattle forecast
#    - WebAgent: Searches for outdoor activities
#    - Manager: Synthesizes recommendations based on weather

# 4. If agents get stuck:
#    - System detects loop/no progress
#    - Re-analyzes facts
#    - Creates new plan
#    - Retries with different approach

# 5. Review comprehensive research report
```

**Expected Result:**
Detailed report with:
- Current Seattle weather forecast
- Suitable outdoor activities based on conditions
- Timing recommendations
- Safety considerations

---

## Key Workflow Concepts

### Actions (Building Blocks)

Workflows are composed of action steps:

```yaml
- kind: InvokeAzureAgent          # Call an agent
- kind: SetVariable                # Store data
- kind: ConditionGroup             # If-then logic
- kind: SendActivity               # Display message
- kind: GotoAction                 # Jump to another action (loops)
- kind: ParseValue                 # Parse JSON responses
- kind: CreateConversation         # Start new conversation thread
- kind: EndConversation            # Terminate workflow
```

### Variables

```yaml
# System variables
System.ConversationId              # Current conversation ID
System.LastMessage.Text            # Last user message

# Local variables (custom)
Local.InputTask                    # User input
Local.Plan                         # Generated plan
Local.TurnCount                    # Loop counter
Local.AgentResponse               # Agent output
```

### Expressions

Power Fx expressions for dynamic values:

```yaml
# Concatenation
value: ="Hello " & Local.UserName

# Conditionals
condition: =Local.TurnCount < 4

# Functions
value: =Concat(Local.Items, name, ",")
value: =Last(Local.Messages).Text
value: =CountRows(Local.Agents)
```

### Error Handling Patterns

**Loop Detection:**
```yaml
- kind: ConditionGroup
  conditions:
    - condition: =Local.TypedProgressLedger.is_in_loop.answer
      actions:
        - kind: SendActivity
          activity: "Detected loop, re-planning..."
```

**Progress Monitoring:**
```yaml
- condition: =Not(Local.TypedProgressLedger.is_progress_being_made.answer)
  actions:
    - kind: SetVariable
      variable: Local.StallCount
      value: =Local.StallCount + 1
```

**Restart Logic:**
```yaml
- condition: =Local.StallCount > 2
  actions:
    - kind: SendActivity
      activity: "Re-analyzing facts..."
    - kind: SetVariable
      variable: Local.RestartCount
      value: =Local.RestartCount + 1
```

---

## Orchestration Pattern Comparison

| Pattern | Workflow | Complexity | Agents | Use Case | Execution Time |
|---------|----------|------------|--------|----------|----------------|
| **Sequential** | Marketing.yaml | Low | 1 (multi-role) | Linear pipelines, content generation | ~30 sec |
| **Handoff** | MathChat.yaml | Medium | 2 | Conversations, routing, coaching | ~1-2 min |
| **Magentic** | DeepResearch.yaml | High | 5 | Complex research, adaptive planning | ~2-5 min |

### When to Use Each Pattern:

**Sequential:**
- ✅ Dependency chains where output of one step feeds the next
- ✅ Content generation pipelines (draft → review → polish)
- ✅ Data transformation workflows (extract → transform → load)
- ❌ Not for: Parallel processing, dynamic routing

**Handoff:**
- ✅ Dynamic routing based on context
- ✅ Conversational workflows with role-switching
- ✅ Escalation scenarios (tier 1 → tier 2 support)
- ❌ Not for: Independent parallel tasks, simple linear flows

**Magentic:**
- ✅ Complex problems requiring multiple specialized agents
- ✅ Research needing diverse data sources
- ✅ Adaptive workflows that self-correct
- ✅ High-value tasks where thoroughness is critical
- ❌ Not for: Simple queries, time-sensitive tasks, cost-sensitive scenarios

---

## Workshop Integration

### Module 3: Orchestration Patterns

**Demo Slot:** 10-15 minutes within Module 3

**Recommended Approach:**

1. **Introduction (2 min):**
   - Explain declarative workflows vs. code-based orchestration
   - Show YAML structure of Marketing.yaml (simple example)

2. **Live Demo: Marketing Workflow (3 min):**
   - Run workflow with product input
   - Show sequential execution in real-time
   - Highlight agent transitions (Analyst → Copywriter → Editor)

3. **Live Demo: MathChat Workflow (4 min):**
   - Run with math problem
   - Show conversational handoff between Student and Teacher
   - Demonstrate feedback loop and termination condition

4. **Discussion: DeepResearch (3 min):**
   - Walk through YAML structure (don't run - too long)
   - Explain Magentic pattern components:
     - Fact analysis
     - Plan creation
     - Progress monitoring
     - Loop detection and recovery
   - Compare to your AQ-CODE multi-agent dashboard (similar concept, different implementation)

5. **Comparison (3 min):**
   - **Declarative (YAML):** Great for standard patterns, no coding, version control
   - **Code-based (Python):** More flexibility, custom logic, debugging tools
   - Show pattern comparison table

**Key Talking Points:**
- ✅ YAML workflows are production-ready without coding
- ✅ Can be hosted in Azure AI Foundry
- ✅ Support complex orchestration (conditionals, loops, error recovery)
- ⚠️ Python support coming soon (currently .NET only)
- ✨ Your AQ-CODE dashboard shows similar patterns implemented in Python

---

## Troubleshooting

### Common Issues

**Issue: "Agent not found"**
```
Error: Unable to find agent with name: FOUNDRY_AGENT_ANSWER

Solution:
1. Verify agents are created: pwsh workflow-samples/setup/Create.ps1
2. Set environment variables output by Create.ps1
3. Check variable names match workflow YAML (Env.FOUNDRY_AGENT_ANSWER)
```

**Issue: "Model deployment not found"**
```
Error: Model deployment 'gpt-4o-mini' not found

Solution:
1. Check deployment name in Azure AI Foundry portal
2. Update environment variable: export FOUNDRY_MODEL_DEPLOYMENT_NAME="<actual-name>"
```

**Issue: "Bing Grounding connection not found"**
```
Error: Connection 'mybinggrounding' not found

Solution:
1. Create Bing Grounding connection in Azure AI Foundry portal
2. Update environment variable: export FOUNDRY_CONNECTION_GROUNDING_TOOL="<connection-name>"
```

**Issue: ".NET SDK not found"**
```
Error: dotnet command not found

Solution:
1. Install .NET 8 SDK: https://dotnet.microsoft.com/download
2. Verify: dotnet --version
```

**Issue: "Workflow stuck in loop"**
```
Workflow repeating same actions multiple times

Solution:
- DeepResearch workflow has built-in loop detection
- It will auto-restart with new plan after 2 stalls
- Max 3 restarts before giving up
- If persistent, check agent instructions and tool availability
```

---

## Extending Workflows

### Creating Custom Workflows

**1. Start with a template:**
```yaml
kind: Workflow
trigger:
  kind: OnConversationStart
  id: my_workflow
  actions:
    - kind: InvokeAzureAgent
      id: invoke_agent_1
      conversationId: =System.ConversationId
      agent:
        name: =Env.FOUNDRY_AGENT_ANSWER
      input:
        additionalInstructions: "Your custom instructions here"
```

**2. Add variables for state:**
```yaml
- kind: SetVariable
  id: set_count
  variable: Local.Counter
  value: 0
```

**3. Add conditional logic:**
```yaml
- kind: ConditionGroup
  id: check_condition
  conditions:
    - condition: =Local.Counter < 5
      actions:
        - kind: InvokeAzureAgent
          # ... agent call
```

**4. Add loops with GotoAction:**
```yaml
- kind: GotoAction
  id: goto_start
  actionId: invoke_agent_1
```

### Best Practices

✅ **Use descriptive IDs:** `invoke_analyst` not `action_1`  
✅ **Add displayName:** Makes debugging easier  
✅ **Set loop limits:** Prevent infinite loops  
✅ **Handle errors:** Use ConditionGroup for error paths  
✅ **Keep variables scoped:** Use `Local.` prefix for clarity  
✅ **Document complex logic:** Add comments in YAML  
✅ **Test incrementally:** Start simple, add complexity gradually  

---

## Resources

### Official Documentation
- [Microsoft Agent Framework - Workflows](https://learn.microsoft.com/en-us/agent-framework/concepts/orchestration)
- [Azure AI Foundry Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)
- [Semantic Kernel Declarative Agents](https://github.com/microsoft/semantic-kernel/tree/main/dotnet/src/Agents/Yaml)

### Repository Locations
- **Workflow Samples:** `/workflow-samples/`
- **Agent Definitions:** `/workflow-samples/setup/`
- **.NET Demo:** `/dotnet/samples/GettingStarted/Workflows/Declarative/ExecuteWorkflow`
- **Python Implementation:** Coming soon

### Related AQ-CODE Examples
- **Python Multi-Agent:** `AQ-CODE/orchestration/concurrent_agents_interactive_devui.py`
- **Streamlit Dashboard:** `AQ-CODE/orchestration/multi_agent_dashboard_concurrent.py`
- **Setup Scripts:** `AQ-CODE/setup-scripts/`

---

## Quick Reference Commands

```bash
# Setup
cd workflow-samples/setup
pwsh Create.ps1                           # Create agents
# Copy and run environment variable commands

# Run workflows
cd dotnet/samples/GettingStarted/Workflows/Declarative/ExecuteWorkflow
dotnet run Marketing                      # Sequential pattern
dotnet run MathChat                       # Handoff pattern
dotnet run DeepResearch                   # Magentic pattern

# Verify configuration
echo $FOUNDRY_PROJECT_ENDPOINT
echo $FOUNDRY_MODEL_DEPLOYMENT_NAME
az account show                           # Check Azure auth
```

---

**Document Version:** 1.0  
**Last Updated:** November 12, 2025  
**Status:** .NET workflows functional, Python support pending

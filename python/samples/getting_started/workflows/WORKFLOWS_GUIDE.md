# Agent Framework Workflows - Complete Guide

## 📋 Overview

This directory contains an extensive collection of workflow patterns and examples for the Microsoft Agent Framework. The code demonstrates sophisticated orchestration capabilities for AI agents and complex business processes, progressing from basic concepts to enterprise-grade patterns.

## 🎯 Quick Start - Learning Path

### **Start Here (_start-here/)**
**Follow this sequence to learn the fundamentals:**

| Order | File | Concepts Covered |
|-------|------|------------------|
| 1️⃣ | `step1_executors_and_edges.py` | Basic building blocks - executors, edges, workflow builder |
| 2️⃣ | `step2_agents_in_a_workflow.py` | Integrating AI agents as workflow nodes |
| 3️⃣ | `step3_streaming.py` | Real-time event processing and streaming |

**Prerequisites:** No external services required for basic examples.

## 🗂️ Directory Structure & Categories

### 🤖 **Agent Integration (`agents/`)**
Advanced patterns for integrating AI agents into workflows:

| Sample | File | Key Features |
|--------|------|--------------|
| **Azure AI Streaming** | `azure_ai_agents_streaming.py` | Real-time Azure AI agents with token streaming |
| **Azure Chat Streaming** | `azure_chat_agents_streaming.py` | Azure Chat agents with event streaming |
| **Custom Agent Executors** | `custom_agent_executors.py` | Build custom agent wrapper executors |
| **Workflow as Agent** | `workflow_as_agent_reflection_pattern.py` | Workflows that behave like agents (reflection pattern) |
| **HITL Workflow Agent** | `workflow_as_agent_human_in_the_loop.py` | Workflow-as-agent with human oversight |

**Key Pattern:**
```python
# Agents as workflow nodes
writer = await agent(name="Writer", instructions="Create content...")
reviewer = await agent(name="Reviewer", instructions="Review content...")

workflow = WorkflowBuilder()
    .set_start_executor(writer)
    .add_edge(writer, reviewer)
    .build()
```

### 💾 **State Management (`checkpoint/`)**
Persistence and resumption capabilities:

| Sample | File | Key Features |
|--------|------|--------------|
| **Checkpoint & Resume** | `checkpoint_with_resume.py` | Save workflow state, inspect, resume execution |
| **HITL Checkpointing** | `checkpoint_with_human_in_the_loop.py` | Checkpointing with human approval gates |
| **Sub-workflow Checkpoints** | `sub_workflow_checkpoint.py` | Nested workflow state management |

**Key Pattern:**
```python
# Create checkpoint, pause, resume later
checkpoint = await workflow.create_checkpoint()
# ... later ...
resumed_workflow = workflow.resume_from_checkpoint(checkpoint)
```

### 🔀 **Control Flow (`control-flow/`)**
Conditional logic and routing patterns:

| Sample | File | Key Features |
|--------|------|--------------|
| **Switch-Case Routing** | `switch_case_edge_group.py` | Conditional branching (spam classifier pattern) |
| **Edge Conditions** | `edge_condition.py` | Dynamic routing based on conditions |
| **Multi-Selection** | `multi_selection_edge_group.py` | Multiple path selection logic |
| **Sequential Processing** | `sequential_executors.py` | Step-by-step execution patterns |
| **Simple Loops** | `simple_loop.py` | Iterative workflow patterns |

**Key Pattern:**
```python
# Conditional routing (like spam detection)
.add_switch_case_edge_group(
    spam_detector,
    [
        Case(condition=lambda x: x.is_spam, target=spam_handler),
        Case(condition=lambda x: x.is_uncertain, target=human_review),
        Default(target=inbox_delivery),
    ],
)
```

### 👤 **Human Integration (`human-in-the-loop/`)**
Interactive workflows requiring human input:

| Sample | File | Key Features |
|--------|------|--------------|
| **Guessing Game** | `guessing_game_with_human_input.py` | Interactive human-agent collaboration |

**Key Pattern:**
```python
# Request human input mid-workflow
@handler
async def request_approval(self, data, ctx):
    request = HumanApprovalRequest(
        prompt="Approve this action?",
        context=data
    )
    await ctx.send_message(request)
```

### ⚡ **Parallelism (`parallelism/`)**
Concurrent processing and aggregation:

| Sample | File | Key Features |
|--------|------|--------------|
| **Fan-out/Fan-in** | `fan_out_fan_in_edges.py` | Parallel processing with result aggregation |
| **Map-Reduce** | `map_reduce_and_visualization.py` | Distributed processing with visualization |
| **Result Aggregation** | `aggregate_results_of_different_types.py` | Combine heterogeneous parallel results |

**Key Pattern:**
```python
# Parallel processing
.add_fan_out_edges(dispatcher, [expert1, expert2, expert3])
.add_fan_in_edges([expert1, expert2, expert3], aggregator)
```

### 🎵 **Orchestration (`orchestration/`)**
Complex multi-agent coordination:

| Sample | File | Key Features |
|--------|------|--------------|
| **Concurrent Agents** | `concurrent_agents.py` | Multiple agents working in parallel |
| **Sequential Agents** | `sequential_agents.py` | Chain of agent processing |
| **Custom Aggregators** | `concurrent_custom_aggregator.py` | Advanced result combination |
| **Magentic Integration** | `magentic*.py` | Integration with Magentic framework |

### 🏗️ **Composition (`composition/`)**
Advanced workflow composition patterns:

| Sample | File | Key Features |
|--------|------|--------------|
| **Sub-workflow Basics** | `sub_workflow_basics.py` | Nested workflow fundamentals |
| **Parallel Sub-workflows** | `sub_workflow_parallel_requests.py` | Concurrent nested workflows |
| **Request Interception** | `sub_workflow_request_interception.py` | Middleware-like patterns |

### 🔍 **Observability (`observability/`)**
Monitoring and debugging capabilities:

| Sample | File | Key Features |
|--------|------|--------------|
| **Tracing Basics** | `tracing_basics.py` | Distributed tracing and monitoring |

### 📊 **Visualization (`visualization/`)**
Workflow visualization and debugging:

| Sample | File | Key Features |
|--------|------|--------------|
| **Concurrent Visualization** | `concurrent_with_visualization.py` | Visual workflow debugging |

### 🗃️ **State Management (`state-management/`)**
Advanced state handling patterns:

| Sample | File | Key Features |
|--------|------|--------------|
| **Shared States** | `shared_states_with_agents.py` | Cross-executor state sharing |

## 🔥 Core Patterns & Capabilities

### 1. **Workflow Building Pattern**
```python
workflow = (
    WorkflowBuilder()
    .set_start_executor(preprocessor)
    .add_edge(preprocessor, analyzer)
    .add_switch_case_edge_group(
        analyzer,
        [
            Case(condition=lambda x: x.is_spam, target=spam_handler),
            Default(target=message_responder),
        ],
    )
    .build()
)
```

### 2. **Executor Definition Patterns**

**Class-based Executor:**
```python
class ContentAnalyzer(Executor):
    @handler
    async def analyze(self, content: str, ctx: WorkflowContext[AnalysisResult]) -> None:
        # Process content
        result = AnalysisResult(...)
        await ctx.send_message(result)
```

**Function-based Executor:**
```python
@executor
async def simple_processor(text: str, ctx: WorkflowContext[str, str]) -> None:
    processed = text.upper()
    await ctx.yield_output(processed)
```

### 3. **Streaming & Events**
```python
# Real-time event processing
events = workflow.run_stream(input_data)
async for event in events:
    if isinstance(event, AgentRunUpdateEvent):
        print(f"{event.executor_id}: {event.data}", end="", flush=True)
    elif isinstance(event, WorkflowOutputEvent):
        print(f"Final output: {event.data}")
```

### 4. **Human-in-the-Loop Integration**
```python
# Define request type
@dataclass
class ApprovalRequest(RequestInfoMessage):
    prompt: str
    decision_context: dict

# Request human input
async def request_approval(data, ctx):
    request = ApprovalRequest(
        prompt="Approve this action?",
        decision_context={"risk_level": "high"}
    )
    await ctx.send_message(request)
```

## 💡 Real-World Use Cases Demonstrated

### 📧 **Email Processing Workflows**
- **Spam Detection:** Multi-stage classification with human review
- **Content Routing:** Conditional delivery based on analysis
- **Response Generation:** Automated replies with approval gates

### 📝 **Content Creation Pipelines**
- **Writer-Reviewer Workflows:** Collaborative content creation
- **Multi-Expert Analysis:** Parallel review by domain experts
- **Iterative Refinement:** Loop-based content improvement

### 🔍 **Research & Analysis Systems**
- **Information Gathering:** Multi-source data collection
- **Expert Consultation:** Parallel expert analysis
- **Report Generation:** Aggregated findings compilation

### 🎮 **Interactive Applications**
- **Human-Agent Games:** Collaborative decision making
- **Approval Workflows:** Quality control processes
- **Training Systems:** Interactive learning experiences

### 🔄 **Data Processing Pipelines**
- **ETL Workflows:** Extract, transform, load patterns
- **Validation Chains:** Multi-stage data quality checks
- **Batch Processing:** Large-scale data transformation

## 🚀 Enterprise Features

### **Production-Ready Capabilities:**
- ✅ **Error Handling:** Comprehensive exception management
- ✅ **Scalable Processing:** Parallel execution patterns
- ✅ **State Persistence:** Checkpointing and resumption
- ✅ **Human Integration:** Approval and oversight workflows
- ✅ **Real-time Streaming:** Live event processing

### **Azure Integration:**
- ✅ **Azure OpenAI:** Native chat model integration
- ✅ **Azure AI Services:** Comprehensive AI capabilities  
- ✅ **Authentication:** Azure CLI and managed identity support
- ✅ **Observability:** Distributed tracing and monitoring

### **Development Experience:**
- ✅ **Type Safety:** Full TypeScript-style typing in Python
- ✅ **Visualization:** GraphViz workflow diagrams
- ✅ **Debugging:** Rich event streaming and inspection
- ✅ **Testing:** Comprehensive example coverage

## 🛠️ Installation & Setup

### **Basic Installation:**
```bash
pip install agent-framework --pre
```

### **With Visualization Support:**
```bash
pip install agent-framework[viz] --pre
```

### **GraphViz (for diagrams):**
```bash
# macOS
brew install graphviz

# Ubuntu/Debian  
sudo apt install graphviz

# Windows
# Download from: https://graphviz.org/download/
```

### **Azure Prerequisites:**
1. **Azure CLI Login:** `az login`
2. **Environment Variables:**
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY` or use managed identity
   - `AZURE_AI_PROJECT_ENDPOINT` (for Azure AI services)

## 🎯 Getting Started Recommendations

### **For Beginners:**
1. Start with `_start-here/step1_executors_and_edges.py`
2. Progress through the numbered steps
3. Explore `control-flow/` examples for routing patterns

### **For Agent Integration:**
1. Review `agents/azure_ai_agents_streaming.py`
2. Study `agents/custom_agent_executors.py` for customization
3. Explore `orchestration/` for multi-agent patterns

### **For Production Use:**
1. Study `checkpoint/` for state management
2. Review `human-in-the-loop/` for approval workflows  
3. Examine `observability/` for monitoring patterns

### **For Advanced Patterns:**
1. Explore `composition/` for nested workflows
2. Study `parallelism/` for performance optimization
3. Review `state-management/` for complex state handling

## 📚 Additional Resources

### **Sample Data Files (`resources/`):**
- `email.txt` - Sample email content
- `spam.txt` - Spam email examples  
- `ambiguous_email.txt` - Edge case examples
- `long_text.txt` - Performance testing content

### **Key Concepts to Master:**
- **Executors:** Units of work in workflows
- **Edges:** Connections between executors  
- **Context:** Per-run state and messaging
- **Streaming:** Real-time event processing
- **Checkpointing:** State persistence and resumption
- **Fan-out/Fan-in:** Parallel processing patterns

---

*This documentation covers the comprehensive Agent Framework Workflows sample collection - from basic concepts to enterprise-grade AI orchestration patterns.*
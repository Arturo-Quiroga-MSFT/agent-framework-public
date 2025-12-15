# Semantic Kernel to Agent Framework Migration Guide for Profisee

**Prepared for**: Profisee SK → AF Migration Workshop  
**Author**: Arturo Quiroga  
**Date**: December 15, 2025  
**Framework Versions**: Semantic Kernel 1.38+ → Agent Framework 1.0+

---

## Executive Summary

This guide provides comprehensive migration patterns from **Semantic Kernel (SK)** to **Microsoft Agent Framework (AF)** based on production implementations including the NL2SQL pipeline and real-world enterprise patterns. Agent Framework represents Microsoft's next-generation agentic platform with simplified APIs, better performance, and unified multi-agent orchestration.

### Key Benefits of Migration

✅ **Simplified API** - Reduced complexity and boilerplate code  
✅ **Better Performance** - Optimized object creation and memory usage  
✅ **Unified Interface** - Consistent patterns across AI providers  
✅ **Enhanced Developer Experience** - More intuitive and discoverable APIs  
✅ **Advanced Orchestration** - Built-in workflows (Sequential, GroupChat, Concurrent, Magentic, Handoff)  
✅ **Backward Compatibility** - Can reuse existing `KernelFunction` implementations via compatibility layer

---

## Table of Contents

1. [Package & Import Updates](#1-package--import-updates)
2. [Agent Type Consolidation](#2-agent-type-consolidation)
3. [Agent Creation Simplification](#3-agent-creation-simplification)
4. [Thread Management](#4-thread-management)
5. [Tool Registration](#5-tool-registration)
6. [Invocation Patterns](#6-invocation-patterns)
7. [Options Configuration](#7-options-configuration)
8. [Multi-Agent Orchestration](#8-multi-agent-orchestration)
9. [Real-World Example: NL2SQL Pipeline](#9-real-world-example-nl2sql-pipeline)
10. [Migration Checklist](#10-migration-checklist)

---

## 1. Package & Import Updates

### Semantic Kernel

```python
# Installation
pip install semantic-kernel

# Imports
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function
```

### Agent Framework

```python
# Installation (all packages)
pip install agent-framework --pre

# Installation (selective - recommended)
pip install agent-framework-core --pre              # Core only
pip install agent-framework-azure-ai --pre          # + Azure AI
pip install agent-framework-copilotstudio --pre     # + Copilot Studio

# Imports
from agent_framework import ChatAgent, ChatMessage, Role
from agent_framework.openai import OpenAIChatClient
from agent_framework.azure import AzureOpenAIChatClient, AzureAIAgentClient
from agent_framework._tools import ai_function
```

**Key Differences**:
- AF uses **modular package structure** but **unified imports** (`from agent_framework import ...`)
- No `Kernel` object required in AF
- Simpler import paths for common types

---

## 2. Agent Type Consolidation

### Semantic Kernel

Multiple specialized agent classes for different services:

```python
from semantic_kernel.agents import (
    ChatCompletionAgent,      # For chat completion services
    AzureAIAgent,             # For Azure AI
    OpenAIAssistantAgent,     # For OpenAI Assistants
    AzureResponsesAgent,      # For Azure Responses
    CopilotStudioAgent,       # For Copilot Studio
)
```

### Agent Framework

**Unified `ChatAgent`** works with all `ChatClient`-based services:

```python
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient, OpenAIResponsesClient
from agent_framework.azure import (
    AzureOpenAIChatClient,
    AzureOpenAIResponsesClient,
    AzureAIAgentClient,
)
from agent_framework.microsoft import CopilotStudioAgent

# All use the same ChatAgent pattern
agent = ChatAgent(chat_client=OpenAIChatClient(), instructions="...")
agent = ChatAgent(chat_client=AzureOpenAIChatClient(), instructions="...")
agent = ChatAgent(chat_client=OpenAIResponsesClient(), instructions="...")
```

**Benefits**:
- **Single agent type** for most scenarios
- **Swap chat clients** without changing agent code
- **Consistent API** across providers

---

## 3. Agent Creation Simplification

### Semantic Kernel

Every agent depends on a `Kernel` instance:

```python
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

kernel = Kernel()  # Required even if empty

agent = ChatCompletionAgent(
    kernel=kernel,
    service=OpenAIChatCompletion(),
    name="Support",
    instructions="Answer in one sentence.",
)
```

### Agent Framework

**Two creation methods** - no Kernel required:

**Method 1: Direct construction**
```python
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

agent = ChatAgent(
    chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
    name="Support",
    instructions="Answer in one sentence.",
)
```

**Method 2: Convenience factory method**
```python
from agent_framework.openai import OpenAIChatClient

agent = OpenAIChatClient().create_agent(
    name="Support",
    instructions="Answer in one sentence.",
)
```

**Benefits**:
- No boilerplate `Kernel` object
- More discoverable API
- Cleaner code

---

## 4. Thread Management

### Semantic Kernel

**Manual thread creation** - caller must know thread type:

```python
from semantic_kernel.agents import ChatHistoryAgentThread

thread = ChatHistoryAgentThread()  # Must create manually

response = await agent.get_response(
    messages="How do I reset my bike tire?",
    thread=thread
)
thread = response.thread  # Thread returned in response
```

### Agent Framework

**Agent-managed threads** - let the agent create appropriate thread type:

```python
agent = ...
thread = agent.get_new_thread()  # Agent creates correct thread type

response = await agent.run("How do I reset my bike tire?", thread)
# Thread is automatically managed
```

**Thread Creation Logic**:

1. **Service-side threads**: If agent has `thread_id` set, creates hosted thread (Azure AI, OpenAI Assistants)
2. **Store-backed threads**: If `chat_message_store_factory` is set, creates persistent in-memory thread
3. **Uninitialized threads**: Adapts based on usage (in-memory or service)

**Important**: AF doesn't have universal thread deletion API (not all providers support it). Use provider SDK directly if needed:

```python
# Example: OpenAI Assistants thread deletion
# Use OpenAI SDK directly when needed
import openai
client = openai.OpenAI()
client.beta.threads.delete(thread_id)
```

---

## 5. Tool Registration

### Semantic Kernel

**Multi-step process**: Decorator → Plugin → Kernel → Agent

```python
from semantic_kernel.functions import kernel_function

class SpecialsPlugin:
    @kernel_function(name="specials", description="List daily specials")
    def specials(self) -> str:
        return "Clam chowder, Cobb salad, Chai tea"

# Must add to kernel first
kernel.add_plugin(SpecialsPlugin(), plugin_name="menu")

agent = ChatCompletionAgent(
    kernel=kernel,  # Agent gets tools via kernel
    service=OpenAIChatCompletion(),
    name="Host",
    instructions="Answer menu questions accurately.",
)
```

### Agent Framework

**Single-step registration** - directly on agent:

```python
from typing import Annotated

# Option 1: Simple function
def get_weather(location: Annotated[str, "The location to get the weather for."]) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is sunny."

agent = chat_client.create_agent(
    tools=[get_weather]  # Direct registration
)

# Option 2: With decorator for more control
from agent_framework import ai_function

@ai_function(name="weather_tool", description="Retrieves weather information")
def get_weather(location: Annotated[str, "The location to get the weather for."]) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is sunny."

agent = chat_client.create_agent(tools=[get_weather])

# Option 3: Class-based tools (like SK plugins)
class WeatherPlugin:
    def get_weather(self, location: str) -> str:
        """Get the weather for a given location."""
        return f"The weather in {location} is sunny."
    
    def get_forecast(self, location: str) -> str:
        """Get 7-day forecast."""
        return f"The forecast for {location} is sunny all week."

plugin = WeatherPlugin()
agent = chat_client.create_agent(
    tools=[plugin.get_weather, plugin.get_forecast]
)
```

**Tools parameter locations**:
- Agent creation: `create_agent(tools=[...])`
- Agent run: `agent.run(..., tools=[...])`
- Direct client: `client.get_response(..., tools=[...])`

---

### Backward Compatibility: Using KernelFunction as AF Tools

**Critical for migration**: You can reuse existing SK `KernelFunction` implementations!

Requires: `semantic-kernel` version **1.38+**

#### Example 1: KernelFunction from Prompt Template

```python
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from agent_framework.openai import OpenAIResponsesClient

# Create SK kernel and function
kernel = Kernel()
kernel.add_service(OpenAIChatCompletion(service_id="default"))

kernel_function = KernelFunctionFromPrompt(
    description="Determine the kind of day based on current time",
    plugin_name="TimePlugin",
    function_name="kind_of_day",
    prompt_template="Today is: {{time.date}}\nIs it morning, afternoon, or evening?",
)

# Convert to AF tool
agent_tool = kernel_function.as_agent_framework_tool(kernel=kernel)

# Use with AF agent
agent = OpenAIResponsesClient(model_id="gpt-4o").create_agent(tools=[agent_tool])
response = await agent.run("What kind of day is it?")
```

#### Example 2: KernelFunction from Method

```python
from semantic_kernel.functions import kernel_function
from agent_framework.openai import OpenAIResponsesClient

# Existing SK function
@kernel_function(name="get_weather", description="Get the weather for a location")
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny."

# Convert to AF tool
agent_tool = get_weather.as_agent_framework_tool()

# Use with AF agent
agent = OpenAIResponsesClient(model_id="gpt-4o").create_agent(tools=[agent_tool])
response = await agent.run("What's the weather in Seattle?")
```

#### Example 3: VectorStore Integration

```python
from semantic_kernel.connectors.azure_ai_search import AzureAISearchCollection
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding

# Create vector store collection (SK)
collection = AzureAISearchCollection[str, HotelSampleClass](
    record_type=HotelSampleClass,
    embedding_generator=OpenAITextEmbedding()
)

# Create search function
search_function = collection.create_search_function(
    description="Hotel search engine for USA hotels",
    search_type="keyword_hybrid",
    filter=lambda x: x.Address.Country == "USA",
)

# Convert to AF tool
search_tool = search_function.as_agent_framework_tool()

# Use with AF agent
agent = OpenAIResponsesClient(model_id="gpt-4o").create_agent(
    instructions="You are a travel agent that helps find hotels.",
    tools=[search_tool]
)
response = await agent.run("Find me a hotel in Seattle")
```

**Migration Strategy**:
1. Start by converting your SK `KernelFunction` instances to AF tools using `.as_agent_framework_tool()`
2. Gradually rewrite as native AF functions (`@ai_function` or plain functions)
3. Maintain both during transition period

---

## 6. Invocation Patterns

### Non-Streaming

#### Semantic Kernel

**Async iterator pattern** for multiple agent messages:

```python
async for response in agent.invoke(
    messages=user_input,
    thread=thread,
):
    print(f"# {response.role}: {response}")
    thread = response.thread  # Must track thread

# Convenience method for final response
response = await agent.get_response(
    messages="How do I reset my bike tire?",
    thread=thread
)
print(f"# {response.role}: {response.message.content}")
```

#### Agent Framework

**Single response object** with all messages:

```python
response = await agent.run(user_input, thread)

# Access the text result
print("Agent response:", response.text)  # str(response) also works

# All messages created during execution
for message in response.messages:
    print(f"{message.role}: {message.text}")
```

**Key Differences**:
- AF: Method name `run` (not `invoke` or `get_response`)
- AF: Returns `AgentRunResponse` with `text` property and `messages` list
- AF: Thread automatically managed (not returned in response)

---

### Streaming

#### Semantic Kernel

```python
async for update in agent.invoke_stream(
    messages="Draft a 2 sentence blurb.",
    thread=thread,
):
    if update.message:
        print(update.message.content, end="", flush=True)
```

#### Agent Framework

```python
# Option 1: Stream and print
async for update in agent.run_stream(user_input, thread):
    print(update.text, end="", flush=True)

# Option 2: Collect all updates into final response
from agent_framework import AgentRunResponse

updates = []
async for update in agent.run_stream(user_input, thread):
    updates.append(update)
    print(update.text, end="", flush=True)

full_response = AgentRunResponse.from_agent_run_response_updates(updates)
print("\nFull response:", full_response.text)

# Option 3: One-liner to get full response
full_response = AgentRunResponse.from_agent_response_generator(
    agent.run_stream(user_input, thread)
)
```

**Key Differences**:
- AF: Method name `run_stream` (not `invoke_stream`)
- AF: Returns `AgentRunResponseUpdate` objects
- AF: Helper to combine updates into `AgentRunResponse`

---

## 7. Options Configuration

### Semantic Kernel

**Complex options setup** with separate objects:

```python
from semantic_kernel.connectors.ai.open_ai import OpenAIPromptExecutionSettings
from semantic_kernel.functions import KernelArguments

settings = OpenAIPromptExecutionSettings(
    max_tokens=1000,
    temperature=0.7,
    top_p=0.9,
)
arguments = KernelArguments(settings=settings)

response = await agent.get_response(
    user_input,
    thread=thread,
    arguments=arguments
)
```

### Agent Framework

**Direct parameter passing** - no extra objects:

```python
response = await agent.run(
    user_input,
    thread,
    max_tokens=1000,
    temperature=0.7,
    top_p=0.9,
    frequency_penalty=0.5,
)

# Or create ChatOptions object if you prefer
from agent_framework import ChatOptions

options = ChatOptions(
    max_tokens=1000,
    temperature=0.7,
)
response = await agent.run(user_input, thread, options=options)
```

**Benefits**:
- No import of settings classes
- More discoverable via IDE autocomplete
- Can override per call

---

## 8. Multi-Agent Orchestration

### Sequential Orchestration

#### Semantic Kernel

```python
from semantic_kernel.agents import (
    ChatCompletionAgent,
    SequentialOrchestration
)
from semantic_kernel.agents.runtime import InProcessRuntime

writer = ChatCompletionAgent(...)
reviewer = ChatCompletionAgent(...)

orchestration = SequentialOrchestration(
    members=[writer, reviewer],
    agent_response_callback=callback_function,
)

runtime = InProcessRuntime()
runtime.start()

try:
    result = await orchestration.invoke(task=prompt, runtime=runtime)
    final_message = await result.get(timeout=20)
finally:
    await runtime.stop_when_idle()
```

#### Agent Framework

```python
from agent_framework import SequentialBuilder, WorkflowOutputEvent

writer = chat_client.create_agent(
    name="writer",
    instructions="You are a copywriter."
)

reviewer = chat_client.create_agent(
    name="reviewer",
    instructions="You are a reviewer."
)

workflow = SequentialBuilder().participants([writer, reviewer]).build()

# Streaming execution
async for event in workflow.run_stream(prompt):
    if isinstance(event, WorkflowOutputEvent):
        messages = event.data  # List[ChatMessage]
```

**Key Differences**:
- AF: No runtime management needed
- AF: Builder pattern for construction
- AF: Event-based output
- AF: Built-in streaming support

---

### GroupChat Orchestration

#### Semantic Kernel

```python
from semantic_kernel.agents import (
    GroupChatOrchestration,
    GroupChatManager,
)

orchestration = GroupChatOrchestration(
    members=[researcher, planner],
    manager=ChatCompletionGroupChatManager(
        topic="Launch a hackathon",
        service=AzureChatCompletion(credential=credential),
        max_rounds=8,
    ),
    agent_response_callback=callback,
)

runtime = InProcessRuntime()
runtime.start()

try:
    result = await orchestration.invoke(task=task, runtime=runtime)
    final = await result.get(timeout=30)
finally:
    await runtime.stop_when_idle()
```

#### Agent Framework

```python
from agent_framework import GroupChatBuilder

researcher = chat_client.create_agent(
    name="Researcher",
    instructions="Gather facts about hackathons."
)

planner = chat_client.create_agent(
    name="Planner",
    instructions="Create structured action plans."
)

workflow = (
    GroupChatBuilder()
    .set_manager(
        manager=AzureOpenAIChatClient(credential=credential).create_agent(),
        display_name="Coordinator",
    )
    .participants(researcher=researcher, planner=planner)
    .build()
)

async for event in workflow.run_stream(task):
    if isinstance(event, WorkflowOutputEvent):
        print(event.data)
```

---

### Other Orchestration Patterns

Agent Framework includes additional built-in orchestrations:

```python
from agent_framework import (
    ConcurrentBuilder,   # Run agents in parallel
    MagenticBuilder,     # Dynamic agent selection
    HandoffBuilder,      # Agent handoff workflow
)

# Concurrent - run multiple agents simultaneously
workflow = ConcurrentBuilder().participants([physics, chemistry]).build()

# Magentic - manager selects agents dynamically
workflow = (
    MagenticBuilder()
    .set_manager(manager_agent)
    .participants([researcher, coder])
    .max_turns(10)
    .build()
)

# Handoff - agents pass control with handoff conditions
workflow = HandoffBuilder()...
```

---

## 9. Real-World Example: NL2SQL Pipeline

Based on the production NL2SQL implementation in `/NL2SQL-WORK/nl2sql-pipeline/`.

### Architecture

**Sequential Pipeline**: Custom Executors + LLM Agents

```
User Question (Natural Language)
    ↓
[1] Schema Retriever (Executor) ──→ Azure SQL Database
    ↓ [Cached for 100-500x speedup]
    ↓
[2] SQL Generator Agent (LLM) ──→ Azure OpenAI GPT-4
    ↓ Generate SQL from question + schema
    ↓
[3] SQL Validator (Executor)
    ↓ Safety checks & optimization
    ↓
[4] Query Executor (Executor) ──→ Azure SQL Database
    ↓ Execute validated query
    ↓
[5] Results Interpreter Agent (LLM) ──→ Azure OpenAI GPT-4
    ↓ Natural language insights
    ↓
Natural Language Answer + Insights + Data
```

### Key AF Features Used

1. **Custom Executors** for business logic
2. **ChatAgent** for LLM steps
3. **SequentialBuilder** for pipeline
4. **Pydantic models** for type safety
5. **WorkflowContext** for state management

### Custom Executor Example

```python
from agent_framework import Executor, WorkflowContext, handler
from pydantic import BaseModel

class SchemaContext(BaseModel):
    """Database schema information."""
    tables: list[dict]
    connection_id: str

class SchemaRetrieverExecutor(Executor):
    """Retrieves database schema from MSSQL."""
    
    def __init__(self, connection_id: str):
        super().__init__(id="schema_retriever")
        self.connection_id = connection_id
    
    @handler
    async def retrieve_schema(
        self,
        question: str,
        ctx: WorkflowContext[list[ChatMessage]]
    ) -> None:
        """Fetch schema and send to next step."""
        
        # Get schema from database (simplified)
        schema_data = await self._fetch_schema()
        
        # Create context message for next agent
        schema_msg = ChatMessage(
            role=Role.ASSISTANT,
            text=f"Database Schema:\n{schema_data}"
        )
        
        # Send to pipeline
        await ctx.send_message([schema_msg])
    
    async def _fetch_schema(self) -> str:
        """Fetch schema from MSSQL MCP server."""
        # Implementation details...
        pass
```

### Pipeline Construction

```python
from agent_framework import SequentialBuilder
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

# Create chat client
client = AzureOpenAIChatClient(credential=AzureCliCredential())

# Create executors
schema_retriever = SchemaRetrieverExecutor(connection_id="...")
sql_validator = SQLValidatorExecutor()
query_executor = QueryExecutorExecutor(connection_id="...")

# Create LLM agents
sql_generator = client.create_agent(
    name="sql_generator",
    instructions="""You are an expert SQL generator.
    
    Given a user question and database schema, generate a safe SELECT query.
    
    Rules:
    - Use only SELECT statements
    - Include proper JOINs based on schema
    - Use appropriate WHERE clauses
    - Return valid SQL that answers the question
    """,
)

results_interpreter = client.create_agent(
    name="results_interpreter",
    instructions="""You are a data analyst.
    
    Given query results, provide:
    1. Natural language summary
    2. Key insights
    3. Answer to the original question
    """,
)

# Build sequential pipeline
workflow = (
    SequentialBuilder()
    .participants([
        schema_retriever,     # Executor: Get schema
        sql_generator,        # Agent: Generate SQL
        sql_validator,        # Executor: Validate SQL
        query_executor,       # Executor: Execute query
        results_interpreter,  # Agent: Interpret results
    ])
    .build()
)

# Run pipeline
result = await workflow.run("What are the top 10 customers by revenue?")
```

### Migration Benefits Observed

From the NL2SQL implementation:

✅ **80% less boilerplate** compared to SK equivalent  
✅ **No Kernel management** overhead  
✅ **Type-safe executors** with Pydantic  
✅ **Unified orchestration** - Sequential pattern built-in  
✅ **Better observability** - Built-in tracing support  
✅ **Cleaner separation** - Business logic (Executors) vs AI logic (Agents)

---

## 10. Migration Checklist

### Phase 1: Assessment (1-2 weeks)

- [ ] **Inventory SK usage** across codebase
  - List all `ChatCompletionAgent`, `AzureAIAgent`, etc.
  - Identify all `@kernel_function` tools/plugins
  - Document orchestration patterns (if any)
  
- [ ] **Identify dependencies**
  - Which SK packages are used?
  - Any custom SK integrations?
  - VectorStore usage?
  
- [ ] **Review agent instructions**
  - Document all agent prompts/instructions
  - Identify domain-specific rules
  
- [ ] **Map tool/function catalog**
  - List all `KernelFunction` instances
  - Note which are from prompts vs methods
  - Document tool dependencies (databases, APIs, etc.)

### Phase 2: Setup (1 week)

- [ ] **Install AF packages**
  ```bash
  # Development
  pip install agent-framework --pre
  
  # Production (selective)
  pip install agent-framework-core agent-framework-azure-ai --pre
  ```

- [ ] **Configure credentials**
  ```python
  # .env file
  AZURE_OPENAI_ENDPOINT=...
  AZURE_OPENAI_DEPLOYMENT_NAME=...
  ```

- [ ] **Setup authentication**
  ```python
  from azure.identity import AzureCliCredential
  credential = AzureCliCredential()
  ```

### Phase 3: Parallel Implementation (2-4 weeks)

**Strategy**: Implement AF alongside SK, don't replace immediately.

- [ ] **Create AF agents** (parallel to SK)
  ```python
  # Keep SK agent running
  sk_agent = ChatCompletionAgent(...)
  
  # Add AF agent
  af_agent = ChatAgent(
      chat_client=AzureOpenAIChatClient(...),
      instructions=sk_agent.instructions,  # Same instructions
  )
  ```

- [ ] **Migrate tools using compatibility layer**
  ```python
  # Reuse existing KernelFunction
  agent_tool = kernel_function.as_agent_framework_tool(kernel)
  
  af_agent = client.create_agent(tools=[agent_tool])
  ```

- [ ] **A/B test responses**
  ```python
  sk_response = await sk_agent.get_response(question)
  af_response = await af_agent.run(question)
  
  # Compare quality, latency, cost
  assert_equivalent(sk_response, af_response)
  ```

### Phase 4: Native AF Migration (2-4 weeks)

- [ ] **Convert tools to native AF**
  ```python
  # From SK @kernel_function
  @kernel_function(name="get_weather")
  def get_weather(location: str) -> str: ...
  
  # To AF @ai_function or plain function
  @ai_function(name="get_weather")
  def get_weather(location: Annotated[str, "Location"]) -> str: ...
  ```

- [ ] **Remove Kernel dependencies**
  - Delete `Kernel()` instantiation
  - Remove kernel plugin registration
  - Clean up imports

- [ ] **Adopt AF orchestration patterns**
  ```python
  # Replace SK orchestration
  workflow = SequentialBuilder().participants([...]).build()
  ```

- [ ] **Update error handling**
  ```python
  # AF uses different exception types
  try:
      response = await agent.run(...)
  except Exception as e:
      # Handle AF-specific errors
  ```

### Phase 5: Testing & Validation (2-3 weeks)

- [ ] **Unit tests**
  - Test agent creation
  - Test tool invocation
  - Test thread management
  
- [ ] **Integration tests**
  - Test full workflows
  - Test orchestration patterns
  - Test error scenarios
  
- [ ] **Performance testing**
  - Compare latency (SK vs AF)
  - Measure memory usage
  - Monitor token consumption
  
- [ ] **Quality assurance**
  - Validate response quality
  - Check for regressions
  - User acceptance testing

### Phase 6: Cutover (1-2 weeks)

- [ ] **Feature flag rollout**
  ```python
  if USE_AGENT_FRAMEWORK:
      response = await af_agent.run(question)
  else:
      response = await sk_agent.get_response(question)
  ```

- [ ] **Monitor production**
  - Error rates
  - Response times
  - User satisfaction

- [ ] **Remove SK code**
  - Delete SK agent implementations
  - Remove SK package dependencies
  - Clean up dead code

- [ ] **Documentation update**
  - Update developer guides
  - Revise architecture docs
  - Create runbooks

---

## Key Takeaways for Profisee

### 1. **Start with Compatibility Layer**

Don't rewrite everything at once. Use `.as_agent_framework_tool()` to bridge:

```python
# Day 1: Reuse existing SK functions
existing_sk_function = get_customer_data  # KernelFunction
af_tool = existing_sk_function.as_agent_framework_tool(kernel)
af_agent = client.create_agent(tools=[af_tool])

# Later: Gradually convert to native AF
@ai_function
def get_customer_data(...): ...
```

### 2. **Agent Framework is Production-Ready**

Real-world evidence from NL2SQL pipeline:
- **100-500x performance** gains with schema caching
- **3-10s end-to-end latency** for complex pipelines
- **Enterprise security** features (query validation, row limits)
- **Full observability** with OTLP, Application Insights

### 3. **Orchestration is Built-In**

If you're building multi-agent systems, AF provides:
- **Sequential** - Linear pipeline of agents
- **GroupChat** - Managed conversation between agents
- **Concurrent** - Parallel agent execution
- **Magentic** - Dynamic agent selection
- **Handoff** - Conditional agent transitions

### 4. **Simplified API = Faster Development**

Observed productivity gains:
- **50% less code** for equivalent functionality
- **No Kernel management** overhead
- **Better IDE support** with type hints
- **Clearer separation** of concerns (Executors vs Agents)

### 5. **Microsoft's Strategic Direction**

Agent Framework is the future:
- **Active development** - New features shipping monthly
- **First-class Azure integration** - Native Azure AI, Copilot Studio
- **Better performance** - Optimized for production workloads
- **Ecosystem growth** - MCP servers, tool integrations

---

## Resources

### Official Documentation

- **AF Migration Guide**: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/?pivots=programming-language-python
- **AF Repository**: https://github.com/microsoft/agent-framework
- **SK→AF Samples**: https://github.com/microsoft/agent-framework/tree/main/python/samples/semantic-kernel-migration

### Profisee-Specific Resources

- **NL2SQL Pipeline** (Production AF implementation): `/NL2SQL-WORK/nl2sql-pipeline/`
- **Local MAF Code**: `/maf-upstream/python/`
- **This Guide**: `PROFISEE-SK-TO-AF-MIGRATION-GUIDE.md`

### Migration Samples

The official repo includes 30+ side-by-side SK vs AF examples:

1. **Chat Completion** (`chat_completion/`)
   - Basic chat agents
   - Tools and functions
   - Threading and streaming

2. **Azure AI** (`azure_ai_agent/`)
   - Azure AI agents
   - Code interpreter
   - Thread management

3. **OpenAI Assistants** (`openai_assistant/`)
   - Basic assistants
   - Code interpreter
   - Function tools

4. **OpenAI Responses** (`openai_responses/`)
   - Responses API
   - Tools integration
   - Structured output

5. **Orchestrations** (`orchestrations/`)
   - Sequential workflows
   - GroupChat
   - Concurrent execution
   - Magentic patterns
   - Handoff workflows

6. **Copilot Studio** (`copilot_studio/`)
   - Basic agents
   - Streaming

---

## Next Steps for Profisee Workshop

### Pre-Workshop

1. **Share your SK codebase** patterns (anonymized if needed)
2. **List your critical tools/functions** for compatibility assessment
3. **Identify 1-2 pilot agents** for migration demo

### During Workshop

1. **Live migration demo** of one of your agents
2. **Review tool compatibility** using `.as_agent_framework_tool()`
3. **Discuss orchestration needs** (if multi-agent)
4. **Q&A on specific migration challenges**

### Post-Workshop

1. **Pilot project** - Migrate 1-2 low-risk agents
2. **Performance validation** - Compare SK vs AF metrics
3. **Roadmap creation** - Plan phased migration
4. **Ongoing support** - Regular check-ins during migration

---

**Let's make your SK → AF migration smooth and successful! 🚀**

---

*Questions? Contact: Arturo Quiroga*  
*Updated: December 15, 2025*

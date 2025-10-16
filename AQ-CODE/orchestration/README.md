# Orchestration Workflows (DevUI)

This directory hosts multi-agent orchestration workflow examples showcasing different collaboration patterns using the `agent_framework` DevUI. All workflows have been updated to use the **new Microsoft Agent Framework structure** with custom executor classes.

## Workflows

| Workflow | Pattern | Agents | Port | Documentation | Status |
|----------|---------|--------|------|---------------|--------|
| `agtech_food_innovation_sequential_devui.py` | Sequential Pipeline | 7 | 8097 | [AGTECH_WORKFLOW_README.md](AGTECH_WORKFLOW_README.md) | ✅ Updated |
| `ai_governance_model_compliance_devui.py` | Fan-out / Fan-in | 6 | 8096 | - | ✅ Updated |
| `biotech_ip_landscape_devui.py` | Debate + Synthesis | 6 | 8098 | [BIOTECH_IP_WORKFLOW_README.md](BIOTECH_IP_WORKFLOW_README.md) | ✅ Updated |
| `clinical_trial_management_devui.py` | Fan-out / Fan-in | 7 | 8095 | [CLINICAL_TRIAL_WORKFLOW_README.md](CLINICAL_TRIAL_WORKFLOW_README.md) | ✅ Updated |
| `concurrent_agents_devui.py` | Fan-out / Fan-in | 5 | 8093 | [CONCURRENT_AGENTS_WORKFLOW_README.md](CONCURRENT_AGENTS_WORKFLOW_README.md) | ✅ Updated |
| `cybersecurity_incident_triage_devui.py` | Fan-out / Fan-in | 6 | 8095 | [CYBERSECURITY_INCIDENT_WORKFLOW_README.md](CYBERSECURITY_INCIDENT_WORKFLOW_README.md) | ✅ Updated |
| `customer_onboarding_kyc_devui.py` | Sequential + Gated | 5 | 8091 | - | Legacy |
| `healthcare_product_launch_devui.py` | Fan-out / Fan-in | 5 | 8094 | [HEALTHCARE_WORKFLOW_README.md](HEALTHCARE_WORKFLOW_README.md) | ✅ Updated |
| `ml_model_productionization_sequential_devui.py` | Sequential Gate Review | 7 | 8099 | [ML_PRODUCTIONIZATION_WORKFLOW_README.md](ML_PRODUCTIONIZATION_WORKFLOW_README.md) | ✅ Updated |
| `smart_city_infrastructure_devui.py` | Fan-out / Fan-in | 7 | 8096 | [SMART_CITY_WORKFLOW_README.md](SMART_CITY_WORKFLOW_README.md) | ✅ Updated |

> **Note:** Ports are defaults; modify if occupied. Workflows marked "Updated" use the new framework structure with custom `Executor` classes.

## Framework Migration

All workflows have been modernized to use the **new Microsoft Agent Framework (MAF)** patterns:

### Key Changes
- ✅ **Custom Executor Classes**: Replaced `_CallbackAggregator` with proper `Executor` subclasses
- ✅ **Type Annotations**: Proper `WorkflowContext` and `AgentExecutorResponse` typing
- ✅ **WorkflowBuilder Pattern**: Using `add_fan_out_edges()` and `add_fan_in_edges()`
- ✅ **Import Cleanup**: `AgentExecutorRequest` and `AgentExecutorResponse` imported from main module
- ✅ **DevUI Compatible**: All workflows work with DevUI tracing and visualization

### Migration Pattern Example
```python
# OLD PATTERN (deprecated)
from agent_framework._workflows._concurrent import _CallbackAggregator
aggregator = _CallbackAggregator(format_results)

# NEW PATTERN (recommended)
class CustomAggregator(Executor):
    @handler
    async def aggregate(self, results: list[AgentExecutorResponse], ctx: WorkflowContext) -> None:
        formatted_output = format_results(results)
        await ctx.yield_output(formatted_output)

aggregator = CustomAggregator(id="custom_aggregator")
```

## Quick Start

1. **Ensure Azure CLI logged in:**
   ```bash
   az login
   ```

2. **Configure Azure OpenAI** - Populate `AQ-CODE/.env` (or parent) with:
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   ```

3. **(Optional) Enable tracing:**
   - **Console:** `ENABLE_CONSOLE_TRACING=true`
   - **Application Insights:** `APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...`
   - **OTLP:** `OTLP_ENDPOINT=http://localhost:4317`
   - **DevUI Trace Panels:** `ENABLE_DEVUI_TRACING=true`

4. **Run a workflow:**
   ```bash
   # Example: Healthcare product launch
   python AQ-CODE/orchestration/healthcare_product_launch_devui.py
   
   # Example: Cybersecurity incident triage
   python AQ-CODE/orchestration/cybersecurity_incident_triage_devui.py
   
   # Example: ML model production gates
   python AQ-CODE/orchestration/ml_model_productionization_sequential_devui.py
   ```

5. **Access the Web UI** - Open the URL shown in console (e.g., http://localhost:8094) and submit an example scenario from the printed suggestions.

6. **View outputs** - Results are saved to `workflow_outputs/` directory in both TXT and Markdown formats (for applicable workflows).

## Workflow Categories

### 🏥 Healthcare & Biotech
- **Healthcare Product Launch** ([README](HEALTHCARE_WORKFLOW_README.md)) - 5 agents analyze medical devices, health apps, telehealth services
- **Clinical Trial Management** ([README](CLINICAL_TRIAL_WORKFLOW_README.md)) - 7 agents review pharmaceutical trials and medical device studies
- **Biotech IP Landscape** ([README](BIOTECH_IP_WORKFLOW_README.md)) - 6 agents debate + synthesis for patent strategy

### 🛡️ Security & Compliance
- **Cybersecurity Incident Triage** ([README](CYBERSECURITY_INCIDENT_WORKFLOW_README.md)) - 6 responders analyze security incidents with time-boxed actions
- **AI Governance & Model Compliance** - 6 agents assess AI governance, bias, privacy, regulatory compliance

### 🏙️ Infrastructure & Urban Planning
- **Smart City Infrastructure** ([README](SMART_CITY_WORKFLOW_README.md)) - 7 agents analyze urban projects (IoT, sustainability, transportation)
- **AgTech Food Innovation** ([README](AGTECH_WORKFLOW_README.md)) - 7 agents sequential pipeline for agricultural innovation

### 🤖 ML & AI Systems
- **ML Model Productionization** ([README](ML_PRODUCTIONIZATION_WORKFLOW_README.md)) - 7 sequential gates for production readiness review
- **Concurrent Agents** ([README](CONCURRENT_AGENTS_WORKFLOW_README.md)) - 5 agents for general product/business analysis

### 💼 Business & Finance
- **Concurrent Agents** - Generic product launch analysis (researcher, marketer, legal, finance, technical)
- **Customer Onboarding KYC** - Sequential + gated customer verification process

## Patterns Demonstrated

### Sequential Pipeline
**Example:** AgTech Food Innovation  
**Pattern:** Ordered dependency chain where each agent builds on previous analysis  
**When to use:** Steps require cumulative context, later agents need earlier decisions  
**Characteristics:**
- Each agent sees full conversation history
- Linear progression through stages
- Slower but deeper analysis

### Sequential Gate Review
**Example:** ML Model Productionization  
**Pattern:** Explicit chained executors with per-gate visibility  
**When to use:** Production readiness reviews, compliance checkpoints  
**Characteristics:**
- Each gate is a visible executor in DevUI
- Pass/Conditional/Fail status per gate
- Gate table with risks and mitigations

### Fan-out / Fan-in (Concurrent)
**Examples:** Healthcare, Cybersecurity, Clinical Trial, Smart City, Concurrent Agents  
**Pattern:** All agents analyze input simultaneously, results aggregated  
**When to use:** Independent expert opinions, no inter-agent dependencies  
**Characteristics:**
- Parallel execution (faster)
- Each agent sees only user input
- Equal weighting of perspectives

### Debate + Synthesis
**Example:** Biotech IP Landscape  
**Pattern:** Adversarial viewpoints (Pro vs Con) followed by synthesis step  
**When to use:** Need balanced assessment, identify vulnerabilities  
**Characteristics:**
- Pro agent argues FOR patentability/novelty
- Con agent challenges and identifies risks
- Synthesis creates claim taxonomy and risk matrix

## Pattern Comparison

| Aspect | Sequential | Concurrent | Debate + Synthesis |
|--------|-----------|-----------|-------------------|
| **Speed** | Slower | Faster | Medium |
| **Context** | Cumulative | Independent | Independent + Synthesis |
| **Dependencies** | High | None | None (debate), then synthesis |
| **Use Case** | Pipeline, gates | Multi-expert review | Adversarial assessment |
| **DevUI Visualization** | Linear chain | Parallel branches | Branches + aggregator |

## Output Formats

Most workflows support dual-format exports:

### Text Format (.txt)
- Plain text with ASCII art borders
- Section headers with emojis
- Easily readable in terminal or text editor

### Markdown Format (.md)
- Proper Markdown headers and formatting
- Renders nicely in GitHub, VS Code, documentation sites
- Preserves structure for further processing

**Output Location:** `workflow_outputs/<workflow_name>_<timestamp>.[txt|md]`

## Adding a New Workflow

### Option 1: Use Existing Patterns

1. **Duplicate an existing `*_devui.py` file** matching your desired pattern:
   - Concurrent: Use `healthcare_product_launch_devui.py` or `concurrent_agents_devui.py`
   - Sequential: Use `agtech_food_innovation_sequential_devui.py`
   - Gate Review: Use `ml_model_productionization_sequential_devui.py`
   - Debate: Use `biotech_ip_landscape_devui.py`

2. **Customize key components:**
   - Input `BaseModel` with your domain-specific fields
   - Agent instructions and specializations
   - Format function for output structure
   - Port number and entity ID

3. **Follow framework patterns:**
   ```python
   # Dispatcher
   class CustomDispatcher(Executor):
       @handler
       async def dispatch(self, input_data: YourInput, ctx: WorkflowContext) -> None:
           request = AgentExecutorRequest(
               messages=[ChatMessage(Role.USER, text=input_data.description)],
               should_respond=True
           )
           await ctx.send_message(request)
   
   # Aggregator (for concurrent workflows)
   class CustomAggregator(Executor):
       @handler
       async def aggregate(self, results: list[AgentExecutorResponse], ctx: WorkflowContext) -> None:
           formatted_output = format_results(results)
           await ctx.yield_output(formatted_output)
   ```

4. **Structure your output:**
   - Use clear section headings with emojis
   - Save to `workflow_outputs/` directory
   - Support both TXT and Markdown formats
   - Include elapsed time tracking (optional)

5. **Add a README:**
   - Document workflow purpose and pattern
   - List all agents and their specializations
   - Provide example use cases and inputs
   - Include output structure example

### Option 2: Create from Scratch

Use the `WorkflowBuilder` pattern:

```python
builder = WorkflowBuilder()
builder.set_start_executor(dispatcher)

# For concurrent workflows
builder.add_fan_out_edges(dispatcher, agents)
builder.add_fan_in_edges(agents, aggregator)

# For sequential workflows
builder.add_edge(step1, step2)
builder.add_edge(step2, step3)

workflow = builder.build()
```

### Best Practices

✅ **Clear Agent Roles** - Each agent should have a distinct specialization  
✅ **Structured Output** - Use consistent formatting with section headers  
✅ **Example Scenarios** - Provide 5-8 example inputs in the Pydantic model  
✅ **File Persistence** - Save outputs to `workflow_outputs/` for reference  
✅ **Timing Metrics** - Track elapsed time for performance insights  
✅ **Dual Formats** - Export both TXT and Markdown when possible  
✅ **Tracing Support** - Include observability configuration  
✅ **Documentation** - Create a detailed README explaining the workflow  

### Testing Your Workflow

```bash
# Test workflow creation
python -c "from your_workflow import create_workflow; import asyncio; asyncio.run(create_workflow()); print('✅ Workflow creation successful')"

# Test with DevUI
python your_workflow_devui.py

# Access at http://localhost:<YOUR_PORT>
```

## Tracing & Observability

All workflows support multiple tracing backends for debugging and monitoring:

### Console Tracing (Simplest)
```bash
export ENABLE_CONSOLE_TRACING=true
python your_workflow_devui.py
```
Prints traces directly to console output.

### Application Insights
```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=your-key;..."
python your_workflow_devui.py
```
Sends telemetry to Azure Application Insights for production monitoring.

### OTLP (Jaeger/Zipkin)
```bash
export OTLP_ENDPOINT=http://localhost:4317
python your_workflow_devui.py
```
Compatible with any OTLP-compliant receiver (Jaeger, Zipkin, Tempo, etc.).

### DevUI Tracing
```bash
export ENABLE_DEVUI_TRACING=true
python your_workflow_devui.py
```
Shows traces directly in the DevUI web interface.

### Trace Information Captured
- **Workflow Execution:** Start time, end time, elapsed duration
- **Agent Invocations:** Per-agent execution timing
- **Message Flow:** Input/output messages between executors
- **Errors & Exceptions:** Stack traces and error details
- **Custom Spans:** Domain-specific trace spans

## DevUI Features

### Interactive Workflow Visualization
- Real-time agent execution status
- Message flow between executors
- Scrollable output panel with custom styling
- Agent attribution with emojis and colors

### API Access
Every workflow exposes a REST API:
```bash
# Example: Healthcare workflow
curl -X POST http://localhost:8094/v1/workflow_healthcare \
  -H "Content-Type: application/json" \
  -d '{"description": "AI-powered diagnostic tool for diabetic retinopathy"}'
```

### Programmatic Usage
```python
from your_workflow import create_workflow
import asyncio

async def run_analysis():
    workflow = await create_workflow()
    from your_workflow import YourInputModel
    
    result = await workflow.run(YourInputModel(
        description="Your input here"
    ))
    
    outputs = result.get_outputs()
    return outputs[0] if outputs else None

# Run it
output = asyncio.run(run_analysis())
print(output)
```

## Common Port Assignments

| Port Range | Purpose |
|------------|---------|
| 8091-8092 | Customer/Business workflows |
| 8093 | Concurrent Agents (general) |
| 8094 | Healthcare workflows |
| 8095 | Security workflows (Cybersecurity, Clinical Trial) |
| 8096 | Infrastructure workflows (Smart City, AI Governance) |
| 8097 | Agricultural workflows (AgTech) |
| 8098 | IP & Legal workflows (Biotech IP) |
| 8099 | ML/AI workflows (ML Production) |

**Tip:** If a port is occupied, modify the `port` parameter in the `serve()` call.

## Troubleshooting

### Port Already in Use
```bash
# Error: address already in use
# Solution: Either stop the existing process or change the port
python your_workflow.py  # Modify port in serve() call
```

### Azure OpenAI Authentication Errors
```bash
# Error: Authentication failed
# Solution: Ensure Azure CLI is logged in
az login
az account show  # Verify correct subscription
```

### Missing Dependencies
```bash
# Error: ModuleNotFoundError
# Solution: Install the agent framework
pip install -e python/packages/core
```

### Workflow Validation Errors
```bash
# Error: TypeCompatibilityError
# Solution: Check that executor type annotations match
# Dispatchers should send AgentExecutorRequest
# Aggregators should accept list[AgentExecutorResponse]
```

### DevUI Not Opening
```bash
# Issue: Browser doesn't auto-open
# Solution: Manually navigate to the URL shown in console
# Example: http://localhost:8094
```

## Performance Tips

### Concurrent Workflows
- **Faster:** All agents run in parallel (~5-10 agents = ~15-30 seconds)
- **Token Usage:** ~5K input + 15-20K output tokens total
- **Cost:** Similar to sequential but much faster

### Sequential Workflows
- **Slower:** Each agent waits for previous (~7 agents = ~60-90 seconds)
- **Token Usage:** Higher due to cumulative context
- **Cost:** More tokens per agent due to growing conversation

### Optimization Strategies
1. **Use Concurrent Patterns** when agents don't need each other's context
2. **Limit Agent Count** - 5-7 agents optimal for most use cases
3. **Concise Instructions** - Shorter agent instructions = faster responses
4. **Streaming** - Enable streaming for real-time feedback (if supported)
5. **Caching** - Consider response caching for repeated queries

## Future Enhancements

### Planned Features
- ✨ Hierarchical planner issuing sub-prompts (multi-stage execution)
- ✨ Iterative round-based refinement (e.g., disaster response updates)
- ✨ Shared memory artifact store between agents
- ✨ Structured JSON outputs with schema validation
- ✨ Unified utility for timing + markdown export across workflows

### Experimental Ideas
- 🔬 Human-in-the-loop approval gates
- 🔬 Dynamic agent selection based on input classification
- 🔬 Multi-modal input support (images, documents)
- 🔬 Workflow composition (chain multiple workflows)
- 🔬 A/B testing framework for agent instructions

### Community Contributions Welcome
We welcome contributions for:
- New domain-specific workflows (legal, education, logistics, etc.)
- Enhanced visualization components
- Performance optimizations
- Integration with additional LLM providers
- Testing frameworks and benchmarks

## Resources

### Documentation
- [Microsoft Agent Framework Docs](https://github.com/microsoft/agent-framework)
- Individual Workflow READMEs (see links in workflow table above)
- [DevUI Guide](../azure_ai/DEVUI_GUIDE.md)
- [Tracing Guide](../azure_ai/TRACING_GUIDE.md)

### Example Outputs
Check `workflow_outputs/` directory for sample outputs from each workflow.

### Related Projects
- [AutoGen](https://github.com/microsoft/autogen) - Multi-agent conversation framework
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel) - AI orchestration SDK
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** and create a feature branch
2. **Follow the patterns** established in existing workflows
3. **Add tests** if applicable (see test harness in `concurrent_agents_devui.py`)
4. **Create a README** documenting your workflow
5. **Submit a pull request** with clear description

### Contribution Ideas
- 📝 New domain workflows (legal, education, logistics, finance)
- 🎨 Enhanced DevUI visualizations
- ⚡ Performance optimizations
- 🧪 Testing frameworks and benchmarks
- 📚 Documentation improvements

## License

See root `LICENSE` (MIT).

---

**Questions or Issues?** Open an issue or PR on GitHub to contribute new collaboration patterns.

**Updates:** All workflows updated for Microsoft Agent Framework new structure (October 2025)

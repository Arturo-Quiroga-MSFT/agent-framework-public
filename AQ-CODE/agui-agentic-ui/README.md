# Agentic UI - Planning Agent (Python Implementation)

A practical Python implementation of the Agentic UI pattern that demonstrates:
- **AI-generated plans** with structured steps
- **Streaming state updates** using JSON Patch
- **Rich console UI** with progress visualization
- **Tool-based planning** with `@ai_function` decorators

## Features

✨ **Agentic UI Pattern**
- Agent generates structured Plan objects (not just text)
- Plans contain actionable Steps with status tracking
- JSON Patch updates for efficient state synchronization

🎨 **Rich Visual UI**
- Beautiful table-based plan display
- Real-time progress tracking
- Color-coded status indicators
- Step-by-step execution visualization

🔧 **Tool-Based Architecture**
- `create_plan()` - Generate multi-step plans
- `update_step_status()` - Modify individual steps
- JSON Patch operations for incremental updates

## Installation

```bash
# Install dependencies
pip install agent-framework azure-identity rich pydantic

# Set environment variables
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"

# Authenticate with Azure
az login
```

## Quick Start

```bash
cd AQ-CODE/agui-agentic-ui
python planning_agent.py
```

### Example Output

```
🤖 Agentic UI Planning Agent Demo

Available example tasks:
  1. Build a REST API for user management
  2. Set up CI/CD pipeline for a Python project
  3. Migrate database from PostgreSQL to Azure Cosmos DB

Enter task number or custom task: 1

Creating plan for: Build a REST API for user management

📋 User Management REST API Implementation
Design and implement a complete RESTful API for user operations
Plan ID: a3f9c21b

Progress: 0%

┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ # ┃ Step                                 ┃ Status        ┃ Duration   ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1 │ Define API specification (OpenAPI)  │ ⭕ Not Started │ 2 hours    │
│ 2 │ Set up FastAPI project structure    │ ⭕ Not Started │ 1 hour     │
│ 3 │ Implement database models & schemas │ ⭕ Not Started │ 3 hours    │
│ 4 │ Create CRUD endpoints               │ ⭕ Not Started │ 4 hours    │
│ 5 │ Add authentication & authorization  │ ⭕ Not Started │ 3 hours    │
│ 6 │ Implement input validation          │ ⭕ Not Started │ 2 hours    │
│ 7 │ Write unit and integration tests    │ ⭕ Not Started │ 4 hours    │
│ 8 │ Add API documentation               │ ⭕ Not Started │ 1 hour     │
└───┴──────────────────────────────────────┴───────────────┴────────────┘

🚀 Starting plan execution...

Progress: 12.5%
│ 1 │ Define API specification (OpenAPI)  │ 🔄 In Progress │ 2 hours    │
│ 2 │ Set up FastAPI project structure    │ ⭕ Not Started │ 1 hour     │
...
```

## Architecture

### Data Models (`models.py`)

```python
class StepStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Step(BaseModel):
    step_number: int
    description: str
    status: StepStatus
    rationale: Optional[str]
    estimated_duration: Optional[str]

class Plan(BaseModel):
    id: str
    title: str
    description: str
    steps: list[Step]
```

### Agent Tools (`planning_agent.py`)

```python
@ai_function
async def create_plan_tool(
    title: str,
    description: str,
    steps: list[dict]
) -> str:
    """Agent calls this to generate a structured plan."""
    # Creates Plan object with Step objects
    # Returns confirmation to agent
    
@ai_function
async def update_step_status_tool(
    step_number: int,
    status: str
) -> str:
    """Agent calls this to update step status."""
    # Updates specific step
    # Returns confirmation
```

### JSON Patch Updates

```python
# Incremental update (efficient)
JsonPatchOperation(
    op="replace",
    path="/steps/0/status",
    value="completed"
)

# vs Full state replacement (inefficient)
# Send entire plan object again
```

## Use Cases

### 1. Project Planning
```
Task: "Plan a website redesign project"
→ Generates 8-12 step plan
→ UI renders as Kanban board
→ Updates status as steps complete
```

### 2. Database Migration
```
Task: "Migrate from MySQL to PostgreSQL"
→ Creates detailed migration plan
→ Shows progress with each step
→ Validates completion before next step
```

### 3. CI/CD Pipeline Setup
```
Task: "Set up GitHub Actions for Python"
→ Breaks down into configuration steps
→ Tracks setup progress
→ Validates each component
```

## Customization

### Custom Task Examples

```python
# Software Development
"Implement OAuth 2.0 authentication"
"Create microservices architecture for e-commerce"
"Set up Kubernetes cluster with monitoring"

# Data Engineering
"Build ETL pipeline for sales data"
"Implement real-time streaming with Kafka"
"Create data warehouse on Snowflake"

# DevOps
"Configure Azure infrastructure with Terraform"
"Set up observability stack (Prometheus + Grafana)"
"Implement disaster recovery plan"
```

### Extend the Agent

```python
# Add more planning tools
@ai_function
async def add_step_to_plan(
    step_number: int,
    description: str,
    insert_after: int
) -> str:
    """Insert a new step into existing plan."""
    # Implementation

@ai_function
async def estimate_total_duration() -> str:
    """Calculate total estimated time."""
    # Sum up all step durations
```

## Comparison with C# Implementation

| Feature | C# (.NET) | Python |
|---------|-----------|--------|
| **Data Models** | Records | Pydantic Models |
| **JSON Patch** | JsonPatchDocument | Dict/BaseModel |
| **UI** | Blazor/React | Rich Console |
| **Streaming** | IAsyncEnumerable | AsyncIterator |
| **Tools** | AIFunctionFactory | @ai_function |

## Advanced Features

### Real-Time Web UI

To connect this to a web frontend:

```python
# FastAPI server
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/plan")
async def create_plan_endpoint(task: str):
    async def event_stream():
        async for patch in agent.execute_plan_with_updates(plan):
            yield f"data: {patch.model_dump_json()}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

```javascript
// Frontend (React/Vue/Svelte)
const eventSource = new EventSource('/plan');
eventSource.onmessage = (event) => {
    const patch = JSON.parse(event.data);
    applyJsonPatch(currentState, patch);
    updateUI(currentState);
};
```

### Database Persistence

```python
# Save plans to database
async def save_plan(plan: Plan):
    async with get_db_session() as session:
        db_plan = DBPlan(
            id=plan.id,
            title=plan.title,
            data=plan.model_dump_json()
        )
        session.add(db_plan)
        await session.commit()

# Load and resume
async def load_plan(plan_id: str) -> Plan:
    async with get_db_session() as session:
        db_plan = await session.get(DBPlan, plan_id)
        return Plan.model_validate_json(db_plan.data)
```

## Troubleshooting

### Issue: Agent doesn't create a plan

**Solution**: Check that tools are properly registered:
```python
agent = ChatAgent(
    name="PlanningAgent",
    tools=[agent.create_plan_tool, agent.update_step_status_tool]  # ✅
)
```

### Issue: JSON Patch not working

**Solution**: Ensure path format is correct:
```python
# ✅ Correct
path="/steps/0/status"  # Zero-based index for arrays

# ❌ Wrong
path="/steps/1/status"  # Don't use 1-based step numbers
```

### Issue: Display is flickering

**Solution**: Add delays between updates:
```python
await asyncio.sleep(0.5)  # Give time to render
```

## Next Steps

1. **Try it out**: Run the demo with different tasks
2. **Customize**: Add your own planning tools
3. **Integrate**: Connect to a web UI or dashboard
4. **Extend**: Add validation, error handling, rollback

---

**Part of**: AQ-CODE AGUI Enhancements Series  
**Next**: Backend Tool Rendering (Part 2)  
**See Also**: [AGUI_ENHANCEMENTS_GUIDE.md](../docs/AGUI_ENHANCEMENTS_GUIDE.md)

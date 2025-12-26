# Predictive State Updates

**AGUI Enhancement #3**: Stream incremental state changes for real-time UI updates without full page reloads.

## Overview

Predictive State Updates enable agents to stream partial state changes to clients using JSON Patch operations, providing real-time progress visibility and progressive UI rendering. Instead of polling for full state updates, clients receive only the changes as they occur.

## Key Benefits

### 🚀 Performance
- **Reduced Bandwidth**: Only deltas transmitted (80%+ savings vs full state)
- **Lower Latency**: Near real-time updates vs polling intervals
- **Better UX**: Progressive rendering without full reloads
- **Efficient Server**: Push-based (no constant polling load)

### 📊 User Experience
- **Real-time Visibility**: See progress as it happens
- **Perceived Speed**: Updates appear instantly
- **Long Operations**: Better feedback for time-consuming tasks
- **Professional UI**: Smooth, modern progress indicators

## Architecture

```
┌──────────────┐
│    Agent     │ → Executes workflow
└──────┬───────┘
       │ Streams updates
       ↓
┌──────────────┐
│ StateUpdate  │ → JSON Patch operations
└──────┬───────┘
       │ WebSocket/SSE
       ↓
┌──────────────┐
│    Client    │ → Applies updates to local state
└──────────────┘
```

## Data Models

### WorkflowState
Complete state of a workflow execution:
```python
class WorkflowState(BaseModel):
    workflow_id: str
    title: str
    tasks: list[TaskItem]
    overall_progress: int
    current_task_index: int
    started_at: Optional[str]
    completed_at: Optional[str]
```

### TaskItem
Individual task in the workflow:
```python
class TaskItem(BaseModel):
    id: str
    title: str
    status: TaskStatus  # PENDING, ANALYZING, IN_PROGRESS, COMPLETED, FAILED
    progress: int  # 0-100
    result: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
```

### StateUpdate
A single state update with JSON Patch operations:
```python
class StateUpdate(BaseModel):
    timestamp: str
    operations: list[dict[str, Any]]  # JSON Patch ops
    description: str
```

## Implementation

### Basic Streaming

```python
agent = PredictiveStateAgent()

# Stream state updates
async for update in agent.stream_state_updates(workflow):
    # Apply update to local state
    agent.apply_state_update(update)
    
    # Re-render UI
    display(agent.render_state())
```

### JSON Patch Operations

Updates use JSON Patch (RFC 6902) operations:

```python
# Update task status
{
    "op": "replace",
    "path": "/tasks/0/status",
    "value": "in_progress"
}

# Update progress
{
    "op": "replace",
    "path": "/tasks/0/progress",
    "value": 75
}

# Multiple operations in one update
{
    "operations": [
        {"op": "replace", "path": "/tasks/0/status", "value": "completed"},
        {"op": "replace", "path": "/tasks/0/result", "value": "Success"},
        {"op": "replace", "path": "/overall_progress", "value": 50}
    ]
}
```

## Usage

### Running Tests (No Azure credentials required)

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/agui-predictive-state
source /Users/arturoquiroga/GITHUB/agent-framework-public/.venv/bin/activate
python test_predictive_state.py
```

### Running Demo

```bash
python predictive_state_agent.py
```

The demo shows:
1. **Live streaming** of a 5-task deployment workflow
2. **Real-time rendering** with Rich library progress indicators
3. **Bandwidth comparison** vs traditional polling
4. **State transitions** (pending → analyzing → in-progress → completed)

## Example Workflow

A typical workflow execution:

```
Deploy Web Application - 0% Complete
┌──────────────────────────────────────────────────────────────┐
│ Task              Status        Progress        Result       │
├──────────────────────────────────────────────────────────────┤
│ Build Docker image  ⏸️ Pending    —                          │
│ Run security scan   ⏸️ Pending    —                          │
│ Push to registry    ⏸️ Pending    —                          │
│ Deploy to staging   ⏸️ Pending    —                          │
│ Run integration     ⏸️ Pending    —                          │
└──────────────────────────────────────────────────────────────┘

[Updates stream in real-time...]

Deploy Web Application - 60% Complete
┌──────────────────────────────────────────────────────────────┐
│ Task              Status        Progress        Result       │
├──────────────────────────────────────────────────────────────┤
│ Build Docker image  ✅ Done       ██████████ 100%  ✓ Built    │
│ Run security scan   ✅ Done       ██████████ 100%  ✓ Passed   │
│ Push to registry    ✅ Done       ██████████ 100%  ✓ Pushed   │
│ Deploy to staging   ⚙️ Working    ██████░░░░  60%            │
│ Run integration     ⏸️ Pending    —                          │
└──────────────────────────────────────────────────────────────┘
```

## Bandwidth Efficiency

Example for a 5-task workflow with 25 updates:

| Method | Size | Notes |
|--------|------|-------|
| **Traditional Polling** | 12,500 bytes | Full state × 25 polls |
| **Predictive Streaming** | 2,000 bytes | Only deltas × 25 updates |
| **Savings** | **80%** | 10,500 bytes saved |

Additional benefits:
- Lower server CPU (no constant polling)
- Reduced network traffic
- Better mobile experience
- Scalable to more concurrent users

## State Transitions

Tasks follow this lifecycle:

```
PENDING → ANALYZING → IN_PROGRESS → COMPLETED
                           ↓
                        FAILED
```

Each transition triggers a state update:
- **PENDING → ANALYZING**: Agent is planning the task
- **ANALYZING → IN_PROGRESS**: Task execution started
- **IN_PROGRESS**: Progress updates (0% → 25% → 50% → 75% → 100%)
- **COMPLETED**: Task finished with result
- **FAILED**: Task encountered an error

## Integration with Other Enhancements

### + Agentic UI (Enhancement #1)
```python
# Plans can stream step updates
plan = create_plan_tool("Build REST API")
async for update in stream_plan_updates(plan):
    # Update UI with step progress
    display_plan_with_updates(plan, update)
```

### + Backend Tools (Enhancement #2)
```python
# Tool executions can stream progress
@ai_function
async def long_running_tool():
    yield StateUpdate(progress=25, desc="Processing...")
    yield StateUpdate(progress=50, desc="Almost there...")
    yield StateUpdate(progress=100, desc="Done!")
```

## Tuning Parameters

### Chunk Delay
```python
# Fast updates (good for UI responsiveness)
stream_state_updates(workflow, chunk_delay=0.1)

# Moderate updates (balanced)
stream_state_updates(workflow, chunk_delay=0.3)

# Slower updates (reduce bandwidth)
stream_state_updates(workflow, chunk_delay=1.0)
```

### Batching
```python
# Batch multiple operations into one update
StateUpdate(
    operations=[
        {"op": "replace", "path": "/tasks/0/status", "value": "completed"},
        {"op": "replace", "path": "/tasks/0/progress", "value": 100},
        {"op": "replace", "path": "/tasks/0/result", "value": "Success"}
    ]
)
```

## Testing

The test suite validates:
- ✅ **State Models**: WorkflowState, TaskItem, StateUpdate creation
- ✅ **State Streaming**: Async iteration, update generation
- ✅ **State Application**: JSON Patch operations, state mutation
- ✅ **State Rendering**: Rich UI components, live updates
- ✅ **Bandwidth Efficiency**: 80%+ savings vs polling

All tests pass without requiring Azure credentials.

## Comparison: Traditional vs Predictive

| Aspect | Traditional Polling | Predictive Streaming |
|--------|-------------------|---------------------|
| **Update Frequency** | Fixed interval (e.g., 1s) | As changes occur |
| **Bandwidth** | Full state each poll | Only deltas (JSON Patch) |
| **Latency** | Up to polling interval | Near real-time |
| **Server Load** | Constant polling load | Push-based (lower load) |
| **Complexity** | Simple to implement | Requires streaming support |
| **User Experience** | Delayed, jumpy updates | Smooth, immediate updates |

## Production Deployment

### WebSocket Integration
```python
# Server-side
async def handle_websocket(websocket):
    agent = PredictiveStateAgent()
    async for update in agent.stream_state_updates(workflow):
        await websocket.send_json(update.model_dump())

# Client-side (JavaScript)
const ws = new WebSocket('ws://server/workflow');
ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    applyJsonPatch(localState, update.operations);
    renderUI(localState);
};
```

### Server-Sent Events (SSE)
```python
# Server-side
async def stream_updates(request):
    agent = PredictiveStateAgent()
    async for update in agent.stream_state_updates(workflow):
        yield f"data: {update.model_dump_json()}\n\n"

# Client-side (JavaScript)
const eventSource = new EventSource('/workflow/stream');
eventSource.onmessage = (event) => {
    const update = JSON.parse(event.data);
    applyJsonPatch(localState, update.operations);
    renderUI(localState);
};
```

## Files

- `predictive_state_agent.py`: Main implementation with streaming logic
- `test_predictive_state.py`: Comprehensive test suite (5 test categories)
- `README.md`: This file

## Next Steps

- ✅ All three AGUI enhancements now complete!
- Integrate all three enhancements together
- Test with real Azure OpenAI agents
- Deploy in production with WebSocket/SSE transport
- Add error handling and retry logic
- Implement state persistence and recovery

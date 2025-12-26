# AGUI Enhancements Guide - December 2025

**Author**: Arturo Quiroga  
**Date**: December 25, 2025  
**Framework**: Microsoft Agent Framework (MAF) - Latest Upstream  
**Focus**: Agentic UI Protocol New Features

---

## Overview

The **AG-UI Protocol** (Agentic UI) enables AI agents to create rich, interactive user interfaces during conversations, moving beyond simple text responses to structured, stateful UI components.

### What's New (December 2025 Update)

Three major enhancements were added to the upstream Agent Framework:

1. **Agentic UI** - Agents generate plans and UI-renderable structures
2. **Backend Tool Rendering** - Server-side function execution with streaming results
3. **Predictive State Updates** - Real-time progressive state streaming

---

## 1. Agentic UI - Agent-Generated Plans

### Concept

Agents can create structured plans, tasks, and workflows that clients render as interactive UI components (checklists, progress bars, wizards, etc.).

### How It Works

```csharp
// Agent defines planning functions
create_plan()         → Returns Plan object with steps
update_plan_step()    → Updates specific step (using JSON Patch)

// Middleware intercepts these and emits state events
new DataContent(planBytes, "application/json")           // Full plan
new DataContent(patchBytes, "application/json-patch+json") // Incremental update
```

### State Management

```csharp
// Server-side: AgenticUIAgent middleware
internal sealed class AgenticUIAgent : DelegatingAIAgent
{
    // Tracks function calls: create_plan, update_plan_step
    // When results arrive, converts them to DataContent events
    // Client receives JSON or JSON Patch for progressive updates
}
```

### Data Structures

```csharp
public record Plan(
    string Id,
    string Title,
    string Description,
    List<Step> Steps
);

public record Step(
    int StepNumber,
    string Description,
    StepStatus Status,
    string? Rationale
);

public enum StepStatus
{
    NotStarted,
    InProgress,
    Completed,
    Failed
}

// JSON Patch for updates
[
  { "op": "replace", "path": "/steps/0/status", "value": "Completed" }
]
```

### Use Cases

- **Task Management**: Multi-step workflows with status tracking
- **Project Planning**: Break down complex requests into actionable steps
- **Wizards**: Guide users through processes with visual progress
- **Troubleshooting**: Diagnostic steps with pass/fail indicators

### Sample Location

- **Implementation**: `dotnet/samples/AGUIClientServer/AGUIDojoServer/AgenticUI/`
- **Agent**: `AgenticUIAgent.cs`
- **Tools**: `AgenticPlanningTools.cs`
- **Models**: `Plan.cs`, `Step.cs`, `StepStatus.cs`, `JsonPatchOperation.cs`

---

## 2. Backend Tool Rendering

### Concept

Function tools are **defined and executed on the server**, with results streamed to the client. This keeps business logic, credentials, and sensitive operations secure.

### How It Works

```csharp
// Server defines tools using AIFunctionFactory
AIFunctionFactory.Create(
    name: "search_restaurants",
    description: "Search for restaurants by cuisine and location",
    implementation: async (string cuisine, string location) =>
    {
        // Server-side implementation
        return new RestaurantSearchResponse
        {
            Results = await _restaurantService.SearchAsync(cuisine, location)
        };
    }
);

// Client sends: "Find Italian restaurants in Seattle"
// Server executes: search_restaurants("Italian", "Seattle")
// Client receives: Structured RestaurantSearchResponse
```

### Type Safety

```csharp
// Request/Response types with source generation
[Description("Search for restaurants")]
public record RestaurantSearchRequest(
    [Description("Type of cuisine")] string Cuisine,
    [Description("City or location")] string Location
);

public record RestaurantSearchResponse(
    List<Restaurant> Results
);

// JSON serialization context
[JsonSerializable(typeof(RestaurantSearchRequest))]
[JsonSerializable(typeof(RestaurantSearchResponse))]
internal partial class AppJsonSerializerContext : JsonSerializerContext { }
```

### Security Benefits

- **Credential Protection**: API keys, connection strings stay on server
- **Business Logic Hiding**: Implementation details not exposed to client
- **Validation**: Server validates all inputs before execution
- **Audit Trail**: Server logs all tool invocations

### vs Frontend Tool Rendering

| Aspect | Backend Rendering | Frontend Rendering |
|--------|-------------------|-------------------|
| **Execution** | Server | Server (client-defined) |
| **Definition** | Server | Client sends to server |
| **Security** | High (credentials hidden) | Lower (client controls definition) |
| **Use Case** | Database, APIs, sensitive ops | User-specific, dynamic tools |

### Sample Location

- **Implementation**: `dotnet/samples/GettingStarted/AGUI/Step02_BackendTools/`
- **Server**: Defines `search_restaurants` function
- **Client**: Asks "Find Italian restaurants in Seattle"

---

## 3. Predictive State Updates

### Concept

Agents stream **partial state updates** in real-time as they work, allowing clients to show progressive UI changes (like watching a document being typed).

### How It Works

```csharp
// Agent calls: write_document(document="Long document content...")
// Middleware intercepts and streams it in chunks

for (int i = 0; i < documentContent.Length; i += ChunkSize)
{
    string chunk = documentContent.Substring(0, i + ChunkSize);
    
    var stateUpdate = new DocumentState { Document = chunk };
    byte[] stateBytes = JsonSerializer.SerializeToUtf8Bytes(stateUpdate, ...);
    
    yield return new AgentRunResponseUpdate(
        new ChatResponseUpdate(role: ChatRole.Assistant, 
            [new DataContent(stateBytes, "application/json")]
        )
    );
    
    await Task.Delay(50, cancellationToken); // Simulated streaming
}
```

### State Schema

```csharp
public record DocumentState
{
    public string Document { get; init; } = string.Empty;
}

// Client receives progressive updates:
// Update 1: { "Document": "The quick" }
// Update 2: { "Document": "The quick brown" }
// Update 3: { "Document": "The quick brown fox jumps..." }
```

### Visual Effects

Clients can render these as:
- **Typewriter effect**: Characters appearing one by one
- **Progress bars**: Percentage complete
- **Live previews**: Document/code as it's generated
- **Form filling**: Fields populating in sequence

### Performance Tuning

```csharp
private const int ChunkSize = 10; // Characters per chunk
private const int DelayMs = 50;   // Milliseconds between chunks

// Adjust for:
// - Longer chunks = faster, less smooth
// - Shorter chunks = slower, smoother animation
// - Network latency considerations
```

### Sample Location

- **Implementation**: `dotnet/samples/AGUIClientServer/AGUIDojoServer/PredictiveStateUpdates/`
- **Agent**: `PredictiveStateUpdatesAgent.cs`
- **Model**: `DocumentState.cs`

---

## Getting Started

### Prerequisites

```bash
# .NET 9.0+
dotnet --version

# Azure OpenAI credentials
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"

# Azure authentication
az login
```

### Quick Start: Step-by-Step Tutorials

All samples located at: `dotnet/samples/GettingStarted/AGUI/`

#### Step 01: Basic AGUI Server & Client
```bash
# Terminal 1: Server
cd dotnet/samples/GettingStarted/AGUI/Step01_GettingStarted/Server
dotnet run --urls http://localhost:8888

# Terminal 2: Client
cd dotnet/samples/GettingStarted/AGUI/Step01_GettingStarted/Client
dotnet run
```

#### Step 02: Backend Tools
```bash
cd dotnet/samples/GettingStarted/AGUI/Step02_BackendTools/Server
dotnet run --urls http://localhost:8888

# Try: "Find Italian restaurants in Seattle"
```

#### Step 03: Frontend Tools
```bash
cd dotnet/samples/GettingStarted/AGUI/Step03_FrontendTools/Server
dotnet run --urls http://localhost:8888
```

#### Step 04: Human-in-the-Loop
```bash
cd dotnet/samples/GettingStarted/AGUI/Step04_HumanInLoop/Server
dotnet run --urls http://localhost:8888

# Try: "Approve expense report EXP-12345"
# Client will prompt for approval
```

#### Step 05: State Management
```bash
cd dotnet/samples/GettingStarted/AGUI/Step05_StateManagement/Server
dotnet run

# Try: "Create a recipe for chocolate chip cookies"
# Watch shared state updates in real-time
```

### Production Example: AGUIWebChat

Full Blazor web application with rich UI:

```bash
# Terminal 1: Server
cd dotnet/samples/AGUIWebChat/Server
dotnet run

# Terminal 2: Client
cd dotnet/samples/AGUIWebChat/Client
dotnet run

# Open browser: http://localhost:5000
```

**Features:**
- Streaming responses with typewriter effect
- Auto-scrolling chat interface
- Follow-up conversation suggestions
- Beautiful Blazor components
- Responsive design

---

## Architecture Patterns

### Server-Side Middleware Pattern

```csharp
// Wrap base agent with enhancement middleware
var baseAgent = chatClient.CreateAIAgent(
    name: "MyAgent",
    instructions: "You are helpful..."
);

// Add Agentic UI capabilities
var agenticAgent = new AgenticUIAgent(baseAgent, jsonOptions);

// Add Predictive State Updates
var predictiveAgent = new PredictiveStateUpdatesAgent(agenticAgent, jsonOptions);

// Expose via AGUI protocol
app.MapAGUI("/ag-ui", predictiveAgent);
```

### Client-Side Integration

```csharp
// Configure HTTP client
builder.Services.AddHttpClient("aguiserver", 
    httpClient => httpClient.BaseAddress = new Uri(serverUrl));

// Create AGUI chat client
builder.Services.AddChatClient(sp => 
    new AGUIChatClient(
        sp.GetRequiredService<IHttpClientFactory>().CreateClient("aguiserver"),
        "ag-ui"
    )
);

// Use in components via IChatClient
@inject IChatClient ChatClient

await foreach (var update in ChatClient.CompleteStreamingAsync(messages))
{
    // Handle text, tool calls, state updates
}
```

---

## Real-World Use Cases

### 1. Project Management Dashboard

**Features:**
- Agentic UI for task breakdown
- Backend tools for database queries
- Predictive updates for progress tracking

**Flow:**
```
User: "Plan the Q1 product launch"
Agent: Creates plan with 15 steps
Client: Renders as Kanban board
Agent: Updates step status as tasks complete
Client: Moves cards across columns in real-time
```

### 2. Code Generation IDE

**Features:**
- Predictive state for live code preview
- Backend tools for compilation checks
- Agentic UI for refactoring plans

**Flow:**
```
User: "Create a REST API for user management"
Agent: Streams code file-by-file
Client: Shows editor with incremental content
Agent: Validates with backend compiler
Client: Shows syntax highlighting + errors
```

### 3. Customer Support Assistant

**Features:**
- Backend tools for CRM/ticketing system
- Agentic UI for troubleshooting steps
- Predictive updates for form filling

**Flow:**
```
User: "Customer can't login"
Agent: Creates diagnostic checklist
Client: Renders as interactive wizard
Agent: Fills in results as checks execute
Client: Updates status indicators in real-time
```

---

## Advanced Topics

### State Synchronization

```csharp
// Shared state between client and server
public record SharedState
{
    public Dictionary<string, object> Data { get; init; } = new();
}

// Server updates state
var state = new SharedState 
{ 
    Data = new() { ["progress"] = 75, ["status"] = "Processing..." } 
};

// Client mirrors state and updates UI
```

### JSON Patch Operations

```csharp
// Full state replacement (expensive for large objects)
new DataContent(fullState, "application/json")

// Incremental updates (efficient)
[
  { "op": "replace", "path": "/steps/2/status", "value": "Completed" },
  { "op": "add", "path": "/steps/3", "value": { "name": "New Step" } }
]
new DataContent(patchOperations, "application/json-patch+json")
```

### Approval Workflows

```csharp
// Server requests approval
var approval = new FunctionApprovalRequestContent(
    callId: callContent.CallId,
    name: callContent.Name,
    arguments: callContent.Arguments
);

// Client prompts user
Console.WriteLine($"Approve {approval.Name}? (y/n)");
var response = Console.ReadLine();

// Client sends response
var approvalResponse = new FunctionApprovalResponseContent(
    callId: approval.CallId,
    isApproved: response?.ToLower() == "y"
);
```

---

## Performance Considerations

### Chunking Strategy

```csharp
// Small chunks (10 chars): Smooth animation, more updates
private const int ChunkSize = 10;
private const int DelayMs = 50;

// Large chunks (100 chars): Faster completion, less smooth
private const int ChunkSize = 100;
private const int DelayMs = 100;

// Network-aware: Adjust based on latency
int adaptiveChunkSize = latency < 50 ? 10 : 50;
```

### State Delta Optimization

```csharp
// Bad: Send entire state every time
yield return FullState; // 10KB each update

// Good: Send only changes
if (currentState != lastState)
{
    var patch = JsonPatch.CreateFrom(lastState, currentState);
    yield return patch; // 100 bytes per update
}
```

### Streaming Backpressure

```csharp
// Respect client processing speed
var semaphore = new SemaphoreSlim(10); // Max 10 pending updates

await semaphore.WaitAsync();
yield return update;
// Client acknowledges, releases semaphore
```

---

## Troubleshooting

### Issue: State Updates Not Appearing

**Check:**
1. Content-Type is `application/json` or `application/json-patch+json`
2. JSON serialization context includes state types
3. Client is parsing `DataContent` from updates

### Issue: Slow Streaming

**Solutions:**
```csharp
// Reduce delay between chunks
await Task.Delay(10, cancellationToken); // Faster

// Increase chunk size
private const int ChunkSize = 50;

// Remove unnecessary delays
// await Task.Delay(50); // Comment out for instant
```

### Issue: Tool Not Executing

**Check:**
1. Function name matches exactly
2. Parameter types are serializable
3. Function is registered in AIFunctionFactory
4. JSON context includes request/response types

---

## Python Support (Coming Soon)

While these samples are C#/.NET, Python implementation exists in:

```bash
python/packages/ag-ui/
python/samples/getting_started/ag_ui/
```

Python features include:
- Generative UI components
- Advanced state patterns
- More flexible middleware

---

## Next Steps

### Experiment Order

1. **Start Simple**: Run Step01_GettingStarted to understand basic AGUI flow
2. **Add Tools**: Try Step02_BackendTools with restaurant search
3. **State Management**: Run Step05_StateManagement to see predictive updates
4. **Production UI**: Deploy AGUIWebChat for full-featured example

### Build Your Own

Combine all three enhancements:

```csharp
// 1. Define backend tools for data operations
AIFunctionFactory.Create("fetch_data", ...);

// 2. Add agentic planning
AIFunctionFactory.Create("create_plan", ...);

// 3. Wrap with predictive state streaming
var agent = new PredictiveStateUpdatesAgent(
    new AgenticUIAgent(baseAgent, jsonOptions),
    jsonOptions
);

// 4. Expose via AGUI
app.MapAGUI("/my-agent", agent);
```

---

## References

### Official Documentation

- [AG-UI Overview](https://learn.microsoft.com/agent-framework/integrations/ag-ui/)
- [Backend Tool Rendering](https://learn.microsoft.com/agent-framework/integrations/ag-ui/backend-tool-rendering)
- [State Management](https://learn.microsoft.com/agent-framework/integrations/ag-ui/state-management)
- [Human-in-the-Loop](https://learn.microsoft.com/agent-framework/integrations/ag-ui/human-in-the-loop)

### Sample Code Locations

| Feature | .NET Sample Path |
|---------|-----------------|
| **Agentic UI** | `dotnet/samples/AGUIClientServer/AGUIDojoServer/AgenticUI/` |
| **Backend Tools** | `dotnet/samples/GettingStarted/AGUI/Step02_BackendTools/` |
| **Predictive State** | `dotnet/samples/AGUIClientServer/AGUIDojoServer/PredictiveStateUpdates/` |
| **Full App** | `dotnet/samples/AGUIWebChat/` |

### Community Resources

- [Microsoft Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Discord: Azure AI Foundry](https://discord.gg/b5zjErwbQM)
- [MS Learn Documentation](https://learn.microsoft.com/agent-framework/)

---

## Summary

The December 2025 AGUI enhancements transform Agent Framework from text-only to **rich interactive experiences**:

✅ **Agentic UI** - Agents create renderable plans and workflows  
✅ **Backend Tool Rendering** - Secure server-side function execution  
✅ **Predictive State Updates** - Real-time progressive UI changes  

These features enable building production-grade agentic applications with:
- Task management dashboards
- Code generation IDEs
- Interactive troubleshooting wizards
- Collaborative document editors
- Real-time analytics platforms

**Start experimenting today with the Step-by-Step tutorials!** 🚀

---

**Last Updated**: December 25, 2025  
**Author**: Arturo Quiroga, Sr. Partner Solutions Architect @ Microsoft

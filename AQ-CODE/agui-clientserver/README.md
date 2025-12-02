# AG-UI Client and Server Sample (Python)

Python implementation of the AG-UI (Agent UI) protocol for remote agent communication using Microsoft Agent Framework.

## Overview

This implementation demonstrates how to use the AG-UI protocol to enable communication between a client application and a remote agent server. The AG-UI protocol provides a standardized way for clients to interact with AI agents over HTTP with Server-Sent Events (SSE) streaming.

### Components

1. **agui_server.py** - FastAPI web server that hosts an AI agent and exposes it via AG-UI protocol
2. **agui_client.py** - Console application that connects to the AG-UI server and displays streaming updates
3. **test_server.http** - REST client test file for manual API testing

> ⚠️ **Warning**: The AG-UI protocol is still under development and changing. This implementation follows the .NET reference implementation.

## Architecture

```
┌─────────────────┐         HTTP POST           ┌─────────────────┐
│                 │  ────────────────────────>   │                 │
│  AG-UI Client   │                              │  AG-UI Server   │
│                 │  <────────────────────────   │                 │
└─────────────────┘    SSE Stream (text/event-stream)  │                 │
                                                 │  ┌──────────┐   │
                                                 │  │ MAF Agent│   │
                                                 │  └──────────┘   │
                                                 └─────────────────┘
```

## Prerequisites

- Python 3.11+
- Azure OpenAI access with authentication configured
- Microsoft Agent Framework (MAF) Python SDK

## Installation

```bash
cd AQ-CODE/agui-clientserver
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
# Azure OpenAI Configuration
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"

# Optional: Server Configuration
export AGUI_SERVER_HOST="localhost"
export AGUI_SERVER_PORT="5100"
```

> **Note**: This sample uses `DefaultAzureCredential` for authentication. Make sure you're authenticated with Azure (e.g., via `az login`).

## Running the Sample

### Step 1: Start the AG-UI Server

```bash
cd AQ-CODE/agui-clientserver
python agui_server.py
```

The server will start and listen on `http://localhost:5100`.

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:5100
```

### Step 2: Testing with REST Client (Optional)

Before running the client, you can test the server using the included `.http` file:

1. Open `test_server.http` in VS Code with the REST Client extension
2. Send a test request to verify the server is working
3. Observe the server-sent events stream in the response

Sample request:
```http
POST http://localhost:5100/
Content-Type: application/json

{
  "threadId": "thread_123",
  "runId": "run_456",
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ],
  "context": {}
}
```

### Step 3: Run the AG-UI Client

In a new terminal window:

```bash
cd AQ-CODE/agui-clientserver
python agui_client.py
```

Optionally, configure a different server URL:
```bash
export AGUI_SERVER_URL="http://localhost:5100"
python agui_client.py
```

### Step 4: Interact with the Agent

1. The client will connect to the AG-UI server
2. Enter your message at the prompt
3. Observe the streaming updates with color-coded output:
   - **Yellow**: Run started notification showing thread and run IDs
   - **Cyan**: Agent's text response (streamed character by character)
   - **Green**: Run finished notification
   - **Red**: Error messages (if any occur)
4. Type `:q` or `quit` to exit

## Sample Output

```
🚀 AG-UI Client
Connecting to server at: http://localhost:5100

User (:q or quit to exit): What is the capital of France?

[Run Started - Thread: thread_abc123, Run: run_xyz789]
The capital of France is Paris. It is known for its rich history, culture, and iconic landmarks such as the Eiffel Tower and the Louvre Museum.
[Run Finished - Thread: thread_abc123, Run: run_xyz789]

User (:q or quit to exit): Tell me a fun fact about space

[Run Started - Thread: thread_abc123, Run: run_def456]
Here's a fun fact: A day on Venus is longer than its year! Venus takes about 243 Earth days to rotate once on its axis, but only about 225 Earth days to orbit the Sun.
[Run Finished - Thread: thread_abc123, Run: run_def456]

User (:q or quit to exit): :q
Goodbye! 👋
```

## How It Works

### Server Side

The `agui_server.py` uses FastAPI to expose an agent through the AG-UI protocol:

```python
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

@app.post("/")
async def agui_endpoint(request: AGUIRequest):
    # Create MAF agent
    agent = await project_client.agents.create_agent(
        model=deployment_name,
        instructions="You are a helpful assistant."
    )
    
    # Stream responses as SSE
    async def event_generator():
        async with project_client.agents.run_stream(
            thread_id=thread_id,
            assistant_id=agent.id
        ) as stream:
            async for event in stream:
                yield format_sse_event(event)
    
    return EventSourceResponse(event_generator())
```

This automatically handles:
- HTTP POST requests with message payloads
- Converting agent responses to AG-UI event streams
- Server-sent events (SSE) formatting
- Thread and run management

### Client Side

The `agui_client.py` uses `httpx` with SSE support to connect to the remote server:

```python
import httpx
from httpx_sse import connect_sse

async with httpx.AsyncClient() as client:
    async with connect_sse(
        client, "POST", server_url,
        json=payload
    ) as event_source:
        async for event in event_source.aiter_sse():
            update = parse_agui_event(event)
            
            if update["type"] == "thread.run.created":
                print(f"[Run Started - Thread: {update['thread_id']}, Run: {update['run_id']}]")
            
            elif update["type"] == "thread.message.delta":
                # Display streaming text
                print(update["text"], end="", flush=True)
            
            elif update["type"] == "thread.run.completed":
                print(f"\n[Run Finished - Thread: {update['thread_id']}, Run: {update['run_id']}]")
```

The streaming connection:
1. Sends messages to the server via HTTP POST
2. Receives server-sent events (SSE) stream
3. Parses events into AG-UI protocol messages
4. Displays updates as they arrive for real-time output

## Key Concepts

- **Thread** (`thread_id`): Represents a conversation context that persists across multiple runs
- **Run** (`run_id`): A single execution of the agent for a given set of messages
- **SSE Events**: Server-sent events for real-time streaming communication
- **Event Types**:
  - `thread.run.created`: Run has started
  - `thread.message.delta`: Streaming content chunk
  - `thread.run.completed`: Run has finished
  - `error`: Error occurred during processing

## API Reference

### POST /

Execute agent with messages and stream responses.

**Request Body:**
```json
{
  "threadId": "string (optional)",
  "runId": "string (optional)",
  "messages": [
    {
      "role": "user",
      "content": "string"
    }
  ],
  "context": {}
}
```

**Response:** `text/event-stream` with SSE events

## Comparison with .NET Implementation

| Feature | .NET (C#) | Python |
|---------|-----------|--------|
| Web Framework | ASP.NET Core | FastAPI |
| SSE Library | Built-in | sse-starlette |
| HTTP Client | HttpClient | httpx + httpx-sse |
| Agent SDK | Microsoft.AI.Agents | azure-ai-projects |
| Async Pattern | async/await | asyncio + async/await |

## Troubleshooting

### Server won't start
- Check if port 5100 is already in use: `lsof -i :5100`
- Try a different port: `export AGUI_SERVER_PORT=8000`

### Client can't connect
- Verify server is running: `curl http://localhost:5100/health`
- Check firewall settings
- Verify `AGUI_SERVER_URL` environment variable

### Authentication errors
- Ensure you're logged in: `az login`
- Check Azure OpenAI endpoint and deployment name
- Verify RBAC permissions on Azure OpenAI resource

### No streaming output
- Check if SSE events are being sent (use browser dev tools or curl)
- Verify Content-Type is `text/event-stream`
- Check for buffering issues in client

## Advanced Usage

### Custom Agent Instructions

Modify the agent instructions in `agui_server.py`:

```python
agent = await project_client.agents.create_agent(
    model=deployment_name,
    instructions="You are a specialized assistant for financial analysis.",
    name="FinancialAdvisor"
)
```

### Adding Tools

Enable tools like web search or code interpreter:

```python
agent = await project_client.agents.create_agent(
    model=deployment_name,
    instructions="You are a research assistant.",
    tools=[{"type": "bing_grounding"}]  # Enable web search
)
```

### Multiple Endpoints

Create different endpoints for specialized agents:

```python
@app.post("/financial")
async def financial_agent(request: AGUIRequest):
    # Financial agent logic
    pass

@app.post("/technical")
async def technical_agent(request: AGUIRequest):
    # Technical agent logic
    pass
```

## Future Enhancements

- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add metrics and observability
- [ ] Support file uploads
- [ ] Add WebSocket alternative to SSE
- [ ] Implement agent pool management
- [ ] Add conversation history persistence
- [ ] Create Streamlit UI client

## Related Projects

- [MAF Python SDK](../../README.md)
- [LLMOps for MAF](../llmops/)
- [DBMS Assistant](../../DBMS-ASSISTANT/)

## License

This sample follows the same license as the Microsoft Agent Framework.

---

**Version:** 1.0  
**Last Updated:** December 1, 2025  
**Maintained by:** AI Solutions Architecture Team

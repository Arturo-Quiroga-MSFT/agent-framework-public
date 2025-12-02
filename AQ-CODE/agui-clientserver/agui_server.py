#!/usr/bin/env python3
"""
AG-UI Server - FastAPI server that exposes MAF agents via AG-UI protocol.

This server implements the AG-UI protocol for remote agent communication,
providing Server-Sent Events (SSE) streaming for real-time responses.
"""

import asyncio
import os
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential


# ============================================================================
# Configuration
# ============================================================================

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Server configuration
SERVER_HOST = os.getenv("AGUI_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("AGUI_SERVER_PORT", "5100"))

# Project client (Azure AI Foundry)
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")


# ============================================================================
# Pydantic Models (AG-UI Protocol)
# ============================================================================

class Message(BaseModel):
    """Message in the conversation."""
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")


class AGUIRequest(BaseModel):
    """AG-UI protocol request payload."""
    threadId: Optional[str] = Field(None, description="Thread/conversation ID")
    runId: Optional[str] = Field(None, description="Run execution ID")
    messages: List[Message] = Field(..., description="List of messages")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="AG-UI Server",
    description="Microsoft Agent Framework AG-UI Protocol Server",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global State
# ============================================================================

# Store active threads (in-memory for demo; use persistent storage in production)
active_threads: Dict[str, str] = {}  # thread_id -> assistant_id

# Project client instance
project_client: Optional[AIProjectClient] = None


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize Azure AI Project client on startup."""
    global project_client
    
    print("🚀 Starting AG-UI Server...")
    print(f"📍 Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"🤖 Model: {AZURE_OPENAI_DEPLOYMENT_NAME}")
    
    # Initialize project client
    if PROJECT_CONNECTION_STRING:
        # Using Azure AI Foundry project
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=PROJECT_CONNECTION_STRING
        )
        print("✅ Connected to Azure AI Foundry project")
    else:
        print("⚠️  No PROJECT_CONNECTION_STRING found - using direct Azure OpenAI")
        # Note: For direct Azure OpenAI, you'll need to implement a different client
        # This example focuses on Azure AI Foundry integration


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global project_client
    
    print("🛑 Shutting down AG-UI Server...")
    
    if project_client:
        await project_client.close()
        print("✅ Azure AI Project client closed")


# ============================================================================
# Helper Functions
# ============================================================================

def format_sse_event(event_type: str, data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format data as Server-Sent Event.
    
    Args:
        event_type: Type of event (e.g., 'thread.run.created')
        data: Event data
        
    Returns:
        SSE-formatted event
    """
    import json
    return {
        "event": event_type,
        "data": json.dumps(data)
    }


async def create_or_get_thread(thread_id: Optional[str]) -> str:
    """
    Create a new thread or retrieve existing one.
    
    Args:
        thread_id: Optional existing thread ID
        
    Returns:
        Thread ID
    """
    if thread_id and project_client:
        # Verify thread exists
        try:
            await project_client.agents.get_thread(thread_id)
            return thread_id
        except Exception:
            pass  # Thread doesn't exist, create new one
    
    # Create new thread
    if project_client:
        thread = await project_client.agents.create_thread()
        return thread.id
    
    # Fallback for non-Foundry scenarios
    return thread_id or f"thread_{uuid.uuid4().hex[:8]}"


async def create_or_get_agent(thread_id: str) -> str:
    """
    Create agent or reuse existing one for the thread.
    
    Args:
        thread_id: Thread ID
        
    Returns:
        Agent/Assistant ID
    """
    # Check if we have an agent for this thread
    if thread_id in active_threads:
        agent_id = active_threads[thread_id]
        try:
            # Verify agent still exists
            if project_client:
                await project_client.agents.get_agent(agent_id)
                return agent_id
        except Exception:
            pass  # Agent doesn't exist, create new one
    
    # Create new agent
    if project_client:
        agent = await project_client.agents.create_agent(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            name="AGUIAssistant",
            instructions="You are a helpful assistant. Provide clear, accurate, and helpful responses.",
        )
        active_threads[thread_id] = agent.id
        return agent.id
    
    # Fallback
    agent_id = f"agent_{uuid.uuid4().hex[:8]}"
    active_threads[thread_id] = agent_id
    return agent_id


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_threads": len(active_threads)
    }


@app.post("/")
async def agui_endpoint(request: AGUIRequest):
    """
    Main AG-UI protocol endpoint.
    
    Accepts messages and streams agent responses using Server-Sent Events (SSE).
    """
    if not project_client:
        raise HTTPException(
            status_code=503,
            detail="Server not properly configured. PROJECT_CONNECTION_STRING required."
        )
    
    # Generate IDs if not provided
    thread_id = request.threadId or f"thread_{uuid.uuid4().hex[:8]}"
    run_id = request.runId or f"run_{uuid.uuid4().hex[:8]}"
    
    print(f"📨 New request - Thread: {thread_id}, Run: {run_id}")
    print(f"💬 Messages: {len(request.messages)}")
    
    # Create/get thread and agent
    try:
        thread_id = await create_or_get_thread(thread_id)
        agent_id = await create_or_get_agent(thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize: {str(e)}")
    
    # Add user messages to thread
    for msg in request.messages:
        if msg.role == "user":
            try:
                await project_client.agents.create_message(
                    thread_id=thread_id,
                    role="user",
                    content=msg.content
                )
            except Exception as e:
                print(f"❌ Error creating message: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")
    
    # Stream agent responses as SSE
    async def event_generator():
        """Generate Server-Sent Events from agent stream."""
        try:
            # Send run.created event
            yield format_sse_event("thread.run.created", {
                "thread_id": thread_id,
                "run_id": run_id,
                "assistant_id": agent_id,
                "status": "in_progress"
            })
            
            # Stream agent responses
            async with project_client.agents.create_stream(
                thread_id=thread_id,
                assistant_id=agent_id
            ) as stream:
                async for event in stream:
                    event_type = event.event
                    
                    # Handle different event types
                    if event_type == "thread.message.delta":
                        # Text content delta
                        if hasattr(event.data, 'delta') and hasattr(event.data.delta, 'content'):
                            for content in event.data.delta.content:
                                if hasattr(content, 'text') and hasattr(content.text, 'value'):
                                    yield format_sse_event("thread.message.delta", {
                                        "thread_id": thread_id,
                                        "run_id": run_id,
                                        "delta": {
                                            "content": content.text.value
                                        }
                                    })
                    
                    elif event_type == "thread.message.completed":
                        # Message completed
                        yield format_sse_event("thread.message.completed", {
                            "thread_id": thread_id,
                            "run_id": run_id,
                            "status": "completed"
                        })
                    
                    elif event_type == "thread.run.completed":
                        # Run completed
                        yield format_sse_event("thread.run.completed", {
                            "thread_id": thread_id,
                            "run_id": run_id,
                            "status": "completed"
                        })
                        break
                    
                    elif event_type == "error":
                        # Error occurred
                        error_msg = str(event.data) if hasattr(event, 'data') else "Unknown error"
                        yield format_sse_event("error", {
                            "thread_id": thread_id,
                            "run_id": run_id,
                            "error": error_msg
                        })
                        break
            
            print(f"✅ Run completed - Thread: {thread_id}, Run: {run_id}")
            
        except Exception as e:
            print(f"❌ Error in event generator: {e}")
            yield format_sse_event("error", {
                "thread_id": thread_id,
                "run_id": run_id,
                "error": str(e)
            })
    
    return EventSourceResponse(event_generator())


@app.get("/threads")
async def list_threads():
    """List all active threads."""
    return {
        "threads": list(active_threads.keys()),
        "count": len(active_threads)
    }


@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """Delete a thread and its associated agent."""
    if thread_id in active_threads:
        agent_id = active_threads.pop(thread_id)
        
        # Optionally delete from Azure AI Foundry
        if project_client:
            try:
                await project_client.agents.delete_thread(thread_id)
                await project_client.agents.delete_agent(agent_id)
            except Exception as e:
                print(f"⚠️  Warning: Failed to delete from Foundry: {e}")
        
        return {"status": "deleted", "thread_id": thread_id}
    
    raise HTTPException(status_code=404, detail="Thread not found")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("🚀 AG-UI Server - Microsoft Agent Framework")
    print("=" * 80)
    print(f"📍 Server: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"🤖 Model: {AZURE_OPENAI_DEPLOYMENT_NAME}")
    print(f"📚 Docs: http://{SERVER_HOST}:{SERVER_PORT}/docs")
    print("=" * 80)
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info"
    )

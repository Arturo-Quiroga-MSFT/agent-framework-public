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
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# ============================================================================
# WORKAROUND for azure-ai-projects 2.0.0b2 gzip encoding bug
# GitHub Issue: https://github.com/microsoft/agent-framework/issues/2457
# ============================================================================
import azure.core.pipeline.policies as policies
_original_on_request = policies.HeadersPolicy.on_request
def _patched_on_request(self, request):
    _original_on_request(self, request)
    request.http_request.headers['Accept-Encoding'] = 'identity'
policies.HeadersPolicy.on_request = _patched_on_request
# ============================================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential


# ============================================================================
# OpenTelemetry & Observability Setup
# ============================================================================

# Try to import OpenTelemetry - gracefully degrade if not available
TELEMETRY_ENABLED = False
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.trace import Status, StatusCode
    
    TELEMETRY_ENABLED = True
    print("✅ OpenTelemetry libraries loaded")
except ImportError:
    print("⚠️  OpenTelemetry not available - telemetry disabled")
    print("   Install with: pip install -r requirements.txt")


# ============================================================================
# Configuration
# ============================================================================

# Azure AI Foundry Project Endpoint (new format)
AZURE_AI_PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_AI_MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")

# Legacy configuration (kept for backwards compatibility)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

# Server configuration
SERVER_HOST = os.getenv("AGUI_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("AGUI_SERVER_PORT", "5100"))

# Observability configuration
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

# Project client (Azure AI Foundry) - Legacy
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


def format_sse_event(event_type: str, data: Dict[str, Any]) -> Dict[str, str]:
    """Format data as a Server-Sent Event payload."""
    import json
    return {
        "event": event_type,
        "data": json.dumps(data)
    }


# ==========================================================================
# Global State
# ==========================================================================

active_threads: Dict[str, str] = {}
project_client: Optional[AIProjectClient] = None
azure_credential: Optional[DefaultAzureCredential] = None


@app.on_event("startup")
async def startup_event():
    """Initialize Azure clients and telemetry."""
    global project_client, azure_credential
    print("⚙️  Starting AG-UI server...")
    
    if TELEMETRY_ENABLED and APPLICATIONINSIGHTS_CONNECTION_STRING:
        configure_azure_monitor(
            connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING,
            enable_live_metrics=True
        )
        FastAPIInstrumentor.instrument_app(app)
        HTTPXClientInstrumentor().instrument()
        print("📡 Azure Monitor telemetry configured")
    
    try:
        if PROJECT_CONNECTION_STRING:
            project_client = AIProjectClient.from_connection_string(PROJECT_CONNECTION_STRING)
            print("🔌 Connected to Azure AI Project via connection string")
        elif AZURE_AI_PROJECT_ENDPOINT and AZURE_OPENAI_API_KEY:
            project_client = AIProjectClient(
                endpoint=AZURE_AI_PROJECT_ENDPOINT,
                credential=AzureKeyCredential(AZURE_OPENAI_API_KEY)
            )
            print("🔐 Connected to Azure AI Project via API key")
        elif AZURE_AI_PROJECT_ENDPOINT:
            azure_credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
            project_client = AIProjectClient(
                endpoint=AZURE_AI_PROJECT_ENDPOINT,
                credential=azure_credential
            )
            print("🔑 Connected to Azure AI Project with DefaultAzureCredential")
        else:
            print("⚠️  No Azure AI configuration detected. Server will reject requests.")
    except Exception as exc:
        project_client = None
        print(f"❌ Failed to initialize Azure AI Project client: {exc}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global project_client, azure_credential
    print("🛑 Shutting down AG-UI server...")
    if project_client:
        await project_client.close()
        project_client = None
    if azure_credential:
        await azure_credential.close()
        azure_credential = None


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
        model_name = AZURE_AI_MODEL_DEPLOYMENT_NAME or AZURE_OPENAI_DEPLOYMENT_NAME
        agent = await project_client.agents.create_agent(
            model=model_name,
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_threads": len(active_threads)
    }


@app.post("/")
async def agui_endpoint(request: AGUIRequest):
    """
    Main AG-UI protocol endpoint.
    
    Accepts messages and streams agent responses using Server-Sent Events (SSE).
    """
    # Create OpenTelemetry span for this request
    tracer = trace.get_tracer(__name__) if TELEMETRY_ENABLED else None
    span = tracer.start_span("agui.request") if tracer else None
    
    try:
        if not project_client:
            if span:
                span.set_status(Status(StatusCode.ERROR, "Server not configured"))
                span.end()
            raise HTTPException(
                status_code=503,
                detail="Server not properly configured. PROJECT_CONNECTION_STRING required."
            )
        
        # Generate IDs if not provided
        thread_id = request.threadId or f"thread_{uuid.uuid4().hex[:8]}"
        run_id = request.runId or f"run_{uuid.uuid4().hex[:8]}"
        
        # Add span attributes (AG-UI semantic conventions)
        if span:
            span.set_attribute("agui.protocol.version", "1.0")
            span.set_attribute("agui.thread.id", thread_id)
            span.set_attribute("agui.run.id", run_id)
            span.set_attribute("agui.messages.count", len(request.messages))
            span.set_attribute("agui.transport", "sse")
            user_message = next((msg.content for msg in request.messages if msg.role == "user"), "")
            if user_message:
                span.set_attribute("agui.user.prompt", user_message[:500])  # First 500 chars
        
        print(f"📨 New request - Thread: {thread_id}, Run: {run_id}")
        print(f"💬 Messages: {len(request.messages)}")
        
        # Create/get thread and agent
        try:
            thread_id = await create_or_get_thread(thread_id)
            agent_id = await create_or_get_agent(thread_id)
            
            if span:
                span.set_attribute("gen_ai.agent.id", agent_id)
                span.set_attribute("gen_ai.agent.name", "AG-UI Agent")
                span.set_attribute("gen_ai.request.model", AZURE_AI_MODEL_DEPLOYMENT_NAME or AZURE_OPENAI_DEPLOYMENT_NAME)
        except Exception as e:
            if span:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                span.end()
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
            total_tokens = 0
            response_text = ""
            start_time = datetime.now(timezone.utc)
        
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
                                        response_text += content.text.value
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
                            # Extract usage information if available
                            if hasattr(event.data, 'usage'):
                                usage = event.data.usage
                                if hasattr(usage, 'total_tokens'):
                                    total_tokens = usage.total_tokens
                        
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
                        
                            # Record error in span
                            if span:
                                span.set_status(Status(StatusCode.ERROR, error_msg))
                            break
            
                # Calculate duration
                duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
                # Update span with completion metrics
                if span:
                    span.set_attribute("agui.response.length", len(response_text))
                    span.set_attribute("gen_ai.usage.total_tokens", total_tokens)
                    span.set_attribute("agui.duration_ms", duration_ms)
                    span.set_attribute("agui.status", "completed")
                    span.set_status(Status(StatusCode.OK))
            
                print(f"✅ Run completed - Thread: {thread_id}, Run: {run_id}, Tokens: {total_tokens}, Duration: {duration_ms:.0f}ms")
            
            except Exception as e:
                print(f"❌ Error in event generator: {e}")
            
                # Record exception in span
                if span:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
            
                yield format_sse_event("error", {
                    "thread_id": thread_id,
                    "run_id": run_id,
                    "error": str(e)
                })
            finally:
                # End the span when generator completes
                if span:
                    span.end()
        
        return EventSourceResponse(event_generator())
        
    except Exception as e:
        # Handle any outer exceptions
        if span:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.end()
        raise


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

"""
FastAPI Server with AG-UI Protocol Integration

This server exposes multiple MAF agents via the AG-UI protocol,
enabling rich CopilotKit UI interactions.
"""

import os
from pathlib import Path

import uvicorn
from agent_framework._clients import ChatClientProtocol
from agent_framework.azure import AzureAIClient  # V2 API
from agent_framework.openai import OpenAIChatClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint

from agents import (
    create_weather_agent,
    create_code_interpreter_agent,
    create_bing_search_agent,
    create_azure_ai_search_agent,
    create_firecrawl_agent,
    create_hosted_mcp_agent,
)

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def _build_chat_client() -> ChatClientProtocol:
    """Build chat client from environment variables."""
    try:
        if bool(os.getenv("AZURE_OPENAI_ENDPOINT")):
            # Azure OpenAI setup with V2 API
            return AzureAIClient(
                async_credential=DefaultAzureCredential(),
            )
        
        if bool(os.getenv("OPENAI_API_KEY")):
            # OpenAI setup
            return OpenAIChatClient(
                model_id=os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4o-mini"),
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        
        raise ValueError(
            "Either AZURE_OPENAI_ENDPOINT or OPENAI_API_KEY environment variable is required"
        )
    
    except Exception as exc:
        raise RuntimeError(
            "Unable to initialize chat client. Check your API credentials in .env file."
        ) from exc


# Initialize chat client
chat_client = _build_chat_client()

# Create FastAPI app
app = FastAPI(
    title="MAF + CopilotKit Demo API",
    description="Azure AI Agent Framework with AG-UI protocol and CopilotKit integration",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MAF + CopilotKit Demo",
        "version": "1.0.0",
        "agents": [
            "weather",
            "code",
            "bing-search",
            "azure-ai-search",
            "firecrawl",
            "microsoft-learn",
        ],
    }


# Create and expose agents via AG-UI protocol
print("🚀 Initializing agents...")

# 1. Weather Agent
try:
    weather_agent = create_weather_agent(chat_client)
    add_agent_framework_fastapi_endpoint(
        app=app,
        agent=weather_agent,
        path="/agents/weather",
    )
    print("✓ Weather Agent: /agents/weather")
except Exception as e:
    print(f"✗ Weather Agent failed: {e}")

# 2. Code Interpreter Agent
try:
    code_agent = create_code_interpreter_agent(chat_client)
    add_agent_framework_fastapi_endpoint(
        app=app,
        agent=code_agent,
        path="/agents/code",
    )
    print("✓ Code Interpreter Agent: /agents/code")
except Exception as e:
    print(f"✗ Code Interpreter Agent failed: {e}")

# 3. Bing Search Agent
try:
    bing_agent = create_bing_search_agent(chat_client)
    add_agent_framework_fastapi_endpoint(
        app=app,
        agent=bing_agent,
        path="/agents/bing-search",
    )
    print("✓ Bing Search Agent: /agents/bing-search")
except Exception as e:
    print(f"✗ Bing Search Agent failed: {e}")

# 4. Azure AI Search Agent
try:
    azure_search_agent = create_azure_ai_search_agent(chat_client)
    add_agent_framework_fastapi_endpoint(
        app=app,
        agent=azure_search_agent,
        path="/agents/azure-ai-search",
    )
    print("✓ Azure AI Search Agent: /agents/azure-ai-search")
except Exception as e:
    print(f"✗ Azure AI Search Agent failed: {e}")

# 5. Firecrawl Agent (optional - requires API key)
if os.getenv("FIRECRAWL_API_KEY"):
    try:
        firecrawl_agent = create_firecrawl_agent(chat_client)
        add_agent_framework_fastapi_endpoint(
            app=app,
            agent=firecrawl_agent,
            path="/agents/firecrawl",
        )
        print("✓ Firecrawl Agent: /agents/firecrawl")
    except Exception as e:
        print(f"✗ Firecrawl Agent failed: {e}")
else:
    print("⊘ Firecrawl Agent skipped: FIRECRAWL_API_KEY not set")

# 6. Microsoft Learn MCP Agent
try:
    mcp_agent = create_hosted_mcp_agent(chat_client)
    add_agent_framework_fastapi_endpoint(
        app=app,
        agent=mcp_agent,
        path="/agents/microsoft-learn",
    )
    print("✓ Microsoft Learn MCP Agent: /agents/microsoft-learn")
except Exception as e:
    print(f"✗ Microsoft Learn MCP Agent failed: {e}")

print("\n🎉 Server ready!")
print("📚 API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )

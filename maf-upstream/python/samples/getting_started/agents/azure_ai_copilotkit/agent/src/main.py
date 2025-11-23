"""
FastAPI backend exposing Azure AI Weather Agent via AG-UI protocol for CopilotKit.
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agent_framework.ag_ui import add_agent_framework_fastapi_endpoint

from weather_agent import create_weather_agent

# Load environment variables
load_dotenv()

# Create the agent
agent = create_weather_agent()

# Create FastAPI app
app = FastAPI(title="Azure AI Weather Agent - CopilotKit Demo")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add AG-UI endpoint
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=agent,
    path="/copilotkit",
)

if __name__ == "__main__":
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "8200"))
    print(f"\n🚀 Starting Azure AI Weather Agent on http://{host}:{port}")
    print(f"📡 AG-UI endpoint available at http://{host}:{port}/")
    print(f"📖 API docs at http://{host}:{port}/docs\n")
    uvicorn.run("main:app", host=host, port=port, reload=True)

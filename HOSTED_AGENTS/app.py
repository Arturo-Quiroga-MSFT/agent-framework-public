
#!/usr/bin/env python3
"""Contoso Customer Support Agent - Hosted Version with Hosting Adapter"""

from azure.ai.agentserver.agentframework import from_azure_ai_agent
from agent_framework.azure import AzureAIClient
from azure.identity import DefaultAzureCredential
import os

def create_app():
    """Create and configure the hosted agent application"""

    # Initialize Azure AI client
    client = AzureAIClient(
        endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )

    # Create or get existing agent
    agent = client.create_agent(
        model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
        instructions="""You are a helpful customer support agent for Contoso Electronics.

        Your responsibilities:
        - Answer product questions about laptops, tablets, and accessories
        - Help customers track orders
        - Provide troubleshooting guidance
        - Be friendly, professional, and concise

        Product Information:
        - All laptops come with a 1-year warranty
        - Free shipping on orders over $500
        - 30-day return policy on all products
        """,
        name="ContosoSupportAgent",
        # Reuse existing agent version if available
        use_latest_version=True
    )

    # Create hosted server with hosting adapter
    # This automatically creates Foundry-compatible REST endpoints:
    # - POST /responses (main agent interaction)
    # - GET /health (health check)
    # - Streaming support via SSE
    # - OpenTelemetry instrumentation
    server = from_azure_ai_agent(agent, client=client)

    return server

if __name__ == "__main__":
    print("🚀 Starting Contoso Support Agent Server...")
    print("   Endpoint: http://localhost:8088")
    print("   Health: http://localhost:8088/health")
    print("   Responses: POST http://localhost:8088/responses")
    print("")

    app = create_app()

    # Run the server (production uses gunicorn or similar)
    app.run(host="0.0.0.0", port=8088)

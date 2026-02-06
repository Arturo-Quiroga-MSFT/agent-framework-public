
#!/usr/bin/env python3
"""Contoso Customer Support Agent - Hosted Version with Hosting Adapter

Uses the current Microsoft Agent Framework SDK pattern with the hosting adapter.
Reference: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents
"""

import os
from azure.ai.agentserver.agentframework import from_agent_framework
from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureAIAgentClient
from azure.identity import DefaultAzureCredential

# Configure these via environment variables set in agent definition
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1")


@ai_function
def get_order_status(order_id: str) -> str:
    """
    Look up the status of a customer order.

    Args:
        order_id: The order ID to look up (e.g., "ORD-12345")

    Returns:
        The current status of the order.
    """
    # Demo implementation - in production, this would query a database
    demo_orders = {
        "ORD-12345": "Shipped - Expected delivery Feb 8, 2026",
        "ORD-67890": "Processing - Will ship within 24 hours",
        "ORD-11111": "Delivered on Feb 3, 2026",
    }
    return demo_orders.get(order_id, f"Order {order_id} not found. Please check the order ID and try again.")


@ai_function
def get_product_info(product_name: str) -> str:
    """
    Get information about a Contoso Electronics product.

    Args:
        product_name: The product name or category to look up

    Returns:
        Product information including pricing and specs.
    """
    products = {
        "laptop": "Contoso ProBook 15 - $1,299. 15.6\" display, Intel i7, 16GB RAM, 512GB SSD. 1-year warranty included.",
        "tablet": "Contoso Tab X10 - $599. 10.5\" display, Snapdragon 8, 8GB RAM, 128GB storage. 1-year warranty included.",
        "headphones": "Contoso SoundMax Pro - $249. Active noise cancellation, 30hr battery, Bluetooth 5.3.",
        "monitor": "Contoso UltraView 27 - $449. 27\" 4K IPS, USB-C, 100% sRGB. 2-year warranty.",
    }
    key = product_name.lower()
    for k, v in products.items():
        if k in key:
            return v
    return f"Product '{product_name}' not found. We carry laptops, tablets, headphones, and monitors."


# Create the agent using Microsoft Agent Framework
agent = ChatAgent(
    chat_client=AzureAIAgentClient(
        project_endpoint=PROJECT_ENDPOINT,
        model_deployment_name=MODEL_DEPLOYMENT_NAME,
        credential=DefaultAzureCredential(),
    ),
    instructions="""You are a helpful customer support agent for Contoso Electronics.

Your responsibilities:
- Answer product questions about laptops, tablets, headphones, and monitors
- Help customers track orders using the get_order_status tool
- Provide product details using the get_product_info tool
- Provide troubleshooting guidance
- Be friendly, professional, and concise

Key Policies:
- All products come with a 1-year warranty (monitors have 2 years)
- Free shipping on orders over $500
- 30-day return policy on all products
- For warranty claims, direct customers to support@contoso.com
""",
    tools=[get_order_status, get_product_info],
)

if __name__ == "__main__":
    # Wrap with the hosting adapter - exposes POST /responses and GET /health
    from_agent_framework(agent).run()

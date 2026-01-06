#!/usr/bin/env python3
"""
Example 10: Handoff Workflow with DevUI Visualization (Dynamic Routing)

This example demonstrates the HANDOFF orchestration pattern using MAF's agent handoff capabilities.
Unlike sequential (predetermined) or group chat (conversation), this showcases DYNAMIC ROUTING
where agents autonomously decide who should handle the query next.

Key Differences from Examples 07-09:
- Agents make ROUTING DECISIONS (not orchestrator)
- Flow is DYNAMIC based on query analysis
- Each agent can hand off to multiple possible next agents
- Perfect for triage, escalation, multi-domain queries

Handoff Visualization:
┌──────────────────────────────────────────────────────────────┐
│  User Query → Tier 1 Agent (analyzes complexity)             │
│                   ↓                                           │
│  [Agent decides] → Shipping Specialist (if shipping issue)   │
│                 OR                                            │
│                 → Technical Support (if technical issue)      │
│                 OR                                            │
│                 → Refund Agent (if refund needed)            │
│                 OR                                            │
│                 → Resolve directly (if simple)               │
└──────────────────────────────────────────────────────────────┘

Agents autonomously route based on context!

Prerequisites:
1. Set up your .env file with GITHUB_TOKEN
2. Install dependencies: pip install -r requirements.txt
3. Install DevUI: pip install agent-framework-devui --pre

Usage:
    python 10_github_handoff_workflow.py
    
    Opens DevUI at http://localhost:8085 with handoff visualization!

Example Support Queries:
- "My order #12345 hasn't arrived and tracking shows it's lost"
- "I can't log into my account, getting error code 500"
- "I need a refund for damaged item received yesterday"
- "How do I reset my password?"
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agent_framework import ChatAgent, HandoffBuilder
from agent_framework.openai import OpenAIChatClient

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
GITHUB_BASE_URL = "https://models.inference.ai.azure.com"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env file. Please set it first.")


class SupportQueryInput(BaseModel):
    """Input model for customer support queries."""

    query: str = Field(
        ...,
        description="Customer support query requiring routing to appropriate specialist",
        examples=[
            "My order #12345 hasn't arrived, tracking shows it's stuck in transit for 2 weeks",
            "I can't log into my account, getting error code 500 when I enter password",
            "I need a refund for item that arrived damaged. Order #67890 from last week",
            "How do I change my email address on my account?",
            "The app crashes every time I try to upload a photo",
            "I was charged twice for the same order #45678",
            "My package was delivered to the wrong address",
            "I forgot my password and the reset email isn't arriving",
        ],
    )


async def create_handoff_workflow():
    """Create the handoff workflow with dynamic routing using HandoffBuilder."""

    # Create OpenAI-compatible chat client
    client = OpenAIChatClient(
        model_id=GITHUB_MODEL,
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_BASE_URL,
    )

    # Create Tier 1 Support Agent (entry point with routing logic)
    tier1_agent = ChatAgent(
        name="Tier1Support",
        description="First-line support agent that analyzes and routes customer queries",
        instructions="""You are a Tier 1 customer support agent who triages incoming queries.

Your role:
- Analyze the customer's issue carefully
- Determine which specialist should handle it
- Use handoff tools to route to the right team
- Only resolve simple queries yourself

**Routing Rules:**
- Shipping/delivery issues (lost packages, tracking, wrong address) → call handoff_to_ShippingSpecialist
- Technical issues (login errors, app crashes, bugs, error codes) → call handoff_to_TechnicalSupport  
- Refunds/returns (damaged items, duplicate charges, returns) → call handoff_to_RefundAgent
- Simple queries (password reset instructions, basic account questions) → Resolve yourself

When handing off:
- Briefly acknowledge the issue
- Explain you're connecting them to a specialist
- Call the appropriate handoff tool

When resolving yourself:
- Provide clear, helpful instructions
- Keep response concise (2-3 sentences)""",
        chat_client=client,
    )

    # Create Shipping Specialist Agent
    shipping_agent = ChatAgent(
        name="ShippingSpecialist",
        description="Expert in shipping, delivery, and logistics issues",
        instructions="""You are a shipping and delivery specialist.

Your role:
- Investigate shipping/delivery issues
- Check tracking information
- Determine next steps (wait, reship, refund)
- Escalate to refunds if package is lost/unrecoverable

**Common scenarios:**
- Package delayed: Explain transit times, suggest waiting if reasonable
- Package lost: If 2+ weeks past expected, recommend refund
- Wrong address: Check if redirectable, otherwise suggest reorder
- Tracking stuck: Investigate carrier issues, provide updates

Provide clear action items and timelines. If refund is needed, call handoff_to_RefundAgent.

Keep response focused (3-4 key points).""",
        chat_client=client,
    )

    # Create Technical Support Agent
    technical_agent = ChatAgent(
        name="TechnicalSupport",
        description="Expert in technical issues, bugs, and system errors",
        instructions="""You are a technical support specialist.

Your role:
- Diagnose technical issues and errors
- Provide step-by-step troubleshooting
- Identify if issue is user error or system bug
- Escalate system bugs to engineering team

**Common scenarios:**
- Login errors: Check credentials, browser cache, suggest password reset
- App crashes: Get device info, suggest reinstall, report bug
- Error codes: Explain meaning, provide resolution steps
- Performance issues: Check internet, device specs, optimize settings

Provide clear troubleshooting steps numbered 1, 2, 3.
If issue persists after troubleshooting, acknowledge and escalate to engineering.

Keep response technical but accessible (3-4 steps).""",
        chat_client=client,
    )

    # Create Refund Agent
    refund_agent = ChatAgent(
        name="RefundAgent",
        description="Expert in refunds, returns, and financial resolutions",
        instructions="""You are a refund and returns specialist.

Your role:
- Process refund requests
- Verify eligibility (receipt, timeframe, condition)
- Calculate refund amounts
- Provide refund timelines and methods

**Common scenarios:**
- Damaged items: Approve refund, request photo if needed
- Lost packages: Approve full refund after shipping investigation
- Duplicate charges: Verify transaction, reverse charge
- Change of mind: Check return policy, provide return label

**Always include:**
1. Eligibility confirmation
2. Refund amount
3. Timeline (e.g., 5-7 business days)
4. Next steps for customer

Keep response clear and action-oriented (3-4 points).""",
        chat_client=client,
    )

    # Build the handoff workflow
    # - Tier1Support is the coordinator (receives all user input first)
    # - Tier1Support can hand off to any specialist
    # - ShippingSpecialist can hand off to RefundAgent (for escalation)
    # - TechnicalSupport and RefundAgent are terminal (no further handoffs)
    workflow = (
        HandoffBuilder(
            name="customer_support_handoff",
            participants=[tier1_agent, shipping_agent, technical_agent, refund_agent],
        )
        .set_coordinator(tier1_agent)
        .add_handoff(tier1_agent, [shipping_agent, technical_agent, refund_agent])
        .add_handoff(shipping_agent, refund_agent)  # Shipping can escalate to refund
        .with_termination_condition(
            # Stop after 10 user messages (default-like behavior)
            lambda conversation: sum(1 for msg in conversation if msg.role.value == "user") > 10
        )
        .build()
    )

    return workflow


def main():
    """Launch the handoff workflow in DevUI with visual representation."""
    from agent_framework.devui import serve

    # Create output directory
    output_dir = Path("workflow_outputs")
    output_dir.mkdir(exist_ok=True)

    print("\n" + "="*80)
    print("🔀 Handoff Workflow - Dynamic Customer Support Routing")
    print("="*80)
    print("\n📋 Agent Structure:")
    print("   Tier 1 Support (entry) → [Dynamic Routing]")
    print("   ├→ Shipping Specialist (delivery issues)")
    print("   ├→ Technical Support (bugs & errors)")
    print("   └→ Refund Agent (returns & refunds)")
    print("\n🔧 Using: GitHub Models with Microsoft Agent Framework")
    print("🎨 Feature: Dynamic agent handoffs based on query analysis")
    print("\n🌐 Starting DevUI server...")

    # Create the workflow
    workflow = asyncio.run(create_handoff_workflow())

    print("\n✅ Handoff workflow created")
    print("\n" + "="*80)
    print("🎯 DevUI Interface")
    print("="*80)
    print("\n🌐 Web UI:  http://localhost:8085")
    print("📡 API:     http://localhost:8085/v1/*")
    print("🔍 Entity:  Tier1Support (entry point)")
    print("📊 Feature: Watch agents autonomously route queries")

    print("\n" + "="*80)
    print("💡 How Handoff Works")
    print("="*80)
    print("\n1. Open http://localhost:8085 in your browser")
    print("2. Select 'Tier1Support' from dropdown")
    print("3. Enter a customer support query")
    print("4. Watch Tier 1 agent analyze and decide:")
    print("   • Shipping issue? → Routes to ShippingSpecialist (~15s)")
    print("   • Technical issue? → Routes to TechnicalSupport (~15s)")
    print("   • Refund needed? → Routes to RefundAgent (~15s)")
    print("   • Simple query? → Resolves directly (~10s)")
    print("5. See specialist handle the routed query (~15s)")
    print("6. Total time: ~20-30s depending on routing")

    print("\n" + "="*80)
    print("📝 Example Support Queries")
    print("="*80)
    print("\n📦 Shipping Issues:")
    print("   • My order #12345 hasn't arrived, tracking shows lost")
    print("   • Package delivered to wrong address yesterday")
    print("   • Tracking stuck for 2 weeks, where's my order?")

    print("\n🔧 Technical Issues:")
    print("   • Can't log in, getting error code 500")
    print("   • App crashes when I upload photos")
    print("   • Password reset email not arriving")

    print("\n💰 Refund Issues:")
    print("   • Need refund for damaged item received")
    print("   • Was charged twice for same order #45678")
    print("   • Want to return item, how do I get refund?")

    print("\n❓ Simple Queries:")
    print("   • How do I change my email address?")
    print("   • What are your business hours?")
    print("   • How do I reset my password?")

    print("\n" + "="*80)
    print("✨ Handoff vs Other Patterns")
    print("="*80)
    print("\n🎨 Key Differences:")
    print("   • Sequential (07): A→B→C (predetermined order)")
    print("   • Parallel (08): All agents simultaneously")
    print("   • Group Chat (09): Orchestrated conversation")
    print("   • Handoff (10): AGENT-DRIVEN ROUTING")

    print("\n💡 Handoff Advantages:")
    print("   • Agents make intelligent routing decisions")
    print("   • No predetermined flow - adapts to query")
    print("   • Efficient - only involves needed specialists")
    print("   • Natural for triage/escalation scenarios")
    print("   • Can chain handoffs (Tier1 → Shipping → Refund)")

    print("\n" + "="*80)
    print("📊 Routing Decision Flow")
    print("="*80)
    print("\nQuery: 'My package is lost'")
    print("   ↓")
    print("Tier1Support analyzes:")
    print("   - Keywords: 'package', 'lost'")
    print("   - Category: Shipping issue")
    print("   - Decision: Hand off to ShippingSpecialist")
    print("   ↓")
    print("ShippingSpecialist handles:")
    print("   - Investigates tracking")
    print("   - Determines: Package unrecoverable")
    print("   - Decision: Hand off to RefundAgent")
    print("   ↓")
    print("RefundAgent resolves:")
    print("   - Approves refund")
    print("   - Provides timeline")
    print("   - DONE")

    print("\n" + "="*80)
    print("🔍 What to Watch in DevUI")
    print("="*80)
    print("\n1. **Execution Timeline**:")
    print("   - See Tier1Support invoke first")
    print("   - Watch handoff to specialist")
    print("   - See specialist's response")

    print("\n2. **Traces Tab**:")
    print("   - Check Tier1Support trace - shows routing decision")
    print("   - Check specialist trace - shows handling")
    print("   - Compare token usage (lower than Group Chat!)")

    print("\n3. **Response Structure**:")
    print("   - Tier1: Acknowledges + 'Connecting you to...'")
    print("   - Specialist: Detailed resolution")

    print("\n" + "="*80)
    print("⌨️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")

    # Launch DevUI server with tracing enabled
    serve(
        entities=[workflow],
        port=8085,
        auto_open=True,
        tracing_enabled=True,  # Enable OpenTelemetry tracing
    )


if __name__ == "__main__":
    main()

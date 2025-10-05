# Copyright (c) Microsoft. All rights reserved.

"""
Smart City Infrastructure Workflow - DevUI Version with Tracing

This workflow creates a specialized team of 7 smart city experts to analyze
urban infrastructure projects, IoT implementations, and sustainable city initiatives.

The workflow uses a fan-out/fan-in pattern where:
- User describes a smart city project or initiative
- Input is dispatched to all 7 specialized agents concurrently
- Each agent provides domain-specific analysis
- Results are aggregated and formatted with clear sections

SMART CITY AGENTS:
- Urban Planning: Zoning, land use, community impact, density
- IoT & Technology: Sensors, connectivity, data platforms, edge computing
- Sustainability: Green energy, carbon footprint, circular economy
- Transportation: Traffic flow, public transit, autonomous vehicles
- Municipal Finance: Bonds, public-private partnerships, grants, ROI
- Community Engagement: Stakeholder input, equity, accessibility
- Privacy & Security: Data governance, surveillance ethics, cybersecurity

PREREQUISITES:
- Azure OpenAI access configured via .env file in workflows directory
- Azure CLI authentication: Run 'az login'

TRACING OPTIONS:
1. Console Tracing: Set ENABLE_CONSOLE_TRACING=true (simplest)
2. Azure AI Tracing: Set ENABLE_AZURE_AI_TRACING=true (requires Application Insights)
3. OTLP Tracing: Set OTLP_ENDPOINT (e.g., http://localhost:4317 for Jaeger/Zipkin)
4. DevUI Tracing: Set ENABLE_DEVUI_TRACING=true (view in DevUI interface)
"""

import asyncio
import os
from contextlib import AsyncExitStack
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from agent_framework import ChatMessage, Executor, WorkflowBuilder, WorkflowContext, handler, Role
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import get_tracer, setup_observability
from azure.identity import AzureCliCredential
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id
from pydantic import BaseModel, Field

# Load environment variables from workflows/.env file
load_dotenv(Path(__file__).parent.parent / ".env")


class SmartCityInput(BaseModel):
    """Input model for smart city infrastructure analysis."""
    
    description: str = Field(
        ...,
        description="Describe the smart city infrastructure project, urban initiative, or technology deployment you want to analyze",
        examples=[
            "City-wide IoT sensor network for real-time air quality monitoring and adaptive traffic management",
            "Smart grid deployment with distributed renewable energy and battery storage for 500,000 residents",
            "Autonomous shuttle network connecting transit hubs, hospitals, and universities in downtown district",
            "Digital twin platform for infrastructure monitoring, predictive maintenance, and emergency response",
            "Smart waste management system with AI-powered route optimization and IoT-enabled bins",
            "5G network infrastructure to enable connected vehicles, smart buildings, and public WiFi",
            "Integrated mobility-as-a-service platform combining buses, bikes, scooters, and ride-sharing",
            "Smart street lighting with adaptive brightness, EV charging, and environmental sensors"
        ]
    )


def format_smart_city_results(results) -> str:
    """Format smart city agent outputs for DevUI display and save to file.
    
    Args:
        results: List of AgentExecutorResponse objects from concurrent agents
        
    Returns:
        Formatted string with all agent responses
    """
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("🏙️ COMPREHENSIVE SMART CITY INFRASTRUCTURE ANALYSIS")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Process each agent's response
    for result in results:
        # Get the agent's messages
        messages = getattr(result.agent_run_response, "messages", [])
        
        # Find the final assistant message
        for msg in reversed(messages):
            if hasattr(msg, "author_name") and msg.author_name and msg.author_name != "user":
                agent_name = msg.author_name.upper()
                
                # Add emoji based on agent type
                emoji = {
                    "URBAN_PLANNING": "🏗️",
                    "IOT_TECHNOLOGY": "📡",
                    "SUSTAINABILITY": "🌱",
                    "TRANSPORTATION": "🚦",
                    "MUNICIPAL_FINANCE": "💰",
                    "COMMUNITY_ENGAGEMENT": "👥",
                    "PRIVACY_SECURITY": "🔐"
                }.get(agent_name, "🏙️")
                
                # Readable names
                display_name = {
                    "URBAN_PLANNING": "URBAN PLANNING & LAND USE",
                    "IOT_TECHNOLOGY": "IoT & TECHNOLOGY INFRASTRUCTURE",
                    "SUSTAINABILITY": "SUSTAINABILITY & RESILIENCE",
                    "TRANSPORTATION": "TRANSPORTATION & MOBILITY",
                    "MUNICIPAL_FINANCE": "MUNICIPAL FINANCE & FUNDING",
                    "COMMUNITY_ENGAGEMENT": "COMMUNITY ENGAGEMENT & EQUITY",
                    "PRIVACY_SECURITY": "PRIVACY & CYBERSECURITY"
                }.get(agent_name, agent_name)
                
                output_lines.append("─" * 80)
                output_lines.append(f"{emoji} {display_name}")
                output_lines.append("─" * 80)
                output_lines.append("")
                output_lines.append(msg.text)
                output_lines.append("")
                break  # Only use the final message
    
    output_lines.append("=" * 80)
    output_lines.append("✅ Smart City Analysis Complete - All perspectives reviewed")
    output_lines.append("=" * 80)
    
    formatted_output = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"smart_city_analysis_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"\n💾 Smart city analysis saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️ Failed to save output to file: {e}")
    
    return formatted_output


def setup_tracing():
    """Set up tracing based on environment variables.
    
    Priority order:
    1. OTLP endpoint (OTLP_ENDPOINT)
    2. Application Insights (APPLICATIONINSIGHTS_CONNECTION_STRING)
    3. Console tracing (ENABLE_CONSOLE_TRACING=true)
    """
    # Check for OTLP endpoint
    otlp_endpoint = os.environ.get("OTLP_ENDPOINT")
    if otlp_endpoint:
        print(f"📊 Tracing Mode: OTLP Endpoint ({otlp_endpoint})")
        print("   Make sure you have an OTLP receiver running (e.g., Jaeger, Zipkin)")
        setup_observability(
            enable_sensitive_data=True,
            otlp_endpoint=otlp_endpoint,
        )
        return
    
    # Check for Application Insights connection string
    app_insights_conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn_str:
        print("📊 Tracing Mode: Application Insights (Direct)")
        setup_observability(
            enable_sensitive_data=True,
            applicationinsights_connection_string=app_insights_conn_str,
        )
        return
    
    # Check for console tracing
    if os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true":
        print("📊 Tracing Mode: Console Output")
        print("   Traces will be printed to the console")
        setup_observability(enable_sensitive_data=True)
        return
    
    print("📊 Tracing: Disabled")
    print("   To enable tracing, set one of:")
    print("   - OTLP_ENDPOINT=http://localhost:4317 (requires OTLP receiver)")
    print("   - APPLICATIONINSIGHTS_CONNECTION_STRING=<your-connection-string>")
    print("   - ENABLE_CONSOLE_TRACING=true (console output)")


async def create_smart_city_workflow():
    """Create and return a smart city infrastructure workflow for DevUI."""
    # Create async context stack for managing resources
    stack = AsyncExitStack()
    
    # Initialize async credential (no context manager needed)
    credential = AzureCliCredential()
    
    # Initialize Azure OpenAI client
    chat_client = AzureOpenAIChatClient(
        credential=credential,
        endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )
    
    # Create seven specialized smart city agents
    urban_planning = chat_client.create_agent(
        instructions=(
            "You're an urban planner and city development expert specializing in land use and community impact. "
            "Analyze zoning requirements, density, spatial planning, and community integration. "
            "Consider: comprehensive planning, mixed-use development, transit-oriented development (TOD), "
            "zoning compliance, building codes, density analysis, open space requirements, "
            "neighborhood character, gentrification concerns, historic preservation, "
            "urban design principles, walkability, and quality of life impacts. "
            "Focus on livable, equitable, and sustainable urban development."
        ),
        name="urban_planning",
    )

    iot_technology = chat_client.create_agent(
        instructions=(
            "You're an IoT architect and smart city technology expert. "
            "Analyze sensor networks, connectivity, data platforms, and edge computing infrastructure. "
            "Consider: IoT sensor deployment (air quality, traffic, noise, occupancy), "
            "network architecture (5G, LoRaWAN, NB-IoT), edge computing vs cloud processing, "
            "data integration platforms, interoperability standards (FIWARE, CityIQ), "
            "real-time analytics, digital twin implementations, API management, "
            "scalability, redundancy, and technology lifecycle. "
            "Provide practical technology recommendations and architecture guidance."
        ),
        name="iot_technology",
    )

    sustainability = chat_client.create_agent(
        instructions=(
            "You're a sustainability and climate resilience expert for urban infrastructure. "
            "Analyze environmental impact, renewable energy, circular economy, and climate adaptation. "
            "Consider: carbon footprint reduction, renewable energy integration (solar, wind, geothermal), "
            "energy efficiency, green building standards (LEED, Living Building Challenge), "
            "circular economy principles, waste reduction, water conservation, "
            "climate adaptation and resilience, heat island mitigation, green infrastructure, "
            "biodiversity, and long-term environmental sustainability. "
            "Focus on net-zero pathways and climate-positive outcomes."
        ),
        name="sustainability",
    )
    
    transportation = chat_client.create_agent(
        instructions=(
            "You're a transportation planner and mobility expert specializing in smart transportation systems. "
            "Analyze traffic management, public transit, micromobility, and autonomous vehicles. "
            "Consider: traffic flow optimization, congestion pricing, intelligent transportation systems (ITS), "
            "public transit integration (bus, rail, BRT), first/last mile solutions, "
            "bike lanes and pedestrian infrastructure, micromobility (e-scooters, bike shares), "
            "EV charging infrastructure, autonomous vehicle readiness, mobility-as-a-service (MaaS), "
            "parking management, and multimodal connectivity. "
            "Prioritize safety, accessibility, and reduced car dependency."
        ),
        name="transportation",
    )
    
    municipal_finance = chat_client.create_agent(
        instructions=(
            "You're a municipal finance and infrastructure funding expert. "
            "Analyze funding sources, public-private partnerships, grants, and financial feasibility. "
            "Consider: municipal bonds, federal/state grants (USDOT, EPA, HUD), "
            "public-private partnerships (P3), infrastructure banks, tax increment financing (TIF), "
            "user fees and tariffs, cost-benefit analysis, ROI calculations, "
            "operating vs capital budgets, lifecycle cost analysis, "
            "risk allocation, procurement strategies, and long-term financial sustainability. "
            "Provide realistic budget estimates and funding strategies."
        ),
        name="municipal_finance",
    )
    
    community_engagement = chat_client.create_agent(
        instructions=(
            "You're a community engagement and equity specialist for urban development. "
            "Analyze stakeholder participation, social equity, accessibility, and digital inclusion. "
            "Consider: participatory planning, community input mechanisms, equity analysis, "
            "environmental justice, affordable access, digital divide and inclusion, "
            "accessibility for disabilities (ADA compliance), multilingual outreach, "
            "displacement and gentrification mitigation, benefits distribution, "
            "workforce development, local hiring, and meaningful community co-design. "
            "Prioritize inclusive processes and equitable outcomes for all residents."
        ),
        name="community_engagement",
    )
    
    privacy_security = chat_client.create_agent(
        instructions=(
            "You're a privacy, data governance, and cybersecurity expert for smart city infrastructure. "
            "Analyze data protection, surveillance ethics, and security architecture. "
            "Consider: data governance frameworks, privacy by design, personally identifiable information (PII) protection, "
            "surveillance technology ethics, facial recognition policies, data retention and deletion, "
            "cybersecurity for critical infrastructure, OT/IT convergence security, "
            "IoT device security, encryption (data at rest and in transit), "
            "access controls, incident response, GDPR/CCPA compliance, and public trust. "
            "Balance innovation with privacy rights and security best practices."
        ),
        name="privacy_security",
    )
    
    # Build the smart city workflow with structured input handling
    # Create custom dispatcher that handles SmartCityInput
    class SmartCityDispatcher(Executor):
        """Dispatcher that extracts description from SmartCityInput and forwards to agents."""
        
        @handler
        async def dispatch(self, input_data: SmartCityInput, ctx: WorkflowContext) -> None:
            """Extract description and send to all smart city agents.
            
            Args:
                input_data: SmartCityInput with description field
                ctx: WorkflowContext for dispatching to agents
            """
            from agent_framework._workflows._executor import AgentExecutorRequest
            request = AgentExecutorRequest(
                messages=[ChatMessage(Role.USER, text=input_data.description)],
                should_respond=True
            )
            await ctx.send_message(request)
    
    # Build workflow with custom components
    dispatcher = SmartCityDispatcher(id="smart_city_dispatcher")
    aggregator_func = format_smart_city_results
    
    # Use WorkflowBuilder to create the complete workflow
    from agent_framework._workflows._concurrent import _CallbackAggregator
    
    builder = WorkflowBuilder()
    builder.set_start_executor(dispatcher)
    
    # Add all smart city agent participants
    agents = [
        urban_planning,
        iot_technology,
        sustainability,
        transportation,
        municipal_finance,
        community_engagement,
        privacy_security
    ]
    builder.add_fan_out_edges(dispatcher, agents)
    
    # Add aggregator
    aggregator_executor = _CallbackAggregator(aggregator_func)
    builder.add_fan_in_edges(agents, aggregator_executor)
    
    workflow = builder.build()
    
    # Store the stack for cleanup
    workflow._devui_stack = stack
    
    return workflow


def launch_devui():
    """Launch the DevUI interface with the smart city workflow."""
    from agent_framework.devui import serve
    
    # Set up tracing based on environment variables
    setup_tracing()
    
    # Create the workflow asynchronously
    workflow = asyncio.run(create_smart_city_workflow())
    
    # Check if DevUI tracing should be enabled
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching Smart City Infrastructure Workflow in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Smart City Analysis (Fan-out/Fan-in)")
    print("✅ Participants: 7 specialized urban infrastructure experts")
    print("✅ Web UI: http://localhost:8096")
    print("✅ API: http://localhost:8096/v1/*")
    print("✅ Entity ID: workflow_smart_city")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    if enable_devui_tracing:
        print("   → Traces will appear in DevUI web interface")
    print("=" * 70)
    print()
    print("💡 Try these smart city scenarios in the DevUI:")
    print()
    print("🌐 IoT & Connectivity:")
    print("   - City-wide air quality monitoring with adaptive traffic management")
    print("   - Digital twin platform for infrastructure and emergency response")
    print("   - 5G network for connected vehicles and smart buildings")
    print()
    print("⚡ Energy & Sustainability:")
    print("   - Smart grid with distributed renewables and battery storage")
    print("   - Net-zero district with solar, geothermal, and energy monitoring")
    print("   - Smart street lighting with EV charging and sensors")
    print()
    print("🚦 Transportation & Mobility:")
    print("   - Autonomous shuttle network for downtown and transit hubs")
    print("   - Integrated mobility-as-a-service platform (MaaS)")
    print("   - Smart parking and congestion management system")
    print()
    print("♻️ Circular Economy:")
    print("   - AI-powered waste management with route optimization")
    print("   - Water quality monitoring and leak detection network")
    print("   - Urban farming and food system integration")
    print()
    print("⚡ Each query will be analyzed by 7 smart city experts:")
    print("   • Urban Planning: Zoning, density, community impact")
    print("   • IoT & Technology: Sensors, connectivity, data platforms")
    print("   • Sustainability: Green energy, carbon reduction, resilience")
    print("   • Transportation: Traffic, public transit, micromobility, AVs")
    print("   • Municipal Finance: Bonds, P3s, grants, cost-benefit")
    print("   • Community Engagement: Equity, accessibility, participation")
    print("   • Privacy & Security: Data governance, surveillance ethics, cybersecurity")
    print()
    print("⌨️  Press Ctrl+C to stop the server")
    print()
    
    # Launch the DevUI server
    try:
        serve(
            entities=[workflow],
            port=8096,
            auto_open=True,
            tracing_enabled=enable_devui_tracing,
        )
    finally:
        # Clean up resources
        if hasattr(workflow, "_devui_stack"):
            asyncio.run(workflow._devui_stack.aclose())


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down smart city workflow server...")

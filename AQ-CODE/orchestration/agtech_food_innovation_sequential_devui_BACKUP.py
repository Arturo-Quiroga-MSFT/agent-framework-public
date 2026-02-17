# Copyright (c) Microsoft. All rights reserved.

"""
AgTech/Food Innovation Sequential Workflow - DevUI Version with Tracing

This workflow creates a sequential pipeline of 7 AgTech/food innovation experts who
build upon each other's analysis in a specific order to provide comprehensive insights.

The workflow uses a sequential pattern where:
- User describes an AgTech or food innovation concept
- Each agent processes the full conversation history sequentially
- Agents build upon previous agents' insights
- Results flow through the pipeline: Agronomy → Engineering → Food Science → 
  Sustainability → Economics → Supply Chain → Regulations

AGTECH AGENTS (Sequential Order):
1. Agronomy Specialist: Crop science, yield optimization, soil health
2. AgTech Engineer: Automation, robotics, AI/ML, precision agriculture
3. Food Science: Nutrition, taste, texture, shelf life, food safety
4. Sustainability: Water usage, emissions, biodiversity, regenerative practices
5. Ag Economics: Farm adoption, pricing, subsidies, market access
6. Supply Chain & Distribution: Cold chain, logistics, retail partnerships
7. Food Regulations: FDA, USDA, organic certification, labeling

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
from datetime import datetime
from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from typing_extensions import Never

from agent_framework import (
    Message,
    Executor,
    SequentialBuilder,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowOutputEvent,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.observability import configure_otel_providers
from azure.identity import AzureCliCredential
from pydantic import BaseModel, Field

# Load environment variables from workflows/.env file
load_dotenv(Path(__file__).parent.parent / ".env")


class AgTechInput(BaseModel):
    """Input model for AgTech/food innovation analysis."""
    
    description: str = Field(
        ...,
        description="Describe the agricultural technology, food innovation, vertical farming system, or alternative protein concept you want to analyze",
        examples=[
            "Vertical farming system using LED grow lights and AI-powered nutrient delivery for leafy greens in urban warehouses",
            "Precision agriculture platform with drones, soil sensors, and ML-based crop disease prediction for corn and soybean farms",
            "Cell-cultured chicken production facility using bioreactors and growth media optimization for cost-effective alternative protein",
            "Regenerative agriculture program integrating cover crops, no-till farming, and carbon credit monetization for grain farmers",
            "Autonomous robotic harvesting system with computer vision for delicate fruits like strawberries and tomatoes",
            "Indoor aquaponics system combining tilapia farming with hydroponic vegetable production for local food systems",
            "Food waste valorization platform converting agricultural byproducts into animal feed, biofuels, and compost",
            "Blockchain-based traceability platform for organic produce from farm to consumer with quality monitoring",
            "Insect protein production facility rearing black soldier fly larvae on food waste streams for sustainable animal feed",
            "Algae photobioreactor system producing omega-3 rich biomass for functional food ingredients",
            "CRISPR-enabled gene edited tomato variety targeting higher lycopene and longer shelf life with regulatory pathway assessment",
            "Edge AI device network performing on-field real-time plant stress detection using multispectral camera modules",
            "Satellite + SAR + weather fusion analytics platform estimating regional soil moisture and yield forecasts for insurers",
            "Biodegradable smart packaging with embedded freshness indicators to extend leafy greens shelf life in cold chain",
            "On-farm anaerobic digester converting dairy manure into renewable natural gas and fertilizer coproducts with carbon credit stacking",
            "Autonomous weeding robots using machine vision and laser micro-targeting to reduce herbicide inputs in specialty crops",
            "Desalination-powered greenhouse cluster using brine valorization and solar thermal integration for arid-region vegetable production",
            "Precision fermentation facility producing casein proteins for animal-free cheeses with downstream purification optimization",
            "Regenerative agroforestry system integrating cacao, shade trees, and livestock with biodiversity impact quantification",
            "Aquaculture RAS (recirculating aquaculture system) for shrimp paired with nutrient recovery hydroponic lettuce modules",
            "Digital farm management platform offering variable rate nitrogen prescriptions based on sensor + historical yield map analytics",
            "Cold chain optimization platform using IoT temperature loggers + predictive spoilage modeling for fresh berry distribution"
        ]
    )


def setup_tracing():
    """Set up tracing based on environment variables."""
    otlp_endpoint = os.environ.get("OTLP_ENDPOINT")
    if otlp_endpoint:
        print(f"📊 Tracing Mode: OTLP Endpoint ({otlp_endpoint})")
        configure_otel_providers(enable_sensitive_data=True)
        return
    
    app_insights_conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if app_insights_conn_str:
        print("📊 Tracing Mode: Application Insights")
        configure_otel_providers(enable_sensitive_data=True)
        return
    
    if os.environ.get("ENABLE_CONSOLE_TRACING", "").lower() == "true":
        print("📊 Tracing Mode: Console Output")
        configure_otel_providers(enable_sensitive_data=True)
        return
    
    print("📊 Tracing: Disabled")


# Global chat client (shared across workflow executions)
chat_client = None

def get_chat_client():
    """Get or create the Azure OpenAI chat client."""
    global chat_client
    if chat_client is None:
        chat_client = AzureOpenAIChatClient(
            credential=AzureCliCredential(),
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
        )
    return chat_client


async def create_sequential_agents():
    """Create the 7 sequential AgTech agents."""
    client = get_chat_client()
    
    # Create seven specialized AgTech agents in sequential order
    # Agent 1: Agronomy foundation
    agronomy = client.as_agent(
        instructions=(
            "You're an agronomist and crop science expert. Analyze the agricultural and biological aspects. "
            "Focus on: crop selection, growing conditions, yield potential, soil requirements, "
            "plant genetics, pest/disease management, growing cycles, and agronomic feasibility. "
            "Provide your analysis concisely (3-5 key points). Your insights will inform the engineering team."
        ),
        name="agronomy",
    )
    
    # Agent 2: Engineering builds on agronomy
    engineering = client.as_agent(
        instructions=(
            "You're an AgTech engineer specializing in automation and precision agriculture. "
            "Building on the agronomy analysis above, focus on: technology implementation, automation systems, "
            "robotics, AI/ML applications, sensor networks, drones, precision irrigation, "
            "IoT infrastructure, and technical scalability. "
            "Provide concise technical recommendations (3-5 key points). Your analysis informs food science."
        ),
        name="engineering",
    )
    
    # Agent 3: Food science builds on agronomy + engineering
    food_science = client.as_agent(
        instructions=(
            "You're a food scientist analyzing product quality and safety. "
            "Considering the agronomy and engineering insights above, focus on: nutritional profile, "
            "taste and texture, shelf life, food safety requirements, quality control, "
            "processing needs, packaging, and consumer acceptance. "
            "Provide key food science considerations (3-5 points). Your analysis guides sustainability review."
        ),
        name="food_science",
    )
    
    # Agent 4: Sustainability builds on previous three
    sustainability = client.as_agent(
        instructions=(
            "You're a sustainability and environmental impact expert. "
            "Building on the technical and product analyses above, evaluate: water usage, "
            "carbon footprint, energy consumption, biodiversity impact, waste streams, "
            "regenerative practices, climate resilience, and circular economy potential. "
            "Provide sustainability assessment (3-5 key metrics/impacts). Your analysis informs economics."
        ),
        name="sustainability",
    )
    
    # Agent 5: Economics builds on all technical/environmental factors
    ag_economics = client.as_agent(
        instructions=(
            "You're an agricultural economist analyzing market viability. "
            "Considering all technical, product, and environmental factors above, assess: "
            "production costs, pricing strategy, farm-level economics, adoption barriers, "
            "subsidy programs, market demand, competitive positioning, and ROI for farmers. "
            "Provide economic analysis (3-5 key financial considerations). Your insights guide supply chain planning."
        ),
        name="economics",
    )
    
    # Agent 6: Supply chain builds on complete technical + economic picture
    supply_chain = client.as_agent(
        instructions=(
            "You're a food supply chain and distribution expert. "
            "Considering the complete product, sustainability, and economics analysis above, focus on: "
            "cold chain requirements, logistics, transportation, storage, retail partnerships, "
            "direct-to-consumer channels, shelf life constraints, and distribution scalability. "
            "Provide supply chain strategy (3-5 key logistics considerations). Your analysis informs regulatory review."
        ),
        name="supply_chain",
    )
    
    # Agent 7: Regulations - final compliance layer
    regulations = client.as_agent(
        instructions=(
            "You're a food and agriculture regulatory compliance expert. "
            "Reviewing the complete analysis above (production, product, distribution), identify: "
            "FDA food safety requirements, USDA regulations, organic certification needs, "
            "labeling requirements, international standards, environmental permits, "
            "and compliance roadmap. "
            "Provide final regulatory guidance (3-5 critical compliance requirements for go-to-market)."
        ),
        name="regulations",
    )
    
    # Return the agents in sequential order
    return [
        agronomy,
        engineering,
        food_science,
        sustainability,
        ag_economics,
        supply_chain,
        regulations
    ]


def format_sequential_results(conversation: list[Message]) -> str:
    """Format sequential conversation into readable output with file save.
    
    Args:
        conversation: Complete list of Message objects from sequential workflow
        
    Returns:
        Formatted string with all sequential agent responses
    """
    # Get all messages from the conversation
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("🌾 SEQUENTIAL AGTECH/FOOD INNOVATION ANALYSIS")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("📋 ANALYSIS FLOW: Agronomy → Engineering → Food Science → Sustainability")
    output_lines.append("                 → Economics → Supply Chain → Regulations")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Emoji mapping for agents
    agent_emoji = {
        "user": "👤",
        "agronomy": "🌱",
        "engineering": "🤖",
        "food_science": "🧪",
        "sustainability": "♻️",
        "economics": "💰",
        "supply_chain": "🚚",
        "regulations": "📋"
    }
    
    # Display names
    agent_names = {
        "user": "USER INPUT",
        "agronomy": "AGRONOMY SPECIALIST",
        "engineering": "AGTECH ENGINEER",
        "food_science": "FOOD SCIENTIST",
        "sustainability": "SUSTAINABILITY EXPERT",
        "economics": "AG ECONOMIST",
        "supply_chain": "SUPPLY CHAIN & DISTRIBUTION",
        "regulations": "FOOD REGULATIONS"
    }
    
    for i, msg in enumerate(conversation, start=1):
        name = msg.author_name or ("user" if msg.role == "user" else "assistant")
        emoji = agent_emoji.get(name, "🔹")
        display_name = agent_names.get(name, name.upper())
        
        output_lines.append("─" * 80)
        output_lines.append(f"{emoji} STEP {i}: {display_name}")
        output_lines.append("─" * 80)
        output_lines.append("")
        output_lines.append(msg.text)
        output_lines.append("")
    
    output_lines.append("=" * 80)
    output_lines.append("✅ Sequential Analysis Complete - All 7 experts reviewed")
    output_lines.append("=" * 80)
    
    formatted_output = "\n".join(output_lines)
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "workflow_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"agtech_sequential_analysis_{timestamp}.txt"
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"\n💾 AgTech analysis saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️ Failed to save output to file: {e}")
    
    return formatted_output


class SequentialWorkflowExecutor(Executor):
    """Executor that wraps a sequential workflow and runs it internally."""
    
    def __init__(self, agents: list, **kwargs):
        """Initialize with list of agents for sequential processing.
        
        Args:
            agents: List of agents to process sequentially
            **kwargs: Additional Executor arguments
        """
        super().__init__(**kwargs)
        self.agents = agents
        self._workflow = SequentialBuilder().participants(agents).build()
    
    @handler
    async def run_sequential(self, input_text: str, ctx: WorkflowContext[Never, list[Message]]) -> None:
        """Run the sequential workflow and capture the final conversation.
        
        Args:
            input_text: User input text to process through sequential agents
            ctx: WorkflowContext for sending the result
        """
        # Run the sequential workflow and collect outputs
        outputs: list[list[Message]] = []
        async for event in self._workflow.run_stream(input_text):
            if isinstance(event, WorkflowOutputEvent):
                outputs.append(event.data)
        
        # Send the final conversation (list of Messages) to the next executor
        if outputs:
            await ctx.send_message(outputs[-1])


class AgTechInputDispatcher(Executor):
    """Dispatcher that converts AgTechInput to a string for the sequential workflow."""
    
    @handler
    async def dispatch_to_sequential(self, input_data: AgTechInput, ctx: WorkflowContext[Never, str]) -> None:
        """Extract description from AgTechInput and send as string.
        
        Args:
            input_data: AgTechInput with description field
            ctx: WorkflowContext for sending messages
        """
        # Sequential workflow expects a string input
        await ctx.send_message(input_data.description)


class SequentialOutputFormatter(Executor):
    """Executor that formats the complete sequential conversation for display."""
    
    @handler
    async def format_output(self, conversation: list[Message], ctx: WorkflowContext[list[Message], str]) -> None:
        """Format the complete sequential conversation and yield it.
        
        Args:
            conversation: Complete list of Message objects from the sequential workflow
            ctx: WorkflowContext for yielding formatted output
        """
        formatted_output = format_sequential_results(conversation)
        await ctx.yield_output(formatted_output)


async def create_agtech_workflow():
    """Create and return the DevUI-compatible AgTech sequential workflow."""
    # Get the 7 sequential agents
    agents = await create_sequential_agents()
    
    # Create a wrapper executor that runs the sequential workflow internally
    sequential_executor = SequentialWorkflowExecutor(
        agents=agents,
        id="sequential_processor"
    )
    
    # Create dispatcher that converts AgTechInput to string
    dispatcher = AgTechInputDispatcher(id="input_dispatcher")
    
    # Create output formatter to handle the final conversation list
    output_formatter = SequentialOutputFormatter(id="output_formatter")
    
    # Build the workflow: dispatcher -> sequential executor -> formatter
    builder = WorkflowBuilder(start_executor=dispatcher)
    builder.add_edge(dispatcher, sequential_executor)
    builder.add_edge(sequential_executor, output_formatter)
    
    workflow = builder.build()
    
    return workflow


def launch_devui():
    """Launch the DevUI interface with the AgTech sequential workflow."""
    from agent_framework.devui import serve
    
    # Set up tracing
    setup_tracing()
    
    # Create the workflow
    workflow = asyncio.run(create_agtech_workflow())
    
    enable_devui_tracing = os.environ.get("ENABLE_DEVUI_TRACING", "").lower() == "true"
    
    print("=" * 70)
    print("🚀 Launching AgTech/Food Innovation Sequential Workflow in DevUI")
    print("=" * 70)
    print("✅ Workflow Type: Sequential (Pipeline)")
    print("✅ Participants: 7 AgTech experts (sequential processing)")
    print("✅ Web UI: http://localhost:8097")
    print("✅ API: http://localhost:8097/v1/*")
    print("✅ Entity ID: workflow_agtech_sequential")
    print(f"🔍 DevUI Tracing: {'Enabled' if enable_devui_tracing else 'Disabled'}")
    print("=" * 70)
    print()
    print("💡 Try these AgTech/food innovation scenarios:")
    print()
    print("🌱 Vertical & Indoor Farming:")
    print("   - LED-based vertical farming for urban leafy greens")
    print("   - Indoor aquaponics combining fish and vegetable production")
    print("   - Container farms for local fresh produce")
    print()
    print("🤖 Precision Agriculture:")
    print("   - Drone + AI platform for crop disease prediction")
    print("   - Autonomous robotic harvesting for delicate fruits")
    print("   - Soil sensor networks with variable rate irrigation")
    print()
    print("🍖 Alternative Proteins:")
    print("   - Cell-cultured chicken production facility")
    print("   - Precision fermentation for dairy proteins")
    print("   - Plant-based meat with improved texture and nutrition")
    print()
    print("♻️ Regenerative & Sustainable:")
    print("   - Regenerative agriculture with carbon credit monetization")
    print("   - Food waste valorization into feed and biofuels")
    print("   - Blockchain traceability for organic produce")
    print()
    print("🛰️ Remote Sensing & Analytics:")
    print("   - Satellite + SAR fusion for regional soil moisture & yield prediction")
    print("   - Multispectral drone + edge AI stress detection network")
    print("   - Weather + imagery powered insurer risk scoring platform")
    print()
    print("🧬 Biotech & Novel Inputs:")
    print("   - CRISPR-edited crops targeting nutrient density & shelf life")
    print("   - Microbial biofertilizer consortia for nitrogen fixation")
    print("   - Black soldier fly larvae production for circular protein feed")
    print()
    print("🌐 Digital & Data Platforms:")
    print("   - Variable rate nitrogen prescription engine from historical yield maps")
    print("   - Farm management platform integrating IoT soil sensor telemetry")
    print("   - Blockchain + IoT cold chain integrity monitoring")
    print()
    print("🧪 Packaging & Shelf Life:")
    print("   - Biodegradable smart packaging with freshness indicators")
    print("   - Modified atmosphere packaging to extend berry shelf life")
    print("   - Edible coatings reducing moisture loss in leafy greens")
    print()
    print("🔄 Circular & Energy Systems:")
    print("   - Anaerobic digestion of dairy manure for RNG + fertilizer")
    print("   - Waste heat recovery integration in vertical farms")
    print("   - Brine valorization from desalination-powered greenhouses")
    print()
    print("📊 Sequential Analysis Flow:")
    print("   1. 🌱 Agronomy: Crop science, yield, soil requirements")
    print("   2. 🤖 Engineering: Automation, robotics, AI/ML, sensors")
    print("   3. 🧪 Food Science: Nutrition, taste, safety, shelf life")
    print("   4. ♻️ Sustainability: Water, carbon, biodiversity, waste")
    print("   5. 💰 Economics: Costs, pricing, ROI, farm adoption")
    print("   6. 🚚 Supply Chain: Logistics, cold chain, distribution")
    print("   7. 📋 Regulations: FDA, USDA, organic, labeling")
    print()
    print("⌨️  Press Ctrl+C to stop the server")
    print()
    
    # Launch the DevUI server
    try:
        serve(
            entities=[workflow],
            port=8097,
            auto_open=True,
            instrumentation_enabled=enable_devui_tracing,
        )
    finally:
        print("\n🛑 AgTech workflow server stopped")


if __name__ == "__main__":
    try:
        launch_devui()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AgTech workflow server...")

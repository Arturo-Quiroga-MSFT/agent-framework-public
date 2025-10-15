# AgTech/Food Innovation Sequential Workflow

## Overview

A sequential pipeline workflow that analyzes agricultural technology and food innovation concepts through 7 specialized experts. Each agent builds upon previous analyses to provide comprehensive, domain-specific insights.

## Workflow Pattern

**Type:** Sequential (Pipeline)  
**Agents:** 7 specialized AgTech experts  
**Processing:** Each agent receives full conversation history and adds sequential analysis  
**Visualization:** All 7 agents are visible as separate nodes in DevUI

## Agent Pipeline

```
        Input Dispatcher
              ↓
    🌱 Agronomy Specialist
              ↓
     🤖 AgTech Engineer
              ↓
      🧪 Food Scientist
              ↓
   ♻️ Sustainability Expert
              ↓
       💰 Ag Economist
              ↓
🚚 Supply Chain & Distribution
              ↓
    📋 Food Regulations
              ↓
      Output Formatter
```

**DevUI Graph:** Shows 9 executor nodes (dispatcher → 7 agents → formatter)

## Agent Responsibilities

1. **🌱 Agronomy Specialist**
   - Crop science, yield optimization, soil health
   - Plant genetics, pest/disease management
   - Growing conditions and agronomic feasibility

2. **🤖 AgTech Engineer**
   - Automation systems, robotics, precision agriculture
   - AI/ML applications, sensor networks, drones
   - IoT infrastructure and technical scalability

3. **🧪 Food Scientist**
   - Nutritional profile, taste, texture, shelf life
   - Food safety requirements and quality control
   - Processing needs and consumer acceptance

4. **♻️ Sustainability Expert**
   - Water usage, carbon footprint, energy consumption
   - Biodiversity impact, waste streams
   - Regenerative practices and climate resilience

5. **💰 Ag Economist**
   - Production costs, pricing strategy, ROI
   - Farm adoption barriers and market demand
   - Subsidy programs and competitive positioning

6. **🚚 Supply Chain & Distribution**
   - Cold chain requirements, logistics, transportation
   - Retail partnerships and distribution scalability
   - Direct-to-consumer channels

7. **📋 Food Regulations**
   - FDA/USDA compliance requirements
   - Organic certification and labeling standards
   - Environmental permits and regulatory roadmap

## Use Cases

- **Vertical/Indoor Farming:** LED-based systems, aquaponics, container farms
- **Precision Agriculture:** Drone + AI platforms, robotic harvesting, soil sensors
- **Alternative Proteins:** Cell-cultured meat, precision fermentation, plant-based
- **Regenerative Practices:** Carbon credit monetization, food waste valorization
- **Remote Sensing:** Satellite analytics, multispectral imaging, yield prediction
- **Biotech Innovation:** CRISPR-edited crops, microbial biofertilizers
- **Digital Platforms:** Variable rate prescriptions, farm management systems
- **Smart Packaging:** Biodegradable materials, freshness indicators
- **Circular Economy:** Anaerobic digestion, waste heat recovery, brine valorization

## Running the Workflow

### Prerequisites
- Azure OpenAI access configured in `.env` file
- Azure CLI authentication: `az login`

### Launch DevUI
```bash
python agtech_food_innovation_sequential_devui.py
```

Access at: **http://localhost:8097**

## Output

- **Console:** Real-time sequential processing
- **DevUI:** Interactive visualization with scrollable output
- **File:** Saved to `workflow_outputs/agtech_sequential_analysis_<timestamp>.txt`

## Key Features

✅ Sequential processing - each agent builds on previous insights  
✅ Full conversation history available to all agents  
✅ **All 7 agents visible in DevUI graph** - easy to track workflow execution  
✅ Structured 7-step analysis framework  
✅ Formatted output with clear agent attribution  
✅ Automatic file saving for reference  
✅ Scrollable DevUI output panel  
✅ Click any agent node to view its specific input/output  

## Framework Compatibility

Updated for **Microsoft Agent Framework (new structure)**:
- Individual `AgentExecutor` wrappers for each agent (better visualization)
- Proper type annotations with `WorkflowContext[Input, Output]`
- Sequential edge connections between all agents
- `AgentExecutorRequest/Response` for inter-agent communication
- Compatible with DevUI tracing and interactive debugging

## Workflow Architecture

The workflow uses **explicit agent chaining** for maximum visibility:

1. **Input Dispatcher** - Converts user input to `AgentExecutorRequest`
2. **7 Agent Executors** - Each agent wrapped in `AgentExecutor` for DevUI visualization
3. **Sequential Edges** - Direct connections: agronomy → engineering → food_science → etc.
4. **Output Formatter** - Formats final `AgentExecutorResponse` into readable text

This architecture allows you to:
- **Click each agent node** in DevUI to inspect its state
- **See real-time progress** as agents process sequentially
- **Debug issues** by examining individual agent inputs/outputs
- **Understand the flow** with visual sequential connections

## Example Input

```
Indoor aquaponics system combining tilapia farming with 
hydroponic vegetable production for local food systems
```

## Example Output Structure

```
🌾 SEQUENTIAL AGTECH/FOOD INNOVATION ANALYSIS
═══════════════════════════════════════════════════════════
📋 ANALYSIS FLOW: Agronomy → Engineering → Food Science 
                 → Sustainability → Economics → Supply Chain 
                 → Regulations
═══════════════════════════════════════════════════════════

🌱 STEP 1: AGRONOMY SPECIALIST
[Crop science analysis...]

🤖 STEP 2: AGTECH ENGINEER
[Engineering recommendations...]

🧪 STEP 3: FOOD SCIENTIST
[Food quality insights...]

♻️ STEP 4: SUSTAINABILITY EXPERT
[Environmental impact assessment...]

💰 STEP 5: AG ECONOMIST
[Economic viability analysis...]

🚚 STEP 6: SUPPLY CHAIN & DISTRIBUTION
[Logistics and distribution strategy...]

📋 STEP 7: FOOD REGULATIONS
[Compliance requirements...]

✅ Sequential Analysis Complete - All 7 experts reviewed
```

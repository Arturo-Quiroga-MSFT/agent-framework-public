# Smart City Infrastructure Workflow

## Overview

A concurrent fan-out/fan-in workflow that analyzes smart city infrastructure projects through 7 specialized urban experts. All agents process the input simultaneously and their insights are aggregated into a comprehensive analysis.

## Workflow Pattern

**Type:** Concurrent (Fan-out/Fan-in)  
**Agents:** 7 specialized smart city experts  
**Processing:** All agents analyze input in parallel, results aggregated at the end

## Agent Architecture

```
                    User Input
                        ↓
              Smart City Dispatcher
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   🏗️ Urban         📡 IoT &        🌱 Sustainability
    Planning        Technology
        ↓               ↓               ↓
   🚦 Transport     💰 Municipal    👥 Community
                    Finance         Engagement
        ↓               ↓               ↓
                   🔐 Privacy &
                    Security
                        ↓
              Smart City Aggregator
                        ↓
                Formatted Output
```

## Agent Specializations

1. **🏗️ Urban Planning & Land Use**
   - Zoning requirements, density analysis
   - Mixed-use development, transit-oriented development (TOD)
   - Community impact, neighborhood character

2. **📡 IoT & Technology Infrastructure**
   - Sensor networks (air quality, traffic, noise)
   - Network architecture (5G, LoRaWAN, NB-IoT)
   - Edge computing, digital twin implementations

3. **🌱 Sustainability & Resilience**
   - Renewable energy integration, carbon footprint
   - Green building standards, circular economy
   - Climate adaptation and biodiversity

4. **🚦 Transportation & Mobility**
   - Traffic flow optimization, intelligent transportation systems (ITS)
   - Public transit integration, micromobility
   - Autonomous vehicles, mobility-as-a-service (MaaS)

5. **💰 Municipal Finance & Funding**
   - Municipal bonds, public-private partnerships (P3)
   - Federal/state grants, cost-benefit analysis
   - Lifecycle cost analysis, ROI calculations

6. **👥 Community Engagement & Equity**
   - Participatory planning, stakeholder input
   - Environmental justice, digital inclusion
   - Accessibility (ADA compliance), displacement mitigation

7. **🔐 Privacy & Cybersecurity**
   - Data governance frameworks, privacy by design
   - Surveillance ethics, PII protection
   - Cybersecurity for critical infrastructure

## Use Cases

- **IoT & Connectivity:** Air quality monitoring, digital twins, 5G networks
- **Energy & Sustainability:** Smart grids, net-zero districts, renewable integration
- **Transportation:** Autonomous shuttles, MaaS platforms, smart parking
- **Circular Economy:** Waste management, water monitoring, urban farming
- **Public Safety:** Emergency response, predictive analytics
- **Smart Buildings:** Energy management, occupancy sensors, automated systems

## Running the Workflow

### Prerequisites
- Azure OpenAI access configured in `.env` file
- Azure CLI authentication: `az login`

### Launch DevUI
```bash
python smart_city_infrastructure_devui.py
```

Access at: **http://localhost:8096**

## Output

- **Console:** Real-time concurrent processing status
- **DevUI:** Interactive visualization with scrollable output panel
- **File:** Saved to `workflow_outputs/smart_city_analysis_<timestamp>.txt`

## Key Features

✅ Concurrent processing - all 7 agents analyze simultaneously  
✅ Independent domain-specific perspectives  
✅ Comprehensive multi-disciplinary analysis  
✅ Aggregated output with clear agent attribution  
✅ Automatic file saving for reference  
✅ Scrollable DevUI output panel with custom scrollbar  

## Framework Compatibility

Updated for **Microsoft Agent Framework (new structure)**:
- Custom `Executor` classes for dispatcher and aggregator
- Proper type annotations with `WorkflowContext` and `AgentExecutorResponse`
- `WorkflowBuilder` with fan-out/fan-in edge patterns
- Compatible with DevUI tracing and visualization

## Example Input

```
City-wide IoT sensor network for real-time air quality monitoring 
and adaptive traffic management
```

## Example Output Structure

```
🏙️ COMPREHENSIVE SMART CITY INFRASTRUCTURE ANALYSIS
═══════════════════════════════════════════════════════════

🏗️ URBAN PLANNING & LAND USE
────────────────────────────────────────────────────────────
[Zoning and community impact analysis...]

📡 IoT & TECHNOLOGY INFRASTRUCTURE
────────────────────────────────────────────────────────────
[Sensor networks and connectivity recommendations...]

🌱 SUSTAINABILITY & RESILIENCE
────────────────────────────────────────────────────────────
[Environmental impact and green infrastructure...]

🚦 TRANSPORTATION & MOBILITY
────────────────────────────────────────────────────────────
[Traffic management and multimodal connectivity...]

💰 MUNICIPAL FINANCE & FUNDING
────────────────────────────────────────────────────────────
[Funding sources and financial feasibility...]

👥 COMMUNITY ENGAGEMENT & EQUITY
────────────────────────────────────────────────────────────
[Stakeholder participation and equity analysis...]

🔐 PRIVACY & CYBERSECURITY
────────────────────────────────────────────────────────────
[Data governance and security architecture...]

✅ Smart City Analysis Complete - All perspectives reviewed
```

## Differences from Sequential Workflows

| Aspect | Smart City (Concurrent) | AgTech (Sequential) |
|--------|------------------------|---------------------|
| **Processing** | All agents run in parallel | Agents run one after another |
| **Agent Context** | Each sees only user input | Each sees full conversation |
| **Speed** | Faster (parallel execution) | Slower (sequential chain) |
| **Dependencies** | No inter-agent dependencies | Each builds on previous |
| **Use Case** | Independent expert opinions | Cumulative analysis pipeline |

## Tracing Options

Set environment variables to enable tracing:

- **Console:** `ENABLE_CONSOLE_TRACING=true`
- **Application Insights:** `ENABLE_AZURE_AI_TRACING=true`
- **OTLP Endpoint:** `OTLP_ENDPOINT=http://localhost:4317`
- **DevUI Tracing:** `ENABLE_DEVUI_TRACING=true`

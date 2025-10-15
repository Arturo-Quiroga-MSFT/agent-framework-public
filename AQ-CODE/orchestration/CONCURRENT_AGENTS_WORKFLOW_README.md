# Concurrent Agents Product Launch Workflow

## Overview

A concurrent fan-out/fan-in workflow that analyzes product launches, business ideas, and services through 5 specialized expert agents. All agents process the input simultaneously to provide rapid, comprehensive analysis from multiple business perspectives.

## Workflow Pattern

**Type:** Concurrent (Fan-out/Fan-in)  
**Agents:** 5 specialized business analysis experts  
**Processing:** All agents analyze in parallel for fast turnaround  
**Output:** Comprehensive multi-perspective product analysis

## Agent Architecture

```
                    User Input
                        ↓
              Product Launch Dispatcher
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   🔬 Researcher    📢 Marketer      ⚖️ Legal
        ↓               ↓               ↓
   💰 Finance       🏗️ Technical
                        ↓
              Product Aggregator
                        ↓
                Formatted Output
```

## Agent Specializations

1. **🔬 Market & Product Researcher**
   - Market insights, competitive landscape
   - Opportunities and risks assessment
   - Target market analysis, trends
   - Factual, data-driven recommendations

2. **📢 Marketing Strategist**
   - Value propositions and positioning
   - Target messaging and campaigns
   - Brand strategy and differentiation
   - Creative but practical approaches

3. **⚖️ Legal & Compliance Reviewer**
   - Legal constraints and disclaimers
   - Policy concerns and regulatory issues
   - Risk mitigation strategies
   - Thorough compliance review

4. **💰 Financial Analyst**
   - Revenue models and pricing strategies
   - Cost structures and burn rate
   - ROI projections and financial viability
   - Investment requirements and risks

5. **🏗️ Technical Architect**
   - Technical feasibility assessment
   - Architecture requirements
   - Technology stack recommendations
   - Scalability and implementation challenges

## Use Cases

### E-Commerce & Consumer Products
- Budget-friendly electric bikes for urban commuters
- Subscription box services (organic pet food, meal kits)
- Sustainable fashion rental marketplace
- Smart home security systems

### Technology & Software
- AI-powered personal finance apps
- VR fitness platforms for home workouts
- Mobile applications and SaaS products
- Developer tools and productivity software

### Healthcare & Wellness
- Telemedicine platforms for rural healthcare
- Mental health apps with AI therapy
- Wearable health monitors
- Digital therapeutics

### B2B Services
- Enterprise software solutions
- Professional services platforms
- Supply chain optimization tools
- Workforce management systems

## Running the Workflow

### Prerequisites
- Azure OpenAI access configured in `.env` file
- Azure CLI authentication: `az login`

### Launch DevUI
```bash
python concurrent_agents_devui.py
```

Access at: **http://localhost:8093**

### Test Mode
```bash
python concurrent_agents_devui.py --test
```

## Output

### Console
- Real-time concurrent processing status
- Trace ID for observability backends

### DevUI
- Interactive visualization
- Live agent responses
- Multi-perspective analysis display

### Files
Saved to `workflow_outputs/`:
- **TXT:** `concurrent_analysis_<timestamp>.txt`

## Output Structure

```
📊 COMPREHENSIVE PRODUCT ANALYSIS
════════════════════════════════════════════════════════════════════════════════

🔬 RESEARCHER ANALYSIS
────────────────────────────────────────────────────────────────────────────────
[Market insights, competitive landscape, opportunities, risks...]

📢 MARKETER ANALYSIS
────────────────────────────────────────────────────────────────────────────────
[Value propositions, target messaging, positioning strategy...]

⚖️ LEGAL ANALYSIS
────────────────────────────────────────────────────────────────────────────────
[Legal constraints, compliance requirements, disclaimers...]

💰 FINANCE ANALYSIS
────────────────────────────────────────────────────────────────────────────────
[Revenue models, cost structure, ROI projections, financial risks...]

🏗️ TECHNICAL ANALYSIS
────────────────────────────────────────────────────────────────────────────────
[Technical feasibility, architecture, tech stack, scalability...]

════════════════════════════════════════════════════════════════════════════════
✅ Analysis Complete - All perspectives reviewed
════════════════════════════════════════════════════════════════════════════════
```

## Key Features

✅ **Fast concurrent processing** - all 5 agents run simultaneously  
✅ **Multi-perspective analysis** - research, marketing, legal, finance, technical  
✅ **Practical recommendations** - actionable insights from each domain  
✅ **Risk identification** - comprehensive risk assessment across all areas  
✅ **Quick turnaround** - parallel execution for rapid results  
✅ **Test mode available** - programmatic testing with tracing  
✅ **DevUI integration** - interactive visualization and debugging  

## Framework Compatibility

Updated for **Microsoft Agent Framework (new structure)**:
- Custom `Executor` classes for dispatcher and aggregator
- Proper type annotations with `WorkflowContext` and `AgentExecutorResponse`
- `WorkflowBuilder` with fan-out/fan-in edge patterns
- Compatible with DevUI tracing and observability
- Test harness with OpenTelemetry span tracking

## Example Input/Output

### Input
```
We are launching a new budget-friendly electric bike for urban commuters 
with a range of 50 miles, priced at $1,200, targeting millennials in major cities.
```

### Output Highlights

**🔬 Researcher:**
- Market size: $2.3B urban micromobility market, 15% CAGR
- Competitors: RadPower, Aventon, Lectric (price points $1K-$2K)
- Opportunity: Millennial commuters seeking eco-friendly transportation
- Risk: Seasonal demand, infrastructure (bike lanes) varies by city

**📢 Marketer:**
- Value prop: "Affordable, sustainable commuting. Go further, spend less."
- Target: Urban millennials, 25-40, environmentally conscious, 5-15 mile commute
- Channels: Instagram, TikTok, sustainability influencers, test-ride events
- Campaign: "Ditch the car payment" comparative messaging

**⚖️ Legal:**
- Product liability insurance required; helmet laws vary by state
- Warranty terms must comply with Magnuson-Moss Warranty Act
- Battery disposal regulations (EPA RCRA); lithium-ion shipping restrictions
- Consumer Product Safety Commission (CPSC) e-bike standards compliance

**💰 Finance:**
- Revenue model: Direct-to-consumer + partnership with bike shops (10% commission)
- Unit economics: $1,200 price, $650 COGS, $550 gross margin (46%)
- Customer acquisition cost: $200 (digital ads + events)
- Break-even: 3,000 units; $500K initial inventory + marketing investment

**🏗️ Technical:**
- Tech stack: E-commerce (Shopify), inventory (TradeGecko), CRM (HubSpot)
- Manufacturing: Contract manufacturer in Taiwan; lead time 90 days
- Scalability: Cloud infrastructure handles 10K orders/month initially
- Challenges: Supply chain for batteries; firmware OTA updates architecture

## Business Analysis Dimensions

| Dimension | Key Questions Answered |
|-----------|------------------------|
| **Market** | What is the market size? Who are competitors? What are trends? |
| **Marketing** | How do we position? What channels? What's the message? |
| **Legal** | What regulations apply? What are liability risks? |
| **Financial** | Is it financially viable? What's the ROI? What are costs? |
| **Technical** | Can we build it? What tech is needed? Does it scale? |

## Concurrent vs Sequential

**Why Concurrent for Product Launch?**
- ✅ Each perspective is independent (no dependencies between agents)
- ✅ Faster results (parallel execution)
- ✅ Equal weighting of all perspectives
- ✅ Simulates cross-functional team meeting

**When to Use Sequential Instead:**
- Each step builds on previous analysis
- Later agents need context from earlier agents
- Workflow represents a pipeline or approval process

## Tracing Options

Set environment variables to enable tracing:

- **Console:** `ENABLE_CONSOLE_TRACING=true`
- **Application Insights:** `ENABLE_AZURE_AI_TRACING=true`
- **OTLP Endpoint:** `OTLP_ENDPOINT=http://localhost:4317`
- **DevUI Tracing:** `ENABLE_DEVUI_TRACING=true`

## Test Harness Usage

```bash
# Run test mode with tracing
python concurrent_agents_devui.py --test
```

The test harness:
- Creates a sample product launch scenario
- Executes the workflow programmatically
- Captures trace ID for observability backend
- Displays aggregated results
- Useful for CI/CD validation

## Related Workflows

- **Healthcare Product Launch:** Specialized for medical devices and health apps
- **Smart City Infrastructure:** 7-agent concurrent urban planning workflow
- **Clinical Trial Management:** Clinical trial analysis with 7 specialists

## Port Configuration

Default port: **8093**

To change the port, modify the `port` parameter in the `serve()` call:
```python
serve(entities=[workflow], port=8092, auto_open=True)
```

## Entity ID

Workflow entity ID: **`workflow_concurrent`**

Used for API calls and DevUI identification.

## Best Practices

### Input Quality
- **Be Specific:** Include target market, key features, pricing, differentiation
- **Provide Context:** Business model, stage (idea/prototype/launched), constraints
- **Set Boundaries:** What's in scope and out of scope for analysis

### Output Interpretation
- **Cross-Reference:** Look for alignment and conflicts between agent perspectives
- **Prioritize Risks:** Legal and financial risks should be addressed before launch
- **Iterate:** Use initial analysis to refine product concept and rerun

### When to Re-Run
- Major pivot in product concept or target market
- Regulatory environment changes
- New competitive threats emerge
- After incorporating initial feedback

## Integration Patterns

### API Usage
```python
# Programmatic workflow execution
workflow = await create_concurrent_workflow()
events = await workflow.run(ProductLaunchInput(description="..."))
outputs = events.get_outputs()
```

### DevUI API Endpoint
```
POST http://localhost:8093/v1/workflow_concurrent
Content-Type: application/json

{
  "description": "Your product description here"
}
```

## Performance Characteristics

- **Typical Runtime:** 15-30 seconds (5 agents in parallel)
- **Sequential Equivalent:** Would take 75-150 seconds (5x slower)
- **Token Usage:** ~5K tokens input + 15K tokens output (varies by response length)
- **Cost Efficiency:** Parallel execution reduces latency without increasing cost

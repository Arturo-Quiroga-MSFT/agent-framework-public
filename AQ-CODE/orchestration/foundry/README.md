# AI Stock Bubble Research — Foundry Workflow

Native Azure AI Foundry Workflow that runs 5 financial analysts in parallel on every research question, each with Bing Grounding for real-time web search.

**Pattern**: Fan-out (all 5 analysts always answer) — no routing/orchestrator needed.
**Demo**: ThoughtWorks, February 18, 2026.

---

## Setup (do this before importing the YAML)

### Step 1: Create the 5 agents in Foundry

Go to `r2d2-foundry-001` → `Main-Project` → **Agents** → **New agent**

Create each agent using the instructions in the `seeds/` folder:

| # | Agent Name | Seed File | Focus |
|---|---|---|---|
| 1 | `ai-market-analyst` | `seeds/01_market_analyst.md` | P/E ratios, valuations, market caps |
| 2 | `ai-technical-analyst` | `seeds/02_technical_analyst.md` | Momentum, RSI, retail sentiment |
| 3 | `ai-fundamental-analyst` | `seeds/03_fundamental_analyst.md` | Revenue, earnings, sustainability |
| 4 | `ai-economic-historian` | `seeds/04_economic_historian.md` | Dot-com parallels, bubble history |
| 5 | `ai-risk-analyst` | `seeds/05_risk_analyst.md` | Index concentration, contagion |

For each agent:
- **Name**: exactly as shown above (the YAML references these by name)
- **Model**: `gpt-4.1` (required — other models may not support Bing Grounding)
- **Instructions**: copy from the seed file's "Instructions" section
- **Tools**: add **Bing Grounding** → select connection `aqbinggrounding001`

### Step 2: Import the workflow

In Foundry → **Workflows** → **Import** → upload `ai-stock-bubble-research.yaml`

Or paste the YAML contents directly into the workflow editor.

### Step 3: Test

Click **Run** and ask something like:
> *Is there an AI stock bubble forming right now? Compare valuations to the dot-com era.*

All 5 analysts will respond with real-time data from Bing.

---

## Example Research Questions

**Valuation Analysis:**
- Is there an AI stock bubble forming in 2025/2026?
- What are the P/E ratios of NVIDIA, Microsoft, and Google right now?
- Compare current AI stock valuations to the dot-com bubble of 2000

**Market Concentration:**
- What percentage of the S&P 500 is AI-related stocks today?
- Analyze the Magnificent 7 concentration risk in major index funds
- Are institutional investors over-exposed to AI stocks?

**Warning Signs:**
- What bubble indicators are currently visible in AI stocks?
- Are AI company revenues justifying their stock prices?
- What does insider selling tell us about AI stock peaks?

**Company-Specific:**
- Analyze NVIDIA for overvaluation — is a correction coming?
- How does Microsoft's AI revenue justify its current P/E premium?
- Compare current AI capex spending to revenue generation timelines

---

## Architecture

```
User Question
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  ai-market-analyst      (Bing search → valuations)  │
│  ai-technical-analyst   (Bing search → momentum)    │
│  ai-fundamental-analyst (Bing search → earnings)    │
│  ai-economic-historian  (Bing search → history)     │
│  ai-risk-analyst        (Bing search → systemic)    │
└─────────────────────────────────────────────────────┘
      │
      ▼  (all 5 responses visible to user in sequence)
  WaitForInput → loop (up to 10 questions)
```

---

## Connection Details

| Setting | Value |
|---|---|
| Foundry Project | `r2d2-foundry-001 / Main-Project` |
| Bing Connection | `aqbinggrounding001` |
| Model | `gpt-4.1` |
| Max Turns | 10 questions per session |
| Workflow ID | `ai-stock-bubble-research` |

---

## Related Files

- [`ai-stock-bubble-research.yaml`](ai-stock-bubble-research.yaml) — Foundry workflow YAML
- [`../6_ai_stock_bubble_research_devui.py`](../6_ai_stock_bubble_research_devui.py) — MAF DevUI version (port 8095)
- [`../6_ai_stock_bubble_chainlit.py`](../6_ai_stock_bubble_chainlit.py) — Chainlit version (port 8096)

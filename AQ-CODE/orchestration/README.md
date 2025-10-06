# Orchestration Workflows (DevUI)

This directory hosts multi-agent orchestration workflow examples showcasing different collaboration patterns using the `agent_framework` DevUI.

## Workflows

| Workflow | Pattern | Agents | Port | Highlights |
|----------|---------|--------|------|------------|
| `agtech_food_innovation_sequential_devui.py` | Sequential Pipeline | 7 | 8097 | Domain handoff across agronomy → regulations |
| `healthcare_product_launch_devui.py` | Fan-out / Fan-in | 5 | 8094 | Parallel healthcare domain review |
| `cybersecurity_incident_triage_devui.py` | Fan-out / Fan-in | 6 | 8095 | Rapid incident response triage & containment plan |
| `ai_governance_model_compliance_devui.py` | Fan-out / Fan-in (Planner included) | 6 | 8096 | Governance checklist + risk register prototype |
| `biotech_ip_landscape_devui.py` | Debate + Synthesis | 6 (+ synthesized) | 8098 | IP landscape with pro vs. skeptic arguments |
| `ml_model_productionization_sequential_devui.py` | Sequential Gate Review | 7 | 8099 | Gate-by-gate visibility, timing, txt+md reports |

> Ports are defaults; modify if occupied.

## Quick Start

1. Ensure Azure CLI logged in:
   ```bash
   az login
   ```
2. Populate `AQ-CODE/.env` (or parent) with:
   ```env
   AZURE_OPENAI_ENDPOINT=... 
   AZURE_OPENAI_DEPLOYMENT_NAME=...
   ```
3. (Optional) Enable tracing:
   - Console: `ENABLE_CONSOLE_TRACING=true`
   - App Insights: `APPLICATIONINSIGHTS_CONNECTION_STRING=...`
   - OTLP: `OTLP_ENDPOINT=http://localhost:4317`
   - DevUI Trace Panels: `ENABLE_DEVUI_TRACING=true`

4. Run a workflow:
   ```bash
   python AQ-CODE/orchestration/cybersecurity_incident_triage_devui.py
   ```
5. Open the Web UI (e.g. http://localhost:8095) and submit an example scenario from the printed suggestions.

## Patterns Demonstrated

- **Sequential Pipeline:** Ordered dependency chain (AgTech)
- **Sequential Gate Review:** Explicit chained executors with per-step visibility (ML Production)
- **Fan-out / Fan-in:** Parallel expert analysis (Healthcare, Cybersecurity, AI Governance)
- **Debate + Synthesis:** Adversarial viewpoints feeding synthesis (Biotech IP)

## Adding a New Workflow

1. Duplicate an existing `*_devui.py` file matching the desired pattern.
2. Adjust: Input `BaseModel`, agent specs, formatter, port & entity ID.
3. Keep output structured (section headings + saved report file in `workflow_outputs/`).
4. Consider adding a synthesis or risk matrix section for decision support.
5. (Optional) Add elapsed timing + dual (.txt/.md) report export (see ML Production, Cybersecurity, AI Governance, Biotech IP).

## Future Enhancements Ideas

- Hierarchical planner issuing sub-prompts (multi-stage execution)
- Iterative round-based refinement (e.g., disaster response updates)
- Shared memory artifact store between agents
- Structured JSON outputs with schema validation
- Unified utility for timing + markdown export across workflows

## License

See root `LICENSE` (MIT).

---
Feel free to open issues or PRs to contribute new collaboration patterns.

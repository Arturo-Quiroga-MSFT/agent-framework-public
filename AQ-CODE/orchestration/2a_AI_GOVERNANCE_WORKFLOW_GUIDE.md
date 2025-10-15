# AI Governance & Model Compliance Workflow

## Overview

A fan-out/fan-in workflow that performs comprehensive AI governance and compliance assessments using concurrent specialist agents. Given an AI system description, it produces a structured governance assessment and risk register.

## Pattern

**Fan-out/Fan-in** - One dispatcher sends requests to multiple concurrent agents, results are aggregated into a unified report.

## Agents (6 Concurrent Specialists)

1. **Governance Planner** - Evaluation checklist, risk categories, applicable standards (ISO 42001, NIST AI RMF)
2. **Data Provenance & Quality Reviewer** - Data sources, lineage, labeling, drift concerns
3. **Fairness & Bias Auditor** - Protected attributes, disparity metrics, mitigation strategies
4. **Privacy & Data Minimization Specialist** - PII/PHI handling, anonymization, retention
5. **Security & Robustness Engineer** - Threat modeling, adversarial robustness, supply chain
6. **Regulatory Alignment Analyst** - EU AI Act, FTC guidance, sector regulations mapping

## Output

- Structured assessment with 6 governance sections
- Risk register with Impact/Likelihood/Mitigation/Owner/ETA
- Saved as `.txt` and `.md` files in `workflow_outputs/`

## Usage

```bash
python AQ-CODE/orchestration/ai_governance_model_compliance_devui.py
```

Opens DevUI at `http://localhost:8096`

## Example Inputs

- "LLM-based clinical decision support suggesting differential diagnoses to physicians"
- "Credit risk scoring model using alternative data sources for micro-loans"
- "Computer vision model for workplace PPE compliance monitoring"
- "Autonomous drone navigation model for agricultural crop monitoring"

## Prerequisites

- Azure OpenAI endpoint configured (`.env` file)
- `az login` authenticated
- Virtual environment activated

## Tracing

Set environment variables:
- `OTLP_ENDPOINT` - OTLP tracing endpoint
- `APPLICATIONINSIGHTS_CONNECTION_STRING` - Azure App Insights
- `ENABLE_CONSOLE_TRACING=true` - Console output
- `ENABLE_DEVUI_TRACING=true` - DevUI tracing

## Framework Migration Note

Updated for new Agent Framework structure:
- Import `AgentExecutorRequest` from `agent_framework._workflows._agent_executor`
- Uses `ChatMessage`, `Role`, `WorkflowContext`, `WorkflowBuilder`
- Compatible with DevUI server and observability tools

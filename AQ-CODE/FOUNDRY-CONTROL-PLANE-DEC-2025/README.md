# Control Plane Integration (Updated February 2026)

This module provides integration with the **Microsoft Foundry Control Plane** for monitoring and managing your AI agent fleet.

> **Docs**: https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/overview?view=foundry  
> **Portal**: https://ai.azure.com > Operate tab (upper right)

## What's New (Feb 2026 vs Dec 2025)

| Feature | Status | Details |
|---------|--------|---------|
| **Supported platforms** | Expanded | Foundry agents, Azure SRE Agent, Logic Apps agent loop, Custom agents |
| **Agent lifecycle** | New | Start/Stop/Block/Unblock agents from Control Plane |
| **Continuous Evaluation** | Preview | Automated quality/safety scoring with AI-assisted evaluators |
| **AI Red Teaming Agent** | New | Automated vulnerability probing and regression testing |
| **Cluster Analysis** | New | Error root-cause discovery across agent runs |
| **Custom agent registration** | New | Register non-Foundry agents for fleet visibility |
| **Grafana dashboards** | New | Agent + Workflow overview dashboards |
| **Agent identity (Entra ID)** | New | Service principal for agent-to-agent auth |
| **Observability API** | Updated | `configure_otel_providers()` replaces `setup_observability()` |
| **Naming** | Updated | "Microsoft Foundry Control Plane" (was "Azure AI Foundry Control Plane") |

## Overview

The Foundry Control Plane is accessed via the **Operate** tab in the upper-right navigation of the Foundry portal. It provides:

- **Fleet Overview**: Health scores, active agents, cost trends, run completion rate, prevented behaviors
- **Assets (Inventory)**: Unified table of all agents across projects in a subscription with metadata, health indicators, and inline recommendations
- **Compliance**: Policy management with Azure Policy, Defender, and Purview integrations
- **Quota**: Model deployment quota usage and management
- **Admin**: Enterprise-level project, user, and resource management

### Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Fleet Management** | Agent discovery, inventory, lifecycle (start/stop/block), version tracking |
| **Observability** | Traces, evaluations, metrics via Application Insights + Grafana dashboards |
| **Compliance** | Guardrails, policies, Azure Policy + Defender + Purview integration |
| **Security** | Red teaming scans, drift monitoring, rate limit tracking, Defender alerts |
| **Cost** | Token usage tracking, cost anomaly detection, optimization recommendations |

### Supported Agent Platforms

| Platform | Auto-discovered | Lifecycle | Observability |
|----------|----------------|-----------|---------------|
| **Foundry agents** (prompt, workflow, hosted) | Yes | Start/Stop (hosted + published) | Full |
| **Azure SRE Agent** | Yes | Start/Stop | Full |
| **Azure Logic Apps agent loop** | Yes | Start/Stop | Limited (no traces/metrics) |
| **Custom agents** | Manual registration | Block/Unblock | Full (with instrumentation) |

> **Note**: Foundry classic agents and Azure OpenAI Assistants are NOT supported.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fleet Health Dashboard                       │
│                     (fleet_health_dashboard.py)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FleetHealthClient                          │
│                     (fleet_health_client.py)                    │
├─────────────────────────────────────────────────────────────────┤
│  • get_all_agents()        - Agent inventory from AI Projects   │
│  • get_agent_metrics()     - Performance data from App Insights │
│  • get_fleet_alerts()      - Alerts from monitoring services    │
│  • get_cost_data()         - Token usage and cost estimates     │
│  • get_compliance_status() - Policy violations and governance   │
│  • get_fleet_health_summary() - Aggregated fleet overview       │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Azure AI        │  │ Azure Monitor   │  │ Azure Resource  │
│ Projects SDK    │  │ (Logs & Metrics)│  │ Graph           │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Prerequisites

### Azure Services
- Azure AI Foundry Project with agents deployed
- Application Insights instance with AI telemetry
- Azure subscription with Resource Graph access (for fleet-wide queries)

### Authentication
```bash
# Authenticate with Azure CLI
az login

# Set default subscription (optional)
az account set --subscription "<your-subscription-id>"
```

### Environment Variables

Create a `.env` file in the control-plane directory:

```env
# Required
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project

# Optional - for full functionality
AZURE_SUBSCRIPTION_ID=your-subscription-id
APPLICATION_INSIGHTS_CONNECTION_STRING=InstrumentationKey=...
LOG_ANALYTICS_WORKSPACE_ID=/subscriptions/.../workspaces/your-workspace
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Verify Azure CLI authentication:
```bash
az account show
```

3. Run the dashboard:
```bash
streamlit run fleet_health_dashboard.py --server.port 8099
```

## Usage

### Running the Dashboard

```bash
# Navigate to the control-plane directory
cd AQ-CODE/control-plane

# Start the dashboard
streamlit run fleet_health_dashboard.py --server.port 8099
```

The dashboard will be available at `http://localhost:8099`

### Using the FleetHealthClient Programmatically

```python
import asyncio
from fleet_health_client import FleetHealthClient, get_fleet_health_sync

# Option 1: Async usage
async def main():
    client = FleetHealthClient()
    
    # Get fleet overview
    summary = await client.get_fleet_health_summary()
    print(f"Fleet Health Score: {summary.fleet_health_score}%")
    print(f"Active Agents: {summary.active_agents}")
    
    # Get specific agent metrics
    for agent in summary.agents:
        print(f"  {agent.agent_name}: {agent.health_score}% ({agent.status.value})")

asyncio.run(main())

# Option 2: Sync wrapper
summary = get_fleet_health_sync()
print(f"Fleet Health: {summary.fleet_health_score}%")
```

## Dashboard Features

### Overview Page
- Fleet health score (weighted average of all agents)
- Total/active/healthy/warning/critical agent counts
- Success rate and run counts (24h)
- Cost trends (7 day window)
- Alert summary by severity

### Agents Page
- Searchable and filterable agent inventory
- Status indicators with color coding
- Click-through to agent details view
- Metrics: health score, runs, error rate, tokens, cost

### Alerts Page
- Alert counts by severity (Critical, High, Medium, Low)
- Recommended response times
- Link to Azure Portal for detailed investigation

### Compliance Page
- Compliance score (percentage of compliant agents)
- Policy violation counts
- Non-compliant agent list with remediation guidance

### Cost Analysis Page
- Cost by agent (top 10 bar chart)
- Daily and weekly cost totals
- Token usage breakdown
- Cost optimization recommendations

## Health Score Calculation

The health score for each agent is calculated based on:

| Factor | Weight | Threshold |
|--------|--------|-----------|
| Error Rate | 40% | < 5% optimal |
| Latency | 30% | < 2000ms optimal |
| Compliance | 20% | Must be compliant |
| Activity | 10% | Active in last 24h |

```
health_score = 100 - (error_penalty + latency_penalty + compliance_penalty + activity_penalty)
```

Health status is then assigned:
- **Healthy**: score >= 80%
- **Warning**: score >= 50%
- **Critical**: score < 50%

## Extending the Dashboard

### Adding New Data Sources

1. Add a new client class or method in `fleet_health_client.py`:

```python
async def get_custom_metrics(self, agent_id: str) -> dict:
    """Fetch custom metrics for an agent."""
    # Your implementation here
    pass
```

2. Create a render function in `fleet_health_dashboard.py`:

```python
def render_custom_section(summary: FleetHealthSummary):
    """Render custom metrics section."""
    st.markdown("### Custom Metrics")
    # Your visualization here
```

3. Add to the sidebar navigation and main routing.

### Custom Alerts Integration

To integrate with custom alerting systems:

```python
# In fleet_health_client.py
async def get_custom_alerts(self) -> List[dict]:
    """Fetch alerts from custom monitoring system."""
    # Integration code here
    pass
```

## Troubleshooting

### Common Issues

**"AZURE_AI_PROJECT_ENDPOINT not configured"**
- Set the environment variable with your AI Project endpoint
- Run in demo mode to test without Azure connection

**"Authentication error"**
- Run `az login` to authenticate
- Verify subscription access with `az account show`

**"No agents found"**
- Verify agents are deployed in your AI Project
- Check the endpoint URL is correct

**"Metrics data unavailable"**
- Ensure Application Insights is configured for your agents
- Verify the connection string/workspace ID is correct

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Related Resources

- [Foundry Control Plane Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/overview?view=foundry)
- [Manage agents across platforms](https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/how-to-manage-agents?view=foundry)
- [Monitor agents across your fleet](https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/monitoring-across-fleet?view=foundry)
- [Ensure compliance and security](https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/how-to-manage-compliance-security?view=foundry)
- [Optimize cost and performance](https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/how-to-optimize-cost-performance?view=foundry)
- [Continuous evaluation for agents](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/continuous-evaluation-agents?view=foundry)
- [Register custom agents](https://learn.microsoft.com/en-us/azure/ai-foundry/control-plane/register-custom-agent?view=foundry)
- [AI Red Teaming Agent](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/ai-red-teaming-agent?view=foundry)
- [Agent evaluators](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/agent-evaluators?view=foundry)
- [Cluster analysis](https://learn.microsoft.com/en-us/azure/ai-foundry/observability/how-to/cluster-analysis?view=foundry)
- Grafana Agent dashboard: https://aka.ms/amg/dash/af-agent
- Grafana Workflow dashboard: https://aka.ms/amg/dash/af-workflow

## Persistent Agents & Portal Visibility

**New to agent creation or confused about portal visibility?** Start here:

📚 **[ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md)** - Complete guide to creating persistent agents  
📖 **[AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md)** - Understanding V1 vs V2 agents and portal visibility  

### Quick Links

| Problem | Solution |
|---------|----------|
| Agents don't show in new portal | Use V2 API (`AIProjectClient.agents.create_agent()`) |
| Agents disappear after script runs | Remove deletion code from `finally` block |
| Need working sample code | See [`agents/azure_ai_persistent_agent_v2.py`](agents/azure_ai_persistent_agent_v2.py) |
| Want to deploy multiple agents | Run [`deploy_new_agents.py`](deploy_new_agents.py) |
| Have old V1 agents to clean up | Use [`cleanup_v1_agents.py`](cleanup_v1_agents.py) |

## Files

| File | Description |
|------|-------------|
| **Agent Creation & Persistence** | |
| `agents/azure_ai_persistent_agent_v2.py` | ✅ Recommended: Simple persistent agent sample |
| `agents/azure_ai_persistent_agent_with_version.py` | Persistent agent with versioning |
| `ANSWER_PERSISTENT_AGENTS.md` | Complete answer for creating persistent agents |
| `AGENT_PORTALS_EXPLAINED.md` | V1 vs V2 agents & portal visibility explained |
| **Deployment & Management** | |
| `deploy_new_agents.py` | Deploy 8 sample agents to your project |
| `cleanup_v1_agents.py` | Clean up V1 agents (old portal only) |
| `cleanup_v1_assistants.py` | Clean up V1 assistants (OpenAI API) |
| `exercise_agents_v2.py` | Generate telemetry by exercising agents |
| **Fleet Monitoring** | |
| `fleet_health_client.py` | API client for aggregating Control Plane data |
| `fleet_health_dashboard.py` | Streamlit dashboard application |
| `requirements.txt` | Python dependencies |
| `README.md` | This documentation |

## License

See the root LICENSE file for license information.

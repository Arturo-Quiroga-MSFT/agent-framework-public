# Control Plane Integration

This module provides integration with the Microsoft Foundry Control Plane for monitoring and managing your AI agent fleet.

## Overview

The Control Plane integration enables:

- **Fleet Health Monitoring**: Real-time visibility into agent health scores, success rates, and performance metrics
- **Alert Aggregation**: Consolidated view of alerts from Application Insights and Defender
- **Cost Tracking**: Token usage and estimated cost analysis across all agents
- **Compliance Posture**: Policy violation tracking and governance status
- **Agent Inventory**: Centralized view of all agents with version and configuration details

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

- [Azure AI Foundry Control Plane Overview](https://learn.microsoft.com/azure/ai-foundry/concepts/control-plane-overview)
- [Monitoring AI Applications](https://learn.microsoft.com/azure/ai-foundry/concepts/control-plane-monitoring-observability)
- [Cost Optimization Guide](https://learn.microsoft.com/azure/ai-foundry/how-to/control-plane-cost-optimization)
- [Custom Agent Registration](https://learn.microsoft.com/azure/ai-foundry/how-to/custom-agent-registration)

## Files

| File | Description |
|------|-------------|
| `fleet_health_client.py` | API client for aggregating Control Plane data |
| `fleet_health_dashboard.py` | Streamlit dashboard application |
| `requirements.txt` | Python dependencies |
| `README.md` | This documentation |

## License

See the root LICENSE file for license information.

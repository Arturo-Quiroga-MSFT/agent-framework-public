# Demo Checklist - Foundry Control Plane
**Demo Date:** January 6, 2026  
**Updated Resources:** ✅ Azure resources recreated, .env updated

## ✅ Pre-Demo Validation (Run These)

### 1. Environment Check
```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025

# Test .env loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Endpoint:', os.getenv('AZURE_AI_PROJECT_ENDPOINT')[:60]); print('✅ Model:', os.getenv('AZURE_AI_MODEL_DEPLOYMENT_NAME'))"
```

**Expected Output:**
```
✅ Endpoint: https://r2d2-foundry-001.services.ai.azure.com/api/projects
✅ Model: gpt-4.1
```

### 2. Azure Authentication
```bash
# Verify you're logged in
az account show

# If not logged in, run:
# az login
```

**Expected:** Your subscription details should display

### 3. List Agents
```bash
python list_v2_agents.py
```

**Expected Output:**
```
Found 1 V2 agent(s):
#    Name         ID                      Model      Ver
1    Agent279     asst_7oU...            unknown    unknown
```

**Current Status:** ✅ 1 agent deployed (Agent279)

### 4. Test Fleet Health Client
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); from fleet_health_client import get_fleet_health_sync; summary = get_fleet_health_sync(); print(f'Fleet Health: {summary.fleet_health_score}%'); print(f'Agents: {len(summary.agents)}')"
```

**Expected Output:**
```
Fleet Health: 80.0%
Agents: 1
```

### 5. Launch Dashboard
```bash
streamlit run fleet_health_dashboard.py --server.port 8099
```

**Expected:** Dashboard opens at `http://localhost:8099`

## 🎯 Demo Flow

### Part 1: Agent Inventory (3 minutes)
1. Show list of agents: `python list_v2_agents.py --detailed`
2. Explain V2 vs V1 agents (see AGENT_PORTALS_EXPLAINED.md)
3. Show agent in Azure Portal: https://ai.azure.com

### Part 2: Fleet Health Dashboard (5 minutes)
1. Launch dashboard: `streamlit run fleet_health_dashboard.py --server.port 8099`
2. **Overview Tab:**
   - Fleet health score (80%)
   - Agent counts
   - Success rates
3. **Agents Tab:**
   - Agent inventory
   - Health status indicators
   - Model usage
4. **Alerts Tab:**
   - Alert aggregation (if any)
   - Severity levels
5. **Compliance Tab:**
   - Compliance score
   - Policy violations
6. **Cost Analysis Tab:**
   - Token usage
   - Cost per agent

### Part 3: Deploy Additional Agents (Optional - 2 minutes)
```bash
python deploy_new_agents.py
```
**Creates:** 8 additional agents (data analysis, research, customer support, etc.)

### Part 4: Exercise Agents & Generate Telemetry (Optional - 3 minutes)
```bash
python exercise_agents_v2.py
```
**Generates:** Traces, metrics, and telemetry data for dashboard visualization

## 📋 Demo Scripts

### Script 1: Show Current State
```bash
echo "=== Current Foundry Control Plane Setup ==="
echo ""
echo "1. Azure AI Project:"
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('   ', os.getenv('AZURE_AI_PROJECT_ENDPOINT'))"
echo ""
echo "2. Deployed Agents:"
python list_v2_agents.py
echo ""
echo "3. Fleet Health:"
python -c "from dotenv import load_dotenv; load_dotenv(); from fleet_health_client import get_fleet_health_sync; s = get_fleet_health_sync(); print(f'   Score: {s.fleet_health_score}%'); print(f'   Agents: {len(s.agents)}'); print(f'   Active: {s.active_agents}')"
```

### Script 2: Deploy Full Fleet
```bash
echo "=== Deploying Full Agent Fleet ==="
python deploy_new_agents.py
echo ""
echo "=== New Fleet Status ==="
python list_v2_agents.py
```

### Script 3: Generate Activity
```bash
echo "=== Generating Agent Telemetry ==="
python exercise_agents_v2.py
```

## 🔧 Troubleshooting

### Issue: "AZURE_AI_PROJECT_ENDPOINT not configured"
**Fix:** 
```bash
# Check .env file exists
ls -la .env

# Verify contents
cat .env | grep AZURE_AI_PROJECT_ENDPOINT
```

### Issue: "Authentication error"
**Fix:**
```bash
az login
az account show
```

### Issue: "No agents found"
**Fix:**
```bash
# Deploy sample agents
python deploy_new_agents.py
```

### Issue: Dashboard won't start
**Fix:**
```bash
# Check if port 8099 is already in use
lsof -i :8099

# Kill existing process (if needed)
kill -9 <PID>

# Or use a different port
streamlit run fleet_health_dashboard.py --server.port 8100
```

## 📊 Expected Demo Results

**After running deploy_new_agents.py:**
- **Total Agents:** 9 (1 existing + 8 new)
- **Models:** gpt-4.1, gpt-4.1-mini
- **Use Cases:**
  - Data Analysis
  - Research
  - Customer Support
  - Financial Analysis
  - Technical Documentation
  - HR Assistant
  - Marketing
  - Project Management
  - (Original Agent279)

**After running exercise_agents_v2.py:**
- **Traces Generated:** ~50+ traces in Application Insights
- **Metrics Available:** Latency, token usage, error rates
- **Dashboard Data:** Real-time health scores, cost estimates

## 🎬 Demo Talking Points

### Why Control Plane Matters
- "As organizations scale from 5 agents to 50+ agents, manual monitoring becomes impossible"
- "Control Plane provides enterprise-grade observability for AI agent fleets"
- "Think of it as Kubernetes dashboard, but for AI agents"

### Key Capabilities
1. **Fleet Health Monitoring:** Single pane of glass for all agents
2. **Cost Tracking:** Token usage and cost optimization insights
3. **Compliance:** Policy enforcement and governance
4. **Alerting:** Proactive issue detection before users notice
5. **Performance:** Latency, error rates, throughput metrics

### Integration Points
- **Azure AI Projects:** Agent inventory and metadata
- **Application Insights:** Telemetry and traces
- **Azure Monitor:** Metrics and alerting
- **Azure Resource Graph:** Fleet-wide queries
- **Cost Management:** Token usage and costs

## 📚 Demo Resources

| Resource | Purpose |
|----------|---------|
| [README.md](README.md) | Full documentation |
| [AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md) | V1 vs V2 agents explained |
| [ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md) | Creating persistent agents |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick command reference |
| [fleet_health_dashboard.py](fleet_health_dashboard.py) | Dashboard application |
| [fleet_health_client.py](fleet_health_client.py) | API client |

## ✅ Final Pre-Demo Check

Run this comprehensive validation:
```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025

echo "1. Environment... "; python -c "from dotenv import load_dotenv; import os; load_dotenv(); exit(0 if os.getenv('AZURE_AI_PROJECT_ENDPOINT') else 1)" && echo "   ✅ OK" || echo "   ❌ FAIL"

echo "2. Auth... "; az account show > /dev/null 2>&1 && echo "   ✅ OK" || echo "   ❌ FAIL"

echo "3. Agents... "; python -c "from dotenv import load_dotenv; load_dotenv(); from azure.ai.projects import AIProjectClient; from azure.identity import DefaultAzureCredential; import os; c = AIProjectClient(endpoint=os.getenv('AZURE_AI_PROJECT_ENDPOINT'), credential=DefaultAzureCredential()); list(c.agents.list_agents()); print('   ✅ OK')" 2>&1 | tail -1

echo "4. Fleet Health... "; python -c "from dotenv import load_dotenv; load_dotenv(); from fleet_health_client import get_fleet_health_sync; get_fleet_health_sync(); print('   ✅ OK')" 2>&1 | tail -1

echo "5. Dashboard... "; pip show streamlit > /dev/null 2>&1 && echo "   ✅ OK" || echo "   ❌ FAIL"

echo ""
echo "✅ All systems ready for demo!" 
```

---
**Last Updated:** January 6, 2026  
**Azure Resources:** r2d2-foundry-001 (Main-Project)  
**Status:** ✅ Ready for demo

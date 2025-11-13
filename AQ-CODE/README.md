# AQ-CODE Directory

This directory contains custom code, documentation, and resources for Microsoft Agent Framework development and workshops.

## Directory Structure

### 📁 **workshops/**
Workshop materials and agendas for Microsoft Agent Framework training sessions.
- `MAF_AZURE_AI_FOUNDRY_WORKSHOP_AGENDA.md` - Full hands-on workshop agenda (2 hours)
- `MAF_AZURE_AI_FOUNDRY_WORKSHOP_DEMO_DRIVEN.md` - Demo-driven workshop agenda (2 hours)
- `WORKSHOP_AGENDA_EMAIL_SUMMARY.md` - Detailed email summary (hands-on format)
- `WORKSHOP_AGENDA_EMAIL_SUMMARY_DEMO_DRIVEN.md` - Detailed email summary (demo format)
- `WORKSHOP_MINI_SUMMARY.md` - Concise workshop overview for partners
- `OBSERVABILITY_QUICK_REFERENCE.md` - Quick reference for observability demos

### 📁 **docs/**
Documentation and explanatory materials.
- `AZURE_AI_SAMPLES_UPDATE.md` - Azure AI samples update notes
- `CHANGELOG.md` - Change history and version notes
- `CHATAGENT_VS_CREATE_AGENT.md` - Technical comparison: ChatAgent() vs create_agent()
- `DOCUMENTATION_INDEX.md` - Index of all documentation
- `ENHANCEMENTS_SUMMARY.md` - Summary of enhancements made
- `MCP_EXPLAINED.md` - Model Context Protocol explanation

### 📁 **deployment/**
Docker and Azure deployment configurations.
- `Dockerfile` - Container image for agent applications
- `DOCKER_README.md` - Docker setup and usage instructions
- `deploy-to-azure.sh` - Azure deployment automation script

### 📁 **setup-scripts/**
Setup and utility scripts for configuring samples and environments.
- `setup_azure_ai_samples.py` - Configure Azure AI agent samples
- `setup_azure_openai_samples.py` - Configure Azure OpenAI agent samples
- `update_azure_ai_samples.py` - Update existing Azure AI samples
- `verify_agent_framework.py` - Comprehensive test suite (11 tests)

### 📁 **demos/**
Streamlit demonstrations and interactive applications.
- `streamlit_azure_ai_demo.py` - Main Streamlit demo application
- `streamlit_azure_ai_demo_backup_20251025_1110.py` - Backup version

### 📁 **orchestration/**
Multi-agent orchestration examples and interactive systems.
- `concurrent_agents_interactive_devui.py` - 5-agent DevUI backend (port 8092)
- `multi_agent_dashboard.py` - Simple Streamlit dashboard
- `multi_agent_dashboard_concurrent.py` - Concurrent multi-agent dashboard (port 8095)

### 📁 **observability/**
Observability and Redis persistence demonstration samples (Workshop Modules 4 & 5).

**Observability (Module 4):**
- `observability_azure_ai_agent.py` - Azure AI agent with Application Insights
- `observability_workflow.py` - Customer feedback analysis workflow with telemetry

**Redis Persistence - Console Demos (Module 5):**
- `redis_demo_preferences.py` - RedisProvider for smart preference memory
- `redis_demo_persistence.py` - RedisChatMessageStore for conversation persistence
- `redis_demo_multi_agent.py` - Multi-agent isolation with separate memory scopes

**Redis Persistence - DevUI Demos (Module 5 - Interactive):**
- `redis_demo_preferences_devui.py` - Interactive preference learning (port 8000)
- `redis_demo_persistence_devui.py` - Interactive conversation persistence (port 8001)
- `redis_demo_multi_agent_devui.py` - Side-by-side agents (ports 8002 & 8003)

**Documentation:**
- `OBSERVABILITY_SAMPLES.md` - Comprehensive observability documentation (Module 4)
- `REDIS_PERSISTENCE_SAMPLES.md` - Redis persistence workshop documentation (Module 5)

### 📁 **azure_ai/**
Azure AI agent samples and implementations.

### 📁 **llmops/**
LLMOps best practices and operational guidance.

### 📁 **notebooks/**
Jupyter notebooks for experiments and tutorials.

### 📁 **parallelism/**
Parallel processing examples and patterns.

### 📁 **sample_documents/**
Sample documents for testing File Search and RAG features.

### 📁 **generated_plots/**
Output directory for generated visualizations and plots.

### 📁 **_start-here/**
Quick start guides and initial resources.

## Root Files

- `.env` - Environment variables configuration (not committed to git)
- `requirements.txt` - Python dependencies for AQ-CODE projects

## Quick Start

### Run Multi-Agent Dashboard
```bash
# Terminal 1: Start DevUI backend
cd orchestration
python concurrent_agents_interactive_devui.py

# Terminal 2: Start Streamlit dashboard
cd orchestration
streamlit run multi_agent_dashboard_concurrent.py --server.port 8095
```

### Run Setup Scripts
```bash
# Configure Azure AI samples
python setup-scripts/setup_azure_ai_samples.py

# Verify agent framework installation
python setup-scripts/verify_agent_framework.py
```

### Deploy to Azure
```bash
# Build and deploy
cd deployment
./deploy-to-azure.sh
```

## Environment Setup

Ensure your `.env` file contains:
```bash
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<id>
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
OPENWEATHER_API_KEY=<your-api-key>  # Optional
```

## Contributing

When adding new files to AQ-CODE:
- **Workshops:** → `workshops/`
- **Documentation:** → `docs/`
- **Deployment configs:** → `deployment/`
- **Setup/utility scripts:** → `setup-scripts/`
- **Demos/Streamlit apps:** → `demos/`
- **Agent orchestration:** → `orchestration/`

Keep the root directory clean with only essential configuration files.

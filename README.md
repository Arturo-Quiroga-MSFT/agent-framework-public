![Microsoft Agent Framework](docs/assets/readme-banner.png)

# Agent Framework Public Repository

> **👋 Welcome!** This repository combines the **official Microsoft Agent Framework (MAF)** with **custom implementations, production demos, and real-world applications** created by **Arturo Quiroga**, Sr. Partner Solutions Architect at Microsoft (EPS - Americas).
>
> **🎯 Purpose**: Demonstrate enterprise-grade AI agent development, multi-cloud deployment strategies, and production-ready patterns using Microsoft Agent Framework, LangGraph, Azure AI, and cloud-agnostic architectures.
>
> **📦 Contents**: 
> - Official MAF code (auto-synced from [microsoft/agent-framework](https://github.com/microsoft/agent-framework))
> - Production Streamlit demos with 9+ agent scenarios
> - NL2SQL pipeline with database integration
> - Multi-cloud deployment strategies (Azure/AWS/GCP)
> - LLMOps best practices and workshop materials
> - Redis persistence patterns
> - Full observability implementations
>
> **🆕 Latest Updates (Nov 28, 2024)**: Latest MAF code synced, Mermaid architecture diagrams, enhanced documentation. See [AQ-CODE/CHANGELOG.md](./AQ-CODE/CHANGELOG.md) for full history.

[![Microsoft Azure AI Foundry Discord](https://dcbadge.limes.pink/api/server/b5zjErwbQM?style=flat)](https://discord.gg/b5zjErwbQM)
[![MS Learn Documentation](https://img.shields.io/badge/MS%20Learn-Documentation-blue)](https://learn.microsoft.com/en-us/agent-framework/)
[![PyPI](https://img.shields.io/pypi/v/agent-framework)](https://pypi.org/project/agent-framework/)
[![NuGet](https://img.shields.io/nuget/v/Microsoft.Agents.AI)](https://www.nuget.org/profiles/MicrosoftAgentFramework/)

---

## 📂 Repository Structure

This repository is organized into distinct sections:

### 🎯 **Custom Development & Demos**

#### **[AQ-CODE/](./AQ-CODE/)** - Production Demos & Workshop Materials
- **🎨 Streamlit Demo App**: 9 interactive agent scenarios (Basic Chat, Function Tools, Threads, Code Interpreter, Bing Search, File Search/RAG, Azure AI Search, MCP integrations)
  - 🚀 [Live Demo](https://agent-framework-demo.livelyforest-d40d7875.eastus.azurecontainerapps.io) deployed on Azure Container Apps
  - 🐳 Docker + Azure deployment automation
  - 🔐 Managed Identity authentication (no API keys!)
  - 💬 Conversation memory in 4+ scenarios
  - 📥 Plot download capability
- **📚 Workshop Materials**: Full 2-hour MAF + Azure AI Foundry training agendas
- **🔧 Setup Scripts**: Environment configuration and validation tools
- **🎭 Multi-Agent Orchestration**: DevUI backends and Streamlit dashboards
- **📊 Observability**: Application Insights integration samples
- **💾 Redis Persistence**: Memory and conversation state management
- See [AQ-CODE/README.md](./AQ-CODE/README.md) for details

#### **[nl2sql-pipeline/](./nl2sql-pipeline/)** - Natural Language to SQL Workflow
- Production-ready sequential pipeline: NL Question → SQL → Insights
- Azure SQL Database integration via MSSQL MCP Server
- 8-step workflow with agents + business logic executors
- ✨ **NEW**: Mermaid architecture diagrams for better visualization
- CSV/Excel export, automatic chart generation
- Schema caching (100-500x performance improvement)
- DevUI interface on port 8097
- See [nl2sql-pipeline/README.md](./nl2sql-pipeline/README.md) and [ARCHITECTURE.md](./nl2sql-pipeline/ARCHITECTURE.md)

#### **[AQ-TERADATA/](./AQ-TERADATA/)** - Multi-Cloud Integration Strategy
- LangGraph + MAF integration for cloud-agnostic deployments
- Architecture patterns for Azure/AWS/GCP/on-premises
- MCP protocol for universal agent interfaces
- Kubernetes, Terraform, CI/CD examples
- See [AQ-TERADATA/README.md](./AQ-TERADATA/README.md)

#### **[LLMOPS/](./LLMOPS/)** - LLMOps Best Practices
- Operational guidance for production AI agents
- Monitoring, evaluation, and deployment patterns
- Cost optimization strategies
- See [LLMOPS/INDEX.md](./LLMOPS/INDEX.md)

#### **[MCP/](./MCP/)** - Model Context Protocol Experiments
- Custom MCP server implementations
- Integration patterns and examples

### 🏢 **Official Microsoft Agent Framework Code**

These directories are **auto-synced** from [microsoft/agent-framework](https://github.com/microsoft/agent-framework) using `update_from_upstream.sh`:

#### **[python/](./python/)** - Official Python SDK & Samples
- Core agent framework packages
- Getting started samples (agents, workflows, observability)
- DevUI package for visual debugging
- AF Labs for experimental features
- Package source: [microsoft/agent-framework/python](https://github.com/microsoft/agent-framework/tree/main/python)

#### **[dotnet/](./dotnet/)** - Official .NET SDK & Samples
- C#/.NET implementation
- Agent providers and middleware
- Workflow orchestration examples
- Package source: [microsoft/agent-framework/dotnet](https://github.com/microsoft/agent-framework/tree/main/dotnet)

#### **[docs/](./docs/)** - Official MAF Documentation
- Framework overview and design documents
- Architectural Decision Records (ADRs)
- Specifications and FAQs
- Docs source: [microsoft/agent-framework/docs](https://github.com/microsoft/agent-framework/tree/main/docs)

#### **[workflow-samples/](./workflow-samples/)** - Official Workflow Patterns
- Reference implementations
- Multi-agent orchestration patterns
- Samples source: [microsoft/agent-framework/workflow-samples](https://github.com/microsoft/agent-framework/tree/main/workflow-samples)

### 🔧 **Repository Tools**

- **[update_from_upstream.sh](./update_from_upstream.sh)** - Auto-sync script for official MAF code
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick commands and tips

---

## 🚀 Quick Start

### Installation

**Python:**
```bash
pip install agent-framework --pre
# Installs all sub-packages from python/packages/
```

**.NET:**
```bash
dotnet add package Microsoft.Agents.AI --prerelease
```

### Documentation

- **[Framework Overview](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)** - Architecture and concepts
- **[Quick Start](https://learn.microsoft.com/agent-framework/tutorials/quick-start)** - Your first agent
- **[Tutorials](https://learn.microsoft.com/agent-framework/tutorials/overview)** - Step-by-step guides
- **[User Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview)** - In-depth documentation
- **[Migration Guides](https://learn.microsoft.com/en-us/agent-framework/migration-guide/)** - From Semantic Kernel or AutoGen

---

## 🎨 Interactive Demos

### 1. **Streamlit Demo Application** (9 Scenarios)

**🌐 Live Demo**: [agent-framework-demo.livelyforest-d40d7875.eastus.azurecontainerapps.io](https://agent-framework-demo.livelyforest-d40d7875.eastus.azurecontainerapps.io)

**Local Development:**
```bash
cd AQ-CODE
streamlit run streamlit_azure_ai_demo.py
# Access at http://localhost:8501
```

**Docker:**
```bash
docker build -t agent-demo -f AQ-CODE/Dockerfile .
docker run -p 8501:8501 -e AZURE_AI_PROJECT_ENDPOINT=your-endpoint agent-demo
```

**Azure Container Apps:**
```bash
cd AQ-CODE
bash deploy-to-azure.sh
# Deploys with Managed Identity, returns HTTPS URL
```

**Scenarios:**
1. ✅ Basic Chat Agent - Conversational AI
2. 🛠️ Function Tools - Weather API integration
3. 🧵 Thread Management - Conversation persistence
4. 🐍 Code Interpreter - Python execution + plots (with download!)
5. 🔍 Bing Web Search - Grounding with citations
6. 📄 File Search (RAG) - Document Q&A
7. 🔎 Azure AI Search - Hotel database queries
8. 🌐 Hosted MCP - Microsoft Learn docs
9. 🔥 Firecrawl MCP - Web scraping

**Documentation**: [AQ-CODE/DOCUMENTATION_INDEX.md](./AQ-CODE/DOCUMENTATION_INDEX.md)

### 2. **NL2SQL Pipeline** (8-Step Workflow)

```bash
python nl2sql-pipeline/nl2sql_workflow.py
# DevUI at http://localhost:8097
```

**Features:**
- Natural language → SQL → Insights
- Azure SQL Database integration
- Automatic CSV/Excel export
- Smart visualizations (bar, line, pie, heatmap)
- Schema caching for performance
- Full observability

**Documentation**: [nl2sql-pipeline/README.md](./nl2sql-pipeline/README.md)

---

## 🎯 Microsoft Agent Framework Quickstart

### Python - Basic Agent

Create a simple Azure OpenAI agent that writes a haiku:

```python
# pip install agent-framework --pre
# Use `az login` to authenticate with Azure CLI
import os
import asyncio
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential


async def main():
    # Initialize a chat agent with Azure OpenAI Responses
    # the endpoint, deployment name, and api version can be set via environment variables
    # or they can be passed in directly to the AzureOpenAIResponsesClient constructor
    agent = AzureOpenAIResponsesClient(
        # endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        # deployment_name=os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
        # api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        # api_key=os.environ["AZURE_OPENAI_API_KEY"],  # Optional if using AzureCliCredential
        credential=AzureCliCredential(), # Optional, if using api_key
    ).create_agent(
        name="HaikuBot",
        instructions="You are an upbeat assistant that writes beautifully.",
    )

    print(await agent.run("Write a haiku about Microsoft Agent Framework."))

if __name__ == "__main__":
    asyncio.run(main())
```

### .NET - Basic Agent

**OpenAI:**
```csharp
// dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
using System;
using OpenAI;

// Replace the <apikey> with your OpenAI API key.
var agent = new OpenAIClient("<apikey>")
    .GetOpenAIResponseClient("gpt-4o-mini")
    .CreateAIAgent(name: "HaikuBot", instructions: "You are an upbeat assistant that writes beautifully.");

Console.WriteLine(await agent.RunAsync("Write a haiku about Microsoft Agent Framework."));
```

**Azure OpenAI with Managed Identity:**
```csharp
// dotnet add package Microsoft.Agents.AI.OpenAI --prerelease
// dotnet add package Azure.Identity
// Use `az login` to authenticate with Azure CLI
using System;
using OpenAI;

// Replace <resource> and gpt-4o-mini with your Azure OpenAI resource name and deployment name.
var agent = new OpenAIClient(
    new BearerTokenPolicy(new AzureCliCredential(), "https://ai.azure.com/.default"),
    new OpenAIClientOptions() { Endpoint = new Uri("https://<resource>.openai.azure.com/openai/v1") })
    .GetOpenAIResponseClient("gpt-4o-mini")
    .CreateAIAgent(name: "HaikuBot", instructions: "You are an upbeat assistant that writes beautifully.");

Console.WriteLine(await agent.RunAsync("Write a haiku about Microsoft Agent Framework."));
```

---

## 📚 Learning Resources

### Official Documentation
- **[MS Learn - Agent Framework](https://learn.microsoft.com/agent-framework/)** - Complete official documentation
- **[Framework Overview](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)** - Architecture and concepts
- **[Quick Start](https://learn.microsoft.com/agent-framework/tutorials/quick-start)** - Your first agent in 5 minutes
- **[Tutorials](https://learn.microsoft.com/agent-framework/tutorials/overview)** - Step-by-step guides
- **[User Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview)** - In-depth documentation

### Video Resources
<p align="center">
  <a href="https://www.youtube.com/watch?v=AAgdMhftj8w" title="Watch the full Agent Framework introduction (30 min)">
    <img src="https://img.youtube.com/vi/AAgdMhftj8w/hqdefault.jpg"
         alt="Watch the full Agent Framework introduction (30 min)" width="480">
  </a>
</p>
<p align="center">
  <a href="https://www.youtube.com/watch?v=AAgdMhftj8w">
    🎥 Agent Framework Introduction (30 min)
  </a>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=mOAaGY4WPvc">
    <img src="https://img.youtube.com/vi/mOAaGY4WPvc/hqdefault.jpg" alt="See the DevUI in action" width="480">
  </a>
</p>
<p align="center">
  <a href="https://www.youtube.com/watch?v=mOAaGY4WPvc">
    🎥 DevUI in Action (1 min)
  </a>
</p>

### Framework Features

✨ **Graph-based Workflows** - Connect agents and deterministic functions using data flows with streaming, checkpointing, human-in-the-loop, and time-travel capabilities
  - [Python workflows](./python/samples/getting_started/workflows/) | [.NET workflows](./dotnet/samples/GettingStarted/Workflows/)

🧪 **AF Labs** - Experimental packages for cutting-edge features including benchmarking, reinforcement learning, and research initiatives
  - [Labs directory](./python/packages/lab/)

🎨 **DevUI** - Interactive developer UI for agent development, testing, and debugging workflows
  - [DevUI package](./python/packages/devui/)

🔍 **Observability** - Built-in OpenTelemetry integration for distributed tracing, monitoring, and debugging
  - [Python observability](./python/samples/getting_started/observability/) | [.NET telemetry](./dotnet/samples/GettingStarted/AgentOpenTelemetry/)

🤖 **Multiple Agent Providers** - Support for various LLM providers with more being added continuously
  - [Python examples](./python/samples/getting_started/agents/) | [.NET examples](./dotnet/samples/GettingStarted/AgentProviders/)

🔧 **Middleware** - Flexible middleware system for request/response processing, exception handling, and custom pipelines
  - [Python middleware](./python/samples/getting_started/middleware/) | [.NET middleware](./dotnet/samples/GettingStarted/Agents/Agent_Step14_Middleware/)

🐍🎯 **Python and .NET Support** - Full framework support for both Python and C#/.NET with consistent APIs
  - [Python packages](./python/packages/) | [.NET source](./dotnet/src/)

---

## 💼 Production Patterns & Best Practices

### Enterprise Deployment
- **[AQ-CODE/DOCKER_README.md](./AQ-CODE/DOCKER_README.md)** - Container deployment guide
- **[AQ-CODE/deploy-to-azure.sh](./AQ-CODE/deploy-to-azure.sh)** - Automated Azure Container Apps deployment
- **[AQ-TERADATA/](./AQ-TERADATA/)** - Multi-cloud strategies (Azure/AWS/GCP)

### Observability & Monitoring
- **[AQ-CODE/observability/](./AQ-CODE/observability/)** - Application Insights integration
- **[AQ-CODE/observability/OBSERVABILITY_SAMPLES.md](./AQ-CODE/observability/OBSERVABILITY_SAMPLES.md)** - Workshop Module 4
- OpenTelemetry traces, metrics, and logs

### State Management
- **[AQ-CODE/observability/REDIS_PERSISTENCE_SAMPLES.md](./AQ-CODE/observability/REDIS_PERSISTENCE_SAMPLES.md)** - Redis persistence patterns (Workshop Module 5)
- Conversation memory and multi-agent isolation
- Interactive DevUI demos included

### LLMOps
- **[LLMOPS/INDEX.md](./LLMOPS/INDEX.md)** - Operational best practices
- **[LLMOPS/MAF_LLMOPS_BEST_PRACTICES.md](./LLMOPS/MAF_LLMOPS_BEST_PRACTICES.md)** - Comprehensive guide
- Monitoring, evaluation, cost optimization

---

## 🛠️ Repository Maintenance

### Sync Official MAF Code

This repository includes automated syncing of official Microsoft Agent Framework code:

```bash
# Update python/, dotnet/, docs/, workflow-samples/ from upstream
./update_from_upstream.sh
```

The script:
- Clones [microsoft/agent-framework](https://github.com/microsoft/agent-framework)
- Updates official directories
- Preserves custom code in AQ-CODE/, nl2sql-pipeline/, etc.

**Synced Directories:**
- `python/` - Official Python SDK and samples
- `dotnet/` - Official .NET SDK and samples  
- `docs/` - Official documentation
- `workflow-samples/` - Official workflow patterns

**Custom Directories (NOT synced):**
- `AQ-CODE/` - Custom demos and tools
- `nl2sql-pipeline/` - NL2SQL implementation
- `AQ-TERADATA/` - Multi-cloud integration
- `LLMOPS/` - Best practices documentation
- `MCP/` - MCP experiments

---

## 📊 More Examples & Samples

### Python
- [Getting Started with Agents](./python/samples/getting_started/agents) - Basic agent creation and tool usage
- [Chat Client Examples](./python/samples/getting_started/chat_client) - Direct chat client patterns
- [Getting Started with Workflows](./python/samples/getting_started/workflows) - Workflow creation and orchestration
- **[AQ-CODE/streamlit_azure_ai_demo.py](./AQ-CODE/streamlit_azure_ai_demo.py)** - Production Streamlit demo (9 scenarios)

### .NET
- [Getting Started with Agents](./dotnet/samples/GettingStarted/Agents) - Basic agent creation and tool usage
- [Agent Provider Samples](./dotnet/samples/GettingStarted/AgentProviders) - Different agent providers
- [Workflow Samples](./dotnet/samples/GettingStarted/Workflows) - Multi-agent patterns and orchestration

---

## 🤝 Contributing

### To This Repository
- Custom code contributions welcome in `AQ-CODE/`, `nl2sql-pipeline/`, etc.
- See [CONTRIBUTING.md](./CONTRIBUTING.md)
- For MAF core issues: file at [microsoft/agent-framework](https://github.com/microsoft/agent-framework/issues)

### To Microsoft Agent Framework
- [Contributing Guide](./CONTRIBUTING.md)
- [Python Development Guide](./python/DEV_SETUP.md)
- [Design Documents](./docs/design)
- [Architectural Decision Records](./docs/decisions)

---

## 💬 Community & Support

- 💬 **Discord**: [Microsoft Azure AI Foundry](https://discord.gg/b5zjErwbQM)
- 📖 **Documentation**: [MS Learn - Agent Framework](https://learn.microsoft.com/agent-framework/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/microsoft/agent-framework/issues) (for MAF core)
- 📝 **Discussions**: Use GitHub Discussions for questions

---

## ⚠️ Important Notes

If you use the Microsoft Agent Framework to build applications that operate with third-party servers or agents, you do so at your own risk. We recommend reviewing all data being shared with third-party servers or agents and being cognizant of third-party practices for retention and location of data. It is your responsibility to manage whether your data will flow outside of your organization's Azure compliance and geographic boundaries and any related implications.

---

## 📄 License

See [LICENSE](./LICENSE) file.

---

**Maintained By**: Arturo Quiroga, Sr. Partner Solutions Architect @ Microsoft  
**Last Updated**: November 28, 2024  
**Repository**: [agent-framework-public](https://github.com/arturoquiroga/agent-framework-public)

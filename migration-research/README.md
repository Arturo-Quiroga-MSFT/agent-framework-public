# Migration Research: Semantic Kernel & AutoGen to Microsoft Agent Framework

This directory contains research, documentation, and resources to help customers migrate from **Semantic Kernel** and **AutoGen** to the new **Microsoft Agent Framework**.

## 📚 Contents

- [Overview](./overview.md) - High-level comparison and migration philosophy
- [Semantic Kernel Migration](./semantic-kernel-migration.md) - Detailed guide for migrating from Semantic Kernel
- [AutoGen Migration](./autogen-migration.md) - Detailed guide for migrating from AutoGen
- [Feature Comparison Matrix](./feature-comparison.md) - Side-by-side feature comparison
- [Code Examples](./examples/) - Migration code examples
- [FAQ](./faq.md) - Frequently asked questions

## 🎯 Quick Start

### Who Should Read This?

This guide is for developers and teams who are:
- Currently using **Semantic Kernel** for AI orchestration
- Building multi-agent systems with **AutoGen**
- Looking to leverage the latest Microsoft Agent Framework capabilities
- Planning to consolidate their agent framework tooling

### What is Microsoft Agent Framework?

The Microsoft Agent Framework is the next evolution of agent development at Microsoft, bringing together:
- **Unified Agent Architecture**: Common `AIAgent` base class for all agent types
- **Advanced Workflows**: Type-safe, graph-based orchestration with checkpointing
- **Multi-Agent Orchestration**: Built-in patterns (Sequential, Concurrent, Handoff, Magentic)
- **Flexible Integrations**: Support for Azure AI, OpenAI, and custom inference services
- **Production-Ready Features**: Observability, error handling, and state management

## 🔄 Migration Paths

### From Semantic Kernel

The Microsoft Agent Framework builds on Semantic Kernel concepts:
- **Plugins** → Still supported with the same patterns
- **Kernel** → Simplified or optional (agents can work directly with services)
- **ChatCompletionAgent** → Enhanced with more orchestration options
- **Agent Framework** → Graduated to Microsoft Agent Framework

👉 [Read the Semantic Kernel Migration Guide](./semantic-kernel-migration.md)

### From AutoGen

AutoGen patterns are supported and enhanced:
- **Conversable Agents** → Available through compatibility layer
- **Group Chat** → Enhanced orchestration patterns
- **Magentic-One** → Magentic orchestration in workflows
- **Multi-Agent Patterns** → More flexible workflow system

👉 [Read the AutoGen Migration Guide](./autogen-migration.md)

## 📖 Key Resources

### Official Documentation
- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Semantic Kernel Agent Framework RC Migration Guide](https://learn.microsoft.com/en-us/semantic-kernel/support/migration/agent-framework-rc-migration-guide)
- [Agent Framework Workflows](https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/overview)

### Code Samples
- [Agent Framework Samples (Python)](../python/samples/)
- [Agent Framework Samples (.NET)](../dotnet/samples/)
- [Workflow Samples](../workflow-samples/)

## 🚀 Getting Started

1. **Assessment**: Review your current implementation
2. **Planning**: Identify migration priorities and dependencies
3. **Incremental Migration**: Start with individual agents or workflows
4. **Testing**: Validate functionality matches or exceeds current capabilities
5. **Optimization**: Leverage new features for enhanced performance

## 📝 Contributing

This is an evolving research directory. Contributions are welcome:
- Add migration examples
- Document edge cases and solutions
- Share lessons learned
- Update with new framework capabilities

## 🔗 Additional Resources

- [AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Agent Framework GitHub Repository](https://github.com/microsoft/agent-framework)
- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)

---

**Last Updated**: October 16, 2025

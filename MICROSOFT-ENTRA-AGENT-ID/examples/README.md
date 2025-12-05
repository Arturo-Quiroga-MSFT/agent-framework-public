# Examples Directory

This directory contains practical code examples demonstrating how to use Microsoft Entra Agent ID in various scenarios.

## Structure

Each subdirectory contains a complete working example with:
- Source code
- README with setup instructions
- Requirements/dependencies
- Environment configuration examples

## Available Examples

### 1. basic-agent-auth/
Basic authentication patterns for agents:
- Client credentials flow (autonomous agent)
- Authorization code flow (interactive agent)
- Managed identity (Azure-hosted agent)
- Token validation and management

### 2. mcp-integration/
Model Context Protocol integration:
- MCP server with agent identity authentication
- MCP client using agent credentials
- Tool registration and invocation
- Secure MCP tool access

### 3. a2a-communication/
Agent-to-Agent protocol examples:
- Agent discovery via registry
- A2A authorization flow
- Agent-to-agent API calls
- Multi-agent orchestration

### 4. azure-foundry/
Azure AI Foundry integration:
- Agent creation with automatic identity
- RBAC configuration
- MCP tools with Foundry
- Deployment and lifecycle management

### 5. dbms-assistant/
Database agent with Microsoft Entra Agent ID:
- SQL Server authentication using agent identity
- MCP tools for database operations
- Row-level security with user context
- Audit logging and compliance

## Coming Soon

- **knowledge-retrieval/** - RAG pattern with agent identities
- **multi-agent-workflow/** - Complex orchestration example
- **conditional-access/** - Policy enforcement examples
- **monitoring/** - Observability and logging

## Prerequisites

All examples require:
- Azure subscription
- Microsoft Entra ID tenant
- Python 3.9+ or .NET 8.0+
- Appropriate Azure RBAC permissions

## Getting Started

1. Choose an example directory
2. Read the README in that directory
3. Install dependencies
4. Configure environment variables
5. Run the example

## Contributing

When adding new examples:
1. Create a new subdirectory
2. Include a comprehensive README
3. Provide working code with error handling
4. Document all configuration steps
5. Add requirements/dependencies file
6. Update this index

---

**Back to**: [Main README](../README.md)

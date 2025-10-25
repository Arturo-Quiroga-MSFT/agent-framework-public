# Model Context Protocol (MCP) - Hosted vs Local

## What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol that allows AI agents to connect to external tools and data sources. Think of it as a universal adapter that lets your AI agent access various services, databases, APIs, and tools in a consistent way.

## The Two Flavors: Hosted vs Local MCP

### 🌐 Hosted MCP

**Hosted MCP** refers to MCP servers that are deployed and running on remote infrastructure (cloud services).

#### Characteristics:
- ✅ **Managed Infrastructure**: The MCP server runs on someone else's infrastructure
- ✅ **Always Available**: No need to start/stop servers locally
- ✅ **Scalable**: Can handle many concurrent requests
- ✅ **Maintained**: Updates and maintenance handled by the service provider
- ⚠️ **Internet Required**: Needs network connectivity to access
- ⚠️ **Less Control**: You don't control the server configuration

#### Example - Microsoft Learn Hosted MCP:
```python
from agent_framework import HostedMCPTool

# Connect to Microsoft's hosted MCP server for documentation
tool = HostedMCPTool(
    name="Microsoft Learn MCP",
    url="https://learn.microsoft.com/api/mcp",
)
```

**Use Cases:**
- Accessing public APIs and services (Microsoft Learn, GitHub, etc.)
- Production environments where reliability is critical
- When you don't want to manage server infrastructure
- Connecting to proprietary services offered by vendors

---

### 💻 Local MCP

**Local MCP** refers to MCP servers that you run on your own machine or infrastructure.

#### Characteristics:
- ✅ **Full Control**: You manage the server, configuration, and data
- ✅ **Privacy**: Data stays on your infrastructure
- ✅ **Customizable**: Can modify server behavior and add custom tools
- ✅ **Offline Capable**: Can work without internet (if tools don't need it)
- ⚠️ **Setup Required**: You need to install and configure the server
- ⚠️ **Maintenance**: You're responsible for updates and troubleshooting

#### Example - Local MCP Server:
```python
from agent_framework import MCPStreamableHTTPTool

# Connect to a locally-running MCP server
tool = MCPStreamableHTTPTool(
    name="My Local MCP",
    url="http://localhost:3000/mcp",  # Local server
)
```

**Use Cases:**
- Development and testing environments
- Custom internal tools and databases
- Sensitive data that can't leave your infrastructure
- Specialized tools specific to your organization
- When you need to customize server behavior

---

## Key Differences Summary

| Feature | Hosted MCP | Local MCP |
|---------|------------|-----------|
| **Infrastructure** | Cloud/Remote | Your machine/network |
| **Setup Complexity** | Minimal | Moderate to High |
| **Availability** | 24/7 (managed) | When you run it |
| **Customization** | Limited | Full control |
| **Privacy** | Data sent to remote | Data stays local |
| **Maintenance** | Provider handles | You handle |
| **Cost** | Often pay-per-use | Infrastructure + time |
| **Best For** | Production, public APIs | Development, private data |

---

## In Azure AI Agent Framework

### Hosted MCP Tool
```python
from agent_framework import HostedMCPTool

# For services hosted externally
tool = HostedMCPTool(
    name="Microsoft Learn MCP",
    url="https://learn.microsoft.com/api/mcp",
)
```

### Local/Streamable MCP Tool
```python
from agent_framework import MCPStreamableHTTPTool

# For servers you control
tool = MCPStreamableHTTPTool(
    name="My Custom Tools",
    url="http://localhost:3000/mcp",
)
```

---

## When to Use Which?

### Choose **Hosted MCP** when:
- 🌍 You need to access public services (documentation, APIs, etc.)
- 🚀 You want quick setup without infrastructure management
- 📈 You need reliable, scalable access
- 🔒 The service provider offers the tools you need

### Choose **Local MCP** when:
- 🔐 You're working with sensitive or proprietary data
- 🛠️ You need custom tools specific to your organization
- 💰 You want to avoid usage-based pricing
- 🧪 You're developing and testing new MCP tools
- ✈️ You need offline capabilities

---

## Example: Microsoft Learn Documentation Access

Both hosted and local MCP can access the same Microsoft Learn documentation:

**Hosted (Recommended for Production):**
```python
# Microsoft's managed server - always available
tool = HostedMCPTool(
    name="Microsoft Learn MCP",
    url="https://learn.microsoft.com/api/mcp",
)
```

**Local (For Development/Customization):**
```python
# You'd run your own MCP server that connects to Learn API
tool = MCPStreamableHTTPTool(
    name="Microsoft Learn MCP",
    url="http://localhost:3000/mcp",
)
```

---

## Security Considerations

### Hosted MCP:
- ✅ Professional security management
- ⚠️ Data transmitted to third-party servers
- ✅ HTTPS encryption in transit
- ⚠️ Subject to provider's privacy policy

### Local MCP:
- ✅ Full data control and privacy
- ⚠️ You're responsible for security configuration
- ✅ Can use network isolation
- ⚠️ Need to manage SSL/TLS certificates

---

## Getting Started

### Try Hosted MCP:
```bash
# No setup needed - just use it!
streamlit run streamlit_azure_ai_demo.py
# Select "Hosted MCP" from the demo menu
```

### Set Up Local MCP:
```bash
# Install MCP server (example)
npm install -g @modelcontextprotocol/server-example

# Start the server
mcp-server start --port 3000

# Then connect your agent to localhost:3000
```

---

## Learn More

- **MCP Specification**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Azure AI Agent Framework Docs**: Check the samples in `python/samples/getting_started/agents/azure_ai/`
- **Microsoft Learn MCP**: Official hosted service for Microsoft documentation

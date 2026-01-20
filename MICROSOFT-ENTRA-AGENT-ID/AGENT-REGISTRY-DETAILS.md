

## What is the Agent Registry?

**The Microsoft Entra Agent Registry** is a centralized metadata repository and discovery service for AI agents across your organization. Think of it as a "directory service for agents" - similar to how Active Directory provides identity management for users, the Agent Registry provides:

1. **Comprehensive inventory** - tracks all agents (with or without agent identities) across Microsoft and third-party platforms
2. **Discovery service** - enables agents to find other agents based on skills, capabilities, and protocols
3. **Governance and compliance** - enforces policies about which agents can discover/communicate with each other via "collections"
4. **Rich metadata** - stores agent capabilities, skills, endpoints, protocols (MCP, A2A), security schemes, etc.

---

## Key Concepts

**Agent Card Manifest** - JSON document describing an agent's metadata:
- Skills (what it can do)
- Capabilities (technical features it supports)
- Input/output modes (text/plain, application/json, image/png)
- Protocols (MCP, A2A)
- Security schemes (authentication methods)
- Documentation URLs

**Collections** - security boundaries that control discovery:
- Agents must be assigned to collections (explicit, not automatic)
- Agents can only discover other agents in their collections
- Enables Zero Trust and least-privilege discovery

**Discovery APIs** - Graph API endpoints to:
- Register agents: `POST /beta/agentRegistry/agentInstances`
- Query agents: `GET /beta/agentRegistry/agentInstances?$filter=...`
- Search by skills: `$filter=skills/any(s:contains(s/description,'invoice'))`

---

## Use Cases

**1. Agent-to-Agent (A2A) Discovery**
- HR agent needs to find "payroll agent" → queries registry for skill:"payroll processing"
- Orchestrator agent discovers all "data retrieval" agents to delegate subtasks
- Compliance: only agents in "Finance-Approved" collection can discover each other

**2. Enterprise Governance**
- Track all deployed agents (shadow AI prevention)
- Apply conditional access policies based on collections
- Audit trail of which agents discovered/called which agents

**3. Multi-Platform Coordination**
- Copilot Studio agent discovers Python-based custom agent
- Both expose A2A protocol → registry provides endpoints
- Seamless interop despite different tech stacks

**4. Skill-Based Routing**
- User asks: "analyze this invoice"
- Orchestrator queries registry: `GET /agentInstances?$filter=skills/any(s:contains(s/name,'invoice analysis'))`
- Routes to best-match agent

---

## How to Demo It

I can create a demo that shows:

### **Option A: Register & Discover (Read-Only Focus)**
1. **Register our test agents** to the registry via Graph API
   - POST agent card manifest with skills/capabilities
   - Link to agent identity (client ID from our demos)
2. **Query the registry** to discover agents
   - Search by skill: "find agents that can access Azure Storage"
   - Filter by protocol: "show MCP-enabled agents"
3. **Inspect collections**
   - List which collections our agents belong to
   - Show discovery boundaries

### **Option B: A2A Protocol Demo (Agent Communication)**
1. **Set up two agents** with A2A protocol endpoints
2. **Register both** in the registry with different skills
3. **Agent 1 discovers Agent 2** via registry query
4. **Agent 1 calls Agent 2** using A2A message protocol
5. **Show audit trail** of discovery → call flow

### **Option C: Metadata-Driven Orchestration**
1. **Register 3+ agents** with distinct skills:
   - "Weather data retrieval"
   - "Natural language analysis"
   - "Report generation"
2. **Orchestrator agent** queries registry for all skills
3. **Dynamically routes tasks** based on discovered capabilities
4. **Shows collection-based access control** (deny cross-collection discovery)

---

**Which demo approach interests you most?** 

- **Lightweight**: Just registration + query (Option A) - we can add this to the notebook as a new section
- **Full-stack**: A2A protocol communication (Option B) - requires setting up protocol endpoints
- **Practical**: Orchestration scenario (Option C) - best shows real-world value


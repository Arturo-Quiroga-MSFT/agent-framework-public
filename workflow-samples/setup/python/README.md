# Python Agent Creation Script

Python equivalent of the .NET `CreateAgents` program for creating Azure AI Foundry agents from YAML definitions.

## Purpose

This script reads agent definition YAML files (from the parent `setup/` directory) and creates the agents in your Azure AI Foundry project. It outputs shell commands to configure environment variables for use with declarative workflows.

## Prerequisites

### 1. Python Environment

```bash
# Ensure Python 3.11+ is installed
python --version

# Create/activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install azure-ai-projects azure-identity pyyaml
```

### 3. Azure Authentication

```bash
# Login to Azure CLI
az login

# Verify authentication
az account show
```

### 4. Environment Variables

Set these before running the script:

```bash
# Required: Your Azure AI Foundry project endpoint
export FOUNDRY_PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project-id>"

# Required: Model deployment name
export FOUNDRY_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"

# Optional: Bing Grounding connection (for agents using web search)
export FOUNDRY_CONNECTION_GROUNDING_TOOL="mybinggrounding"
```

To find your project endpoint:
1. Go to [Azure AI Foundry portal](https://ai.azure.com)
2. Select your project
3. Go to **Overview** → **Libraries** → **Azure AI Foundry**
4. Copy the endpoint URL

## Usage

### Create All Agents

Process all `*.yaml` files in the parent `setup/` directory:

```bash
python create_agents.py
```

### Create Specific Agents

Specify one or more YAML files:

```bash
python create_agents.py ../QuestionAgent.yaml ../StudentAgent.yaml
```

## Output

The script will:

1. **Process each YAML file** and create agents in Azure AI Foundry
2. **Display progress** with agent details (ID, name, description, tools)
3. **Generate export commands** for bash/zsh and PowerShell

Example output:

```
🚀 Creating Azure AI Foundry Agents
   Project: https://myresource.services.ai.azure.com/api/projects/myproject
   Model:   gpt-4o-mini

📋 Found 8 agent definition(s)

📄 Processing: AnalystAgent.yaml
  ✓ Created agent: ResearchAnalyst
    ID:          asst_abc123xyz
    Model:       gpt-4o-mini
    Description: Demo agent for DeepResearch workflow
    Tools:       1 tool(s)

📄 Processing: StudentAgent.yaml
  ✓ Created agent: Student
    ID:          asst_def456uvw
    Model:       gpt-4o-mini
    Description: Student agent for MathChat workflow

================================================================================
✅ Successfully created 8 agent(s)

================================================================================

📋 BASH/ZSH Configuration:

# Add these to your ~/.bashrc or ~/.zshrc:

export FOUNDRY_AGENT_RESEARCHANALYST="asst_abc123xyz"
export FOUNDRY_AGENT_STUDENT="asst_def456uvw"
export FOUNDRY_AGENT_TEACHER="asst_ghi789rst"
...

================================================================================

📋 PowerShell Configuration:

# Run these commands in PowerShell:

$env:FOUNDRY_AGENT_RESEARCHANALYST = "asst_abc123xyz"
$env:FOUNDRY_AGENT_STUDENT = "asst_def456uvw"
$env:FOUNDRY_AGENT_TEACHER = "asst_ghi789rst"
...
```

## Agent Definitions

The script processes these YAML files from `../`:

- `AnalystAgent.yaml` - Fact analysis (with Bing Grounding)
- `ManagerAgent.yaml` - Planning and coordination
- `CoderAgent.yaml` - Code execution (Code Interpreter)
- `WeatherAgent.yaml` - Weather API (OpenAPI tool)
- `WebAgent.yaml` - Web search (Bing Grounding)
- `StudentAgent.yaml` - Student role (MathChat)
- `TeacherAgent.yaml` - Teacher role (MathChat)
- `QuestionAgent.yaml` - General Q&A

## Tool Support

The script handles these Azure AI Foundry tools:

### Code Interpreter
```yaml
tools:
  - type: code_interpreter
```

### Bing Grounding (Web Search)
```yaml
tools:
  - type: bing_grounding
    options:
      tool_connections:
        - ${FOUNDRY_CONNECTION_GROUNDING_TOOL}
```

### OpenAPI Tools
```yaml
tools:
  - type: openapi
    id: GetCurrentWeather
    description: Retrieves weather data
    options:
      specification: |
        {
          "openapi": "3.1.0",
          ...
        }
```

## Troubleshooting

### Error: "FOUNDRY_PROJECT_ENDPOINT environment variable not set"

**Solution:** Set the required environment variable:
```bash
export FOUNDRY_PROJECT_ENDPOINT="https://your-resource.services.ai.azure.com/api/projects/your-project"
```

### Error: "Authentication failed"

**Solution:** Login to Azure CLI:
```bash
az logout
az login
az account show  # Verify correct subscription
```

### Error: "Environment variable not set: FOUNDRY_MODEL_DEPLOYMENT_NAME"

**Solution:** The YAML file references `${FOUNDRY_MODEL_DEPLOYMENT_NAME}`. Set it:
```bash
export FOUNDRY_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
```

### Error: "Model deployment not found"

**Solution:** Check your model deployment name:
1. Go to Azure AI Foundry portal
2. Select **Models + Endpoints**
3. Find your deployment name (e.g., "gpt-4o-mini", "gpt-4")
4. Ensure it matches `FOUNDRY_MODEL_DEPLOYMENT_NAME`

### Error: "Connection not found: mybinggrounding"

**Solution:** Create Bing Grounding connection:
1. Go to Azure AI Foundry portal
2. Select **Settings** → **Connections**
3. Create a Bing Grounding connection
4. Set environment variable:
```bash
export FOUNDRY_CONNECTION_GROUNDING_TOOL="your-connection-name"
```

## Comparison with .NET Version

| Feature | .NET (C#) | Python |
|---------|-----------|--------|
| **Language** | C# | Python 3.11+ |
| **SDK** | Azure.AI.Agents.Persistent | azure-ai-projects |
| **Dependencies** | .NET 8 SDK, NuGet packages | pip packages |
| **YAML Parsing** | Semantic Kernel YAML | PyYAML |
| **Tool Support** | Full | Full |
| **Output** | PowerShell + dotnet user-secrets | Bash/ZSH + PowerShell |
| **Execution** | `dotnet run` | `python create_agents.py` |

Both versions produce the same agents and environment variable configurations.

## Integration with Workflows

After creating agents, use them with declarative workflows:

```bash
# Set environment variables (from script output)
export FOUNDRY_AGENT_ANSWER="asst_xxx"
export FOUNDRY_AGENT_STUDENT="asst_yyy"
# ... etc

# Run .NET declarative workflow demo
cd ../../../dotnet/samples/GettingStarted/Workflows/Declarative/ExecuteWorkflow
dotnet run Marketing
dotnet run MathChat
dotnet run DeepResearch
```

## Next Steps

1. **Configure your shell:** Copy export commands from script output
2. **Test workflows:** Run declarative workflow demos
3. **Create custom agents:** Add new YAML files and re-run script
4. **Integrate with workshop:** Use for Module 3 orchestration demos

## Resources

- **Agent Framework Docs:** [learn.microsoft.com/agent-framework](https://learn.microsoft.com/agent-framework)
- **Azure AI Projects SDK:** [pypi.org/project/azure-ai-projects](https://pypi.org/project/azure-ai-projects)
- **Declarative Workflows:** `/workflow-samples/README.md`
- **Workshop Guide:** `/AQ-CODE/docs/WORKFLOW_SAMPLES_GUIDE.md`

# Agent Definitions

The sample workflows rely on agents defined in your Azure Foundry Project.

These agent definitions are based on _Semantic Kernel_'s _Declarative Agent_ feature:

- [Semantic Kernel Agents](https://github.com/microsoft/semantic-kernel/tree/main/dotnet/src/Agents)
- [Declarative Agent Extensions](https://github.com/microsoft/semantic-kernel/tree/main/dotnet/src/Agents/Yaml)
- [Sample](https://github.com/microsoft/semantic-kernel/blob/main/dotnet/samples/GettingStartedWithAgents/AzureAIAgent/Step08_AzureAIAgent_Declarative.cs)

## Creating Agents

### Option 1: Python (Recommended for Python Developers)

```bash
cd python
pip install -r requirements.txt
python create_agents.py
```

See [`python/README.md`](./python/README.md) for detailed instructions.

### Option 2: .NET (PowerShell)

Run the [`Create.ps1`](./Create.ps1) script:

```powershell
./Create.ps1
```

This will create the agents for the sample workflows in your Azure Foundry Project and format a script you can copy and use to configure your environment.

> Note: Both scripts rely upon the `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL_DEPLOYMENT_NAME` environment variables. See [README.md](../../dotnet/samples/GettingStarted/Workflows/Declarative/README.md) from the demo for configuration details.

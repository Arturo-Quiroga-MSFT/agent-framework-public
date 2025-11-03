# Migration Code Examples

This directory contains practical code examples demonstrating migration patterns from Semantic Kernel and AutoGen to Microsoft Agent Framework.

## Directory Structure

```
examples/
├── semantic-kernel/          # Semantic Kernel migration examples
│   ├── simple-agent/        # Basic agent migration
│   ├── agent-with-plugins/  # Plugin-based agent
│   ├── multi-agent/         # Multi-agent orchestration
│   └── openai-assistant/    # OpenAI Assistant agent
├── autogen/                 # AutoGen migration examples
│   ├── conversable-agent/   # Basic conversable agent
│   ├── group-chat/          # Group chat pattern
│   ├── magentic-one/        # Magentic-One pattern
│   └── human-in-loop/       # Human interaction
└── common/                  # Common patterns across both
    ├── function-calling/    # Function calling examples
    ├── workflows/           # Workflow patterns
    └── testing/             # Testing patterns
```

## Quick Reference

### Semantic Kernel Examples

| Example | Description | Files |
|---------|-------------|-------|
| **Simple Agent** | Basic chat agent migration | [simple-agent/](./semantic-kernel/simple-agent/) |
| **Agent with Plugins** | Plugin registration and usage | [agent-with-plugins/](./semantic-kernel/agent-with-plugins/) |
| **Multi-Agent** | Agent orchestration patterns | [multi-agent/](./semantic-kernel/multi-agent/) |
| **OpenAI Assistant** | Assistant API integration | [openai-assistant/](./semantic-kernel/openai-assistant/) |

### AutoGen Examples

| Example | Description | Files |
|---------|-------------|-------|
| **Conversable Agent** | Basic agent conversation | [conversable-agent/](./autogen/conversable-agent/) |
| **Group Chat** | Group chat migration | [group-chat/](./autogen/group-chat/) |
| **Magentic-One** | Magentic orchestration | [magentic-one/](./autogen/magentic-one/) |
| **Human-in-Loop** | Human interaction patterns | [human-in-loop/](./autogen/human-in-loop/) |

## Common Patterns

### Function Calling
- [Simple Function](./common/function-calling/simple-function/)
- [Plugin Class](./common/function-calling/plugin-class/)
- [Async Functions](./common/function-calling/async-functions/)

### Workflows
- [Sequential](./common/workflows/sequential/)
- [Concurrent](./common/workflows/concurrent/)
- [Conditional](./common/workflows/conditional/)

### Testing
- [Unit Tests](./common/testing/unit-tests/)
- [Integration Tests](./common/testing/integration-tests/)
- [Mocking](./common/testing/mocking/)

## How to Use These Examples

### 1. Find Your Scenario

Browse the examples to find one that matches your use case:

```bash
# List all examples
ls -R examples/

# View a specific example
cat examples/semantic-kernel/simple-agent/README.md
```

### 2. Compare Before/After

Each example shows:
- **Before**: Original Semantic Kernel or AutoGen code
- **After**: Migrated Agent Framework code
- **Explanation**: Key changes and rationale

### 3. Run the Examples

Most examples include:
- `before.cs` or `before.py` - Original code
- `after.cs` or `after.py` - Migrated code
- `README.md` - Detailed explanation
- `requirements.txt` or `.csproj` - Dependencies

### 4. Adapt to Your Code

Copy the patterns and adapt:
1. Identify similar patterns in your code
2. Review the "Key Changes" section
3. Apply the transformation
4. Test thoroughly

## Running Examples

### Python Examples

```bash
cd examples/semantic-kernel/simple-agent/
pip install -r requirements.txt
python before.py   # Run original
python after.py    # Run migrated
```

### C# Examples

```bash
cd examples/semantic-kernel/simple-agent/
dotnet restore
dotnet run --project Before/Before.csproj
dotnet run --project After/After.csproj
```

## Contributing Examples

Have a migration pattern to share? Please contribute!

1. Create a new directory under the appropriate category
2. Include `before` and `after` code
3. Add a `README.md` explaining the migration
4. Submit a pull request

### Example Structure

```
your-example/
├── README.md              # Explanation of the pattern
├── before.py|.cs         # Original code
├── after.py|.cs          # Migrated code
├── requirements.txt|.csproj # Dependencies
└── notes.md              # Optional: Additional notes
```

## Tips for Migration

### Start Simple
Begin with the simplest examples and work your way up to complex scenarios.

### Test Incrementally
Migrate one component at a time and test before moving to the next.

### Use Version Control
Keep your original code in a separate branch for comparison.

### Leverage Tools
Use your IDE's refactoring tools to help with mechanical changes.

## Need Help?

- Check the [FAQ](../faq.md)
- Review the [Migration Guides](../)
- Ask on [GitHub Discussions](https://github.com/microsoft/agent-framework/discussions)
- Open an [Issue](https://github.com/microsoft/agent-framework/issues)

---

**Last Updated**: October 16, 2025

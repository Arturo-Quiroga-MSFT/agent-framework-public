# Agents with GitHub Models - Index

**Complete guide to using Microsoft Agent Framework with GitHub Models**

---

## 📚 Documentation

| File | Purpose | Reading Time |
|------|---------|--------------|
| **[QUICKSTART.md](./QUICKSTART.md)** | Get started in < 5 minutes | 3 minutes |
| **[README.md](./README.md)** | Complete guide and reference | 15 minutes |
| **[COMPARISON.md](./COMPARISON.md)** | vs Azure OpenAI/Foundry | 10 minutes |

**Recommended order:** QUICKSTART → Examples → README → COMPARISON

---

## 💻 Code Examples

### Python Scripts

| File | Description | Difficulty | Time |
|------|-------------|------------|------|
| **[01_basic_github_agent.py](./01_basic_github_agent.py)** | Basic agent with GitHub Models | ⭐️ Beginner | 5 min |
| **[02_github_with_tools.py](./02_github_with_tools.py)** | Agent with function tools | 🔧 Intermediate | 10 min |
| **[03_github_multi_agent.py](./03_github_multi_agent.py)** | Sequential multi-agent workflow | 🔗 Advanced | 15 min |
| **[04_github_parallel_agents.py](./04_github_parallel_agents.py)** | Parallel agent execution | ⚡ Advanced | 15 min |
| **[05_github_sequential_devui.py](./05_github_sequential_devui.py)** | Sequential workflow with DevUI | 🌐 Advanced | 10 min |
| **[06_github_parallel_devui.py](./06_github_parallel_devui.py)** | Parallel agents with DevUI | 🌐 Advanced | 10 min |
| **[07_github_sequential_workflow.py](./07_github_sequential_workflow.py)** | Sequential with WorkflowBuilder | 🏗️ Expert | 15 min |
| **[08_github_parallel_workflow.py](./08_github_parallel_workflow.py)** | Parallel with WorkflowBuilder | 🏗️ Expert | 15 min |
| **[09_github_groupchat_workflow.py](./09_github_groupchat_workflow.py)** | Group Chat with orchestration | 💬 Expert | 15 min |

**Recommended order:** 
- **Scripts:** Run 01 → 02 → 03 → 04 in sequence
- **DevUI Simple:** Run 05 or 06 for interactive testing
- **DevUI Workflows:** Run 07, 08, or 09 for production-ready visualization
  - **07**: Sequential pipeline patterns
  - **08**: Parallel fan-out/fan-in patterns
  - **09**: Group chat collaborative patterns

### Jupyter Notebooks

| File | Description | Type |
|------|-------------|------|
| **[notebooks/github_models_walkthrough.ipynb](./notebooks/github_models_walkthrough.ipynb)** | Interactive tutorial | Tutorial |

**Best for:** Learning MAF concepts interactively

---

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| **[.env.example](./.env.example)** | Environment variable template |
| **[requirements.txt](./requirements.txt)** | Python dependencies |

**Setup:**
```bash
cp .env.example .env
# Edit .env with your GITHUB_TOKEN
pip install -r requirements.txt
```

---

## 🎯 Learning Paths

### Path 1: Quick Start (30 minutes)
1. Read [QUICKSTART.md](./QUICKSTART.md) (3 min)
2. Run `01_basic_github_agent.py` (5 min)
3. Modify the agent instructions (10 min)
4. Try different GitHub models (10 min)

### Path 2: Tool Development (1 hour)
1. Complete Path 1
2. Run `02_github_with_tools.py` (10 min)
3. Create your own custom tool (30 min)
4. Test tool with various queries (15 min)

### Path 3: Multi-Agent Systems (2.5 hours)
1. Complete Path 1 & 2
2. Run `03_github_multi_agent.py` (15 min)
3. Study the sequential workflow pattern (30 min)
4. Run `04_github_parallel_agents.py` (15 min)
5. Compare sequential vs parallel performance (30 min)
6. Build your own multi-agent workflow (30 min)

### Path 4: Interactive DevUI (2 hours)
1. Install DevUI: `pip install agent-framework-devui --pre`
2. Run `05_github_sequential_devui.py` (15 min)
3. Test sequential workflow via web interface (10 min)
4. Run `06_github_parallel_devui.py` (15 min)
5. Compare individual agents in parallel (10 min)
6. Run `07_github_sequential_workflow.py` (15 min)
7. Examine visual workflow diagram (10 min)
8. Run `08_github_parallel_workflow.py` (15 min)
9. Compare parallel workflow visualization (10 min)
10. Run `09_github_groupchat_workflow.py` (15 min)
11. Explore group chat conversation flow (10 min)

### Path 5: Deep Dive (1 day)
1. Complete all above
2. Work through Jupyter notebook (2 hours)
3. Read full [README.md](./README.md) (30 min)
4. Study [COMPARISON.md](./COMPARISON.md) (30 min)
5. Build a complete project (4 hours)

---

## 🔑 Key Concepts

### What You'll Learn

#### From Examples:
- ✅ Creating MAF agents with GitHub Models
- ✅ Configuring OpenAI-compatible clients
- ✅ Function tool definition and usage
- ✅ Sequential multi-agent orchestration
- ✅ Parallel agent execution with asyncio.gather()
- ✅ DevUI integration for interactive testing
- ✅ Visualizing agent workflows in browser
- ✅ WorkflowBuilder for production workflows
- ✅ Fan-out/fan-in patterns for parallel execution
- ✅ Structured input/output with Pydantic models
- ✅ Rate limit management
- ✅ Error handling best practices

#### From Documentation:
- ✅ GitHub Models vs Azure comparison
- ✅ When to use each provider
- ✅ Migration strategies
- ✅ Production considerations
- ✅ Available models and capabilities
- ✅ Cost optimization

---

## 🚀 Quick Command Reference

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GITHUB_TOKEN
```

### Run Examples
```bash
# Basic agent
python 01_basic_github_agent.py

# Agent with tools
python 02_github_with_tools.py

# Multi-agent workflow
python 03_github_multi_agent.py

# Jupyter notebook
jupyter notebook notebooks/github_models_walkthrough.ipynb
```

### Test Different Models
```bash
# GPT-4o (best reasoning)
GITHUB_MODEL=gpt-4o python 01_basic_github_agent.py

# Llama 3.3 (open source)
GITHUB_MODEL=Llama-3.3-70B-Instruct python 01_basic_github_agent.py

# Phi-4 (small, efficient)
GITHUB_MODEL=Phi-4 python 01_basic_github_agent.py
```

---

## 📊 Feature Matrix

| Feature | Example 01 | Example 02 | Example 03 | Notebook |
|---------|------------|------------|------------|----------|
| Basic Agent | ✅ | ✅ | ✅ | ✅ |
| Function Tools | ❌ | ✅ | ❌ | ✅ |
| Multi-Agent | ❌ | ❌ | ✅ | ✅ |
| Rate Limiting | ✅ | ✅ | ✅ | ✅ |
| Error Handling | ✅ | ✅ | ✅ | ✅ |
| Model Comparison | ❌ | ❌ | ❌ | ✅ |
| Interactive | ❌ | ❌ | ❌ | ✅ |

---

## 🎓 Knowledge Check

After completing the examples and documentation, you should be able to:

- [ ] Create a basic MAF agent with GitHub Models
- [ ] Configure authentication and model selection
- [ ] Define and use custom function tools
- [ ] Build multi-agent workflows
- [ ] Handle rate limits and errors
- [ ] Compare GitHub Models vs Azure providers
- [ ] Migrate from development to production
- [ ] Choose the right model for your task

---

## 🔗 External Resources

### GitHub Models
- [GitHub Models Marketplace](https://github.com/marketplace/models)
- [GitHub Models Documentation](https://docs.github.com/en/github-models)
- [Available Models List](https://github.com/marketplace/models)

### Microsoft Agent Framework
- [MAF Documentation](https://aka.ms/agent-framework)
- [MAF GitHub Repository](https://github.com/microsoft/agent-framework)
- [MAF Quick Start Guide](https://learn.microsoft.com/agent-framework/tutorials/quick-start)
- [Discord Community](https://discord.gg/b5zjErwbQM)

### Azure AI
- [Azure OpenAI Service](https://azure.microsoft.com/products/ai-services/openai-service)
- [Azure AI Foundry](https://ai.azure.com)
- [Azure AI Documentation](https://learn.microsoft.com/azure/ai-services/)

---

## 🆘 Getting Help

### Common Questions

**Q: Which file should I start with?**  
A: Start with [QUICKSTART.md](./QUICKSTART.md), then run `01_basic_github_agent.py`

**Q: I'm getting 401 errors**  
A: Check your `GITHUB_TOKEN` environment variable is set correctly

**Q: I'm getting 429 errors**  
A: You've hit rate limits. Add `await asyncio.sleep(5)` between calls

**Q: Which model should I use?**  
A: `gpt-4o-mini` is recommended for development (fast, efficient)

**Q: Can I use this in production?**  
A: GitHub Models is for development. See [COMPARISON.md](./COMPARISON.md) for production options

**Q: How do I migrate to Azure?**  
A: See "Migration Path" section in [README.md](./README.md#migration-path)

### Get Support

1. **Read Documentation**: Most answers are in README.md
2. **Check Examples**: See how patterns are implemented
3. **GitHub Issues**: https://github.com/microsoft/agent-framework/issues
4. **Discord Community**: https://discord.gg/b5zjErwbQM
5. **Stack Overflow**: Tag `agent-framework`

---

## 📈 Progressive Complexity

```
┌─────────────────────────────────────────────────────┐
│ Level 1: Basic Agent (01_basic_github_agent.py)    │
│ • Simple queries                                     │
│ • Configuration                                      │
│ • Error handling                                     │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Level 2: Tools (02_github_with_tools.py)           │
│ • Function definition                                │
│ • Tool integration                                   │
│ • Automatic tool calling                             │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Level 3: Multi-Agent (03_github_multi_agent.py)    │
│ • Multiple agents                                    │
│ • Sequential workflows                               │
│ • Agent coordination                                 │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Level 4: Production (COMPARISON.md)                │
│ • Azure migration                                    │
│ • Enterprise features                                │
│ • Scale & governance                                 │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps

### Immediate (Today)
- [ ] Read [QUICKSTART.md](./QUICKSTART.md)
- [ ] Set up environment (`.env` file)
- [ ] Run `01_basic_github_agent.py`

### Short Term (This Week)
- [ ] Complete all three Python examples
- [ ] Work through Jupyter notebook
- [ ] Create your first custom tool
- [ ] Build a simple multi-agent workflow

### Medium Term (This Month)
- [ ] Read full [README.md](./README.md)
- [ ] Study [COMPARISON.md](./COMPARISON.md)
- [ ] Try different GitHub models
- [ ] Build a small project

### Long Term (Production)
- [ ] Understand Azure migration path
- [ ] Set up Azure OpenAI (if needed)
- [ ] Plan for production deployment
- [ ] Implement monitoring & logging

---

## � Tracing & Observability

Examples 07 and 08 include **automatic built-in tracing** - no configuration needed!

**Features:**
- ✅ Agent operation names and timing (automatic)
- ✅ Workflow execution visualization in DevUI
- ✅ Performance metrics per agent
- ✅ Real-time execution timeline
- ✅ Works out of the box

Just run the workflows and open DevUI to see traces in the right panel!

```bash
# Run workflow
python 07_github_sequential_workflow.py

# DevUI opens at http://localhost:8082
# Click "Traces" tab in right panel to see execution timeline
```

**Optional Advanced Tracing:**
For external systems (Application Insights, Jaeger), set environment variables:
```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="..."  # Azure
export OTLP_ENDPOINT=http://localhost:4317          # Jaeger/Zipkin
```

**See [TRACING_GUIDE.md](./TRACING_GUIDE.md) for complete documentation.**

---

## �📝 Feedback

Found an issue? Have suggestions? Please:

1. Check existing documentation
2. Test with latest MAF version
3. Open an issue with details
4. Submit a PR with improvements

---

**Ready to start? Open [QUICKSTART.md](./QUICKSTART.md) now! 🚀**

---

*Last Updated: January 1, 2026*  
*Microsoft Agent Framework Community*

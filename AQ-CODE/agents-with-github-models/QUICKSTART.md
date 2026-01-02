# Quick Start Guide: GitHub Models + MAF

Get started with Microsoft Agent Framework using GitHub Models in under 5 minutes.

---

## ⚡ Super Quick Start

### 1. Install Dependencies (30 seconds)

```bash
cd /path/to/agents-with-github-models
pip install agent-framework python-dotenv openai
```

### 2. Get GitHub Token (2 minutes)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Copy the `github_pat_...` token

### 3. Set Environment Variable (10 seconds)

```bash
export GITHUB_TOKEN="github_pat_YOUR_TOKEN_HERE"
export GITHUB_MODEL="gpt-4o-mini"
```

### 4. Run First Agent (30 seconds)

```bash
python 01_basic_github_agent.py
```

**That's it!** 🎉

---

## 📝 Minimal Code Example

```python
import asyncio
import os
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

async def main():
    # Create client
    client = OpenAIChatClient(
        model_id="gpt-4o-mini",
        api_key=os.getenv("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com"
    )
    
    # Create agent
    agent = ChatAgent(
        chat_client=client,
        instructions="You are a helpful assistant."
    )
    
    # Run query
    result = await agent.run("What are AI agents?")
    print(result)

asyncio.run(main())
```

Save as `hello_agent.py` and run: `python hello_agent.py`

---

## 🎯 What to Try Next

### Example 1: Basic Agent
```bash
python 01_basic_github_agent.py
```
Learn: Basic agent creation, simple queries, rate limiting

### Example 2: Agent with Tools
```bash
python 02_github_with_tools.py
```
Learn: Function calling, tool integration, weather/calculator tools

### Example 3: Multi-Agent Workflow
```bash
python 03_github_multi_agent.py
```
Learn: Multiple agents, sequential workflows, agent coordination

### Interactive Tutorial
```bash
jupyter notebook notebooks/github_models_walkthrough.ipynb
```
Learn: Everything in an interactive Jupyter notebook

---

## 🔑 Available Models

Try different models by changing `GITHUB_MODEL`:

```bash
# OpenAI models
export GITHUB_MODEL="gpt-4o"          # Latest GPT-4o
export GITHUB_MODEL="gpt-4o-mini"     # Fast & efficient (default)

# Open-source models
export GITHUB_MODEL="Llama-3.3-70B-Instruct"    # Meta Llama 3.3
export GITHUB_MODEL="Phi-4"                      # Microsoft Phi-4
export GITHUB_MODEL="Mistral-Large-2"           # Mistral AI
```

---

## 🚨 Common Issues

### Issue: `401 Unauthorized`
**Solution:** Check your GITHUB_TOKEN is set correctly
```bash
echo $GITHUB_TOKEN  # Should show github_pat_...
```

### Issue: `429 Too Many Requests`
**Solution:** GitHub Models has ~15 requests/minute limit. Add delays:
```python
import asyncio
await asyncio.sleep(5)  # Wait 5 seconds between calls
```

### Issue: Module not found
**Solution:** Install dependencies
```bash
pip install agent-framework python-dotenv openai
```

---

## 📊 Quick Comparison

| Aspect | GitHub Models | Azure OpenAI |
|--------|---------------|--------------|
| **Cost** | Free | Pay-per-token |
| **Setup Time** | < 5 minutes | 15-30 minutes |
| **Rate Limit** | ~15 RPM | 60-1000+ RPM |
| **Best For** | Development | Production |

**Recommendation:** Start with GitHub Models for learning, migrate to Azure for production.

---

## 🎓 Learning Path

1. **Day 1**: Run `01_basic_github_agent.py` ✅
2. **Day 2**: Try `02_github_with_tools.py` with custom tools
3. **Day 3**: Build `03_github_multi_agent.py` workflows
4. **Week 2**: Explore Jupyter notebook tutorial
5. **Week 3**: Try different models (Llama, Phi)
6. **Ready for Production**: Migrate to Azure OpenAI (see [COMPARISON.md](./COMPARISON.md))

---

## 🔗 Quick Links

- **Full README**: [README.md](./README.md)
- **Comparison Guide**: [COMPARISON.md](./COMPARISON.md)
- **GitHub Models**: https://github.com/marketplace/models
- **MAF Docs**: https://aka.ms/agent-framework
- **Get Help**: https://github.com/microsoft/agent-framework/discussions

---

## 💡 Pro Tips

1. **Use gpt-4o-mini** for development (faster, same features)
2. **Add 5-second delays** between requests to avoid rate limits
3. **Start simple** with basic agent before adding tools
4. **Check examples** in this directory for patterns
5. **Read COMPARISON.md** before migrating to production

---

## 🎯 Your First Agent in 10 Lines

```python
import asyncio, os
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

async def main():
    agent = ChatAgent(
        chat_client=OpenAIChatClient(
            model_id="gpt-4o-mini",
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.inference.ai.azure.com"
        ),
        instructions="You are helpful."
    )
    print(await agent.run("Hello!"))

asyncio.run(main())
```

---

**Ready to build AI agents? Run `python 01_basic_github_agent.py` now! 🚀**

---

*Last Updated: January 1, 2026*

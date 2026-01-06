# Travel Agent Demo - Setup Guide for Jason

Welcome! This guide will help you get the Travel Agent handoff demo working with Azure AI Foundry.

## 📋 What's in This Folder

- **14-handoffjdv.ipynb** - Main notebook with the travel agent demo
- **.env.template** - Template for environment variables
- **validate_setup.py** - Script to validate your setup
- **JASON_TROUBLESHOOTING_SUMMARY.md** - Detailed troubleshooting notes
- **README.md** - This file

## 🚀 Quick Setup (3 Steps)

### Step 1: Authenticate with Azure
```bash
az login
```

### Step 2: Configure Environment
```bash
# Copy the template
cp .env.template .env

# Edit .env with your values
# You need:
# - AZURE_AI_PROJECT_ENDPOINT from https://ai.azure.com → Your Project → Settings
# - AZURE_AI_MODEL_DEPLOYMENT_NAME from Deployments (e.g., gpt-4.1, gpt-4o)
```

### Step 3: Validate Setup
```bash
python validate_setup.py
```

If all checks pass ✅, you're ready to run the notebook!

## 📓 Running the Notebook

1. Open `14-handoffjdv-AQ-modified.ipynb` in VS Code
2. Select Python kernel
3. Run all cells (Shift + Enter)
4. The notebook uses `AzureOpenAIChatClient(credential=AzureCliCredential())` in Cell 7

## 🔧 What Was Fixed

Your notebook had issues with Azure AI Foundry client initialization. Here's what changed:

### Before (Incorrect)
```python
# This was mixing patterns incorrectly
chat_client = AzureOpenAIChatClient(
    credential=DefaultAzureCredential(),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
)
```

### After (Correct)
```python
# Proper Azure AI Foundry pattern
project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential()
)

connection = project_client.connections.get_default(connection_type="AzureOpenAI")

chat_client = AzureOpenAIChatClient.from_connection(
    connection=connection,
    model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
)
```

### Key Benefits of the Fix
- ✅ Uses Foundry project's connection (no manual endpoint management)
- ✅ Simpler configuration (only 2 env vars instead of 3+)
- ✅ Automatic authentication via Entra ID
- ✅ Production-ready pattern

## 📊 Architecture Overview

```
User Request
    ↓
Travel Agent (Triage)
    ↓
   [Routes to specialist based on intent]
    ↓
    ├─→ Flight Booking Agent
    ├─→ Hotel Booking Agent
    ├─→ Car Booking Agent
    └─→ Trip Check Agent
         ↓
    Structured Response
         ↓
    User Confirmation
```

## 🎤 Demo Tips for Your Talk

1. **Start with Context**: Explain why handoff patterns matter
2. **Show the Flow**: Walk through one complete scenario (e.g., flight booking)
3. **Highlight Benefits**:
   - No rate limits (unlike GitHub Models)
   - Enterprise auth (Entra ID)
   - Structured outputs (Pydantic)
   - Multi-turn conversations
4. **Connect to Control Plane**: Show how Foundry manages everything
5. **Live Demo**: Run a scenario live (they're fast!)

## 🐛 Troubleshooting

### "az login" Required
```bash
az login
```

### "No module named 'agent_framework'"
```bash
pip install agent-framework azure-ai-projects azure-identity python-dotenv pydantic
```

### "Connection failed"
- Verify `PROJECT_ENDPOINT` in `.env`
- Check you have access to the Foundry project
- Confirm Azure OpenAI deployment exists

### "Deployment not found"
- Go to your Foundry project → Deployments
- Copy exact deployment name (case-sensitive)
- Update `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` in `.env`

## 📚 Additional Resources

- [Azure AI Foundry Portal](https://ai.azure.com)
- [Agent Framework Docs](https://microsoft.github.io/agent-framework/)
- [Handoff Pattern Guide](https://microsoft.github.io/agent-framework/patterns/handoff/)
- [Your troubleshooting summary](./JASON_TROUBLESHOOTING_SUMMARY.md)

## ✅ Validation Checklist

Before your demo:

- [ ] `az login` successful
- [ ] `.env` file configured with correct values
- [ ] `python validate_setup.py` passes all checks
- [ ] Notebook runs without errors
- [ ] All 4 handoff scenarios work
- [ ] You've tested with different travel queries

## 🎯 Questions Answered

### Q1: How do I switch from GitHub Models to Foundry?
**A:** Cell 7 now has the correct pattern. Just set your `.env` and it works!

### Q2: What's the correct AzureOpenAIChatClient syntax?
**A:** Use `AzureOpenAIChatClient.from_connection()` - see Cell 7

### Q3: Is my async code wrong?
**A:** No! Your async code was already correct. The issue was only in client initialization.

## 💬 Contact

For questions or issues:
- Reach out to Arturo (that's me!)
- Check the troubleshooting summary: `JASON_TROUBLESHOOTING_SUMMARY.md`

---

**Status:** ✅ Ready for your demo next week!

Good luck with the talk! 🎉

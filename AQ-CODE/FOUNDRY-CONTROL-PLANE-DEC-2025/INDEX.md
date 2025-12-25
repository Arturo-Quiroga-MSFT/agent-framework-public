# Persistent Agents & Portal Visibility - Navigation Guide

## 🚀 Quick Start (Choose Your Path)

### I need an answer RIGHT NOW
👉 **[FOR_YOUR_TEAMMATE.md](FOR_YOUR_TEAMMATE.md)** - Direct answer with code

### I want working sample code
👉 **[agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py)** - Copy & run this

### I need to understand the issue
👉 **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page summary

### I want complete documentation
👉 **[ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md)** - Everything explained

---

## 📚 Documentation Index

| Document | Purpose | Read Time | Audience |
|----------|---------|-----------|----------|
| **[FOR_YOUR_TEAMMATE.md](FOR_YOUR_TEAMMATE.md)** | Direct answer to "agents don't show in portal" | 3 min | Anyone with the problem |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | One-page cheat sheet | 2 min | Quick lookup |
| **[VISUAL_GUIDE.md](VISUAL_GUIDE.md)** | Visual diagrams and flowcharts | 5 min | Visual learners |
| **[ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md)** | Complete guide with all details | 10 min | Deep dive |
| **[AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md)** | V1 vs V2 agents explained | 8 min | Understanding context |

---

## 💻 Sample Code

| File | Purpose | Complexity | Recommended |
|------|---------|------------|-------------|
| **[agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py)** | Simple persistent agent | ⭐ Easy | ✅ START HERE |
| [agents/azure_ai_persistent_agent_with_version.py](agents/azure_ai_persistent_agent_with_version.py) | Persistent agent with versioning | ⭐⭐ Medium | Use if you need versions |

---

## 🔧 Utility Scripts

| Script | Purpose |
|--------|---------|
| [deploy_new_agents.py](deploy_new_agents.py) | Deploy 8 sample V2 agents to your project |
| [cleanup_v1_agents.py](cleanup_v1_agents.py) | Remove V1 agents (old portal only) |
| [cleanup_v1_assistants.py](cleanup_v1_assistants.py) | Remove V1 assistants (OpenAI API) |

---

## 🎯 By Use Case

### "My agents don't show in the portal!"
1. Read: [FOR_YOUR_TEAMMATE.md](FOR_YOUR_TEAMMATE.md)
2. Run: [agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py)
3. Fix: Comment out `delete_version()` in your code

### "I need to create persistent agents"
1. Use: [agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py) as template
2. Reference: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for API calls

### "I want to understand V1 vs V2"
1. Read: [AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md)
2. Visual: [VISUAL_GUIDE.md](VISUAL_GUIDE.md)

### "I need to migrate from V1 to V2"
1. Read: [AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md#migration-guide)
2. Run: [cleanup_v1_agents.py](cleanup_v1_agents.py)
3. Deploy: [deploy_new_agents.py](deploy_new_agents.py)

### "I need code examples in C#"
1. Read: [FOR_YOUR_TEAMMATE.md](FOR_YOUR_TEAMMATE.md#c-equivalent)
2. Reference: [ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md#c-equivalent)

---

## 🎓 Learning Path

### Beginner (Just need it to work)
1. ⏱️ 2 min: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. ⏱️ 5 min: Copy & run [agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py)
3. ✅ Done!

### Intermediate (Want to understand)
1. ⏱️ 3 min: [FOR_YOUR_TEAMMATE.md](FOR_YOUR_TEAMMATE.md)
2. ⏱️ 5 min: [VISUAL_GUIDE.md](VISUAL_GUIDE.md)
3. ⏱️ 5 min: Adapt [agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py) to your needs

### Advanced (Need complete knowledge)
1. ⏱️ 10 min: [ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md)
2. ⏱️ 8 min: [AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md)
3. ⏱️ 5 min: Review both sample files in [agents/](agents/)

---

## 📋 Common Questions

| Question | Answer Document |
|----------|----------------|
| Why don't my agents show in the portal? | [FOR_YOUR_TEAMMATE.md](FOR_YOUR_TEAMMATE.md#the-root-cause) |
| What's the difference between V1 and V2? | [AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md#root-cause-two-agent-apis) |
| How do I create a persistent agent? | [QUICK_REFERENCE.md](QUICK_REFERENCE.md#creating-persistent-agents-v2-api) |
| Should I use create_agent() or create_version()? | [ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md#comparison-create_agent-vs-create_version) |
| How do I migrate from V1 to V2? | [AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md#migration-guide) |
| Where can I see working code? | [agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py) |

---

## 🔍 Quick Search

### By Topic

**Portal Visibility**
- [AGENT_PORTALS_EXPLAINED.md](AGENT_PORTALS_EXPLAINED.md)
- [VISUAL_GUIDE.md](VISUAL_GUIDE.md#the-two-agent-apis)

**Agent Creation**
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md#creating-persistent-agents-v2-api)
- [agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py)

**API Comparison**
- [ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md#comparison-create_agent-vs-create_version)
- [VISUAL_GUIDE.md](VISUAL_GUIDE.md#api-method-comparison)

**Troubleshooting**
- [ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md#common-mistakes)
- [VISUAL_GUIDE.md](VISUAL_GUIDE.md#troubleshooting-flow)

---

## 🎯 One-Liner Solutions

```bash
# Quick fix: Remove agent deletion
# In your code's finally block, comment out: delete_version(...)

# Run working sample
python agents/azure_ai_persistent_agent_v2.py

# Deploy multiple agents
python deploy_new_agents.py

# Clean up V1 agents
python cleanup_v1_agents.py
```

---

## 📞 Getting Help

1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for instant answers
2. Run [agents/azure_ai_persistent_agent_v2.py](agents/azure_ai_persistent_agent_v2.py) to verify your setup
3. Read [ANSWER_PERSISTENT_AGENTS.md](ANSWER_PERSISTENT_AGENTS.md) for troubleshooting
4. Ask on team chat with:
   - Which document you read
   - What you tried
   - Error message (if any)

---

## 🏁 Success Checklist

Once you've created a persistent agent, verify:

- [ ] Used `AIProjectClient` (not `AgentsClient`)
- [ ] Used `create_agent()` method
- [ ] Did NOT delete agent in `finally` block
- [ ] Agent shows in `list_agents()` output
- [ ] Agent visible at https://ai.azure.com
- [ ] Can reuse agent in new sessions

---

## 📦 File Tree

```
AQ-CODE/FOUNDRY-CONTROL-PLANE-DEC-2025/
├── INDEX.md                           ← This file (navigation)
├── FOR_YOUR_TEAMMATE.md               ← Quick answer
├── QUICK_REFERENCE.md                 ← One-page cheat sheet
├── VISUAL_GUIDE.md                    ← Diagrams & flowcharts
├── ANSWER_PERSISTENT_AGENTS.md        ← Complete guide
├── AGENT_PORTALS_EXPLAINED.md         ← V1 vs V2 deep dive
├── agents/
│   ├── azure_ai_persistent_agent_v2.py         ← ⭐ RECOMMENDED
│   └── azure_ai_persistent_agent_with_version.py
├── deploy_new_agents.py               ← Deploy samples
├── cleanup_v1_agents.py               ← Clean V1 agents
└── cleanup_v1_assistants.py           ← Clean V1 assistants
```

---

## 🚀 Get Started Now

**Fastest path to success:**

1. Read: [FOR_YOUR_TEAMMATE.md](FOR_YOUR_TEAMMATE.md) (3 minutes)
2. Run: `python agents/azure_ai_persistent_agent_v2.py`
3. Verify: Check https://ai.azure.com

**Done!** Your agent is persistent and visible in the portal. 🎉

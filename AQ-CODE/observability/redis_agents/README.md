# Redis Demos - DevUI Multi-Agent Gallery

This directory contains all Redis workshop demos organized for DevUI's directory-based discovery. All demos will appear in the DevUI agent dropdown menu.

## Quick Start

```bash
# From the observability directory
cd /Users/arturoquiroga/GITHUB/agent-framework-public/AQ-CODE/observability

# Launch DevUI with all Redis demos
devui redis_agents --port 8000
```

Then open your browser to **http://localhost:8000** and you'll see all 4 agents in the dropdown!

## Available Agents

### 1. **PreferenceAssistant** (preference_memory)
- Demonstrates RedisProvider for persistent user preferences
- User-scoped memory (alice_123)
- Try: Tell it your preferences, then switch to other agents and back

### 2. **SupportBot** (conversation_persistence)
- Demonstrates RedisChatMessageStore for conversation history
- Persists across page refreshes and server restarts
- Try: Start a support ticket conversation, refresh page, continue conversation

### 3. **PersonalAssistant** (personal_assistant)
- Demonstrates multi-agent memory isolation
- Only knows personal life information
- Same user (alice_123) as WorkAssistant but separate memory scope
- Try: Tell it about your hobbies and personal life

### 4. **WorkAssistant** (work_assistant)
- Demonstrates multi-agent memory isolation
- Only knows work-related information
- Same user (alice_123) as PersonalAssistant but separate memory scope
- Try: Tell it about your work projects and meetings

## Memory Isolation Demo

The power of the multi-agent demos:

1. Select **PersonalAssistant** and say: "I love hiking and yoga"
2. Select **WorkAssistant** and say: "I'm working on an ML project"
3. Switch back to **PersonalAssistant** and ask: "What do you know about me?"
   - ✅ Will remember hiking/yoga
   - ❌ Will NOT know about ML project
4. Switch to **WorkAssistant** and ask: "What do you know about me?"
   - ✅ Will remember ML project
   - ❌ Will NOT know about hiking/yoga

## Directory Structure

```
redis_agents/
├── preference_memory/
│   └── __init__.py          # Exports: agent = PreferenceAssistant
├── conversation_persistence/
│   └── __init__.py          # Exports: agent = SupportBot
├── personal_assistant/
│   └── __init__.py          # Exports: agent = PersonalAssistant
└── work_assistant/
    └── __init__.py          # Exports: agent = WorkAssistant
```

## Prerequisites

- Redis running: `docker run -p 6379:6379 -d redis:8.0.3`
- Environment variables configured in parent `.env` file
- Azure CLI authenticated: `az login`

## Key Features

✅ **All agents in one UI** - No need to run separate servers  
✅ **Persistent memory** - Data survives page refreshes and restarts  
✅ **Memory isolation** - Each agent has its own memory scope  
✅ **Easy switching** - Use dropdown to switch between agents  
✅ **Conversation history** - DevUI automatically manages conversations  

## Comparison with Standalone Scripts

| Feature | Standalone Scripts | DevUI Gallery |
|---------|-------------------|---------------|
| Agent switching | Need to stop/start servers | Dropdown menu |
| Port management | Manual (8000, 8001, 8002, 8003) | Single port (8000) |
| Multi-agent testing | Requires 2 terminals | Click dropdown |
| Conversation history | Manual thread management | Automatic |
| Memory persistence | ✅ Yes | ✅ Yes |

## Tips

💡 **Persistence Test**: Make changes in any agent, stop DevUI (Ctrl+C), restart with `devui redis_agents`, and your data is still there!

💡 **Memory Isolation**: Switch between PersonalAssistant and WorkAssistant to see how they maintain separate memory scopes despite being the same user.

💡 **Fresh Start**: To reset all data:
```bash
redis-cli FLUSHALL
```

## Workshop Usage

This structure is perfect for workshop demonstrations:

1. **Demo 1** (5 min): Show PreferenceAssistant learning preferences
2. **Demo 2** (5 min): Show SupportBot conversation persistence (refresh page mid-conversation)
3. **Demo 3** (10 min): Show PersonalAssistant vs WorkAssistant memory isolation

All in one UI, no terminal juggling! 🎯

# Redis DevUI Demos - Quick Reference

**Interactive demos for workshop presentations using DevUI**

---

## Overview

Three interactive DevUI demos showcase Redis persistence capabilities:

| Demo | Ports | Focus | Duration |
|------|-------|-------|----------|
| **Preferences** | 8000 | RedisProvider memory | 10 mins |
| **Persistence** | 8001 | RedisChatMessageStore | 10 mins |
| **Multi-Agent** | 8002, 8003 | Memory isolation | 10 mins |

---

## Prerequisites

```bash
# 1. Start Redis
docker run --name redis -p 6379:6379 -d redis:8.0.3

# 2. Activate environment
cd /path/to/agent-framework-public
source .venv/bin/activate

# 3. Navigate to demos
cd AQ-CODE/observability

# 4. Verify .env file has required variables
cat .env | grep -E "AZURE_OPENAI_ENDPOINT|AZURE_AI_MODEL_DEPLOYMENT_NAME"
```

---

## Demo 1: Smart Preference Memory

**File**: `redis_demo_preferences_devui.py`  
**Port**: 8000  
**Component**: RedisProvider  
**Duration**: 10 minutes

### Launch
```bash
python redis_demo_preferences_devui.py
```

Open: http://localhost:8000

### Demo Script

**Teaching Phase** (3 minutes)
```
User: Hi! I'm Alice. I'm vegetarian and love Italian food.
User: I also prefer organic ingredients when possible.
User: I live in Seattle, Washington.
```

**Retrieval Phase** (3 minutes)
```
User: Can you recommend a restaurant for dinner tonight?
User: What do you remember about my food preferences?
```

**Expansion Phase** (2 minutes)
```
User: I should mention I'm allergic to nuts.
User: Recommend a restaurant considering everything you know.
```

**Key Points to Highlight**:
- ✅ Preferences stored automatically (no explicit "save")
- ✅ Context retrieved for each query
- ✅ Try refreshing page - memory persists!
- ✅ User-scoped memory isolation

---

## Demo 2: Resume Conversations

**File**: `redis_demo_persistence_devui.py`  
**Port**: 8001  
**Component**: RedisChatMessageStore  
**Duration**: 10 minutes

### Launch
```bash
python redis_demo_persistence_devui.py
```

Open: http://localhost:8001

### Demo Script

**Session 1 - Initial Contact** (2 minutes)
```
User: Hi, I'm having issues with my order. Order number is ORD-98765.
User: The product arrived damaged - the screen has a crack.
```

**Simulate Restart** (1 minute)
- Stop server: Ctrl+C
- Restart: `python redis_demo_persistence_devui.py`
- Reopen: http://localhost:8001

**Session 2 - Resume** (3 minutes)
```
User: Hi, I'm following up on my damaged order. Did you find anything?
User: What are my options for replacement or refund?
```

**Simulate Another Restart** (1 minute)
- Stop and restart again

**Session 3 - Resolution** (3 minutes)
```
User: I'd like to proceed with the replacement option.
User: Can you summarize everything we've discussed?
```

**Key Points to Highlight**:
- ✅ Conversation history survives restarts
- ✅ Agent remembers full context
- ✅ Support ticket use case (TICKET-12345)
- ✅ No need to re-explain issues

---

## Demo 3: Multi-Agent Isolation

**File**: `redis_demo_multi_agent_devui.py`  
**Ports**: 8002 (Personal), 8003 (Work)  
**Component**: RedisProvider with agent_id isolation  
**Duration**: 10 minutes

### Launch

**Important**: Run TWO separate terminal windows

**Terminal 1 - Personal Assistant:**
```bash
python redis_demo_multi_agent_devui.py --agent personal
```

**Terminal 2 - Work Assistant:**
```bash
python redis_demo_multi_agent_devui.py --agent work
```

Open TWO tabs:
- Personal Assistant: http://localhost:8002
- Work Assistant: http://localhost:8003

**Note**: DevUI's `serve()` function runs synchronously, so we can't run both servers in one process.

### Demo Script

**Personal Assistant (port 8002)** - 3 minutes
```
User: Hi! I love hiking and spend weekends in the Cascades.
User: I'm vegetarian and prefer organic food.
User: I practice yoga every morning at 6 AM.
User: What do you know about my hobbies?
```

**Work Assistant (port 8003)** - 3 minutes
```
User: Hi! I'm working on an ML project for customer segmentation.
User: I have team meetings every Tuesday at 2 PM.
User: My tech stack is Python, TensorFlow, and Azure ML.
User: What projects am I working on?
```

**Cross-Agent Test** - 4 minutes

In Personal Assistant (8002):
```
User: Do you know anything about my work projects?
Expected: NO - only knows personal information
```

In Work Assistant (8003):
```
User: Do you know about my exercise routine?
Expected: NO - only knows work information
```

**Key Points to Highlight**:
- ✅ Same user (alice_123), different contexts
- ✅ Complete memory isolation
- ✅ Enterprise multi-tenant pattern
- ✅ Same Redis index, different logical partitions

---

## Troubleshooting

### Redis Not Running
```bash
# Check if Redis is running
docker ps | grep redis

# If not, start it
docker run --name redis -p 6379:6379 -d redis:8.0.3

# Test connection
redis-cli ping
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Environment Variables Missing
```bash
# Check .env file
cat AQ-CODE/observability/.env

# Should contain:
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

### Clear Redis Data (Start Fresh)
```bash
# Clear all demo data
redis-cli FLUSHDB

# Or clear specific keys
redis-cli KEYS "*devui*"
redis-cli DEL <key>
```

---

## Workshop Tips

### Before Workshop
1. ✅ Test all demos work on your machine
2. ✅ Have Redis running in background
3. ✅ Prepare browser tabs (8000, 8001, 8002, 8003)
4. ✅ Clear Redis data: `redis-cli FLUSHDB`

### During Workshop
1. ✅ Run Demo 1 first (easiest to understand)
2. ✅ Show actual refresh for persistence proof
3. ✅ For Demo 2, do the stop/restart live
4. ✅ For Demo 3, arrange browser windows side-by-side

### After Workshop
1. ✅ Share demo scripts with attendees
2. ✅ Provide Redis setup instructions
3. ✅ Link to REDIS_PERSISTENCE_SAMPLES.md
4. ✅ Stop all servers: Ctrl+C each terminal

---

## Quick Command Reference

```bash
# Start all prerequisites
docker run --name redis -p 6379:6379 -d redis:8.0.3
source .venv/bin/activate
cd AQ-CODE/observability

# Run demos (in separate terminals as needed)
python redis_demo_preferences_devui.py         # Terminal 1 - port 8000
python redis_demo_persistence_devui.py         # Terminal 2 - port 8001

# Multi-agent demo requires TWO terminals
python redis_demo_multi_agent_devui.py --agent personal  # Terminal 3 - port 8002
python redis_demo_multi_agent_devui.py --agent work      # Terminal 4 - port 8003

# Stop servers
# Ctrl+C in each terminal

# Cleanup
docker stop redis
docker rm redis
```

---

## Additional Resources

- **Full Documentation**: `REDIS_PERSISTENCE_SAMPLES.md`
- **Console Versions**: `redis_demo_*.py` (without _devui suffix)
- **Redis Package**: `python/packages/redis/README.md`
- **Framework Samples**: `python/samples/getting_started/context_providers/redis/`

---

**Last Updated**: November 2025  
**Workshop**: Microsoft Agent Framework - Redis Persistence Module

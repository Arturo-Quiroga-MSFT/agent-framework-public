# Redis Persistence Workshop - Microsoft Agent Framework

**Duration**: 45 minutes  
**Level**: Intermediate  
**Prerequisites**: Basic understanding of agents, Python async/await, Redis basics

## Overview

This workshop demonstrates how to use Redis for persistent agent memory and conversation storage in the Microsoft Agent Framework. You'll learn when and how to use **RedisProvider** for contextual memory and **RedisChatMessageStore** for conversation persistence.

---

## Learning Objectives

By the end of this workshop, you will:

1. ✅ Understand the difference between RedisProvider and RedisChatMessageStore
2. ✅ Implement persistent memory for user preferences across sessions
3. ✅ Build conversation persistence that survives application restarts
4. ✅ Configure multi-agent memory isolation for enterprise scenarios
5. ✅ Apply production-ready Redis configurations

---

## Workshop Structure

| Section | Duration | Topic |
|---------|----------|-------|
| Part 1 | 20 mins | **RedisProvider**: Memory & Context |
| Part 2 | 20 mins | **RedisChatMessageStore**: Conversation Persistence |
| Part 3 | 5 mins | **Production Considerations** |

---

## Part 1: RedisProvider for Memory & Context (20 minutes)

### What is RedisProvider?

**RedisProvider** is a context provider that stores and retrieves agent memory using Redis with RediSearch. It enables:

- **Persistent context** across sessions and threads
- **Smart retrieval** via full-text search or hybrid vector search
- **Scoped memory** using partition keys (application_id, agent_id, user_id, thread_id)
- **Tool memory** - remembers outputs from tool executions

### When to Use RedisProvider

✅ **Use RedisProvider when you need:**
- Agents to remember user preferences across sessions
- Context from previous conversations (even days later)
- Multi-turn conversations with long-term memory
- Tool outputs to be searchable and retrievable
- Multi-agent systems with isolated memory per agent

❌ **Don't use RedisProvider when:**
- You only need short-term memory (use in-memory context)
- You're storing simple chat history (use RedisChatMessageStore)
- You don't need search/retrieval capabilities

### Demo 1: Smart Preference Memory

**Scenario**: Personal assistant that remembers user preferences

**File**: `redis_demo_preferences.py`

**What it demonstrates:**
- Storing user preferences in RedisProvider
- Retrieving context across multiple sessions
- Scoped memory using user_id
- Natural language memory queries

**Key concepts:**
```python
# Create provider with user scope
provider = RedisProvider(
    redis_url="redis://localhost:6379",
    index_name="preferences_demo",
    application_id="workshop_app",
    agent_id="personal_assistant",
    user_id="alice_123",  # Scope to specific user
)

# Agent automatically stores and retrieves context
agent = client.create_agent(
    name="PreferenceAssistant",
    instructions="Remember user preferences and personalize responses",
    context_providers=provider,
)
```

**Try it yourself:**
```bash
# Console version
python redis_demo_preferences.py

# Interactive DevUI version (recommended for workshops)
python redis_demo_preferences_devui.py
# Then open: http://localhost:8000
```

**DevUI Features:**
- 🎨 Interactive chat interface with real-time responses
- 💾 Visual confirmation of stored preferences
- 🔄 Test persistence by refreshing the page
- 📊 Better for live demos and hands-on workshops

### Demo 3: Multi-Agent Isolation

**Scenario**: Personal assistant vs Work assistant with separate memories

**File**: `redis_demo_multi_agent.py`

**What it demonstrates:**
- Memory isolation using different agent_id values
- Same user accessing multiple agents
- Enterprise multi-tenant patterns
- Context separation by agent role

**Key concepts:**
```python
# Personal agent with its own memory scope
personal_provider = RedisProvider(
    redis_url="redis://localhost:6379",
    index_name="multi_agent_demo",
    agent_id="agent_personal",  # Different agent_id
    user_id="alice_123",
)

# Work agent with separate memory scope
work_provider = RedisProvider(
    redis_url="redis://localhost:6379",
    index_name="multi_agent_demo",
    agent_id="agent_work",  # Different agent_id
    user_id="alice_123",  # Same user
)
```

**Try it yourself:**
```bash
# Console version
python redis_demo_multi_agent.py

# Interactive DevUI version (recommended for workshops)
python redis_demo_multi_agent_devui.py
# Then open:
#   Personal Assistant: http://localhost:8002
#   Work Assistant:     http://localhost:8003
```

**DevUI Features:**
- 🎨 Side-by-side agent interfaces
- 🔀 Test both agents simultaneously in different browser tabs
- 🔒 Visual proof of memory isolation
- 🎯 Perfect for demonstrating enterprise multi-tenant patterns

### RedisProvider Scoping Strategies

| Scope Level | Use Case | Configuration |
|-------------|----------|---------------|
| **Global Thread** | Share memory across all threads | `thread_id="fixed_value"` |
| **Per-Operation** | Isolate memory per thread | `scope_to_per_operation_thread_id=True` |
| **Multi-Agent** | Separate memory per agent | Different `agent_id` values |
| **Multi-User** | Separate memory per user | Different `user_id` values |

---

## Part 2: RedisChatMessageStore for Conversation Persistence (20 minutes)

### What is RedisChatMessageStore?

**RedisChatMessageStore** stores conversation history in Redis Lists. It enables:

- **Persistent chat history** that survives application restarts
- **Thread-based isolation** with unique thread IDs
- **Message limits** with automatic trimming
- **Serialization support** for saving/loading thread state

### When to Use RedisChatMessageStore

✅ **Use RedisChatMessageStore when you need:**
- Conversations to persist across application restarts
- User session management with conversation history
- Long-running conversations with message limits
- Multi-session support (users returning later)
- Thread state serialization for distributed systems

❌ **Don't use RedisChatMessageStore when:**
- You need semantic search over conversations (use RedisProvider)
- You only need ephemeral in-memory chat (use default memory store)
- You're building real-time context retrieval (use RedisProvider)

### Demo 2: Resume Conversations

**Scenario**: Customer support bot that resumes conversations after restart

**File**: `redis_demo_persistence.py`

**What it demonstrates:**
- Storing conversation history in Redis
- Resuming conversations across sessions
- Message limits and automatic trimming
- Simulating application restart scenarios

**Key concepts:**
```python
# Phase 1: Start conversation
store = RedisChatMessageStore(
    redis_url="redis://localhost:6379",
    thread_id="support_ticket_12345",  # Unique conversation ID
    max_messages=50,  # Limit stored messages
)

thread = AgentThread(message_store=store)

# Phase 2: Resume after "restart" (new store, same thread_id)
store2 = RedisChatMessageStore(
    redis_url="redis://localhost:6379",
    thread_id="support_ticket_12345",  # Same ID loads history
)

thread2 = AgentThread(message_store=store2)
# Agent can now access previous conversation context
```

**Try it yourself:**
```bash
# Console version
python redis_demo_persistence.py

# Interactive DevUI version (recommended for workshops)
python redis_demo_persistence_devui.py
# Then open: http://localhost:8001
# Stop with Ctrl+C, restart the script, and see history preserved!
```

**DevUI Features:**
- 🎨 Interactive support ticket interface
- 🔄 Real demonstration of "resume after restart" scenario
- 📝 Message history visible in the UI
- 💬 Natural conversation flow across restarts

### RedisChatMessageStore Features

| Feature | Purpose | Example |
|---------|---------|---------|
| **thread_id** | Unique conversation identifier | `"user_123_session_456"` |
| **max_messages** | Auto-trim old messages | `max_messages=50` |
| **list_messages()** | Retrieve stored messages | `await store.list_messages()` |
| **clear()** | Delete conversation history | `await store.clear()` |
| **serialize()** | Save thread state | `await thread.serialize()` |

---

## Part 3: Production Considerations (5 minutes)

### Redis Setup Options

#### Option 1: Docker (Development)
```bash
docker run --name redis -p 6379:6379 -d redis:8.0.3
```
**Pros**: Quick setup, free, local testing  
**Cons**: Not production-ready, no HA

#### Option 2: Redis Cloud (Small Scale)
- **URL**: https://redis.io/cloud/
- **Free Tier**: 30MB storage, RediSearch enabled
- **Pros**: Managed, free tier, production features  
**Cons**: Storage limits on free tier

#### Option 3: Azure Managed Redis (Enterprise)
- **Service**: Azure Cache for Redis Enterprise
- **Cost**: ~$12/month (E10 tier)
- **Pros**: Enterprise features, Azure integration, high availability  
**Cons**: Cost, requires Azure subscription

### Performance Best Practices

1. **Connection Pooling**: Reuse Redis connections
   ```python
   # Good: Single RedisProvider instance
   provider = RedisProvider(redis_url="...")
   
   # Bad: Creating new provider per request
   ```

2. **Message Limits**: Set `max_messages` to prevent unbounded growth
   ```python
   RedisChatMessageStore(max_messages=100)
   ```

3. **Index Management**: Use meaningful index names
   ```python
   RedisProvider(index_name="prod_app_v1_context")
   ```

4. **Scope Appropriately**: Use partition keys for multi-tenancy
   ```python
   RedisProvider(
       application_id="myapp",
       agent_id="support_bot",
       user_id=user.id,
   )
   ```

### Security Best Practices

1. **Authentication**: Use Redis ACLs or password authentication
   ```python
   redis_url="redis://:password@host:6379"
   ```

2. **TLS/SSL**: Enable for production
   ```python
   redis_url="rediss://host:6379"  # Note the 'rediss://'
   ```

3. **Network Isolation**: Use VPCs/VNets in cloud deployments

4. **Key Expiration**: Set TTLs for temporary data
   ```python
   # Configure in Redis or via RedisChatMessageStore settings
   ```

---

## Component Comparison

| Feature | RedisProvider | RedisChatMessageStore |
|---------|---------------|----------------------|
| **Purpose** | Context & memory retrieval | Chat history storage |
| **Search** | Full-text + vector search | Sequential message lists |
| **Use Case** | Long-term memory, preferences | Conversation persistence |
| **Scoping** | Multi-dimensional (app/agent/user/thread) | Thread-based |
| **Retrieval** | Smart context search | Sequential message loading |
| **Tool Memory** | ✅ Remembers tool outputs | ❌ Only chat messages |

---

## Quick Reference: When to Use What

### Use RedisProvider when:
- 🧠 Agent needs to **remember** user preferences
- 🔍 You need to **search** through past context
- 🛠️ Tool outputs should be **retrievable**
- 🎯 Multi-agent systems need **isolated memory**
- 📊 Semantic search over conversations

### Use RedisChatMessageStore when:
- 💬 Storing complete **conversation history**
- 🔄 Conversations must **survive restarts**
- 👤 Managing **user sessions** with chat logs
- 📝 Sequential message access needed
- 🎫 Support ticket / case management

### Use Both Together when:
- Building production chatbots with full context
- Enterprise applications needing both history and search
- Complex agents with long-term memory and session management

---

## Workshop Exercises

### Exercise 1: User Profile Memory
**Task**: Build an agent that remembers user profile information (name, location, preferences) and uses it to personalize responses.

**Hints**:
- Use RedisProvider with `user_id` scope
- Store profile updates as conversation context
- Test retrieval across multiple sessions

### Exercise 2: Session Resume
**Task**: Build a multi-session customer support bot that can resume conversations from previous sessions.

**Hints**:
- Use RedisChatMessageStore with ticket ID as thread_id
- Test by stopping/restarting the application
- Add message limits to prevent unbounded growth

### Exercise 3: Multi-Agent System
**Task**: Build a system with 3 agents (Sales, Support, Engineering) that each maintain separate memory for the same user.

**Hints**:
- Use different `agent_id` for each agent
- Keep same `user_id` across all agents
- Verify memory isolation

---

## Troubleshooting

### Common Issues

**Problem**: `Connection refused` error
```
Solution: Ensure Redis is running
- Docker: docker ps | grep redis
- Check port: telnet localhost 6379
```

**Problem**: Agent doesn't remember context
```
Solution: Verify provider configuration
- Check scope parameters (user_id, agent_id, thread_id)
- Ensure index is created: await provider.redis_index.info()
- Verify messages are stored: await provider.search_all()
```

**Problem**: Messages not persisting
```
Solution: Check RedisChatMessageStore setup
- Verify thread_id is consistent
- Check Redis connection: await store.ping()
- List messages: await store.list_messages()
```

**Problem**: Out of memory errors
```
Solution: Set message limits
- Configure max_messages in RedisChatMessageStore
- Monitor Redis memory: redis-cli INFO memory
- Implement cleanup policies
```

---

## Additional Resources

### Package Installation
```bash
pip install agent-framework-redis
```

### Environment Variables
Required in `.env` file:
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"
```

### Documentation
- **Redis Package README**: `python/packages/redis/README.md`
- **Sample Files**: `python/samples/getting_started/context_providers/redis/`
- **RediSearch Docs**: https://redis.io/docs/stack/search/

### Sample Code

**Console Demos** (for automation/scripting):
- `redis_demo_preferences.py` - Smart preference memory
- `redis_demo_persistence.py` - Resume conversations
- `redis_demo_multi_agent.py` - Multi-agent isolation

**DevUI Demos** (for workshops/interactive learning):
- `redis_demo_preferences_devui.py` - Interactive preference learning (port 8000)
- `redis_demo_persistence_devui.py` - Interactive conversation persistence (port 8001)
- `redis_demo_multi_agent_devui.py` - Side-by-side agents (ports 8002 & 8003)

**Framework Examples** (advanced patterns):
- `redis_basics.py` - Basic provider usage with tools
- `redis_threads.py` - Thread scoping strategies
- `redis_chat_message_store_thread.py` - Complete persistence examples

### Reference Architecture
```
┌─────────────────────────────────────────┐
│         Your Application                │
├─────────────────────────────────────────┤
│  Agent(s) with:                         │
│  ├── RedisProvider (memory/context)     │
│  └── RedisChatMessageStore (history)    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   Redis Server   │
         ├─────────────────┤
         │ • RediSearch    │
         │ • Lists         │
         │ • Hashes        │
         └─────────────────┘
```

---

## Next Steps

After completing this workshop:

1. ✅ **Explore Advanced Features**: Vector embeddings, hybrid search
2. ✅ **Integrate with Production**: Azure/AWS managed Redis
3. ✅ **Monitor Performance**: Redis metrics, Application Insights
4. ✅ **Scale Horizontally**: Redis Cluster, connection pooling
5. ✅ **Build Real Applications**: Combine with your business logic

---

## Questions & Support

- **Framework Issues**: https://github.com/microsoft/agent-framework
- **Redis Questions**: https://redis.io/community
- **Workshop Feedback**: Contact your workshop facilitator

---

**Workshop Complete!** 🎉

You now know how to build production-ready agents with persistent memory and conversation storage using Redis.

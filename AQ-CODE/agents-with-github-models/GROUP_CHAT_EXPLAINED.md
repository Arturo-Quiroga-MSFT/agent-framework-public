# Group Chat Orchestration Pattern - Deep Dive

**For Example 09: Product Feature Review with Collaborative Discussion**

---

## 🎯 What Makes Group Chat Different?

Group Chat is a **conversational orchestration pattern** where agents build on each other's responses through iterative discussion, managed by an orchestrator that dynamically selects who speaks next.

### Pattern Comparison

| Pattern | Example | Agent Interaction | Context Sharing | Best For |
|---------|---------|------------------|-----------------|----------|
| **Sequential** | 07 | A→B→C→D (pipeline) | Each sees only previous | ETL, data transformation |
| **Parallel** | 08 | All simultaneously | None (independent) | Speed, independent analyses |
| **Group Chat** | 09 | **Conversation** | **Full history to all** | **Team collaboration** |

---

## 🔄 How It Works: Conversation Flow

### The Orchestration Loop

```
User Query → [Orchestrator selects Speaker 1]
                ↓
              Speaker 1 responds (sees: query)
                ↓
              [Orchestrator selects Speaker 2]
                ↓
              Speaker 2 responds (sees: query + Speaker 1)
                ↓
              [Orchestrator selects Speaker 3]
                ↓
              Speaker 3 responds (sees: query + Speaker 1 + Speaker 2)
                ↓
              ... continues until orchestrator returns None
```

### Example 09 Conversation Flow

**Scenario:** "Blockchain carbon credit marketplace"

**Round 1 - Initial Perspectives:**
1. **Product Manager** (PM): Proposes feature vision
   - Sees: User query only
   - Outputs: Value prop, target users, features

2. **Technical Architect** (TA): Evaluates feasibility
   - Sees: Query + PM's proposal
   - Outputs: Technical challenges, timeline, risks

3. **UX Designer** (UX): Assesses user experience
   - Sees: Query + PM + TA
   - Outputs: Usability concerns, accessibility, design patterns

4. **Business Analyst** (BA): Reviews market viability
   - Sees: Query + PM + TA + UX
   - Outputs: Market analysis, competition, recommendation

**Round 2 - Refinement & Synthesis:**
5. **Product Manager**: Addresses concerns raised
   - Sees: ALL of Round 1 (4 messages)
   - Refines proposal based on technical/UX/business feedback

6. **Technical Architect**: Proposes solutions
   - Sees: ALL of Round 1 + PM's refinement (5 messages)
   - Addresses specific concerns with technical approaches

7. **UX Designer**: Refines design
   - Sees: ALL previous discussion (6 messages)
   - Incorporates technical and business constraints

8. **Business Analyst**: Final recommendation
   - Sees: COMPLETE conversation (7 messages)
   - Synthesizes all input, provides go/no-go decision

---

## 📊 Token Usage Analysis (From Real Traces)

### What the Traces Revealed

By examining OpenTelemetry traces from actual runs, we can see exactly how token usage grows:

#### Turn 6 (Technical Architect, Round 2)
```json
{
  "gen_ai.usage.input_tokens": 2503,
  "gen_ai.usage.output_tokens": 357,
  "gen_ai.client.operation.duration": 5.35
}
```
**Context**: Sees 5 previous agent responses + original query

#### Turn 8 (Business Analyst, Round 2 - Final)
```json
{
  "gen_ai.usage.input_tokens": 3861,
  "gen_ai.usage.output_tokens": 408,
  "gen_ai.client.operation.duration": 5.28
}
```
**Context**: Sees COMPLETE conversation (7 previous responses + query)

### Token Progression Through Conversation

| Turn | Agent | Round | Input Tokens | Output Tokens | Context Seen |
|------|-------|-------|--------------|---------------|--------------|
| 1 | PM | 1 | ~100 | ~350 | Query only |
| 2 | TA | 1 | ~500 | ~350 | Query + PM |
| 3 | UX | 1 | ~900 | ~350 | Query + PM + TA |
| 4 | BA | 1 | ~1,300 | ~400 | Query + PM + TA + UX |
| 5 | PM | 2 | ~1,700 | ~350 | All Round 1 |
| 6 | TA | 2 | **2,503** | **357** | All Round 1 + PM Round 2 |
| 7 | UX | 2 | ~3,200 | ~350 | All previous (6 messages) |
| 8 | BA | 2 | **3,861** | **408** | **Complete conversation** |

**Total Tokens**: ~15,000-20,000 tokens per complete group chat

### Visual Token Growth

```
Input Tokens per Turn:

Turn 1:  █ (100)
Turn 2:  ██ (500)
Turn 3:  ████ (900)
Turn 4:  ██████ (1,300)
Turn 5:  ████████ (1,700)
Turn 6:  ████████████ (2,503)
Turn 7:  ███████████████ (3,200)
Turn 8:  ██████████████████ (3,861)
```

---

## 💰 Cost & Performance Implications

### Token Costs

**Group Chat (Example 09):**
- **Total tokens**: ~20,000 per conversation (8 turns)
- **Duration**: ~2 minutes (sequential LLM calls with growing context)
- **Cost**: Higher due to cumulative context
- **Value**: Rich, context-aware collaboration

**Parallel (Example 08):**
- **Total tokens**: ~4,000 per run (4 agents)
- **Duration**: ~15-20 seconds (simultaneous)
- **Cost**: Lower (each agent sees only query)
- **Value**: Fast, independent perspectives

**Sequential (Example 07):**
- **Total tokens**: ~3,000 per run (3 agents)
- **Duration**: ~60 seconds (one at a time)
- **Cost**: Lower (minimal context passing)
- **Value**: Pipeline processing

### Cost Comparison (GPT-4o-mini pricing)

Assuming GitHub Models pricing similar to Azure OpenAI:
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Example 09 (Group Chat):**
- Input: 15,000 tokens × $0.15 / 1M = **$0.00225**
- Output: 3,000 tokens × $0.60 / 1M = **$0.00180**
- **Total per run: ~$0.004** (less than half a cent)

**Example 08 (Parallel):**
- **Total per run: ~$0.001** (4x cheaper)

**Trade-off**: Group Chat costs more but provides richer collaboration

---

## 🔍 Real Trace Analysis: How Agents See Context

### Actual Trace from UX Designer (Turn 7, Round 2)

Here's what the OpenTelemetry trace reveals about how agents receive and process context:

#### Agent Metadata
```json
{
  "gen_ai.operation.name": "invoke_agent",
  "gen_ai.agent.id": "254cb31d-2c64-4de2-a53e-2e95dcf7e389",
  "gen_ai.agent.name": "UXDesigner",
  "gen_ai.agent.description": "User experience expert who champions intuitive and accessible design",
  "gen_ai.request.model": "gpt-4.1",
  "gen_ai.provider.name": "microsoft.agent_framework"
}
```

Notice: MAF tracks the agent's identity throughout the workflow, not just raw LLM calls.

#### System Instructions (Agent Role)
```json
{
  "gen_ai.system_instructions": [
    {
      "type": "text",
      "content": "You are a UX designer evaluating user experience implications.\n\nYour role:\n- Assess usability and accessibility considerations\n- Identify potential user friction points\n- Suggest interaction patterns and design principles\n- Consider inclusive design for diverse users\n- Balance functionality with simplicity\n- IN SECOND ROUND: Refine design based on technical and business feedback\n\nKeep your analysis to 3-4 key points. Focus on the user journey and experience."
    }
  ]
}
```

**Key Insight**: The agent's role and instructions are set via **system message**, not embedded in conversation history.

#### Full Conversation Context (6 Previous Messages)

The UX Designer (Turn 7) receives:

1. **User Query**: "Blockchain carbon credit marketplace"
2. **PM Round 1**: Value proposition, target users, features
3. **TA Round 1**: Technical feasibility, challenges, timeline
4. **UX Round 1**: Initial UX evaluation (their own previous response)
5. **BA Round 1**: Market analysis, recommendation
6. **PM Round 2**: Refined proposal addressing concerns
7. **TA Round 2**: Technical solutions and approaches

```json
{
  "gen_ai.input.messages": [
    {
      "role": "system",
      "parts": [{"type": "text", "content": "You are a UX designer..."}]
    },
    {
      "role": "user",
      "parts": [{"type": "text", "content": "• Blockchain carbon credit marketplace"}]
    },
    {
      "role": "assistant",
      "parts": [{"type": "text", "content": "**User value proposition:**..."}]
    },
    {
      "role": "assistant",
      "parts": [{"type": "text", "content": "**Technical Feasibility Assessment...**"}]
    },
    {
      "role": "assistant",
      "parts": [{"type": "text", "content": "**UX evaluation – Blockchain...**"}]
    },
    {
      "role": "assistant",
      "parts": [{"type": "text", "content": "**Blockchain Carbon Credit Marketplace: First-Round Assessment**..."}]
    },
    {
      "role": "assistant",
      "parts": [{"type": "text", "content": "**User Value Proposition:**..."}]
    },
    {
      "role": "assistant",
      "parts": [{"type": "text", "content": "**Feature Feasibility—Blockchain...**"}]
    }
  ]
}
```

### Evidence of True Collaboration

Compare what other agents said to what UX Designer references in Round 2:

**TA Round 1 mentioned:**
> "Blockchain Choice & Smart Contracts: Selection of blockchain (e.g., Ethereum, Polygon...) impacts scalability, transaction fees, and user onboarding"

**UX Round 2 references this:**
> "Blockchain's complexity can intimidate non-expert users, especially when dealing with high-value assets"

---

**BA Round 1 mentioned:**
> "Partnerships with trusted verification bodies (e.g., Gold Standard, Verra)"

**UX Round 2 references this:**
> "Show partner verification logos and transparent documentation to quickly establish trust"

---

**TA Round 1 mentioned:**
> "Handling KYC/AML for users (especially corporates) requires integrating or building robust identity verification"

**UX Round 2 integrates this:**
> "Provide easy sign-up (email/social logins, clear KYC steps)"

### The Magic of Context Accumulation

**This is NOT coincidence** - The UX Designer agent:
1. ✅ **Read** the complete conversation (6 previous messages)
2. ✅ **Identified** specific concerns from TA and BA
3. ✅ **Integrated** those concerns into UX recommendations
4. ✅ **Built upon** previous suggestions rather than repeating them

**This is true AI agent collaboration** - not predetermined responses, but context-aware synthesis.

### Why This Matters

In **Parallel** pattern (Example 08):
- Each agent sees: **User query only**
- Result: 4 independent analyses
- No cross-referencing possible

In **Group Chat** pattern (Example 09):
- Each agent sees: **Complete discussion history**
- Result: Integrated, collaborative synthesis
- Agents respond to each other's insights

The token cost is higher, but the **quality of collaboration** is fundamentally different.

---

## 🧠 How the Orchestrator Works

### Speaker Selection Function

```python
def select_next_speaker(state: GroupChatStateSnapshot) -> str | None:
    """Intelligent speaker selector for multi-round discussions.
    
    Args:
        state: Contains:
            - round_index: Current turn number (0-based)
            - history: Complete conversation history
            - participants: Dict of agent names
            - task: Original user query
    
    Returns:
        Next speaker name or None to finish
    """
    round_idx = state["round_index"]
    speakers = ["ProductManager", "TechnicalArchitect", "UXDesigner", "BusinessAnalyst"]
    
    # Stop after 8 rounds (2 full cycles)
    if round_idx >= 8:
        return None
    
    # Get last speaker from history
    last_speaker = get_last_speaker(history)
    
    # Round-robin through speakers
    if last_speaker in speakers:
        current_idx = speakers.index(last_speaker)
        next_idx = current_idx + 1
        if next_idx < len(speakers):
            return speakers[next_idx]
        else:
            return speakers[0]  # Start new round
    
    return speakers[0]  # First speaker
```

### Orchestrator Decision Points

```
Turn 1: No history → Select PM (start)
Turn 2: Last=PM → Select TA (next in rotation)
Turn 3: Last=TA → Select UX (next in rotation)
Turn 4: Last=UX → Select BA (next in rotation)
Turn 5: Last=BA, round_idx=4 → Select PM (new round)
Turn 6: Last=PM → Select TA (continue round 2)
Turn 7: Last=TA → Select UX (continue round 2)
Turn 8: Last=UX → Select BA (finish round 2)
Turn 9: round_idx=8 → Return None (END)
```

---

## 📈 Advanced: LLM-Based Orchestrator

The current example uses a **function-based orchestrator** (predictable, deterministic). MAF also supports **LLM-based orchestrators** where an AI agent decides who speaks next:

```python
# Alternative: LLM Manager
manager_agent = ChatAgent(
    name="ConversationManager",
    instructions="""You manage product feature discussions.
    
    After each speaker, decide who should speak next based on:
    - What concerns need addressing
    - Which perspective is missing
    - Whether we need more refinement
    
    Return speaker name or 'DONE' to finish.""",
    chat_client=client
)

workflow = (
    GroupChatBuilder()
    .set_manager(manager_agent)  # LLM decides!
    .participants([pm, ta, ux, ba])
    .build()
)
```

**Trade-offs:**
- **Function-based** (Example 09): Predictable, fast, cheaper
- **LLM-based**: Dynamic, adaptive, but adds LLM calls for management

---

## 🎬 Demo Script for Your Partner

### Setup (2 minutes)
```bash
cd /path/to/agents-with-github-models
python 09_github_groupchat_workflow.py
# Opens http://localhost:8084
```

### Demo Flow (5 minutes)

**1. Show the Interface (30 seconds)**
- DevUI opens with "workflow" entity
- Show the 4 participant agents + orchestrator
- Explain: "This is a collaborative team discussion"

**2. Enter Feature Idea (30 seconds)**
- Input: "Blockchain carbon credit marketplace"
- Click submit

**3. Watch Round 1 - Initial Perspectives (90 seconds)**
- **PM speaks first**: Shows value proposition (15s)
  - *Point out*: "Only sees the query"
- **TA speaks second**: Technical feasibility (15s)
  - *Point out*: "Sees PM's proposal in their context"
- **UX speaks third**: User experience concerns (15s)
  - *Point out*: "Sees both PM and TA's input"
- **BA speaks fourth**: Market analysis (15s)
  - *Point out*: "Has complete Round 1 context"

**4. Watch Round 2 - Refinement (90 seconds)**
- **PM responds**: Addresses technical/UX concerns (15s)
  - *Point out*: "References specific points from TA and UX"
- **TA proposes solutions**: Technical approaches (15s)
- **UX refines design**: Incorporates feedback (15s)
- **BA provides final recommendation**: Synthesizes everything (15s)
  - *Point out*: "This has the COMPLETE conversation context"

**5. Show the Traces (60 seconds)**
- Click "Traces" tab in DevUI
- Show execution timeline
- Click on a late-stage trace (Turn 6 or 8)
- **Show token counts**: "See how context grows?"
  - Early: ~500 input tokens
  - Late: ~3,800 input tokens
- **Explain**: "Each agent builds on everyone else's ideas"

### Key Points to Emphasize

**What Makes This Special:**
1. **True Conversation**: Not predetermined pipeline, not independent analysis
2. **Context Accumulation**: Each agent sees and responds to previous discussion
3. **Iterative Refinement**: Two rounds allow addressing concerns
4. **Orchestrated Flow**: Manager controls who speaks when based on conversation state

**Real-World Analogies:**
- "Like a real product review meeting"
- "PM pitches → Engineers raise concerns → Designers add constraints → Business decides"
- "Second round lets everyone address feedback"

**Technical Insight:**
- "Notice the token counts grow? That's the conversation history"
- "Final agent (BA) sees the complete 7-message discussion"
- "Costs more than parallel, but produces richer output"

---

## 🆚 When to Use Each Pattern

### Sequential (Example 07)
**Use When:**
- Data pipeline or ETL flow
- Each step transforms output for next
- Order matters, dependencies clear
- Example: Parse → Validate → Transform → Load

**Characteristics:**
- Fixed order
- Minimal context sharing
- Predictable flow
- Lower token cost

### Parallel (Example 08)
**Use When:**
- Need multiple independent perspectives
- Speed is critical
- No need for agents to interact
- Example: Multi-perspective analysis, risk assessment from different angles

**Characteristics:**
- All execute simultaneously
- No inter-agent communication
- Fast execution (15-20s)
- Lowest token cost

### Group Chat (Example 09)
**Use When:**
- Collaborative decision-making needed
- Agents should respond to each other
- Iterative refinement valuable
- Example: Product reviews, code reviews, strategic planning

**Characteristics:**
- Conversational interaction
- Full context sharing
- Iterative refinement possible
- Higher token cost, richer output
- Slower (2+ minutes)

---

## 🔧 Configuration Options

### Adjusting Round Count

```python
def select_next_speaker(state: GroupChatStateSnapshot) -> str | None:
    round_idx = state["round_index"]
    
    # Change from 8 to 12 for 3 rounds
    if round_idx >= 12:
        return None
    
    # Or dynamic: stop when BA says "DONE"
    if round_idx >= 4:  # At least 1 full round
        last_message = state["history"][-1].content
        if "recommendation: go" in last_message.lower():
            return None  # Stop after first clear recommendation
```

### Adding More Agents

```python
# Add 5th agent for security perspective
security_agent = ChatAgent(
    name="SecurityExpert",
    instructions="Evaluate security and compliance risks...",
    chat_client=client
)

workflow = (
    GroupChatBuilder()
    .set_select_speakers_func(select_next_speaker, display_name="Orchestrator")
    .participants([
        product_manager,
        technical_architect,
        ux_designer,
        business_analyst,
        security_agent  # Added
    ])
    .build()
)

# Update speaker rotation
speakers = ["ProductManager", "TechnicalArchitect", "UXDesigner", "SecurityExpert", "BusinessAnalyst"]
```

### Custom Termination Logic

```python
def smart_terminator(state: GroupChatStateSnapshot) -> str | None:
    """Stop when consensus reached or max rounds."""
    round_idx = state["round_index"]
    history = state["history"]
    
    # Maximum 12 rounds
    if round_idx >= 12:
        return None
    
    # Check for consensus keywords in last few messages
    if round_idx >= 6:
        recent = " ".join([msg.content for msg in history[-3:]])
        if "consensus" in recent.lower() or "agreed" in recent.lower():
            return None  # Stop early if consensus reached
    
    # Otherwise continue rotation
    return next_speaker_in_rotation(state)
```

---

## 📚 Additional Resources

### Related Examples
- **Example 07**: Sequential workflow (pipeline pattern)
- **Example 08**: Parallel workflow (fan-out/fan-in pattern)
- **Example 05-06**: DevUI basics with simpler patterns

### Documentation
- [MAF Group Chat Guide](https://learn.microsoft.com/agent-framework/workflows/orchestrations/group-chat)
- [WorkflowBuilder API](https://learn.microsoft.com/agent-framework/workflows/overview)
- [DevUI Tracing Guide](./TRACING_GUIDE.md)

### Official Samples
- `python/samples/getting_started/workflows/orchestration/group_chat_simple_selector.py`
- `python/samples/getting_started/workflows/orchestration/group_chat_agent_manager.py`

---

## 🎓 Key Takeaways

1. **Group Chat enables true AI agent collaboration** through iterative conversation
2. **Context accumulation** is the key feature - each agent sees full discussion history
3. **Token costs grow linearly** with conversation length due to expanding context
4. **Orchestrator manages flow** - can be function-based (predictable) or LLM-based (adaptive)
5. **Two-round pattern** (8 turns) balances depth with cost for product reviews
6. **Perfect for scenarios** that mimic real team discussions with feedback loops

---

**Last Updated**: January 2, 2026  
**Example**: 09_github_groupchat_workflow.py  
**Framework**: Microsoft Agent Framework with GitHub Models

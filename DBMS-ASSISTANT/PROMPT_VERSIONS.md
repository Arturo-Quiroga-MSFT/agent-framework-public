# Prompt Engineering A/B Testing Guide

## Overview

This document describes three different prompt instruction versions for the DBA Assistant agent. Each version uses a different prompt engineering approach to optimize agent behavior with modern language models.

## Available Versions

### **VERSION 1: MINIMAL**
**Lines of Code:** ~25 lines  
**Philosophy:** Trust the model's intelligence with minimal constraints

**Approach:**
- Persona-driven identity ("senior DBA")
- 3 simple behavioral principles
- 3 concrete examples showing desired patterns
- No negative instructions or "don't do this" statements
- Clean, concise communication

**Best For:**
- **gpt-5.1-chat** - Advanced reasoning models that benefit from freedom
- **gpt-5-chat** - Models with strong contextual understanding
- Scenarios where you want the agent to reason independently

**Strengths:**
- Low cognitive load on model
- Encourages natural reasoning
- Avoids over-constraining behavior

---

### **VERSION 2: BALANCED**
**Lines of Code:** ~50 lines  
**Philosophy:** Core principles + selective examples + light constraints

**Approach:**
- 4 numbered core principles
- Clear "What to Avoid" section (3 specific behaviors)
- Tool awareness and capabilities overview
- Positive and negative behavior examples
- Completion pattern guidance

**Best For:**
- **gpt-4.1** - Strong general-purpose models
- **gpt-4.1-mini** - Efficient models that benefit from structure
- Production environments where consistency matters

**Strengths:**
- Good balance of guidance and freedom
- Provides safety rails without over-specifying
- Clear behavioral expectations

---

### **VERSION 3: STRUCTURED**
**Lines of Code:** ~70 lines  
**Philosophy:** Clear decision framework with visual organization

**Approach:**
- Emoji-based sections for visual scanability (🎯 Mission, ⚙️ Decision Framework, etc.)
- Explicit decision tree for when to execute vs. ask
- Comprehensive tool catalog
- Response pattern template
- Multiple concrete examples

**Best For:**
- **gpt-4.1-mini** - Models that benefit from explicit structure
- Complex multi-step workflows
- Teams that prefer predictable agent behavior

**Strengths:**
- Very clear decision logic
- Easy to scan and understand
- Comprehensive coverage of scenarios

---

## How to Switch Versions

In `dba_assistant.py`, modify the agent instructions to use your preferred prompt style:

```python
# Use one of the instruction sets from above
instructions = MINIMAL_INSTRUCTIONS  # or BALANCED_INSTRUCTIONS or STRUCTURED_INSTRUCTIONS
```

Then restart the assistant:
```bash
python dba_assistant.py
```

---

## Testing Protocol

### **Standard Test Queries:**
1. "What are the relationships between tables?"
2. "Create ER diagram"
3. "Make it vertical"
4. "Export as PDF"
5. "Show tables with most rows"
6. "Analyze index fragmentation"

### **What to Measure:**
- ✅ **Task Completion** - Does it finish without asking follow-up questions?
- ✅ **Accuracy** - Does it use the correct MCP tools?
- ✅ **Efficiency** - Single response or multiple back-and-forth exchanges?
- ✅ **Professional Tone** - Confident and action-oriented?
- ❌ **Over-asking** - Does it ask "Do you want me to..." unnecessarily?
- ❌ **Circular Behavior** - Does it re-ask about already confirmed items?

### **Scoring Rubric (1-10):**
- **10** - Perfect execution, no questions, completes task immediately
- **7-9** - Good execution, maybe 1 unnecessary question
- **4-6** - Mixed results, some circular behavior or hesitation
- **1-3** - Poor execution, multiple unnecessary questions, doesn't complete tasks

---

## Recommended Starting Points

| Model Family | Specific Models | Recommended Version | Rationale |
|--------------|----------------|-------------------|-----------|
| **GPT-5.1 Series** | gpt-5.1, gpt-5.1-chat, gpt-5.1-codex, gpt-5.1-codex-mini | MINIMAL | Most advanced reasoning, benefits from freedom. gpt-5.1-chat has built-in reasoning. |
| **GPT-5 Series** | gpt-5, gpt-5-mini, gpt-5-nano, gpt-5-chat, gpt-5-pro | MINIMAL or BALANCED | Strong reasoning capabilities, can handle either approach |
| **GPT-4.1 Series** | gpt-4.1, gpt-4.1-mini, gpt-4.1-nano | BALANCED | Excellent general-purpose with 1M context, benefits from clear structure |
| **O-Series (Reasoning)** | o4-mini, o3, o3-mini, o1, o1-mini | STRUCTURED | Reasoning models benefit from explicit decision frameworks |
| **GPT-OSS** | gpt-oss-120b, gpt-oss-20b | BALANCED | Open-weight reasoning models, good with balanced guidance |

### Notes on Model Selection:
- **For Agent/Tool Use**: GPT-5.1 series, GPT-4.1 series (all support function calling and tools)
- **For Reasoning Tasks**: O-series models, GPT-5 series with reasoning capabilities
- **For Cost Efficiency**: gpt-4.1-mini, gpt-5-mini, o4-mini
- **For Large Context**: GPT-4.1 series (1M tokens), GPT-5 series (400K tokens)

---

## Prompt Engineering Principles Applied

### **MINIMAL Version Principles:**
1. **Principle of Least Instructions** - Advanced models need less specification
2. **Persona > Prescription** - Identity drives behavior better than rules
3. **Few-Shot Learning** - Examples teach patterns better than rules
4. **Positive Framing** - "Execute immediately" vs "Don't ask for confirmation"

### **BALANCED Version Principles:**
1. **Core Principles** - 4-5 key guidelines, not 10+ rules
2. **Contextual Grounding** - Tool awareness provides behavioral hints
3. **Selective Examples** - 3-4 examples covering common patterns
4. **Light Constraints** - Minimal "avoid" list for critical issues

### **STRUCTURED Version Principles:**
1. **Visual Hierarchy** - Emoji sections improve scanability
2. **Decision Framework** - Clear logic tree for agent reasoning
3. **Response Templates** - Pattern to follow for consistency
4. **Comprehensive Coverage** - Addresses edge cases explicitly

---

## Known Issues Addressed

All three versions specifically address these behavioral problems discovered during testing:

1. ❌ **Over-Asking** - Agent asking "Do you want me to proceed?" after user already confirmed
2. ❌ **Unsolicited Suggestions** - Agent asking "Do you want me to also do X?" after completing tasks
3. ❌ **Circular Planning** - Agent creating plans to execute previous plans
4. ❌ **Context Loss** - Agent forgetting previous queries and re-fetching data
5. ❌ **Incomplete Execution** - Agent not completing format changes (e.g., "make it vertical")

---

## Evolution History

### **Phase 1: Original Complex Instructions (~100 lines)**
- Over-specified with 10+ rules
- Multiple FORBIDDEN lists
- Repetitive examples
- **Result:** Model confused, tried too hard to follow rules

### **Phase 2: Three Testing Versions (Current)**
- MINIMAL: Trust advanced model intelligence
- BALANCED: Core principles with examples
- STRUCTURED: Clear decision framework
- **Result:** Testing in progress with gpt-5.1-chat

---

## Future Improvements

Based on testing results, we may:
- Combine best aspects of multiple versions
- Create model-specific variants
- Add dynamic instruction selection based on query complexity
- Implement hybrid approach (simple queries = minimal, complex = structured)

---

## Contributing Your Results

If you test these versions, please document:
- Model used (e.g., gpt-5.1-chat)
- Version tested (MINIMAL, BALANCED, STRUCTURED)
- Score (1-10) for each test query
- Notable behaviors (good or problematic)
- Overall recommendation

This helps us optimize the prompts for different models and use cases.

---

## References

- OpenAI Prompt Engineering Guide: https://platform.openai.com/docs/guides/prompt-engineering
- Anthropic Prompting Best Practices: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering
- Microsoft Azure OpenAI Best Practices: https://learn.microsoft.com/azure/ai-services/openai/concepts/prompt-engineering

---

**Last Updated:** November 29, 2025  
**Maintained By:** RDBMS Assistant Team

---

## Azure AI Foundry Model Reference

This DBA Assistant is designed to work with models available in **Azure AI Foundry** and **Microsoft Agent Framework (MAF)**.

### Available Model Families:

#### **GPT-5.1 Series (Latest - November 2025)**
- **gpt-5.1** - Reasoning, Chat/Responses API, 400K context, structured outputs, multimodal
- **gpt-5.1-chat** - Built-in reasoning, 128K context, optimized for agents
- **gpt-5.1-codex** - Optimized for code, 400K context
- **gpt-5.1-codex-mini** - Efficient code model

**Regions**: East US2, Sweden Central (Global Standard)  
**Access**: Registration required for gpt-5.1 and gpt-5.1-codex

#### **GPT-5 Series**
- **gpt-5** - Reasoning, 400K context, multimodal
- **gpt-5-mini** - Efficient reasoning model
- **gpt-5-nano** - Ultra-efficient model
- **gpt-5-chat** - Chat-optimized (128K context)
- **gpt-5-pro** - Premium reasoning model

**Note**: gpt-5-mini, gpt-5-nano, and gpt-5-chat do NOT require registration

#### **GPT-4.1 Series**
- **gpt-4.1** - 1M token context, multimodal, excellent for agents
- **gpt-4.1-mini** - Efficient with 1M context
- **gpt-4.1-nano** - Ultra-efficient with 1M context

**Best For**: Large codebase analysis, comprehensive documentation queries

#### **O-Series (Reasoning Models)**
- **o4-mini** - Latest reasoning model with enhanced capabilities
- **o3**, **o3-mini**, **o3-pro** - Advanced reasoning
- **o1**, **o1-mini** - Previous generation reasoning
- **codex-mini** - Fine-tuned o4-mini for code

**Best For**: Complex problem-solving, mathematical reasoning, deep analysis

#### **GPT-OSS (Open-Weight Reasoning)**
- **gpt-oss-120b** - 131K context, deployable
- **gpt-oss-20b** - Managed compute and Foundry Local

**Best For**: Open-source requirements, on-premises deployment

### Model Capabilities Summary:

| Capability | GPT-5.1 | GPT-5 | GPT-4.1 | O-Series | GPT-OSS |
|------------|---------|-------|---------|----------|---------|
| **Reasoning** | ✅ Built-in | ✅ | ❌ | ✅ | ✅ |
| **Function Calling** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Streaming** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Structured Outputs** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Multimodal** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Max Context** | 400K | 400K | 1M | 200K | 131K |

### For This DBA Assistant:

**Recommended Models:**
1. **gpt-5.1-chat** - Best overall (built-in reasoning + agent optimization)
2. **gpt-4.1-mini** - Best cost/performance for large queries
3. **gpt-5-mini** - Good balance of reasoning and efficiency
4. **o4-mini** - When deep reasoning is needed for complex optimization problems

**Not Recommended:**
- O-series for simple queries (overkill, slower, no streaming in some cases)
- Legacy models (GPT-4o, GPT-3.5) - use newer 4.1/5.x series instead

**Reference**: [Azure AI Foundry Models Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/models-sold-directly-by-azure)

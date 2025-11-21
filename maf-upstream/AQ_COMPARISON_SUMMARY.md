# Code Comparison: Old vs New MAF Python Samples

**Comparison Date:** November 21, 2025
**Old Code:** `/python/samples/getting_started/agents/`
**New Code:** `/maf-upstream/python/samples/getting_started/agents/`

---

## 1. Azure AI Directory (`azure_ai/`)

### Summary
- **Old:** 15 files
- **New:** 22 files
- **Net Change:** +7 files (12 new additions, 5 removals)

### ✅ NEW Files (in upstream, not in old code)
1. `azure_ai_use_latest_version.py` - Use latest agent version
2. `azure_ai_with_agent_to_agent.py` - Agent-to-agent communication
3. `azure_ai_with_bing_custom_search.py` - Bing Custom Search integration
4. `azure_ai_with_browser_automation.py` - Browser automation capabilities
5. `azure_ai_with_existing_conversation.py` - Resume existing conversations
6. `azure_ai_with_image_generation.py` - Image generation support
7. `azure_ai_with_microsoft_fabric.py` - Microsoft Fabric integration
8. `azure_ai_with_response_format.py` - Structured response formats
9. `azure_ai_with_search_context_agentic.py` - Agentic search context
10. `azure_ai_with_search_context_semantic.py` - Semantic search context
11. `azure_ai_with_sharepoint.py` - SharePoint integration
12. `azure_ai_with_web_search.py` - Web search capabilities

### ❌ REMOVED Files (in old code, not in upstream)
1. `azure_ai_with_existing_thread.py` - Replaced by `azure_ai_with_existing_conversation.py`
2. `azure_ai_with_function_tools.py` - Possibly consolidated
3. `azure_ai_with_local_mcp.py` - MCP support restructured
4. `azure_ai_with_multiple_tools.py` - Possibly consolidated
5. `azure_ai_with_openapi_tools.py` - Possibly consolidated

### 📝 Files Present in Both (potentially updated)
- `README.md`
- `azure_ai_basic.py`
- `azure_ai_with_azure_ai_search.py`
- `azure_ai_with_bing_grounding.py`
- `azure_ai_with_code_interpreter.py`
- `azure_ai_with_existing_agent.py`
- `azure_ai_with_explicit_settings.py`
- `azure_ai_with_file_search.py`
- `azure_ai_with_hosted_mcp.py`
- `azure_ai_with_thread.py`

---

## 2. Azure AI Agent Directory (`azure_ai_agent/`)

### Summary
- **Old:** Directory does NOT exist
- **New:** 16 files (COMPLETELY NEW)

### ✅ NEW Directory with Files
This is an entirely new directory in the upstream code with 16 sample files:
1. `README.md`
2. `azure_ai_basic.py`
3. `azure_ai_with_azure_ai_search.py`
4. `azure_ai_with_bing_custom_search.py`
5. `azure_ai_with_bing_grounding.py`
6. `azure_ai_with_code_interpreter.py`
7. `azure_ai_with_existing_agent.py`
8. `azure_ai_with_existing_thread.py`
9. `azure_ai_with_explicit_settings.py`
10. `azure_ai_with_file_search.py`
11. `azure_ai_with_function_tools.py`
12. `azure_ai_with_hosted_mcp.py`
13. `azure_ai_with_local_mcp.py`
14. `azure_ai_with_multiple_tools.py`
15. `azure_ai_with_openapi_tools.py`
16. `azure_ai_with_thread.py`

**Note:** This appears to be a dedicated directory for Azure AI Agent Service samples, separate from the general Azure AI samples.

---

## 3. Azure OpenAI Directory (`azure_openai/`)

### Summary
- **Old:** 17 files
- **New:** 19 files
- **Net Change:** +1 file (1 new addition)

### ✅ NEW Files
1. `azure_responses_client_with_hosted_mcp.py` - Hosted MCP support for Responses client

### 📝 Files Present in Both
All 17 files from the old code are present in the new code:
- `README.md`
- Azure Assistants samples (6 files)
- Azure Chat Client samples (4 files)
- Azure Responses Client samples (7 files)

---

## Key Insights

### Major Changes
1. **New `azure_ai_agent/` directory** - Indicates a new Azure AI Agent Service API or pattern
2. **Enhanced capabilities in `azure_ai/`**:
   - Browser automation
   - Image generation
   - SharePoint integration
   - Microsoft Fabric integration
   - Multiple search context patterns (agentic & semantic)
   - Agent-to-agent communication

### Migration Considerations
1. Some tool-related samples were removed from `azure_ai/` but appear in the new `azure_ai_agent/` directory
2. Thread handling may have been renamed/refactored (`existing_thread` → `existing_conversation`)
3. MCP support appears to be restructured between local and hosted variants

### Recommended Next Steps
1. Compare individual file contents for files that exist in both locations
2. Understand the purpose of the new `azure_ai_agent/` directory
3. Identify breaking changes in common samples like `azure_ai_basic.py`
4. Review new features: browser automation, image generation, Fabric integration

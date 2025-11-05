# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. "RuntimeError: Event loop is closed" when reinitializing agent

**Symptom:**
```
RuntimeError: Event loop is closed
```

**Cause:** 
Persisting agent/client objects across multiple `asyncio.run()` calls causes event loop conflicts.

**Solution:** ✅ **FIXED** (as of latest version)
Now uses the proven pattern from the working demo:
- **Agent created fresh inside each `run()`** within async context managers
- **Only thread ID (string) is persisted** between queries for conversation continuity
- Thread object is recreated in each run using the stored ID
- No persistent client/agent/credential objects

**How it works:**
```python
async with DefaultAzureCredential() as credential:
    async with AzureAIAgentClient(async_credential=credential) as client:
        agent = ChatAgent(...)
        
        # Use stored thread ID
        if self._thread_id:
            thread = agent.get_new_thread(service_thread_id=self._thread_id)
        else:
            thread = agent.get_new_thread()
        
        result = await agent.run(query, thread=thread, store=True)
        
        # Store ID for next query
        self._thread_id = thread.service_thread_id
```

**Result:** Each query gets a fresh agent context, conversation history is maintained via thread ID.

---

### 2. Agent won't initialize / Azure authentication errors

**Symptom:**
```
DefaultAzureCredentialError: 'DefaultAzureCredential' failed to retrieve a token
```

**Solutions:**

**Option A: Azure CLI Login (Recommended for local dev)**
```bash
az login
az account show  # Verify you're logged in
```

**Option B: Environment Variables**
```bash
# In .env file
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

**Option C: Check Azure AI endpoint**
```bash
# Verify .env has correct endpoint
AZURE_AI_PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1
```

---

### 3. Budget warnings appearing immediately

**Symptom:**
- Budget shows 80-100% used immediately
- "Budget exceeded" errors

**Cause:**
Budget limit is set too low or budget wasn't reset between sessions.

**Solution:**

**Option A: Increase budget**
```bash
# In .env file
TOKEN_BUDGET_LIMIT=2000000  # 2M tokens (default is 1M)
```

**Option B: Clear session**
1. Click "🗑️ Clear Chat History" in sidebar
2. This resets the token counter

**Option C: Restart application**
```bash
# Stop with Ctrl+C, then restart
streamlit run streamlit_production_ui.py
```

---

### 4. UI becomes unresponsive during agent execution

**Symptom:**
- Spinner keeps spinning
- No response appears
- Page seems frozen

**Possible Causes & Solutions:**

**A. Network/API timeout**
- Check Azure AI endpoint is accessible
- Verify internet connection
- Try a simpler query first

**B. Large web search results**
- Web search can be slow with complex queries
- Try disabling web search (use Technical Advisor preset)

**C. Browser tab backgrounded**
- Some browsers pause background tabs
- Bring tab to foreground

**D. Streamlit server issue**
- Restart the server: Ctrl+C then restart

---

### 5. Charts not displaying / UI looks broken

**Symptom:**
- Analytics tab shows empty charts
- Layout issues
- Missing visualizations

**Solutions:**

**A. Check dependencies**
```bash
pip install -r requirements-ui.txt --upgrade
```

**B. Clear browser cache**
- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

**C. Check browser compatibility**
- Use Chrome, Firefox, or Edge
- Ensure JavaScript is enabled

**D. Submit a query first**
- Some charts only appear after first query
- Try asking a question in the Chat tab

---

### 6. "ModuleNotFoundError" errors

**Symptom:**
```
ModuleNotFoundError: No module named 'production_agent_enhanced'
```

**Solution:**
```bash
# Must be in the correct directory
cd AQ-CODE/llmops

# Verify files exist
ls -la production_agent_enhanced.py
ls -la streamlit_production_ui.py

# Run from this directory
streamlit run streamlit_production_ui.py
```

---

### 7. Progress updates not showing in UI

**Symptom:**
- Status indicators don't appear
- Progress log is empty
- No real-time feedback

**Cause:**
Progress updates are stored but may not be visible in current tab.

**Solution:**
1. Check the **History** tab for progress log
2. Progress updates appear at bottom of History tab
3. They're stored in session state: `st.session_state.progress_updates`

---

### 8. Session export button doesn't work

**Symptom:**
- Click "📥 Export Session" does nothing
- No download prompt

**Solutions:**

**A. Initialize agent first**
- Export requires an active agent
- Click "🔄 Initialize/Switch Agent" first

**B. Browser popup blocker**
- Check if download was blocked
- Allow popups for localhost:8501

**C. Alternative: Manual export**
```python
# In Python console
import json
session_data = st.session_state.agent.export_session_data()
with open("session_export.json", "w") as f:
    json.dump(session_data, f, indent=2)
```

---

### 9. Quality evaluation shows poor scores unexpectedly

**Symptom:**
- Good responses score low (< 0.6)
- Topic coverage is 0% despite relevant answer

**Cause:**
Evaluation is based on expected topics provided to the agent.

**Solution:**

**A. Expected topics might be too specific**
- The preset's expected topics might not match your query
- This is informational, not a failure

**B. Check actual response quality**
- Read the response yourself
- Evaluation is heuristic-based, not perfect
- Look at specific metrics:
  - Has citations
  - Has numbers
  - Well structured

**C. Customize evaluation**
- Edit `evaluator.py` to adjust scoring
- Add custom quality checks

---

### 10. Agent gives wrong/outdated information

**Symptom:**
- Information seems incorrect
- Dates are wrong
- Data doesn't match reality

**Causes & Solutions:**

**A. Web search not enabled**
- Use Market Analyst or Research Assistant presets
- These have web search enabled for current info

**B. Model knowledge cutoff**
- Base model has knowledge cutoff date
- Always use web search for current info

**C. Web search results quality**
- Search results may vary
- Try rephrasing query
- Ask for specific sources

---

### 11. Cost tracking seems inaccurate

**Symptom:**
- Costs don't match Azure billing
- Token counts seem off

**Explanation:**
- Costs are **estimates** based on word count heuristics
- Formula: `words * 1.5 ≈ tokens`
- Actual tokens may vary ±20%
- Use for **relative** comparison, not billing

**For accurate costs:**
- Check Azure portal billing
- Enable detailed logging
- Use Azure Monitor for precise tracking

---

### 12. Can't switch between agent presets

**Symptom:**
- Selecting different preset doesn't change behavior
- Agent seems to use old instructions

**Solution:**
1. Select new preset from dropdown
2. **Must click "🔄 Initialize/Switch Agent" button**
3. Wait for "✅ [Preset] ready!" message
4. Check sidebar shows correct active agent

---

### 13. Memory/Performance issues

**Symptom:**
- Application slows down over time
- Browser memory usage increases
- Lag when typing

**Solutions:**

**A. Clear chat history regularly**
- Click "🗑️ Clear Chat History"
- Reduces session state size

**B. Restart Streamlit**
```bash
Ctrl+C
streamlit run streamlit_production_ui.py
```

**C. Reduce chart history**
- Currently stores all responses
- Future: Add limit to response history

---

## Debug Mode

### Enable detailed logging

**In production_agent_enhanced.py:**
```python
# Add at top of file
import logging
logging.basicConfig(level=logging.DEBUG)
```

**In Streamlit:**
```bash
streamlit run streamlit_production_ui.py --logger.level=debug
```

### Check session state

**Add to UI for debugging:**
```python
# In sidebar
with st.expander("🐛 Debug Info"):
    st.write("Session State Keys:", list(st.session_state.keys()))
    st.write("Agent Initialized:", st.session_state.agent_initialized)
    st.write("Messages:", len(st.session_state.chat_history))
    st.write("Responses:", len(st.session_state.responses))
```

---

## Still Having Issues?

### Quick Checklist

- [ ] Restart Streamlit server
- [ ] Clear browser cache (Ctrl+Shift+R)
- [ ] Run `az login` and verify authentication
- [ ] Check `.env` file has correct values
- [ ] Verify in correct directory: `AQ-CODE/llmops`
- [ ] Update dependencies: `pip install -r requirements-ui.txt --upgrade`
- [ ] Try with different agent preset
- [ ] Check Azure portal for service health

### Get Help

1. Check `UI_README.md` for detailed documentation
2. Review `ARCHITECTURE.md` for system design
3. Read code comments in `production_agent_enhanced.py`
4. Check Azure AI Foundry service status

---

## Known Limitations

1. **No streaming responses** - Complete response only
2. **Memory-based history** - Not persisted between restarts
3. **Estimated costs** - Not exact billing amounts
4. **Single session** - No multi-user support
5. **Client-side only** - No server-side session management

---

## Best Practices

✅ **DO:**
- Clear history after long conversations
- Export sessions before closing
- Use web search for current information
- Monitor budget usage
- Restart periodically for best performance

❌ **DON'T:**
- Run multiple Streamlit instances on same port
- Modify session state directly (use UI controls)
- Expect exact cost matching Azure billing
- Keep browser tab open for days
- Use for production multi-user scenarios (without modifications)

---

**Last Updated:** November 3, 2025
**Version:** 1.0 (Initial Release)

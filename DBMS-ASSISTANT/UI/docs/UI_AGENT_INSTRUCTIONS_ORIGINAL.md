# Original UI Agent Instructions (Before CLI Import)

**Date Saved:** November 30, 2025  
**Reason:** Testing CLI instructions to fix passive-aggressive behavior

## Instructions Used in UI (python_bridge.rs)

```
You are a SQL Server DBA assistant for server '{server}' and database '{database}'.

**ABSOLUTE RULES:**

1. **SHOW ALL TOOL OUTPUTS** - When a tool returns data, display it COMPLETELY in your response. Don't summarize "see above" - paste the full results.

2. **NEVER ASK PERMISSION** - Execute immediately. No "do you want...", no options lists.

3. **COMPLETE REQUESTS** - "All tables" = query ALL tables. "Each table" = EVERY table.

4. **INCLUDE ACTUAL DATA** - When tools return query results, show them in full. Don't just say "the query returned X rows" - show the rows.

5. **REMEMBER CONTEXT** - Use previous conversation info. If you listed tables before, reference them.

6. **MULTIPLE TOOL CALLS** - For "sample from each table", call the query tool once PER table and show each result.

7. **VERBOSE OUTPUT** - More data is better than summaries. Users want to see actual results, not descriptions.

**ONLY EXCEPTION:** Ask confirmation ONLY for DROP, DELETE, TRUNCATE, ALTER with data loss.

When using mssql_run_query tool, always include the returned rows/columns in your response text.
```

## Issues Discovered

1. **Rule #6 "MULTIPLE TOOL CALLS"** - Caused agent to pause between table queries asking for "continue"
2. **No Examples Section** - Agent interpreted rules literally without context
3. **Missing "STOP OFFERING UNSOLICITED NEXT STEPS"** - Agent kept suggesting more actions
4. **No Forbidden Phrases List** - Agent didn't know what questions to avoid
5. **Too Short** - Only 15 lines vs CLI's ~100 lines with comprehensive guidance

## Behavioral Problems

- Asked "Say 'next' to continue" when querying multiple tables
- Offered option lists instead of executing
- Gave passive-aggressive explanation when conflicting instructions prevented execution
- Did not complete full multi-table requests in one response

## Test Case That Failed

**User:** "show me a sample of 5 rows for each of the tables in the DB"  
**Expected:** Execute all 22 queries and show results  
**Actual:** Executed 1 query, then explained why it can't do all 22 at once, asked for "continue"

## Next Step

Replace these instructions with the proven CLI instructions from `dba_assistant.py` (lines 86-176) and test again.

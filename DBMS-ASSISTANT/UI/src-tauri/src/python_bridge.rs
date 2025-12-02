use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::PathBuf;

/// Initialize Python interpreter and set up the environment with venv
pub fn initialize_python() -> PyResult<()> {
    Python::with_gil(|py| {
        // Get paths
        let mut parent_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        parent_dir.pop(); // Remove "src-tauri"
        parent_dir.pop(); // Remove "UI"
        
        let mut venv_path = parent_dir.clone();
        venv_path.pop(); // Remove "DBMS-ASSISTANT"
        venv_path.push(".venv");
        
        // Programmatically activate the venv by executing activate_this.py equivalent
        let activate_code = format!(r#"
import sys
import site

# Set venv paths
venv_path = r'{}'
site_packages = r'{}'

# Add venv site-packages to the beginning of sys.path
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

# Update sys.prefix and sys.exec_prefix to venv
sys.prefix = venv_path
sys.exec_prefix = venv_path

# Force reload of site to pick up new paths
import importlib
importlib.reload(site)
"#, 
            venv_path.display(),
            venv_path.join("lib/python3.13/site-packages").display()
        );
        
        py.run_bound(&activate_code, None, None)?;
        
        // Now add project directories to Python path
        let sys = py.import_bound("sys")?;
        let path = sys.getattr("path")?;
        
        path.call_method1("insert", (0, parent_dir.to_str().unwrap()))?;
        
        let project_root = parent_dir.parent().unwrap();
        path.call_method1("insert", (0, project_root.to_str().unwrap()))?;
        
        Ok(())
    })
}

/// Run a DBA query with conversation history
pub fn run_python_query_with_history(query: String, history: Vec<(String, String)>) -> PyResult<String> {
    use std::fs::OpenOptions;
    use std::io::Write;
    
    // Create log file path
    let mut log_path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    log_path.pop(); // Remove "src-tauri"
    log_path.pop(); // Remove "UI"
    log_path.push("agent_forensic.log");
    
    // Log the incoming query
    if let Ok(mut log_file) = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_path)
    {
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        let _ = writeln!(log_file, "\n{}", "=".repeat(80));
        let _ = writeln!(log_file, "TIMESTAMP: {}", timestamp);
        let _ = writeln!(log_file, "INCOMING QUERY: {}", query);
        let _ = writeln!(log_file, "HISTORY LENGTH: {}", history.len());
        for (i, (q, r)) in history.iter().enumerate() {
            let _ = writeln!(log_file, "  History[{}] Q: {}", i, q);
            let _ = writeln!(log_file, "  History[{}] R: {}", i, r);
        }
        let _ = writeln!(log_file, "{}\n", "=".repeat(80));
    }
    
    Python::with_gil(|py| {
        // Set __file__ to point to DBMS-ASSISTANT directory first
        let mut parent_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        parent_dir.pop(); // Remove "src-tauri"
        parent_dir.pop(); // Remove "UI"
        let file_path = parent_dir.join("dba_assistant.py");
        
        // Get builtins module and add to globals so import works
        let builtins = py.import_bound("builtins")?;
        
        let globals = PyDict::new_bound(py);
        globals.set_item("__builtins__", builtins)?;
        globals.set_item("__file__", file_path.to_str().unwrap())?;
        globals.set_item("__name__", "__main__")?;
        
        // Convert history to Python-friendly format
        let history_str: String = history
            .iter()
            .map(|(q, r)| format!("User: {}\nAssistant: {}\n", q, r))
            .collect::<Vec<_>>()
            .join("\n---\n");
        
        // Create Python code to run async agent query with history
        let code = format!(r#"
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

from agent_framework import MCPStdioTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

async def run_query():
    server = os.getenv("SERVER_NAME", "localhost")
    database = os.getenv("DATABASE_NAME", "master")
    
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Construct path relative to DBMS-ASSISTANT directory
    base_path = Path(__file__).parent
    mcp_server_path = base_path / "MssqlMcp" / "Node" / "dist" / "index.js"
    
    if not mcp_server_path.exists():
        return f"Error: MCP server not found at {{mcp_server_path}}"
    
    mcp_env = {{
        "SERVER_NAME": server,
        "DATABASE_NAME": database,
        "SQL_USERNAME": os.getenv("SQL_USERNAME", ""),
        "SQL_PASSWORD": os.getenv("SQL_PASSWORD", ""),
        "TRUST_SERVER_CERTIFICATE": os.getenv("TRUST_SERVER_CERTIFICATE", "true"),
        "READONLY": os.getenv("READONLY", "false"),
    }}
    
    # Previous conversation history
    history = r'''{history}'''
    
    # Build context-aware prompt
    if history.strip():
        full_prompt = f"""Previous conversation:
{{history}}

---
Current question: {query}

Please answer based on the context from our previous conversation."""
    else:
        full_prompt = r'''{query}'''
    
    result_parts = []
    chunk_count = 0
    tool_call_count = 0
    
    # Open forensic log for streaming data
    forensic_log = Path(__file__).parent / "agent_forensic.log"
    
    try:
        async with (
            AzureCliCredential() as credential,
            MCPStdioTool(
                name="mssql",
                command="node",
                args=[str(mcp_server_path)],
                env=mcp_env,
                description="Microsoft SQL Server database operations",
            ) as mcp_tool,
            AzureAIAgentClient(async_credential=credential).create_agent(
                name="DBA_UI",
                instructions=f"""You are a helpful SQL Server DBA assistant for server '{{server}}' and database '{{database}}'.

You help database administrators with:
- Health monitoring and diagnostics
- Performance analysis and tuning  
- Query optimization
- Index recommendations
- Troubleshooting blocking and deadlocks
- Capacity planning
- Maintenance task guidance

**CRITICAL: SCHEMA-FIRST APPROACH**

BEFORE answering ANY question that involves table or column names, you MUST:

1. **FETCH THE SCHEMA FIRST** using these MCP tools:
   - Use `mssql_list_tables` to get all tables with their schemas
   - Use `mssql_list_schemas` to understand schema organization
   - For specific tables, query INFORMATION_SCHEMA.COLUMNS to get exact column names:
     ```sql
     SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
     FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'schema_name' AND TABLE_NAME = 'table_name'
     ORDER BY ORDINAL_POSITION
     ```

2. **VERIFY COLUMN NAMES** - Never guess column names like 'CustomerName', 'IndustryKey'. 
   - Query the actual schema to find the correct names (e.g., 'CompanyName', 'PrimaryIndustryId')
   - Use INFORMATION_SCHEMA views to discover relationships and foreign keys

3. **CACHE SCHEMA KNOWLEDGE** - Once you fetch schema for a table, remember it for the conversation

4. **USE EXACT NAMES** - Always use schema-qualified names (e.g., `dim.DimCustomer`) and exact column names from the schema

**HELPFUL SCHEMA DISCOVERY QUERIES:**

```sql
-- Get all columns for a specific table
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dim' AND TABLE_NAME = 'DimCustomer'
ORDER BY ORDINAL_POSITION;

-- Find foreign key relationships
SELECT 
    fk.name AS FK_Name,
    OBJECT_SCHEMA_NAME(fk.parent_object_id) AS Schema_Name,
    OBJECT_NAME(fk.parent_object_id) AS Table_Name,
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS Column_Name,
    OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS Referenced_Schema,
    OBJECT_NAME(fk.referenced_object_id) AS Referenced_Table,
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS Referenced_Column
FROM sys.foreign_keys AS fk
INNER JOIN sys.foreign_key_columns AS fkc 
    ON fk.object_id = fkc.constraint_object_id
WHERE OBJECT_SCHEMA_NAME(fk.parent_object_id) = 'dim'
ORDER BY Table_Name, FK_Name;

-- Find primary keys
SELECT 
    OBJECT_SCHEMA_NAME(t.object_id) AS Schema_Name,
    t.name AS Table_Name,
    c.name AS Column_Name,
    ic.key_ordinal AS Key_Order
FROM sys.tables t
INNER JOIN sys.indexes i ON t.object_id = i.object_id
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.is_primary_key = 1
    AND OBJECT_SCHEMA_NAME(t.object_id) = 'dim'
ORDER BY Table_Name, Key_Order;
```

**EXAMPLE WORKFLOW:**
User asks: "Show me customers by industry"

❌ WRONG: Immediately write `SELECT CustomerName, IndustryKey FROM Customer...`
✅ CORRECT: 
   Step 1: Run `mssql_list_tables` → Find dim.DimCustomer, dim.DimIndustry
   Step 2: Query schema for dim.DimCustomer columns → Find CompanyName, PrimaryIndustryId
   Step 3: Query schema for dim.DimIndustry columns → Find IndustryKey, IndustryName
   Step 4: Query FK relationships to find join keys
   Step 5: Write accurate query with verified column names

**CRITICAL BEHAVIORAL RULES - FOLLOW STRICTLY:**

1. **EXECUTE, DON'T ASK** - When you create a plan, EXECUTE IT IMMEDIATELY. Do NOT ask "do you want me to proceed?" - just proceed.

2. **NO REPEATED QUESTIONS** - If the user confirms a plan or says "yes, do it", DO NOT ask again. Execute the entire plan in one response.

3. **MAINTAIN CONTEXT** - Remember the conversation. If you already listed tables and relationships, DO NOT ask to list them again. Reference what you already know.

4. **BE DECISIVE** - Don't present options if the user already chose one. Example: If user says "PNG format", don't ask "PNG or Mermaid?" - just generate PNG.

5. **COMPLETE TASKS** - When asked to "create ER diagram", that means:
   - Query FK relationships (do it, don't ask)
   - Generate the diagram IN MERMAID TEXT FORMAT (do it, don't ask)
   - Provide the Mermaid code in a ```mermaid code block
   - DONE. No follow-up questions unless there's an error.

6. **ERD DIAGRAMS: ALWAYS USE MERMAID TEXT FORMAT** - When generating ERD diagrams, NEVER execute Python code or try to create image files. ALWAYS output Mermaid erDiagram syntax directly in your response. Users can paste it into mermaid.live to visualize. See detailed ERD instructions below.

7. **SCHEMA VALIDATION** - Always verify table and column names exist before writing SQL.

8. **USE SCHEMA-QUALIFIED NAMES** - Always use "schema.table" format in queries and descriptions.

9. **NO CIRCULAR PLANNING** - If you create a plan, execute it. Don't create a new plan to execute the previous plan.

10. **ASSUME PRODUCTION MINDSET** - This is a DBA tool for professionals. Be efficient, direct, and action-oriented.

11. **WHEN USER SAYS "NO MORE QUESTIONS"** - That's an explicit command. Execute everything without asking for confirmation.

**CRITICAL: YOU MUST SHOW ALL DATA IN YOUR RESPONSE**

When you call a tool and get results back, YOU MUST INCLUDE THE ACTUAL DATA in your text response.

❌ WRONG: "Samples retrieved successfully" (no data shown)
❌ WRONG: "Query executed, 5 rows returned" (no data shown)
❌ WRONG: "Here are the results:" (then nothing)

✅ CORRECT: Show the ACTUAL rows with their values. Example:
"Table: dim.DimCustomer (5 rows)
- CustomerKey: 1, CompanyName: Johnson Manufacturing, Revenue: 12500000
- CustomerKey: 2, CompanyName: Smith Healthcare, Revenue: 28000000
..."

**If a tool returns JSON with rows/data, copy that data into your response text!**

**EXAMPLES OF CORRECT BEHAVIOR:**

User: "Create ER diagram" or "Generate ERD"
✅ CORRECT: [Execute query for FKs] [Output Mermaid syntax] "Here's your ERD diagram in Mermaid format: ```mermaid\nerDiagram..."
❌ WRONG: "Do you want me to proceed with creating the diagram?"
❌ WRONG: Attempting to execute Python code with graphviz/networkx

User: "yes" (after a plan was presented)
✅ CORRECT: [Execute the entire plan] [Show results]
❌ WRONG: "What would you like me to do?" or "Should I proceed?"

User: "build ER diagram, no more questions"
✅ CORRECT: [Query FKs] [Output Mermaid syntax in code block] DONE.
❌ WRONG: "Do you want all tables or specific ones?" - THIS IS A QUESTION!

User: "export as PDF"
✅ CORRECT: [Convert to PDF] "Here's your PDF: [download link]"
❌ WRONG: "Do you also want PNG?" - They asked for PDF, give them PDF!

User: "produce a high-resolution PNG"
✅ CORRECT: [Generate PNG with high DPI] "Here's your PNG: [image]"
❌ WRONG: "Do you want me to include all tables or limit to four?" - JUST MAKE A DECISION AND EXECUTE!

User: "show me samples from all tables"
✅ CORRECT: [Execute queries] "dim.DimCustomer: row1data, row2data... dim.DimProduct: row1data, row2data..."
❌ WRONG: "Samples retrieved successfully" (WHERE IS THE DATA?!)

**CRITICAL: STOP OFFERING UNSOLICITED NEXT STEPS:**
When you complete a task, STOP. Don't ask "Do you want me to also do X?" That's still a question!

✅ CORRECT: "Here are the relationships. ✅ Analysis complete."
❌ WRONG: "Here are the relationships. Do you want me to build a diagram?"

✅ CORRECT: "ER diagram generated. [show diagram]"
❌ WRONG: "ER diagram generated. Do you want me to also export as PDF?"

If the user wants something else, THEY WILL ASK. Your job is to complete the requested task, not to suggest more work.

**REMEMBER:**
- "Do you want..." = FORBIDDEN after user confirms
- "Should I..." = FORBIDDEN after user says yes
- "Would you like..." = FORBIDDEN after explicit request
- "Do you want me to include..." = FORBIDDEN - make the best decision yourself
- "Do you want me to also..." = FORBIDDEN - don't suggest additional tasks
- "Do you want me to proceed?" after presenting a plan = FORBIDDEN
- When user says "no more questions" = STOP ASKING ENTIRELY
- "Successfully retrieved" without showing data = FORBIDDEN

**EXCEPTION:** Only offer to execute if the action is DESTRUCTIVE (DROP, DELETE, TRUNCATE, REBUILD with downtime).
For read-only analysis or safe operations, just do it.

**ERD DIAGRAM GENERATION - MANDATORY MERMAID FORMAT:**

⚠️ **CRITICAL: NEVER execute Python code to generate ERD diagrams. ALWAYS output Mermaid text syntax.** ⚠️

When asked to generate an ERD (Entity Relationship Diagram):

1. **Query foreign key relationships** using mssql_run_query tool:
```sql
SELECT 
    fk.name AS FK_Name,
    OBJECT_SCHEMA_NAME(fk.parent_object_id) AS Schema_Name,
    OBJECT_NAME(fk.parent_object_id) AS Table_Name,
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS Column_Name,
    OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS Referenced_Schema,
    OBJECT_NAME(fk.referenced_object_id) AS Referenced_Table,
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS Referenced_Column
FROM sys.foreign_keys AS fk
INNER JOIN sys.foreign_key_columns AS fkc 
    ON fk.object_id = fkc.constraint_object_id
ORDER BY Schema_Name, Table_Name, FK_Name;
```

2. **Output Mermaid erDiagram syntax directly** in a code block.

**Mermaid ERD Structure:**
- Wrap table attributes in curly braces after table name
- List attributes as: datatype ColumnName PK/FK
- Use relationship arrows between tables
- Format: TableA relationship TableB : "label"

**Mermaid Relationship Syntax:**
- Many to one: closing-braces-o--pipe-pipe (most common for FK)
- One to many: pipe-pipe--o-opening-braces
- One to one: pipe-pipe--pipe-pipe
- Many to many: closing-braces-o--o-opening-braces

**Example pattern:**
- Start with "erDiagram"
- Define each table with its columns
- Add relationship lines at the end
- Wrap entire output in triple-backtick mermaid code block

**FORBIDDEN - DO NOT DO THIS:**
❌ `import graphviz` or `import networkx` or `import matplotlib`
❌ `plt.savefig()` or `graph.render()` or any file creation
❌ Executing Python code to generate images
❌ Trying to create PNG, SVG, or any image files

**CORRECT RESPONSE PATTERN:**
1. "Let me get the foreign key relationships..." [execute SQL query]
2. [Show FK table if helpful]
3. "Here's the ERD diagram in Mermaid format:"
4. [Output ```mermaid code block with erDiagram syntax]
5. "You can visualize this at https://mermaid.live or in VS Code/GitHub"
6. DONE - no questions about format or alternatives

Just execute and deliver results WITH THE ACTUAL DATA. DBAs want action and data, not conversation and summaries.

Always explain your findings clearly and provide actionable recommendations.
When suggesting SQL queries, ensure they are safe and read-only unless explicitly asked for changes.""",
                tools=mcp_tool,
            ) as agent,
        ):
            with open(forensic_log, 'a') as log:
                log.write(f"\\n[AGENT STREAMING STARTED]\\n")
                log.write(f"Prompt: {{full_prompt[:200]}}...\\n")
                log.write("="*80 + "\\n")
            
            async for chunk in agent.run_stream(full_prompt):
                # Log ALL chunk attributes
                with open(forensic_log, 'a') as log:
                    log.write(f"\\n[RAW CHUNK {{chunk_count + 1}}]\\n")
                    log.write(f"Chunk type: {{type(chunk)}}\\n")
                    log.write(f"Chunk dir: {{dir(chunk)}}\\n")
                    if hasattr(chunk, 'tool_calls'):
                        log.write(f"Tool calls: {{chunk.tool_calls}}\\n")
                        tool_call_count += len(chunk.tool_calls or [])
                    if hasattr(chunk, 'text'):
                        log.write(f"Text: {{chunk.text}}\\n")
                    log.write("-"*40 + "\\n")
                
                if chunk.text:
                    chunk_count += 1
                    result_parts.append(chunk.text)
                    
                    # Log each text chunk
                    with open(forensic_log, 'a') as log:
                        log.write(f"[TEXT CHUNK {{chunk_count}}] Length: {{len(chunk.text)}}\\n")
                        log.write(f"Content: {{chunk.text}}\\n")
                        log.write("-"*40 + "\\n")
            
            with open(forensic_log, 'a') as log:
                log.write(f"\\n[STREAMING COMPLETE]\\n")
                log.write(f"Total text chunks: {{chunk_count}}\\n")
                log.write(f"Total tool calls detected: {{tool_call_count}}\\n")
                log.write("="*80 + "\\n")
        
        return ''.join(result_parts) if result_parts else "No response from agent"
    except Exception as e:
        import traceback
        return f"Error: {{str(e)}}\n\nTraceback:\n{{traceback.format_exc()}}"

# Run the async function
result = asyncio.run(run_query())

# Log the result to forensic file
import json
from datetime import datetime
log_path = Path(__file__).parent / "agent_forensic.log"
try:
    with open(log_path, 'a') as f:
        f.write(f"\\n[PYTHON RESULT AT {{datetime.now().isoformat()}}]\\n")
        f.write(f"Result length: {{len(result)}} characters\\n")
        f.write(f"Result preview (first 500 chars): {{result[:500]}}\\n")
        f.write(f"Result preview (last 500 chars): {{result[-500:]}}\\n")
        f.write(f"Full result:\\n{{result}}\\n")
        f.write("="*80 + "\\n")
except Exception as log_err:
    pass  # Don't fail if logging fails
"#, query = query, history = history_str);
        
        // Execute the code with globals
        py.run_bound(&code, Some(&globals), Some(&globals))?;
        
        // Get the result
        let result: String = globals.get_item("result")?.unwrap().extract()?;
        
        // Log the result back in Rust
        if let Ok(mut log_file) = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&log_path)
        {
            let _ = writeln!(log_file, "[RUST RECEIVED RESULT]");
            let _ = writeln!(log_file, "Result length: {} characters", result.len());
            let _ = writeln!(log_file, "Result preview (first 200): {}", 
                if result.len() > 200 { &result[..200] } else { &result });
            let _ = writeln!(log_file, "Result preview (last 200): {}", 
                if result.len() > 200 { &result[result.len()-200..] } else { &result });
            let _ = writeln!(log_file, "{}\n", "=".repeat(80));
        }
        
        Ok(result)
    })
}

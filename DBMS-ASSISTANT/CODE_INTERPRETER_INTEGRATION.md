# Code Interpreter Integration Guide

## Overview

This document outlines how to add **Code Interpreter** capabilities to the RDBMS DBA Assistant for generating visualizations and data analysis.

---

## 🎯 Use Cases for Code Interpreter in DBA Assistant

### **Visualization Capabilities:**
- 📊 **Performance Charts** - Query execution time trends, CPU/Memory usage graphs
- 📈 **Index Fragmentation Visualizations** - Bar charts showing fragmentation levels
- 🔍 **Query Plan Analysis** - Visual breakdown of execution plan operators
- 📉 **Growth Trends** - Table/database size over time
- 🗂️ **Table Relationship Diagrams** - ER diagrams from FK metadata
- 🎨 **Heatmaps** - Query frequency by table, blocking session patterns
- 📊 **Comparison Charts** - Before/after index optimization

### **Data Analysis:**
- Statistical analysis of query performance
- Anomaly detection in database metrics
- Predictive analysis for capacity planning

---

## 🚀 Integration Approaches

### **Approach 1: Azure AI Foundry Agent Service (Recommended)**

This approach uses the **Foundry Agent Service** which provides built-in `CodeInterpreterTool`.

#### **Requirements:**
```bash
pip install azure-ai-projects
pip install azure-ai-projects[agents]
```

#### **Implementation:**

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.identity.aio import AzureCliCredential
import os

# Initialize project client
project_client = AIProjectClient.from_connection_string(
    credential=AzureCliCredential(),
    conn_str=os.environ["AZURE_AI_PROJECT_CONNECTION_STRING"]
)

# Create code interpreter tool
code_interpreter = CodeInterpreterTool()

# Create agent with both MCP tools AND code interpreter
agent = project_client.agents.create_agent(
    model="gpt-5.1-chat",
    name="DBA-Assistant-with-Viz",
    instructions="""You are a SQL Server DBA assistant with visualization capabilities.
    
Use the code interpreter when users ask for:
- Charts, graphs, or visualizations
- Statistical analysis
- Data comparisons
- Performance trends

Always use matplotlib or seaborn for charts. Save as PNG and return the file.""",
    tools=[
        *mcp_tool.definitions,  # Your existing 11 MCP tools
        *code_interpreter.definitions  # Code interpreter tool
    ],
    tool_resources={
        **mcp_tool.resources,
        **code_interpreter.resources
    }
)
```

#### **Example Usage:**

```python
# User asks: "Show me a chart of index fragmentation for the top 10 most fragmented indexes"

# Agent will:
# 1. Call MCP tool: index_fragmentation() to get data
# 2. Call code_interpreter to generate matplotlib chart
# 3. Return PNG image

thread = project_client.agents.create_thread()
message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Show me a bar chart of index fragmentation for the top 10 indexes"
)

run = project_client.agents.create_and_process_run(
    thread_id=thread.id,
    agent_id=agent.id
)

# Get messages (will include image file references)
messages = project_client.agents.list_messages(thread_id=thread.id)
for message in messages:
    if message.file_ids:
        # Download generated images
        for file_id in message.file_ids:
            file_content = project_client.agents.files.get_file_content(file_id)
            with open(f"output_{file_id}.png", "wb") as f:
                f.write(file_content)
```

---

### **Approach 2: Microsoft Agent Framework with Custom Python Execution (Current Setup)**

Since you're currently using `AzureAIAgentClient` from `agent-framework`, we can add a **custom MCP tool** that executes Python code.

#### **Create Custom Python Execution MCP Tool:**

```typescript
// Add to MssqlMcp/Node/src/tools/PythonExecuteTool.ts

import { z } from "zod";
import { ToolDefinition } from "../types.js";
import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";

const PythonExecuteSchema = z.object({
  code: z.string().describe("Python code to execute (matplotlib/seaborn for viz)"),
  save_as: z.string().optional().describe("Filename to save output (e.g., chart.png)")
});

export const PythonExecuteTool: ToolDefinition = {
  name: "execute_python",
  description: "Execute Python code for data visualization and analysis. Use matplotlib/seaborn for charts.",
  inputSchema: {
    type: "object",
    properties: {
      code: {
        type: "string",
        description: "Python code to execute (include matplotlib.pyplot.savefig() for charts)"
      },
      save_as: {
        type: "string",
        description: "Optional: filename to save chart (e.g., 'fragmentation_chart.png')"
      }
    },
    required: ["code"]
  },

  async execute(args: z.infer<typeof PythonExecuteSchema>) {
    try {
      const { code, save_as } = args;
      
      // Create temp directory for outputs
      const tempDir = path.join(process.cwd(), "python_outputs");
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }

      // Write code to temp file
      const codeFile = path.join(tempDir, "execute_code.py");
      fs.writeFileSync(codeFile, code);

      // Execute Python code
      const output = execSync(`python3 ${codeFile}`, {
        cwd: tempDir,
        encoding: "utf-8",
        timeout: 30000 // 30 second timeout
      });

      // Check if file was created
      let fileInfo = null;
      if (save_as) {
        const filePath = path.join(tempDir, save_as);
        if (fs.existsSync(filePath)) {
          const stats = fs.statSync(filePath);
          fileInfo = {
            filename: save_as,
            size: stats.size,
            path: filePath
          };
        }
      }

      return {
        success: true,
        output: output.trim(),
        file: fileInfo,
        message: fileInfo 
          ? `✅ Code executed successfully. Generated file: ${fileInfo.filename} (${fileInfo.size} bytes)`
          : "✅ Code executed successfully"
      };

    } catch (error: any) {
      return {
        success: false,
        error: error.message,
        message: `❌ Python execution failed: ${error.message}`
      };
    }
  }
};
```

#### **Register the Tool:**

```typescript
// In MssqlMcp/Node/src/index.ts

import { PythonExecuteTool } from "./tools/PythonExecuteTool.js";

// Add to server.setRequestHandler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const tools = {
    // ... existing tools ...
    execute_python: PythonExecuteTool,
  };
  
  // ... rest of handler
});
```

#### **Update Agent Instructions:**

```python
# In gradio_app.py, update agent instructions

instructions = f"""You are a SQL Server DBA assistant with data visualization capabilities.

**Available Tools:**
- 11 MCP tools for database operations (query, analyze, describe)
- execute_python: Run Python code for charts and analysis

**Visualization Workflow:**
1. Use database tools to gather data (e.g., index_fragmentation)
2. Transform data into Python-friendly format
3. Use execute_python with matplotlib/seaborn code
4. Always use plt.savefig('filename.png') to save charts
5. Tell user where to find the generated file

**Example:**
User: "Show index fragmentation chart"
You:
1. Call index_fragmentation tool
2. Generate Python code:
   ```python
   import matplotlib.pyplot as plt
   data = {{indexes: [...], fragmentation: [...]}}
   plt.bar(data['indexes'], data['fragmentation'])
   plt.xlabel('Index Name')
   plt.ylabel('Fragmentation %')
   plt.title('Index Fragmentation Analysis')
   plt.xticks(rotation=45)
   plt.tight_layout()
   plt.savefig('fragmentation_chart.png')
   ```
3. Call execute_python with code and save_as='fragmentation_chart.png'
4. Inform user: "Chart saved to python_outputs/fragmentation_chart.png"

Be direct and action-oriented."""
```

---

## 📊 Example Interactions

### **Example 1: Index Fragmentation Chart**

**User:** "Show me a chart of index fragmentation"

**Agent Response:**
```
[Calls index_fragmentation MCP tool]
[Generates Python visualization code]
[Calls execute_python or code_interpreter]

Here's the index fragmentation analysis:

📊 Chart generated: fragmentation_chart.png

Top 5 Most Fragmented Indexes:
1. IX_Customer_Email - 87.3%
2. PK_Orders - 65.2%
3. IX_Product_Category - 54.8%
4. IX_Transactions_Date - 42.1%
5. IX_Users_LastLogin - 38.7%

Recommendation: Rebuild indexes with >30% fragmentation.
```

### **Example 2: Query Performance Trend**

**User:** "Show query execution time trends for the last 24 hours"

**Agent Response:**
```
[Calls query_stats MCP tool with time filter]
[Generates line chart with matplotlib]

📈 Query Performance Trend (24h)

Generated chart showing:
- Average execution time per hour
- Peak times: 2 PM - 4 PM (highest load)
- Slowest query: CustomerReport_v2 (avg 3.2s)

Chart saved to: query_performance_24h.png
```

---

## 🔧 Installation & Setup

### **Prerequisites:**

```bash
# For Approach 1 (Foundry Agent Service)
pip install azure-ai-projects[agents]

# For Approach 2 (Custom Python Tool)
pip install matplotlib seaborn pandas numpy

# Ensure Python 3 is available
python3 --version
```

### **Environment Variables:**

```bash
# Approach 1: Add to .env
AZURE_AI_PROJECT_CONNECTION_STRING="your-connection-string"

# Approach 2: No additional env vars needed
# Python outputs will be in: ./python_outputs/
```

---

## ⚖️ Comparison: Which Approach to Use?

| Feature | Foundry Agent Service | Custom MCP Tool |
|---------|----------------------|-----------------|
| **Setup Complexity** | Medium (new client) | Low (extend existing) |
| **Sandboxing** | ✅ Built-in sandbox | ⚠️ Runs locally |
| **File Management** | ✅ Managed by Azure | ❌ Manual cleanup |
| **Cost** | 💰 Azure charges | 💰 Free (local execution) |
| **Performance** | ⚡ Fast (Azure compute) | ⚡ Depends on local machine |
| **Integration** | Requires refactor | Works with current setup |
| **Security** | ✅ Azure security | ⚠️ Code execution risk |
| **Image Display** | ✅ Built-in | ❌ Manual display in UI |

### **Recommendation:**

- **For Production**: Use **Approach 1** (Foundry Agent Service) - better security, managed files
- **For Quick Prototyping**: Use **Approach 2** (Custom MCP Tool) - faster to implement with current setup

---

## 🚦 Next Steps

### **Phase 1: Quick Win (Custom MCP Tool)**
1. Implement `PythonExecuteTool` in MCP server
2. Update agent instructions for visualization
3. Test with simple bar chart request
4. Add file serving in Gradio UI to display generated charts

### **Phase 2: Production (Foundry Agent Service)**
1. Set up Azure AI Project connection
2. Migrate to `AIProjectClient`
3. Add `CodeInterpreterTool`
4. Implement file download/display in Gradio
5. Add chart caching and cleanup

### **Phase 3: Enhancement**
1. Add chart templates (standard DBA visualizations)
2. Implement interactive charts (Plotly)
3. Add report generation (PDF with charts)
4. Create chart gallery in UI

---

## 📚 References

- [Azure AI Foundry Code Interpreter](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Matplotlib Documentation](https://matplotlib.org/)
- [Seaborn Gallery](https://seaborn.pydata.org/examples/index.html)

---

**Last Updated:** November 29, 2025  
**Status:** Design Complete - Ready for Implementation

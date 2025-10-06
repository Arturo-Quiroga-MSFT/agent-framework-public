# NL2SQL Pipeline - Quick Start Guide

## 📦 What You Got

A complete **6-stage sequential pipeline** that converts natural language questions into SQL queries and executes them against your Azure SQL Database.

## 🎯 Files Created

```
python/nl2sql_workflow/
├── nl2sql_sequential_devui.py  # Main workflow file (port 8099)
├── README.md                    # Comprehensive documentation
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── workflow_outputs/            # Auto-created for results
```

## ⚡ Quick Setup (3 Steps)

### 1. Install Dependencies

```bash
# Install pyodbc
pip install pyodbc

# Install ODBC Driver (macOS)
brew install unixodbc
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18
```

### 2. Create .env File

```bash
cd python/nl2sql_workflow
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"

# Azure SQL Database
AZURE_SQL_SERVER="your-server.database.windows.net"
AZURE_SQL_DATABASE="your-database"
AZURE_SQL_USERNAME="your-username"
AZURE_SQL_PASSWORD="your-password"
```

### 3. Run It!

```bash
python nl2sql_sequential_devui.py
```

Opens browser at `http://localhost:8099` 🎉

## 🔍 How It Works

```
Your Question: "Show me top 10 customers by sales"
        ↓
   🎯 Intent: Needs top 10, customer data, sales aggregation
        ↓
   📊 Schema: Maps to Customers + Orders tables, SUM(Amount)
        ↓
   💻 SQL: SELECT TOP 10 c.Name, SUM(o.Amount) FROM...
        ↓
   ✅ Validate: Checks syntax, adds ORDER BY DESC
        ↓
   🔧 Execute: Runs against your Azure SQL DB
        ↓
   📝 Format: Natural language summary + insights
        ↓
   Saved to: workflow_outputs/nl2sql_pipeline_TIMESTAMP.txt
```

## 💡 Example Questions

Try these in the DevUI:

**Sales Analytics:**
- "Show me the top 10 customers by total purchase amount"
- "What are the sales trends by month for the last year?"

**Inventory:**
- "Which products have inventory below 50 units?"
- "List all products that need reordering"

**HR Queries:**
- "List all employees hired in 2024 with their departments"
- "What is the average salary by department?"

**Financial:**
- "What is the average order value per customer segment?"
- "Show revenue by product category for Q4 2024"

## 🎨 Key Features

✅ **6 Specialized Agents** - Each handles one pipeline stage
✅ **Sequential Processing** - Each agent builds on previous analysis
✅ **Real Database Schema** - Auto-retrieves your actual schema
✅ **Azure SQL Connection** - Uses SQL authentication
✅ **File Output** - Saves complete pipeline to timestamped files
✅ **DevUI Visualization** - See workflow structure
✅ **Tracing Support** - Console, Azure AI, OTLP, DevUI
✅ **Error Handling** - Graceful degradation if DB unavailable

## 🔧 Configuration Tips

### Use Existing Azure OpenAI Settings

Copy from your main `.env`:
```bash
# From workflows/.env
AZURE_OPENAI_ENDPOINT="..."
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1"
```

### Azure SQL Database Setup

1. **Enable SQL Authentication:**
   - Azure Portal → Your SQL Server → Settings → Azure Active Directory → Enable SQL authentication

2. **Configure Firewall:**
   - Azure Portal → Your SQL Server → Security → Firewalls and virtual networks
   - Add your client IP address

3. **Test Connection:**
   ```bash
   # Using Azure Data Studio or sqlcmd
   sqlcmd -S your-server.database.windows.net -d your-database -U username -P password
   ```

### Verify ODBC Driver

```bash
# macOS/Linux
odbcinst -q -d

# Should show:
[ODBC Driver 18 for SQL Server]
```

## 📊 Understanding the Output

### DevUI Shows 3 Executors:
1. `input_dispatcher` - Converts your input
2. `nl2sql_pipeline` - **All 6 agents run here sequentially**
3. `output_formatter` - Formats final result

### Text File Shows All 6 Stages:
```
Stage 1: USER QUESTION (your input)
Stage 2: INTENT ANALYZER (what you want)
Stage 3: SCHEMA EXPERT (tables/columns needed)
Stage 4: SQL GENERATOR (actual SQL query)
Stage 5: SQL VALIDATOR (validated/optimized SQL)
Stage 6: QUERY EXECUTOR (execution notes)
Stage 7: RESULTS FORMATTER (formatted insights)
```

## 🚨 Common Issues

### "Unable to connect to database"
- Check server name (no `tcp:` prefix)
- Verify firewall allows your IP
- Test SQL authentication is enabled

### "Import pyodbc failed"
```bash
pip install pyodbc
```

### "ODBC Driver not found"
- Install Microsoft ODBC Driver 18 (see README.md)
- Update `AZURE_SQL_DRIVER` in `.env`

### "Schema retrieval failed"
- Workflow continues with simulated schema
- Check user permissions on INFORMATION_SCHEMA views

## 🎓 Learning Points

This workflow demonstrates:

1. **Sequential Pipeline Pattern** - Perfect for dependent stages
2. **SequentialBuilder Usage** - Maintains conversation history
3. **SequentialWorkflowExecutor Wrapper** - Enables DevUI visibility
4. **Database Integration** - Real Azure SQL connectivity
5. **Agent Specialization** - Each agent has one clear job
6. **Context Building** - Each agent sees all previous analysis

## 🔄 Comparison with Your Other Workflows

| Feature | Concurrent Workflows | NL2SQL Sequential |
|---------|---------------------|-------------------|
| **Pattern** | Fan-out/Fan-in | Linear pipeline |
| **Agents** | Work independently | Build on each other |
| **Use Case** | Parallel analysis | Dependent stages |
| **DevUI View** | All agents visible | 3 executors (6 agents inside) |
| **Conversation** | Separate contexts | Accumulated history |
| **Best For** | Expert opinions | Multi-step processes |

## 📈 Next Steps

1. **Test with your database** - Run simple queries first
2. **Customize agent instructions** - Match your schema/domain
3. **Add error handling** - Enhance execution stage
4. **Enable tracing** - Set `ENABLE_DEVUI_TRACING=true`
5. **Extend functionality** - Add result visualization, caching, etc.

## 🤝 Need Help?

Check the comprehensive `README.md` for:
- Detailed prerequisites
- Step-by-step configuration
- Troubleshooting guide
- Security best practices
- Additional resources

## 🎉 You're Ready!

Run the workflow and ask your database questions in plain English!

```bash
python nl2sql_sequential_devui.py
```

Happy querying! 🚀

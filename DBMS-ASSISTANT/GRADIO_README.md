# 🗄️ RDBMS DBA Assistant - Gradio UI

Modern web-based chat interface for database administrators, powered by Microsoft Agent Framework and MSSQL MCP Server.

## 🎯 Features

### 💬 Interactive Chat Interface
- **Real-time AI Assistant**: Natural language conversations with your SQL Server
- **Chat History**: Persistent conversation tracking within session
- **Code Highlighting**: Automatic syntax highlighting for SQL queries
- **Copy-to-Clipboard**: Easy copying of queries and results

### 🔧 DBA Operations
- **Health Monitoring**: Database status, size, and configuration
- **Performance Analysis**: Query execution, index usage, statistics
- **Schema Exploration**: Tables, views, columns, relationships
- **Query Execution**: Run custom SQL queries safely
- **Troubleshooting**: Blocking sessions, long queries, errors

### 📊 Visual Features
- **Connection Status**: Live server and database connection info
- **Tool Availability**: See all 11 available MCP tools
- **Sample Queries**: Quick reference for common DBA tasks
- **Formatted Results**: Tables, code blocks, and structured output

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Ensure you're in the rdbms-assistant directory
cd AQ-CODE/rdbms-assistant

# Verify .env file exists with database credentials
cat .env
```

Your `.env` should contain:
```env
SERVER_NAME=your-server.database.windows.net
DATABASE_NAME=your-database
SQL_USERNAME=your-username
SQL_PASSWORD=your-password
TRUST_SERVER_CERTIFICATE=true
READONLY=false
```

### 2. Start the UI

**Option A: Using startup script (recommended)**
```bash
./start_ui.sh
```

**Option B: Manual start**
```bash
# Activate virtual environment
source ../../.venv/bin/activate

# Install dependencies if needed
pip install -r requirements.txt

# Build MCP server if not already built
cd MssqlMcp/Node && npm install && npm run build && cd ../..

# Start Gradio
python gradio_app.py
```

### 3. Access the Interface

Open your browser to: **http://localhost:7860**

### 4. Initialize Agent

1. Click the **"Initialize Agent 🚀"** button in the right panel
2. Wait for initialization confirmation
3. Start chatting!

## 📖 Using the Interface

### Main Chat Area (Left)
- **Chatbot Window**: Shows conversation history with the AI assistant
- **Input Box**: Type your questions or commands
- **Send Button**: Submit your message (or press Enter)
- **Clear Chat**: Reset conversation history
- **Retry Last**: Re-run the last query

### Control Panel (Right)
- **Initialize Agent**: Connect to database and start MCP server
- **Connection Info**: Current server, database, and mode
- **Quick Reference**: Sample queries and common tasks

## 💡 Sample Queries

### General Information
```
How many tables are in the database?
List all dimension tables
What's the database size?
Show me the schema for the customers table
```

### Performance Analysis
```
Show tables with most rows
Check for missing indexes
Find long-running queries
Show database statistics
```

### Health Checks
```
Are there any blocking sessions?
Check index fragmentation
Show database file sizes
List recent backups
```

### Data Exploration
```
Show top 10 customers
Count records in all fact tables
Find tables with no data
Show column types for a table
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Gradio Web UI                          │
│  (Browser Interface - http://localhost:7860)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   gradio_app.py                             │
│  - Async chat handler                                       │
│  - Message streaming                                        │
│  - History management                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Microsoft Agent Framework                      │
│  - AzureAIAgentClient                                       │
│  - Agent orchestration                                      │
│  - Tool routing                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                MCPStdioTool (MCP Bridge)                    │
│  - Spawns Node.js MCP server                                │
│  - Manages tool communication                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│             MSSQL MCP Server (Node.js)                      │
│  11 Tools:                                                  │
│  - connect_db, list_databases, run_query                   │
│  - list_table, describe_table                              │
│  - read_data, insert_data, update_data                     │
│  - create_table, drop_table, create_index                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure SQL Database                             │
│  Your SQL Server instance                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🔒 Security Features

### Read-Only Mode
Set `READONLY=true` in `.env` to enable safe exploration mode:
- Blocks INSERT, UPDATE, DELETE operations
- Prevents DROP, TRUNCATE, ALTER commands
- Allows only SELECT queries

### Environment Variables
- Credentials stored in `.env` (not committed to git)
- SSL/TLS support via `TRUST_SERVER_CERTIFICATE`
- Separate credentials for different environments

### Safe Query Execution
- WHERE clause enforcement for UPDATE operations
- Row limit defaults (1000 rows max)
- Query validation before execution
- Error handling and user feedback

## 🎨 Customization

### UI Theme
Modify in `gradio_app.py`:
```python
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # Options: Soft(), Glass(), Monochrome(), etc.
```

### Port Configuration
Change the port in `gradio_app.py`:
```python
demo.launch(
    server_port=7860,  # Change to your preferred port
    share=False,
)
```

### Agent Instructions
Customize DBA assistant behavior in the `create_agent()` call:
```python
agent = client.create_agent(
    name="InteractiveDBA",
    instructions="""Your custom instructions here...""",
    tools=mcp_tool,
)
```

## 🐛 Troubleshooting

### Agent Won't Initialize
```
❌ MCP server not found
```
**Solution**: Build the MCP server
```bash
cd MssqlMcp/Node
npm install
npm run build
cd ../..
```

### Connection Errors
```
❌ Login failed for user
```
**Solution**: Verify credentials in `.env` file
```bash
# Test connection
python dba_assistant.py
```

### Port Already in Use
```
❌ Address already in use
```
**Solution**: Change port or kill existing process
```bash
lsof -ti:7860 | xargs kill -9
# Or change port in gradio_app.py
```

### Missing Dependencies
```
❌ ModuleNotFoundError: No module named 'gradio'
```
**Solution**: Install requirements
```bash
pip install -r requirements.txt
```

## 📦 Deployment

### Local Development
```bash
./start_ui.sh
# Access at http://localhost:7860
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y nodejs npm
RUN cd MssqlMcp/Node && npm install && npm run build

RUN pip install -r requirements.txt

EXPOSE 7860
CMD ["python", "gradio_app.py"]
```

### Cloud Deployment
For production deployment, consider:
- **Azure Container Apps**: Easy Python + Node.js deployment
- **Azure App Service**: Web Apps with container support
- **Docker Compose**: Multi-container orchestration

⚠️ **Security Note**: Never commit `.env` file. Use Azure Key Vault or similar for production credentials.

## 🔄 Future Enhancements

### Planned Features
- [ ] Multi-session support with separate agents
- [ ] Query history export (CSV, JSON)
- [ ] Visual query builder
- [ ] Performance dashboards with charts
- [ ] Alert configuration and monitoring
- [ ] Scheduled query execution
- [ ] Multi-database switching
- [ ] User authentication and roles
- [ ] Query result visualization (plotly/matplotlib)
- [ ] Database schema diagram viewer

### Contributions Welcome
See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## 📝 Files

```
rdbms-assistant/
├── gradio_app.py           # Main Gradio UI application
├── start_ui.sh             # Startup script
├── GRADIO_README.md        # This file
├── dba_assistant.py        # CLI version
├── test_all_tools.py       # Tool testing suite
├── requirements.txt        # Python dependencies
├── .env                    # Database credentials (not in git)
└── MssqlMcp/
    └── Node/
        ├── dist/           # Built MCP server
        └── src/            # TypeScript source
```

## 📚 Related Documentation

- [Main README](README.md) - Project overview
- [CHANGELOG](CHANGELOG.md) - Recent changes and fixes
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Gradio Documentation](https://www.gradio.app/docs)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 🙋 Support

For questions or issues:
1. Check [TROUBLESHOOTING](#-troubleshooting) section above
2. Review [CHANGELOG](CHANGELOG.md) for recent fixes
3. Open an issue in the repository

---

**Built with ❤️ using Microsoft Agent Framework**

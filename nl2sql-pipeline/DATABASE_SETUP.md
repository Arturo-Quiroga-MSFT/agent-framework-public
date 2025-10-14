# Real Database Integration Setup Guide

## 🎯 Goal
Connect your NL2SQL pipeline to the real Azure SQL Database (`TERADATA-FI` on `aqsqlserver001.database.windows.net`)

## 📋 Prerequisites

### 1. ODBC Driver Installation

The workflow uses `pyodbc` which requires the Microsoft ODBC Driver for SQL Server.

**Check if installed:**
```bash
# macOS/Linux
odbcinst -j

# Should show ODBC Driver 18 for SQL Server
```

**Install if needed:**

**macOS:**
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql18 mssql-tools18
```

**Linux (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
sudo apt-get update
sudo apt-get install msodbcsql18
```

**Windows:**
- Usually pre-installed
- If not: Download from [Microsoft](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 2. Azure SQL Firewall Configuration

Ensure your IP address is allowed in the Azure SQL Server firewall:

1. Go to **Azure Portal**
2. Navigate to **SQL Server** → `aqsqlserver001`
3. Click **Networking** (or **Firewalls and virtual networks**)
4. Add your current IP address
5. Click **Save**

## 🔧 Configuration Steps

### Step 1: Update .env File

Open `/Users/arturoquiroga/GITHUB/agent-framework-public/nl2sql-pipeline/.env` and update:

```bash
# SQL Server Connection (SQL Authentication)
MSSQL_SERVER_NAME=aqsqlserver001.database.windows.net
MSSQL_DATABASE_NAME=TERADATA-FI
MSSQL_USERNAME=your-actual-username      # ← UPDATE THIS
MSSQL_PASSWORD=your-actual-password      # ← UPDATE THIS
MSSQL_AUTHENTICATION_TYPE=SqlPassword

# SQL Query Safety Settings
MAX_ROWS=1000
ALLOW_WRITE_OPERATIONS=false
QUERY_TIMEOUT_SECONDS=30
```

**Replace:**
- `your-actual-username` with your SQL Server username
- `your-actual-password` with your SQL Server password

### Step 2: Test the Connection

Before running the full workflow, test the connection:

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/nl2sql-pipeline
python test_db_connection.py
```

**Expected Output:**
```
============================================
🔍 Testing Azure SQL Database Connection
============================================

📋 Configuration:
   Server: aqsqlserver001.database.windows.net
   Database: TERADATA-FI
   Username: your-username
   Password: ********
   Auth Type: SqlPassword

🔌 Connecting to database...
✅ Connection successful!

📊 Running test query...
✅ SQL Server Version: Microsoft SQL Server 2022...

🗂️  Retrieving schema information...
✅ Found 15 tables:

   1. dbo.Customers (5 columns)
      - CustomerID: int NOT NULL
      - CustomerName: nvarchar(100) NULL
      - Email: nvarchar(100) NULL
      ...

============================================
✅ Database Connection Test PASSED
============================================

Your database is ready for NL2SQL queries!
Run: python nl2sql_workflow.py
```

## 🚀 Running with Real Database

### Start the Workflow

```bash
cd /Users/arturoquiroga/GITHUB/agent-framework-public/nl2sql-pipeline
python nl2sql_workflow.py
```

**Look for this confirmation:**
```
✅ Database Configuration Found
   Server: aqsqlserver001.database.windows.net
   Database: TERADATA-FI
   Authentication: SQL Password
```

### Access DevUI

Open your browser to: **http://localhost:8097**

### Submit a Question

Try questions based on your actual schema:
- "Show me the first 10 rows from [your-table-name]"
- "What tables are in the database?"
- "Count the rows in [table-name]"

## 🔍 Verification

After submitting a question, check:

1. **Terminal Output** - Should show:
   ```
   ✅ Retrieved schema for 15 tables from database
   ✅ Query executed: 10 rows, 45.23ms
   ```

2. **DevUI Results** - Will show:
   - Real SQL query generated
   - Actual data from your database
   - AI interpretation of real results

3. **Result File** - Saved to:
   ```
   workflow_outputs/nl2sql_results_YYYYMMDD_HHMMSS.txt
   ```

## 🔒 Security Best Practices

### 1. Never Commit Credentials
```bash
# Verify .env is in .gitignore
cat .gitignore | grep .env
```

### 2. Use Read-Only Credentials (Recommended)

Create a dedicated read-only SQL user:

```sql
-- Run this in Azure SQL Database
CREATE USER [nl2sql_readonly] WITH PASSWORD = 'StrongPassword123!';
ALTER ROLE db_datareader ADD MEMBER [nl2sql_readonly];
GRANT VIEW DEFINITION TO [nl2sql_readonly];
```

Then use this in your `.env`:
```bash
MSSQL_USERNAME=nl2sql_readonly
MSSQL_PASSWORD=StrongPassword123!
```

### 3. Enable Query Timeouts

Already configured in `.env`:
```bash
QUERY_TIMEOUT_SECONDS=30  # Prevents long-running queries
MAX_ROWS=1000             # Limits result set size
ALLOW_WRITE_OPERATIONS=false  # Prevents INSERT/UPDATE/DELETE
```

## 🐛 Troubleshooting

### Issue: "Connection test failed: No module named 'pyodbc'"

**Solution:**
```bash
.venv/bin/pip install pyodbc
```

### Issue: "Connection test failed: [Microsoft][ODBC Driver 18 for SQL Server][SSL Provider]"

**Solution:** SSL/TLS certificate issue

Update connection string in `db_utils.py` to trust server certificate:
```python
# Add this to connection string parts:
"TrustServerCertificate=yes"
```

Or install the certificate properly (preferred for production).

### Issue: "Login failed for user 'username'"

**Solutions:**
1. Verify username and password are correct
2. Check if the user exists in the database
3. Ensure the user has at least `db_datareader` role

### Issue: "Cannot open server 'aqsqlserver001' requested by the login"

**Solution:** Firewall issue
1. Go to Azure Portal → SQL Server → Networking
2. Add your IP address
3. Save and wait 1-2 minutes

### Issue: "Connection timeout"

**Solutions:**
1. Check your network connection
2. Verify the server name is correct
3. Ensure no VPN/proxy is blocking the connection
4. Try increasing timeout: `QUERY_TIMEOUT_SECONDS=60`

### Issue: "Driver not found"

**Solution:** ODBC Driver not installed

```bash
# macOS
brew install msodbcsql18

# Linux
sudo apt-get install msodbcsql18

# Verify installation
odbcinst -q -d -n "ODBC Driver 18 for SQL Server"
```

## 📊 Performance Optimization

### For Large Databases

If your database has many tables (>100), you may want to:

1. **Cache schema information:**

Add to `db_utils.py`:
```python
import json
from pathlib import Path

def cache_schema(schema: dict, cache_file: str = "schema_cache.json"):
    """Cache schema to avoid repeated queries."""
    Path(cache_file).write_text(json.dumps(schema, indent=2))

def load_cached_schema(cache_file: str = "schema_cache.json") -> dict | None:
    """Load cached schema if available."""
    cache_path = Path(cache_file)
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    return None
```

2. **Limit schema to specific schemas:**

Update the SQL query in `get_schema_info()`:
```sql
WHERE t.TABLE_TYPE = 'BASE TABLE'
  AND t.TABLE_SCHEMA IN ('dbo', 'analytics')  -- Add your schemas
```

## ✅ Success Checklist

Before considering the integration complete:

- [ ] ODBC Driver installed
- [ ] Firewall configured for your IP
- [ ] Credentials updated in `.env`
- [ ] Test script runs successfully (`test_db_connection.py`)
- [ ] Workflow starts without errors
- [ ] DevUI shows real schema (not mock)
- [ ] Test query returns real data
- [ ] Results saved to file
- [ ] Performance acceptable (<5 seconds for simple queries)

## 🎉 Next Steps

Once connected:

1. **Test various query types:**
   - Simple SELECT: "Show me 5 rows from [table]"
   - Aggregations: "Count rows in [table]"
   - Joins: "Join [table1] with [table2]"
   - Filters: "Find records where [condition]"

2. **Monitor performance:**
   - Check execution times in logs
   - Review query plans for slow queries
   - Consider adding indexes if needed

3. **Enhance features:**
   - Add query history tracking
   - Implement result caching
   - Create visualization options
   - Add export capabilities (CSV, Excel)

## 📖 Additional Resources

- [Azure SQL Database Documentation](https://learn.microsoft.com/azure/azure-sql/)
- [pyodbc Documentation](https://github.com/mkleehammer/pyodbc/wiki)
- [Microsoft ODBC Driver](https://learn.microsoft.com/sql/connect/odbc/microsoft-odbc-driver-for-sql-server)
- [SQL Server Best Practices](https://learn.microsoft.com/azure/azure-sql/database/performance-guidance)

---

**Need Help?** Check the logs in the terminal for detailed error messages.

# MCP Server Tools Guide
## Complete Reference for All 11 MSSQL MCP Tools

This guide documents all 11 tools available in the enhanced MSSQL MCP Server for database administration tasks.

---

## 🔍 DBA Workflow: Connect → Discover → Analyze → Query → Optimize

The 11 tools are organized to support the complete DBA workflow from initial connection through optimization.

---

## 📋 Tool Categories

### **DBA/Metadata Tools (6)**

Tools for connecting, discovering schema, and understanding database structure.

#### 1. **connect_db**
**Purpose:** Test database connectivity and retrieve server information

**Use Cases:**
- Verify database connection is working
- Get SQL Server version and instance name
- Check database statistics (table count, view count, data size)
- Initial health check

**Returns:**
- Server version (e.g., Microsoft SQL Server 2022)
- Server name
- Current database name
- Number of tables and views
- Total data size in MB

**Example Questions:**
- "Test the database connection"
- "What SQL Server version are we running?"
- "How many tables are in the database?"

---

#### 2. **list_databases**
**Purpose:** List all databases on the SQL Server instance

**Use Cases:**
- Discover available databases
- Cross-database exploration
- Database inventory
- Exclude system databases (master, tempdb, model, msdb)

**Returns:**
- Database name
- Database ID
- Creation date
- State (ONLINE, OFFLINE, etc.)
- Recovery model (SIMPLE, FULL, BULK_LOGGED)

**Example Questions:**
- "List all databases on this server"
- "Show me available databases"
- "What databases exist besides system DBs?"

---

#### 3. **list_table**
**Purpose:** List all tables in the current database

**Use Cases:**
- Schema discovery
- Table inventory
- Filter by schema (dim, fact, dbo, etc.)
- Find specific table patterns

**Parameters:**
- `schemaName` (optional): Filter by schema name

**Returns:**
- Schema name
- Table name
- Full qualified name (schema.table)

**Example Questions:**
- "List all tables"
- "Show only dimension tables" (filters for dim schema)
- "What fact tables exist?"

---

#### 4. **describe_table**
**Purpose:** Get detailed schema information for a specific table

**Use Cases:**
- Understand table structure
- Review column definitions
- Check data types and constraints
- Validate schema before queries

**Parameters:**
- `tableName`: Table name (supports "schema.table" or just "table")

**Returns:**
- Column name
- Data type
- Max length (for varchar, nvarchar, etc.)
- Nullable (YES/NO)
- Default value
- Ordinal position (column order)

**Enhanced Features:**
- ✅ Supports schema-qualified names (e.g., "dim.DimCustomer")
- ✅ Defaults to 'dbo' schema if not specified
- ✅ Orders columns by position

**Example Questions:**
- "Describe the dim.DimCustomer table"
- "Show me the schema for FACT_LOAN_ORIGINATION"
- "What columns are in the customers table?"

---

#### 5. **run_query**
**Purpose:** Execute arbitrary SQL queries with safety checks

**Use Cases:**
- Custom SQL queries
- Complex joins and aggregations
- Performance analysis queries
- Database statistics
- Foreign key discovery

**Parameters:**
- `query`: SQL query string
- `maxRows` (optional): Limit result rows (default 1000)

**Safety Features:**
- ✅ Read-only mode enforcement (when enabled)
- ✅ Blocks dangerous operations: INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, CREATE
- ✅ Query validation before execution
- ✅ Row count limits
- ✅ Execution time tracking

**Returns:**
- Row count
- Columns (name, type)
- Result rows
- Execution time

**Example Questions:**
- "Count all records in fact tables"
- "Show foreign key relationships"
- "Get top 10 loans by amount"
- "Check for NULL values in customer IDs"

---

#### 6. **list_databases** (duplicate functionality)
See tool #2 above - provides database enumeration capabilities.

---

### **CRUD Operations (3)**

Tools for reading and modifying data.

#### 7. **read_data**
**Purpose:** Read/query data from tables with filtering and pagination

**Use Cases:**
- Simple table data retrieval
- Filtered queries
- Pagination support
- Data exploration without writing SQL

**Parameters:**
- `tableName`: Target table
- `columns` (optional): Specific columns to retrieve
- `filter` (optional): WHERE clause conditions
- `limit` (optional): Max rows to return
- `offset` (optional): Skip N rows for pagination

**Returns:**
- Matching rows
- Column metadata

**Example Questions:**
- "Show the first 10 customers"
- "Read data from dim.DimLoanProduct"
- "Get loans where amount > 100000"

---

#### 8. **insert_data**
**Purpose:** Insert new records into tables

**Use Cases:**
- Add new dimension values
- Insert test data
- Data migration
- Manual data entry

**Parameters:**
- `tableName`: Target table
- `data`: Object with column-value pairs

**Restrictions:**
- ❌ Disabled in read-only mode
- ⚠️ Requires exact column names
- ⚠️ Must match data types

**Example Questions:**
- "Insert a new loan product"
- "Add a customer record"

---

#### 9. **update_data**
**Purpose:** Update existing records

**Use Cases:**
- Fix data issues
- Update statuses
- Correct values
- Data maintenance

**Parameters:**
- `tableName`: Target table
- `data`: Object with column-value pairs to update
- `filter`: WHERE clause (REQUIRED for safety)

**Safety Features:**
- ✅ **Requires WHERE clause** - prevents accidental full table updates
- ❌ Disabled in read-only mode

**Example Questions:**
- "Update customer status to 'ACTIVE' where ID = 123"
- "Set delinquency status to 'CURRENT' for loan 456"

---

### **DDL Operations (2)**

Tools for database structure management.

#### 10. **create_table**
**Purpose:** Create new tables with specified schema

**Use Cases:**
- Create staging tables
- Add dimension tables
- Set up temporary tables
- Database schema expansion

**Parameters:**
- `tableName`: New table name
- `columns`: Array of column definitions (name, type, nullable, etc.)

**Restrictions:**
- ❌ Disabled in read-only mode
- ⚠️ Requires proper permissions

**Example Questions:**
- "Create a staging table for customer imports"
- "Add a new dimension table"

---

#### 11. **create_index**
**Purpose:** Create indexes for performance optimization

**Use Cases:**
- Improve query performance
- Speed up JOIN operations
- Optimize frequent queries
- Add covering indexes

**Parameters:**
- `tableName`: Target table
- `indexName`: Name for the new index
- `columns`: Array of columns to index
- `isUnique` (optional): Create unique index

**Example Questions:**
- "Create an index on customer_id"
- "Add a composite index on loan_id and date"
- "Optimize queries on FACT_PAYMENT_TRANSACTION"

---

## 🎯 Complete DBA Workflow Example

### Phase 1: Connect
```
Question: "Test the database connection"
Tool Used: connect_db
Result: Server info, database name, table count, size
```

### Phase 2: Discover
```
Question: "List all dimension tables"
Tool Used: list_table (with schemaName='dim')
Result: All tables in dim schema

Question: "Describe dim.DimCustomer"
Tool Used: describe_table
Result: All columns with types, nullability, defaults
```

### Phase 3: Analyze
```
Question: "Show tables with most rows"
Tool Used: run_query
SQL: SELECT COUNT(*) FROM each table
Result: Row counts per table

Question: "What are the foreign key relationships?"
Tool Used: run_query
SQL: Query sys.foreign_keys and sys.foreign_key_columns
Result: All FK constraints
```

### Phase 4: Query
```
Question: "Show top 10 loans by amount"
Tool Used: run_query
SQL: SELECT TOP 10 * FROM FACT_LOAN_ORIGINATION ORDER BY LoanAmount DESC
Result: Loan records

Question: "Count records in fact tables"
Tool Used: run_query (multiple)
Result: Record counts per fact table
```

### Phase 5: Optimize
```
Question: "Check for missing indexes"
Tool Used: run_query
SQL: Query sys.dm_db_missing_index_details
Result: Index recommendations

Question: "Create index on customer_id"
Tool Used: create_index
Result: New index created
```

---

## 🔒 Safety Features

### Read-Only Mode
When `READONLY=true` in environment:
- ✅ All read operations (connect_db, list_*, describe_table, run_query with SELECT, read_data)
- ❌ Blocked: insert_data, update_data, create_table, create_index
- ❌ run_query blocks: INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, CREATE

### Data Protection
- **update_data** requires WHERE clause
- **run_query** enforces maxRows limit (default 1000)
- Parameterized queries prevent SQL injection
- Error messages don't expose sensitive data

---

## 📊 Tool Usage Frequency (Typical DBA Session)

**Most Used:**
1. `run_query` - 40% (custom queries, analysis)
2. `describe_table` - 20% (schema exploration)
3. `list_table` - 15% (discovery)
4. `read_data` - 10% (quick data checks)
5. `connect_db` - 5% (health checks)

**Occasional:**
6. `list_databases` - 5%
7. `create_index` - 3%
8. `update_data` - 2%

**Rare:**
9. `insert_data` - <1%
10. `create_table` - <1%

---

## 🚀 Quick Reference

| Tool | Primary Use | Read-Only Safe? | Output Format |
|------|-------------|-----------------|---------------|
| connect_db | Connection test | ✅ | Server info + stats |
| list_databases | Database enumeration | ✅ | Database list |
| list_table | Table discovery | ✅ | Table list |
| describe_table | Schema details | ✅ | Column definitions |
| run_query | Custom SQL | ✅ (SELECT only) | Query results |
| read_data | Simple queries | ✅ | Table data |
| insert_data | Add records | ❌ | Success/failure |
| update_data | Modify records | ❌ | Rows affected |
| create_table | New tables | ❌ | Success/failure |
| create_index | Performance | ❌ | Success/failure |

---

## 💡 Best Practices

1. **Start with connect_db** - Always verify connection first
2. **Use describe_table before queries** - Understand schema to avoid errors
3. **Prefer run_query for complex analysis** - Most flexible tool
4. **Use read_data for simple lookups** - Easier than writing SQL
5. **Enable read-only mode for exploration** - Prevents accidental changes
6. **Check relationships before queries** - Use run_query to find FKs
7. **Test queries with LIMIT** - Use maxRows to preview results
8. **Create indexes after analysis** - Based on actual query patterns

---

## 🔧 Environment Configuration

```env
# Database Connection
SERVER_NAME=your-server.database.windows.net
DATABASE_NAME=your-database
SQL_USERNAME=your-username
SQL_PASSWORD=your-password
TRUST_SERVER_CERTIFICATE=true

# Safety Settings
READONLY=false  # Set to 'true' for read-only mode

# Azure AI (for agent)
AZURE_AI_PROJECT_ENDPOINT=your-endpoint
```

---

## 📚 Related Documentation

- [Main README](README.md) - Project overview
- [CHANGELOG](CHANGELOG.md) - Tool enhancements and fixes
- [QUICKSTART](QUICKSTART.md) - Quick start guide
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

**Built with Microsoft Agent Framework**

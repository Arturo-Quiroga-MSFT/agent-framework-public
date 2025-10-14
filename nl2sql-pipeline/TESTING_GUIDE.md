# NL2SQL Pipeline - Testing Guide

## ✅ Current Status

The NL2SQL pipeline is now **running successfully** with an interactive input form in DevUI!

## 🎯 How to Test the Workflow

### 1. Access the DevUI
Open your browser to: **http://localhost:8097**

### 2. Submit a Test Question

You should see a form with a text input field labeled "**question**". 

**Try these example questions:**

#### Simple Queries
- "What are the top 10 customers by total revenue?"
- "Show me all orders from last month"
- "How many products are out of stock?"
- "List all employees hired in 2024"

#### Analytics Queries
- "What is the average order value by region?"
- "Show me the top 5 best-selling products"
- "What's the total revenue for each customer?"

#### Aggregation Queries
- "Count the number of orders per customer"
- "Sum the total quantity of each product sold"
- "Calculate the average price of products by category"

### 3. View Results

After submitting a question, you'll see:

1. **Workflow Graph**: Visual representation showing the flow through all 10 executors
   - `input_dispatcher` - Converts your input
   - `schema_retriever` - Gets database schema  
   - `sql_generator` - GPT-4 generates SQL
   - `to-conversation:sql_generator` - Adapter
   - `sql_validator` - Safety checks
   - `query_executor` - Executes query
   - `results_interpreter` - GPT-4 interprets
   - `to-conversation:results_interpreter` - Adapter
   - `output_formatter` - Formats output
   - `end` - Workflow completion

2. **Results Pane**: Formatted output showing each step's contribution

3. **Individual Executor Details**: Click any node to see its specific input/output

## 🔄 Current Demo Mode

The workflow is currently running with **mock data**:

- ⚠️ Mock database schema (Customers, Orders, Products, OrderDetails)
- ⚠️ Mock query execution (returns sample data)
- ✅ Real LLM agents (SQL generation and results interpretation)
- ✅ Real validation and safety checks
- ✅ Full observability and tracing

### Mock Schema
```
Database: SampleDB
Server: Azure SQL Database

Available Tables:
  - Customers (CustomerID, CustomerName, Email, Region)
  - Orders (OrderID, CustomerID, OrderDate, TotalAmount)
  - Products (ProductID, ProductName, Category, Price, StockQuantity)
  - OrderDetails (OrderDetailID, OrderID, ProductID, Quantity, UnitPrice)
```

### Mock Query Results
When you submit a question, the pipeline will:
1. ✅ Generate a real SQL query using GPT-4
2. ✅ Validate the query for safety
3. ⚠️ Return mock sample data (3 rows)
4. ✅ Interpret the results using GPT-4

## 📊 What You'll See

### Example Flow for: "Show me the top 5 customers by revenue"

**Step 1: User Input**
```
Your question about the database
```

**Step 2: Schema Retrieval**
```
DATABASE SCHEMA CONTEXT:
[Mock schema with table definitions]

ORIGINAL USER QUESTION:
Show me the top 5 customers by revenue
```

**Step 3: SQL Generation (GPT-4)**
````sql
SELECT TOP 5 
    c.CustomerName,
    SUM(o.TotalAmount) as TotalRevenue
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerName
ORDER BY TotalRevenue DESC
````

**Step 4: SQL Validation**
```
VALIDATED SQL QUERY:
[SQL query with safety confirmation]
```

**Step 5: Query Execution**
```
Query Results:
[Mock sample data - 3 rows]
Execution Time: ~50ms
```

**Step 6: Results Interpretation (GPT-4)**
```
**Answer:** The top 5 customers by total revenue are...

**Insights:**
- Customer distribution shows...
- Revenue concentration indicates...

**Suggestions:**
- Analyze customer retention rates
- Investigate seasonal patterns
```

## 🎨 DevUI Features to Try

### Interactive Features
1. **Click executor nodes** to see detailed input/output
2. **View traces** tab for OpenTelemetry data
3. **Use "Run Again"** button to test multiple questions
4. **Zoom/pan** the workflow graph for better visibility

### Result Files
Results are automatically saved to:
```
nl2sql-pipeline/workflow_outputs/nl2sql_results_YYYYMMDD_HHMMSS.txt
```

## 🔧 Next Steps: Real Database Integration

To connect to a real Azure SQL Database, you'll need to:

1. **Configure MSSQL Connection**
   - Set `MSSQL_CONNECTION_ID` in `.env`
   - Or implement direct pyodbc connection

2. **Update Executors**
   - Replace `_get_mock_schema()` in `SchemaRetrieverExecutor`
   - Replace `_execute_mock_query()` in `QueryExecutorExecutor`
   - Use actual database connections

3. **Test with Real Data**
   - Verify schema retrieval
   - Test query execution
   - Validate results interpretation

## 🐛 Troubleshooting

### "No validated SQL query found"
- The SQL generator didn't produce valid SQL
- Check the `sql_generator` node output
- Try rephrasing your question

### "Error retrieving schema"
- Expected in demo mode (using mocks)
- Will be fixed when database is connected

### Workflow doesn't start
- Refresh the browser page
- Check terminal for errors
- Verify the server is running on port 8097

## 📖 Documentation

- **QUICKSTART.md** - 5-minute setup guide
- **ARCHITECTURE.md** - System design details
- **CONFIGURATION.md** - Customization options
- **examples/sample_questions.md** - 100+ test queries

## 🎉 Success Criteria

You've successfully tested the workflow when you:

1. ✅ Submitted a natural language question
2. ✅ Saw the workflow execute through all steps
3. ✅ Received formatted results with:
   - Generated SQL query
   - Validation confirmation
   - Mock execution results
   - Natural language insights

## 💡 Tips

- **Start simple**: Use basic questions first
- **Check each step**: Click nodes to see transformations
- **Read interpretations**: The LLM provides insights beyond raw data
- **Try variations**: Test different question phrasings
- **Save results**: Output files are timestamped for comparison

---

**Ready to test?** Go to http://localhost:8097 and submit your first question! 🚀

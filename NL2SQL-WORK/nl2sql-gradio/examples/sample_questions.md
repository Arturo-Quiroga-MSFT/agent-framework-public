# Example Questions for NL2SQL Pipeline

Test these questions with your database to see the pipeline in action.

## Basic Queries

### Simple Selection
```
Show me all customers
```

### With Limit
```
What are the top 20 products?
```

### Specific Columns
```
List customer names and email addresses
```

## Filtering

### Date Filters
```
Show me orders from last week
```

```
Which customers registered in 2024?
```

### Numeric Filters
```
Find products with price greater than $100
```

```
Show orders with quantity over 50
```

### Text Filters
```
Find customers whose name starts with 'A'
```

## Aggregations

### Count
```
How many total orders do we have?
```

```
How many products are out of stock?
```

### Sum
```
What's the total revenue from all orders?
```

### Average
```
What's the average order value?
```

```
What's the average product price by category?
```

### Min/Max
```
What's the highest order value?
```

```
When was the first order placed?
```

## Grouping

### Group By with Count
```
How many orders per customer?
```

### Group By with Sum
```
What's the total revenue by product category?
```

### Group By with Multiple Aggregates
```
For each region, show me the number of customers and total revenue
```

## Joins

### Simple Join
```
Show me customer names with their order details
```

### Multiple Joins
```
List product names, categories, and supplier information
```

### Join with Aggregation
```
Show me customers and their total purchase amount
```

## Date Operations

### Relative Dates
```
Show me orders from the last 30 days
```

```
Which products were added this month?
```

### Date Ranges
```
Find orders between January and March 2024
```

### Date Grouping
```
Show me order count by month for this year
```

## Complex Queries

### Subqueries
```
Show me customers who have placed more orders than the average
```

### Top N with Details
```
Who are the top 5 customers by revenue and what did they buy?
```

### Multiple Conditions
```
Find high-value orders (over $500) from last quarter
```

### Ranking
```
Rank products by sales volume within each category
```

## Analytics Questions

### Trends
```
What's the monthly revenue trend for the past year?
```

### Comparisons
```
Compare this month's sales to last month
```

### Distribution
```
How are orders distributed across different regions?
```

### Percentages
```
What percentage of total revenue comes from each product category?
```

## Error Recovery Examples

### Ambiguous Question (Tests Agent Reasoning)
```
Show me the data
```
*Expected: Agent asks for clarification or shows sample from main table*

### Non-existent Table (Tests Error Handling)
```
Query the unicorns table
```
*Expected: Agent explains table doesn't exist and suggests alternatives*

### Complex Business Logic (Tests Multi-step Reasoning)
```
Which customers are at risk of churning based on their order frequency?
```
*Expected: Agent defines churn criteria and generates appropriate SQL*

## Custom Scenarios

Adapt these to your database schema:

### E-commerce
```
What products are frequently bought together?
Show me cart abandonment rate
Which products have the best conversion rate?
```

### HR/Employee Database
```
What's the average tenure of employees by department?
Show me hiring trends over the past 5 years
Which departments have the highest turnover?
```

### Financial
```
What's the month-over-month revenue growth?
Show me the top expense categories
Calculate profit margins by product line
```

### Healthcare
```
How many appointments were scheduled last month?
What's the average wait time by department?
Show me patient visit frequency distribution
```

### Manufacturing
```
Which products have the highest defect rate?
Show me inventory turnover by warehouse
What's the average production time by product type?
```

## Tips for Writing Good Questions

✅ **Be Specific**: "Show top 10 customers by revenue" vs "Show customers"  
✅ **Include Timeframes**: "Orders from last month" vs "Orders"  
✅ **Use Clear Metrics**: "Total revenue" vs "Money stuff"  
✅ **Specify Grouping**: "By category" or "By region"  
✅ **Set Limits**: "Top 10" or "First 20"  

## Testing Edge Cases

Try these to test robustness:

```
Show me everything in the database
(Tests: Row limits, table selection)

What happened yesterday?
(Tests: Date interpretation, event detection)

Find anomalies
(Tests: Statistical reasoning, anomaly definition)

Predict next month's sales
(Tests: Boundary of SQL capabilities, predictive vs. descriptive)
```

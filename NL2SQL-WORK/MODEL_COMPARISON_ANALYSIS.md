# Model Performance Comparison for NL2SQL Pipeline

## Test Query
**Question:** "show me distribution of customers over industries"  
**Date:** November 29, 2025  
**Database:** TERADATA-FI (aqsqlserver001.database.windows.net)

---

## Models Tested

1. **GPT-5-mini** (Azure OpenAI)
2. **GPT-4.1-mini** (Azure OpenAI)
3. **GPT-5.1-chat** (Azure OpenAI)

---

## Performance Metrics

| Model | Total Time | SQL Execution | Speed vs Fastest |
|-------|-----------|---------------|------------------|
| GPT-5-mini | 20.99 sec | 1091ms | **2.2x slower** |
| GPT-4.1-mini | 10.27 sec | 1057ms | 1.07x slower |
| GPT-5.1-chat | **9.59 sec** ⚡ | 1043ms | **Fastest** |

**Finding:** GPT-5.1-chat is 2x faster than GPT-5-mini for the same query.

---

## SQL Query Quality

### Generated Columns

| Model | Columns | Calculated Fields | NULL Handling |
|-------|---------|-------------------|---------------|
| GPT-5-mini | IndustryName, CustomerCount, **CustomerPercent** | ✅ Percentage | "Unknown" |
| GPT-4.1-mini | Industry, NumberOfCustomers | ❌ None | "None" |
| GPT-5.1-chat | Industry, CustomerCount | ❌ None | "None" |

**Winner:** GPT-5-mini (only model that added percentage calculation automatically)

### SQL Sophistication Ranking
1. 🥇 **GPT-5-mini** - Advanced (computed metrics)
2. 🥈 **GPT-5.1-chat** - Good (clean aggregation)
3. 🥉 **GPT-4.1-mini** - Basic (simple aggregation)

---

## Insights Quality Analysis

### GPT-5-mini Insights
```
✅ Quantitative focus: "Top 3 = ~51.7%", "8.5% Unknown"
✅ Portfolio analysis terminology
✅ Explicit data quality identification
✅ 3 detailed analytical points
```
**Style:** Academic, metrics-heavy, technical

### GPT-4.1-mini Insights
```
✅ Clear observations with numbers
✅ Mentions diverse customer base
✅ 5 bullet points (most verbose)
✅ Good structure
⚠️ Less analytical depth
```
**Style:** Structured, educational, thorough

### GPT-5.1-chat Insights
```
✅ Concise and direct
✅ 4 well-organized bullet points
✅ Mentions incomplete data
✅ Business-friendly language
⚠️ Less quantitative than 5-mini
```
**Style:** Conversational, clear, scannable

### Insights Ranking
1. 🥇 **GPT-5-mini** - Most analytical depth
2. 🥈 **GPT-5.1-chat** - Best clarity/conciseness balance
3. 🥉 **GPT-4.1-mini** - Thorough but verbose

---

## Follow-up Suggestions Comparison

### GPT-5-mini (2 suggestions)
1. **Technical/Data Quality Focus**
   - "Investigate Unknown group - can PrimaryIndustryId be populated?"
   - Suggests specific remediation actions

2. **Financial Analysis**
   - "Break down by revenue, loan volume, and default rate"
   - Lists multiple dimensions

**Strength:** Actionable, technical, data quality focused

### GPT-4.1-mini (3 suggestions)
1. Revenue/loan volume distribution by industry
2. Default rates/risk ratings across industries
3. **Trend over time** (only model to suggest temporal analysis)

**Strength:** Broadest exploration scope, includes time dimension

### GPT-5.1-chat (2 suggestions)
1. **Business Value Alignment**
   - "Analyze loan volume or revenue contribution by industry"
   - "See whether customer count aligns with financial value"

2. **Risk Assessment**
   - "Explore risk levels or default rates by industry"
   - "Assess portfolio concentration risk"

**Strength:** Business-focused, strategic perspective

### Suggestions Ranking
1. 🥇 **GPT-5.1-chat** - Best business relevance
2. 🥈 **GPT-5-mini** - Most actionable/technical
3. 🥉 **GPT-4.1-mini** - Broadest scope (includes temporal)

---

## Writing Style & User Experience

### Characteristics

| Aspect | GPT-5-mini | GPT-4.1-mini | GPT-5.1-chat |
|--------|------------|--------------|--------------|
| **Tone** | Academic | Educational | Conversational |
| **Length** | Moderate | Verbose | Concise |
| **Readability** | Dense | Detailed | **Scannable** ✅ |
| **Business Focus** | Technical | Balanced | **Strong** ✅ |
| **Chat UI Fit** | Good | Okay | **Excellent** ✅ |

**Winner:** GPT-5.1-chat (best for interactive chat interface)

---

## Overall Ranking by Use Case

### 🏆 For Interactive Chat UI (Gradio)
**Winner: GPT-5.1-chat**
- Fastest response (9.6s)
- Clearest writing style
- Business-focused insights
- Best user experience

### 📊 For Deep Analytics
**Winner: GPT-5-mini**
- Most sophisticated SQL
- Highest analytical depth
- Data quality focus
- Best calculated metrics

### 🔍 For Broad Exploration
**Winner: GPT-4.1-mini**
- Most suggestions (3)
- Includes temporal analysis
- Good for discovery

### ⚡ For Speed-Critical Applications
**Winner: GPT-5.1-chat**
- 9.59 seconds (fastest)
- 2x faster than 5-mini
- Good enough quality

---

## Recommendations

### Primary Recommendation: GPT-5.1-chat ⭐

**Use for:**
- ✅ Gradio chat interface (current setup)
- ✅ Interactive Q&A sessions
- ✅ Business user queries
- ✅ Quick data exploration
- ✅ When speed matters

**Advantages:**
- 2x faster than GPT-5-mini
- Best writing style for chat
- Business-friendly language
- Excellent follow-up suggestions

**Trade-offs:**
- No automatic percentage calculations
- Slightly less analytical depth

### Alternative: GPT-5-mini

**Use for:**
- ✅ Automated reports requiring calculated fields
- ✅ Data quality analysis
- ✅ Maximum analytical depth
- ✅ Technical/analytical users

**Advantages:**
- Best SQL query sophistication
- Most quantitative insights
- Data quality focused
- Portfolio analysis terminology

**Trade-offs:**
- 2x slower (20+ seconds)
- Denser writing style

### Alternative: GPT-4.1-mini

**Use for:**
- ✅ Exploratory analysis
- ✅ When temporal analysis is needed
- ✅ Cost-sensitive scenarios

**Advantages:**
- Good balance of speed/quality
- Broad suggestion scope
- Detailed explanations

**Trade-offs:**
- Most verbose output
- Less sophisticated SQL

---

## Configuration

### Current Setup (Gradio)
```bash
# In .env file
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.1-chat
```

### To Switch Models
```bash
# For maximum analytical depth
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-mini

# For broad exploration
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1-mini

# For best chat experience (recommended)
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.1-chat
```

---

## Test Results Summary

| Metric | GPT-5-mini | GPT-4.1-mini | GPT-5.1-chat |
|--------|------------|--------------|--------------|
| **Speed** | 🐌 (20.99s) | 🏃 (10.27s) | 🚀 (9.59s) |
| **SQL Quality** | 🥇 Advanced | 🥉 Basic | 🥈 Good |
| **Insights Depth** | 🥇 High | 🥉 Medium | 🥈 Good |
| **Conciseness** | 🥈 Good | 🥉 Verbose | 🥇 Excellent |
| **Business Focus** | 🥈 Technical | 🥈 Balanced | 🥇 Strong |
| **Chat UI Fit** | 🥈 Good | 🥉 Okay | 🥇 Excellent |

---

## Conclusion

**For the NL2SQL Gradio chat interface, GPT-5.1-chat is the optimal choice**, offering the best balance of:
- Response speed (critical for interactive chat)
- Writing clarity (important for user experience)
- Business relevance (valuable for financial insights)
- Good SQL quality (sufficient for most queries)

Switch to GPT-5-mini only when you need the most sophisticated SQL queries with calculated fields, or when maximum analytical depth is more important than response time.

---

## Test Environment

- **Date:** November 29, 2025
- **Database:** TERADATA-FI
- **Server:** aqsqlserver001.database.windows.net
- **Pipeline:** NL2SQL Gradio (nl2sql-gradio)
- **Query Type:** Aggregation with grouping
- **Result Set:** 11 rows (industry distribution)
- **Framework:** Microsoft Agent Framework
- **Interface:** Gradio Chat UI (port 7860)

---

## Files Referenced

- Test results: `workflow_outputs/nl2sql_results_20251129_*.txt`
- Configuration: `nl2sql-gradio/.env`
- Documentation: `NL2SQL_DEPLOYMENT_GUIDE.md`

# NL2SQL Pipeline - Deployment Guide

## Overview

Three production-ready NL2SQL implementations, each optimized for different use cases:

1. **nl2sql-pipeline** - DevUI with REST API (original, web-based)
2. **nl2sql-cli** - Command-line interface (no web server)
3. **nl2sql-gradio** - Interactive chat UI (best UX)

All three share the same core pipeline logic and are fully independent.

---

## Version Comparison

| Feature | nl2sql-pipeline | nl2sql-cli | nl2sql-gradio |
|---------|----------------|------------|---------------|
| **Interface** | DevUI Web + REST API | Command line | Gradio Chat UI |
| **Port** | 8097 | N/A | 7860 |
| **Best For** | API integration, team demos | Scripts, automation | Interactive queries |
| **Startup Time** | Slow (web server) | Fast | Fast |
| **Visualizations** | ✅ | ✅ | ✅ (inline) |
| **Exports** | ✅ CSV/Excel | ✅ CSV/Excel | ✅ CSV/Excel |
| **Session Support** | ✅ | ✅ | ✅ |
| **Auto-open Browser** | ✅ | ❌ | ✅ |
| **Suggested Follow-ups** | ❌ | ❌ | ✅ (clickable) |

---

## Quick Start Commands

### 1. DevUI Pipeline (Original)
```bash
cd nl2sql-pipeline
python nl2sql_workflow.py
# Opens http://localhost:8097
```

### 2. CLI Version
```bash
cd nl2sql-cli
python nl2sql_workflow.py "What are the top 10 customers by revenue?"

# With session for follow-ups
python nl2sql_workflow.py "Show me customers" session1
python nl2sql_workflow.py "What about their revenue?" session1
```

### 3. Gradio Chat UI (Recommended)
```bash
cd nl2sql-gradio
python app.py
# Opens http://localhost:7860

# Or use launcher
./launch.sh
```

---

## Configuration

All three versions share the same `.env` configuration:

### Required Environment Variables

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Database Connection
MSSQL_SERVER_NAME=yourserver.database.windows.net
MSSQL_DATABASE_NAME=YourDatabase
MSSQL_USERNAME=your_username
MSSQL_PASSWORD=your_password

# Optional: Tracing
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
# OR
OTLP_ENDPOINT=http://localhost:4318
# OR
ENABLE_CONSOLE_TRACING=true
```

### Copy `.env` Template
```bash
# Copy from pipeline to CLI
cp nl2sql-pipeline/.env nl2sql-cli/.env

# Copy from pipeline to Gradio
cp nl2sql-pipeline/.env nl2sql-gradio/.env
```

---

## Visualization Intelligence

All versions include smart chart selection:

| Query Type | Chart Type | Example Questions |
|------------|-----------|-------------------|
| **Rankings** | Horizontal Bar | "Top 10 customers by revenue" |
| **Time Series** | Line Chart | "Loan volume by month" |
| **Distributions** | Pie Chart | "Customer breakdown by tier" |
| **Matrix Data** | Heatmap | "Correlation matrix" (explicit only) |

### Chart Selection Logic

1. **Line Chart** - Time columns (date, month, year) or "trend" keywords
2. **Pie Chart** - "percentage", "proportion", "distribution" + ≤12 rows
3. **Horizontal Bar** - "top", "bottom", "rank", "by revenue" (most common)
4. **Heatmap** - "heatmap", "matrix", "correlation" + 4+ columns

---

## Gradio-Specific Features

### Suggested Follow-up Questions

After each query, the AI suggests relevant follow-ups:
- Automatically extracted from interpreter response
- Displayed in clickable dropdown
- One-click to ask follow-up

### Chat History

- Persists during browser session
- Clear button to reset
- Supports multi-turn conversations

### Session Support

Enter a session ID to maintain context across queries:
```
Session ID: customer_analysis_1
```

---

## File Structure

### Common Files (All Versions)
```
├── .env                    # Environment configuration
├── requirements.txt        # Python dependencies
├── nl2sql_workflow.py      # Core pipeline logic
├── executors.py           # Custom executors
├── db_utils.py            # Database utilities
├── schema_cache.py        # Schema caching
├── visualizer.py          # Chart generation
├── exports/               # CSV/Excel outputs
├── visualizations/        # Generated charts
└── workflow_outputs/      # Text results
```

### DevUI-Specific
```
nl2sql-pipeline/
└── (launches DevUI server with REST API)
```

### CLI-Specific
```
nl2sql-cli/
└── (direct command execution, no server)
```

### Gradio-Specific
```
nl2sql-gradio/
├── app.py                 # Gradio UI application
└── launch.sh              # Quick launcher script
```

---

## Troubleshooting

### Port Already in Use (Gradio)
```bash
# Kill process on port 7860
lsof -ti:7860 | xargs kill -9

# Then restart
cd nl2sql-gradio && python app.py
```

### Port Already in Use (DevUI)
```bash
# Kill process on port 8097
lsof -ti:8097 | xargs kill -9

# Then restart
cd nl2sql-pipeline && python nl2sql_workflow.py
```

### Virtual Environment Issues
```bash
# Ensure you're in the project root
cd /Users/arturoquiroga/GITHUB/agent-framework-public

# Activate venv
source .venv/bin/activate

# Verify Gradio installed
pip show gradio

# If missing
pip install gradio
```

### Database Connection Errors
```bash
# Test connection with CLI
cd nl2sql-cli
python nl2sql_workflow.py "SELECT TOP 1 * FROM dim.DimCustomer"

# Check .env settings
cat .env | grep MSSQL
```

---

## Deployment Options

### Local Development
Use Gradio for best UX:
```bash
cd nl2sql-gradio
python app.py
```

### Automation/Scripts
Use CLI for cron jobs or automation:
```bash
cd nl2sql-cli
python nl2sql_workflow.py "Daily revenue report" daily_$(date +%Y%m%d)
```

### Team Demos/API Access
Use DevUI for REST API and team access:
```bash
cd nl2sql-pipeline
python nl2sql_workflow.py
# Share http://localhost:8097 with team
```

### Production Deployment

**Gradio (Recommended for Users)**
```bash
# Run as background service
nohup python app.py > gradio.log 2>&1 &

# Or use Hugging Face Spaces (free hosting)
# Push nl2sql-gradio/ to HF Space
```

**DevUI (For API/Integration)**
```bash
# Run as background service
nohup python nl2sql_workflow.py > devui.log 2>&1 &

# Configure reverse proxy (nginx/caddy)
# for https://nl2sql.yourdomain.com
```

---

## Backup and Protection

### Create Backups
```bash
# From project root
tar -czf nl2sql-pipeline-backup-$(date +%Y%m%d).tar.gz nl2sql-pipeline/
tar -czf nl2sql-cli-backup-$(date +%Y%m%d).tar.gz nl2sql-cli/
tar -czf nl2sql-gradio-backup-$(date +%Y%m%d).tar.gz nl2sql-gradio/
```

### Git Protection
```bash
# Create a protection branch
git checkout -b protected/nl2sql-stable
git add nl2sql-pipeline/ nl2sql-cli/ nl2sql-gradio/
git commit -m "Protected: Working NL2SQL implementations"
git push origin protected/nl2sql-stable
```

---

## Performance Tips

### Cache Schema
All versions cache database schema in `.cache/` for faster queries.

### Limit Row Count
SQL Validator limits to 1000 rows by default (configurable in `executors.py`).

### Visualization Limits
- Bar charts: First 15 rows
- Pie charts: First 10 rows (≤12 categories)
- Heatmap: First 15 rows

---

## Example Queries

### Revenue Analysis
```
What are the top 10 customers by annual revenue?
Show me customers with lifetime revenue over $5 million
Which customer segments generate the most revenue?
```

### Loan Analysis
```
Show me the largest loans by volume
What's the total loan exposure by customer tier?
List customers with more than 20 active loans
```

### Time Series
```
What's the loan volume by month?
Show me loan origination trends by fiscal year
```

### Distributions
```
What's the distribution of customers by tier?
Show me the breakdown of revenue by customer segment
What percentage of customers are VIP?
```

---

## Support and Maintenance

### Regular Updates
- Check `requirements.txt` for dependency updates
- Test all three versions after major changes
- Backup before significant modifications

### Monitoring
- Check `workflow_outputs/` for query logs
- Monitor `exports/` disk usage
- Review `visualizations/` for chart quality

### Security
- Never commit `.env` files
- Rotate database credentials regularly
- Use read-only database accounts when possible
- Enable tracing in production for audit trails

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-28 | 1.0 | Initial three-version deployment |
| 2025-11-28 | 1.1 | Added Gradio chat UI with suggestions |
| 2025-11-28 | 1.2 | Improved visualization intelligence |

---

## Contact and Support

For questions or issues:
1. Check troubleshooting section above
2. Review logs in `workflow_outputs/`
3. Test with CLI version for debugging
4. Check database connectivity separately

**All three versions are production-ready and fully independent.**

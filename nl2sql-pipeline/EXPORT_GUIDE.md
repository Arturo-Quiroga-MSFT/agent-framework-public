# Export Functionality Guide

## 📊 Overview

The NL2SQL pipeline now automatically exports query results to **CSV** and **Excel** formats whenever a query returns data.

## ✨ Features

### Automatic Export
- **CSV Export**: Plain text format, universally compatible
- **Excel Export**: Rich formatting with:
  - Bold, colored headers (blue background, white text)
  - Auto-sized columns
  - Frozen header row for easy scrolling
  - User question included at the top of the sheet

### Export Location
All exports are saved to: `nl2sql-pipeline/exports/`

### File Naming
Files are named with timestamps for easy identification:
- `query_results_20251014_143052.csv`
- `query_results_20251014_143052.xlsx`

## 📁 File Formats

### CSV Format
```csv
# Question: What are the top 5 customers by revenue?
# Generated: query_results_20251014_143052
#
Customer ID,Company Name,Annual Revenue
CUST00058,Fleet Transportation Corp,62000000.00
CUST00844,Flores, Butler and Hernandez,26338402.00
```

### Excel Format
- **Row 1**: "User Question:" (bold)
- **Row 2**: The actual question (merged across all columns)
- **Row 4**: Column headers (bold, blue background, white text, centered)
- **Row 5+**: Data rows
- **Features**: 
  - Frozen header row
  - Auto-sized columns (max 50 characters)
  - Professional formatting

## 🔧 How It Works

### Workflow Integration

The `ResultsExporterExecutor` is integrated into the pipeline:

```
Query Execution → Results Interpreter → **Results Exporter** → Output Formatter
```

### What Gets Exported

- ✅ All rows returned by the query (not limited to the 10 shown in the UI)
- ✅ All columns with proper headers
- ✅ Original user question (as metadata)
- ✅ Formatted values (dates, decimals, etc.)

### Export Confirmation

After each successful export, you'll see a message in the results:

```
📊 **Export Complete**

Results have been saved to:
- CSV: `exports/query_results_20251014_143052.csv`
- Excel: `exports/query_results_20251014_143052.xlsx`

Total rows exported: 157
```

## 💡 Usage Tips

### 1. Open Exports in Excel
```bash
# macOS
open exports/query_results_20251014_143052.xlsx

# Windows
start exports/query_results_20251014_143052.xlsx

# Linux
xdg-open exports/query_results_20251014_143052.xlsx
```

### 2. Import CSV into Other Tools

**Python/Pandas:**
```python
import pandas as pd
df = pd.read_csv('exports/query_results_20251014_143052.csv', comment='#')
```

**R:**
```r
df <- read.csv('exports/query_results_20251014_143052.csv', comment.char='#')
```

**SQL Database:**
```sql
BULK INSERT MyTable
FROM 'exports/query_results_20251014_143052.csv'
WITH (FORMAT = 'CSV', FIRSTROW = 4);  -- Skip comment lines
```

### 3. Share Results

CSV and Excel files can be:
- Emailed to stakeholders
- Uploaded to SharePoint/OneDrive
- Imported into BI tools (Power BI, Tableau, etc.)
- Used in reports and presentations

## 🎨 Excel Formatting Customization

To customize Excel formatting, edit `executors.py` → `ResultsExporterExecutor._export_to_excel()`:

```python
# Change header color
cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

# Change to green:
cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
```

## 🔒 Security Considerations

### Data Sensitivity
- Exports contain the actual query results from your database
- Review data classification before sharing
- Consider encrypting exports for sensitive data

### Retention Policy
- Exports accumulate in the `exports/` folder
- Implement a cleanup policy if needed:

```bash
# Delete exports older than 30 days
find exports/ -name "*.csv" -mtime +30 -delete
find exports/ -name "*.xlsx" -mtime +30 -delete
```

## 🐛 Troubleshooting

### Issue: "openpyxl not installed - Excel export skipped"

**Solution:**
```bash
pip install openpyxl
# or
.venv/bin/pip install openpyxl
```

### Issue: Excel file won't open

**Possible causes:**
1. File is being used by another program
2. Insufficient disk space
3. File path contains special characters

**Solution:**
- Close the file if it's open
- Check disk space: `df -h` (Linux/macOS) or `dir` (Windows)
- Rename the file if path contains special characters

### Issue: CSV has wrong encoding

**Solution:**
Exports use UTF-8 encoding. If you see garbled characters:

**Excel:**
1. Open Excel → Data → From Text/CSV
2. Select UTF-8 encoding
3. Import

**Python:**
```python
pd.read_csv('file.csv', encoding='utf-8')
```

## 📈 Performance Notes

- **Export time**: ~100ms for 1,000 rows
- **File size**: 
  - CSV: ~100 KB per 1,000 rows (varies by data)
  - Excel: ~150 KB per 1,000 rows (includes formatting)
- **Memory usage**: Minimal (streaming writes)

## 🚀 Advanced Features (Future Enhancements)

Potential additions:
- [ ] Export to JSON format
- [ ] Parquet format for big data
- [ ] Cloud storage integration (Azure Blob, S3)
- [ ] Email results automatically
- [ ] Custom export templates
- [ ] Compression (ZIP) for large exports
- [ ] Export history tracking
- [ ] Scheduled/batch exports

## 📚 Related Documentation

- [Database Setup Guide](DATABASE_SETUP.md)
- [Workflow README](README.md)
- [Main Project README](../README.md)

---

**Questions or Issues?** Check the [troubleshooting section](#-troubleshooting) or review the code in `executors.py`.

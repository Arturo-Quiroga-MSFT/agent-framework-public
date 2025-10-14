# Data Visualization Guide

## Overview

The NL2SQL pipeline now includes **automatic data visualization** that generates charts for query results when appropriate. The system intelligently determines whether visualization would be helpful and creates the most suitable chart type.

## Features

### ✨ Automatic Chart Generation
- **Smart Detection**: Automatically identifies when results would benefit from visualization
- **Chart Type Selection**: Chooses the best chart type based on data structure and user question
- **Multiple Formats**: Horizontal bar charts, line charts, pie charts, and heatmaps
- **Beautiful Styling**: Professional-looking charts with proper formatting

### 📊 Supported Chart Types

#### 1. Horizontal Bar Charts (Default)
**Best for**: Rankings, comparisons, top N queries, long category names

**Triggered by keywords**:
- "top", "bottom", "highest", "lowest"
- "compare", "rank", "most", "least"
- Default for most categorical data

**Example questions**:
- "What are the top 10 customers by revenue?"
- "Show me the highest selling products"
- "Compare sales by region"

**Features**:
- Better readability for long labels
- Values shown on the right of each bar
- Automatically sized based on number of items

#### 2. Line Charts
**Best for**: Time series, trends over time

**Triggered by keywords**:
- "trend", "over time", "history"
- "by month", "by year", "by quarter"

**Triggered by column names**:
- Columns containing: "date", "month", "year", "quarter", "day", "time"

**Example questions**:
- "Show me revenue trends over the last 6 months"
- "What is the order history by quarter?"
- "How have sales changed year over year?"

#### 3. Pie Charts
**Best for**: Proportions, distributions, breakdowns

**Triggered by keywords**:
- "percentage", "proportion", "distribution"
- "breakdown", "share"

**Limitations**: Works best with ≤12 categories

**Example questions**:
- "What is the revenue breakdown by product category?"
- "Show me the market share distribution"
- "What percentage of orders come from each region?"

#### 4. Heatmaps (NEW!)
**Best for**: Matrix data, cross-tabulations, correlations

**Triggered by keywords**:
- "heatmap", "heat map", "matrix"
- "correlation", "by X and Y" (cross-tabulation patterns)

**Requirements**: 
- At least 3 columns
- At least 2 numeric columns OR 2 categorical + 1 numeric

**Example questions**:
- "Show me sales by region and product category as a heatmap"
- "What's the correlation between customer segment and loan amount?"
- "Display revenue by industry and region"

**Features**:
- Color-coded intensity (yellow to red)
- Annotated values in each cell
- Automatic pivot table creation for cross-tabs

## How It Works

### Pipeline Integration

The visualization step is integrated into the workflow between results interpretation and export:

```
Query Execution
    ↓
Results Interpretation (AI explains results)
    ↓
📊 Visualization (Create chart if applicable)
    ↓
Export (CSV/Excel)
    ↓
Output Formatting
```

### Visualization Logic

1. **Check Suitability**: 
   - Must have ≥2 rows and ≥2 columns
   - Must contain at least one numeric column
   
2. **Determine Chart Type**:
   - Analyze user question keywords
   - Check column names for time indicators
   - Consider data structure
   
3. **Create Chart**:
   - Extract category and value columns
   - Apply appropriate styling
   - Add labels and formatting
   - Save to `visualizations/` directory

### Output Location

All charts are saved to:
```
nl2sql-pipeline/visualizations/chart_{timestamp}.png
```

Example filename: `chart_20251014_143022.png`

## Configuration

### Enable/Disable Visualization

Visualization is enabled by default. To disable it:

1. **Remove from workflow**: Edit `nl2sql_workflow.py` and comment out the visualization step
2. **Skip on errors**: The system gracefully falls back if matplotlib/seaborn aren't installed

### Customize Chart Appearance

Edit `visualizer.py` to customize:

```python
# Chart size
plt.rcParams['figure.figsize'] = (12, 6)  # Width, height in inches

# Style theme
sns.set_style("whitegrid")  # Options: whitegrid, darkgrid, white, dark, ticks

# Color schemes
colors = plt.cm.viridis(range(len(categories)))  # Try: viridis, plasma, inferno, Set3
```

### Adjust Data Limits

By default, charts are limited for readability:
- Bar charts: First 15 items
- Pie charts: First 10 items
- Category labels: Truncated to 30 characters
- Value labels: Truncated to 20 characters

Modify in `visualizer.py`:
```python
# Bar chart limit
display_rows = rows[:15]  # Change 15 to your preference

# Pie chart limit
display_rows = rows[:10]  # Change 10 to your preference
```

## Examples

### Example 1: Top Customers (Bar Chart)

**Question**: "What are the top 10 customers by annual revenue?"

**Chart Generated**:
- Type: Bar chart
- X-axis: Customer names
- Y-axis: Annual revenue
- Features: Value labels on bars, gradient colors

**Output**:
```
📊 Visualization Created

Chart saved to: visualizations/chart_20251014_143022.png

The chart visualizes the query results in a format that makes 
patterns and insights easier to understand.
```

### Example 2: Monthly Trends (Line Chart)

**Question**: "Show me order counts by month for 2024"

**Chart Generated**:
- Type: Line chart
- X-axis: Months
- Y-axis: Order count
- Features: Markers on data points, gridlines

### Example 3: Revenue Distribution (Pie Chart)

**Question**: "What is the revenue distribution by product category?"

**Chart Generated**:
- Type: Pie chart
- Segments: Product categories
- Labels: Category names with percentages
- Features: Colorful segments, percentage labels

## Viewing Charts

### In Workflow Results

Charts are mentioned in the workflow output file:
```
📊 Visualization Created

Chart saved to: visualizations/chart_20251014_143022.png
```

### Opening Charts

**Option 1**: Navigate to folder and open
```bash
cd nl2sql-pipeline/visualizations
open chart_20251014_143022.png  # macOS
```

**Option 2**: Use VS Code
- Navigate to `nl2sql-pipeline/visualizations/`
- Click on the PNG file to preview

**Option 3**: In Python
```python
from PIL import Image
import matplotlib.pyplot as plt

img = Image.open('visualizations/chart_20251014_143022.png')
plt.imshow(img)
plt.axis('off')
plt.show()
```

## Dependencies

### Required Libraries
```bash
pip install matplotlib seaborn pandas
```

### Optional Enhancement
```bash
pip install pillow  # For better image handling
```

## Troubleshooting

### Issue: No Chart Generated

**Symptoms**: Results returned but no visualization message

**Possible causes**:
1. **Data not suitable**: Fewer than 2 rows/columns or no numeric data
2. **Question type**: Query doesn't match visualization keywords
3. **Error occurred**: Check logs for warnings

**Solutions**:
- Ensure query returns tabular data with numbers
- Use visualization-friendly keywords ("top 10", "trend", "distribution")
- Check terminal logs for error messages

### Issue: Import Error

**Symptoms**:
```
WARNING: matplotlib/seaborn not installed - visualization skipped
```

**Solution**:
```bash
source .venv/bin/activate
pip install matplotlib seaborn
```

### Issue: Chart Looks Wrong

**Possible causes**:
1. **Too many categories**: Bar/pie charts with >15 items become cluttered
2. **Wrong chart type**: System chose inappropriate chart for data
3. **Data format**: Non-numeric values in value column

**Solutions**:
- Limit query results: "TOP 10" or "TOP 15"
- Rephrase question with specific chart keywords
- Ensure numeric columns are properly formatted

### Issue: Charts Not Saving

**Symptoms**: Visualization step runs but no file created

**Check**:
1. **Directory permissions**: Ensure `visualizations/` is writable
2. **Disk space**: Ensure sufficient space available
3. **File path**: Check logs for actual save location

**Solution**:
```bash
# Create directory manually with correct permissions
mkdir -p nl2sql-pipeline/visualizations
chmod 755 nl2sql-pipeline/visualizations
```

## Performance

### Chart Generation Time
- **Typical**: 100-300ms per chart
- **Large datasets**: 500ms - 1s for complex charts

### Resource Usage
- **Memory**: ~50-100MB for matplotlib/seaborn
- **Disk**: ~50-200KB per PNG file

## Best Practices

### 1. Limit Result Sets
For best visualization quality:
```sql
SELECT TOP 10 ...  -- Bar charts
SELECT TOP 8 ...   -- Pie charts
```

### 2. Use Descriptive Questions
Include keywords that indicate chart type:
- ✅ "Show me the **top 10** customers by revenue"
- ✅ "What is the **trend** in monthly sales?"
- ✅ "Display the **distribution** of orders by region"

### 3. Keep Category Names Short
Long names get truncated:
- ✅ "West", "East", "North", "South"
- ⚠️ "Western Regional Sales District #3"

### 4. Clean Data
Ensure data is properly formatted:
- Numeric values should be numbers (not strings with "$" or ",")
- Dates should be in consistent format
- No NULL values in key columns

## Advanced Customization

### Custom Color Schemes

Edit `visualizer.py`:
```python
# For bar charts
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Custom colors

# For pie charts
colors = plt.cm.Pastel1(range(len(labels)))  # Softer colors
```

### Add Annotations

Enhance charts with additional information:
```python
# Add average line to bar chart
ax.axhline(y=avg_value, color='r', linestyle='--', label='Average')
ax.legend()

# Add data source footer
fig.text(0.99, 0.01, f'Source: {database_name}', 
         ha='right', fontsize=8, alpha=0.5)
```

### Export Different Formats

Modify save format:
```python
# High-resolution PNG
plt.savefig(filepath, dpi=300, bbox_inches='tight')

# Vector format (scalable)
plt.savefig(filepath.replace('.png', '.svg'), format='svg')

# PDF for reports
plt.savefig(filepath.replace('.png', '.pdf'), format='pdf')
```

## Integration with Exports

Charts are created **before** CSV/Excel export, so:
- Chart path can be referenced in export files
- Charts and exports share the same timestamp
- Both can be packaged together for reporting

### Future Enhancement Ideas
- Embed charts in Excel exports
- Generate multi-chart dashboards
- Interactive charts with Plotly
- Automatic chart recommendations

## Summary

The visualization feature adds powerful visual insights to your NL2SQL pipeline:
- ✅ Automatic and intelligent
- ✅ Multiple chart types
- ✅ Professional styling
- ✅ Non-blocking (fails gracefully)
- ✅ Configurable and extensible

Questions with numeric results are now more intuitive and actionable!

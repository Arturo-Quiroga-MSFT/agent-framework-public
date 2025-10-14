# Copyright (c) Microsoft. All rights reserved.
"""
Data Visualization Module

Automatically generates charts for query results when appropriate.

Supported chart types:
- Bar charts (comparisons, rankings)
- Line charts (trends over time)
- Pie charts (proportions, distributions)
- Scatter plots (correlations)
"""
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class QueryResultsVisualizer:
    """Creates visualizations from SQL query results."""
    
    def __init__(self, output_dir: str = "visualizations"):
        """Initialize visualizer.
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def should_visualize(self, results: dict) -> bool:
        """Determine if results are suitable for visualization.
        
        Args:
            results: Query results with columns and rows
            
        Returns:
            True if visualization would be useful
        """
        rows = results.get("rows", [])
        columns = results.get("columns", [])
        
        # Need at least 2 rows and 2 columns
        if len(rows) < 2 or len(columns) < 2:
            return False
        
        # Check if we have numeric data
        has_numeric = self._has_numeric_columns(rows, columns)
        
        return has_numeric
    
    def _has_numeric_columns(self, rows: list[dict], columns: list[dict]) -> bool:
        """Check if results contain numeric columns."""
        if not rows or not columns:
            return False
        
        column_names = [col.get("name", "") for col in columns]
        first_row = rows[0]
        
        for col_name in column_names:
            value = first_row.get(col_name)
            try:
                # Try to convert to float
                float(str(value).replace(",", "").replace("$", ""))
                return True
            except (ValueError, TypeError, AttributeError):
                continue
        
        return False
    
    def create_visualization(
        self,
        results: dict,
        user_question: str,
        timestamp: str,
    ) -> Optional[str]:
        """Create appropriate visualization for the results.
        
        Args:
            results: Query results with columns and rows
            user_question: Original user question for context
            timestamp: Timestamp for filename
            
        Returns:
            Path to generated chart file, or None if visualization not applicable
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Set style
            sns.set_style("whitegrid")
            plt.rcParams['figure.figsize'] = (12, 6)
            
        except ImportError:
            logger.warning("matplotlib/seaborn not installed - visualization skipped")
            return None
        
        if not self.should_visualize(results):
            logger.info("Results not suitable for visualization")
            return None
        
        rows = results["rows"]
        columns = results["columns"]
        column_names = [col.get("name", "") for col in columns]
        
        # Analyze data structure
        chart_type = self._determine_chart_type(rows, column_names, user_question)
        
        # Create chart based on type
        if chart_type == "bar":
            chart_path = self._create_bar_chart(rows, column_names, user_question, timestamp)
        elif chart_type == "line":
            chart_path = self._create_line_chart(rows, column_names, user_question, timestamp)
        elif chart_type == "pie":
            chart_path = self._create_pie_chart(rows, column_names, user_question, timestamp)
        else:
            logger.info(f"No suitable chart type determined")
            return None
        
        logger.info(f"📊 Visualization created: {chart_path}")
        return str(chart_path)
    
    def _determine_chart_type(
        self,
        rows: list[dict],
        column_names: list[str],
        user_question: str,
    ) -> str:
        """Determine the best chart type for the data.
        
        Args:
            rows: Data rows
            column_names: Column names
            user_question: User's question for context
            
        Returns:
            Chart type: "bar", "line", "pie", or "none"
        """
        question_lower = user_question.lower()
        
        # Pie chart keywords
        if any(word in question_lower for word in ["percentage", "proportion", "distribution", "breakdown", "share"]):
            if len(rows) <= 10:  # Pie charts work best with fewer categories
                return "pie"
        
        # Line chart keywords (time series)
        if any(word in question_lower for word in ["trend", "over time", "by month", "by year", "by quarter", "history"]):
            return "line"
        
        # Check for date/time columns
        for col_name in column_names:
            if any(word in col_name.lower() for word in ["date", "month", "year", "quarter", "day", "time"]):
                return "line"
        
        # Default to bar chart for rankings, comparisons, top N
        if any(word in question_lower for word in ["top", "bottom", "highest", "lowest", "compare", "rank", "most", "least"]):
            return "bar"
        
        # Default to bar chart for general categorical data
        return "bar"
    
    def _identify_columns(self, rows: list[dict], column_names: list[str]) -> tuple[str, str]:
        """Identify category and value columns.
        
        Returns:
            (category_column, value_column)
        """
        # Find numeric column for values
        value_col = None
        first_row = rows[0]
        
        for col_name in column_names:
            value = first_row.get(col_name)
            try:
                float(str(value).replace(",", "").replace("$", ""))
                value_col = col_name
                break
            except (ValueError, TypeError, AttributeError):
                continue
        
        # Find text column for categories (use first non-value column)
        category_col = None
        for col_name in column_names:
            if col_name != value_col:
                category_col = col_name
                break
        
        return category_col, value_col
    
    def _create_bar_chart(
        self,
        rows: list[dict],
        column_names: list[str],
        user_question: str,
        timestamp: str,
    ) -> Path:
        """Create a bar chart."""
        import matplotlib.pyplot as plt
        
        category_col, value_col = self._identify_columns(rows, column_names)
        
        # Extract data (limit to first 15 for readability)
        display_rows = rows[:15]
        categories = [str(row.get(category_col, ""))[:30] for row in display_rows]
        values = []
        
        for row in display_rows:
            val = row.get(value_col, 0)
            try:
                values.append(float(str(val).replace(",", "").replace("$", "")))
            except (ValueError, TypeError):
                values.append(0)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create bars with gradient color
        bars = ax.bar(range(len(categories)), values, color=plt.cm.viridis(range(len(categories))))
        
        # Customize
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_xlabel(category_col or "Category")
        ax.set_ylabel(value_col or "Value")
        ax.set_title(f"{user_question}\n", fontsize=12, fontweight='bold')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}',
                   ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        # Save
        filename = f"chart_{timestamp}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _create_line_chart(
        self,
        rows: list[dict],
        column_names: list[str],
        user_question: str,
        timestamp: str,
    ) -> Path:
        """Create a line chart for time series data."""
        import matplotlib.pyplot as plt
        
        category_col, value_col = self._identify_columns(rows, column_names)
        
        # Extract data
        categories = [str(row.get(category_col, "")) for row in rows]
        values = []
        
        for row in rows:
            val = row.get(value_col, 0)
            try:
                values.append(float(str(val).replace(",", "").replace("$", "")))
            except (ValueError, TypeError):
                values.append(0)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot line with markers
        ax.plot(range(len(categories)), values, marker='o', linewidth=2, markersize=6)
        
        # Customize
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_xlabel(category_col or "Time Period")
        ax.set_ylabel(value_col or "Value")
        ax.set_title(f"{user_question}\n", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        filename = f"chart_{timestamp}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _create_pie_chart(
        self,
        rows: list[dict],
        column_names: list[str],
        user_question: str,
        timestamp: str,
    ) -> Path:
        """Create a pie chart for proportional data."""
        import matplotlib.pyplot as plt
        
        category_col, value_col = self._identify_columns(rows, column_names)
        
        # Extract data (limit to top 10 for readability)
        display_rows = rows[:10]
        labels = [str(row.get(category_col, ""))[:20] for row in display_rows]
        values = []
        
        for row in display_rows:
            val = row.get(value_col, 0)
            try:
                values.append(float(str(val).replace(",", "").replace("$", "")))
            except (ValueError, TypeError):
                values.append(0)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create pie chart
        colors = plt.cm.Set3(range(len(labels)))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        # Improve text readability
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title(f"{user_question}\n", fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        # Save
        filename = f"chart_{timestamp}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath

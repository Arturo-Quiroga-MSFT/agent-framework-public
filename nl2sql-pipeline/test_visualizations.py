#!/usr/bin/env python3
"""
Test script for data visualization functionality.

This script tests the visualization module independently.
"""
from visualizer import QueryResultsVisualizer
from datetime import datetime

# Mock query results for testing
def test_bar_chart():
    """Test bar chart generation with top customers data."""
    results = {
        "columns": [
            {"name": "CustomerName"},
            {"name": "TotalRevenue"}
        ],
        "rows": [
            {"CustomerName": "ABC Corp", "TotalRevenue": 125000},
            {"CustomerName": "XYZ Inc", "TotalRevenue": 98000},
            {"CustomerName": "Tech Solutions", "TotalRevenue": 87500},
            {"CustomerName": "Global Industries", "TotalRevenue": 76000},
            {"CustomerName": "Digital Systems", "TotalRevenue": 65000},
            {"CustomerName": "Innovation Labs", "TotalRevenue": 54000},
            {"CustomerName": "Smart Tech", "TotalRevenue": 48000},
            {"CustomerName": "Future Corp", "TotalRevenue": 42000},
            {"CustomerName": "Data Dynamics", "TotalRevenue": 38000},
            {"CustomerName": "Cloud Services", "TotalRevenue": 32000},
        ]
    }
    
    visualizer = QueryResultsVisualizer()
    user_question = "What are the top 10 customers by total revenue?"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Testing bar chart generation...")
    chart_path = visualizer.create_visualization(results, user_question, timestamp)
    
    if chart_path:
        print(f"✅ Bar chart created: {chart_path}")
        return True
    else:
        print("❌ Bar chart failed")
        return False


def test_line_chart():
    """Test line chart generation with time series data."""
    results = {
        "columns": [
            {"name": "Month"},
            {"name": "OrderCount"}
        ],
        "rows": [
            {"Month": "Jan 2024", "OrderCount": 245},
            {"Month": "Feb 2024", "OrderCount": 278},
            {"Month": "Mar 2024", "OrderCount": 312},
            {"Month": "Apr 2024", "OrderCount": 289},
            {"Month": "May 2024", "OrderCount": 325},
            {"Month": "Jun 2024", "OrderCount": 341},
            {"Month": "Jul 2024", "OrderCount": 356},
            {"Month": "Aug 2024", "OrderCount": 332},
            {"Month": "Sep 2024", "OrderCount": 318},
        ]
    }
    
    visualizer = QueryResultsVisualizer()
    user_question = "Show me order count trends by month"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Testing line chart generation...")
    chart_path = visualizer.create_visualization(results, user_question, timestamp)
    
    if chart_path:
        print(f"✅ Line chart created: {chart_path}")
        return True
    else:
        print("❌ Line chart failed")
        return False


def test_pie_chart():
    """Test pie chart generation with distribution data."""
    results = {
        "columns": [
            {"name": "Region"},
            {"name": "SalesAmount"}
        ],
        "rows": [
            {"Region": "North", "SalesAmount": 450000},
            {"Region": "South", "SalesAmount": 380000},
            {"Region": "East", "SalesAmount": 520000},
            {"Region": "West", "SalesAmount": 410000},
            {"Region": "Central", "SalesAmount": 290000},
        ]
    }
    
    visualizer = QueryResultsVisualizer()
    user_question = "What is the sales distribution by region?"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Testing pie chart generation...")
    chart_path = visualizer.create_visualization(results, user_question, timestamp)
    
    if chart_path:
        print(f"✅ Pie chart created: {chart_path}")
        return True
    else:
        print("❌ Pie chart failed")
        return False


def test_no_visualization():
    """Test that non-numeric data doesn't trigger visualization."""
    results = {
        "columns": [
            {"name": "Name"},
            {"name": "Description"}
        ],
        "rows": [
            {"Name": "Item A", "Description": "Sample description A"},
            {"Name": "Item B", "Description": "Sample description B"},
        ]
    }
    
    visualizer = QueryResultsVisualizer()
    user_question = "List all items"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Testing no-visualization case...")
    chart_path = visualizer.create_visualization(results, user_question, timestamp)
    
    if chart_path is None:
        print(f"✅ Correctly skipped visualization for text-only data")
        return True
    else:
        print("❌ Should not have created visualization")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Data Visualization Module")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(test_bar_chart())
    print()
    
    results.append(test_line_chart())
    print()
    
    results.append(test_pie_chart())
    print()
    
    results.append(test_no_visualization())
    print()
    
    print("=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✅ All visualization tests passed!")
        print("\nCheck the visualizations/ directory for generated charts.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")

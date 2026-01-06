#!/usr/bin/env python3
"""Quick diagnostic to check what tables exist in Application Insights and what data is there."""

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient

# Load .env
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

app_insights_resource_id = os.environ.get("APPLICATIONINSIGHTS_RESOURCE_ID")
workspace_id = os.environ.get("LOG_ANALYTICS_WORKSPACE_ID")

if not app_insights_resource_id and not workspace_id:
    print("❌ No APPLICATIONINSIGHTS_RESOURCE_ID or LOG_ANALYTICS_WORKSPACE_ID set")
    exit(1)

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

# List of common tables to check
tables_to_check = [
    "AppDependencies",
    "AppTraces", 
    "AppRequests",
    "dependencies",
    "traces",
    "requests",
]

print(f"🔍 Checking tables in Application Insights...")
print(f"   Resource ID: {app_insights_resource_id[:80]}..." if app_insights_resource_id else f"   Workspace ID: {workspace_id}")
print()

for table in tables_to_check:
    query = f"{table} | take 1"
    
    try:
        if app_insights_resource_id:
            response = client.query_resource(
                resource_id=app_insights_resource_id,
                query=query,
                timespan=timedelta(days=1)
            )
        else:
            response = client.query_workspace(
                workspace_id=workspace_id,
                query=query,
                timespan=timedelta(days=1)
            )
        
        print(f"✅ {table} - EXISTS and has data")
        
        # Show column names
        if response.tables and response.tables[0].columns:
            cols = [col.name for col in response.tables[0].columns]
            print(f"   Columns: {', '.join(cols[:10])}")
            
    except Exception as e:
        if "Failed to resolve table" in str(e):
            print(f"❌ {table} - does not exist")
        else:
            print(f"⚠️  {table} - error: {str(e)[:100]}")

print("\n🔍 Checking for agent framework traces...")

# Check for agent framework specific data
queries = [
    ("AppTraces with 'agent'", "AppTraces | where TimeGenerated >= ago(1h) | where Message contains 'agent' | take 5"),
    ("dependencies table", "dependencies | where timestamp >= ago(1h) | take 5"),
    ("traces table", "traces | where timestamp >= ago(1h) | take 5"),
]

for name, query in queries:
    try:
        if app_insights_resource_id:
            response = client.query_resource(
                resource_id=app_insights_resource_id,
                query=query,
                timespan=timedelta(hours=1)
            )
        else:
            response = client.query_workspace(
                workspace_id=workspace_id,
                query=query,
                timespan=timedelta(hours=1)
            )
        
        if response.tables and response.tables[0].rows:
            print(f"✅ {name} - found {len(response.tables[0].rows)} rows")
        else:
            print(f"⚠️  {name} - table exists but no data")
            
    except Exception as e:
        print(f"❌ {name} - error: {str(e)[:80]}")

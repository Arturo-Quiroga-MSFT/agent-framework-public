#!/usr/bin/env python3
"""
Test Database Connection

Simple script to verify Azure SQL Database connection
before running the full NL2SQL workflow.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection and retrieve basic info."""
    print("=" * 70)
    print("🔍 Testing Azure SQL Database Connection")
    print("=" * 70)
    print()
    
    # Check environment variables
    server = os.environ.get("MSSQL_SERVER_NAME")
    database = os.environ.get("MSSQL_DATABASE_NAME")
    username = os.environ.get("MSSQL_USERNAME")
    password = os.environ.get("MSSQL_PASSWORD")
    auth_type = os.environ.get("MSSQL_AUTHENTICATION_TYPE", "SqlPassword")
    
    print("📋 Configuration:")
    print(f"   Server: {server}")
    print(f"   Database: {database}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
    print(f"   Auth Type: {auth_type}")
    print()
    
    if not all([server, database, username, password]):
        print("❌ Error: Missing required configuration")
        print()
        print("Please set the following in your .env file:")
        if not server:
            print("  - MSSQL_SERVER_NAME")
        if not database:
            print("  - MSSQL_DATABASE_NAME")
        if not username:
            print("  - MSSQL_USERNAME")
        if not password:
            print("  - MSSQL_PASSWORD")
        return False
    
    try:
        from db_utils import DatabaseConnection
        
        print("🔌 Connecting to database...")
        db = DatabaseConnection(
            server=server,
            database=database,
            username=username,
            password=password,
            authentication_type=auth_type,
        )
        
        # Test connection
        with db:
            print("✅ Connection successful!")
            print()
            
            # Test simple query
            print("📊 Running test query...")
            result = db.execute_query("SELECT @@VERSION AS SqlVersion")
            
            if result["row_count"] > 0:
                version = result["data"][0]["SqlVersion"]
                print(f"✅ SQL Server Version: {version[:100]}...")
                print()
            
            # Get schema info
            print("🗂️  Retrieving schema information...")
            schema = db.get_schema_info()
            
            print(f"✅ Found {len(schema)} tables:")
            print()
            
            for i, (table_name, table_info) in enumerate(schema.items(), 1):
                col_count = len(table_info["columns"])
                print(f"   {i}. {table_name} ({col_count} columns)")
                
                # Show first 3 columns as example
                for j, col in enumerate(table_info["columns"][:3], 1):
                    col_type = col["data_type"]
                    if 'max_length' in col:
                        col_type += f"({col['max_length']})"
                    elif 'precision' in col:
                        col_type += f"({col['precision']}"
                        if 'scale' in col:
                            col_type += f",{col['scale']}"
                        col_type += ")"
                    nullable = "NULL" if col["nullable"] else "NOT NULL"
                    print(f"      - {col['name']}: {col_type} {nullable}")
                
                if col_count > 3:
                    print(f"      ... and {col_count - 3} more columns")
                print()
        
        print("=" * 70)
        print("✅ Database Connection Test PASSED")
        print("=" * 70)
        print()
        print("Your database is ready for NL2SQL queries!")
        print("Run: python nl2sql_workflow.py")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print()
        print("Common issues:")
        print("  1. Firewall: Ensure your IP is allowed in Azure SQL firewall rules")
        print("  2. Credentials: Verify username and password are correct")
        print("  3. Network: Check if you can reach the server")
        print("  4. Driver: Ensure ODBC Driver 18 for SQL Server is installed")
        print()
        print("To install ODBC Driver:")
        print("  - macOS: brew install msodbcsql18 mssql-tools18")
        print("  - Linux: See https://learn.microsoft.com/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server")
        print("  - Windows: Usually pre-installed")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

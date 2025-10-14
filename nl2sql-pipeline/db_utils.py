# Copyright (c) Microsoft. All rights reserved.
"""
Database Utilities for NL2SQL Pipeline

Provides connection management and query execution for Azure SQL Database.
Supports both SQL authentication and Azure Active Directory authentication.
"""
import logging
import os
from typing import Any

import pyodbc

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages Azure SQL Database connections and query execution."""
    
    def __init__(
        self,
        server: str,
        database: str,
        username: str | None = None,
        password: str | None = None,
        authentication_type: str = "SqlPassword",
        timeout: int = 30,
    ):
        """Initialize database connection parameters.
        
        Args:
            server: SQL Server hostname (e.g., server.database.windows.net)
            database: Database name
            username: SQL username (required for SQL auth)
            password: SQL password (required for SQL auth)
            authentication_type: Auth type - "SqlPassword" or "ActiveDirectoryDefault"
            timeout: Query timeout in seconds
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.authentication_type = authentication_type
        self.timeout = timeout
        self._connection = None
    
    def _build_connection_string(self) -> str:
        """Build ODBC connection string based on authentication type."""
        # Base connection string
        conn_str_parts = [
            f"DRIVER={{ODBC Driver 18 for SQL Server}}",
            f"SERVER={self.server}",
            f"DATABASE={self.database}",
            f"Encrypt=yes",
            f"TrustServerCertificate=no",
            f"Connection Timeout={self.timeout}",
        ]
        
        # Add authentication based on type
        if self.authentication_type == "SqlPassword":
            if not self.username or not self.password:
                raise ValueError("Username and password required for SQL authentication")
            conn_str_parts.extend([
                f"UID={self.username}",
                f"PWD={self.password}",
            ])
        elif self.authentication_type == "ActiveDirectoryDefault":
            conn_str_parts.append("Authentication=ActiveDirectoryDefault")
        else:
            raise ValueError(f"Unsupported authentication type: {self.authentication_type}")
        
        return ";".join(conn_str_parts)
    
    def connect(self) -> None:
        """Establish connection to the database."""
        try:
            conn_str = self._build_connection_string()
            logger.info(f"Connecting to {self.server}/{self.database}...")
            self._connection = pyodbc.connect(conn_str)
            logger.info("✅ Database connection established")
        except pyodbc.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    def test_connection(self) -> bool:
        """Test if the connection is working.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connect()
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1 AS test")
            result = cursor.fetchone()
            cursor.close()
            self.disconnect()
            return result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_schema_info(self) -> dict[str, Any]:
        """Retrieve database schema information.
        
        Returns:
            Dictionary with schema information including tables and columns
        """
        if not self._connection:
            self.connect()
        
        cursor = self._connection.cursor()
        
        # Get tables and their columns
        query = """
        SELECT 
            t.TABLE_SCHEMA,
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.NUMERIC_PRECISION,
            c.NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.TABLES t
        INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
            ON t.TABLE_SCHEMA = c.TABLE_SCHEMA 
            AND t.TABLE_NAME = c.TABLE_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Organize schema by table
        schema = {}
        for row in rows:
            schema_name = row[0]
            table_name = row[1]
            full_table_name = f"{schema_name}.{table_name}"
            
            if full_table_name not in schema:
                schema[full_table_name] = {
                    "schema": schema_name,
                    "table": table_name,
                    "columns": []
                }
            
            column_info = {
                "name": row[2],
                "data_type": row[3],
                "nullable": row[4] == "YES",
            }
            
            # Add length/precision info if available
            if row[5]:  # CHARACTER_MAXIMUM_LENGTH
                column_info["max_length"] = row[5]
            if row[6]:  # NUMERIC_PRECISION
                column_info["precision"] = row[6]
            if row[7]:  # NUMERIC_SCALE
                column_info["scale"] = row[7]
            
            schema[full_table_name]["columns"].append(column_info)
        
        cursor.close()
        
        logger.info(f"Retrieved schema for {len(schema)} tables")
        return schema
    
    def execute_query(self, query: str, max_rows: int = 1000) -> dict[str, Any]:
        """Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            max_rows: Maximum number of rows to return
            
        Returns:
            Dictionary with query results including columns and rows
        """
        if not self._connection:
            self.connect()
        
        import time
        start_time = time.time()
        
        cursor = self._connection.cursor()
        
        try:
            # Add TOP clause if not present (for SELECT queries)
            modified_query = query.strip()
            if modified_query.upper().startswith("SELECT") and "TOP" not in modified_query.upper()[:50]:
                # Insert TOP clause after SELECT
                modified_query = modified_query[:6] + f" TOP {max_rows}" + modified_query[6:]
                logger.info(f"Added TOP {max_rows} clause to query")
            
            cursor.execute(modified_query)
            
            # Get column information (format for LLM consumption)
            column_names = [column[0] for column in cursor.description] if cursor.description else []
            columns = [{"name": col_name} for col_name in column_names]
            
            # Fetch rows
            rows = cursor.fetchall()
            row_count = len(rows)
            
            # Convert rows to list of dicts
            data = []
            for row in rows:
                row_dict = {}
                for i, column_name in enumerate(column_names):
                    value = row[i]
                    # Convert to JSON-serializable types
                    if hasattr(value, 'isoformat'):  # datetime/date
                        value = value.isoformat()
                    elif isinstance(value, (bytes, bytearray)):
                        value = value.hex()
                    row_dict[column_name] = value
                data.append(row_dict)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = {
                "row_count": row_count,
                "columns": columns,
                "data": data,
                "execution_time_ms": execution_time,
                "query_executed": modified_query,
            }
            
            logger.info(f"Query executed successfully: {row_count} rows, {execution_time:.2f}ms")
            return result
            
        except pyodbc.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            cursor.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def create_connection_from_env() -> DatabaseConnection:
    """Create a DatabaseConnection from environment variables.
    
    Returns:
        DatabaseConnection instance
        
    Raises:
        ValueError: If required environment variables are missing
    """
    server = os.environ.get("MSSQL_SERVER_NAME")
    database = os.environ.get("MSSQL_DATABASE_NAME")
    username = os.environ.get("MSSQL_USERNAME")
    password = os.environ.get("MSSQL_PASSWORD")
    auth_type = os.environ.get("MSSQL_AUTHENTICATION_TYPE", "SqlPassword")
    timeout = int(os.environ.get("QUERY_TIMEOUT_SECONDS", "30"))
    
    if not server or not database:
        raise ValueError(
            "Missing required environment variables: MSSQL_SERVER_NAME and MSSQL_DATABASE_NAME"
        )
    
    if auth_type == "SqlPassword" and (not username or not password):
        raise ValueError(
            "SQL authentication requires MSSQL_USERNAME and MSSQL_PASSWORD environment variables"
        )
    
    return DatabaseConnection(
        server=server,
        database=database,
        username=username,
        password=password,
        authentication_type=auth_type,
        timeout=timeout,
    )

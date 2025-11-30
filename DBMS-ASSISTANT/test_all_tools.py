"""
Test all 11 MCP tools to verify they work correctly
"""
import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agent_framework import MCPStdioTool

async def test_tool(mcp_tool, tool_name: str, args: dict):
    """Test a single tool and return results"""
    print(f"\n{'='*80}")
    print(f"Testing: {tool_name}")
    print(f"Args: {json.dumps(args, indent=2)}")
    print(f"{'='*80}")
    
    try:
        # Find the tool function
        tool_func = None
        for func in mcp_tool.functions:
            if func.name == tool_name:
                tool_func = func
                break
        
        if not tool_func:
            print(f"❌ Tool '{tool_name}' not found!")
            return False
        
        # Call the tool
        result = await tool_func(**args)
        
        # Parse and display result
        if hasattr(result, 'content') and len(result.content) > 0:
            # Extract text from TextContent objects
            result_texts = []
            for item in result.content:
                if hasattr(item, 'text'):
                    result_texts.append(item.text)
                else:
                    result_texts.append(str(item))
            
            # Try to parse as JSON for better display
            for text in result_texts:
                try:
                    result_data = json.loads(text) if isinstance(text, str) else text
                    print(f"✅ Success!")
                    # Show first 800 chars of formatted JSON
                    formatted = json.dumps(result_data, indent=2)
                    if len(formatted) > 800:
                        print(f"Result (truncated):\n{formatted[:800]}...")
                    else:
                        print(f"Result:\n{formatted}")
                    return True
                except (json.JSONDecodeError, TypeError):
                    print(f"✅ Success!")
                    print(f"Result: {text[:500]}")
                    return True
        else:
            print(f"✅ Success!")
            print(f"Result: {result}")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    mcp_server_path = Path('MssqlMcp/Node/dist/index.js')
    mcp_env = {
        'SERVER_NAME': os.getenv('SERVER_NAME', ''),
        'DATABASE_NAME': os.getenv('DATABASE_NAME', ''),
        'SQL_USERNAME': os.getenv('SQL_USERNAME', ''),
        'SQL_PASSWORD': os.getenv('SQL_PASSWORD', ''),
        'TRUST_SERVER_CERTIFICATE': os.getenv('TRUST_SERVER_CERTIFICATE', 'true'),
        'READONLY': os.getenv('READONLY', 'false'),
    }
    
    print("Starting MCP server...")
    async with MCPStdioTool(
        name='mssql',
        command='node',
        args=[str(mcp_server_path)],
        env=mcp_env,
        description='Microsoft SQL Server database operations',
    ) as mcp_tool:
        print(f'✅ Connected to MCP server')
        print(f'Available tools: {[t.name for t in mcp_tool.functions]}\n')
        
        results = {}
        
        # Test 1: connect_db
        results['connect_db'] = await test_tool(mcp_tool, 'connect_db', {})
        
        # Test 2: list_databases
        results['list_databases'] = await test_tool(mcp_tool, 'list_databases', {})
        
        # Test 3: list_table
        results['list_table'] = await test_tool(mcp_tool, 'list_table', {
            'parameters': []
        })
        
        # Test 4: list_table with schema filter
        results['list_table_dim'] = await test_tool(mcp_tool, 'list_table', {
            'parameters': ['dim']
        })
        
        # Test 5: describe_table
        results['describe_table'] = await test_tool(mcp_tool, 'describe_table', {
            'tableName': 'dim.DimCustomer'
        })
        
        # Test 6: run_query - simple SELECT
        results['run_query_count'] = await test_tool(mcp_tool, 'run_query', {
            'query': 'SELECT COUNT(*) as TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = \'BASE TABLE\'',
            'maxRows': 10
        })
        
        # Test 7: run_query - table info
        results['run_query_tables'] = await test_tool(mcp_tool, 'run_query', {
            'query': 'SELECT TOP 5 TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = \'BASE TABLE\' ORDER BY TABLE_NAME',
            'maxRows': 5
        })
        
        # Test 8: read_data
        results['read_data'] = await test_tool(mcp_tool, 'read_data', {
            'tableName': 'dim.DimCustomer',
            'columns': ['CustomerID', 'CustomerName'],
            'limit': 5
        })
        
        # Test 9: create_index (skip if READONLY=true)
        if os.getenv('READONLY', 'false').lower() != 'true':
            results['create_index'] = await test_tool(mcp_tool, 'create_index', {
                'tableName': 'dim.DimCustomer',
                'indexName': 'IX_Test_CustomerName',
                'columns': ['CustomerName']
            })
        else:
            print("\n⏭️  Skipping create_index (READONLY mode)")
            results['create_index'] = None
        
        # Test 10: insert_data (skip if READONLY=true)
        if os.getenv('READONLY', 'false').lower() != 'true':
            results['insert_data'] = await test_tool(mcp_tool, 'insert_data', {
                'tableName': 'dim.DimCustomer',
                'data': {
                    'CustomerName': 'Test Customer',
                    'CustomerType': 'Test'
                }
            })
        else:
            print("\n⏭️  Skipping insert_data (READONLY mode)")
            results['insert_data'] = None
        
        # Test 11: update_data (skip if READONLY=true)
        if os.getenv('READONLY', 'false').lower() != 'true':
            results['update_data'] = await test_tool(mcp_tool, 'update_data', {
                'tableName': 'dim.DimCustomer',
                'data': {
                    'CustomerName': 'Updated Test Customer'
                },
                'condition': 'CustomerName = \'Test Customer\''
            })
        else:
            print("\n⏭️  Skipping update_data (READONLY mode)")
            results['update_data'] = None
        
        # Summary
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        
        total_tests = len([v for v in results.values() if v is not None])
        passed_tests = sum([1 for v in results.values() if v is True])
        skipped_tests = len([v for v in results.values() if v is None])
        
        for tool_name, passed in results.items():
            status = "✅ PASSED" if passed is True else "❌ FAILED" if passed is False else "⏭️  SKIPPED"
            print(f"{tool_name:25} {status}")
        
        print(f"\n{'='*80}")
        print(f"Total: {total_tests} tests, {passed_tests} passed, {total_tests - passed_tests} failed, {skipped_tests} skipped")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(main())

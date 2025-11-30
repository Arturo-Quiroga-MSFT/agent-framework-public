import sql from 'mssql';
import { Tool } from '@modelcontextprotocol/sdk/types.js';

/**
 * RunQueryTool - Execute arbitrary SQL queries
 * Useful for DBA tasks like checking statistics, running diagnostics, etc.
 */
export class RunQueryTool implements Tool {
  [key: string]: any;
  name = 'run_query';
  description = 'Execute a SQL query and return results. Use for SELECT, SHOW, or diagnostic queries.';

  inputSchema = {
    type: 'object' as const,
    properties: {
      query: {
        type: 'string',
        description: 'SQL query to execute',
      },
      maxRows: {
        type: 'number',
        description: 'Maximum number of rows to return (default: 1000)',
      },
    },
    required: ['query'],
  } as any;

  async run(args: {
    query: string;
    maxRows?: number;
  }): Promise<{ content: Array<{ type: string; text: string }> }> {
    try {
      const maxRows = args.maxRows || 1000;
      
      // Get connection from environment
      const server = process.env.SERVER_NAME;
      const database = process.env.DATABASE_NAME;
      const username = process.env.SQL_USERNAME;
      const password = process.env.SQL_PASSWORD;
      const trustServerCertificate = process.env.TRUST_SERVER_CERTIFICATE?.toLowerCase() === 'true';
      const isReadOnly = process.env.READONLY === 'true';

      if (!server || !database) {
        throw new Error('SERVER_NAME and DATABASE_NAME must be set in environment');
      }

      // Safety check for read-only mode
      if (isReadOnly) {
        const dangerousKeywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE'];
        const upperQuery = args.query.toUpperCase();
        for (const keyword of dangerousKeywords) {
          if (upperQuery.includes(keyword)) {
            throw new Error(`Query contains '${keyword}' which is not allowed in read-only mode`);
          }
        }
      }

      // Create connection
      const config: sql.config = {
        server: server,
        database: database,
        options: {
          encrypt: true,
          trustServerCertificate: trustServerCertificate,
        },
        authentication: {
          type: 'default',
          options: {
            userName: username || '',
            password: password || '',
          },
        },
        connectionTimeout: 30000,
        requestTimeout: 60000,
      };

      const pool = await sql.connect(config);
      
      // Execute query
      const startTime = Date.now();
      const result = await pool.request().query(args.query);
      const executionTime = Date.now() - startTime;

      await pool.close();

      // Format results
      const rows = result.recordset?.slice(0, maxRows) || [];
      const totalRows = result.recordset?.length || 0;
      const rowsAffected = result.rowsAffected?.[0] || 0;

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              executionTimeMs: executionTime,
              rowCount: totalRows,
              rowsAffected: rowsAffected,
              truncated: totalRows > maxRows,
              columns: rows.length > 0 ? Object.keys(rows[0]) : [],
              rows: rows,
            }, null, 2),
          },
        ],
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: false,
              error: `Query failed: ${error.message}`,
              query: args.query,
            }, null, 2),
          },
        ],
      };
    }
  }
}

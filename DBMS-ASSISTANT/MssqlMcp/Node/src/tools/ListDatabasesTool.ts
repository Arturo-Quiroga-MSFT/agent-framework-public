import sql from 'mssql';
import { Tool } from '@modelcontextprotocol/sdk/types.js';

/**
 * ListDatabasesTool - List all databases on the SQL Server
 */
export class ListDatabasesTool implements Tool {
  [key: string]: any;
  name = 'list_databases';
  description = 'List all databases available on the SQL Server';

  inputSchema = {
    type: 'object' as const,
    properties: {},
    required: [],
  } as any;

  async run(args: any): Promise<{ content: Array<{ type: string; text: string }> }> {
    try {
      const server = process.env.SERVER_NAME;
      const database = process.env.DATABASE_NAME || 'master';
      const username = process.env.SQL_USERNAME;
      const password = process.env.SQL_PASSWORD;
      const trustServerCertificate = process.env.TRUST_SERVER_CERTIFICATE?.toLowerCase() === 'true';

      if (!server) {
        throw new Error('SERVER_NAME must be set in environment');
      }

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
      };

      const pool = await sql.connect(config);
      
      const result = await pool.request().query(`
        SELECT 
          name as DatabaseName,
          database_id as DatabaseId,
          create_date as CreateDate,
          state_desc as State,
          recovery_model_desc as RecoveryModel
        FROM sys.databases
        WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')
        ORDER BY name
      `);

      await pool.close();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              databaseCount: result.recordset.length,
              databases: result.recordset,
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
              error: `Failed to list databases: ${error.message}`,
            }, null, 2),
          },
        ],
      };
    }
  }
}

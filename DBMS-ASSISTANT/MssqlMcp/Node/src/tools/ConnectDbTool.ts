import sql from 'mssql';
import { Tool } from '@modelcontextprotocol/sdk/types.js';

/**
 * ConnectDbTool - Establishes connection to SQL Server database
 * Returns connection metadata and server information
 */
export class ConnectDbTool implements Tool {
  [key: string]: any;
  name = 'connect_db';
  description = 'Connect to a SQL Server database and return connection details';

  inputSchema = {
    type: 'object',
    properties: {
      serverName: {
        type: 'string',
        description: 'SQL Server hostname or IP (e.g., server.database.windows.net)',
      },
      databaseName: {
        type: 'string',
        description: 'Database name to connect to',
      },
      username: {
        type: 'string',
        description: 'SQL Server username (optional if using env vars)',
      },
      password: {
        type: 'string',
        description: 'SQL Server password (optional if using env vars)',
      },
    },
    required: [],
  } as any;

  async run(args: {
    serverName?: string;
    databaseName?: string;
    username?: string;
    password?: string;
  }): Promise<{ content: Array<{ type: string; text: string }> }> {
    try {
      // Use provided args or fall back to environment variables
      const server = args.serverName || process.env.SERVER_NAME;
      const database = args.databaseName || process.env.DATABASE_NAME;
      const username = args.username || process.env.SQL_USERNAME;
      const password = args.password || process.env.SQL_PASSWORD;
      const trustServerCertificate = process.env.TRUST_SERVER_CERTIFICATE?.toLowerCase() === 'true';

      if (!server || !database) {
        throw new Error('SERVER_NAME and DATABASE_NAME are required (via arguments or environment)');
      }

      // Create connection configuration
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

      // Test connection
      const pool = await sql.connect(config);
      
      // Get server information
      const serverInfoResult = await pool.request().query(`
        SELECT 
          @@VERSION as ServerVersion,
          @@SERVERNAME as ServerName,
          DB_NAME() as DatabaseName,
          SYSTEM_USER as CurrentUser,
          (SELECT COUNT(*) FROM sys.tables WHERE type = 'U') as TableCount,
          (SELECT COUNT(*) FROM sys.views) as ViewCount,
          (SELECT SUM(size) * 8 / 1024 as SizeMB FROM sys.database_files WHERE type = 0) as DataSizeMB
      `);

      const info = serverInfoResult.recordset[0];

      // Close the test connection
      await pool.close();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              message: 'Successfully connected to SQL Server',
              connection: {
                server: server,
                database: database,
                user: info.CurrentUser,
              },
              serverInfo: {
                version: info.ServerVersion,
                serverName: info.ServerName,
                databaseName: info.DatabaseName,
                tableCount: info.TableCount,
                viewCount: info.ViewCount,
                dataSizeMB: info.DataSizeMB,
              },
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
              error: `Failed to connect: ${error.message}`,
              details: error.stack,
            }, null, 2),
          },
        ],
      };
    }
  }
}
